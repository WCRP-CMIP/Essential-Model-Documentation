#!/usr/bin/env python3
"""
Pre-build hook: clean build directory.
Includes an on_page_content hook that rewrites SVG font URLs to be relative
to the site root, so they work in any deployment environment.
"""

import shutil
from pathlib import Path

# Placeholder used in source markdown; replaced at build time with the real URL.
_FONT_PLACEHOLDER = "https://emd.mipcvs.dev/docs/assets/Virgil.woff2"


def on_config(config, **kwargs):
    """Store the resolved font URL on the config object for later hooks."""
    site_url = config.get("site_url", "/").rstrip("/")
    config["_virgil_font_url"] = f"{site_url}/assets/Virgil.woff2"
    return config


def on_page_content(html, page, config, **kwargs):
    """Replace the hardcoded font URL with one derived from site_url."""
    font_url = config.get("_virgil_font_url", _FONT_PLACEHOLDER)
    if _FONT_PLACEHOLDER in html:
        html = html.replace(_FONT_PLACEHOLDER, font_url)
    return html


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
