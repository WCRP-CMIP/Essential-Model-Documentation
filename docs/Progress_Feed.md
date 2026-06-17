---
hide:
  - toc
---

# EMD Submission Feed

<style>
* { box-sizing: border-box; }

.emd-feed-wrap {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
}

/* ── top bar ── */
.emd-feed-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}
.emd-feed-status {
  font-size: 0.75rem;
  color: var(--emd-text-tertiary);
}
.emd-refresh-btn {
  padding: 0.4rem 1rem;
  background: var(--emd-primary);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.emd-refresh-btn:hover  { background: var(--emd-primary-dark); }
.emd-refresh-btn:disabled { background: var(--emd-text-tertiary); cursor: not-allowed; }

/* ── filter pills ── */
.emd-filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}
.emd-pill {
  padding: 0.25rem 0.85rem;
  border-radius: 20px;
  border: 1.5px solid var(--emd-border);
  background: var(--emd-bg);
  font-size: 0.72rem;
  font-weight: 500;
  color: var(--emd-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.emd-pill:hover { border-color: var(--emd-primary); color: var(--emd-primary); }
.emd-pill.active {
  background: var(--emd-primary);
  border-color: var(--emd-primary);
  color: #fff;
}
.emd-pill-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ── cards ── */
.emd-card {
  background: var(--emd-bg);
  border: 1px solid var(--emd-border);
  border-left: 4px solid var(--emd-border);
  border-radius: 8px;
  margin-bottom: 0.4rem;
  overflow: hidden;
  transition: box-shadow 0.15s;
  cursor: pointer;
}
.emd-card:hover { box-shadow: 0 2px 10px rgba(0,0,0,0.07); }

.emd-card-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.45rem 0.75rem;
  min-height: 2.2rem;
}

.emd-card-stamp {
  font-family: "JetBrains Mono", monospace;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--emd-text);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}
.emd-badge {
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  color: var(--badge-color);
  background: transparent;
  border: 1.5px solid var(--badge-color);
  white-space: nowrap;
  flex-shrink: 0;
}
.emd-card-spacer { flex: 1; }

.emd-issue-link {
  font-family: "JetBrains Mono", monospace;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--emd-primary);
  text-decoration: none;
  opacity: 0.7;
  flex-shrink: 0;
  white-space: nowrap;
}
.emd-issue-link:hover { opacity: 1; text-decoration: underline; }

.emd-issue-num {
  font-family: "JetBrains Mono", monospace;
  font-size: 0.65rem;
  font-weight: 500;
  color: var(--emd-text-tertiary);
  text-decoration: none;
  flex-shrink: 0;
  white-space: nowrap;
}
.emd-issue-num:hover { color: var(--emd-primary); text-decoration: underline; }

.emd-date {
  font-size: 0.68rem;
  color: var(--emd-text-tertiary);
  white-space: nowrap;
  flex-shrink: 0;
}


/* avatar */
.emd-avatar-stack { display: flex; }
.emd-avatar {
  width: 26px; height: 26px;
  border-radius: 50%;
  border: 2px solid var(--emd-bg);
  box-shadow: 0 1px 3px rgba(0,0,0,0.12);
  margin-left: -8px;
  display: block;
  flex-shrink: 0;
  background: var(--emd-bg-tertiary);
  transition: transform 0.15s;
}
.emd-avatar:first-child { margin-left: 0; }
.emd-avatar:hover { transform: scale(1.12); z-index: 5; }

/* expand icon */
.emd-chevron {
  font-size: 0.7rem;
  color: var(--emd-text-tertiary);
  transition: transform 0.2s;
  flex-shrink: 0;
}
.emd-card.open .emd-chevron { transform: rotate(180deg); }

/* github icon */
.emd-gh-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px; height: 22px;
  opacity: 0.4;
  transition: opacity 0.15s;
  flex-shrink: 0;
}
.emd-gh-link:hover { opacity: 1; }
.emd-gh-link svg { width: 16px; height: 16px; }

