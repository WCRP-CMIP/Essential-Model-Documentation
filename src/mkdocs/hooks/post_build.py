#!/usr/bin/env python3
"""
post_build.py
=============
Runs after MkDocs has built the site.

Steps
-----
1.  Strip numeric prefixes from every dir/file in site_dir
    (e.g. 10_EMD_Repository → EMD_Repository, 001_Similarity → Similarity).
    When the target already exists as a directory, *merge* contents into it.
2.  Load docs/nav_order.json.
3.  Scan the now-clean site_dir (full hierarchy) and merge every discovered
    item into nav_order.json.  New items get value null.  Existing values
    are never overwritten.  Overwrite the JSON.
4.  Build the sidebar nav from nav_order.json using the value rules:
      positive int  → show, ordered by that number (ascending) first
      null          → show, alphabetical after all numbered items
      negative int  → hidden from nav (kept in JSON for reference)
5.  Inject the nav into every built HTML file.
6.  Generate the root-level index.html redirect.

nav_order.json format  (nested)
--------------------------------
The JSON mirrors the file hierarchy.  The root object represents the site
root.  Directory entries are dicts; file/leaf entries are int / null.

"." inside a dict sets that directory's own order in its parent.

Value rules (same everywhere):
  positive int → visible, ordered at that position
  null         → visible, alphabetical after all numbered items
  negative int → hidden from nav (tracked in JSON for reference)

Example:
  {
    "Submission-Guide": 1,
    "EMD_Repository": {
      ".": 2,
      "Model_Components": {
        ".": 1,
        "Similarity": 1,
        "gelato":     null
      },
      "old-section": -1
    }
  }
"""

import json
import os
import re
import shutil
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

SKIP = {
    '.DS_Store', '.gitignore', '.version',
    'scripts', '__pycache__', 'assets', 'stylesheets',
    'Visualizations', 'links.yml', 'json', 'nav_order.json',
    'css', 'js', 'fonts', 'icons', 'img', 'search',
    '404.html', 'sitemap.xml', 'sitemap.xml.gz',
    'index.md',
}


# ─────────────────────────────────────────────────────────────────────────────
# Name helpers
# ─────────────────────────────────────────────────────────────────────────────

def _strip(name: str) -> str:
    """Remove leading numeric prefix: '01_', '10_', '001_' → ''."""
    return re.sub(r'^\d+[-_.]', '', name)


def _stem(name: str) -> str:
    """Strip numeric prefix then file extension."""
    return re.sub(r'\.(html|md)$', '', _strip(name))


def _label(stem: str) -> str:
    """Human-readable label from a clean stem."""
    s = re.sub(r'[_-]', ' ', stem).strip()
    return (s[0].upper() + s[1:]) if s else s


def _visible(path: Path) -> bool:
    """True for paths that should appear in the nav."""
    return (
        not path.name.startswith('.')
        and path.name not in SKIP
        and path.name != 'index.html'
        and (path.is_dir() or path.suffix in ('.html', '.md'))
    )


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — prefix stripping with directory merge
# ─────────────────────────────────────────────────────────────────────────────

def _merge_dirs(src: Path, dst: Path):
    """Move all children of *src* into *dst*, then remove *src*."""
    for child in list(src.iterdir()):
        target = dst / child.name
        if target.exists():
            if child.is_dir() and target.is_dir():
                _merge_dirs(child, target)
            # file conflict: dst (MkDocs output) wins
        else:
            shutil.move(str(child), str(target))
    try:
        src.rmdir()
    except OSError:
        pass


def strip_prefixes(site_dir: Path) -> dict:
    """
    Walk site_dir bottom-up, strip numeric prefixes from every dir/file name.
    When the clean target already exists as a dir, merge into it.
    Returns {old_name: new_name} for link-fixing.
    """
    renames = {}
    for root, dirs, files in os.walk(str(site_dir), topdown=False):
        rp = Path(root)
        for name in dirs + files:
            clean = _strip(name)
            if clean == name:
                continue
            old = rp / name
            new = rp / clean
            renames[name] = clean
            if not old.exists():
                continue
            if new.exists():
                if old.is_dir() and new.is_dir():
                    _merge_dirs(old, new)
                # old file + new file → dst wins
            else:
                shutil.move(str(old), str(new))
    return renames


