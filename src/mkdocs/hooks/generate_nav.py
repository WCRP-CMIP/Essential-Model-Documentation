#!/usr/bin/env python3
"""
Navigation generation hook for MkDocs.
- on_config : generates SUMMARY.md (kept for reference)
- on_files  : scans ALL script-generated HTML/MD files and injects them into
              the MkDocs file collection + rebuilds the nav dynamically.
              Runs AFTER gen-files plugin so every generated file is on disk.
"""

import os
import re
import yaml
from pathlib import Path


# ── Directories produced by docs/scripts/*.py ────────────────────────────────
# Paths are relative to docs_dir.  Add new output dirs here as scripts grow.
GENERATED_DIRS = [
    "10_EMD_Repository/01_Models",
    "10_EMD_Repository/02_Model_Components",
    "10_EMD_Repository/03_Component_Families",
    "10_EMD_Repository/04_Earth_System_Model_Families",
    "10_EMD_Repository/05_Horizontal_Computational_Grids",
    "10_EMD_Repository/06_Vertical_Computational_Grids",
    "110_Data_Summaries",
]

# Dirs/files to ignore when scanning docs_dir
EXCLUDE = {'scripts', 'assets', 'stylesheets', '__pycache__', 'Visualizations',
           'SUMMARY.md', 'links.yml', 'json'}


# ─────────────────────────────────────────────────────────────────────────────
# on_files  — inject generated files + rebuild nav
# ─────────────────────────────────────────────────────────────────────────────

def on_files(files, config):
    """
    1. Remove any index.html that conflicts with index.md (shadcn theme artefact).
    2. Scan all GENERATED_DIRS for .html and .md files not yet known to MkDocs.
    3. Add missing files to the Files collection so they are copied to build.
    4. Rebuild config['nav'] from the full on-disk state of docs/.
    """
    from mkdocs.structure.files import File

    docs_dir  = Path(config['docs_dir']).resolve()
    site_dir  = Path(config['site_dir']).resolve()
    use_dir   = config.get('use_directory_urls', True)

    # Remove any bare index.html that conflicts with index.md
    conflicting = [f for f in files
                   if f.src_path == 'index.html' and
                   (docs_dir / 'index.md').exists()]
    for f in conflicting:
        files._files.remove(f)  # type: ignore[attr-defined]

    # Index existing src paths so we don't double-add
    existing = {f.src_path for f in files}
    added = 0

    for rel_dir in GENERATED_DIRS:
        abs_dir = docs_dir / rel_dir
        if not abs_dir.exists():
            continue
        for fpath in sorted(abs_dir.iterdir()):
            if fpath.suffix not in ('.html', '.md'):
                continue
            src = str(fpath.relative_to(docs_dir))
            if src in existing:
                continue
            mf = File(src, str(docs_dir), str(site_dir), use_dir)
            files.append(mf)
            existing.add(src)
            added += 1

    if added:
        print(f"  [generate_nav] Added {added} generated files to MkDocs collection")

    # Rebuild nav from current on-disk state
    config['nav'] = _build_nav(docs_dir)

    return files


# ─────────────────────────────────────────────────────────────────────────────
# on_config  — kept only to write SUMMARY.md (legacy / informational)
# ─────────────────────────────────────────────────────────────────────────────

def on_config(config):
    docs_dir = Path(config['docs_dir'])
    _write_summary(docs_dir)
    return config


# ─────────────────────────────────────────────────────────────────────────────
# Nav building
# ─────────────────────────────────────────────────────────────────────────────

def _strip_prefix(name):
    return re.sub(r'^\d+[-_.]', '', name)

def _sort_key(name):
    m = re.match(r'^(\d+)[-_.]', name.replace('.md','').replace('.html',''))
    return (int(m.group(1)), name.lower()) if m else (9999, name.lower())

def _title(name):
    name = _strip_prefix(name)
    name = re.sub(r'\.(md|html)$', '', name)
    name = re.sub(r'[_-]', ' ', name).strip()
    return name[0].upper() + name[1:] if name else name