/* expanded description */
.emd-body {
  display: none;
  padding: 0.75rem 1rem 1rem;
  background: var(--emd-bg-secondary);
  border-top: 1px solid var(--emd-border-light);
  font-size: 0.85rem;
  color: var(--emd-text-secondary);
  line-height: 1.6;
}
.emd-card.open .emd-body { display: block; }
.emd-body a { color: var(--emd-primary); }
.emd-body-content { font-size: 0.8rem; line-height: 1.6; color: var(--emd-text-secondary); }
.emd-body-content h2,
.emd-body-content h3,
.emd-body-content h4 { margin: 0.5rem 0 0.25rem; color: var(--emd-text); font-size: 0.85rem; }
.emd-body-content pre { background: var(--emd-bg-tertiary); border-radius: 4px; padding: 0.5rem 0.75rem; overflow-x: auto; margin: 0.4rem 0; }
.emd-body-content code { background: var(--emd-bg-tertiary); padding: 0.1em 0.3em; border-radius: 3px; font-family: "JetBrains Mono", monospace; font-size: 0.8em; }

.emd-empty {
  text-align: center;
  padding: 2.5rem;
  color: var(--emd-text-tertiary);
  font-size: 0.9rem;
  border: 1px dashed var(--emd-border);
  border-radius: 10px;
}