def fix_html_links(site_dir: Path, renames: dict):
    """Replace old prefixed names with clean names inside every HTML file."""
    if not renames:
        return
    for html in site_dir.rglob('*.html'):
        try:
            text = html.read_text(encoding='utf-8')
            orig = text
            for old, new in renames.items():
                text = text.replace(old, new)
            if text != orig:
                html.write_text(text, encoding='utf-8')
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Steps 2–3 — nav_order.json load / merge / save
# ─────────────────────────────────────────────────────────────────────────────

def load_nav_order(docs_dir: Path) -> dict:
    """
    Load nav_order.json.  Handles both the old flat format (with a "/" root
    key) and the new nested format.  Old format is migrated on load so the
    first save will upgrade the file.
    """
    p = docs_dir / 'nav_order.json'
    if not p.exists():
        return {}
    try:
        raw = json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {}

    # Detect old flat format: has a "/" key with a dict value
    if '/' not in raw:
        return raw   # already nested

    # ── Migrate flat → nested ─────────────────────────────────────────
    def _nest(stem, parent_val):
        section = raw.get(stem)
        if not isinstance(section, dict):
            return parent_val
        entry = {}
        dot = section.get('.')
        if dot is not None:
            entry['.'] = dot
        for child_stem, child_val in section.items():
            if child_stem == '.':
                continue
            entry[child_stem] = _nest(child_stem, child_val)
        return entry

    nested = {}
    for stem, val in raw.get('/', {}).items():
        nested[stem] = _nest(stem, val)
    return nested


def save_nav_order(docs_dir: Path, nav_order: dict):
    (docs_dir / 'nav_order.json').write_text(
        json.dumps(nav_order, indent=2),
        encoding='utf-8',
    )


# ── Entry helpers (nested format) ────────────────────────────────────────────

def _entry_order(entry) -> 'int | None':
    """Ordering value for sorting: from int/null directly, or from dict["."]."""
    if entry is None:
        return None
    if isinstance(entry, int):
        return entry
    if isinstance(entry, dict):
        return entry.get('.')   # may be None
    return None


def _is_hidden(entry) -> bool:
    """True when the entry should be hidden from the nav."""
    order = _entry_order(entry)
    return isinstance(order, int) and order < 0


def _entry_children(entry) -> dict:
    """Return the children dict when entry represents a directory."""
    return entry if isinstance(entry, dict) else {}


def _sort_key(stem: str, entry) -> tuple:
    """
    Sort key respecting the unified value rules:
      positive int → (0, value, stem)  shown, ordered first
      None         → (1, 0,     stem)  shown, alpha after numbered
      negative int → None              hidden (caller filters)
    """
    order = _entry_order(entry)
    if order is None:
        return (1, 0, stem.lower())
    if order >= 0:
        return (0, order, stem.lower())
    return None   # sentinel: hidden


def _scan_disk(path: Path) -> tuple[list[str], list[str]]:
    """
    Returns (visible_stems, hidden_stems) for children of *path*.
    visible_stems  — pass _visible()
    hidden_stems   — exist on disk, not dot-files, but fail _visible();
                     recorded as -1 so they are tracked.
    """
    visible, hidden = [], []
    for c in path.iterdir():
        if c.name.startswith('.'):
            continue
        s = _stem(c.name)
        if _visible(c):
            visible.append(s)
        else:
            hidden.append(s)
    return sorted(visible, key=str.lower), sorted(hidden, key=str.lower)


