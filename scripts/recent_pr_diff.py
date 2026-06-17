#!/usr/bin/env python3
"""
recent_pr_diff.py
=================
Find all emd-submission issues updated in the last N hours.
For each issue, find the emd-bot-issue-status comment and fetch
its edit history via GraphQL — showing only edits made in the
lookback window, with the PR link extracted from each version.

Then for each PR found, fetch the previous and latest versions
of the submitted JSON file and display a diff.

Usage
-----
  python scripts/recent_pr_diff.py
  python scripts/recent_pr_diff.py --hours 6
  python scripts/recent_pr_diff.py --repo ORG/REPO

Requirements
------------
  gh CLI authenticated:  gh auth status
"""

import argparse
import base64
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

REPO_DEFAULT = "WCRP-CMIP/Essential-Model-Documentation"
PR_IN_BODY_RE = re.compile(r"/pull/(\d+)", re.IGNORECASE)
BOT_MARKER    = "emd-bot-issue-status"


# =============================================================================
# GitHub helpers
# =============================================================================

def gh(*args):
    cmd = "gh " + " ".join(f'"{a}"' if " " in str(a) else str(a) for a in args)
    result = os.popen(cmd).read().strip()
    return result or None


def gh_json(*args):
    raw = gh(*args)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def graphql(query, variables=None):
    payload = json.dumps({"query": query, "variables": variables or {}})
    # Write to a temp file to avoid shell quoting issues
    tmp = "/tmp/emd_gql_query.json"
    with open(tmp, "w") as f:
        f.write(payload)
    raw = os.popen(f"gh api graphql --input {tmp}").read().strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def fetch_recent_issues(repo, since_iso):
    all_issues = []
    page = 1
    while True:
        data = gh_json(
            "api", f"repos/{repo}/issues",
            "--method", "GET",
            "-f", "state=closed",
            "-f", "labels=emd-submission",
            "-f", "per_page=100",
            "-f", f"page={page}",
            "-f", f"since={since_iso}",
        )
        if not data:
            break
        batch = [i for i in data if "pull_request" not in i]
        if not batch:
            break
        all_issues.extend(batch)
        if len(data) < 100:
            break
        page += 1
    return all_issues


def fetch_bot_comment_id(repo, issue_number):
    """Return the node_id and database id of the emd-bot-issue-status comment."""
    data = gh_json(
        "api", f"repos/{repo}/issues/{issue_number}/comments",
        "--method", "GET", "-f", "per_page=100",
    )
    if not data:
        return None, None
    for c in data:
        if BOT_MARKER in (c.get("body") or ""):
            return c["node_id"], c["id"]
    return None, None


def fetch_comment_full_history(node_id):
    """
    Fetch the full edit history of a comment via GraphQL.
    GitHub stores edits newest-first; we reverse to get chronological order.
    Returns list of {editedAt, diff, editor} dicts, oldest first.
    """
    query = """
    query($id: ID!) {
      node(id: $id) {
        ... on IssueComment {
          body
          userContentEdits(first: 25) {
            nodes {
              editedAt
              diff
              editor { login }
            }
          }
        }
      }
    }
    """
    result = graphql(query, {"id": node_id})
    if not result:
        return [], None

    node = result.get("data", {}).get("node", {}) or {}
    current_body = node.get("body", "")
    nodes = node.get("userContentEdits", {}).get("nodes", []) or []

    edits = []
    for n in nodes:
        edited_at_str = n.get("editedAt")
        if not edited_at_str:
            continue
        edits.append({
            "editedAt": datetime.fromisoformat(edited_at_str.replace("Z", "+00:00")),
            "diff":     n.get("diff") or "",
            "editor":   (n.get("editor") or {}).get("login", "unknown"),
        })

    # GitHub returns newest-first — reverse for chronological order
    edits.sort(key=lambda x: x["editedAt"])
    return edits, current_body


