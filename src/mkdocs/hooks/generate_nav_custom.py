#!/usr/bin/env python3
"""
Navigation generation hook for MkDocs.
Reads actual folder/file structure, preserves order by numeric prefix,
strips prefixes from display names only.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple


def strip_prefix(name: str) -> str:
    """Strip numeric prefix for display."""
    return re.sub(r'^\d+[-_.]', '', name)


def get_sort_key(name: str) -> Tuple[int, str]:
    """Get sort key: (prefix_number, cleaned_name). Unprefixed sorts last."""
    match = re.match(r'^(\d+)', name)
    if match:
        return (int(match.group(1)), strip_prefix(name).lower())
    return (9999, strip_prefix(name).lower())


def clean_title(name: str, is_dir: bool = False) -> str:
    """Convert name to display title."""
    clean = strip_prefix(name)
    if not is_dir:
        clean = clean.replace('.md', '').replace('.html', '')
    return clean.replace('_', ' ').replace('-', ' ').title()


def scan_directory(path: Path, base_path: Path, exclude: set = None) -> List[Dict]:
    """Scan directory, return sorted items with original paths."""
    if exclude is None:
        exclude = {'scripts', 'assets', 'stylesheets', '__pycache__', 'Visualizations', 'json'}
    
    items = []
    
    for item in sorted(path.iterdir(), key=lambda x: get_sort_key(x.name)):
        if item.name.startswith('.') or item.name.startswith('_'):
            continue
        if item.name in exclude or item.name == 'SUMMARY.md':
            continue
        
        if item.is_file() and item.suffix in ('.md', '.html'):
            rel_path = item.relative_to(base_path).as_posix()
            items.append({
                'type': 'file',
                'name': item.name,
                'path': rel_path,
                'display': clean_title(item.name),
                'sort_key': get_sort_key(item.name)
            })
        elif item.is_dir():
            children = scan_directory(item, base_path, exclude)
            if children or (item / 'index.md').exists():
                rel_path = item.relative_to(base_path).as_posix()
                items.append({
                    'type': 'dir',
                    'name': item.name,
                    'path': rel_path,
                    'display': clean_title(item.name, is_dir=True),
                    'children': children,
                    'sort_key': get_sort_key(item.name)
                })
    
    return sorted(items, key=lambda x: x['sort_key'])


def items_to_nav_lines(items: List[Dict], indent: str = "") -> List[str]:
    """Convert items to SUMMARY.md lines. Strip prefixes from both paths and display names."""
    lines = []
    
    for item in items:
        if item['type'] == 'file':
            # Strip prefix from path too
            clean_path = strip_prefix(item['path'].split('/')[-1])
            # Reconstruct path without prefixes
            path_parts = [strip_prefix(p) for p in item['path'].split('/')]
            clean_full_path = '/'.join(path_parts)
            lines.append(f"{indent}- [{item['display']}]({clean_full_path})")
        else:
            lines.append(f"{indent}- {item['display']}")
            
            if item['children']:
                child_lines = items_to_nav_lines(item['children'], indent + "  ")
                lines.extend(child_lines)
    
    return lines


def generate_navigation(docs_dir: Path) -> str:
    """Generate SUMMARY.md with stripped prefixes in display, original paths for MkDocs."""
    items = scan_directory(docs_dir, docs_dir)
    
    nav_lines = []
    
    # Separate and handle index.md
    index_item = None
    other_items = []
    
    for item in items:
        if item['type'] == 'file' and item['name'] == 'index.md':
            index_item = item
        else:
            other_items.append(item)
    
    if index_item:
        nav_lines.append(f"- [{index_item['display']}]({index_item['path']})")
    
    nav_lines.extend(items_to_nav_lines(other_items))
    
    return '\n'.join(nav_lines)