def merge_nav_order(site_dir: Path, docs_dir: Path, nav_order: dict) -> dict:
    """
    Walk the full site_dir hierarchy and ensure every item is represented in
    the nested nav_order dict.

    Nested format rules
    -------------------
    Directory  → dict entry.  "." key inside sets its order in parent.
                 Children are nested inside the same dict.
    File       → int / null / -1  (leaf value)
    New dir    → {}  (empty dict, order = null = unordered)
    New file   → null
    Non-nav    → -1  (hidden, tracked)
    """
    changed = False

    def _merge_level(section: dict, disk_path: Path):
        nonlocal changed
        visible_stems, hidden_stems = _scan_disk(disk_path)

        # ── visible items ─────────────────────────────────────────────
        for stem in visible_stems:
            child_path = _find_child(disk_path, stem)
            is_dir     = child_path is not None and child_path.is_dir()
            has_kids   = is_dir and any(_visible(c) for c in child_path.iterdir())

            current = section.get(stem, _MISSING := object())
            if current is _MISSING:
                section[stem] = {} if has_kids else None
                changed = True
                current = section[stem]
            elif has_kids and not isinstance(current, dict):
                # Upgrade leaf to dir entry, preserving any numeric value as "."
                section[stem] = {'.': current} if isinstance(current, int) else {}
                changed = True
                current = section[stem]

            if has_kids and not _is_hidden(current):
                _merge_level(current, child_path)

        # ── hidden / non-nav items ─────────────────────────────────────
        for stem in hidden_stems:
            if stem not in section:
                section[stem] = -1
                changed = True

    _merge_level(nav_order, site_dir)

    if changed:
        save_nav_order(docs_dir, nav_order)
        print('  [post_build] nav_order.json updated with new items')

    return nav_order


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — build nav from nested nav_order
# ─────────────────────────────────────────────────────────────────────────────

def _url(path: Path, site_dir: Path) -> str:
    parts = [_strip(p) for p in path.relative_to(site_dir).parts]
    if path.is_dir():
        return '/' + '/'.join(parts) + '/'
    stem = re.sub(r'\.html$', '', parts[-1])
    return '/' + '/'.join(parts[:-1] + [stem]) + '.html'


def _find_child(parent: Path, wanted_stem: str) -> Path | None:
    """Prefer directories over same-stem files (directory URL wins)."""
    match_file = None
    for child in parent.iterdir():
        if _stem(child.name) == wanted_stem:
            if child.is_dir():
                return child
            match_file = child
    return match_file


def _is_leaf_dir(path: Path) -> bool:
    return not any(_visible(c) for c in path.iterdir())


def _build_items(parent: Path, site_dir: Path, section: dict) -> list:
    """Build ordered nav items for directory *parent* using *section* dict."""
    items = []
    seen  = set()

    disk_stems = {_stem(c.name) for c in parent.iterdir() if _visible(c)}
    # entry map: stem → entry from section (None if not yet recorded)
    entries = {s: section.get(s) for s in disk_stems if s != '.'}

    def _sk(pair):
        k = _sort_key(pair[0], pair[1])
        return k if k is not None else (2, 0, pair[0].lower())

    for stem, entry in sorted(entries.items(), key=_sk):
        if _is_hidden(entry):
            continue
        if stem in seen:
            continue
        seen.add(stem)

        found = _find_child(parent, stem)
        if found is None:
            continue

        lbl = _label(stem)
        if found.is_dir():
            if _is_leaf_dir(found):
                items.append({'type': 'link', 'label': lbl, 'url': _url(found, site_dir)})
            else:
                kids = _build_items(found, site_dir, _entry_children(entry))
                items.append({'type': 'group', 'label': lbl,
                              'url': _url(found, site_dir), 'children': kids})
        else:
            items.append({'type': 'link', 'label': lbl, 'url': _url(found, site_dir)})

    return items


