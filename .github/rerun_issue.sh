#!/usr/bin/env bash
# Manually re-run the New Issue Processing workflow on a single issue.
#
# Usage:
#   .github/rerun_issue.sh <issue_number>
#
# Example:
#   .github/rerun_issue.sh 43

set -euo pipefail

REPO="WCRP-CMIP/Essential-Model-Documentation"
WORKFLOW="new-issue.yml"

if [[ -z "${1:-}" ]]; then
    echo "Usage: $0 <issue_number>"
    exit 1
fi

ISSUE="$1"

# Show the issue title so you know you're targeting the right one
TITLE=$(gh issue view "$ISSUE" --repo "$REPO" --json title --jq '.title')
echo "Issue #${ISSUE}: ${TITLE}"

gh workflow run "$WORKFLOW" \
    --repo "$REPO" \
    --field "issue_number=${ISSUE}"

echo "✓ Triggered workflow for issue #${ISSUE}"
echo "  https://github.com/${REPO}/actions/workflows/${WORKFLOW}"