def update_comment_body(repo, comment_id, body):
    """Update a comment's body via the REST API."""
    import tempfile
    payload = json.dumps({"body": body})
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    tmp.write(payload)
    tmp.close()
    result = gh("api", f"repos/{repo}/issues/comments/{comment_id}",
                "--method", "PATCH",
                "--input", tmp.name)
    os.unlink(tmp.name)
    return result is not None


def extract_pr_from_text(text):
    m = PR_IN_BODY_RE.search(text)
    return m.group(1) if m else None


def fetch_pr_info(repo, pr_number):
    return gh_json("pr", "view", pr_number, "--repo", repo,
                   "--json", "files,mergedAt,state,headRefName,baseRefName,baseRefOid") or {}


def fetch_pr_base_sha(repo, pr_number):
    data = gh_json("api", f"repos/{repo}/pulls/{pr_number}", "--method", "GET")
    return (data or {}).get("base", {}).get("sha")


def fetch_file_at_ref(repo, path, ref):
    raw = gh("api", f"repos/{repo}/contents/{path}",
             "--method", "GET", "-f", f"ref={ref}")
    if not raw:
        return None
    try:
        data = json.loads(raw)
        return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    except Exception:
        return None


# =============================================================================
# Diff display
# =============================================================================

def json_diff(old_str, new_str, label_old="previous", label_new="latest"):
    import difflib
    def pretty(s):
        try:
            return json.dumps(json.loads(s), indent=2).splitlines(keepends=True)
        except Exception:
            return s.splitlines(keepends=True)
    return list(difflib.unified_diff(
        pretty(old_str), pretty(new_str),
        fromfile=label_old, tofile=label_new, lineterm=""
    ))


RESET = "\033[0m"
BOLD  = "\033[1m"
GREEN = "\033[32m"
RED   = "\033[31m"
CYAN  = "\033[36m"

def print_diff(diff_lines):
    if not diff_lines:
        print("    (no changes in JSON content)")
        return
    for line in diff_lines:
        if line.startswith(("+++", "---")):
            print(f"    {BOLD}{line}{RESET}")
        elif line.startswith("+"):
            print(f"    {GREEN}{line}{RESET}")
        elif line.startswith("-"):
            print(f"    {RED}{line}{RESET}")
        elif line.startswith("@@"):
            print(f"    {CYAN}{line}{RESET}")
        else:
            print(f"    {line}")


