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


REPO_DEFAULT = "WCRP-CMIP/Essential-Model-Documentation"
# Stamped = starts with | xxx | or [closed]
STAMP_RE      = re.compile(r"^\s*\|\s*\S+.*\|\s*|^\[closed\]", re.IGNORECASE)
LINK_RE = re.compile(
    r"(?:resolves|fixes|closes)\s+\[?#(\d+)\]?",
    re.IGNORECASE
)
PR_REF_RE = re.compile(
    r"pull[/ ]request[^\d]*#?(\d+)|/pull/(\d+)",
    re.IGNORECASE
)
NAMED_TYPE_RE = re.compile(
    r"(model|model_family|model_component|component_config)\s*:", re.IGNORECASE
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


def fetch_closed_issues(repo):
    all_issues = []
    page = 1
    while True:
        raw = gh("api", f"repos/{repo}/issues",
                 "--method", "GET",
                 "-f", "state=closed",
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
        print(f"  page {page}: {len(batch)} issues (total: {len(all_issues)})")
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
            return m.group(1) or m.group(2)

    # Fall back to branch name pattern
    raw = gh("pr", "list", "--repo", repo, "--state", "all",
             "--limit", "200", "--json", "number,headRefName")
    if not raw:
        return None
    pattern = re.compile(rf"_?{number}_|[-_]{number}$")
    for pr in json.loads(raw):
        if pattern.search(pr.get("headRefName", "")):
            return str(pr["number"])
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


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo",    default=REPO_DEFAULT)
    parser.add_argument("--apply",   action="store_true",
                        help="Write title changes to GitHub (default: dry run)")
    parser.add_argument("--verbose", action="store_true",
                        help="Show all unstamped issues and type-match result")
    args = parser.parse_args()

    print(f"Fetching closed emd-submission issues from {args.repo}...")
    issues = fetch_closed_issues(args.repo)
    print(f"  {len(issues)} closed issues fetched.")

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
