#!/usr/bin/env python3
"""
Pre-build hook: clean build directory.
Includes an on_page_content hook that rewrites the SVG Virgil font URL to be
relative to each page's location, so it works on any deployment (mipcvs.dev,
GitHub Pages, local dev) without hardcoding a base URL.
"""

import shutil
from pathlib import Path

# Placeholder used in source markdown — replaced at build time.
_FONT_PLACEHOLDER = "https://emd.mipcvs.dev/docs/assets/Virgil.woff2"


def on_page_content(html, page, config, **kwargs):
    """
    Replace the hardcoded font URL with an absolute URL derived from site_url.
    The SVG @font-face is inline HTML, so relative paths resolve against the
    page URL which varies by depth — an absolute URL is the only safe option.
    """
    if _FONT_PLACEHOLDER not in html:
        return html

    site_url = config.get("site_url", "/").rstrip("/")
    font_url = f"{site_url}/assets/Virgil.woff2"
    return html.replace(_FONT_PLACEHOLDER, font_url)


def on_pre_build(config, **kwargs):
    """Clean build directory and remove old SUMMARY.md."""
    docs_dir = Path(config['docs_dir']).resolve()
    site_dir = Path(config['site_dir'])
    
    # Delete old SUMMARY.md to force regeneration
    summary_path = docs_dir / 'SUMMARY.md'
    if summary_path.exists():
        summary_path.unlink()
    
    # Clean old build
    if site_dir.exists():
        shutil.rmtree(site_dir)
    
    site_dir.mkdir(parents=True, exist_ok=True)