def show_pr_file_diff(repo, pr_number, pr_info):
    files     = pr_info.get("files", [])
    merged_at = pr_info.get("mergedAt")
    base_ref  = pr_info.get("baseRefName", "main")
    head_ref  = pr_info.get("headRefName", "")
    base_sha  = pr_info.get("baseRefOid") or fetch_pr_base_sha(repo, pr_number)

    json_files = [f for f in files if f.get("filename", "").endswith(".json")]
    if not json_files:
        print("    No JSON files in PR.")
        return

    for f in json_files:
        path   = f["filename"]
        status = f.get("status", "?")
        print(f"\n    File: {path}  ({status})")

        latest   = fetch_file_at_ref(repo, path, base_ref if merged_at else head_ref)
        previous = fetch_file_at_ref(repo, path, base_sha) if base_sha else None

        if status == "added":
            print("    (new file — no previous version)")
            if latest:
                try:
                    parsed = json.loads(latest)
                    for k, v in list(parsed.items())[:8]:
                        print(f"      {k}: {v}")
                except Exception:
                    print(f"      {latest[:300]}")
        elif previous and latest:
            diff = json_diff(
                previous, latest,
                label_old=f"base ({base_sha[:7] if base_sha else '?'})",
                label_new=f"PR #{pr_number} head",
            )
            print_diff(diff)
        else:
            print("    (could not fetch one or both versions for diff)")


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo",  default=REPO_DEFAULT)
    parser.add_argument("--hours", type=float, default=4)
    parser.add_argument("--apply", action="store_true",
                        help="Restore overwritten comments (default: dry run)")
    args = parser.parse_args()

    since_dt  = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    since_iso = since_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"Looking back {args.hours}h  (since {since_iso})\n")

    issues = fetch_recent_issues(args.repo, since_iso)
    print(f"{len(issues)} issues updated in window.\n")

    for issue in issues:
        number  = issue["number"]
        title   = issue["title"]
        updated = issue.get("updated_at", "")
        state   = issue.get("state", "")

        print(f"{'═'*70}")
        print(f"  #{number}  [{state}]  {title}")
        print(f"  {issue.get('html_url','')}")
        print(f"  Last updated: {updated}")

        # Find the bot comment
        node_id, comment_id = fetch_bot_comment_id(args.repo, number)
        if not node_id:
            print("  No emd-bot-issue-status comment found.\n")
            continue

        # Fetch full edit history + current body
        all_edits, current_body = fetch_comment_full_history(node_id)
        if not all_edits:
            print("  No edit history available.\n")
            continue

        # Find edits within the window
        recent_edits = [e for e in all_edits if e["editedAt"] >= since_dt]
        if not recent_edits:
            print("  Bot comment not edited in this window.\n")
            continue

        latest_edit   = recent_edits[-1]
        latest_ts     = latest_edit["editedAt"].strftime("%Y-%m-%d %H:%M UTC")
        latest_editor = latest_edit["editor"]

        # Find the last edit outside the window — walk back through all edits
        # to find the most recent one that predates the lookback window.
        before_window = [e for e in all_edits if e["editedAt"] < since_dt]

        if before_window:
            prev_edit = before_window[-1]
            prev_ts   = prev_edit["editedAt"].strftime("%Y-%m-%d %H:%M UTC")

            # Reconstruct body as it was AFTER prev_edit by reading its diff:
            # [+] lines = what was added (i.e. the new content at that point)
            # [-] lines = what was removed (i.e. the old content before that edit)
            # Context lines (no marker) = unchanged content present in both.
            # So: body after prev_edit = context lines + [+] lines.
            restored = []
            for line in prev_edit["diff"].splitlines():
                if line.startswith("[+") and line.endswith("+]"):
                    restored.append(line[2:-2])
                elif line.startswith("[-") and line.endswith("-]"):
                    pass  # removed by that edit — not present after it
                else:
                    restored.append(line)
            prev_body = "\n".join(restored).strip()
        else:
            prev_ts   = "(original — no prior edit)"
            prev_body = "(no previous version available)"

        # Extract PR numbers from both versions
        prev_pr    = extract_pr_from_text(prev_body)
        current_pr = extract_pr_from_text(current_body or "")

        print(f"\n  Bot comment edit history:")
        print(f"  {'─'*60}")
        print(f"  PREVIOUS  ({prev_ts})")
        if prev_pr:
            print(f"  PR: #{prev_pr}  https://github.com/{args.repo}/pull/{prev_pr}")
        print()
        for line in (prev_body or "").splitlines():
            print(f"    {line}")

        print(f"\n  {'─'*60}")
        print(f"  LATEST  ({latest_ts})  edited by: {latest_editor}")
        if current_pr:
            print(f"  PR: #{current_pr}  https://github.com/{args.repo}/pull/{current_pr}")
        print()
        for line in (current_body or "").splitlines():
            print(f"    {line}")

        print(f"\n  {'─'*60}")
        if prev_pr and current_pr and prev_pr != current_pr:
            print(f"  ⚠  PR changed: #{prev_pr} → #{current_pr}")
            if args.apply:
                if comment_id and prev_body:
                    ok = update_comment_body(args.repo, comment_id, prev_body)
                    if ok:
                        print(f"  ✓  Comment restored to previous version (PR #{prev_pr})")
                    else:
                        print(f"  ✗  Failed to restore comment — check gh auth permissions")
            else:
                print(f"  (dry run — pass --apply to restore comment to PR #{prev_pr})")
        elif prev_pr == current_pr:
            print(f"  PR unchanged (#{current_pr})")

        print()

    print(f"{'═'*70}")
    print("Done.")


if __name__ == "__main__":
    main()
