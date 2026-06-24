#!/usr/bin/env python3
"""
audit_unstamped_issues.py
=========================
Finds all closed emd-submission issues without a pipe stamp in the title,
locates their linked PR, and reports what action would be taken.

Actions (dry-run by default, use --apply to execute):
  no PR found      -> prepend | skip |  (signals progress tracker to ignore)
  PR merged        -> prepend | <merged filename> |
  PR closed        -> prepend [closed]

Usage
-----
  python3 audit_unstamped_issues.py              # dry run
  python3 audit_unstamped_issues.py --apply      # write changes to GitHub
  python3 audit_unstamped_issues.py --repo ORG/REPO

Requirements
------------
  gh CLI authenticated:  gh auth status
"""

import argparse
import json
import re
import subprocess
import sys

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


MAN_PAGE = """
╔══════════════════════════════════════════════════════════════════════╗
║                     audit_unstamped_issues.py                        ║
╚══════════════════════════════════════════════════════════════════════╝

Audits emd-submission issues (open + closed) that are missing a pipe
stamp in their title, and optionally fixes them.

USAGE
  python scripts/audit_unstamped_issues.py [OPTIONS]

OPTIONS
  --man / --help-full     Show this manual and exit.

  --apply                 Write changes to GitHub (default: dry run).
                          Without this flag nothing is modified.

  --merged                Mode: find open issues whose linked PR has
                          already been merged. Stamps the title with
                          | <filename> | and closes the issue.
                          Use with --apply to execute.

  --verbose               In default mode, print all unstamped issues
                          before the type filter with their match result.

  --repo ORG/REPO         Override the default repository.
                          Default: WCRP-CMIP/Essential-Model-Documentation

MODES
  Default (no --merged)
  ─────────────────────
  Scans all open + closed emd-submission issues without a stamp.
  For each one that has a linked PR:
    • PR merged  → prepend  | <filename> |  to the title
    • PR closed  → prepend  [closed]  to the title
    • No PR      → skip (issue excluded from output)

  --merged mode
  ─────────────
  Scans only open issues. For each one whose linked PR is merged:
    • Stamps the title with  | <filename> |
    • Closes the issue
  Useful for model / model_component / model_family issues that stay
  open after their PR merges (they are not auto-closed by the workflow).

EXAMPLES
  # See what would be stamped (dry run, default mode)
  python scripts/audit_unstamped_issues.py

  # Apply stamps to all unstamped closed issues
  python scripts/audit_unstamped_issues.py --apply

  # Find open issues with merged PRs (dry run)
  python scripts/audit_unstamped_issues.py --merged

  # Stamp + close open issues with merged PRs
  python scripts/audit_unstamped_issues.py --merged --apply

  # Debug: show all unstamped issues and type-match result
  python scripts/audit_unstamped_issues.py --verbose

  # Run against a fork
  python scripts/audit_unstamped_issues.py --repo myorg/my-fork

REQUIREMENTS
  gh CLI installed and authenticated:
    gh auth status
"""



# Detect current repository (overridable via --repo).
try:
    REPO_DEFAULT = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
except Exception:
    REPO_DEFAULT = ""


# Stamped = starts with | xxx | or [closed]
STAMP_RE      = re.compile(r"^\s*\|\s*\S+.*\|\s*|^\[closed\]", re.IGNORECASE)
LINK_RE = re.compile(
    r"(?:resolves|fixes|closes)\s+\[?#(\d+)\]?",
    re.IGNORECASE
)
PR_REF_RE = re.compile(
    r"/pull/(\d+)",
    re.IGNORECASE
)
NAMED_TYPE_RE = re.compile(
    r"(model|model_family|model_component|component_config)\s*:|"
    r"\[EMD\]\s*Stage\s*4:\s*Model",
    re.IGNORECASE
)

# Directories that contain named-type submissions
SUBMISSION_DIRS = {
    "horizontal_grid_cell", "horizontal_computational_grid",
    "vertical_computational_grid", "model_family",
    "model_component", "component_config", "model",
}


def gh(*args):
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  gh error: {result.stderr.strip()}", file=sys.stderr)
        return None
    return result.stdout.strip()


