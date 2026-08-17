#!/usr/bin/env bash
# close_linked_prs.sh
#
# Lists all open PRs linked to closed issues via Resolves/Fixes/Closes #N.
# Usage:
#   .github/close_linked_prs.sh         # dry run — print only
#   .github/close_linked_prs.sh --run   # close PRs and comment

set -euo pipefail

RUN=false
[[ "${1:-}" == "--run" ]] && RUN=true

REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
echo "Repo: $REPO"
echo ""

# Fetch all closed issue numbers
echo "Fetching closed issues..."
CLOSED_ISSUES=$(gh issue list --repo "$REPO" --state closed --limit 500 --json number --jq '.[].number')

# Fetch all open PRs with their bodies
echo "Fetching open PRs..."
OPEN_PRS=$(gh pr list --repo "$REPO" --state open --limit 200 --json number,title,body)

FOUND=0

while IFS= read -r issue_num; do
    [[ -z "$issue_num" ]] && continue

    # Find open PRs referencing this issue
    LINKED=$(echo "$OPEN_PRS" | jq -r \
        --arg n "$issue_num" \
        '.[] | select(
            .body != null and
            (.body | test("(?i)(resolves|fixes|closes)[[:space:]]+#" + $n + "\\b"))
        ) | "#\(.number) — \(.title)"')

    [[ -z "$LINKED" ]] && continue

    echo "Issue #${issue_num} → linked open PRs:"
    while IFS= read -r pr_line; do
        echo "  $pr_line"
        FOUND=$((FOUND + 1))

        if [[ "$RUN" == "true" ]]; then
            PR_NUM=$(echo "$pr_line" | grep -oE '^#[0-9]+' | tr -d '#')
            gh pr comment "$PR_NUM" --repo "$REPO" \
                --body "Closing this PR as the linked issue #${issue_num} has been closed."
            gh pr close "$PR_NUM" --repo "$REPO"
            echo "    ✓ Closed PR #${PR_NUM}"
        fi
    done <<< "$LINKED"
    echo ""
done <<< "$CLOSED_ISSUES"

if [[ $FOUND -eq 0 ]]; then
    echo "No open PRs found linked to any closed issue."
elif [[ "$RUN" == "false" ]]; then
    echo "---"
    echo "Found $FOUND linked PR(s). Re-run with --run to close them."
fi