def build_nav(site_dir: Path, nav_order: dict) -> list:
    """Build the full sidebar nav list from the nested nav_order."""
    nav = [{'type': 'link', 'label': 'Home', 'url': '/'}]

    disk_stems = {_stem(c.name) for c in site_dir.iterdir() if _visible(c)}
    entries    = {s: nav_order.get(s) for s in disk_stems if s != '.'}

    def _sk(pair):
        k = _sort_key(pair[0], pair[1])
        return k if k is not None else (2, 0, pair[0].lower())

    for stem, entry in sorted(entries.items(), key=_sk):
        if _is_hidden(entry):
            continue

        found = _find_child(site_dir, stem)
        if found is None:
            continue

        lbl = _label(stem)
        if found.is_dir():
            if _is_leaf_dir(found):
                nav.append({'type': 'link', 'label': lbl, 'url': _url(found, site_dir)})
            else:
                kids = _build_items(found, site_dir, _entry_children(entry))
                nav.append({'type': 'group', 'label': lbl,
                            'url': _url(found, site_dir), 'children': kids})
        else:
            nav.append({'type': 'link', 'label': lbl, 'url': _url(found, site_dir)})

    return nav

# ─────────────────────────────────────────────────────────────────────────────
# Step 5 — inject nav into HTML
# ─────────────────────────────────────────────────────────────────────────────

# CSS is written to a shared file (emd-nav.css) and linked from every page.
# It is NOT inlined into each page.
_NAV_CSS_FILENAME = 'emd-nav.css'

