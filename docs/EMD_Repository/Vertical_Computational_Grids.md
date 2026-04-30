# Vertical Computational Grids

**Stage 2b.** Vertical grids are registered separately from horizontal grids because they vary independently of the horizontal layout. Each record captures coordinate type, level count, and vertical extent, and receives a `v###` ID used in Stage 3.

---

!!! info "Generated files"
    This page is auto-generated during the build from live registry data. Three files are produced for each record type:

    - **`Vertical_Computational_Grids.md`** — this page, embedded in the MkDocs site layout
    - **`Vertical_Computational_Grids_data.json`** — processed similarity matrices, dendrogram tree, and key schema
    - **`Vertical_Computational_Grids_raw.json`** — raw JSON-LD records as fetched from the cmipld registry (depth 2)

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
<span class="emd-section-label">View a specific Vertical Grid</span>
<div class="emd-selector-row">
  <select id="emd-entry-select">
    <option value="">Select an entry…</option>
    <option value="../Vertical_Computational_Grids/v105/">v105</option>
    <option value="../Vertical_Computational_Grids/v108/">v108</option>
    <option value="../Vertical_Computational_Grids/v107/">v107</option>
    <option value="../Vertical_Computational_Grids/v101/">v101</option>
    <option value="../Vertical_Computational_Grids/v102/">v102</option>
    <option value="../Vertical_Computational_Grids/v106/">v106</option>
    <option value="../Vertical_Computational_Grids/v110/">v110</option>
    <option value="../Vertical_Computational_Grids/v100/">v100</option>
    <option value="../Vertical_Computational_Grids/v104/">v104</option>
    <option value="../Vertical_Computational_Grids/v103/">v103</option>
    <option value="../Vertical_Computational_Grids/v109/">v109</option>
  </select>
  <button id="emd-go-btn" onclick="emdGotoEntry()">Open →</button>
  <button class="emd-font-btn" id="emd-font-toggle" onclick="emdToggleFont()">✨ Pretty font</button>