def fetch_closed_issues(repo, closed_only=False):
    """Fetch emd-submission issues without a stamp.

    By default fetches both closed and open issues; pass closed_only=True to
    skip the open pass.
    """
    all_issues = []
    states = ("closed",) if closed_only else ("closed", "open")
    for state in states:
        page = 1
        while True:
            raw = gh("api", f"repos/{repo}/issues",
                     "--method", "GET",
                     "-f", f"state={state}",
                     "-f", "labels=emd-submission",
                     "-f", "per_page=100",
                     "-f", f"page={page}")
            if not raw:
                break
            batch = json.loads(raw)
            batch = [i for i in batch if "pull_request" not in i]
            if not batch:
                break
            all_issues.extend(batch)
            print(f"  [{state}] page {page}: {len(batch)} issues (total: {len(all_issues)})")
            if len(batch) < 100:
                break
            page += 1
    return all_issues


def find_pr(repo, issue):
    """Return PR number as string, or None."""
    number = issue["number"]

    # Search body + comments for any PR reference
    texts = [issue.get("body") or ""]

    raw = gh("api", f"repos/{repo}/issues/{number}/comments",
             "--method", "GET", "-f", "per_page=100")
    if raw:
        for c in json.loads(raw):
            texts.append(c.get("body") or "")

    for text in texts:
        flat = text.replace("\n", " ")
        m = LINK_RE.search(flat)
        if m:
            return m.group(1)
        m = PR_REF_RE.search(flat)
        if m:
            return m.group(1)

    # Fall back to branch name pattern — search all PRs via API pagination
    pattern = re.compile(rf"(?:^|[-_]){number}(?:[-_]|$)")
    page = 1
    while True:
        raw = gh("api", f"repos/{repo}/pulls",
                 "--method", "GET",
                 "-f", "state=all",
                 "-f", "per_page=100",
                 "-f", f"page={page}")
        if not raw:
            break
        prs = json.loads(raw)
        if not prs:
            break
        for pr in prs:
            if pattern.search(pr.get("head", {}).get("ref", "")):
                return str(pr["number"])
        if len(prs) < 100:
            break
        page += 1
    return None


def fetch_pr_info(repo, pr_number):
    """Return (status, merged_filename). status: 'merged'|'closed'|'unknown'."""
    raw = gh("pr", "view", pr_number, "--repo", repo,
             "--json", "state,mergedAt,files")
    if not raw:
        return "unknown", None
    data = json.loads(raw)

    merged = bool(data.get("mergedAt"))
    status = "merged" if merged else data.get("state", "unknown").lower()

    filename = None
    if merged:
        for f in data.get("files", []):
            path = f.get("path", "")
            parts = path.split("/")
            if parts[0] in SUBMISSION_DIRS and path.endswith(".json"):
                filename = parts[-1].replace(".json", "")
                break

    return status, filename


def compute_new_title(title, status, filename):
    if status == "merged":
        stamp = filename if filename else "unknown"
        return f"| {stamp} | {title}"
    elif status == "closed":
        return f"[closed] {title}"
    return title


