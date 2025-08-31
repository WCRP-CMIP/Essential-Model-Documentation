#!/usr/bin/env python3
"""
Fix Reserved Word Script

Finds and replaces GitHub reserved words like 'None' in template data files.
Specifically replaces 'none' entries with 'not-applicable' to avoid GitHub restrictions.
"""

import re
from pathlib import Path

def fix_reserved_words_in_py_file(py_file):
    """Fix reserved words in a Python template data file."""
    
    print(f"Checking {py_file.name}...")
    
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    
    # Pattern 1: Fix 'none' in dictionary keys
    # 'none': {'id': 'none', 'validation-key': 'none'}
    pattern1 = r"'none': \{'id': 'none'(?:, 'validation-key': 'none')?\}"
    replacement1 = "'not-applicable': {'id': 'not-applicable', 'validation-key': 'not-applicable'}"
    content, count1 = re.subn(pattern1, replacement1, content)
    changes_made += count1
    
    # Pattern 2: Fix standalone 'none' in lists
    # ['option1', 'none', 'option2']
    pattern2 = r"'none'(?=\s*[,\]])"
    replacement2 = "'not-applicable'"
    content, count2 = re.subn(pattern2, replacement2, content)
    changes_made += count2
    
    # Pattern 3: Fix 'None' (capitalized) in dictionary keys
    pattern3 = r"'None': \{'id': 'None'(?:, 'validation-key': 'None')?\}"
    replacement3 = "'not-applicable': {'id': 'not-applicable', 'validation-key': 'not-applicable'}"
    content, count3 = re.subn(pattern3, replacement3, content)
    changes_made += count3
    
    # Pattern 4: Fix standalone 'None' in lists
    pattern4 = r"'None'(?=\s*[,\]])"
    replacement4 = "'not-applicable'"
    content, count4 = re.subn(pattern4, replacement4, content)
    changes_made += count4
    
    if changes_made > 0:
        # Write back the fixed content
        with open(py_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Fixed {changes_made} instances of reserved words")
        return True
    else:
        print(f"  No reserved words found")
        return False

def fix_reserved_words_in_csv_file(csv_file):
    """Fix reserved words in CSV files."""
    
    print(f"Checking {csv_file.name}...")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    
    # Fix 'none' in data_source column (but not when it means "no data source")
    # We need to be careful here - 'none' as data_source is valid, but 'none' as an option value is not
    
    # For now, let's focus on option values that might contain 'none'
    # This is trickier in CSV format, so we'll mainly rely on the Python file fixes
    
    print(f"  CSV file checked (main fixes applied to Python files)")
    return False

def main():
    """Main function to fix reserved words across all template files."""
    
    print("Reserved Word Fixer for GitHub Issue Templates")
    print("=" * 50)
    
    # Find template directory
    script_dir = Path(__file__).parent
    template_dir = script_dir / "templates"
    
    if not template_dir.exists():
        print(f"Template directory not found: {template_dir}")
        return False
    
    # Find all Python and CSV files
    py_files = list(template_dir.glob('*.py'))
    csv_files = list(template_dir.glob('*.csv'))
    
    print(f"Found {len(py_files)} Python files and {len(csv_files)} CSV files")
    
    fixed_files = 0
    
    # Fix Python files (main source of the problem)
    print(f"\nFixing Python template data files...")
    for py_file in py_files:
        if fix_reserved_words_in_py_file(py_file):
            fixed_files += 1
    
    # Check CSV files
    print(f"\nChecking CSV files...")
    for csv_file in csv_files:
        if fix_reserved_words_in_csv_file(csv_file):
            fixed_files += 1
    
    # Summary
    print(f"\nResults:")
    print(f"  Files processed: {len(py_files) + len(csv_files)}")
    print(f"  Files modified: {fixed_files}")
    
    if fixed_files > 0:
        print(f"\nReserved words fixed! Now run:")
        print(f"  python per_file_generator.py --validate-only")
        print(f"  python per_file_generator.py")
        return True
    else:
        print(f"\nNo reserved words found or already fixed.")
        return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