</div>
<div class="emd-stats">
  <span><b>11</b> registered entries</span>
  <span>Endpoint: <b>vertical_computational_grid</b></span>
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
var EMD_DATA    = {"ids":["v105","v108","v107","v101","v102","v106","v110","v100","v104","v103","v109"],"link":[[0.0,0.3657142857142857,0.32515698587127156,0.2299765807962529,0.03205574912891986,0.007653061224489796,0.028571428571428574,0.0162748643761302,0.06373626373626375,0.05201465201465201,0.0],[0.3657142857142857,0.0,0.3317307692307692,0.17142857142857143,0.0642857142857143,0.008928571428571428,0.0,0.0642857142857143,0.028571428571428574,0.047619047619047616,0.028571428571428574],[0.32515698587127156,0.3317307692307692,0.0,0.17857142857142858,0.23724489795918366,0.026785714285714284,0.07397959183673468,0.1096938775510204,0.07653061224489796,0.047619047619047616,0.10714285714285714],[0.2299765807962529,0.17142857142857143,0.17857142857142858,0.0,0.00273224043715847,0.0,0.038056206088992975,0.002185792349726776,0.035519125683060114,0.13943533697632057,0.0],[0.03205574912891986,0.0642857142857143,0.23724489795918366,0.00273224043715847,0.0,0.06547619047619048,0.07054060989114874,0.2981029810298103,0.20624724270498518,0.02032520325203252,0.078125],[0.007653061224489796,0.008928571428571428,0.026785714285714284,0.0,0.06547619047619048,0.0,0.16476328903654486,0.19608843537414966,0.16029900332225913,0.0,0.0],[0.028571428571428574,0.0,0.07397959183673468,0.038056206088992975,0.07054060989114874,0.16476328903654486,0.0,0.2104185065253655,0.4195767195767196,0.010582010582010581,0.10625],[0.0162748643761302,0.0642857142857143,0.1096938775510204,0.002185792349726776,0.2981029810298103,0.19608843537414966,0.2104185065253655,0.0,0.25517531809112615,0.016877637130801686,0.125],[0.06373626373626375,0.028571428571428574,0.07653061224489796,0.035519125683060114,0.20624724270498518,0.16029900332225913,0.4195767195767196,0.25517531809112615,0.0,0.030864197530864196,0.025],[0.05201465201465201,0.047619047619047616,0.047619047619047616,0.13943533697632057,0.02032520325203252,0.0,0.010582010582010581,0.016877637130801686,0.030864197530864196,0.0,0.0],[0.0,0.028571428571428574,0.10714285714285714,0.0,0.078125,0.0,0.10625,0.125,0.025,0.0,0.0]],"text":[[0.0,0.2060920261180281,0.2060920261180281,0.19760730253973047,0.06628396064960454,0.06618504411799693,0.0661579181205903,0.032022907903928644,0.0,0.0,0.0],[0.2060920261180281,0.0,0.3244730568385177,0.12267914219261603,0.02211472079248486,0.10420230217766806,0.10415959477426137,0.0,0.0,0.0,0.0],[0.2060920261180281,0.3244730568385177,0.0,0.06779855050952814,0.12845167617307765,0.10420230217766807,0.1041595947742614,0.0,0.0,0.0,0.0],[0.19760730253973047,0.12267914219261603,0.06779855050952814,0.0,0.062094648873080575,0.0,0.19585771510577066,0.049803214381210124,0.0,0.0,0.0],[0.06628396064960454,0.02211472079248486,0.12845167617307765,0.062094648873080575,0.0,0.04829704299329367,0.014349628900205755,0.025689568389021325,0.0,0.03403564357388283,0.0],[0.06618504411799693,0.10420230217766806,0.10420230217766807,0.0,0.04829704299329367,0.0,0.0915379640729323,0.12400192126130626,0.05667657725661642,0.16428789813106265,0.07156434318618692],[0.0661579181205903,0.10415959477426137,0.1041595947742614,0.19585771510577066,0.014349628900205755,0.0915379640729323,0.0,0.026127187510391177,0.21642351937313928,0.03461543721659834,0.03263815195259083],[0.032022907903928644,0.0,0.0,0.049803214381210124,0.025689568389021325,0.12400192126130626,0.026127187510391177,0.0,0.11567199976638062,0.1879586981758526,0.03934570254166284],[0.0,0.0,0.0,0.0,0.0,0.05667657725661642,0.21642351937313928,0.11567199976638062,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.03403564357388283,0.16428789813106265,0.03461543721659834,0.1879586981758526,0.0,0.0,0.05212840821585593],[0.0,0.0,0.0,0.0,0.0,0.07156434318618692,0.03263815195259083,0.03934570254166284,0.0,0.05212840821585593,0.0]],"method":"embedding (all-MiniLM-L6-v2) | link: field-level (links uninformative) | order: spectral graph components","folder":"Vertical Computational Grids","meta":[{"label":"v105","tags":[]},{"label":"v108","tags":[]},{"label":"v107","tags":[]},{"label":"v101","tags":[]},{"label":"v102","tags":[]},{"label":"v106","tags":[]},{"label":"v110","tags":[]},{"label":"v100","tags":[]},{"label":"v104","tags":[]},{"label":"v103","tags":[]},{"label":"v109","tags":[]}],"tree":{"name":"","leaf":false,"children":[{"name":"v109","leaf":true,"spectral_index":10,"value":0.0},{"name":"","leaf":false,"children":[{"name":"v103","leaf":true,"spectral_index":9,"value":0.0},{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"v101","leaf":true,"spectral_index":3,"value":0.0},{"name":"","leaf":false,"children":[{"name":"v105","leaf":true,"spectral_index":0,"value":0.0},{"name":"","leaf":false,"children":[{"name":"v108","leaf":true,"spectral_index":1,"value":0.0},{"name":"v107","leaf":true,"spectral_index":2,"value":0.0}],"value":0.6718980869653566}],"value":0.7242361690445966}],"value":0.8386564039936454},{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"v102","leaf":true,"spectral_index":4,"value":0.0},{"name":"v100","leaf":true,"spectral_index":7,"value":0.0}],"value":0.8381037252905842},{"name":"","leaf":false,"children":[{"name":"v106","leaf":true,"spectral_index":5,"value":0.0},{"name":"","leaf":false,"children":[{"name":"v110","leaf":true,"spectral_index":6,"value":0.0},{"name":"v104","leaf":true,"spectral_index":8,"value":0.0}],"value":0.6819998805250705}],"value":0.8816807915779119}],"value":0.8889671597087881}],"value":0.9494303386483314}],"value":0.9563202883432125}],"value":0.9667117054194708},"clusters":[0,0,0,0,0,0,0,0,0,1,2]};
var EMD_ENTRIES = [{"label":"v105","url":"../Vertical_Computational_Grids/v105/"},{"label":"v108","url":"../Vertical_Computational_Grids/v108/"},{"label":"v107","url":"../Vertical_Computational_Grids/v107/"},{"label":"v101","url":"../Vertical_Computational_Grids/v101/"},{"label":"v102","url":"../Vertical_Computational_Grids/v102/"},{"label":"v106","url":"../Vertical_Computational_Grids/v106/"},{"label":"v110","url":"../Vertical_Computational_Grids/v110/"},{"label":"v100","url":"../Vertical_Computational_Grids/v100/"},{"label":"v104","url":"../Vertical_Computational_Grids/v104/"},{"label":"v103","url":"../Vertical_Computational_Grids/v103/"},{"label":"v109","url":"../Vertical_Computational_Grids/v109/"}];
var EMD_SCHEMA  = {"name":"record","children":[{"name":"bottom_layer_thickness","type":"scalar"},{"name":"description","type":"scalar"},{"name":"n_z","type":"scalar"},{"name":"top_layer_thickness","type":"scalar"},{"name":"total_thickness","type":"scalar"},{"name":"ui_label","type":"scalar"},{"name":"validation_key","type":"scalar"},{"name":"vertical_coordinate","type":"scalar"}]};

