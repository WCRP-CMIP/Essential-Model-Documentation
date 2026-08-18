#!/usr/bin/env python3
"""
Scan all JSON files in the repo and rewrite any that contain unescaped control characters.
RFC 7159 compliance: Control characters (U+0000–U+001F) must be escaped.

Usage:
    python3 sanitize_all_json.py [--dry-run] [--verbose]

Options:
    --dry-run    Show what would be fixed, don't write changes
    --verbose    Print details for every file processed
"""

import json
import sys
import os
import re
import argparse
from pathlib import Path
from typing import Tuple, Set, Optional


def _escape_control_chars_in_json(text: str) -> str:
    """
    Escape control characters (U+0000–U+001F) only within JSON string values.
    Leaves JSON structure intact.
    """
    result = []
    in_string = False
    escape_next = False
    i = 0
    
    while i < len(text):
        char = text[i]
        code = ord(char)
        
        # Track if we're inside a JSON string value
        if char == '"' and not escape_next:
            in_string = not in_string
            result.append(char)
        elif escape_next:
            # Already escaped, pass through
            result.append(char)
            escape_next = False
        elif char == '\\' and in_string:
            escape_next = True
            result.append(char)
        elif in_string and 0 <= code <= 0x1F:
            # Control character inside a string - escape it
            if char == '\n':
                result.append('\\n')
            elif char == '\t':
                result.append('\\t')
            elif char == '\r':
                result.append('\\r')
            elif char == '\b':
                result.append('\\b')
            elif char == '\f':
                result.append('\\f')
            else:
                result.append(f'\\u{code:04x}')
        else:
            result.append(char)
        
        i += 1
    
    return ''.join(result)


def _sanitize_value(value):
    """
    Recursively sanitize all strings in a data structure (dict/list/str).
    Ensures control chars are properly escaped before JSON serialization.
    """
    if isinstance(value, str):
        # Re-serialize and parse to ensure proper escaping via json module
        return json.loads(json.dumps(value))
    elif isinstance(value, dict):
        return {k: _sanitize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_sanitize_value(v) for v in value]
    return value


