#!/usr/bin/env python3
"""
Navigation Generation & Build Process Verification

This document explains the custom navigation system and how to verify it works correctly.

## The Build Pipeline

1. **Pre-build hook** (hooks/pre_build.py)
   - Deletes old SUMMARY.md to force regeneration
   - Clears build directory (shutil.rmtree)
   - Creates fresh build directory

2. **Gen-files plugin** with run_scripts.py
   - Executes all scripts in docs/scripts/
   - These generate HTML files in nested directories like:
     * docs/10_EMD_Repository/01_Models/*.html
     * docs/10_EMD_Repository/02_Model_Components/*.html
     * docs/10_EMD_Repository/03_Component_Families/*.html
     * etc.
   - After all scripts complete, generate_nav_custom.py creates SUMMARY.md

3. **Literate-nav plugin**
   - Reads the generated SUMMARY.md
   - Builds site navigation with support for nested folders
   - Creates the navigation structure in mkdocs

4. **on_files hook** (hooks/generate_nav.py)
   - Strips numeric prefixes from dest_uri (output URLs)
   - E.g., "01_Models" becomes "Models" in URLs
   - But filenames keep the prefix for proper ordering

5. **MkDocs build**
   - clean_site_directory: true ensures build dir is clean
   - HTML output is generated in site_dir (../../build)


## Key Features of generate_nav_custom.py

✓ Recursive directory scanning with proper nesting
✓ Numeric prefix handling:
  - Preserves numeric prefixes in filenames for ordering
  - Strips them from display names (01_Models -> Models)
✓ File type filtering (only .md and .html included)
✓ Automatic exclusions (.git, __pycache__, scripts/, etc.)
✓ Proper markdown formatting for shadcn theme
✓ Max depth limiting to prevent scanning too deep
✓ Permission error handling for restricted dirs


## Typesetting Preservation

The generated HTML files maintain their exact typesetting and formatting:
- Only the numeric prefix is stripped from display names
- All other content, HTML structure, styling remains intact
- Links between HTML files work correctly with path adjustments


## Testing the Navigation

To verify the navigation works:

1. From src/mkdocs/, run:
   mkdocs build -f mkdocs.yml

2. Check that:
   ✓ docs/SUMMARY.md was created/regenerated
   ✓ All directories appear in SUMMARY.md
   ✓ All .md and .html files are listed
   ✓ Numeric prefixes are stripped in SUMMARY.md display names
   ✓ Folder nesting is correct (proper indentation)
   ✓ build/ directory contains the generated site

3. Inspect docs/SUMMARY.md:
   - Should show hierarchical structure
   - Display names should have no numeric prefixes
   - Paths should preserve prefixes (for MkDocs src_uri)

4. Check build/index.html:
   - Navigation should show nested folders
   - URLs should have no numeric prefixes
   - All HTML pages should be reachable


## Troubleshooting

If navigation is missing:
1. Check that generate_nav_custom.py ran (look for "Generating SUMMARY.md" in build output)
2. Verify docs/SUMMARY.md exists and has content
3. Check that literate-nav plugin is listed in mkdocs.yml
4. Ensure nav_file: SUMMARY.md is set in literate-nav config

If folders are missing:
1. Verify scripts are generating HTML files in docs/10_EMD_Repository/
2. Check that directories aren't in the exclusions list
3. Ensure max_depth in generate_nav_custom.py is sufficient

If prefixes aren't stripped from URLs:
1. Verify on_files hook in hooks/generate_nav.py is executing
2. Check that the regex pattern matches your prefix format
3. Ensure hook is listed in mkdocs.yml

If HTML files aren't showing in nav:
1. Verify they have .html extension
2. Check that they're in subdirectories of docs/
3. Ensure they're not in exclusion patterns


## Manual Navigation Generation

If needed, you can manually regenerate SUMMARY.md:

cd docs/
python ../src/mkdocs/hooks/generate_nav_custom.py

Or from anywhere:
cd /Users/daniel.ellis/WIPwork/Essential-Model-Documentation/src/mkdocs/hooks
python generate_nav_custom.py

This will scan docs/ and create SUMMARY.md without running a full build.
"""

# If run as script, provide helpful output
if __name__ == "__main__":
    import sys
    print(__doc__)
    sys.exit(0)
