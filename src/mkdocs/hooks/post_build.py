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

nav_order.json format
---------------------
Each key is a section stem (the directory name, no prefix).
"/" is the root level.
Each value is a dict mapping child stem → order value.

Special key "."
  A section dict may contain the key "." whose value sets the order of
  *that directory itself* in its parent section.  This lets you control a
  directory's position from within its own entry without editing the parent.
  The "." value obeys the same rules: positive = ordered, null = unordered
  alpha, negative = hidden.

Example:
  {
    "/": {
      "Submission-Guide": 1,
      "EMD_Repository":   2,
      "old-draft":       -1    ← hidden
    },
    "EMD_Repository": {
      ".": 2,                   ← sets this dir's own position in "/"
      "Model_Components": 1,
      "new-section":      null  ← unordered (appears after numbered)
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
    """Load nav_order.json; return {} on missing/corrupt."""
    p = docs_dir / 'nav_order.json'
    if p.exists():
        try:
            return json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {}


def save_nav_order(docs_dir: Path, nav_order: dict):
    (docs_dir / 'nav_order.json').write_text(
        json.dumps(nav_order, indent=2),
        encoding='utf-8',
    )


def _scan_disk(path: Path) -> tuple[list[str], list[str]]:
    """
    Returns (visible_stems, hidden_stems) for children of *path*.
    visible_stems  — pass _visible(), should appear in nav (value null / positive)
    hidden_stems   — fail _visible() but exist on disk and aren't dot-files;
                     recorded in nav_order.json as -1 so they're tracked.
    """
    visible, hidden = [], []
    for c in path.iterdir():
        if c.name.startswith('.'):
            continue                      # ignore dot-files entirely
        s = _stem(c.name)
        if _visible(c):
            visible.append(s)
        else:
            hidden.append(s)
    return sorted(visible, key=str.lower), sorted(hidden, key=str.lower)


def merge_nav_order(site_dir: Path, docs_dir: Path, nav_order: dict) -> dict:
    """
    Walk the full site_dir hierarchy and ensure every visible item is
    represented in nav_order.json as {stem: null} (if new) or with its
    existing value (if already set).

    - New items → value null
    - Existing values → preserved exactly
    - nav_order is updated in-place and saved to docs/nav_order.json.
    """
    changed = False

    def _self_value(stem: str):
        """Return the '.' self-key value from a stem's own section, or None."""
        s = nav_order.get(stem)
        return s.get('.') if isinstance(s, dict) else None

    def _merge_level(section_dict: dict, disk_path: Path, section_key: str):
        nonlocal changed
        visible_stems, hidden_stems = _scan_disk(disk_path)

        # ── visible items ─────────────────────────────────────────────
        for stem in visible_stems:
            sv = _self_value(stem)
            if stem not in section_dict:
                section_dict[stem] = sv   # self-key value, or null
                changed = True
            elif sv is not None and section_dict[stem] != sv:
                section_dict[stem] = sv   # '.' overrides parent value
                changed = True

            # Recurse into dirs with visible children
            child = _find_child(disk_path, stem)
            if child is not None and child.is_dir():
                has_children = any(_visible(c) for c in child.iterdir())
                if has_children:
                    if stem not in nav_order:
                        nav_order[stem] = {}
                        changed = True
                    _merge_level(nav_order[stem], child, stem)

        # ── hidden items (-1) ─────────────────────────────────────────
        for stem in hidden_stems:
            if stem not in section_dict:
                section_dict[stem] = -1   # exists on disk but not in nav
                changed = True
            # Never overwrite a value already set by the user

    root_section = nav_order.setdefault('/', {})
    _merge_level(root_section, site_dir, '/')

    if changed:
        save_nav_order(docs_dir, nav_order)
        print('  [post_build] nav_order.json updated with new items')

    return nav_order


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — build nav from nav_order.json
# ─────────────────────────────────────────────────────────────────────────────

def _sort_key(stem: str, value) -> tuple:
    """
    Sort key for nav items:
      positive int  → (0, value, stem)  — ordered first, ascending
      null/None     → (1, 0,     stem)  — unordered, alpha after numbered
      negative int  → None              — hidden (caller must filter)
    """
    if value is None:
        return (1, 0, stem.lower())
    if value >= 0:
        return (0, value, stem.lower())
    return None   # sentinel: hidden


def _url(path: Path, site_dir: Path) -> str:
    parts = [_strip(p) for p in path.relative_to(site_dir).parts]
    if path.is_dir():
        return '/' + '/'.join(parts) + '/'
    stem = re.sub(r'\.html$', '', parts[-1])
    return '/' + '/'.join(parts[:-1] + [stem]) + '.html'


def _find_child(parent: Path, wanted_stem: str) -> Path | None:
    """
    Find the child of *parent* whose stripped stem equals *wanted_stem*.
    Prefers directories over same-stem files (directory URL wins).
    """
    match_file = None
    for child in parent.iterdir():
        if _stem(child.name) == wanted_stem:
            if child.is_dir():
                return child
            match_file = child
    return match_file


def _is_leaf_dir(path: Path) -> bool:
    """Dir containing nothing visible beyond index.html → plain link."""
    return not any(_visible(c) for c in path.iterdir())


def _build_items(parent: Path, site_dir: Path, section_key: str,
                 nav_order: dict) -> list:
    """
    Build ordered nav items for a directory.

    Uses nav_order[section_key] for ordering/hiding.
    Items not in the section dict appear last (alphabetical, value=null).
    """
    section = nav_order.get(section_key, {})
    items   = []
    seen    = set()

    # Collect all visible stems from disk (".") is a JSON-only key, not a file)
    disk_stems = {_stem(c.name) for c in parent.iterdir() if _visible(c)}

    # Merge disk stems; skip the self-key "." — it is not a child item
    all_items = {s: section.get(s) for s in disk_stems if s != '.'}

    # Sort: positive-numbered → null/unordered → skip negative
    def _sk(pair):
        k = _sort_key(pair[0], pair[1])
        return k if k is not None else (2, 0, pair[0].lower())   # temp bucket

    ordered = sorted(all_items.items(), key=_sk)

    for stem, value in ordered:
        # Skip hidden items
        if value is not None and value < 0:
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
                items.append({'type': 'link', 'label': lbl,
                              'url': _url(found, site_dir)})
            else:
                kids = _build_items(found, site_dir, stem, nav_order)
                items.append({'type': 'group', 'label': lbl,
                              'url': _url(found, site_dir), 'children': kids})
        else:
            items.append({'type': 'link', 'label': lbl,
                          'url': _url(found, site_dir)})

    return items


def build_nav(site_dir: Path, nav_order: dict) -> list:
    """Build the full sidebar nav list from nav_order + disk state."""
    nav         = [{'type': 'link', 'label': 'Home', 'url': '/'}]
    root_section = nav_order.get('/', {})

    disk_stems = {_stem(c.name) for c in site_dir.iterdir() if _visible(c)}
    all_root   = {s: root_section.get(s) for s in disk_stems if s != '.'}  # "." is not a file

    def _sk(pair):
        k = _sort_key(pair[0], pair[1])
        return k if k is not None else (2, 0, pair[0].lower())

    for stem, value in sorted(all_root.items(), key=_sk):
        if value is not None and value < 0:
            continue

        found = _find_child(site_dir, stem)
        if found is None:
            continue

        lbl = _label(stem)
        if found.is_dir():
            if _is_leaf_dir(found):
                nav.append({'type': 'link', 'label': lbl,
                            'url': _url(found, site_dir)})
            else:
                kids = _build_items(found, site_dir, stem, nav_order)
                nav.append({'type': 'group', 'label': lbl,
                            'url': _url(found, site_dir), 'children': kids})
        else:
            nav.append({'type': 'link', 'label': lbl,
                        'url': _url(found, site_dir)})

    return nav


# ─────────────────────────────────────────────────────────────────────────────
# Step 5 — inject nav into HTML
# ─────────────────────────────────────────────────────────────────────────────

_NAV_CSS = """
#custom-nav { font-size: 0.85rem; padding: 0.5rem 0; }
#custom-nav a {
  display: block; padding: 0.25rem 0.75rem; border-radius: 0.375rem;
  color: inherit; text-decoration: none; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis; transition: background 0.15s;
}
#custom-nav a:hover { background: var(--accent, rgba(0,0,0,0.07)); }
#custom-nav a.active {
  background: var(--accent, rgba(0,0,0,0.10));
  font-weight: 600; color: var(--accent-foreground, inherit);
}
.nav-group-label {
  display: flex; align-items: center; gap: 0.35rem;
  padding: 0.25rem 0.75rem; font-weight: 600; font-size: 0.85rem;
  color: var(--muted-foreground, #888); cursor: pointer;
  border-radius: 0.375rem; user-select: none; transition: background 0.15s;
}
.nav-group-label:hover { background: var(--accent, rgba(0,0,0,0.05)); }
.nav-group-label svg { flex-shrink: 0; transition: transform 0.2s; }
.nav-group-label.collapsed svg { transform: rotate(-90deg); }
.nav-group-children {
  padding-left: 0.75rem;
  border-left: 1px solid var(--border, rgba(0,0,0,0.1));
  margin-left: 0.9rem; margin-bottom: 0.25rem;
}
.nav-group-children.collapsed { display: none; }
#mobile-nav-overlay {
  position: fixed; inset: 0; z-index: 100;
  background: rgba(0,0,0,0.5); display: none;
}
#mobile-nav-overlay.open { display: block; }
#mobile-nav-drawer {
  position: fixed; top: 0; left: 0; bottom: 0;
  width: min(85vw, 300px); background: var(--background, #fff);
  z-index: 101; overflow-y: auto; padding: 1rem 0.5rem;
  transform: translateX(-100%); transition: transform 0.25s ease;
  box-shadow: 4px 0 24px rgba(0,0,0,0.15);
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
      if(it.url)h+='<a href="'+rel(it.url)+'"'+(active(it.url)?' class="active"':'')+'>Overview</a>';
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
function desk(){
  var s=document.querySelector('[data-slot="sidebar-content"]');
  if(s){
    var old=s.querySelector('#custom-nav');if(old)old.remove();
    var sp=s.querySelector('.h-\\(--top-spacing\\)');
    var d=document.createElement('div');d.innerHTML=navHtml();
    if(sp&&sp.nextSibling)s.insertBefore(d.firstChild,sp.nextSibling);else s.appendChild(d.firstChild);
  } else {
    /* Standalone page (e.g. Similarity.html) — inject a fixed sidebar */
    if(document.getElementById('custom-nav'))return;
    var sidebar=document.createElement('div');
    sidebar.style.cssText='position:fixed;top:0;left:0;bottom:0;width:220px;overflow-y:auto;'
      +'background:var(--background,#fff);border-right:1px solid var(--border,rgba(0,0,0,.1));'
      +'padding:1rem 0;z-index:50;font-size:0.82rem;box-shadow:2px 0 8px rgba(0,0,0,.06);';
    sidebar.innerHTML=navHtml();
    document.body.style.marginLeft='220px';
    document.body.appendChild(sidebar);
  }
}
function mob(){
  if(document.getElementById('mobile-nav-overlay'))return;
  var o=document.createElement('div');
  o.id='mobile-nav-overlay';
  o.innerHTML='<div id="mobile-nav-drawer">'+navHtml()+'</div>';
  o.addEventListener('click',function(e){if(e.target===o)o.classList.remove('open');});
  document.body.appendChild(o);
  var b=document.getElementById('menu-button');
  if(b)b.addEventListener('click',function(e){e.stopPropagation();o.classList.toggle('open');});
}
var st=document.createElement('style');st.textContent=%(css_json)s;
document.head.appendChild(st);
if(document.readyState==='loading')
  document.addEventListener('DOMContentLoaded',function(){desk();mob();});
else{desk();mob();}
})();
"""


# Unique marker written into every page after nav injection.
# Must NOT appear in any MkDocs theme file or generated content.
_NAV_MARKER = '<!-- emd-nav-v1 -->'


def inject_nav(site_dir: Path, nav: list):
    nav_json = json.dumps(nav)
    css_json = json.dumps(_NAV_CSS)
    injected = 0
    for html in site_dir.rglob('*.html'):
        content = html.read_text(encoding='utf-8')
        if _NAV_MARKER in content:          # already injected this build
            continue
        depth  = len(html.relative_to(site_dir).parts) - 1
        prefix = '../' * depth if depth else './'
        js = (f'var NAV_PREFIX={json.dumps(prefix)};\n'
              + _NAV_JS % {'nav_json': nav_json, 'css_json': css_json})
        # Marker + script injected just before </body>
        tag = f'{_NAV_MARKER}<script>{js}</script>'
        new = content.replace('</body>', f'  {tag}\n</body>')
        if new == content:
            new = content.replace('</html>', f'  {tag}\n</html>')
        html.write_text(new, encoding='utf-8')
        injected += 1
    print(f'  [post_build] Nav injected into {injected} HTML files')


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

    # 5. Inject into HTML
    inject_nav(site_dir, nav)