_NAV_CSS = """
/* ── EMD nav — uses the shadcn/Geist CSS variables from base.css ─────────── */

/* ── Nav tree shared by sidebar slot, standalone drawer, and mobile drawer ── */
#custom-nav {
  font-family: var(--font-sans, ui-sans-serif, system-ui, sans-serif);
  font-size: var(--text-sm, 0.875rem);
  padding: 0.25rem 0;
}
#custom-nav a {
  display: flex;
  align-items: center;
  padding: 0.3rem 0.625rem;
  border-radius: var(--radius-md, 0.375rem);
  color: var(--sidebar-foreground, inherit);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: background 0.15s, color 0.15s;
  font-size: var(--text-sm, 0.875rem);
  line-height: 1.4;
}
#custom-nav a:hover {
  background: var(--sidebar-accent, rgba(0,0,0,0.06));
  color: var(--sidebar-accent-foreground, inherit);
}
#custom-nav a.active {
  background: var(--accent, rgba(0,0,0,0.09));
  color: var(--foreground, inherit);
  font-weight: var(--font-weight-medium, 500);
}

/* Group label row */
.nav-group-label {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.625rem;
  font-size: var(--text-sm, 0.875rem);
  font-weight: var(--font-weight-medium, 500);
  color: var(--muted-foreground, #888);
  cursor: pointer;
  border-radius: var(--radius-md, 0.375rem);
  user-select: none;
  transition: background 0.15s, color 0.15s;
  font-family: var(--font-sans, ui-sans-serif, system-ui, sans-serif);
}
.nav-group-label:hover {
  background: var(--sidebar-accent, rgba(0,0,0,0.06));
  color: var(--sidebar-accent-foreground, inherit);
}
.nav-group-label svg {
  flex-shrink: 0;
  width: 12px; height: 12px;
  transition: transform 0.2s var(--ease-in-out, ease);
}
.nav-group-label.collapsed svg { transform: rotate(-90deg); }

/* Indented child group */
.nav-group-children {
  padding-left: 0.5rem;
  margin-left: 1rem;
  margin-bottom: 0.125rem;
  border-left: 1px solid var(--sidebar-border, rgba(0,0,0,0.08));
}
.nav-group-children.collapsed { display: none; }

/* ── Standalone page: slide-in drawer ────────────────────────────────────── */
#emd-nav-drawer {
  position: fixed; top: 0; left: 0; bottom: 0;
  width: var(--sidebar-width, 240px);
  max-width: min(85vw, 280px);
  background: var(--sidebar, #fafafa);
  color: var(--sidebar-foreground, #111);
  border-right: 1px solid var(--sidebar-border, rgba(0,0,0,0.08));
  box-shadow: 2px 0 20px rgba(0,0,0,0.12);
  padding: 0.75rem 0.5rem 1.5rem;
  overflow-y: auto;
  z-index: 200;
  transform: translateX(-100%);
  transition: transform 0.22s var(--ease-out, ease);
  font-family: var(--font-sans, ui-sans-serif, system-ui, sans-serif);
  scrollbar-width: thin;
  scrollbar-color: var(--muted-foreground, #aaa) transparent;
}
#emd-nav-drawer.open { transform: translateX(0); }

/* Drawer header — mirrors the MkDocs site header height */
#emd-nav-drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.25rem 0.625rem 0.875rem;
  border-bottom: 1px solid var(--sidebar-border, rgba(0,0,0,0.08));
  margin-bottom: 0.5rem;
}
#emd-nav-drawer-title {
  font-size: var(--text-sm, 0.875rem);
  font-weight: var(--font-weight-semibold, 600);
  color: var(--sidebar-foreground, #111);
  font-family: var(--font-sans, ui-sans-serif, system-ui, sans-serif);
  letter-spacing: var(--tracking-tight, -0.015em);
}
#emd-nav-drawer-close {
  display: flex; align-items: center; justify-content: center;
  width: 1.75rem; height: 1.75rem;
  border: none; border-radius: var(--radius-md, 0.375rem);
  background: transparent; cursor: pointer;
  color: var(--muted-foreground, #888);
  transition: background 0.15s, color 0.15s;
}
#emd-nav-drawer-close:hover {
  background: var(--sidebar-accent, rgba(0,0,0,0.06));
  color: var(--sidebar-accent-foreground, #111);
}
#emd-nav-drawer-close svg { width: 14px; height: 14px; }

/* Scrim */
#emd-nav-scrim {
  display: none; position: fixed; inset: 0;
  background: rgba(0,0,0,0.3);
  z-index: 199; backdrop-filter: blur(1px);
}
#emd-nav-scrim.open { display: block; }

/* Edge tab — hamburger handle */
#emd-nav-tab {
  position: fixed; top: 50%; left: 0;
  transform: translateY(-50%);
  z-index: 198;
  display: flex; flex-direction: column; align-items: center;
  gap: 2px; padding: 10px 6px;
  background: var(--sidebar, #fafafa);
  border: 1px solid var(--sidebar-border, rgba(0,0,0,0.08));
  border-left: none;
  border-radius: 0 var(--radius-md, 0.375rem) var(--radius-md, 0.375rem) 0;
  box-shadow: 2px 0 8px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: background 0.15s, box-shadow 0.15s;
}
#emd-nav-tab:hover {
  background: var(--sidebar-accent, #f3f3f3);
  box-shadow: 2px 0 12px rgba(0,0,0,0.12);
}
#emd-nav-tab.hidden { display: none; }
#emd-nav-tab svg {
  width: 14px; height: 14px;
  color: var(--muted-foreground, #666);
  flex-shrink: 0;
}

/* ── Mobile drawer (MkDocs-themed pages) ─────────────────────────────────── */
#mobile-nav-overlay {
  position: fixed; inset: 0; z-index: 100;
  background: rgba(0,0,0,0.4); display: none;
}
#mobile-nav-overlay.open { display: block; }
#mobile-nav-drawer {
  position: fixed; top: 0; left: 0; bottom: 0;
  width: min(85vw, 300px);
  background: var(--sidebar, #fafafa);
  color: var(--sidebar-foreground, #111);
  z-index: 101; overflow-y: auto;
  padding: 0.75rem 0.5rem;
  transform: translateX(-100%);
  transition: transform 0.22s var(--ease-out, ease);
  box-shadow: 4px 0 24px rgba(0,0,0,0.15);
  font-family: var(--font-sans, ui-sans-serif, system-ui, sans-serif);
}
#mobile-nav-overlay.open #mobile-nav-drawer { transform: translateX(0); }
"""
_NAV_JS = r"""
(function(){
var NAV=%(nav_json)s;
var PFX=(typeof NAV_PREFIX!=='undefined')?NAV_PREFIX:'';
function rel(u){return PFX+(u||'').replace(/^\//,'');}
function cur(){return window.location.pathname.replace(/\/$/,'')||'/';}
function active(u){
  if(!u)return false;
  var a=document.createElement('a');a.href=rel(u);
  var p=a.pathname.replace(/\/$/,'');
  return cur()===p||cur().startsWith(p+'/');
}
var chv='<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>';
function grpActive(g){
  for(var i=0;i<(g.children||[]).length;i++){
    var c=g.children[i];
    if(c.type==='link'&&active(c.url))return true;
    if(c.type==='group'&&grpActive(c))return true;
  }
  return g.url&&active(g.url);
}
function render(items){
  var h='';
  for(var i=0;i<items.length;i++){
    var it=items[i];
    if(it.type==='link'){
      h+='<a href="'+rel(it.url)+'"'+(active(it.url)?' class="active"':'')+'>'+it.label+'</a>';
    } else {
      var on=grpActive(it);
      var col=on?'':' collapsed';
      var id='g'+Math.random().toString(36).slice(2);
      h+='<div><div class="nav-group-label'+col+'" onclick="toggleNav(this,\''+id+'\')">'+chv+it.label+'</div>';
      h+='<div id="'+id+'" class="nav-group-children'+col+'">';
      /* Overview link intentionally omitted — group URL is the section header */
      h+=render(it.children||[]);
      h+='</div></div>';
    }
  }
  return h;
}
window.toggleNav=function(el,id){
  el.classList.toggle('collapsed');
  document.getElementById(id).classList.toggle('collapsed');
};
function navHtml(){return'<div id="custom-nav">'+render(NAV)+'</div>';}

function initStandalone(){
  /* Standalone .html page — nav hidden by default, tab reveals drawer */
  if(document.getElementById('emd-nav-drawer'))return;

  /* Scrim */
  var scrim=document.createElement('div');
  scrim.id='emd-nav-scrim';
  document.body.appendChild(scrim);

  /* Drawer */
  var drawer=document.createElement('div');
  drawer.id='emd-nav-drawer';
  var hdr=document.createElement('div');
  hdr.id='emd-nav-drawer-header';
  var ttl=document.createElement('span');
  ttl.id='emd-nav-drawer-title';
  ttl.textContent='Navigation';
  var cls=document.createElement('button');
  cls.id='emd-nav-drawer-close';
  cls.setAttribute('aria-label','Close navigation');
  cls.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
  hdr.appendChild(ttl);hdr.appendChild(cls);
  drawer.appendChild(hdr);
  var navWrap=document.createElement('div');
  navWrap.innerHTML=navHtml();
  drawer.appendChild(navWrap);
  document.body.appendChild(drawer);

  /* Tab */
  var tab=document.createElement('div');
  tab.id='emd-nav-tab';
  tab.setAttribute('aria-label','Open navigation');
  tab.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';
  document.body.appendChild(tab);

  function openDrawer(){
    drawer.classList.add('open');
    scrim.classList.add('open');
    tab.classList.add('hidden');
  }
  function closeDrawer(){
    drawer.classList.remove('open');
    scrim.classList.remove('open');
    tab.classList.remove('hidden');
  }
  tab.addEventListener('click', openDrawer);
  cls.addEventListener('click', closeDrawer);
  scrim.addEventListener('click', closeDrawer);
  document.addEventListener('keydown',function(e){if(e.key==='Escape')closeDrawer();});
}

function initMkDocs(){
  /* MkDocs-themed page — inject into sidebar slot */
  var s=document.querySelector('[data-slot="sidebar-content"]');
  if(!s)return false;
  var old=s.querySelector('#custom-nav');if(old)old.remove();
  var sp=s.querySelector('.h-\\(--top-spacing\\)');
  var d=document.createElement('div');d.innerHTML=navHtml();
  if(sp&&sp.nextSibling)s.insertBefore(d.firstChild,sp.nextSibling);else s.appendChild(d.firstChild);

  /* Mobile drawer */
  if(!document.getElementById('mobile-nav-overlay')){
    var o=document.createElement('div');
    o.id='mobile-nav-overlay';
    o.innerHTML='<div id="mobile-nav-drawer">'+navHtml()+'</div>';
    o.addEventListener('click',function(e){if(e.target===o)o.classList.remove('open');});
    document.body.appendChild(o);
    var b=document.getElementById('menu-button');
    if(b)b.addEventListener('click',function(e){e.stopPropagation();o.classList.toggle('open');});
  }
  return true;
}

function init(){
  if(!initMkDocs()) initStandalone();
}
if(document.readyState==='loading')
  document.addEventListener('DOMContentLoaded',init);
else init();
})();
"""