def check_json_compliance(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a JSON file is RFC 7159 compliant (no unescaped control chars).
    
    Returns:
        (is_compliant, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return False, "Empty file"
        
        json.loads(content)
        return True, None
    
    except json.JSONDecodeError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error: {e}"


def sanitize_json_file(file_path: str, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Load a JSON file, sanitize control characters, and rewrite it.
    
    Strategy:
    1. Try to parse as-is
    2. If control char error, escape chars in string values and retry
    3. Recursively sanitize all values
    4. Write back
    
    Returns:
        (success, message)
    """
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if not text.strip():
            return False, "Empty file - skipped"
        
        # Try to parse
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            error_msg = str(e)
            
            # Check if it's a control character error
            if 'control character' in error_msg.lower():
                # Strategy: escape control chars only in string values
                escaped_text = _escape_control_chars_in_json(text)
                try:
                    data = json.loads(escaped_text)
                except json.JSONDecodeError as e2:
                    # Still failing - try a more aggressive approach
                    # Replace literal control chars globally
                    sanitized_text = text
                    for code in range(0x00, 0x20):
                        char = chr(code)
                        if code == 0x0A:  # \n
                            sanitized_text = sanitized_text.replace(char, '\\n')
                        elif code == 0x09:  # \t
                            sanitized_text = sanitized_text.replace(char, '\\t')
                        elif code == 0x0D:  # \r
                            sanitized_text = sanitized_text.replace(char, '\\r')
                        elif code == 0x08:  # \b
                            sanitized_text = sanitized_text.replace(char, '\\b')
                        elif code == 0x0C:  # \f
                            sanitized_text = sanitized_text.replace(char, '\\f')
                        else:
                            sanitized_text = sanitized_text.replace(char, f'\\u{code:04x}')
                    
                    try:
                        data = json.loads(sanitized_text)
                    except json.JSONDecodeError as e3:
                        return False, f"Failed after sanitization: {str(e3)[:80]}"
            else:
                # Other JSON errors (malformed structure, etc.)
                return False, f"JSON error: {error_msg[:80]}"
        
        # Recursively sanitize all string values
        data = _sanitize_value(data)
        
        if not dry_run:
            # Write back with proper formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write('\n')  # Trailing newline
        
        return True, "Fixed and rewritten"
    
    except Exception as e:
        return False, f"Unexpected error: {str(e)[:80]}"


def main():
    parser = argparse.ArgumentParser(
        description='Sanitize all JSON files in the repo for RFC 7159 compliance'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be fixed without writing')
    parser.add_argument('--verbose', action='store_true',
                        help='Print details for every file')
    parser.add_argument('--root', default=None,
                        help='Root directory to scan (default: repo root)')
    args = parser.parse_args()
    
    # Determine repo root
    if args.root:
        repo_root = Path(args.root)
    else:
        # Try to find .git directory to locate repo root
        current = Path.cwd()
        while current != current.parent:
            if (current / '.git').exists():
                repo_root = current
                break
            current = current.parent
        else:
            # Fallback: use the directory containing this script
            repo_root = Path(__file__).parent.parent.parent
    
    repo_root = repo_root.resolve()
    print(f"📁 Scanning repo: {repo_root}", flush=True)
    print(f"{'[DRY RUN]' if args.dry_run else '[WRITE MODE]'}", flush=True)
    print()
    
    # Find all .json files
    json_files = list(repo_root.rglob('*.json'))
    
    # Exclude certain directories
    exclude_dirs = {'.git', 'node_modules', 'build', 'dist', '__pycache__', '.github/workflows'}
    filtered_files = [
        f for f in json_files
        if not any(excluded in f.parts for excluded in exclude_dirs)
    ]
    
    print(f"Found {len(filtered_files)} JSON files to check\n", flush=True)
    
    compliant = 0
    non_compliant = 0
    failed = 0
    fixed = []
    
    for i, file_path in enumerate(filtered_files, 1):
        relative_path = file_path.relative_to(repo_root)
        
        is_compliant, error = check_json_compliance(str(file_path))
        
        if is_compliant:
            compliant += 1
            if args.verbose:
                print(f"  ✓ {relative_path}")
        else:
            non_compliant += 1
            print(f"  ⚠ {relative_path}")
            if args.verbose and error:
                print(f"     Problem: {error[:100]}")
            
            # Try to fix it
            success, msg = sanitize_json_file(str(file_path), dry_run=args.dry_run)
            if success:
                fixed.append((relative_path, msg))
                print(f"     → {msg} {'(dry run)' if args.dry_run else '✓'}")
            else:
                failed += 1
                print(f"     ❌ Cannot fix: {msg[:80]}")
        
        # Progress indicator
        if (i % 50) == 0:
            print(f"  ... processed {i}/{len(filtered_files)}", flush=True)
    
    # Summary
    print("\n" + "=" * 70, flush=True)
    print("SUMMARY", flush=True)
    print("=" * 70, flush=True)
    print(f"Total files scanned:    {len(filtered_files)}", flush=True)
    print(f"✓ Compliant:            {compliant}", flush=True)
    print(f"⚠ Non-compliant:        {non_compliant}", flush=True)
    print(f"✅ Successfully fixed:   {len(fixed)}", flush=True)
    print(f"❌ Failed to fix:        {failed}", flush=True)
    
    if fixed:
        print("\n📝 Files that were fixed:", flush=True)
        for path, msg in fixed:
            print(f"  ✓ {path}", flush=True)
    
    if failed > 0:
        print(f"\n⚠️  {failed} file(s) could not be auto-fixed (may need manual review)", flush=True)
    
    if args.dry_run and fixed:
        print(f"\n💡 Re-run WITHOUT --dry-run to apply {len(fixed)} fixes", flush=True)
    
    print()
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
