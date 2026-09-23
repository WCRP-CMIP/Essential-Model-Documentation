#!/usr/bin/env bash
# Re-run "New Issue Processing" across every OPEN issue carrying a given label.
#
# Two safety rails, both deliberate:
#
#   1. --state open is enforced. The `if:` in new-issue.yml reads
#        github.event_name == 'workflow_dispatch' || (... && state != 'closed')
#      so workflow_dispatch short-circuits BEFORE the closed check. Dispatching
#      a closed issue really does reprocess it and recreate branches/PRs for
#      already-merged content.
#
#   2. Issues labelled 'approved' are skipped. A re-run force-pushes the
#      branch and updates the PR, which resets the review state and
#      re-notifies reviewers.
#
# Dry-run by default — you must pass --yes to actually dispatch anything.
#
# Usage:
#   .github/rerun_label.sh horizontal_grid_cell
#   .github/rerun_label.sh horizontal_grid_cell --yes
#   .github/rerun_label.sh horizontal_grid_cell --yes --skip approved,changes-requested
#   RERUN_SLEEP=45 .github/rerun_label.sh model --yes
#
# See also: .github/rerun_issue.sh for a single issue.

set -euo pipefail

REPO="WCRP-CMIP/Essential-Model-Documentation"
WORKFLOW="new-issue.yml"
SLEEP="${RERUN_SLEEP:-20}"
SKIP_LABELS="approved"
CONFIRM=false

LABEL="${1:-}"
if [[ -z "$LABEL" ]]; then
    echo "Usage: $0 <label> [--yes] [--skip label1,label2]"
    exit 1
fi
shift

while [[ $# -gt 0 ]]; do
    case "$1" in
        --yes)  CONFIRM=true; shift ;;
        --skip) SKIP_LABELS="${2:-}"; shift 2 ;;
        *)      echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Collected with a while-read rather than mapfile so this still runs on the
# bash 3.2 that ships with macOS.
ROWS=()
while IFS= read -r line; do
    [[ -n "$line" ]] && ROWS+=("$line")
done < <(
    gh issue list --repo "$REPO" --label "$LABEL" --state open --limit 500 \
        --json number,labels \
        --jq '.[] | [.number, (.labels | map(.name) | join(","))] | @tsv' \
    | sort -n
)

if [[ ${#ROWS[@]} -eq 0 ]]; then
    echo "No open issues with label '$LABEL'."
    exit 0
fi

IFS=',' read -ra SKIPS <<< "$SKIP_LABELS"

RUN=()
echo "Open issues labelled '$LABEL': ${#ROWS[@]}"
echo
for row in "${ROWS[@]}"; do
    num="${row%%$'\t'*}"
    labels="${row#*$'\t'}"
    hit=""
    for s in "${SKIPS[@]}"; do
        if [[ -n "$s" && ",$labels," == *",$s,"* ]]; then hit="$s"; break; fi
    done
    if [[ -n "$hit" ]]; then
        printf '  %-7s SKIP  (%s)\n' "$num" "$hit"
    else
        printf '  %-7s run\n' "$num"
        RUN+=("$num")
    fi
done

echo
echo "Will dispatch ${#RUN[@]} of ${#ROWS[@]} (${SLEEP}s apart)."

if [[ "$CONFIRM" != true ]]; then
    echo "Dry run — re-run with --yes to dispatch."
    exit 0
fi

echo
for i in "${!RUN[@]}"; do
    n="${RUN[$i]}"
    title=$(gh issue view "$n" --repo "$REPO" --json title --jq '.title')
    echo "→ #${n}: ${title}"
    gh workflow run "$WORKFLOW" --repo "$REPO" --field "issue_number=${n}"
    if [[ $i -lt $(( ${#RUN[@]} - 1 )) ]]; then sleep "$SLEEP"; fi
done

echo
echo "✓ Dispatched ${#RUN[@]} run(s)."
echo "  https://github.com/${REPO}/actions/workflows/${WORKFLOW}"