var ids      = EMD_DATA.ids;
var link     = EMD_DATA.link;
var text     = EMD_DATA.text;
var method   = EMD_DATA.method;
var meta     = EMD_DATA.meta;
var tree     = EMD_DATA.tree;
var clusters = EMD_DATA.clusters || ids.map(function() { return 0; });
var n        = ids.length;

/* Cluster colour palette — 20 distinct monotone colours */
var CLUSTER_COLORS = [
  '#1565c0','#b71c1c','#1b5e20','#4a148c','#e65100',
  '#006064','#3e2723','#37474f','#880e4f','#33691e',
  '#0d47a1','#bf360c','#1a237e','#01579b','#004d40',
  '#f57f17','#4e342e','#263238','#6a1b9a','#827717'
];
function clusterColor(k) {
  return CLUSTER_COLORS[k % CLUSTER_COLORS.length];
}

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
var DEND_W   = Math.max(30, Math.round(n * cellSize * 0.09));  /* compact right-side dendrogram */
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

/* Show cluster boxes only while the mouse is over the matrix */
d3.select('#emd-combined-chart')
  .on('mouseenter.cluster', function () {
    matG.selectAll('.emd-cluster-box').attr('opacity', 0.8);
  })
  .on('mouseleave.cluster', function () {
    matG.selectAll('.emd-cluster-box').attr('opacity', 0);
  });