# Unique marker — written once per page, never present in theme or generator output.
_NAV_MARKER = '<!-- emd-nav-v1 -->'


def inject_nav(site_dir: Path, nav: list):
    """
    For every HTML file in site_dir:
      1. Write emd-nav.css to site/stylesheets/ (once).
      2. Inject a <link> to that CSS + the nav <script> into the page.

    CSS is shared across all pages via a single file; only nav data + JS
    is inlined per-page (because it contains per-page relative URL prefix).
    """
    nav_json  = json.dumps(nav)
    css_path  = site_dir / 'stylesheets' / _NAV_CSS_FILENAME
    css_path.parent.mkdir(parents=True, exist_ok=True)
    css_path.write_text(_NAV_CSS, encoding='utf-8')

    injected = 0
    for html in site_dir.rglob('*.html'):
        content = html.read_text(encoding='utf-8')
        if _NAV_MARKER in content:
            continue
        depth  = len(html.relative_to(site_dir).parts) - 1
        prefix = '../' * depth if depth else './'
        css_rel = f'{prefix}stylesheets/{_NAV_CSS_FILENAME}'

        # On standalone pages (no base.css/geist.css), inject the theme
        # CSS so all CSS variables resolve correctly.
        theme_links = ''
        if 'css/base.css' not in content:
            base_rel  = f'{prefix}css/base.css'
            geist_rel = f'{prefix}css/geist.css'
            theme_links = (f'<link rel="stylesheet" href="{base_rel}">'
                           f'<link rel="stylesheet" href="{geist_rel}">')

        js  = f'var NAV_PREFIX={json.dumps(prefix)};\n' + (
              _NAV_JS % {'nav_json': nav_json})
        tag = (f'{_NAV_MARKER}'
               f'{theme_links}'
               f'<link rel="stylesheet" href="{css_rel}">'
               f'<script>{js}</script>')
        new = content.replace('</body>', f'  {tag}\n</body>')
        if new == content:
            new = content.replace('</html>', f'  {tag}\n</html>')
        html.write_text(new, encoding='utf-8')
        injected += 1
    print(f'  [post_build] Nav injected into {injected} HTML files + emd-nav.css written')


