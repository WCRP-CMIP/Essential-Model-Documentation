#!/usr/bin/env python3
"""
Generate index pages for HTML content directories.

Creates index.md files for model_family/, model_component/, and model/ 
directories, listing all the generated HTML files with links.

Must run AFTER the HTML generators and BEFORE nav generation.
"""

import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
DOCS_DIR = SCRIPT_DIR.parent


def generate_index_for_directory(dir_path: Path, title: str, description: str) -> int:
    """Generate an index.md for a directory of HTML files."""
    if not dir_path.exists():
        print(f"  Directory not found: {dir_path}")
        return 0
    
    html_files = sorted(dir_path.glob("*.html"))
    if not html_files:
        print(f"  No HTML files in {dir_path.name}/")
        return 0
    
    # Build index content
    lines = [
        f"# {title}",
        "",
        description,
        "",
        f"**Total entries:** {len(html_files)}",
        "",
        "---",
        "",
    ]
    
    # List files as links
    for html_file in html_files:
        name = html_file.stem
        display_name = name.replace("-", " ").replace("_", " ").title()
        lines.append(f"- [{display_name}]({html_file.name})")
    
    lines.extend([
        "",
        "---",
        "",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*"
    ])
    
    # Write index
    index_path = dir_path / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Created {dir_path.name}/index.md with {len(html_files)} entries")
    
    return len(html_files)


def main():
    print("Index Page Generator")
    print("=" * 40)
    
    directories = [
        ("model_family", "Model Families", "Families of related climate models and components."),
        ("model_component", "Model Components", "Individual model components (atmosphere, ocean, land, etc.)."),
        ("model", "Models", "Complete coupled climate models (source_id)."),
    ]
    
    total = 0
    for dir_name, title, desc in directories:
        dir_path = DOCS_DIR / dir_name
        count = generate_index_for_directory(dir_path, title, desc)
        total += count
    
    print(f"\nTotal: {total} entries indexed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
