#!/usr/bin/env bash
# pr_issue_map.sh
#
# Lists open PRs, the issues they reference, and their review status.
# Usage:
#   .github/pr_issue_map.sh              # open PRs, pretty print
#   .github/pr_issue_map.sh --all        # all PRs, pretty print
#   .github/pr_issue_map.sh --json       # open PRs, JSON output
#   .github/pr_issue_map.sh --all --json # all PRs, JSON output

set -euo pipefail

JSON=false
PR_STATE="open"
for arg in "$@"; do
    [[ "$arg" == "--json" ]] && JSON=true
    [[ "$arg" == "--all" ]]  && PR_STATE="all"
done

REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
echo "Fetching PRs and issues for $REPO..." >&2

# Fetch PRs with reviews
ALL_PRS=$(gh pr list --repo "$REPO" --state "$PR_STATE" --limit 500 \
    --json number,title,state,body,reviews)

# Fetch all issues (open + closed)
ALL_ISSUES=$(gh issue list --repo "$REPO" --state all --limit 500 \
    --json number,title,state)

# Build mapping: for each PR, extract linked issues + review summary
MAPPING=$(echo "$ALL_PRS" | jq -c '.[]' | while IFS= read -r pr; do
    pr_num=$(echo "$pr"   | jq -r '.number')
    pr_title=$(echo "$pr" | jq -r '.title')
    pr_state=$(echo "$pr" | jq -r '.state')
    pr_body=$(echo "$pr"  | jq -r '.body // ""')
    reviews=$(echo "$pr"  | jq -c '.reviews // []')

    # Approved: anyone with APPROVED state
    approved=$(echo "$reviews" | jq -r '[.[] | select(.state=="APPROVED") | .author.login] | unique | join(", ")')

    # Engaged: anyone who reviewed or commented (deduplicated)
    engaged=$(echo "$reviews" | jq -r '[.[].author.login] | unique | join(", ")')

    # Extract referenced issue numbers from PR body
    issue_nums=$(echo "$pr_body" | grep -oiE '(resolves|fixes|closes)[[:space:]]+#[0-9]+' \
        | grep -oE '[0-9]+' || true)

    linked_issues=$(echo "$issue_nums" | while IFS= read -r inum; do
        [[ -z "$inum" ]] && continue
        echo "$ALL_ISSUES" | jq -c --arg n "$inum" \
            '.[] | select(.number == ($n | tonumber)) | {number, title, state}'
    done | jq -s '.')
    [[ -z "$linked_issues" ]] && linked_issues='[]'

    jq -n \
        --argjson pr_num "$pr_num" \
        --arg     pr_title "$pr_title" \
        --arg     pr_state "$pr_state" \
        --arg     approved "$approved" \
        --arg     engaged "$engaged" \
        --argjson linked_issues "$linked_issues" \
        '{pr: $pr_num, pr_title: $pr_title, pr_state: $pr_state,
          reviews: {approved: $approved, engaged: $engaged},
          linked_issues: $linked_issues}'
done | jq -s '.')


if [[ "$JSON" == "true" ]]; then
    echo "$MAPPING" | jq '.'
    exit 0
fi

# Pretty print
echo ""
echo "$MAPPING" | jq -r '[.[] | select(.reviews.approved == "")] |  .[] |
    "PR #\(.pr) [\(.pr_state | ascii_upcase)] — \(.pr_title)",
    (if .reviews.approved != "" then "  ✓ Approved : \(.reviews.approved)" else "  ✓ Approved : —" end),
    (if .reviews.engaged  != "" then "  💬 Engaged : \(.reviews.engaged)"  else "  💬 Engaged : —" end),
    (if (.linked_issues | length) > 0 then
        (.linked_issues[] | "  └─ Issue #\(.number) [\(.state)] — \(.title)")
    else
        "  └─ (no linked issues)"
    end),
    ""'

TOTAL=$(echo "$MAPPING" | jq 'length')
REVIEWED=$(echo "$MAPPING" | jq '[.[] | select(.reviews.engaged != "")] | length')
echo "---"
echo "$TOTAL PR(s) shown — $REVIEWED with reviews."