def _extract_search_block(site_dir: Path) -> str:
    """
    Pull the search button + dialog HTML from a built MkDocs index page.
    Returns an empty string if not found.
    """
    for candidate in [site_dir / 'index.html',
                      site_dir / 'Submission-Guide' / 'index.html']:
        if not candidate.exists():
            continue
        text = candidate.read_text(encoding='utf-8')
        if 'search-dialog' not in text:
            continue
        # Locate button that opens the dialog
        btn_start = text.rfind('<button', 0, text.find('search-dialog'))
        if btn_start < 0:
            continue
        # Locate end of the inline shortcut re-registration script
        dialog_pos   = text.find('</dialog>')
        script_end   = text.find('</script>', dialog_pos)
        if script_end < 0:
            continue
        return text[btn_start: script_end + len('</script>')]
    return ''


def inject_search(site_dir: Path):
    """
    For every standalone .html page (i.e. pages that don't already have the
    MkDocs theme search dialog), inject:
      - the search button + dialog HTML extracted from index.html
      - <script src="…/js/callbacks.js"> (defines onSearchBarClick etc.)
      - <script src="…/search/main.js"> (starts the Lunr web worker)

    MkDocs-built index pages already have all this — we only patch standalone
    pages such as Similarity.html.
    """
    search_block = _extract_search_block(site_dir)
    if not search_block:
        print('  [post_build] search block not found — skipping search injection')
        return

    patched = 0
    for html in site_dir.rglob('*.html'):
        content = html.read_text(encoding='utf-8')
        # Skip pages that already have the search dialog
        if 'search-dialog' in content:
            continue
        # Skip pages where the nav marker hasn't been written yet
        # (shouldn't happen, but be safe)
        if _NAV_MARKER not in content:
            continue

        depth  = len(html.relative_to(site_dir).parts) - 1
        prefix = '../' * depth if depth else './'

        scripts = (
            f'<script src="{prefix}js/callbacks.js"></script>'
            f'<script src="{prefix}search/main.js"></script>'
        )
        # Insert right before </body> — after nav, before close
        injection = f'{search_block}\n{scripts}'
        new = content.replace('</body>', f'  {injection}\n</body>')
        if new != content:
            html.write_text(new, encoding='utf-8')
            patched += 1

    print(f'  [post_build] Search injected into {patched} standalone HTML files')


