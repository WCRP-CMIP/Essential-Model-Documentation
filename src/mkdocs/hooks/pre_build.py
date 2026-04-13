#!/usr/bin/env python3
"""
Pre-build hook: clean build directory.
Includes an on_page_content hook that:
  1. Rewrites the SVG Virgil font URL to be relative to each page.
  2. Replaces the hardcoded base_url (used by the search plugin) with a
     dynamically computed value so search works on any origin.
"""

import re
import shutil
from pathlib import Path

# Placeholder used in source markdown — replaced at build time.
_FONT_PLACEHOLDER = "https://emd.mipcvs.dev/docs/assets/Virgil.woff2"

# Matches the hardcoded base_url line the shadcn theme injects into <head>
_BASE_URL_RE = re.compile(r'const base_url = "[^"]*";')

# JS snippet: strips `depth` path segments from window.location to get site root.
# e.g. depth=1, page at /docs/Submission-Guide/ → base = /docs/
_BASE_URL_JS = """\
(function(){{
  var parts = window.location.pathname.split('/').filter(Boolean);
  parts.splice(parts.length - {depth});
  return window.location.origin + (parts.length ? '/' + parts.join('/') + '/' : '/');
}})()"""


def on_page_content(html, page, config, **kwargs):
    depth = len([p for p in (page.url or '').split('/') if p])

    # 1. Rewrite SVG font URL to be relative to this page
    if _FONT_PLACEHOLDER in html:
        prefix = '../' * depth if depth else ''
        html = html.replace(_FONT_PLACEHOLDER, f"{prefix}assets/Virgil.woff2")

    # 2. Replace hardcoded base_url with a dynamic one
    if _BASE_URL_RE.search(html):
        js = _BASE_URL_JS.format(depth=depth)
        html = _BASE_URL_RE.sub(f'const base_url = {js};', html, count=1)

    return html


def on_pre_build(config, **kwargs):
    """Clean build directory and remove old SUMMARY.md."""
    docs_dir = Path(config['docs_dir']).resolve()
    site_dir = Path(config['site_dir'])

    summary_path = docs_dir / 'SUMMARY.md'
    if summary_path.exists():
        summary_path.unlink()

    if site_dir.exists():
        shutil.rmtree(site_dir)

    site_dir.mkdir(parents=True, exist_ok=True)
