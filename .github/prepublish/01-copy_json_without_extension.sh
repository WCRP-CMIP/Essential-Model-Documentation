#!/bin/bash
# Copy JSON files without extension for content negotiation
# Repository: Essential-Model-Documentation
#
# Creates extensionless copies:
#   x/y/file.json → x/y/file
#   _graph.json → graph (special case: removes underscore)
#   _context.json → _context (keeps underscore for context files)

echo "Copying JSON files without .json extension..."

count=0

find . -type f -name "*.json" \
  ! -path "*/docs/*" \
  ! -path "*/summaries/*" \
  ! -path "*/.*" \
  -print0 | while IFS= read -r -d '' file; do
    dir=$(dirname "$file")
    base=$(basename "$file" .json)
    
    # Special case: _graph.json → graph (remove underscore)
    if [ "$base" = "_graph" ]; then
      dest="$dir/graph"
    else
      dest="$dir/$base"
    fi
    
    cp "$file" "$dest"
    echo "  $file → $dest"
    ((count++))
done

echo "✓ JSON files copied (extensionless)"
