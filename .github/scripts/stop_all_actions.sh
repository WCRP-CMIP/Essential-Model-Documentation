#!/bin/bash
# stop_all_actions.sh
# Cancel all in-progress and queued workflow runs in the repo.

REPO="${1:-WCRP-CMIP/Essential-Model-Documentation}"

echo "Cancelling all running/queued actions in $REPO..."

gh run list --repo "$REPO" \
  --status in_progress \
  --limit 100 \
  --json databaseId \
  --jq '.[].databaseId' \
| xargs -I {} gh run cancel {} --repo "$REPO"

gh run list --repo "$REPO" \
  --status queued \
  --limit 100 \
  --json databaseId \
  --jq '.[].databaseId' \
| xargs -I {} gh run cancel {} --repo "$REPO"

echo "Done."
