#!/usr/bin/env python3
"""
Post-build hook: clean numeric prefixes from built site.
Also pre-creates directories for shadcn's markdown copy (which uses src_path).
Also generates root-level index.html redirect.
Also injects custom navigation sidebar into all built HTML files.
"""

import os
import re
import json
import shutil
from pathlib import Path


def generate_root_redirect(site_dir):
    """Generate index.html at root level that redirects to /docs/"""
    root_index = Path(site_dir).parent / 'index.html'
    
    redirect_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redirecting...</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            color: #1e293b;
        }

        body.dark {
            background: #0f172a;
            color: #f1f5f9;
        }

        .redirect-container {
            text-align: center;
            max-width: 400px;
            padding: 24px;
        }

        .spinner {
            width: 80px;
            height: 80px;
            margin: 0 auto 24px;
            animation: spin 2s linear infinite;
        }

        @keyframes spin {
            from {
                transform: rotate(0deg);
            }
            to {
                transform: rotate(360deg);
            }
        }

        .spinner svg {
            width: 100%;
            height: 100%;
        }

        .text {
            font-size: 16px;
            opacity: 0.7;
            margin-bottom: 12px;
        }

        .redirect-link {
            display: inline-block;
            margin-top: 24px;
            padding: 12px 24px;
            background: #f1f5f9;
            color: #1e293b;
            text-decoration: none;
            border-radius: 6px;
            font-size: 14px;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        body.dark .redirect-link {
            background: #1e293b;
            color: #f1f5f9;
        }

        .redirect-link:hover {
            opacity: 0.8;
            transform: translateY(-2px);
        }

        .redirect-link:active {
            transform: translateY(0);
        }

        .explanation {
            font-size: 13px;
            opacity: 0.5;
            margin-top: 16px;
            line-height: 1.5;
        }
    </style>
    <script>
        // Detect system preference for dark mode
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark');
        }

        // Simple dynamic redirect to docs page
        window.addEventListener('load', () => {
            const docsUrl = window.location.origin + window.location.pathname.replace(/\/$/, '') + '/docs/';
            window.location.href = docsUrl;
        });

        // Allow manual redirect via link
        function redirectToDocs() {
            const docsUrl = window.location.origin + window.location.pathname.replace(/\/$/, '') + '/docs/';
            window.location.href = docsUrl;
        }
    </script>
</head>
<body>
    <div class="redirect-container">
        <div class="spinner">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
                <circle cx="50" cy="50" r="45" stroke="currentColor" stroke-width="2" opacity="0.3"/>
                <circle cx="50" cy="50" r="35" stroke="currentColor" stroke-width="2" opacity="0.5"/>
                <circle cx="50" cy="50" r="25" stroke="currentColor" stroke-width="3" opacity="0.8"/>
                <circle cx="50" cy="12" r="4" fill="currentColor"/>
            </svg>
        </div>
        <p class="text">Redirecting to documentation...</p>
        <a class="redirect-link" href="javascript:void(0)" onclick="redirectToDocs()">
            Go to Documentation
        </a>
        <p class="explanation">
            You are being redirected to the Essential Model Documentation. If the redirect doesn't work, click the button above.
        </p>
    </div>
