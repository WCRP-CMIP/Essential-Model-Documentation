#!/usr/bin/env bash
# pr_issue_map.sh
#
# Gets all pull requests and maps them to the issues that reference them
# via Resolves/Fixes/Closes #N in the issue body.
#
# Usage:
#   .github/pr_issue_map.sh           # print mapping
#   .github/pr_issue_map.sh --json    # output as JSON

set -euo pipefail

JSON=false
PR_STATE="open"
for arg in "$@"; do
    [[ "$arg" == "--json" ]] && JSON=true
    [[ "$arg" == "--all" ]]  && PR_STATE="all"
done

REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

echo "Fetching PRs and issues for $REPO..." >&2

# Fetch all PRs (open + closed) with number and title
ALL_PRS=$(gh pr list --repo "$REPO" --state "$PR_STATE" --limit 500 --json number,title,state,body)

# Fetch all issues (open + closed) with number, title, state, body
ALL_ISSUES=$(gh issue list --repo "$REPO" --state all --limit 500 --json number,title,state,body)

# Build mapping: for each PR, extract issues referenced in the PR body
MAPPING=$(echo "$ALL_PRS" | jq -c '.[]' | while IFS= read -r pr; do
    pr_num=$(echo "$pr" | jq -r '.number')
    pr_title=$(echo "$pr" | jq -r '.title')
    pr_state=$(echo "$pr" | jq -r '.state')
    pr_body=$(echo "$pr" | jq -r '.body // ""')

    # Extract issue numbers referenced in this PR's body
    issue_nums=$(echo "$pr_body" | grep -oiE '(resolves|fixes|closes)[[:space:]]+#[0-9]+' | grep -oE '[0-9]+' || true)

    # Look up each referenced issue's title and state
    linked_issues=$(echo "$issue_nums" | while IFS= read -r inum; do
        [[ -z "$inum" ]] && continue
        echo "$ALL_ISSUES" | jq -c --arg n "$inum" '.[] | select(.number == ($n | tonumber)) | {number, title, state}'
    done | jq -s '.')

    [[ -z "$linked_issues" ]] && linked_issues='[]'

    echo "{\"pr\": $pr_num, \"pr_title\": $(echo "$pr_title" | jq -Rs .), \"pr_state\": \"$pr_state\", \"linked_issues\": $linked_issues}"
done | jq -s '.')

if [[ "$JSON" == "true" ]]; then
    echo "$MAPPING" | jq '.'
    exit 0
fi

# Pretty print
echo ""
echo "$MAPPING" | jq -r '.[] | select(.linked_issues | length > 0) |
    "PR #\(.pr) [\(.pr_state)] — \(.pr_title)",
    (.linked_issues[] | "  └─ Issue #\(.number) [\(.state)] — \(.title)"),
    ""'

# Summary of PRs with no linked issues
NO_LINKS=$(echo "$MAPPING" | jq '[.[] | select(.linked_issues | length == 0)] | length')
TOTAL=$(echo "$MAPPING" | jq 'length')
echo "---"
echo "$(echo "$MAPPING" | jq '[.[] | select(.linked_issues | length > 0)] | length') / $TOTAL PRs have linked issues ($NO_LINKS unlinked)."
