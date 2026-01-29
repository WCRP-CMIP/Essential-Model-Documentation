#!/usr/bin/env python3
"""
Process JSON summary files from ./summaries/ and generate documentation pages.

This hook reads JSON files from the summaries/ directory at project root
and generates formatted markdown documentation in docs/data-summaries/.
"""

import json
import re
import shutil
from pathlib import Path
from datetime import datetime


# Configuration
CONFIG = {
    'summaries_dir': 'summaries',           # Relative to project root
    'output_dir': 'data-summaries',         # Relative to docs dir
    'max_columns': 10,                       # Max columns in tables
    'max_cell_length': 50,                   # Max chars per cell
}


def on_pre_build(config):
    """Process summary JSON files before build."""
    print("\n" + "-" * 40)
    print("PROCESS SUMMARIES: Converting JSON to docs")
    print("-" * 40)
    
    docs_dir = Path(config['docs_dir'])
    project_root = docs_dir.parent
    summaries_dir = project_root / CONFIG['summaries_dir']
    
    if not summaries_dir.exists():
        print(f"ℹ️  No {CONFIG['summaries_dir']}/ directory found")
        return
    
    json_files = list(summaries_dir.glob('*.json'))
    if not json_files:
        print(f"ℹ️  No JSON files in {CONFIG['summaries_dir']}/")
        return
    
    print(f"📁 Found {len(json_files)} summary JSON files")
    
    output_dir = docs_dir / CONFIG['output_dir']
    
    # Clear output directory if it exists
    if output_dir.exists():
        print(f"🗑️  Clearing {CONFIG['output_dir']}/ directory")
        shutil.rmtree(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create json subdirectory for downloadable files
    json_output_dir = output_dir / 'json'
    json_output_dir.mkdir(parents=True, exist_ok=True)
    
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
            
            # Copy JSON file to output directory for downloads
            shutil.copy2(json_file, json_output_dir / json_file.name)
            
            # Generate documentation page (download path relative to the md file)
            page_content = generate_summary_page(json_file, data)
            page_name = json_file.stem
            
            output_path = output_dir / f"{page_name}.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(page_content)
            
            # Extract info for index
            description, record_count = extract_summary_info(data)
            index_lines.append(f"| [{page_name}]({page_name}.md) | {description} | {record_count} |")
            print(f"   ✅ {json_file.name}")
            
        except Exception as e:
            print(f"   ❌ Error processing {json_file.name}: {e}")
    
    # Write index
    index_lines.append(f"\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    with open(output_dir / 'index.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(index_lines))
    
    print(f"✅ Generated {len(json_files)} summary pages in {CONFIG['output_dir']}/")
    print(f"✅ Copied {len(json_files)} JSON files to {CONFIG['output_dir']}/json/")
    print("-" * 40 + "\n")


def extract_summary_info(data):
    """Extract description and record count from data."""
    description = "Summary data"
    record_count = 0
    
    if isinstance(data, dict):
        data_keys = [k for k in data.keys() if k != 'Header']
        if data_keys:
            first_key = data_keys[0]
            first_data = data[first_key]
            if isinstance(first_data, dict):
                record_count = len(first_data)
            elif isinstance(first_data, list):
                record_count = len(first_data)
            description = format_key_name(first_key)
    
    return description, record_count


def generate_summary_page(json_file, data):
    """Generate a markdown page from a JSON summary file."""
    lines = [f"# {format_key_name(json_file.stem)}\n"]
    lines.append(f"**Source:** `{json_file.name}`\n")
    
    # Download link path - points to json/ subfolder (relative from the md file location)
    download_path = f"json/{json_file.name}"
    
    if isinstance(data, dict):
        # Process Header separately (collapsible)
        if 'Header' in data:
            lines.extend(format_header_section(data['Header']))
        
        # Process data sections
        for section_key in [k for k in data.keys() if k != 'Header']:
            section_data = data[section_key]
            lines.append(f"## {format_key_name(section_key)}\n")
            
            if isinstance(section_data, dict):
                if section_data and all(isinstance(v, dict) for v in section_data.values()):
                    lines.extend(format_records_table(section_data, download_path))
                else:
                    lines.extend(format_simple_dict(section_data))
            elif isinstance(section_data, list):
                lines.extend(format_list_table(section_data, download_path))
            else:
                lines.append(f"```\n{section_data}\n```\n")
    
    elif isinstance(data, list):
        lines.append("## Data\n")
        lines.extend(format_list_table(data, download_path))
    
    return '\n'.join(lines)


def format_header_section(header):
    """Format header as collapsible section."""
    lines = [
        "## Metadata\n",
        '<details markdown="1">',
        "<summary>Click to expand header information</summary>",
        "",  # Blank line required for markdown parsing inside details
        "| Property | Value |",
        "|----------|-------|"
    ]
    
    if isinstance(header, dict):
        for key, value in header.items():
            lines.append(f"| {format_key_name(key)} | {escape_markdown(str(value)[:100])} |")
    
    lines.append("")  # Blank line before closing tag
    lines.append("</details>")
    lines.append("")  # Blank line after
    return lines


def format_records_table(data, download_path=None):
    """Format a dictionary of records as a table."""
    if not data:
        return ["*No data*\n"]
    
    # Collect all keys from all records
    all_keys = set()
    for record in data.values():
        if isinstance(record, dict):
            all_keys.update(record.keys())
    
    keys = sorted(list(all_keys))[:CONFIG['max_columns']]
    
    lines = [
        "| ID | " + " | ".join(format_key_name(k) for k in keys) + " |",
        "|---|" + "|".join("---" for _ in keys) + "|"
    ]
    
    for record_id, record in sorted(data.items()):
        row = f"| **{record_id}** |"
        for key in keys:
            value = record.get(key, "")
            formatted = format_cell_value(value)
            row += f" {formatted} |"
        lines.append(row)
    
    # Add record count and download link on same line
    record_text = f"*{len(data)} records*"
    if download_path:
        lines.append(f'\n<div class="table-footer"><span>{record_text}</span><a href="{download_path}" download class="download-btn" title="Download JSON">⬇</a></div>\n')
    else:
        lines.append(f"\n{record_text}\n")
    return lines


def format_simple_dict(data):
    """Format a simple dictionary as a key-value table."""
    lines = [
        "| Property | Value |",
        "|----------|-------|"
    ]
    for key, value in data.items():
        formatted = format_cell_value(value)
        lines.append(f"| {format_key_name(key)} | {formatted} |")
    lines.append("")
    return lines


def format_list_table(data, download_path=None):
    """Format a list as a table."""
    if not data:
        return ["*Empty list*\n"]
    
    if all(isinstance(item, dict) for item in data):
        # List of dicts - get all keys
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        keys = sorted(list(all_keys))[:CONFIG['max_columns']]
        
        lines = [
            "| # | " + " | ".join(format_key_name(k) for k in keys) + " |",
            "|---|" + "|".join("---" for _ in keys) + "|"
        ]
        
        for i, item in enumerate(data[:100], 1):
            row = f"| {i} |"
            for key in keys:
                value = item.get(key, "")
                row += f" {format_cell_value(value)} |"
            lines.append(row)
        
        if len(data) > 100:
            record_text = f"*Showing first 100 of {len(data)} items*"
        else:
            record_text = f"*{len(data)} items*"
    else:
        # Simple list
        lines = ["| # | Value |", "|---|-------|"]
        for i, item in enumerate(data[:100], 1):
            lines.append(f"| {i} | {format_cell_value(item)} |")
        
        if len(data) > 100:
            record_text = f"*Showing first 100 of {len(data)} items*"
        else:
            record_text = f"*{len(data)} items*"
    
    # Add record count and download link
    if download_path:
        lines.append(f'\n<div class="table-footer"><span>{record_text}</span><a href="{download_path}" download class="download-btn" title="Download JSON">⬇</a></div>\n')
    else:
        lines.append(f"\n{record_text}\n")
    
    return lines


def format_cell_value(value):
    """Format a value for display in a table cell."""
    if value is None or value == "":
        return "*—*"
    elif isinstance(value, bool):
        return "✓" if value else "✗"
    elif isinstance(value, list):
        if len(value) > 3:
            display = ", ".join(str(v) for v in value[:3]) + "..."
        else:
            display = ", ".join(str(v) for v in value)
        return escape_markdown(display[:CONFIG['max_cell_length']])
    elif isinstance(value, dict):
        return f"*{len(value)} items*"
    else:
        return escape_markdown(str(value)[:CONFIG['max_cell_length']])


def format_key_name(key):
    """Format a JSON key for display."""
    name = str(key)
    # Handle nested keys with dots
    if '.' in name:
        parts = name.split('.')
        return ' → '.join(p.replace('_', ' ').replace('-', ' ').title() for p in parts)
    return name.replace('_', ' ').replace('-', ' ').title()


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
