#!/usr/bin/env python3
"""
Navigation generation hook for MkDocs.
Generates SUMMARY.md for literate-nav plugin using on_config hook.
Keeps original paths with prefixes so MkDocs can find source files.
Post-build hook handles URL cleaning after site is built.
"""

import os
import re
import yaml
from pathlib import Path


def on_config(config):
    """Hook that runs BEFORE plugins - generates SUMMARY.md."""
    docs_dir = Path(config['docs_dir'])
    generate_navigation(docs_dir)
    return config


def clean_name(name):
    """Remove numeric prefix from name for display."""
    return re.sub(r'^\d+[-_.](?=\w)', '', name)


def clean_title_folder(name):
    """Convert folder name to display title."""
    name = clean_name(name)
    return name.replace('_', ' ').replace('-', ' ')


def clean_title_file(filename):
    """Convert filename to display title."""
    name = filename.replace('.md', '').replace('.html', '')
    name = clean_name(name)
    return name.replace('_', ' ').replace('-', ' ')


def get_sort_key(name):
    """Get sort key for ordering - unprefixed items sort last at 9999."""
    base = name.replace('.md', '').replace('.html', '')
    match = re.match(r'^(\d+)[-_.]', base)
    if match:
        return (int(match.group(1)), name.lower())
    return (9999, name.lower())


def parse_links_file(docs_dir):
    """Parse custom links from YAML file."""
    links_path = docs_dir / "links.yml"
    if not links_path.exists():
        return []
    
    try:
        with open(links_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data.get('links', []) if data else []
    except:
        return []


def add_links_to_nav(nav_lines, links):
    """Add links directly to navigation."""
    if not links:
        return nav_lines
    
    categories = {}
    root_links = []
    
    for link in links:
        if not isinstance(link, dict) or 'title' not in link or 'url' not in link:
            continue
        cat = link.get('category')
        if cat:
            categories.setdefault(cat, []).append(link)
        else:
            root_links.append(link)
    
    for link in root_links:
        nav_lines.append(f"- [{link['title']}]({link['url']})")
    
    for cat_name in sorted(categories.keys()):
        nav_lines.append(f'- {cat_name}:')
        for link in categories[cat_name]:
            nav_lines.append(f"  - [{link['title']}]({link['url']})")
    
    return nav_lines


def build_tree(docs_path, exclude=None):
    """Build directory tree with files and dirs as unified items.
    Uses ORIGINAL paths with prefixes - post_build.py handles URL cleaning."""
    if exclude is None:
        exclude = {'scripts', 'assets', 'stylesheets', '__pycache__', 'Visualizations'}
    
    items = []
    
    for item in docs_path.iterdir():
        if item.name.startswith('.') or item.name.startswith('_'):
            continue
        if item.name in exclude or item.name in ('SUMMARY.md', 'links.yml'):
            continue
        
        if item.is_file() and item.suffix in ('.md', '.html'):
            items.append({
                'type': 'file',
                'name': item.name,
                'path': item.name,
                'sort': get_sort_key(item.name)
            })
        elif item.is_dir():
            subtree = build_subtree(item, docs_path)
            if subtree:
                items.append({
                    'type': 'dir',
                    'name': item.name,
                    'children': subtree,
                    'sort': get_sort_key(item.name)
                })
    
    return items


def build_subtree(dir_path, base_path):
    """Build subtree recursively - excludes index.md (implicit_index handles it)."""
    items = []
    
    for item in dir_path.iterdir():
        if item.name.startswith('.') or item.name.startswith('_'):
            continue
        if item.name == 'index.md':
            continue
        
        rel = item.relative_to(base_path)
        
        if item.is_file() and item.suffix in ('.md', '.html'):
            # Keep original path WITH prefixes for MkDocs to find during build
            original_path = str(rel).replace(os.sep, '/')
            items.append({
                'type': 'file',
                'name': item.name,
                'path': original_path,
                'sort': get_sort_key(item.name)
            })
        elif item.is_dir():
            subtree = build_subtree(item, base_path)
            if subtree:
                items.append({
                    'type': 'dir',
                    'name': item.name,
                    'children': subtree,
                    'sort': get_sort_key(item.name)
                })
    
    return items


def items_to_nav(items, nav_lines, indent="", base_path=None):
    """Convert items to nav lines, sorted by numerical prefix.
    Uses original paths (with prefixes) - post_build.py cleans URLs after build."""
    for item in sorted(items, key=lambda x: x['sort']):
        if item['type'] == 'file':
            title = clean_title_file(item['name'])
            # Use original path WITH prefix - MkDocs needs it to find the file
            nav_lines.append(f"{indent}- [{title}]({item['path']})")
        else:
            title = clean_title_folder(item['name'])
            # Check if folder has index.md
            if base_path:
                folder_path = base_path / item['name']
                if (folder_path / 'index.md').exists():
                    # Make section header a clickable link to index.md
                    index_path = f"{item['name']}/index.md"
                    nav_lines.append(f'{indent}- [{title}]({index_path})')
                else:
                    # Just a section header
                    nav_lines.append(f'{indent}- {title}:')
            else:
                nav_lines.append(f'{indent}- {title}:')
            items_to_nav(item['children'], nav_lines, indent + "  ", base_path)


def generate_navigation(docs_path):
    """Generate SUMMARY.md with ORIGINAL paths (prefixed).
    Post-build hook will clean URLs and rename files AFTER build completes."""
    items = build_tree(docs_path)
    nav_lines = []
    
    # Separate index.md from other items
    index_item = None
    other_items = []
    
    for item in items:
        if item['type'] == 'file' and item['name'] == 'index.md':
            index_item = item
        else:
            other_items.append(item)
    
    # Add index.md first
    if index_item:
        nav_lines.append('- [Home](index.md)')
    
    # Add other items sorted by prefix
    items_to_nav(other_items, nav_lines, "", docs_path)
    
    # Add custom links from links.yml
    links = parse_links_file(docs_path)
    nav_lines = add_links_to_nav(nav_lines, links)
    
    # Write SUMMARY.md
    with open(docs_path / 'SUMMARY.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(nav_lines))
