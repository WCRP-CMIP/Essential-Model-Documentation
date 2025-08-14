#!/bin/bash
# Setup branches for CMIP workflow repositories
# This script creates the required branches if they don't exist

set -e

REPO_PATH="${1:-.}"
cd "$REPO_PATH"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Setting up CMIP repository branches${NC}"
echo "Repository: $(pwd)"
echo ""

# Check if we're in a git repo
if [ ! -d ".git" ]; then
    echo "Error: Not a git repository"
    exit 1
fi

# Get current branch
CURRENT=$(git branch --show-current)
echo "Current branch: $CURRENT"
echo ""

# Function to create branch if it doesn't exist
create_branch_if_needed() {
    local branch_name=$1
    local description=$2
    
    if git show-ref --verify --quiet "refs/heads/$branch_name"; then
        echo -e "${GREEN}✓ $branch_name branch exists${NC}"
    elif git ls-remote --heads origin "$branch_name" | grep -q "$branch_name"; then
        echo -e "${YELLOW}→ $branch_name exists on remote, checking out${NC}"
        git fetch origin "$branch_name"
        git checkout -b "$branch_name" "origin/$branch_name"
        git checkout "$CURRENT"
    else
        echo -e "${YELLOW}→ Creating $branch_name branch${NC}"
        echo "   $description"
        
        # Create orphan branch (no history)
        git checkout --orphan "$branch_name"
        
        # Clear any staged files
        git rm -rf . 2>/dev/null || true
        
        # Create appropriate initial content
        case "$branch_name" in
            "src-data")
                # Create example vocabulary structure
                mkdir -p example_vocab
                cat > example_vocab/_context << 'EOF'
{
  "@context": {
    "@vocab": "https://example.com/vocab/",
    "id": "@id",
    "name": "http://schema.org/name",
    "description": "http://schema.org/description"
  }
}
EOF
                cat > example_vocab/example.json << 'EOF'
{
  "id": "example",
  "name": "Example Entry",
  "description": "This is an example vocabulary entry. Replace with your actual data."
}
EOF
                git add example_vocab/
                ;;
                
            "docs")
                # Create basic documentation
                mkdir -p docs
                cat > docs/index.md << 'EOF'
# Documentation

Welcome to the documentation.

## Getting Started

Add your documentation pages here.

## Structure

```
docs/
├── index.md          # This file
├── getting-started.md
└── api/
    └── reference.md
```

## Editing

Push changes to the `docs` branch to automatically deploy to GitHub Pages.
EOF
                git add docs/
                ;;
                
            "production")
                # Create empty production branch
                cat > README.md << 'EOF'
# Production Branch

This branch contains the published version of the repository.

**Do not edit this branch directly!**

It is automatically updated by GitHub Actions workflows from:
- `src-data` branch (vocabulary data)
- `docs` branch (documentation)
EOF
                git add README.md
                ;;
        esac
        
        # Commit
        git commit -m "Initialize $branch_name branch" --allow-empty
        
        # Push to remote
        git push origin "$branch_name"
        
        # Return to original branch
        git checkout "$CURRENT"
        
        echo -e "${GREEN}✓ Created $branch_name branch${NC}"
    fi
    echo ""
}

# Create required branches
echo "Creating required branches..."
echo ""

create_branch_if_needed "src-data" "Source data branch for vocabulary JSON-LD files"
create_branch_if_needed "docs" "Documentation branch for user-facing docs"
create_branch_if_needed "production" "Published version (auto-updated by workflows)"

# Summary
echo ""
echo -e "${GREEN}Branch setup complete!${NC}"
echo ""
echo "Branches:"
git branch -a | grep -E "(src-data|docs|production|main)" || true
echo ""
echo "Next steps:"
echo "1. Add vocabulary data to src-data branch"
echo "2. Add documentation to docs branch"
echo "3. Workflows will automatically update production branch"
echo "4. Configure GitHub Pages to deploy from 'production' branch"
echo ""
