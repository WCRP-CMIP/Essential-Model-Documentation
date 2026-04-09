#!/bin/bash
REPO=${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}

echo "PRs for $REPO"
echo "============================================"

# Fetch all PRs as JSON
PRS=$(gh pr list --repo "$REPO" --state open --json number,title,headRefName,baseRefName,author)

# Print all PRs
echo "$PRS" | jq -r '.[] | "#\(.number) [\(.headRefName) → \(.baseRefName)] \(.title) (@\(.author.login))"'

echo ""
echo "============ Duplicate head branches ============"

# Find any head branches used by more than one PR
echo "$PRS" | jq -r '
  group_by(.headRefName)[] 
  | select(length > 1) 
  | "Branch: \(.[0].headRefName) used by \(length) PRs:"
  + (map("  #\(.number) \(.title) (@\(.author.login))") | "\n" + join("\n"))
'
