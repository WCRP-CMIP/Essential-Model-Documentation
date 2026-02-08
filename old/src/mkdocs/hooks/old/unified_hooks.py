#!/usr/bin/env python3
"""
Unified MkDocs Hooks for Essential Model Documentation
======================================================

This single file consolidates all build hooks:
1. Pre-build: Generate summaries and run scripts
2. Files: Process generated files for indexing
3. Page markdown: Inject content (README, etc.)
4. Navigation: Generate SUMMARY.md
5. Post-build: Index HTML files for search

Configuration is centralized at the top for easy customization.
"""

import os
import sys
import re
import json
import yaml
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

CONFIG = {
    # Directories to process for HTML search indexing
    'html_dirs': ['model', 'model_component', 'model_family', 'bidk'],
    
    # Directories to exclude from navigation
    'nav_exclude': {'scripts', 'assets', 'stylesheets', '__pycache__', 'technical'},
    
    # File extensions to include in navigation
    'nav_extensions': ('.md', '.html'),
    
    # Maximum text length for search indexing
    'max_search_text': 1000,
    
    # Summaries directory (relative to project root)
    'summaries_dir': 'summaries',
    
    # Output directory for generated summary docs
    'summaries_output': 'data-summaries',
    
    # Whether to inject README.md into index.md
    'inject_readme': True,
    
    # Tip marker to find in index.md for README injection
    'readme_tip_marker': '!!! tip "Documentation in progress"',
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def clean_title(filename):
    """Convert filename to display title."""
    name = filename.replace('.md', '').replace('.html', '')
    name = re.sub(r'^\d+[-_.](?=\w)', '', name)
    return name.replace('_', ' ').replace('-', ' ').title()


def get_sort_key(filename):
    """Get sort key for ordering files."""
    name = filename.replace('.md', '').replace('.html', '')
    match = re.match(r'^(\d+)[-_.]', name)
    if match:
        return (int(match.group(1)), filename)
    return (9999, filename)


def format_key_name(key):
    """Format a JSON key for display."""
    if '.' in key:
        parts = key.split('.')
        return ' → '.join(p.replace('_', ' ').title() for p in parts)
    return key.replace('_', ' ').title()


def escape_markdown(text):
    """Escape text for markdown table display."""
    if not text:
        return text
    content = str(text)
    content = content.replace('\n', ' ').replace('\r', ' ')
    content = re.sub(r'\s+', ' ', content)
    content = content.replace('|', '\\|')
    content = content.replace('`', '\\`')
    return content.strip()


# =============================================================================
# PRE-BUILD HOOK
# =============================================================================

def on_pre_build(config):
    """
    Pre-build hook: Execute generators and process summaries.
    """
    print("\n" + "=" * 60)
    print("PRE-BUILD: Processing summaries and running generators")
    print("=" * 60)
    
    docs_dir = Path(config['docs_dir'])
    project_root = docs_dir.parent
    
    # 1. Process JSON summaries
    process_summaries(project_root, docs_dir)
    
    # 2. Run generator scripts
    run_generator_scripts(docs_dir)
    
    print("=" * 60 + "\n")


def process_summaries(project_root, docs_dir):
    """Process JSON files in summaries/ directory and generate documentation."""
    summaries_dir = project_root / CONFIG['summaries_dir']
    
    if not summaries_dir.exists():
        print(f"ℹ️  No {CONFIG['summaries_dir']}/ directory found")
        return
    
    json_files = list(summaries_dir.glob('*.json'))
    if not json_files:
        print(f"ℹ️  No JSON files in {CONFIG['summaries_dir']}/")
        return
    
    print(f"📁 Found {len(json_files)} summary JSON files")
    
    output_dir = docs_dir / CONFIG['summaries_output']
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create index page
    index_lines = [
        "# Data Summaries\n",
        "This section contains formatted views of JSON summary files.\n",
        "## Available Summaries\n",
        "| File | Description | Records |",
        "|------|-------------|---------|"
    ]
    
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Generate documentation page
            page_content = generate_summary_page(json_file, data)
            page_name = json_file.stem
            
            output_path = output_dir / f"{page_name}.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(page_content)
            
            # Extract description for index
            description = "Summary data"
            record_count = 0
            
            if isinstance(data, dict):
                # Skip Header, count data keys
                data_keys = [k for k in data.keys() if k != 'Header']
                if data_keys:
                    first_data = data[data_keys[0]]
                    if isinstance(first_data, dict):
                        record_count = len(first_data)
                        description = f"{data_keys[0]} data"
            
            index_lines.append(f"| [{page_name}]({page_name}.md) | {description} | {record_count} |")
            print(f"   ✅ {json_file.name}")
            
        except Exception as e:
            print(f"   ❌ Error processing {json_file.name}: {e}")
    
    # Write index
    index_lines.append(f"\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    with open(output_dir / 'index.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(index_lines))
    
    print(f"✅ Generated {len(json_files)} summary pages")


def generate_summary_page(json_file, data):
    """Generate a markdown page from a JSON summary file."""
    lines = [f"# {json_file.stem.replace('_', ' ').title()}\n"]
    
    # Add file info
    lines.append(f"**Source:** `{json_file.name}`\n")
    
    if isinstance(data, dict):
        # Process Header separately
        if 'Header' in data:
            header = data['Header']
            lines.append("## Metadata\n")
            lines.append("<details>")
            lines.append("<summary>Click to expand header information</summary>\n")
            lines.append("| Property | Value |")
            lines.append("|----------|-------|")
            for key, value in header.items():
                lines.append(f"| {format_key_name(key)} | {escape_markdown(str(value)[:100])} |")
            lines.append("\n</details>\n")
        
        # Process data sections
        for section_key in [k for k in data.keys() if k != 'Header']:
            section_data = data[section_key]
            lines.append(f"## {format_key_name(section_key)}\n")
            
            if isinstance(section_data, dict):
                # Dictionary of records
                if section_data and all(isinstance(v, dict) for v in section_data.values()):
                    lines.extend(format_records_table(section_data))
                else:
                    lines.extend(format_simple_dict(section_data))
            elif isinstance(section_data, list):
                lines.extend(format_list_table(section_data))
            else:
                lines.append(f"```\n{section_data}\n```\n")
    
    return '\n'.join(lines)


def format_records_table(data):
    """Format a dictionary of records as a table."""
    if not data:
        return ["*No data*\n"]
    
    # Collect all keys
    all_keys = set()
    for record in data.values():
        if isinstance(record, dict):
            all_keys.update(record.keys())
    
    keys = sorted(list(all_keys))[:10]  # Limit columns
    
    lines = [
        "| ID | " + " | ".join(format_key_name(k) for k in keys) + " |",
        "|---|" + "|".join("---" for _ in keys) + "|"
    ]
    
    for record_id, record in sorted(data.items()):
        row = f"| **{record_id}** |"
        for key in keys:
            value = record.get(key, "")
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value[:3])
                if len(record.get(key, [])) > 3:
                    value += "..."
            row += f" {escape_markdown(str(value)[:50])} |"
        lines.append(row)
    
    lines.append(f"\n*{len(data)} records*\n")
    return lines


def format_simple_dict(data):
    """Format a simple dictionary as a table."""
    lines = [
        "| Property | Value |",
        "|----------|-------|"
    ]
    for key, value in data.items():
        lines.append(f"| {format_key_name(key)} | {escape_markdown(str(value)[:100])} |")
    return lines + [""]


def format_list_table(data):
    """Format a list as a table."""
    if not data:
        return ["*Empty list*\n"]
    
    if all(isinstance(item, dict) for item in data):
        # List of dicts
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        keys = sorted(list(all_keys))[:8]
        
        lines = [
            "| # | " + " | ".join(format_key_name(k) for k in keys) + " |",
            "|---|" + "|".join("---" for _ in keys) + "|"
        ]
        
        for i, item in enumerate(data[:100], 1):
            row = f"| {i} |"
            for key in keys:
                value = item.get(key, "")
                row += f" {escape_markdown(str(value)[:50])} |"
            lines.append(row)
        
        if len(data) > 100:
            lines.append(f"\n*Showing first 100 of {len(data)} items*")
    else:
        # Simple list
        lines = ["| # | Value |", "|---|-------|"]
        for i, item in enumerate(data[:100], 1):
            lines.append(f"| {i} | {escape_markdown(str(item)[:100])} |")
    
    return lines + [""]


def run_generator_scripts(docs_dir):
    """Run generator scripts in docs/scripts/."""
    scripts_dir = docs_dir / "scripts"
    
    if not scripts_dir.exists():
        print("ℹ️  No docs/scripts/ directory")
        return
    
    scripts = sorted(scripts_dir.glob("generate_*.py"))
    scripts = [s for s in scripts if not s.name.startswith('_')]
    
    if not scripts:
        print("ℹ️  No generate_*.py scripts found")
        return
    
    print(f"📜 Running {len(scripts)} generator script(s)")
    
    for script_path in scripts:
        print(f"   🔄 {script_path.name}...", end=" ")
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(scripts_dir),
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                print("✅")
            else:
                print(f"⚠️ (exit {result.returncode})")
        except subprocess.TimeoutExpired:
            print("❌ timeout")
        except Exception as e:
            print(f"❌ {e}")


# =============================================================================
# FILES HOOK
# =============================================================================

def on_files(files, config):
    """
    Files hook: Generate navigation and ensure files are indexed.
    """
    docs_dir = Path(config['docs_dir'])
    
    # Generate SUMMARY.md for literate-nav
    generate_navigation(docs_dir)
    
    return files


def generate_navigation(docs_dir):
    """Generate SUMMARY.md for navigation."""
    nav_lines = []
    
    # Home
    if (docs_dir / 'index.md').exists():
        nav_lines.append('- [Home](index.md)')
    
    # Build tree and convert to nav
    tree = build_nav_tree(docs_dir, docs_dir)
    
    # Root files first
    for f in sorted(tree['files'], key=lambda x: x['sort']):
        if f['name'] != 'index.md':
            nav_lines.append(f"- [{clean_title(f['name'])}]({f['path']})")
    
    # Then directories
    for name, subtree in sorted(tree['dirs'].items(), key=lambda x: get_sort_key(x[0])):
        nav_lines.append(f'- {clean_title(name)}:')
        tree_to_nav(subtree, nav_lines, "  ")
    
    # Custom links from links.yml
    links = parse_links_file(docs_dir)
    if links:
        for link in links:
            if isinstance(link, dict) and 'title' in link and 'url' in link:
                nav_lines.append(f"- [{link['title']}]({link['url']})")
    
    with open(docs_dir / 'SUMMARY.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(nav_lines))


def build_nav_tree(dir_path, base_path):
    """Build navigation tree recursively."""
    tree = {'files': [], 'dirs': {}}
    
    try:
        items = sorted(dir_path.iterdir())
    except PermissionError:
        return tree
    
    for item in items:
        if item.name.startswith('.') or item.name.startswith('_'):
            continue
        if item.name in CONFIG['nav_exclude']:
            continue
        if item.name in ('SUMMARY.md', 'links.yml'):
            continue
        
        rel = item.relative_to(base_path)
        
        if item.is_file() and item.suffix in CONFIG['nav_extensions']:
            tree['files'].append({
                'name': item.name,
                'path': str(rel).replace(os.sep, '/'),
                'sort': get_sort_key(item.name)
            })
        elif item.is_dir():
            subtree = build_nav_tree(item, base_path)
            if subtree['files'] or subtree['dirs']:
                tree['dirs'][item.name] = subtree
    
    return tree


def tree_to_nav(tree, nav_lines, indent=""):
    """Convert tree to navigation lines."""
    for f in sorted(tree['files'], key=lambda x: x['sort']):
        title = clean_title(f['name'])
        nav_lines.append(f"{indent}- [{title}]({f['path']})")
    
    for name, subtree in sorted(tree['dirs'].items(), key=lambda x: get_sort_key(x[0])):
        nav_lines.append(f'{indent}- {clean_title(name)}:')
        tree_to_nav(subtree, nav_lines, indent + "  ")


def parse_links_file(docs_dir):
    """Parse custom links from links.yml."""
    links_path = docs_dir / "links.yml"
    if not links_path.exists():
        return []
    try:
        with open(links_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data.get('links', []) if data else []
    except:
        return []


# =============================================================================
# PAGE MARKDOWN HOOK
# =============================================================================

def on_page_markdown(markdown, page, config, files):
    """
    Page markdown hook: Inject README content into index.md.
    """
    if not CONFIG['inject_readme']:
        return markdown
    
    # Only process index.md
    if page.file.src_path != 'index.md':
        return markdown
    
    tip_marker = CONFIG['readme_tip_marker']
    if tip_marker not in markdown:
        return markdown
    
    # Find README.md
    docs_dir = Path(config['docs_dir'])
    project_root = docs_dir.parent
    readme_path = project_root / 'README.md'
    
    if not readme_path.exists():
        return markdown
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read().strip()
        print(f"✅ Injecting README.md ({len(readme_content)} chars) into index.md")
    except Exception as e:
        print(f"⚠️  Error reading README.md: {e}")
        return markdown
    
    # Find end of tip section and inject
    lines = markdown.split('\n')
    new_lines = []
    in_tip = False
    injected = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        if tip_marker in line:
            in_tip = True
            continue
        
        if in_tip and not injected:
            # End of tip = non-indented non-empty line
            if line.strip() and not line.startswith('    '):
                new_lines.insert(-1, '')
                new_lines.insert(-1, '## Project Information')
                new_lines.insert(-1, '')
                new_lines.insert(-1, readme_content)
                new_lines.insert(-1, '')
                injected = True
    
    # If tip was at end of file
    if in_tip and not injected:
        new_lines.extend(['', '## Project Information', '', readme_content])
    
    return '\n'.join(new_lines)


# =============================================================================
# POST-BUILD HOOK
# =============================================================================

def on_post_build(config):
    """
    Post-build hook: Index HTML files for search.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("ℹ️  beautifulsoup4 not installed, HTML search indexing skipped")
        return
    
    site_dir = Path(config['site_dir'])
    docs_dir = Path(config['docs_dir'])
    search_index_path = site_dir / 'search' / 'search_index.json'
    
    if not search_index_path.exists():
        return
    
    with open(search_index_path, 'r', encoding='utf-8') as f:
        search_data = json.load(f)
    
    html_count = 0
    
    for html_dir in CONFIG['html_dirs']:
        src_dir = docs_dir / html_dir
        if not src_dir.exists():
            continue
        
        for html_file in src_dir.glob('*.html'):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                
                for tag in soup(['script', 'style']):
                    tag.decompose()
                
                # Extract title
                title = None
                for selector in ['h1', 'title', '.emd-title']:
                    elem = soup.select_one(selector)
                    if elem:
                        title = elem.get_text(strip=True)
                        break
                if not title:
                    title = html_file.stem.replace('-', ' ').title()
                
                # Extract text
                text = soup.get_text(separator=' ', strip=True)
                text = re.sub(r'\s+', ' ', text)[:CONFIG['max_search_text']]
                
                if 'docs' in search_data:
                    search_data['docs'].append({
                        'location': f"{html_dir}/{html_file.name}",
                        'title': title,
                        'text': text
                    })
                    html_count += 1
                    
            except Exception as e:
                print(f"⚠️  Could not index {html_file.name}: {e}")
    
    if html_count > 0:
        with open(search_index_path, 'w', encoding='utf-8') as f:
            json.dump(search_data, f, ensure_ascii=False)
        print(f"✅ HTML Search: Indexed {html_count} files")
