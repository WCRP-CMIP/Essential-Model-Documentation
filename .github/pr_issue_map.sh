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
[[ "${1:-}" == "--json" ]] && JSON=true

REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

echo "Fetching PRs and issues for $REPO..." >&2

# Fetch all PRs (open + closed) with number and title
ALL_PRS=$(gh pr list --repo "$REPO" --state all --limit 500 --json number,title,state)

# Fetch all issues (open + closed) with number, title, state, body
ALL_ISSUES=$(gh issue list --repo "$REPO" --state all --limit 500 --json number,title,state,body)

# Build mapping: for each PR, find issues whose body references it
MAPPING=$(echo "$ALL_PRS" | jq -c '.[]' | while IFS= read -r pr; do
    pr_num=$(echo "$pr" | jq -r '.number')
    pr_title=$(echo "$pr" | jq -r '.title')
    pr_state=$(echo "$pr" | jq -r '.state')

    # Find issues referencing this PR number
    linked_issues=$(echo "$ALL_ISSUES" | jq -c \
        --arg n "$pr_num" \
        '[.[] | select(
            .body != null and
            (.body | test("(?i)(resolves|fixes|closes)[[:space:]]+#" + $n + "\\b"))
        ) | {number, title, state}]')

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
