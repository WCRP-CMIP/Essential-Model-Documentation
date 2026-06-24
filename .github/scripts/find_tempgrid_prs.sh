#!/bin/bash
REPO="/Users/daniel.ellis/WIPwork/Essential-Model-Documentation"
BASE_URL="https://github.com/WCRP-CMIP/Essential-Model-Documentation"

cd "$REPO" || { echo "ERROR: cannot cd to $REPO"; exit 1; }

echo "========================================"
echo "Tempgrid files in grid folders"
echo "========================================"

for f in horizontal_grid_cell/tempgrid_*.json \
          horizontal_computational_grid/tempgrid_*.json \
          vertical_computational_grid/tempgrid_*.json; do

    [ -f "$f" ] || continue

    echo ""
    echo "FILE: $f"

    commit=$(git log --all --diff-filter=A --pretty=format:"%H" -- "$f" | tail -1)

    if [ -z "$commit" ]; then
        echo "  WARNING: no introducing commit found"
        continue
    fi

    echo "  Commit: $commit"

    branch=$(git branch -r --contains "$commit" 2>/dev/null \
             | grep 'origin/issue_' | head -1 | tr -d ' ')

    echo "  Branch: $branch"

    issue=$(echo "$branch" | grep -oE 'issue_[0-9]+' | grep -oE '[0-9]+')
    if [ -n "$issue" ]; then
        echo "  PR: $BASE_URL/pull/$issue"
    else
        echo "  WARNING: could not extract issue number"
    fi
done

echo ""
echo "========================================"
