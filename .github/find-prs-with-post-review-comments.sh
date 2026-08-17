#!/usr/bin/env bash
# find-prs-with-post-review-comments.sh
#
# Lists PRs that have received comments (review or issue) AFTER
# the most recent APPROVED or CHANGES_REQUESTED review.
# Inline comments shown in blue, thread comments in violet.
#
# Usage:
#   ./find-prs-with-post-review-comments.sh [--state open|closed|all] [--limit N]
#
# Defaults: --state open  --limit 50

set -euo pipefail

STATE="open"
LIMIT=50

VIOLET='\033[38;5;135m'
BLUE='\033[38;5;75m'
CORAL='\033[38;5;209m'
GRAY='\033[38;5;245m'
RESET='\033[0m'

# OSC 8 hyperlink — clickable in iTerm2, Terminal ≥Ventura, WezTerm, Kitty
hyperlink() { printf '\e]8;;%s\e\\%s\e]8;;\e\\' "$1" "$2"; }

# Colour the word APPROVED in coral wherever it appears in a string
coral_approved() { echo "$1" | sed "s/APPROVED/$(printf "${CORAL}")APPROVED$(printf "${RESET}")/g"; }

# Strip email quote blocks — exit at the "On Weekday, ..." preamble line
strip_email_quote() {
  echo "$1" | awk '/^On [A-Z][a-z][a-z],/{exit} {print}' | awk 'NF{found=1} found'
}

# Print a full comment block in gray, indenting continuation lines
print_comment() {
  local prefix="$1"   # e.g. "[inline] user:" or "[thread] user:"
  local body="$2"
  local first=true
  while IFS= read -r line; do
    if $first; then
      printf "${GRAY}    %s %s${RESET}\n" "$prefix" "$line"
      first=false
    else
      printf "${GRAY}      %s${RESET}\n" "$line"
    fi
  done <<< "$body"
}

BOT_FILTER='((.user.login | endswith("[bot]")) or (.user.login | ascii_downcase | startswith("copilot"))) | not'

while [[ $# -gt 0 ]]; do
  case $1 in
    --state) STATE="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "Repo: $REPO"
echo "Checking $LIMIT $STATE PRs for comments after review decisions..."
echo ""

PRS=$(gh pr list --state "$STATE" --limit "$LIMIT" --json number,title,url)

echo "$PRS" | jq -c '.[]' | while read -r pr; do
  NUMBER=$(echo "$pr" | jq -r '.number')
  TITLE=$(echo  "$pr" | jq -r '.title')
  URL=$(echo    "$pr" | jq -r '.url')

  REVIEWS=$(gh api "repos/$REPO/pulls/$NUMBER/reviews" --paginate 2>/dev/null)

  LATEST_DECISION_DATE=$(echo "$REVIEWS" | jq -r '
    [ .[] | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED") ]
    | sort_by(.submitted_at) | last | .submitted_at // empty')

  [[ -z "$LATEST_DECISION_DATE" ]] && continue

  LATEST_DECISION_STATE=$(echo "$REVIEWS" | jq -r '
    [ .[] | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED") ]
    | sort_by(.submitted_at) | last | .state')

  # Fetch post-review inline comments — output as NUL-delimited "user\x01body" pairs
  REVIEW_COMMENTS_RAW=$(gh api "repos/$REPO/pulls/$NUMBER/comments" --paginate 2>/dev/null)
  POST_REVIEW=$(echo "$REVIEW_COMMENTS_RAW" | jq --arg d "$LATEST_DECISION_DATE" \
    '[.[] | select(.created_at > $d)] | length')
  REVIEW_PAIRS=$(echo "$REVIEW_COMMENTS_RAW" | jq -r --arg d "$LATEST_DECISION_DATE" \
    --argjson bot_filter 'null' \
    '[.[] | select(.created_at > $d) | select('"$BOT_FILTER"')] | .[] | "\(.user.login)\u0001\(.body)\u0000"')

  # Fetch post-review thread comments — output as NUL-delimited "user\x01body" pairs
  ISSUE_COMMENTS_RAW=$(gh api "repos/$REPO/issues/$NUMBER/comments" --paginate 2>/dev/null)
  POST_ISSUE=$(echo "$ISSUE_COMMENTS_RAW" | jq --arg d "$LATEST_DECISION_DATE" \
    '[.[] | select(.created_at > $d)] | length')
  ISSUE_PAIRS=$(echo "$ISSUE_COMMENTS_RAW" | jq -r --arg d "$LATEST_DECISION_DATE" \
    '[.[] | select(.created_at > $d) | select('"$BOT_FILTER"')] | .[] | "\(.user.login)\u0001\(.body)\u0000"')

  TOTAL=$(( POST_REVIEW + POST_ISSUE ))

  # Count human comments (bot-filtered)
  HUMAN_REVIEW=$(echo "$REVIEW_COMMENTS_RAW" | jq --arg d "$LATEST_DECISION_DATE" \
    '[.[] | select(.created_at > $d) | select('"$BOT_FILTER"')] | length')
  HUMAN_ISSUE=$(echo "$ISSUE_COMMENTS_RAW" | jq --arg d "$LATEST_DECISION_DATE" \
    '[.[] | select(.created_at > $d) | select('"$BOT_FILTER"')] | length')
  HUMAN_TOTAL=$(( HUMAN_REVIEW + HUMAN_ISSUE ))

  [[ "$HUMAN_TOTAL" -eq 0 ]] && continue

  echo "PR #$NUMBER — $TITLE"
  echo "  Decision : $(coral_approved "$LATEST_DECISION_STATE") at $LATEST_DECISION_DATE"
  echo "  Comments : $HUMAN_TOTAL ($HUMAN_REVIEW inline, $HUMAN_ISSUE thread)"
  echo "  $(hyperlink "$URL" "$URL")"

  # Show the review body that triggered the decision
  REVIEW_BODY=$(echo "$REVIEWS" | jq -r '
    [ .[] | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED") ]
    | sort_by(.submitted_at) | last
    | select(.body != null and .body != "") | "  \(.user.login): \(.body)"')
  if [[ -n "$REVIEW_BODY" ]]; then
    printf "${BLUE}  Review decision body:${RESET}\n"
    while IFS= read -r line; do
      printf "${BLUE}    %s${RESET}\n" "$line"
    done <<< "$REVIEW_BODY"
  fi
  echo ""

  # Print inline comments (gray) — one compact JSON per line avoids NUL-in-variable issue
  echo "$REVIEW_COMMENTS_RAW" | jq -c --arg d "$LATEST_DECISION_DATE" \
    '[.[] | select(.created_at > $d) | select(((.user.login | endswith("[bot]")) or (.user.login | ascii_downcase | startswith("copilot"))) | not)] | .[]' \
  | while IFS= read -r obj; do
      user=$(echo "$obj" | jq -r '.user.login')
      body=$(echo "$obj" | jq -r '.body')
      print_comment "[inline] $user:" "$(strip_email_quote "$body")"
    done

  # Print thread comments (gray) — one compact JSON per line
  echo "$ISSUE_COMMENTS_RAW" | jq -c --arg d "$LATEST_DECISION_DATE" \
    '[.[] | select(.created_at > $d) | select(((.user.login | endswith("[bot]")) or (.user.login | ascii_downcase | startswith("copilot"))) | not)] | .[]' \
  | while IFS= read -r obj; do
      user=$(echo "$obj" | jq -r '.user.login')
      body=$(echo "$obj" | jq -r '.body')
      print_comment "[thread] $user:" "$(strip_email_quote "$body")"
    done

  echo ""
done