def find_issues_with_merged_prs(repo, issues, apply=False):
    """
    For every issue, find its linked PR and check if it's merged.
    Returns list of (issue, pr_number, filename) for merged PRs only.
    Prints a table as it goes.
    """
    print(f"\n{'─'*70}")
    print(f"  Scanning for issues with merged PRs...")
    print(f"{'─'*70}\n")

    results = []
    iterator = tqdm(issues, desc="Scanning", unit="issue") if tqdm else issues

    for issue in iterator:
        number = issue["number"]
        title  = issue["title"]
        state  = issue.get("state", "?")

        pr_num = find_pr(repo, issue)
        if not pr_num:
            continue

        status, filename = fetch_pr_info(repo, pr_num)
        if status != "merged":
            continue

        results.append((issue, pr_num, filename))

    mode = "APPLY" if apply else "DRY RUN"
    print(f"\n{'Issue':<8}  {'State':<7}  {'PR':<8}  {'File':<30}  New Title")
    print(f"{'─'*8}  {'─'*7}  {'─'*8}  {'─'*30}  {'─'*40}")
    for issue, pr_num, filename in results:
        stamp = filename if filename else "unknown"
        new_title = f"| {stamp} | {issue['title']}"
        print(
            f"  #{issue['number']:<6}  {issue.get('state','?'):<7}  "
            f"#{pr_num:<7}  {(filename or '?'):<30}  {new_title}"
        )
        if apply:
            gh("issue", "edit", str(issue["number"]), "--repo", repo,
               "--title", new_title)
            gh("issue", "close", str(issue["number"]), "--repo", repo)
            print(f"  ✓ #{issue['number']} stamped and closed")

    print(f"\nTotal: {len(results)}  [{mode}]")
    if not apply:
        print("(dry run — pass --apply to stamp and close)")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo",    default=REPO_DEFAULT)
    parser.add_argument("--man", "--help-full", action="store_true",
                        help="Show full manual and exit")
    parser.add_argument("--apply",   action="store_true",
                        help="Write title changes to GitHub (default: dry run)")
    parser.add_argument("--verbose", action="store_true",
                        help="Show all unstamped issues and type-match result")
    parser.add_argument("--merged",  action="store_true",
                        help="Show all issues that have a merged PR (ignores stamp filter)")
    parser.add_argument("--closed-only", action="store_true",
                        help="Only scan closed issues (skip open ones)")
    args = parser.parse_args()

    if args.man:
        print(MAN_PAGE)
        return

    if args.apply:
        ans = input("Have you turned off the new-issue workflow? [y/N] ").strip().lower()
        if ans != "y":
            print("Aborting — disable the new-issue workflow first to avoid conflicts.")
            return

    scope = "closed" if args.closed_only else "open + closed"
    print(f"Fetching emd-submission issues ({scope}) from {args.repo}...")
    issues = fetch_closed_issues(args.repo, closed_only=args.closed_only)
    print(f"  {len(issues)} issues fetched.")

    if args.merged:
        open_issues = [i for i in issues if i.get("state") == "open"]
        find_issues_with_merged_prs(args.repo, open_issues, apply=args.apply)
        return

    unstamped = [
        i for i in issues
        if not STAMP_RE.match(i["title"])
    ]
    print(f"  {len(unstamped)} issues without a stamp.\n")

    if args.verbose:
        no_stamp = [i for i in issues if not STAMP_RE.match(i["title"])]
        print(f"  {len(no_stamp)} total without a stamp (before type filter):")
        for i in no_stamp:
            matched = bool(NAMED_TYPE_RE.search(i["title"]))
            print(f"    #{i['number']:4}  match={matched}  {i['title']!r}")
        print()

    if not unstamped:
        print("Nothing to do.")
        return

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"{'='*60}")
    print(f"  {mode}")
    print(f"{'='*60}\n")

    rows = []
    iterator = (
        tqdm(unstamped, desc="Processing issues", unit="issue")
        if tqdm else unstamped
    )
    for issue in iterator:
        number = issue["number"]
        title  = issue["title"]

        pr_num = find_pr(args.repo, issue)

        if pr_num is None:
            continue  # no linked PR — skip entirely

        status, filename = fetch_pr_info(args.repo, pr_num)
        new_title = compute_new_title(title, status, filename)
        pr_col    = f"#{pr_num}"

        rows.append((f"#{number}", pr_col, status, title, new_title))

        if args.apply:
            gh("issue", "edit", str(number), "--repo", args.repo,
               "--title", new_title)
            print(f"  ✓ #{number} updated")

    # Print summary table
    print(f"\n{'Issue':<8}  {'PR':<8}  {'Status':<8}  {'New Title'}")
    print(f"{'─'*8}  {'─'*8}  {'─'*8}  {'─'*50}")
    for issue_col, pr_col, status, old, new in rows:
        print(f"{issue_col:<8}  {pr_col:<8}  {status:<8}  {new}")

    print(f"\nTotal: {len(rows)}")
    if not args.apply:
        print("\n(dry run — pass --apply to write changes)")


if __name__ == "__main__":
    main()