.emd-loading {
  text-align: center;
  padding: 3rem;
  color: var(--emd-text-tertiary);
}
.emd-spinner {
  display: inline-block;
  width: 18px; height: 18px;
  border: 2px solid var(--emd-border);
  border-top-color: var(--emd-primary);
  border-radius: 50%;
  animation: emd-spin 0.7s linear infinite;
  vertical-align: -4px;
  margin-right: 0.5rem;
}
.emd-rss-link {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.35rem 0.75rem;
  border: 1.5px solid #e8601a;
  border-radius: 6px;
  color: #e8601a;
  font-size: 0.75rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.15s;
}
.emd-rss-link:hover { background: #e8601a; color: #fff; }

</style>

<div class="emd-feed-wrap">

<div class="emd-feed-topbar">
  <span class="emd-feed-status" id="emd-status">Loading…</span>
  <div style="display:flex;gap:0.5rem;align-items:center;">
    <a class="emd-rss-link" id="emd-rss-link" href="#" title="Subscribe to RSS feed" target="_blank">
      <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm1.5 2.5a1 1 0 1 1 0 2 1 1 0 0 1 0-2zM2 5h1.5A5.5 5.5 0 0 1 9 10.5V12H7.5v-1.5A4 4 0 0 0 3.5 7H2V5zm0 3.5h1.5a2 2 0 0 1 2 2V12H4v-1.5A.5.5 0 0 0 3.5 10H2V8.5z"/></svg>
      RSS
    </a>
    <button class="emd-refresh-btn" id="emd-refresh-btn" onclick="emdRefresh()">↻ Refresh</button>
  </div>
</div>

<div class="emd-filter-bar" id="emd-filter-bar"></div>

<div id="emd-cards"><div class="emd-loading"><span class="emd-spinner"></span>Fetching submissions…</div></div>

</div>

<script>
(function () {
'use strict';

var REPO  = 'WCRP-CMIP/Essential-Model-Documentation';
var API   = 'https://api.github.com/repos/' + REPO + '/issues';
var LABEL = 'emd-submission';
var STAMP_RE   = /^\s*\|\s*([^|]+?)\s*\|/;
var PR_LINK_RE = /\/pull\/(\d+)/;

function extractPR(body) {
  if (!body) return null;
  var m = PR_LINK_RE.exec(body);
  return m ? m[1] : null;
}

var CATEGORY_COLORS = {
  horizontal_grid_cell:          '#2980b9',
  horizontal_computational_grid: '#3498db',
  vertical_computational_grid:   '#16a085',
  model_family:                  '#f39c12',
  model_component:               '#d35400',
  component_config:              '#1abc9c',
  link_existing_component:       '#1abc9c',
  model:                         '#e67e22',
};

var CATEGORY_LABELS = Object.keys(CATEGORY_COLORS);

var GH_ICON = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>';

var allItems = [];
var activeFilter = 'all';

function stamp(title) {
  var m = STAMP_RE.exec(title);
  return m ? m[1].trim() : null;
}

function category(labels) {
  for (var i = 0; i < labels.length; i++) {
    var n = labels[i].name || labels[i];
    if (CATEGORY_LABELS.indexOf(n) >= 0) return n;
  }
  return 'unknown';
}

function timeAgo(iso) {
  var diff = Date.now() - new Date(iso).getTime();
  var m = Math.floor(diff / 60000);
  var h = Math.floor(diff / 3600000);
  var d = Math.floor(h / 24);
  if (m < 1)  return 'Just now';
  if (m < 60) return m + 'm ago';
  if (h < 24) return h + 'h ago';
  if (d < 7)  return d + 'd ago';
  return new Date(iso).toLocaleDateString();
}

function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

async function fetchAll() {
  var items = [];
  var page  = 1;
  while (true) {
    var url = API + '?state=closed&labels=' + LABEL + '&per_page=100&page=' + page;
    var r = await fetch(url, { headers: { Accept: 'application/vnd.github+json' } });
    if (!r.ok) throw new Error('GitHub API ' + r.status);
    var batch = await r.json();
    batch = batch.filter(function(i) { return !i.pull_request; });
    items = items.concat(batch);
    if (batch.length < 100) break;
    page++;
  }
  return items;
}

function buildItems(raw) {
  var out = [];
  raw.forEach(function(issue) {
    var s = stamp(issue.title);
    if (!s || s.toLowerCase() === 'skip') return;
    var cat = category(issue.labels);
    var body = issue.body || '';
    var prNumber = extractPR(body);
    out.push({
      number:    issue.number,
      stamp:     s,
      category:  cat,
      color:     CATEGORY_COLORS[cat] || '#94a3b8',
      submitter: issue.user ? issue.user.login : 'unknown',
      avatar:    issue.user ? issue.user.avatar_url : '',
      closedAt:  issue.closed_at,
      url:       issue.html_url,
      prNumber:  prNumber,
      prUrl:     prNumber ? 'https://github.com/' + REPO + '/pull/' + prNumber : null,
      body:      body,
    });
  });
  out.sort(function(a,b) { return new Date(b.closedAt) - new Date(a.closedAt); });
  return out;
}

function renderBody(md) {
  if (!md) return '';
  md = md.replace(/<!--\s*emd-bot-issue-status\s*-->[\s\S]*/i, '').trim();
  if (!md) return '';
  // Compact 3+ consecutive blank lines down to 1
  md = md.replace(/\n{3,}/g, '\n\n');
  var html = esc(md)
    .replace(/```[\w]*\n?([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^## (.+)$/gm,  '<h3>$1</h3>')
    .replace(/^# (.+)$/gm,   '<h2>$1</h2>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" onclick="event.stopPropagation()">$1</a>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>');
  return '<div class="emd-body-content"><p>' + html + '</p></div>';
}

function buildFilterBar(items) {
  var counts = { all: items.length };
  items.forEach(function(i) {
    counts[i.category] = (counts[i.category] || 0) + 1;
  });

  var bar = document.getElementById('emd-filter-bar');
  var pills = [{ key: 'all', label: 'All (' + items.length + ')', color: 'var(--emd-primary)' }];
  CATEGORY_LABELS.forEach(function(cat) {
    if (counts[cat]) pills.push({ key: cat, label: cat.replace(/_/g, ' ') + ' (' + counts[cat] + ')', color: CATEGORY_COLORS[cat] });
  });

  bar.innerHTML = pills.map(function(p) {
    return '<button class="emd-pill' + (activeFilter === p.key ? ' active' : '') + '" onclick="emdFilter(\'' + p.key + '\')">' +
      '<span class="emd-pill-dot" style="background:' + p.color + '"></span>' + esc(p.label) + '</button>';
  }).join('');
}

window.emdFilter = function(key) {
  activeFilter = key;
  buildFilterBar(allItems);
  renderCards();
};

function renderCards() {
  var filtered = activeFilter === 'all'
    ? allItems
    : allItems.filter(function(i) { return i.category === activeFilter; });

  var container = document.getElementById('emd-cards');
  if (!filtered.length) {
    container.innerHTML = '<div class="emd-empty">No submissions found.</div>';
    return;
  }

  container.innerHTML = filtered.map(function(item, idx) {
    var bodyHtml = renderBody(item.body);
    return '<div class="emd-card" id="emd-card-' + idx + '" style="border-left-color:' + item.color + '" onclick="emdToggle(' + idx + ')">' +
      '<div class="emd-card-row">' +
        '<a class="emd-issue-num" href="' + esc(item.url) + '" target="_blank" onclick="event.stopPropagation()" title="Issue #' + item.number + '">#' + item.number + '</a>' +
        '<span class="emd-card-stamp">' + esc(item.stamp) + '</span>' +
        '<span class="emd-card-spacer"></span>' +
        (item.prUrl ? '<a class="emd-issue-link" href="' + esc(item.prUrl) + '" target="_blank" onclick="event.stopPropagation()" title="PR #' + item.prNumber + '">PR #' + item.prNumber + '</a>' : '') +
        '<span class="emd-badge" style="--badge-color:' + item.color + '">' + esc(item.category.replace(/_/g,' ')) + '</span>' +
        (item.avatar ? '<a href="https://github.com/' + esc(item.submitter) + '" target="_blank" onclick="event.stopPropagation()" title="' + esc(item.submitter) + '">' +
          '<img class="emd-avatar" src="' + esc(item.avatar) + '?size=26" alt="' + esc(item.submitter) + '">' +
        '</a>' : '') +
        '<span class="emd-date">' + timeAgo(item.closedAt) + '</span>' +
        '<span class="emd-chevron">▼</span>' +
      '</div>' +
      (bodyHtml ? '<div class="emd-body">' + bodyHtml + '</div>' : '') +
    '</div>';
  }).join('');
}

window.emdToggle = function(idx) {
  document.getElementById('emd-card-' + idx).classList.toggle('open');
};

function setStatus(msg) {
  document.getElementById('emd-status').textContent = msg;
}

window.emdRefresh = async function() {
  var btn = document.getElementById('emd-refresh-btn');
  btn.disabled = true; btn.textContent = '…';
  document.getElementById('emd-cards').innerHTML = '<div class="emd-loading"><span class="emd-spinner"></span>Fetching submissions…</div>';
  try {
    var raw = await fetchAll();
    allItems = buildItems(raw);
    buildFilterBar(allItems);
    renderCards();
    setStatus('Updated ' + new Date().toLocaleTimeString() + ' · ' + allItems.length + ' submissions');
  } catch(e) {
    setStatus('Error: ' + e.message);
    document.getElementById('emd-cards').innerHTML = '<div class="emd-empty">Could not load submissions — ' + esc(e.message) + '</div>';
  }
  btn.disabled = false; btn.textContent = '↻ Refresh';
};

// Set RSS link to the emd_rss.xml relative to the current site root
(function() {
  var origin = window.location.origin;
  var path = window.location.pathname;
  // Walk up to site root (strip page path, keep base)
  var parts = path.replace(/\/$/, '').split('/');
  // Find the root: drop the last segment (the page name)
  parts.pop();
  var base = origin + (parts.length ? parts.join('/') : '');
  var rssUrl = base.replace(/\/$/, '') + '/emd_rss.xml';
  var link = document.getElementById('emd-rss-link');
  if (link) link.href = rssUrl;
}());

emdRefresh();
}());
</script>
