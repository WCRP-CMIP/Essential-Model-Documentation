#!/usr/bin/env python3
"""
Generate index pages for HTML content directories.

Discovers all subdirectories under docs/ that contain .html files
and creates an index.md listing them with links.

Must run AFTER the HTML generators and BEFORE nav generation.
"""

import re
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
DOCS_DIR = SCRIPT_DIR.parent


def dir_to_title(name: str) -> str:
    """Convert a directory name to a display title.
    
    Strips leading numeric prefixes (e.g. '01_', '05_') and converts
    underscores/hyphens to spaces.
    """
    clean = re.sub(r'^\d+[-_.]', '', name)
    return clean.replace('_', ' ').replace('-', ' ')


def generate_index_for_directory(dir_path: Path) -> int:
    """Generate an index.md for a directory of HTML files."""
    html_files = sorted(dir_path.glob("*.html"))
    if not html_files:
        return 0

    title = dir_to_title(dir_path.name)

    lines = [
        f"# {title}",
        "",
        f"**Total entries:** {len(html_files)}",
        "",
        "---",
        "",
    ]

    for html_file in html_files:
        display_name = html_file.stem.replace("-", " ").replace("_", " ").title()
        lines.append(f"- [{display_name}]({html_file.name})")

    lines.extend([
        "",
        "---",
        "",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*"
    ])

    index_path = dir_path / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  {dir_path.name}/index.md — {len(html_files)} entries")

    return len(html_files)


def main():
    print("Index Page Generator")
    print("=" * 40)

    total = 0

    # Walk all subdirectories under docs/ and index any that contain .html files
    for subdir in sorted(DOCS_DIR.rglob("*")):
        if not subdir.is_dir():
            continue
        if subdir.name.startswith("."):
            continue
        if any(subdir.glob("*.html")):
            total += generate_index_for_directory(subdir)

    print(f"\nTotal: {total} entries indexed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
else:
    main()