</body>
</html>'''
    
    try:
        root_index.write_text(redirect_html, encoding='utf-8')
        print(f"Generated root-level redirect: {root_index}")
    except Exception as e:
        print(f"Error generating root redirect: {e}")


def on_page_context(context, page, config, nav, **kwargs):
    """Pre-create the directory that shadcn will try to copy the markdown file to.
    
    shadcn's MarkdownMixin copies source .md files to site_dir/page.file.src_path,
    which still has the numeric prefix (e.g. build/10_EMD_Repository/02_.../index.md).
    on_files() only cleans dest_uri, so that prefixed directory never gets created.
    We create it here before shadcn's on_page_context runs.
    """
    site_dir = Path(config['site_dir'])
    src_path = page.file.src_path
    dest = site_dir / src_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    return context


def strip_numeric_prefix(name):
    """Strip numeric prefix from a name."""
    return re.sub(r'^\d+[-_.]', '', name)


def collect_renames(site_dir):
    """Collect all items that need renaming."""
    renames = {}
    rename_operations = []
    
    for root, dirs, files in os.walk(site_dir, topdown=False):
        root_path = Path(root)
        
        for d in dirs:
            old_name = d
            clean_name = strip_numeric_prefix(d)
            if clean_name != old_name:
                old_full = root_path / old_name
                new_full = root_path / clean_name
                if old_full.exists() and not new_full.exists():
                    renames[old_name] = clean_name
                    rename_operations.append((str(old_full), str(new_full)))
        
        for f in files:
            old_name = f
            clean_name = strip_numeric_prefix(f)
            if clean_name != old_name:
                old_full = root_path / old_name
                new_full = root_path / clean_name
                if old_full.exists() and not new_full.exists():
                    renames[old_name] = clean_name
                    rename_operations.append((str(old_full), str(new_full)))
    
    return renames, rename_operations


def fix_html_links(site_dir, name_replacements):
    """Fix all links in HTML files."""
    if not name_replacements:
        return 0
    
    fixed_count = 0
    
    for root, dirs, files in os.walk(site_dir):
        for f in files:
            if not f.endswith('.html'):
                continue
            
            filepath = Path(root) / f
            try:
                content = filepath.read_text(encoding='utf-8')
                original = content
                
                for old_name, clean_name in name_replacements.items():
                    content = content.replace(old_name, clean_name)
                
                if content != original:
                    filepath.write_text(content, encoding='utf-8')
                    fixed_count += 1
            except Exception:
                pass
    
    return fixed_count


def rename_all_items(rename_operations):
    """Execute all rename operations."""
    if not rename_operations:
        return 0
    
    sorted_ops = sorted(rename_operations, key=lambda x: -x[0].count(os.sep))
    
    renamed_count = 0
    for old_path_str, new_path_str in sorted_ops:
        old_path = Path(old_path_str)
        new_path = Path(new_path_str)
        
        if old_path.exists() and not new_path.exists():
            try:
                shutil.move(str(old_path), str(new_path))
                renamed_count += 1
            except Exception:
                pass
    
    return renamed_count


def update_summary_file(site_dir, name_replacements):
    """Update SUMMARY.md with cleaned names."""
    summary_path = site_dir / 'SUMMARY.md'
    if not summary_path.exists():
        return False
    
    try:
        content = summary_path.read_text(encoding='utf-8')
        original = content
        
        for old_name, clean_name in name_replacements.items():
            content = content.replace(old_name, clean_name)
        
        if content != original:
            summary_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception:
        return False


##############################################################################
# Custom nav injection
##############################################################################

NAV_CSS = """
#custom-nav {
  font-size: 0.85rem;
  padding: 0.5rem 0;
}
#custom-nav a {
  display: block;
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  color: inherit;
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: background 0.15s;
}
#custom-nav a:hover { background: var(--accent, rgba(0,0,0,0.07)); }
#custom-nav a.active {
  background: var(--accent, rgba(0,0,0,0.10));
  font-weight: 600;
  color: var(--accent-foreground, inherit);
}
.nav-group-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.75rem;
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--muted-foreground, #888);
  cursor: pointer;
  border-radius: 0.375rem;
  user-select: none;
  transition: background 0.15s;
}
.nav-group-label:hover { background: var(--accent, rgba(0,0,0,0.05)); }
.nav-group-label svg { flex-shrink: 0; transition: transform 0.2s; }
.nav-group-label.collapsed svg { transform: rotate(-90deg); }
.nav-group-children {
  padding-left: 0.75rem;
  border-left: 1px solid var(--border, rgba(0,0,0,0.1));
  margin-left: 0.9rem;
  margin-bottom: 0.25rem;
}
.nav-group-children.collapsed { display: none; }
#mobile-nav-overlay {
  position: fixed; inset: 0; z-index: 100;
  background: rgba(0,0,0,0.5); display: none;
}
#mobile-nav-overlay.open { display: block; }
#mobile-nav-drawer {
  position: fixed; top: 0; left: 0; bottom: 0;
  width: min(85vw, 300px);
  background: var(--background, #fff);
  z-index: 101; overflow-y: auto;
  padding: 1rem 0.5rem;
  transform: translateX(-100%);
  transition: transform 0.25s ease;
  box-shadow: 4px 0 24px rgba(0,0,0,0.15);
}
#mobile-nav-overlay.open #mobile-nav-drawer { transform: translateX(0); }
"""

NAV_JS_TEMPLATE = r"""
(function() {
  var BASE_URL = "%(base_url)s";
  var NAV = %(nav_json)s;
  var chevron = '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>';

  function currentPath() {
    return window.location.pathname.replace(/\/$/, '') || '/';
  }
  function isActive(url) {
    var cp = currentPath();
    var u = (url || '').replace(/\/$/, '');
    if (!u) return cp === '' || cp === '/';
    return cp === u || cp.startsWith(u + '/');
  }
  function groupHasActive(group) {
    for (var i = 0; i < (group.children || []).length; i++) {
      var item = group.children[i];
      if (item.type === 'link' && isActive(item.url)) return true;
      if (item.type === 'group' && groupHasActive(item)) return true;
    }
    return group.url && isActive(group.url);
  }
  function renderItems(items) {
    var html = '';
    for (var i = 0; i < items.length; i++) {
      var item = items[i];
      if (item.type === 'link') {
        html += '<a href="' + item.url + '"' + (isActive(item.url) ? ' class="active"' : '') + '>' + item.label + '</a>';
      } else {
        var hasActive = groupHasActive(item);
        var collapsed = hasActive ? '' : ' collapsed';
        var id = 'grp' + Math.random().toString(36).slice(2);
        html += '<div>';
        html += '<div class="nav-group-label' + collapsed + '" onclick="toggleNavGroup(this,\'' + id + '\')">' + chevron + item.label + '</div>';
        html += '<div id="' + id + '" class="nav-group-children' + collapsed + '">';
        if (item.url) html += '<a href="' + item.url + '"' + (isActive(item.url) ? ' class="active"' : '') + '>Overview</a>';
        html += renderItems(item.children || []);
        html += '</div></div>';
      }
    }
    return html;
  }
  window.toggleNavGroup = function(el, id) {
    el.classList.toggle('collapsed');
    document.getElementById(id).classList.toggle('collapsed');
  };
  function buildNav() { return '<div id="custom-nav">' + renderItems(NAV) + '</div>'; }
  function injectDesktop() {
    var slot = document.querySelector('[data-slot="sidebar-content"]');
    if (!slot) return;
    var old = slot.querySelector('#custom-nav');
    if (old) old.remove();
    var spacer = slot.querySelector('.h-\\(--top-spacing\\)');
    var div = document.createElement('div');
    div.innerHTML = buildNav();
    if (spacer && spacer.nextSibling) slot.insertBefore(div.firstChild, spacer.nextSibling);
    else slot.appendChild(div.firstChild);
  }
  function injectMobile() {
    if (document.getElementById('mobile-nav-overlay')) return;
    var overlay = document.createElement('div');
    overlay.id = 'mobile-nav-overlay';
    overlay.innerHTML = '<div id="mobile-nav-drawer">' + buildNav() + '</div>';
    overlay.addEventListener('click', function(e) { if (e.target === overlay) overlay.classList.remove('open'); });
    document.body.appendChild(overlay);
    var btn = document.getElementById('menu-button');
    if (btn) btn.addEventListener('click', function(e) { e.stopPropagation(); overlay.classList.toggle('open'); });
  }
  var style = document.createElement('style');
  style.textContent = %(css_json)s;
  document.head.appendChild(style);
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { injectDesktop(); injectMobile(); });
  } else { injectDesktop(); injectMobile(); }
})();
"""

SKIP_NAMES = {'.DS_Store', '.gitignore', '.version', 'scripts', '__pycache__',
              'assets', 'stylesheets', 'Visualizations', 'links.yml', 'json'}


def strip_prefix(name):
    return re.sub(r'^\d+_', '', name)


def nice_label(name):
    name = re.sub(r'\.(md|html)$', '', name)
    name = re.sub(r'[_-]', ' ', name).strip()
    # Title-case only the first letter, preserve the rest
    return name[0].upper() + name[1:] if name else name


def scan_docs_for_nav(docs_path):
    """Recursively scan docs dir and build nav structure using site-root-relative paths."""
    def scan(path):
        items = []
        try:
            entries = sorted(path.iterdir(), key=lambda e: e.name)
        except PermissionError:
            return items
        for entry in entries:
            if entry.name in SKIP_NAMES or entry.name.startswith('.'):
                continue
            if entry.is_dir():
                children = scan(entry)
                label = nice_label(strip_prefix(entry.name))
                rel_parts = [strip_prefix(p) for p in entry.relative_to(docs_path).parts]
                # Root-relative path (no domain), e.g. /EMD_Repository/Models/
                url = '/' + '/'.join(rel_parts) + '/'
                items.append({'type': 'group', 'label': label, 'url': url, 'children': children})
            elif entry.suffix in ('.md', '.html'):
                stem = strip_prefix(entry.stem)
                if stem == 'index':
                    continue
                label = nice_label(stem)
                rel_parts = [strip_prefix(p) for p in entry.relative_to(docs_path).parts[:-1]]
                url = '/' + '/'.join(rel_parts + [stem])
                if entry.suffix == '.md':
                    url += '/'
                items.append({'type': 'link', 'label': label, 'url': url})
        return items

    nav = [{'type': 'link', 'label': 'Home', 'url': '/'}]
    nav += scan(docs_path)
    return nav


def inject_custom_nav(site_dir, docs_dir):
    """Inject an inline nav script into every HTML file using root-relative paths."""
    docs_path = Path(docs_dir)
    site_path = Path(site_dir)

    nav = scan_docs_for_nav(docs_path)
    nav_json = json.dumps(nav)
    css_json = json.dumps(NAV_CSS)

    # Build the inline script (no external file needed — avoids path depth issues)
    inline_js = NAV_JS_TEMPLATE % {'base_url': '', 'nav_json': nav_json, 'css_json': css_json}
    inline_tag = f'<script>{inline_js}</script>'

    injected = 0
    for html_path in site_path.rglob('*.html'):
        content = html_path.read_text(encoding='utf-8')
        if 'custom-nav.js' in content or 'id="custom-nav"' in content or 'toggleNavGroup' in content:
            continue
        new_content = content.replace('</body>', f'  {inline_tag}\n</body>')
        if new_content == content:
            new_content = content.replace('</html>', f'  {inline_tag}\n</html>')
        html_path.write_text(new_content, encoding='utf-8')
        injected += 1

    print(f"Custom nav: injected into {injected} HTML files")


##############################################################################
# End custom nav
##############################################################################


def on_post_build(config, **kwargs):
    """Post-build hook: clean numeric prefixes from build folder and generate root redirect."""
    site_dir = Path(config['site_dir']).resolve()
    
    name_replacements, rename_operations = collect_renames(site_dir)
    
    if name_replacements:
        fix_html_links(site_dir, name_replacements)
        update_summary_file(site_dir, name_replacements)
        rename_all_items(rename_operations)
    
    # Generate root-level redirect
    generate_root_redirect(site_dir)

    # Inject custom nav sidebar into all HTML files
    inject_custom_nav(site_dir, config['docs_dir'])
