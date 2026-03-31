#!/usr/bin/env bash
# Finds open issues matching a title pattern and triggers
# the "New Issue Processing" workflow for each one.
#
# Usage:
#   .github/rerun_stage.sh                        # dry run, matches 'Stage 1'
#   .github/rerun_stage.sh "Stage 2"              # dry run, custom pattern
#   .github/rerun_stage.sh --run                  # trigger workflows, matches 'Stage 1'
#   .github/rerun_stage.sh "Stage 2" --run        # trigger workflows, custom pattern
#
# Requires: gh CLI authenticated to WCRP-CMIP/Essential-Model-Documentation

set -euo pipefail

REPO="WCRP-CMIP/Essential-Model-Documentation"
WORKFLOW="new-issue.yml"
DRY_RUN=true
PATTERN="Stage 1"  # default

# Parse args: optional --run flag and optional pattern string (either order)
for arg in "$@"; do
    if [[ "$arg" == "--run" ]]; then
        DRY_RUN=false
    else
        PATTERN="$arg"
    fi
done

echo "Fetching issues matching '${PATTERN}' from ${REPO}..."

ISSUES=$(gh issue list \
    --repo "$REPO" \
    --state open \
    --limit 200 \
    --json number,title \
    --jq ".[] | select(.title | test(\"${PATTERN}\"; \"i\")) | \"\(.number)\t\(.title)\"")

if [[ -z "$ISSUES" ]]; then
    echo "No open issues found matching '${PATTERN}'."
    exit 0
fi

echo ""
echo "Found issues:"
echo "$ISSUES" | while IFS=$'\t' read -r number title; do
    echo "  #${number}  ${title}"
done
echo ""

if $DRY_RUN; then
    echo "DRY RUN — pass --run to trigger workflows."
    exit 0
fi

echo "Triggering workflow '${WORKFLOW}' for each issue..."
echo "$ISSUES" | while IFS=$'\t' read -r number title; do
    echo -n "  Triggering #${number} (${title})... "
    gh workflow run "$WORKFLOW" \
        --repo "$REPO" \
        --field "issue_number=${number}"
    echo "done"
    sleep 2
done

echo ""
echo "All workflows triggered."