/* ── cluster background fills (drawn before cells so they sit behind) ──── */
(function () {
  var runs = [];
  var start = 0;
  for (var i = 1; i <= n; i++) {
    if (i === n || clusters[i] !== clusters[start]) {
      runs.push({ k: clusters[start], start: start, end: i - 1 });
      start = i;
    }
  }
  var clusterSize = {};
  clusters.forEach(function (c) { clusterSize[c] = (clusterSize[c] || 0) + 1; });

  runs.forEach(function (r) {
    if (clusterSize[r.k] < 2) return;
    var x  = r.start * cellSize;
    var sz = (r.end - r.start + 1) * cellSize;
    matG.append('rect')
      .attr('class', 'emd-cluster-box')
      .attr('x', x).attr('y', x)
      .attr('width', sz).attr('height', sz)
      .attr('fill', 'none')
      .attr('stroke', clusterColor(r.k))
      .attr('stroke-width', 2)
      .attr('rx', rad + 1)
      .attr('pointer-events', 'none')
      .attr('opacity', 0);
  });
}());

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
      '<span class="emd-tip-link">▲ Link similarity</span>&nbsp;' + (link[li][lj]*100).toFixed(1) + '%<br>' +
      '<span class="emd-tip-text">▼ Embeddings</span>&nbsp;' + (text[lj][li]*100).toFixed(1) + '%'
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

/* ── cluster legend ────────────────────────────────────────────────────── */
(function () {
  var clusterSize = {};
  clusters.forEach(function (c) { clusterSize[c] = (clusterSize[c] || 0) + 1; });
  var shownClusters = Object.keys(clusterSize)
    .map(Number)
    .filter(function (k) { return clusterSize[k] >= 2; })
    .sort(function (a, b) { return a - b; });
  var legY2 = matW + XLBL_H + LEG_H + 28;
  var legFs2 = Math.max(9, Math.round(cellSize * 0.14));
  var dot = legFs2 + 2;
  var lx = 0;
  shownClusters.forEach(function (k, idx) {
    matG.append('rect')
      .attr('x', lx).attr('y', legY2)
      .attr('width', dot).attr('height', dot)
      .attr('rx', 2)
      .attr('fill', clusterColor(k));
    matG.append('text')
      .attr('x', lx + dot + 4).attr('y', legY2 + dot - 2)
      .attr('font-family', FONT).attr('font-size', legFs2)
      .attr('fill', NAVY)
      .text('Group ' + (idx + 1));
    lx += dot + 70;
  });
}());

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

/* ── upper / lower triangle corner labels ──────────────────────────────── */
/* These make explicit that the two triangles show different metrics. */
var triFs = Math.max(8, Math.round(cellSize * 0.13));
var pad   = Math.max(6, Math.round(cellSize * 0.18));
/* Upper-right: link / field-level label (from method string) */
var upperLabel = (method.indexOf('field-level') >= 0 && method.indexOf('jaccard') < 0)
  ? 'field similarity' : 'link similarity';
matG.append('text')
  .attr('x', matW - pad).attr('y', pad + triFs)
  .attr('text-anchor','end').attr('font-family', FONT)
  .attr('font-size', triFs).attr('font-weight', 700).attr('fill', RED).attr('opacity', 0.75)
  .text(upperLabel);
/* Lower-left: text / embedding label */
matG.append('text')
  .attr('x', pad).attr('y', matW - pad)
  .attr('text-anchor','start').attr('font-family', FONT)
  .attr('font-size', triFs).attr('font-weight', 700).attr('fill', MUSTARD).attr('opacity', 0.75)
  .text('embeddings');

/* ── legend ────────────────────────────────────────────────────────────── */
var legY  = matW + XLBL_H + 16;
var barW  = Math.floor(matW * 0.43);
var barH  = 13;
var legFs = Math.max(9, Math.round(cellSize * 0.16));

matG.append('text').attr('x',0).attr('y',legY-8)
  .attr('font-family',FONT).attr('font-size',legFs).attr('font-weight',700).attr('fill',RED)
  .text('▲  link similarity (upper)');
matG.append('rect').attr('x',0).attr('y',legY).attr('width',barW).attr('height',barH)
  .attr('rx',3).attr('fill','url(#emd-leg-red)');
matG.append('text').attr('x',0).attr('y',legY+barH+9)
  .attr('font-size',legFs-1).attr('fill','#bbb').attr('font-family',FONT).text('0%');
matG.append('text').attr('x',barW).attr('y',legY+barH+9).attr('text-anchor','end')
  .attr('font-size',legFs-1).attr('fill','#bbb').attr('font-family',FONT).text('100%');

