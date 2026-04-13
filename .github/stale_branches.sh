#!/usr/bin/env bash
# stale_branches.sh
#
# Finds remote branches that are only attached to closed/merged PRs
# (and no open ones) — safe candidates for deletion.
#
# Usage:
#   .github/stale_branches.sh          # list stale branches
#   .github/stale_branches.sh --delete # delete them (with confirmation)

set -euo pipefail

DELETE=false
[[ "${1:-}" == "--delete" ]] && DELETE=true

REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
echo "Repo: $REPO"
echo ""
echo "Fetching PRs..." >&2

# Get all PRs grouped by branch, state
ALL_PRS=$(gh pr list --repo "$REPO" --state all --limit 500 \
    --json number,headRefName,state)

# Get all remote branches
ALL_BRANCHES=$(git ls-remote --heads origin | awk '{print $2}' | sed 's|refs/heads/||')

STALE=()

while IFS= read -r branch; do
    # Only consider branches with new_ or modify_ in the name
    [[ "$branch" != *new_* && "$branch" != *modify_* ]] && continue

    # PRs on this branch
    open_count=$(echo "$ALL_PRS" | jq --arg b "$branch" \
        '[.[] | select(.headRefName == $b and .state == "OPEN")] | length')
    closed_count=$(echo "$ALL_PRS" | jq --arg b "$branch" \
        '[.[] | select(.headRefName == $b and (.state == "CLOSED" or .state == "MERGED"))] | length')

    # Stale = has closed/merged PRs, zero open PRs
    if [[ "$open_count" -eq 0 && "$closed_count" -gt 0 ]]; then
        STALE+=("$branch")
        echo "  [stale] $branch  (${closed_count} closed/merged PR(s), 0 open)"
    fi
done <<< "$ALL_BRANCHES"

echo ""
echo "${#STALE[@]} stale branch(es) found."

if [[ "${#STALE[@]}" -eq 0 ]]; then
    exit 0
fi

if [[ "$DELETE" == "true" ]]; then
    echo ""
    read -r -p "Delete all ${#STALE[@]} stale branch(es) from origin? [y/N] " confirm
    [[ "$confirm" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }
    for branch in "${STALE[@]}"; do
        git push origin --delete "$branch" && echo "  deleted: $branch"
    done
    echo "Done."
else
    echo ""
    echo "Re-run with --delete to remove them."
fi
