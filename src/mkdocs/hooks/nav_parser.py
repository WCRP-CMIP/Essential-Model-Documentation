#!/usr/bin/env python3
"""
Plugin to parse SUMMARY.md and inject nav structure into MkDocs config.
Bypasses shadcn's auto nav generation by providing explicit nav structure.
"""

import re
from pathlib import Path
from typing import List, Dict, Any


def parse_summary_md(summary_path: Path) -> List[Dict[str, Any]]:
    """Parse SUMMARY.md into nav structure."""
    if not summary_path.exists():
        return []
    
    content = summary_path.read_text(encoding='utf-8')
    nav = []
    stack = [nav]  # Stack of list contexts for nesting
    
    for line in content.split('\n'):
        # Skip empty lines and header
        if not line.strip() or line.startswith('#'):
            continue
        
        # Calculate indent level
        indent = (len(line) - len(line.lstrip())) // 2
        
        # Get current list at this indent level
        while len(stack) > indent + 1:
            stack.pop()
        while len(stack) <= indent:
            stack.append([])
        
        current_list = stack[indent]
        
        # Parse line
        if '[' in line and ']' in line and '(' in line:
            # Link: - [Title](path)
            match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)
            if match:
                title, path = match.groups()
                current_list.append({'title': title, 'url': path})
        elif '-' in line:
            # Section header: - Title or - Title:
            title = line.split('-', 1)[1].strip().rstrip(':')
            item = {'title': title, 'children': []}
            current_list.append(item)
            # Push new list for children
            if len(stack) <= indent + 1:
                stack.append(item['children'])
            else:
                stack[indent + 1] = item['children']
    
    return nav


def on_config(config):
    """MkDocs on_config hook - parse SUMMARY.md and inject nav."""
    docs_dir = Path(config['docs_dir'])
    summary_path = docs_dir / 'SUMMARY.md'
    
    if summary_path.exists():
        nav = parse_summary_md(summary_path)
        # Store in config for templates to access
        config['nav_data'] = nav
        print(f"[nav_parser] Parsed SUMMARY.md with {len(nav)} items")
    
    return config
