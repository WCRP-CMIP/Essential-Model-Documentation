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
    
    # Directory structure under 10_EMD_Repository
    explore_dir = DOCS_DIR / "10_EMD_Repository"
    
    directories = [
        (explore_dir / "05_Horizontal_Computational_Grids", "Horizontal Computational Grids", "Horizontal grid configurations used by model components."),
        (explore_dir / "06_Vertical_Computational_Grids", "Vertical Computational Grids", "Vertical coordinate systems and layer structures."),
        (explore_dir / "02_Model_Components", "Model Components", "Individual model components (atmosphere, ocean, land, etc.)."),
        (explore_dir / "03_Component_Families", "Component Families", "Families of related model components sharing common code."),
        (explore_dir / "04_Earth_System_Model_Families", "ESM Families", "Earth System Model families and lineages."),
        (explore_dir / "01_Models", "Models", "Complete coupled climate models (source_id)."),
    ]
    
    total = 0
    for dir_path, title, desc in directories:
        count = generate_index_for_directory(dir_path, title, desc)
        total += count
    
    print(f"\nTotal: {total} entries indexed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
else:
    main()
