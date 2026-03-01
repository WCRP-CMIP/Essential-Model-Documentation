#!/usr/bin/env python3
"""
generate_nav.py — MkDocs hook.

on_files  : inject every generated .html/.md file from docs/ output dirs
            into the MkDocs file collection so they are copied to site/.
            .html files are injected with use_directory_urls=False so they
            are served at their literal path (e.g. Similarity.html stays
            at /…/Similarity.html, not /…/Similarity/index.html).
on_config : no-op.
"""

import re
from pathlib import Path


# Files/dirs to never inject
_SKIP = {
    'scripts', 'assets', 'stylesheets', '__pycache__',
    'Visualizations', 'links.yml', 'json', 'nav_order.json',
}

# Top-level docs/ dirs that are pure static (never contain generated pages)
_STATIC = {'assets', 'stylesheets', 'scripts', 'json'}


def on_files(files, config):
    """
    Scan all non-static top-level dirs under docs/ for generated files and
    inject any that MkDocs hasn't already picked up.

    .html files → injected with use_directory_urls=False so the file is
                  served at its literal URL (critical for Similarity.html).
    .md files   → injected with the site's use_directory_urls setting.
    """
    from mkdocs.structure.files import File

    docs_dir = Path(config['docs_dir']).resolve()
    site_dir = Path(config['site_dir']).resolve()
    use_dir  = config.get('use_directory_urls', True)

    # Remove bare index.html if index.md also exists (shadcn artefact)
    conflict = [
        f for f in files
        if f.src_path == 'index.html' and (docs_dir / 'index.md').exists()
    ]
    for f in conflict:
        files._files.remove(f)  # type: ignore[attr-defined]

    existing = {f.src_path for f in files}
    added    = 0

    for top in sorted(docs_dir.iterdir()):
        if top.name in _STATIC or top.name in _SKIP or top.name.startswith('.'):
            continue
        if not top.is_dir():
            continue
        for fpath in top.rglob('*'):
            if fpath.is_dir():
                continue
            if fpath.suffix not in ('.html', '.md'):
                continue
            src = str(fpath.relative_to(docs_dir))
            if src in existing:
                continue
            # .html files must NOT use directory URLs — they are already
            # rendered HTML and should be served at their literal path.
            file_use_dir = False if fpath.suffix == '.html' else use_dir
            files.append(File(src, str(docs_dir), str(site_dir), file_use_dir))
            existing.add(src)
            added += 1

    if added:
        print(f'  [generate_nav] Injected {added} generated files')

    return files


def on_config(config):
    return config
