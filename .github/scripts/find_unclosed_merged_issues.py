#!/usr/bin/env python3
"""
find_unclosed_merged_issues.py
==============================
Finds open issues whose PR was merged but the issue was not auto-closed
(typically because of a tempgrid rename or other workflow issue).

For every merged PR, this script collects every linked issue (from PR body
Closes/Fixes/Resolves keywords AND from the issue_NNN_* head branch naming)
and reports any that are still open.

Usage
-----
  python3 find_unclosed_merged_issues.py                       # dry run, list only
  python3 find_unclosed_merged_issues.py --run                 # close them
  python3 find_unclosed_merged_issues.py --repo ORG/REPO       # different repo
  python3 find_unclosed_merged_issues.py --limit 500           # cap merged PRs scanned

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


CLOSE_KW_RE = re.compile(
    r'(?:Close[sd]?|Fix(?:e[sd])?|Resolve[sd]?)\s+#(\d+)',
    re.IGNORECASE,
)
BRANCH_ISSUE_RE = re.compile(r'^issue_(\d+)_', re.IGNORECASE)


def gh(args, **kwargs):
    """Run gh and return stdout (raises on failure)."""
    result = subprocess.run(
        ['gh', *args],
        capture_output=True, text=True, check=True, **kwargs,
    )
    return result.stdout


def fetch_merged_prs(repo: str, limit: int) -> list[dict]:
    raw = gh([
        'pr', 'list', '--repo', repo,
        '--state', 'merged',
        '--limit', str(limit),
        '--json', 'number,title,body,headRefName,closingIssuesReferences',
    ])
    return json.loads(raw)


def extract_linked_issues(pr: dict) -> set[int]:
    issues: set[int] = set()

    # 1. GitHub's own "closing issues references" (the proper link)
    for ref in pr.get('closingIssuesReferences') or []:
        if isinstance(ref, dict) and 'number' in ref:
            issues.add(int(ref['number']))

    # 2. Closes/Fixes/Resolves #N in the PR body
    for m in CLOSE_KW_RE.finditer(pr.get('body') or ''):
        issues.add(int(m.group(1)))

    # 3. issue_NNN_... head branch name
    br = pr.get('headRefName') or ''
    m = BRANCH_ISSUE_RE.match(br)
    if m:
        issues.add(int(m.group(1)))

    return issues


def get_issue_state(repo: str, num: int) -> str | None:
    """Return 'OPEN', 'CLOSED', or None if the issue doesn't exist."""
    try:
        raw = gh([
            'issue', 'view', str(num),
            '--repo', repo,
            '--json', 'state',
        ])
    except subprocess.CalledProcessError:
        return None
    return json.loads(raw).get('state')


def close_issue(repo: str, num: int, pr_num: int) -> bool:
    body = (
        f'Closing automatically: PR #{pr_num} was merged but the issue was '
        f'not closed at the time (likely due to a tempgrid-rename workflow '
        f'race). Closed via `find_unclosed_merged_issues.py`.'
    )
    try:
        subprocess.run(
            ['gh', 'issue', 'comment', str(num), '--repo', repo, '--body', body],
            check=True, capture_output=True,
        )
        subprocess.run(
            ['gh', 'issue', 'close', str(num), '--repo', repo],
            check=True, capture_output=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f'  ✗ close failed for #{num}: {e.stderr.decode().strip()}\n')
        return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument('--repo', default='WCRP-CMIP/Essential-Model-Documentation')
    p.add_argument('--limit', type=int, default=1000,
                   help='Max merged PRs to scan (default: 1000)')
    p.add_argument('--run', action='store_true',
                   help='Actually close the issues (default: dry run)')
    args = p.parse_args()

    print(f'Scanning merged PRs in {args.repo} (limit {args.limit}) ...')
    prs = fetch_merged_prs(args.repo, args.limit)
    print(f'  found {len(prs)} merged PRs\n')

    # Build (pr -> linked issues) map
    pr_to_issues: list[tuple[dict, set[int]]] = []
    for pr in prs:
        linked = extract_linked_issues(pr)
        if linked:
            pr_to_issues.append((pr, linked))

    # Resolve issue states (one call per unique issue)
    unique_issues = sorted({n for _, s in pr_to_issues for n in s})
    print(f'Resolving state of {len(unique_issues)} linked issues ...')

    iterator = tqdm(unique_issues, unit='issue') if tqdm else unique_issues
    state: dict[int, str | None] = {}
    for n in iterator:
        state[n] = get_issue_state(args.repo, n)

    # Report and (optionally) close
    open_pairs: list[tuple[int, dict]] = []  # (issue_num, pr)
    for pr, linked in pr_to_issues:
        for n in sorted(linked):
            if state.get(n) == 'OPEN':
                open_pairs.append((n, pr))

    print()
    print('=' * 78)
    if not open_pairs:
        print('✅ No merged PRs with unclosed linked issues found.')
        return 0

    print(f'Found {len(open_pairs)} open issues whose PR was merged:')
    print('=' * 78)
    print(f'{"Issue":>6}  {"PR":>6}  Title')
    print('-' * 78)
    for issue_num, pr in open_pairs:
        title = (pr.get('title') or '').strip()[:60]
        print(f'  #{issue_num:<5} #{pr["number"]:<5}  {title}')

    if not args.run:
        print()
        print('Dry run only. Re-run with --run to close these issues.')
        return 0

    print()
    print(f'Closing {len(open_pairs)} issues ...')
    closed = 0
    for issue_num, pr in open_pairs:
        if close_issue(args.repo, issue_num, pr['number']):
            print(f'  ✓ closed #{issue_num} (linked to PR #{pr["number"]})')
            closed += 1
    print(f'\nDone. Closed {closed}/{len(open_pairs)}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