var mustX = matW - barW;
matG.append('text').attr('x',mustX).attr('y',legY-8)
  .attr('font-family',FONT).attr('font-size',legFs).attr('font-weight',700).attr('fill','#c49000')
  .text('▼  embeddings (lower)');
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

  /* 1. y-positions: distribute leaves uniformly in DFS order so all
        vertical bars have equal height, then propagate means upward.
        Dashed connectors (step 5) bridge each leaf to its matrix row. */
  var orderedLeaves = [];
  (function collectLeaves(node) {
    if (!node.children) { orderedLeaves.push(node); }
    else node.children.forEach(collectLeaves);
  }(root));

  var step = matW / orderedLeaves.length;
  orderedLeaves.forEach(function (leaf, i) {
    leaf.dendY = step * i + step / 2;
  });

  /* propagate means bottom-up (leaves already set) */
  function assignYMean(node) {
    if (!node.children) return;
    node.children.forEach(assignYMean);
    node.dendY = d3.mean(node.children, function (c) { return c.dendY; });
  }
  assignYMean(root);

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

  /* Annotate each node with the majority cluster of its leaf subtree.
     Used to colour branches: a branch is the cluster colour when all
     leaves below share the same cluster AND that cluster is not a singleton.
     Grey when mixed or all singletons. */
  var clusterSizeD = {};
  clusters.forEach(function (c) { clusterSizeD[c] = (clusterSizeD[c] || 0) + 1; });

  root.each(function (d) {
    var leaves = d.leaves();
    var clusterSet = {};
    leaves.forEach(function (l) {
      var ci = clusters[l.data.spectral_index || 0];
      clusterSet[ci] = (clusterSet[ci] || 0) + 1;
    });
    var keys = Object.keys(clusterSet);
    var singleCluster = (keys.length === 1) ? parseInt(keys[0]) : -1;
    /* Only assign a clique colour if the cluster has more than 1 item total */
    d._clique = (singleCluster >= 0 && clusterSizeD[singleCluster] >= 2)
      ? singleCluster : -1;
  });

  /* 4. Orthogonal elbow paths: M px,py V cy H cx
        Parent (further right) → vertical to child’s y → horizontal left to child.
        Coloured by cluster when the entire subtree belongs to one cluster. */
  dendG.selectAll('.emd-dend-branch')
    .data(links).join('path')
    .attr('class','emd-dend-branch')
    .attr('fill','none')
    .attr('stroke', function (d) {
      var k = d.tgt._clique;
      return k >= 0 ? clusterColor(k) : '#888';
    })
    .attr('stroke-width', function (d) { return d.tgt._clique >= 0 ? 1.8 : 0.9; })
    .attr('opacity', function (d) { return d.tgt._clique >= 0 ? 0.6 : 0.25; })
    .attr('d', function (d) {
      return 'M ' + d.src.dendX + ',' + d.src.dendY +
             ' V ' + d.tgt.dendY +
             ' H ' + d.tgt.dendX;
    });

  /* 5. Dashed connector: matrix row → dendrogram leaf position.
        Uses an elbow: vertical from matY to dendY, then horizontal to leaf. */
  root.leaves().forEach(function (d) {
    var matY = (d.data.spectral_index || 0) * cellSize + cellSize / 2;
    if (Math.abs(matY - d.dendY) < 0.5) {
      /* already aligned — simple horizontal tick */
      dendG.append('line')
        .attr('x1', 0).attr('y1', d.dendY)
        .attr('x2', d.dendX).attr('y2', d.dendY)
        .attr('stroke', NAVY).attr('stroke-width', 0.5)
        .attr('stroke-dasharray','1,3').attr('opacity', 0.18);
    } else {
      /* elbow: V at x=0 from matY to dendY, then H to leaf */
      dendG.append('path')
        .attr('fill', 'none')
        .attr('stroke', NAVY).attr('stroke-width', 0.5)
        .attr('stroke-dasharray','1,3').attr('opacity', 0.18)
        .attr('d', 'M 0,' + matY + ' V ' + d.dendY + ' H ' + d.dendX);
    }
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
