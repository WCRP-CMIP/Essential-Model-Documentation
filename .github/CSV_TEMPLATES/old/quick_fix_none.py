#!/usr/bin/env python3
"""
Quick fix for reserved word 'none' in all template files
"""

from pathlib import Path
import re

def fix_file(file_path):
    """Fix reserved words in a single file."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix 'none' in vertical coordinates to 'no-vertical-dimension'
    content = re.sub(r"'none': \{'id': 'none'", "'no-vertical-dimension': {'id': 'no-vertical-dimension'", content)
    
    # Fix 'none' in horizontal grid types to 'no-horizontal-grid'  
    content = re.sub(r"'none': \{'id': 'none'\}", "'no-horizontal-grid': {'id': 'no-horizontal-grid'}", content)
    
    # Fix 'none' in calendars to 'no-calendar'
    content = re.sub(r"'none': \{'id': 'none', 'validation-key': 'none'\}", "'no-calendar': {'id': 'no-calendar', 'validation-key': 'no-calendar'}", content)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    template_dir = Path(__file__).parent / "templates"
    py_files = list(template_dir.glob('*.py'))
    
    print("Fixing reserved word 'none' in template files...")
    
    fixed = 0
    for py_file in py_files:
        if fix_file(py_file):
            print(f"Fixed {py_file.name}")
            fixed += 1
        else:
            print(f"No changes needed in {py_file.name}")
    
    print(f"\nFixed {fixed} files")
    return fixed > 0

if __name__ == '__main__':
    main()