def _build_nav(docs_dir):
    """Walk docs_dir and build a MkDocs nav list from what exists on disk."""

    def _scan(path, rel_base):
        items = []
        try:
            entries = sorted(path.iterdir(), key=lambda e: _sort_key(e.name))
        except PermissionError:
            return items

        for entry in entries:
            if entry.name in EXCLUDE or entry.name.startswith('.') or entry.name.startswith('_'):
                continue

            if entry.is_dir():
                children = _scan(entry, rel_base)
                if not children:
                    continue
                rel = str(entry.relative_to(rel_base)).replace(os.sep, '/')
                # Use index.md as section root if available
                index = rel + '/index.md'
                if (rel_base / (rel + '/index.md')).exists():
                    items.append({_title(entry.name): [{ 'Overview': index }] + children})
                else:
                    items.append({_title(entry.name): children})

            elif entry.suffix in ('.md', '.html') and entry.name != 'index.md':
                rel = str(entry.relative_to(rel_base)).replace(os.sep, '/')
                items.append({_title(entry.name): rel})

        return items

    # Root: index.md first, then everything else
    root = []
    if (docs_dir / 'index.md').exists():
        root.append({'Home': 'index.md'})

    root += _scan(docs_dir, docs_dir)
    return root


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY.md writer (legacy — not used by literate-nav but kept for reference)
# ─────────────────────────────────────────────────────────────────────────────

def _write_summary(docs_path):
    def _scan(path, base, indent=''):
        lines = []
        try:
            entries = sorted(path.iterdir(), key=lambda e: _sort_key(e.name))
        except PermissionError:
            return lines
        for entry in entries:
            if entry.name in EXCLUDE or entry.name.startswith('.') or entry.name.startswith('_'):
                continue
            if entry.name == 'index.md':
                continue
            rel = str(entry.relative_to(base)).replace(os.sep, '/')
            if entry.is_file() and entry.suffix in ('.md', '.html'):
                lines.append(f"{indent}- [{_title(entry.name)}]({rel})")
            elif entry.is_dir():
                sub = _scan(entry, base, indent + '  ')
                if sub:
                    if (entry / 'index.md').exists():
                        lines.append(f"{indent}- [{_title(entry.name)}]({rel}/index.md)")
                    else:
                        lines.append(f"{indent}- {_title(entry.name)}:")
                    lines += sub
        return lines

    nav_lines = []
    if (docs_path / 'index.md').exists():
        nav_lines.append('- [Home](index.md)')
    nav_lines += _scan(docs_path, docs_path)

    # Custom links
    links_path = docs_path / 'links.yml'
    if links_path.exists():
        try:
            import yaml as _yaml
            data = _yaml.safe_load(links_path.read_text())
            for link in (data or {}).get('links', []):
                if isinstance(link, dict) and 'title' in link and 'url' in link:
                    nav_lines.append(f"- [{link['title']}]({link['url']})")
        except Exception:
            pass

    (docs_path / 'SUMMARY.md').write_text('\n'.join(nav_lines), encoding='utf-8')


# ── parse_links_file / add_links_to_nav kept for any external callers ─────────
def parse_links_file(docs_dir):
    links_path = Path(docs_dir) / "links.yml"
    if not links_path.exists():
        return []
    try:
        import yaml as _yaml
        data = _yaml.safe_load(links_path.read_text())
        return (data or {}).get('links', [])
    except Exception:
        return []

def add_links_to_nav(nav_lines, links):
    for link in links:
        if isinstance(link, dict) and 'title' in link and 'url' in link:
            nav_lines.append(f"- [{link['title']}]({link['url']})")
    return nav_lines


# Legacy aliases kept so other hooks don't break
def clean_name(name):        return _strip_prefix(name)
def get_sort_key(name):      return _sort_key(name)
def clean_title_file(name):  return _title(name)
def clean_title_folder(name):return _title(name)
def generate_navigation(docs_path): _write_summary(docs_path)