# ─────────────────────────────────────────────────────────────────────────────
# Step 6 — root redirect
# ─────────────────────────────────────────────────────────────────────────────

def root_redirect(site_dir: Path):
    html = (
        '<!DOCTYPE html><html><head><meta charset="UTF-8"><script>\n'
        'window.addEventListener("load",function(){\n'
        '  window.location.href=window.location.origin'
        '+window.location.pathname.replace(/\\/$/,"")+"/docs/";\n'
        '});\n</script></head><body><p>Redirecting\u2026</p></body></html>'
    )
    try:
        (site_dir.parent / 'index.html').write_text(html, encoding='utf-8')
    except Exception as e:
        print(f'  [post_build] root redirect failed: {e}')


# ─────────────────────────────────────────────────────────────────────────────
# MkDocs hooks
# ─────────────────────────────────────────────────────────────────────────────

def on_page_context(context, page, config, nav, **kwargs):
    """Strip numeric prefixes from every .md page's dest_uri."""
    import posixpath
    site_dir = Path(config['site_dir'])
    src      = page.file.src_path

    clean_src = '/'.join(_strip(p) for p in src.replace('\\', '/').split('/'))
    use_dir   = config.get('use_directory_urls', True)
    parent, fname = posixpath.split(clean_src)
    stem          = posixpath.splitext(fname)[0]

    if stem.lower() == 'index' or not use_dir:
        correct = posixpath.join(parent, 'index.html') \
                  if stem.lower() == 'index' else posixpath.join(parent, stem + '.html')
    else:
        correct = posixpath.join(parent, stem, 'index.html')

    if page.file.dest_uri != correct:
        page.file.dest_uri = correct

    (site_dir / src).parent.mkdir(parents=True, exist_ok=True)
    return context


def on_post_build(config, **kwargs):
    site_dir = Path(config['site_dir']).resolve()
    docs_dir = Path(config['docs_dir']).resolve()

    # 1. Strip prefixes + merge conflicting dirs
    renames = strip_prefixes(site_dir)
    fix_html_links(site_dir, renames)
    print(f'  [post_build] Prefix-stripped {len(renames)} items')

    # 2. Root redirect
    root_redirect(site_dir)

    # 3. Load → full-hierarchy merge → save nav_order.json
    nav_order = load_nav_order(docs_dir)
    nav_order = merge_nav_order(site_dir, docs_dir, nav_order)

    # 4. Build nav (positive ordered first, null alpha after, negative hidden)
    nav = build_nav(site_dir, nav_order)

    # 5. Inject nav into HTML
    inject_nav(site_dir, nav)

    # 6. Inject search into standalone pages
    inject_search(site_dir)
