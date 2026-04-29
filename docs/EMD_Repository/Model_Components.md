# Model Components

**Stage 3.** Model components are specific versioned instances of model software — an atmosphere, ocean, sea-ice, or land-surface code at a specific version — bound to horizontal and vertical grids. Each produces a component config ID used in Stage 4.

---

!!! info "Generated files"
    This page is auto-generated during the build from live registry data. Three files are produced for each record type:

    - **`Model_Components.md`** — this page, embedded in the MkDocs site layout
    - **`Model_Components_data.json`** — processed similarity matrices, dendrogram tree, and key schema
    - **`Model_Components_raw.json`** — raw JSON-LD records as fetched from the cmipld registry (depth 2)

---

<link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;600;700&family=Pacifico&display=swap" rel="stylesheet">

<style>
.emd-viz { font-family: 'Source Code Pro', monospace; width: 100%; }
.emd-section { margin-bottom: 2.5rem; }
.emd-section-label {
  font-size: 11px; font-weight: 700; color: #0d1035;
  text-transform: uppercase; letter-spacing: 0.09em;
  margin-bottom: 12px; display: block;
}
.emd-selector-row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
#emd-entry-select {
  flex: 1; min-width: 240px; padding: 8px 12px;
  border: 1.5px solid #ccc; border-radius: 6px;
  font-family: 'Source Code Pro', monospace; font-size: 12px;
  color: #0d1035; background: #fff; cursor: pointer;
}
#emd-entry-select:focus { outline: none; border-color: #0d1035; }
#emd-go-btn {
  padding: 8px 18px; border: 1.5px solid #0d1035; border-radius: 6px;
  background: #0d1035; color: #fff;
  font-family: 'Source Code Pro', monospace; font-size: 12px;
  font-weight: 600; cursor: pointer; transition: background .15s;
}
#emd-go-btn:hover { background: #1a2080; }
.emd-stats {
  margin-top: 10px; font-size: 11px; color: #888;
  display: flex; gap: 20px; flex-wrap: wrap;
}
.emd-stats b { color: #0d1035; }
.emd-filter-bar { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.emd-fbtn {
  padding: 4px 11px; border-radius: 20px; border: 1.5px solid #ccc;
  background: #fff; cursor: pointer; font-family: 'Source Code Pro', monospace;
  font-size: 11px; color: #555; transition: all .15s;
}
.emd-fbtn:hover  { border-color: #0d1035; color: #0d1035; }
.emd-fbtn.active { background: #0d1035; border-color: #0d1035; color: #fff; font-weight: 600; }
.emd-tip {
  position: fixed; background: #0d1035; color: #fff;
  padding: 10px 14px; border-radius: 8px; font-size: 12px;
  font-family: 'Source Code Pro', monospace; pointer-events: none;
  opacity: 0; transition: opacity .12s; line-height: 1.9;
  box-shadow: 0 6px 24px rgba(0,0,0,.25); max-width: 280px; z-index: 999;
}
.emd-tip-link { color: #e8607e; font-weight: 600; }
.emd-tip-text { color: #f5c842; font-weight: 600; }
.emd-tip-head { font-weight: 700; font-size: 13px;
  border-bottom: 1px solid rgba(255,255,255,.2); padding-bottom: 5px; margin-bottom: 5px; }
/* ── font toggle ── */
.emd-font-btn {
  padding: 5px 12px; border-radius: 20px; border: 1.5px solid #ccc;
  background: #fff; font-size: 11px; cursor: pointer;
  font-family: 'Source Code Pro', monospace; color: #888;
  transition: all .2s; white-space: nowrap;
}
.emd-font-btn:hover { border-color: #a060c0; color: #602080; }
.emd-font-btn.active { background: #f3e8ff; border-color: #a060c0;
  color: #602080; font-family: 'Pacifico', cursive; }
.emd-viz.pretty svg text { font-family: 'Pacifico', cursive !important; }
.emd-viz.pretty #emd-entry-select,
.emd-viz.pretty .emd-stats,
.emd-viz.pretty .emd-section-label { font-family: 'Pacifico', cursive !important; }
</style>

<div class="emd-viz">

<div class="emd-section">
<span class="emd-section-label">View a specific Model Component</span>
<div class="emd-selector-row">
  <select id="emd-entry-select">
    <option value="">Select an entry…</option>
    <option value="../Model_Components/bisicles-ukesm-ismip6-1_0/">bisicles-ukesm-ismip6-1_0</option>
    <option value="../Model_Components/tactic/">tactic</option>
    <option value="../Model_Components/clm4/">clm4</option>
    <option value="../Model_Components/surfex_v8_modeling_platform/">surfex_v8_modeling_platform</option>
    <option value="../Model_Components/hadam3/">hadam3</option>
    <option value="../Model_Components/arpege-climat_version_6_3/">arpege-climat_version_6_3</option>
    <option value="../Model_Components/reprobus-c_v2_0/">reprobus-c_v2_0</option>
    <option value="../Model_Components/gelato/">gelato</option>
    <option value="../Model_Components/piscesv2-gas/">piscesv2-gas</option>
    <option value="../Model_Components/nemo_v3_6/">nemo_v3_6</option>
  </select>
  <button id="emd-go-btn" onclick="emdGotoEntry()">Open →</button>
  <button class="emd-font-btn" id="emd-font-toggle" onclick="emdToggleFont()">✨ Pretty font</button>
</div>
<div class="emd-stats">
  <span><b>10</b> registered entries</span>
  <span>Endpoint: <b>model_component</b></span>
</div>
</div>

<div class="emd-section">
<span class="emd-section-label">Similarity &amp; Hierarchical Clustering</span>
<div class="emd-filter-bar" id="emd-filter-bar"></div>
<div id="emd-combined-chart" style="overflow-x:auto; display:flex; justify-content:center;"></div>
<div class="emd-tip" id="emd-tip"></div>
</div>

<div class="emd-section">
<span class="emd-section-label">Record Key Schema</span>
<div id="emd-key-graph"></div>
</div>

</div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
(function () {
'use strict';

/* ── injected data ─────────────────────────────────────────────────────── */
var EMD_DATA    = {"ids":["bisicles-ukesm-ismip6-1_0","tactic","clm4","surfex_v8_modeling_platform","hadam3","arpege-climat_version_6_3","reprobus-c_v2_0","gelato","piscesv2-gas","nemo_v3_6"],"link":[[0.0,0.028321467371671287,0.06354571826912403,0.0,0.08008260189445798,0.013206579842902829,0.03336755435114665,0.0,0.02034869109253925,0.0],[0.028321467371671287,0.0,0.03113848947717675,0.08485235684482495,0.043795218473467235,0.08684838734053892,0.13001552554555912,0.05809170796507239,0.02611878295630914,0.04574271253356089],[0.06354571826912403,0.03113848947717675,0.0,0.190958146215307,0.12596625602330952,0.051134089989285134,0.1142051248501426,0.0,0.02132031984235423,0.04223732941817712],[0.0,0.08485235684482495,0.190958146215307,0.0,0.08838128442975393,0.10163404675309934,0.15418045925099905,0.048217723613393555,0.02890574924422914,0.06607152203940175],[0.08008260189445798,0.043795218473467235,0.12596625602330952,0.08838128442975393,0.0,0.14027663509444627,0.15302456664295516,0.03077108925676573,0.021871833432872,0.04332992377762123],[0.013206579842902829,0.08684838734053892,0.051134089989285134,0.10163404675309934,0.14027663509444627,0.0,0.16749972997466012,0.11426255439980898,0.0803579674048647,0.10613458406050613],[0.03336755435114665,0.13001552554555912,0.1142051248501426,0.15418045925099905,0.15302456664295516,0.16749972997466012,0.0,0.01711050311621888,0.06306405407493056,0.10778555017859458],[0.0,0.05809170796507239,0.0,0.048217723613393555,0.03077108925676573,0.11426255439980898,0.01711050311621888,0.0,0.0648491340222091,0.04523395349100263],[0.02034869109253925,0.02611878295630914,0.02132031984235423,0.02890574924422914,0.021871833432872,0.0803579674048647,0.06306405407493056,0.0648491340222091,0.0,0.093919715902127],[0.0,0.04574271253356089,0.04223732941817712,0.06607152203940175,0.04332992377762123,0.10613458406050613,0.10778555017859458,0.04523395349100263,0.093919715902127,0.0]],"text":[[0.0,0.028321467371671287,0.06354571826912403,0.0,0.08008260189445798,0.013206579842902829,0.03336755435114665,0.0,0.02034869109253925,0.0],[0.028321467371671287,0.0,0.03113848947717675,0.08485235684482495,0.043795218473467235,0.08684838734053892,0.13001552554555912,0.05809170796507239,0.02611878295630914,0.04574271253356089],[0.06354571826912403,0.03113848947717675,0.0,0.190958146215307,0.12596625602330952,0.051134089989285134,0.1142051248501426,0.0,0.02132031984235423,0.04223732941817712],[0.0,0.08485235684482495,0.190958146215307,0.0,0.08838128442975393,0.10163404675309934,0.15418045925099905,0.048217723613393555,0.02890574924422914,0.06607152203940175],[0.08008260189445798,0.043795218473467235,0.12596625602330952,0.08838128442975393,0.0,0.14027663509444627,0.15302456664295516,0.03077108925676573,0.021871833432872,0.04332992377762123],[0.013206579842902829,0.08684838734053892,0.051134089989285134,0.10163404675309934,0.14027663509444627,0.0,0.16749972997466012,0.11426255439980898,0.0803579674048647,0.10613458406050613],[0.03336755435114665,0.13001552554555912,0.1142051248501426,0.15418045925099905,0.15302456664295516,0.16749972997466012,0.0,0.01711050311621888,0.06306405407493056,0.10778555017859458],[0.0,0.05809170796507239,0.0,0.048217723613393555,0.03077108925676573,0.11426255439980898,0.01711050311621888,0.0,0.0648491340222091,0.04523395349100263],[0.02034869109253925,0.02611878295630914,0.02132031984235423,0.02890574924422914,0.021871833432872,0.0803579674048647,0.06306405407493056,0.0648491340222091,0.0,0.093919715902127],[0.0,0.04574271253356089,0.04223732941817712,0.06607152203940175,0.04332992377762123,0.10613458406050613,0.10778555017859458,0.04523395349100263,0.093919715902127,0.0]],"method":"embedding (all-MiniLM-L6-v2) | link: text (links uninformative) | order: UPGMA leaf traversal","folder":"Model Components","meta":[{"label":"bisicles-ukesm-ismip6-1_0","tags":["land-ice"]},{"label":"tactic","tags":["aerosol"]},{"label":"clm4","tags":["land-surface"]},{"label":"surfex_v8_modeling_platform","tags":["land-surface"]},{"label":"hadam3","tags":["atmosphere"]},{"label":"arpege-climat_version_6_3","tags":["atmosphere"]},{"label":"reprobus-c_v2_0","tags":["atmospheric-chemistry"]},{"label":"gelato","tags":["sea-ice"]},{"label":"piscesv2-gas","tags":["ocean-biogeochemistry"]},{"label":"nemo_v3_6","tags":["ocean"]}],"tree":{"name":"","leaf":false,"children":[{"name":"bisicles-ukesm-ismip6-1_0","leaf":true,"spectral_index":0,"value":0.0},{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"tactic","leaf":true,"spectral_index":1,"value":0.0},{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"clm4","leaf":true,"spectral_index":2,"value":0.0},{"name":"surfex_v8_modeling_platform","leaf":true,"spectral_index":3,"value":0.0}],"value":0.8090418537846931},{"name":"","leaf":false,"children":[{"name":"hadam3","leaf":true,"spectral_index":4,"value":0.0},{"name":"","leaf":false,"children":[{"name":"arpege-climat_version_6_3","leaf":true,"spectral_index":5,"value":0.0},{"name":"reprobus-c_v2_0","leaf":true,"spectral_index":6,"value":0.0}],"value":0.8325002700253399}],"value":0.8533493991312993}],"value":0.8940831231172351}],"value":0.9246700044636867},{"name":"","leaf":false,"children":[{"name":"gelato","leaf":true,"spectral_index":7,"value":0.0},{"name":"","leaf":false,"children":[{"name":"piscesv2-gas","leaf":true,"spectral_index":8,"value":0.0},{"name":"nemo_v3_6","leaf":true,"spectral_index":9,"value":0.0}],"value":0.906080284097873}],"value":0.9449584562433941}],"value":0.9488114495936287}],"value":0.9734585985753509}};
var EMD_ENTRIES = [{"label":"bisicles-ukesm-ismip6-1_0","url":"../Model_Components/bisicles-ukesm-ismip6-1_0/"},{"label":"tactic","url":"../Model_Components/tactic/"},{"label":"clm4","url":"../Model_Components/clm4/"},{"label":"surfex_v8_modeling_platform","url":"../Model_Components/surfex_v8_modeling_platform/"},{"label":"hadam3","url":"../Model_Components/hadam3/"},{"label":"arpege-climat_version_6_3","url":"../Model_Components/arpege-climat_version_6_3/"},{"label":"reprobus-c_v2_0","url":"../Model_Components/reprobus-c_v2_0/"},{"label":"gelato","url":"../Model_Components/gelato/"},{"label":"piscesv2-gas","url":"../Model_Components/piscesv2-gas/"},{"label":"nemo_v3_6","url":"../Model_Components/nemo_v3_6/"}];
var EMD_SCHEMA  = {"name":"record","children":[{"name":"code_base","type":"scalar"},{"name":"component","type":"scalar"},{"name":"description","type":"scalar"},{"name":"family","type":"scalar"},{"name":"name","type":"scalar"},{"name":"references","type":"scalar"},{"name":"ui_label","type":"scalar"},{"name":"validation_key","type":"scalar"}]};

var ids    = EMD_DATA.ids;
var link   = EMD_DATA.link;
var text   = EMD_DATA.text;
var method = EMD_DATA.method;
var meta   = EMD_DATA.meta;
var tree   = EMD_DATA.tree;
var n      = ids.length;

var FONT    = "'Source Code Pro', monospace";
var RED     = '#a40e4c';
var MUSTARD = '#f2b30d';
var NAVY    = '#0d1035';
var WHITE   = '#ffffff';

/* ── entry selector ────────────────────────────────────────────────────── */
window.emdGotoEntry = function () {
  var v = document.getElementById('emd-entry-select').value;
  if (v) window.location.href = v;
};

/* ── filter buttons ────────────────────────────────────────────────────── */
var allTags = Array.from(new Set(meta.flatMap(function (m) { return m.tags || []; }))).sort();
var activeFilter = null;

function itemVisible(i) {
  return !activeFilter || (meta[i].tags || []).indexOf(activeFilter) >= 0;
}

var matG, dendG;   // assigned below; needed by applyFilter

function applyFilter() {
  if (!matG) return;
  matG.selectAll('.emd-cell').attr('opacity', function (d) {
    if (d.i === d.j) return itemVisible(d.i) ? 1 : 0.08;
    return (itemVisible(d.i) && itemVisible(d.j)) ? 1 : 0.06;
  });
  matG.selectAll('.emd-val').attr('opacity', function (d) {
    return (itemVisible(d.i) && itemVisible(d.j)) ? 1 : 0;
  });
  matG.selectAll('.emd-diag').attr('opacity', function (d, i) { return itemVisible(i) ? 1 : 0.1; });
  matG.selectAll('.emd-xlabel').attr('opacity', function (d, i) { return itemVisible(i) ? 1 : 0.1; });
  matG.selectAll('.emd-ylabel').attr('opacity', function (d, i) { return itemVisible(i) ? 1 : 0.1; });
}

if (allTags.length > 0) {
  var bar = document.getElementById('emd-filter-bar');
  var allBtn = document.createElement('button');
  allBtn.className = 'emd-fbtn active'; allBtn.textContent = 'All';
  allBtn.onclick = function () {
    activeFilter = null;
    document.querySelectorAll('.emd-fbtn').forEach(function (b) { b.classList.remove('active'); });
    allBtn.classList.add('active'); applyFilter();
  };
  bar.appendChild(allBtn);
  allTags.forEach(function (tag) {
    var btn = document.createElement('button');
    btn.className = 'emd-fbtn';
    btn.textContent = tag.replace(/[-_]/g, ' ');
    btn.onclick = function () {
      activeFilter = tag;
      document.querySelectorAll('.emd-fbtn').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active'); applyFilter();
    };
    bar.appendChild(btn);
  });
}

/* ── font toggle ──────────────────────────────────────────────────────── */
window.emdToggleFont = function () {
  var viz = document.querySelector('.emd-viz');
  var btn = document.getElementById('emd-font-toggle');
  viz.classList.toggle('pretty');
  btn.classList.toggle('active');
};

/* ── layout constants ──────────────────────────────────────────────────── */
var cellSize = Math.min(60, Math.floor(Math.min(window.innerWidth * 0.65, 440) / n));
var gap      = Math.max(2, Math.round(cellSize * 0.055));
var inner    = cellSize - gap;
var rad      = Math.round(inner * 0.14);
var lblFs    = Math.max(8, Math.round(cellSize * 0.145));
var maxLLen  = Math.max.apply(null, meta.map(function (m) { return Math.min(m.label.length, 50); }));
var XLBL_H   = Math.ceil(maxLLen * lblFs * 0.62) + 12;
var YLBL_W   = Math.ceil(maxLLen * lblFs * 0.62) + 16;
var LEG_H    = 62;
var DEND_W   = Math.max(60, Math.round(n * cellSize * 0.18));  /* narrow right-side dendrogram */
var matW     = n * cellSize;
var margin   = { top: 30, right: DEND_W + 8, bottom: XLBL_H + LEG_H + 16, left: YLBL_W };
var totalW   = matW + margin.left + margin.right;
var totalH   = matW + margin.top + margin.bottom;

/* ── root SVG ──────────────────────────────────────────────────────────── */
var svg = d3.select('#emd-combined-chart').append('svg')
  .attr('width', totalW).attr('height', totalH);

var defs = svg.append('defs');
[['emd-leg-red', RED], ['emd-leg-mustard', MUSTARD]].forEach(function (pair) {
  var gr = defs.append('linearGradient').attr('id', pair[0]).attr('x1','0%').attr('x2','100%');
  gr.append('stop').attr('offset','0%').attr('stop-color', WHITE);
  gr.append('stop').attr('offset','100%').attr('stop-color', pair[1]);
});

/* Clip the dendrogram to its column */
defs.append('clipPath').attr('id','emd-dend-clip')
  .append('rect').attr('x', 0).attr('y', 0).attr('width', DEND_W).attr('height', matW);

/* Matrix is at left; dendrogram is to the RIGHT of the matrix */
matG = svg.append('g')
  .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

dendG = svg.append('g')
  .attr('transform', 'translate(' + (margin.left + matW) + ',' + margin.top + ')')
  .attr('clip-path', 'url(#emd-dend-clip)');

/* ── colour helpers ────────────────────────────────────────────────────── */
function hexToRgb(h) {
  return [parseInt(h.slice(1,3),16)/255, parseInt(h.slice(3,5),16)/255, parseInt(h.slice(5,7),16)/255];
}
function blend(hex, a) {
  var c = hexToRgb(hex);
  return 'rgb(' + Math.round((1-a+c[0]*a)*255) + ',' +
                  Math.round((1-a+c[1]*a)*255) + ',' +
                  Math.round((1-a+c[2]*a)*255) + ')';
}

/* ── method subtitle ───────────────────────────────────────────────────── */
svg.append('text')
  .attr('x', margin.left + matW / 2).attr('y', margin.top - 12)
  .attr('text-anchor','middle').attr('font-family', FONT).attr('font-size', 9).attr('fill','#aaa')
  .text(n + ' items  ·  UPGMA leaf order  ·  ' + method);

/* ── similarity matrix ─────────────────────────────────────────────────── */
var cellData = [];
for (var i = 0; i < n; i++) for (var j = 0; j < n; j++) cellData.push({i: i, j: j});

var tip = d3.select('#emd-tip');

matG.selectAll('.emd-cell').data(cellData).join('rect')
  .attr('class','emd-cell')
  .attr('x', function (d) { return d.j * cellSize + gap / 2; })
  .attr('y', function (d) { return d.i * cellSize + gap / 2; })
  .attr('width', inner).attr('height', inner).attr('rx', rad)
  .attr('fill', function (d) {
    if (d.i === d.j) return NAVY;
    return d.i < d.j ? blend(RED, link[d.i][d.j]) : blend(MUSTARD, text[d.i][d.j]);
  })
  .style('cursor', function (d) { return d.i === d.j ? 'default' : 'pointer'; })
  .on('mouseover', function (event, d) {
    if (d.i === d.j) return;
    var li = Math.min(d.i, d.j), lj = Math.max(d.i, d.j);
    tip.style('opacity', 1).html(
      '<div class="emd-tip-head">' + meta[d.i].label + ' ↔ ' + meta[d.j].label + '</div>' +
      '<span class="emd-tip-link">▲ Link</span>&nbsp;' + (link[li][lj]*100).toFixed(1) + '%<br>' +
      '<span class="emd-tip-text">▼ Content</span>&nbsp;' + (text[lj][li]*100).toFixed(1) + '%'
    );
    d3.select(this).attr('stroke', NAVY).attr('stroke-width', 2);
    matG.selectAll('.emd-cell').filter(function (e) { return e.i !== d.i && e.j !== d.j; })
      .attr('opacity', function (e) { return (itemVisible(e.i) && itemVisible(e.j)) ? 0.35 : 0.04; });
  })
  .on('mousemove', function (ev) {
    tip.style('left', (ev.clientX + 14) + 'px').style('top', (ev.clientY - 10) + 'px');
  })
  .on('mouseout', function () {
    tip.style('opacity', 0); d3.select(this).attr('stroke', 'none'); applyFilter();
  });

var maxDiagFs = Math.max(9, Math.round(cellSize * 0.18));
function diagText(label) {
  for (var fs = maxDiagFs; fs >= 6; fs--) {
    var mc = Math.floor(inner / (0.58 * fs));
    if (label.length <= mc) return {fs: fs, t: label};
  }
  var mc2 = Math.floor(inner / (0.58 * 6));
  return {fs: 6, t: label.slice(0, Math.max(1, mc2 - 1)) + '…'};
}

matG.selectAll('.emd-val').data(cellData.filter(function (d) { return d.i !== d.j; })).join('text')
  .attr('class','emd-val')
  .attr('x', function (d) { return d.j * cellSize + cellSize / 2; })
  .attr('y', function (d) { return d.i * cellSize + cellSize / 2; })
  .attr('dy','0.35em').attr('text-anchor','middle')
  .attr('font-family', FONT).attr('font-size', Math.max(8, Math.round(cellSize * 0.16)))
  .attr('font-weight', 600).attr('pointer-events','none')
  .attr('fill', function (d) {
    var v = d.i < d.j ? link[d.i][d.j] : text[d.i][d.j];
    if (v < 0.08) return 'none';
    var c = hexToRgb(d.i < d.j ? RED : MUSTARD);
    return (0.299*(1-v+c[0]*v) + 0.587*(1-v+c[1]*v) + 0.114*(1-v+c[2]*v)) < 0.55 ? WHITE : NAVY;
  })
  .text(function (d) {
    var v = d.i < d.j ? link[d.i][d.j] : text[d.i][d.j];
    return v >= 0.08 ? Math.round(v * 100) + '%' : '';
  });

matG.selectAll('.emd-diag').data(meta).join('text')
  .attr('class','emd-diag')
  .attr('x', function (d, i) { return i * cellSize + cellSize / 2; })
  .attr('y', function (d, i) { return i * cellSize + cellSize / 2; })
  .attr('dy','0.35em').attr('text-anchor','middle')
  .attr('font-family', FONT).attr('font-size', function (d) { return diagText(d.label).fs; })
  .attr('font-weight', 700).attr('fill', WHITE).attr('pointer-events','none')
  .text(function (d) { return diagText(d.label).t; });

var pivotY = matW + 4;
matG.selectAll('.emd-xlabel').data(meta).join('text')
  .attr('class','emd-xlabel')
  .attr('transform', function (d, i) {
    return 'translate(' + (i * cellSize + cellSize / 2) + ',' + pivotY + ') rotate(-90)';
  })
  .attr('text-anchor','end').attr('dy','0.35em')
  .attr('font-family', FONT).attr('font-size', lblFs).attr('font-weight', 600).attr('fill', NAVY)
  .text(function (d) { return d.label.length > 50 ? d.label.slice(0,50) + '…' : d.label; });

matG.selectAll('.emd-ylabel').data(meta).join('text')
  .attr('class','emd-ylabel').attr('x', -6)
  .attr('y', function (d, i) { return i * cellSize + cellSize / 2; })
  .attr('text-anchor','end').attr('dominant-baseline','middle')
  .attr('font-family', FONT).attr('font-size', lblFs).attr('font-weight', 600).attr('fill', NAVY)
  .text(function (d) { return d.label.length > 50 ? d.label.slice(0,50) + '…' : d.label; });

matG.append('line')
  .attr('x1',0).attr('y1',0).attr('x2',matW).attr('y2',matW)
  .attr('stroke', NAVY).attr('stroke-width', 1.5).attr('stroke-dasharray','5,4').attr('opacity',0.22);

/* ── legend ────────────────────────────────────────────────────────────── */
var legY  = matW + XLBL_H + 16;
var barW  = Math.floor(matW * 0.43);
var barH  = 13;
var legFs = Math.max(9, Math.round(cellSize * 0.16));

matG.append('text').attr('x',0).attr('y',legY-8)
  .attr('font-family',FONT).attr('font-size',legFs).attr('font-weight',700).attr('fill',RED)
  .text('▲  link similarity');
matG.append('rect').attr('x',0).attr('y',legY).attr('width',barW).attr('height',barH)
  .attr('rx',3).attr('fill','url(#emd-leg-red)');
matG.append('text').attr('x',0).attr('y',legY+barH+9)
  .attr('font-size',legFs-1).attr('fill','#bbb').attr('font-family',FONT).text('0%');
matG.append('text').attr('x',barW).attr('y',legY+barH+9).attr('text-anchor','end')
  .attr('font-size',legFs-1).attr('fill','#bbb').attr('font-family',FONT).text('100%');

var mustX = matW - barW;
matG.append('text').attr('x',mustX).attr('y',legY-8)
  .attr('font-family',FONT).attr('font-size',legFs).attr('font-weight',700).attr('fill','#c49000')
  .text('▼  content similarity');
matG.append('rect').attr('x',mustX).attr('y',legY).attr('width',barW).attr('height',barH)
  .attr('rx',3).attr('fill','url(#emd-leg-mustard)');
matG.append('text').attr('x',mustX).attr('y',legY+barH+9)
  .attr('font-size',legFs-1).attr('fill','#bbb').attr('font-family',FONT).text('0%');
matG.append('text').attr('x',mustX+barW).attr('y',legY+barH+9).attr('text-anchor','end')
  .attr('font-size',legFs-1).attr('fill','#bbb').attr('font-family',FONT).text('100%');

/* ── dendrogram (orthogonal, spectral-ordered leaves) ──────────────────── */
(function () {
  var root = d3.hierarchy(tree);

  /* max merge distance for x-scaling */
  var maxDist = 0;
  root.each(function (d) { if (d.data.value > maxDist) maxDist = d.data.value; });
  if (maxDist < 1e-9) maxDist = 1;

  /* 1. y-positions: each leaf pins to its spectral_index matrix row */
  function assignY(node) {
    if (!node.children) {
      node.dendY = (node.data.spectral_index || 0) * cellSize + cellSize / 2;
    } else {
      node.children.forEach(assignY);
      node.dendY = d3.mean(node.children, function (c) { return c.dendY; });
    }
  }
  assignY(root);

  /* 2. x-positions for RIGHT-SIDE dendrogram:
        Leaf x = 2  (touching matrix right edge = left edge of dendG)
        Root x = DEND_W-2  (rightmost — furthest from matrix)
        Internal nodes: scaled by merge distance — larger distance → further right */
  function assignX(node) {
    if (!node.children) {
      node.dendX = 2;
    } else {
      /* distance 0 → x=2 (at matrix), distance=maxDist → x=DEND_W-2 (far right) */
      node.dendX = node.data.value / maxDist * (DEND_W - 4) + 2;
      node.children.forEach(assignX);
    }
  }
  assignX(root);

  /* 3. Collect parent→child pairs */
  var links = [];
  root.each(function (d) {
    if (d.children) d.children.forEach(function (c) { links.push({src: d, tgt: c}); });
  });

  /* 4. Orthogonal elbow paths: M px,py V cy H cx
        Parent (further right) → vertical to child's y → horizontal left to child. */
  dendG.selectAll('.emd-dend-branch')
    .data(links).join('path')
    .attr('class','emd-dend-branch')
    .attr('fill','none')
    .attr('stroke', NAVY).attr('stroke-width', 1.1).attr('opacity', 0.55)
    .attr('d', function (d) {
      return 'M ' + d.src.dendX + ',' + d.src.dendY +
             ' V ' + d.tgt.dendY +
             ' H ' + d.tgt.dendX;
    });

  /* 5. Dashed connector: matrix right edge → leaf left-edge
        (small tick showing which row the leaf belongs to) */
  root.leaves().forEach(function (d) {
    dendG.append('line')
      .attr('x1', 0).attr('y1', d.dendY)
      .attr('x2', d.dendX).attr('y2', d.dendY)
      .attr('stroke', NAVY).attr('stroke-width', 0.5)
      .attr('stroke-dasharray','1,3').attr('opacity', 0.18);
  });

  /* No leaf labels — rows are already labelled by the matrix y-axis */

  /* 6. Internal node dots */
  root.each(function (d) {
    if (!d.children) return;
    dendG.append('circle')
      .attr('cx', d.dendX).attr('cy', d.dendY).attr('r', 1.8)
      .attr('fill', WHITE).attr('stroke', NAVY).attr('stroke-width', 1).attr('opacity', 0.65);
  });
}());

/* ── key schema radial graph ───────────────────────────────────────────── */
(function () {
  var w  = Math.min(window.innerWidth - 48, 720);
  var h  = Math.max(360, Math.round(w * 0.6));
  var cx = w / 2, cy = h / 2;
  var R  = Math.min(cx, cy) - 90;

  var root = d3.hierarchy(EMD_SCHEMA).sum(function () { return 1; });

  var treeLayout = d3.tree()
    .size([2 * Math.PI, R])
    .separation(function (a, b) { return (a.parent === b.parent ? 1 : 1.5) / a.depth; });
  treeLayout(root);

  var svg2 = d3.select('#emd-key-graph').append('svg').attr('width', w).attr('height', h);
  var g2   = svg2.append('g').attr('transform', 'translate(' + cx + ',' + cy + ')');

  /* Radial curved links */
  g2.selectAll('.emd-klink')
    .data(root.links()).join('path')
    .attr('class','emd-klink')
    .attr('fill','none').attr('stroke', NAVY).attr('stroke-width', 1.1).attr('opacity', 0.3)
    .attr('d', d3.linkRadial().angle(function (d) { return d.x; }).radius(function (d) { return d.y; }));

  var typeColor = { scalar: NAVY, link: RED, links: RED, list: MUSTARD };

  var knode = g2.selectAll('.emd-knode')
    .data(root.descendants()).join('g')
    .attr('class','emd-knode')
    .attr('transform', function (d) {
      return 'rotate(' + (d.x * 180 / Math.PI - 90) + ') translate(' + d.y + ',0)';
    });

  knode.append('circle')
    .attr('r', function (d) { return d.depth === 0 ? 6 : (d.depth === 1 ? 4 : 3); })
    .attr('fill', function (d) { return d.depth === 0 ? NAVY : (typeColor[d.data.type] || NAVY); })
    .attr('stroke', WHITE).attr('stroke-width', 1);

  knode.append('text')
    .attr('dy','0.31em')
    .attr('x', function (d) { return d.x < Math.PI === !d.children ? 8 : -8; })
    .attr('text-anchor', function (d) { return d.x < Math.PI === !d.children ? 'start' : 'end'; })
    .attr('transform', function (d) { return d.x >= Math.PI ? 'rotate(180)' : null; })
    .attr('font-family', FONT)
    .attr('font-size', function (d) { return d.depth === 0 ? 11 : (d.depth === 1 ? 9 : 8); })
    .attr('font-weight', function (d) { return d.depth <= 1 ? 600 : 400; })
    .attr('fill', function (d) { return d.depth === 0 ? NAVY : (typeColor[d.data.type] || '#555'); })
    .text(function (d) { return d.data.name; });

  /* Legend */
  var legItems = [
    {label: 'Scalar field',       col: NAVY},
    {label: 'Linked record',      col: RED},
    {label: 'List / multi-value', col: MUSTARD},
  ];
  var legG = svg2.append('g').attr('transform', 'translate(12,' + (h - 58) + ')');
  legItems.forEach(function (item, idx) {
    legG.append('circle').attr('cx',6).attr('cy', idx*17+6).attr('r',4).attr('fill', item.col);
    legG.append('text').attr('x',16).attr('y', idx*17+10)
      .attr('font-family',FONT).attr('font-size',9).attr('fill','#666').text(item.label);
  });
}());

}());
</script>
