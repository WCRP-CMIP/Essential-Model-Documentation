---
title: View Horizontal Grid
hide:
  - navigation
  - toc
search:
  exclude: true
---

# Horizontal Grid Viewer

<style>
.emd-view { width: 100%; font-family: inherit; }
.emd-view-loading,
.emd-view-error {
  padding: 28px; text-align: center; color: #666;
  border: 1px dashed #ccc; border-radius: 6px; margin: 18px 0;
}
.emd-view-error { color: #a40e4c; border-color: #f3c4d2; background: #fff7fa; }
.emd-view-back {
  display: inline-block; margin-bottom: 16px;
  font-size: 12px; color: #1a4a80; text-decoration: none;
  font-family: 'Source Code Pro', monospace;
}
.emd-view-back:hover { text-decoration: underline; }
.emd-view-header { margin-bottom: 22px; padding-bottom: 18px; border-bottom: 1px solid #e4e6ec; }
.emd-view-badge {
  display: inline-block; padding: 3px 10px; border-radius: 999px;
  background: #e8f0ff; color: #1a4a80; font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.08em;
  font-family: 'Source Code Pro', monospace; margin-bottom: 10px;
}
.emd-view-title { font-size: 1.6rem; font-weight: 700; color: #0d1035; margin: 0 0 6px; }
.emd-view-id    { font-family: 'Source Code Pro', monospace; font-size: 12px; color: #888; }
.emd-view-desc  { color: #444; line-height: 1.65; margin: 12px 0 0; font-size: 0.95rem; }

.emd-view-stat-row {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px; margin: 18px 0;
}
.emd-view-stat {
  background: #f7f8fa; border-left: 3px solid #0d1035;
  border-radius: 4px; padding: 10px 14px;
}
.emd-view-stat-label {
  font-family: 'Source Code Pro', monospace; color: #888;
  font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em;
  margin-bottom: 3px;
}
.emd-view-stat-value {
  font-family: 'Source Code Pro', monospace; color: #0d1035;
  font-weight: 600; font-size: 14px;
}

.emd-view-section { margin: 26px 0; }
.emd-view-section-title {
  font-family: 'Source Code Pro', monospace;
  font-size: 11px; font-weight: 700; color: #0d1035;
  text-transform: uppercase; letter-spacing: 0.09em;
  margin-bottom: 10px;
}

.emd-view-prop-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.emd-view-prop-table tr { border-bottom: 1px solid #eef0f4; }
.emd-view-prop-table tr:last-child { border-bottom: none; }
.emd-view-prop-table td { padding: 9px 12px; vertical-align: top; }
.emd-view-prop-table td:first-child {
  font-family: 'Source Code Pro', monospace;
  font-weight: 600; color: #555; font-size: 0.78rem;
  text-transform: uppercase; letter-spacing: 0.04em;
  width: 32%; white-space: nowrap;
}
.emd-view-prop-table td:last-child { color: #222; word-break: break-word; }
.emd-view-prop-table code {
  font-family: 'Source Code Pro', monospace; font-size: 0.85em;
  background: #f3f4f8; padding: 1px 5px; border-radius: 3px;
}

.emd-view-tag {
  display: inline-block; padding: 3px 10px; margin: 2px 4px 2px 0;
  border-radius: 14px; font-size: 11px;
  background: #f3f4f8; color: #333; border: 1px solid #e4e6ec;
}
.emd-view-tag.link { background: #fff0f4; color: #a40e4c; border-color: #f3c4d2; }
.emd-view-tag a { color: inherit; text-decoration: none; }
.emd-view-tag a:hover { text-decoration: underline; }
.emd-view-list-item { margin-bottom: 4px; }
.emd-view-link-card {
  display: inline-block; padding: 8px 12px; margin: 4px 6px 4px 0;
  border: 1px solid #e4e6ec; border-radius: 6px;
  background: #fafbfd; text-decoration: none; color: #0d1035;
  font-size: 0.85rem; min-width: 120px;
}
.emd-view-link-card:hover { background: #e8f0ff; border-color: #1a4a80; }
.emd-view-link-card-id { font-family: 'Source Code Pro', monospace; color: #888; font-size: 10px; display: block; }
.emd-view-link-card-name { color: #0d1035; font-weight: 600; }

.emd-view-json-toggle {
  margin: 28px 0 8px;
  border: 1px solid #e4e6ec; border-radius: 6px; padding: 10px 14px;
  background: #fafbfd; font-size: 0.85rem; cursor: pointer;
}
.emd-view-json-toggle summary {
  font-family: 'Source Code Pro', monospace;
  font-weight: 600; color: #555; outline: none;
}
.emd-view-json-toggle pre {
  margin: 10px 0 0; padding: 12px; background: #0d1035; color: #d4d9ff;
  border-radius: 4px; overflow-x: auto; font-size: 0.78rem; line-height: 1.5;
}
</style>

<div class="emd-view">
  <a class="emd-view-back" href="../Horizontal_Computational_Grids/">← Back to all Horizontal Computational Grids</a>
  <div id="emd-view-content">
    <div class="emd-view-loading">Loading entry…</div>
  </div>
</div>

<script>
(function () {
  'use strict';

  var STEM       = "Horizontal_Computational_Grids";
  var SINGULAR   = "Horizontal Grid";
  var BADGE_TEXT = SINGULAR;
  var STAT_KEYS  = ["arrangement"];       /* JSON list */
  var LINK_TYPES = {"family":"model_family","horizontal_grid_cell":"horizontal_grid_cells","horizontal_subgrid":"horizontal_subgrid","horizontal_computational_grid":"horizontal_computational_grids","vertical_computational_grid":"vertical_computational_grids","model_component":"model_components","component":"model_components","component_configs":"horizontal_computational_grids","horizontal_subgrids":"horizontal_subgrid","esm_family":"earth_system_model_families"};      /* JSON map: field name -> view-page stem */

  var params  = new URLSearchParams(window.location.search);
  var entryId = (params.get('id') || '').trim();
  var contentEl = document.getElementById('emd-view-content');

  if (!entryId) {
    contentEl.innerHTML =
      '<div class="emd-view-error">No entry ID specified.<br>' +
      'Add <code>?id=&lt;identifier&gt;</code> to the URL.</div>';
    return;
  }

  /* JSON sits next to the summary page at ../<stem>_raw.json */
  fetch('../' + STEM + '_raw.json')
    .then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status + ' fetching ' + STEM + '_raw.json');
      return r.json();
    })
    .then(function (items) {
      var entry = findEntry(items, entryId);
      if (!entry) {
        contentEl.innerHTML =
          '<div class="emd-view-error">No entry with id <code>' + escapeHtml(entryId) +
          '</code> in <code>' + STEM + '_raw.json</code>.</div>';
        return;
      }
      renderEntry(entry);
    })
    .catch(function (err) {
      contentEl.innerHTML =
        '<div class="emd-view-error">Failed to load: ' + escapeHtml(err.message) + '</div>';
    });

  /* ── helpers ─────────────────────────────────────────────── */

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function lastSeg(s) {
    if (!s) return '';
    s = String(s);
    var idx = Math.max(s.lastIndexOf('/'), s.lastIndexOf(':'));
    return idx >= 0 ? s.slice(idx + 1) : s;
  }

  function findEntry(items, id) {
    if (!Array.isArray(items)) return null;
    var lower = id.toLowerCase();
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      if (!it || typeof it !== 'object') continue;
      var candidates = [
        it.validation_key,
        it.ui_label,
        it['@id'],
        lastSeg(it['@id']),
        it.name
      ].map(function (x) { return x == null ? '' : String(x).toLowerCase(); });
      if (candidates.indexOf(lower) >= 0) return it;
    }
    return null;
  }

  function bestLabel(entry) {
    if (!entry || typeof entry !== 'object') return String(entry || '');
    return entry.name || entry.ui_label || entry.validation_key ||
           lastSeg(entry['@id']) || '(unnamed)';
  }

  function bestId(entry) {
    if (!entry || typeof entry !== 'object') return String(entry || '');
    return entry.validation_key || lastSeg(entry['@id']) || '';
  }

  function isNoneVal(v) {
    if (v === null || v === undefined) return true;
    if (typeof v === 'string') {
      var s = v.trim().toLowerCase();
      return s === '' || s === 'none' || s === 'null' || s === 'n/a' || s === './';
    }
    if (Array.isArray(v)) return v.length === 0;
    return false;
  }

  function formatKey(k) {
    return String(k).replace(/[_-]/g, ' ')
      .replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }

  function viewUrlFor(field, id) {
    var targetStem = LINK_TYPES[field];
    if (!targetStem) return null;
    return '../view_' + targetStem.toLowerCase() + '/?id=' + encodeURIComponent(id);
  }

  /* ── value renderer ─────────────────────────────────────────── */

  function renderValue(field, value) {
    if (isNoneVal(value)) return '<span style="color:#aaa">—</span>';

    /* Linked-object renderer */
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      if ('@value' in value) return escapeHtml(String(value['@value']));
      var label = bestLabel(value);
      var id    = bestId(value);
      var href  = viewUrlFor(field, id);
      if (href) {
        return '<a class="emd-view-link-card" href="' + href + '">' +
          '<span class="emd-view-link-card-name">' + escapeHtml(label) + '</span>' +
          '<span class="emd-view-link-card-id">' + escapeHtml(id) + '</span>' +
        '</a>';
      }
      return '<span class="emd-view-tag link">' + escapeHtml(label) +
        (id && id !== label ? ' <code>(' + escapeHtml(id) + ')</code>' : '') + '</span>';
    }

    /* Array — render each item */
    if (Array.isArray(value)) {
      if (!value.length) return '<span style="color:#aaa">—</span>';
      return value.map(function (v) {
        return '<div class="emd-view-list-item">' + renderValue(field, v) + '</div>';
      }).join('');
    }

    /* URLs become clickable links */
    var s = String(value);
    if (/^https?:\/\//i.test(s)) {
      return '<a href="' + escapeHtml(s) + '" target="_blank" rel="noopener">' +
             escapeHtml(s) + '</a>';
    }

    /* Bare string that names a sibling record — also link it. */
    var href = viewUrlFor(field, s);
    if (href) {
      return '<a class="emd-view-tag link" href="' + href + '">' + escapeHtml(s) + '</a>';
    }

    /* Numbers shown in code style for visual contrast */
    if (typeof value === 'number') {
      return '<code>' + escapeHtml(s) + '</code>';
    }
    return escapeHtml(s);
  }

  /* ── main render ─────────────────────────────────────────────── */

  function renderEntry(entry) {
    var label    = bestLabel(entry);
    var id       = bestId(entry);
    var desc     = isNoneVal(entry.description) ? '' : entry.description;
    var validKey = entry.validation_key || id || lastSeg(entry['@id']);

    document.title = label + ' — ' + SINGULAR;

    var html = '';

    /* Header */
    html += '<header class="emd-view-header">';
    html += '<div class="emd-view-badge">' + escapeHtml(BADGE_TEXT) + '</div>';
    html += '<h1 class="emd-view-title">' + escapeHtml(label) + '</h1>';
    if (validKey) html += '<div class="emd-view-id">id: <code>' + escapeHtml(validKey) + '</code></div>';
    if (desc)     html += '<p class="emd-view-desc">' + escapeHtml(desc) + '</p>';
    html += '</header>';

    /* Quick stats from STAT_KEYS — show fields the script flagged as numeric/important */
    var stats = [];
    STAT_KEYS.forEach(function (k) {
      if (k in entry && !isNoneVal(entry[k])) {
        stats.push({ label: formatKey(k), value: String(entry[k]) });
      }
    });
    if (stats.length) {
      html += '<div class="emd-view-stat-row">';
      stats.forEach(function (s) {
        html += '<div class="emd-view-stat">' +
          '<div class="emd-view-stat-label">' + escapeHtml(s.label) + '</div>' +
          '<div class="emd-view-stat-value">' + escapeHtml(s.value) + '</div>' +
        '</div>';
      });
      html += '</div>';
    }

    /* Properties table */
    var skip = { 'validation_key': 1, 'ui_label': 1, 'description': 1, 'name': 1 };
    var keys = Object.keys(entry).filter(function (k) {
      return k.charAt(0) !== '@' && !skip[k] && STAT_KEYS.indexOf(k) < 0;
    });

    if (keys.length) {
      html += '<section class="emd-view-section">';
      html += '<h2 class="emd-view-section-title">Properties</h2>';
      html += '<table class="emd-view-prop-table">';
      keys.forEach(function (k) {
        html += '<tr><td>' + escapeHtml(formatKey(k)) + '</td>' +
                '<td>' + renderValue(k, entry[k]) + '</td></tr>';
      });
      html += '</table>';
      html += '</section>';
    }

    /* Raw JSON (collapsible) */
    html += '<details class="emd-view-json-toggle">' +
      '<summary>View raw JSON</summary>' +
      '<pre>' + escapeHtml(JSON.stringify(entry, null, 2)) + '</pre>' +
      '</details>';

    contentEl.innerHTML = html;
  }
}());
</script>
