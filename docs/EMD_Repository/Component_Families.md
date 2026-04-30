# Component Families

**Optional.** Component families capture scientific lineage by grouping versions of a single-domain code base (e.g. NEMO, ARPEGE-Climat, SURFEX). A family ID can be referenced by model components at Stage 3.

---

!!! info "Generated files"
    This page is auto-generated during the build from live registry data. Three files are produced for each record type:

    - **`Component_Families.md`** — this page, embedded in the MkDocs site layout
    - **`Component_Families_data.json`** — processed similarity matrices, dendrogram tree, and key schema
    - **`Component_Families_raw.json`** — raw JSON-LD records as fetched from the cmipld registry (depth 2)

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
<span class="emd-section-label">View a specific Component Family</span>
<div class="emd-selector-row">
  <select id="emd-entry-select">
    <option value="">Select an entry…</option>
    <option value="../Component_Families/nemo/">nemo</option>
    <option value="../Component_Families/pisces/">pisces</option>
    <option value="../Component_Families/hadam/">hadam</option>
    <option value="../Component_Families/tactic/">tactic</option>
    <option value="../Component_Families/surfex/">surfex</option>
    <option value="../Component_Families/gelato/">gelato</option>
    <option value="../Component_Families/arpege-climat/">arpege-climat</option>
    <option value="../Component_Families/reprobus/">reprobus</option>
    <option value="../Component_Families/NICAM/">NICAM</option>
    <option value="../Component_Families/CAM/">CAM</option>
    <option value="../Component_Families/IFS/">IFS</option>
    <option value="../Component_Families/GEOS/">GEOS</option>
    <option value="../Component_Families/CLM/">CLM</option>
    <option value="../Component_Families/BISICLES/">BISICLES</option>
  </select>
  <button id="emd-go-btn" onclick="emdGotoEntry()">Open →</button>
  <button class="emd-font-btn" id="emd-font-toggle" onclick="emdToggleFont()">✨ Pretty font</button>
</div>
<div class="emd-stats">
  <span><b>14</b> registered entries</span>
  <span>Endpoint: <b>model_family</b></span>
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
var EMD_DATA    = {"ids":["nemo","pisces","hadam","tactic","surfex","gelato","arpege-climat","reprobus","NICAM","CAM","IFS","GEOS","CLM","BISICLES"],"link":[[0.0,0.8483152325257588,0.780952380952381,0.7807017543859649,0.7817460317460317,0.7806026365348399,0.7793650793650794,0.7831541218637993,0.778816199376947,0.7823232323232323,0.7777777777777778,0.7875118708452041,0.07998957790515894,0.0735015208987239],[0.8483152325257588,0.0,0.8272445820433437,0.8247678018575851,0.8278637770897833,0.8253869969040248,0.8260061919504644,0.8530738611233968,0.8262781748213304,0.8256684491978609,0.826625386996904,0.8325421396628827,0.053673788431474724,0.06796478301440916],[0.780952380952381,0.8272445820433437,0.0,0.8445378151260504,0.8394957983193277,0.826890756302521,0.9168067226890756,0.8495798319327731,0.8873007146783948,0.8834224598930481,0.8861236802413273,0.8853695324283559,0.053152683689421575,0.0611122556564102],[0.7807017543859649,0.8247678018575851,0.8445378151260504,0.0,0.8857142857142857,0.8937473294402506,0.9025210084033614,0.8907563025210083,0.843375481033535,0.8433155080213903,0.8441930618401207,0.8411764705882353,0.053673788431474724,0.056370202503726506],[0.7817460317460317,0.8278637770897833,0.8394957983193277,0.8857142857142857,0.0,0.8848739495798319,0.9092436974789916,0.8859943977591036,0.8268279274326553,0.8245989304812834,0.8265460030165912,0.8250377073906485,0.1068264721208963,0.07725781758102372],[0.7806026365348399,0.8253869969040248,0.826890756302521,0.8937473294402506,0.8848739495798319,0.0,0.8840336134453781,0.8851992409867173,0.8246289169873556,0.8251336898395722,0.8265460030165912,0.8250377073906485,0.06096925482021886,0.05480688827756705],[0.7793650793650794,0.8260061919504644,0.9168067226890756,0.9025210084033614,0.9092436974789916,0.8840336134453781,0.0,0.9084033613445378,0.8867509620670698,0.8834224598930481,0.8846153846153846,0.8846153846153846,0.053673788431474724,0.0611122556564102],[0.7831541218637993,0.8530738611233968,0.8495798319327731,0.8907563025210083,0.8859943977591036,0.8851992409867173,0.9084033613445378,0.0,0.8498390010209691,0.8503437738731856,0.8494936436112906,0.852510234863176,0.058264473063847744,0.05835536342583376],[0.778816199376947,0.8262781748213304,0.8873007146783948,0.843375481033535,0.8268279274326553,0.8246289169873556,0.8867509620670698,0.8498390010209691,0.0,0.8850267379679144,0.8929553129663081,0.8921874045568383,0.05558288243974422,0.06244180326931217],[0.7823232323232323,0.8256684491978609,0.8834224598930481,0.8433155080213903,0.8245989304812834,0.8251336898395722,0.8834224598930481,0.8503437738731856,0.8850267379679144,0.0,0.8957219251336898,0.8920974450386215,0.11148325358851674,0.06089907644375209],[0.7777777777777778,0.826625386996904,0.8861236802413273,0.8441930618401207,0.8265460030165912,0.8265460030165912,0.8846153846153846,0.8494936436112906,0.8929553129663081,0.8957219251336898,0.0,0.8936651583710408,0.06472120896300156,0.0611122556564102],[0.7875118708452041,0.8325421396628827,0.8853695324283559,0.8411764705882353,0.8250377073906485,0.8250377073906485,0.8846153846153846,0.852510234863176,0.8921874045568383,0.8920974450386215,0.8936651583710408,0.0,0.06004284638990215,0.06059115091435705],[0.07998957790515894,0.053673788431474724,0.053152683689421575,0.053673788431474724,0.1068264721208963,0.06096925482021886,0.053673788431474724,0.058264473063847744,0.05558288243974422,0.11148325358851674,0.06472120896300156,0.06004284638990215,0.0,0.2551727331928142],[0.0735015208987239,0.06796478301440916,0.0611122556564102,0.056370202503726506,0.07725781758102372,0.05480688827756705,0.0611122556564102,0.05835536342583376,0.06244180326931217,0.06089907644375209,0.0611122556564102,0.06059115091435705,0.2551727331928142,0.0]],"text":[[0.0,0.7967787408236354,0.773966176323649,0.7354895626438687,0.7807930626756651,0.7723659016295318,0.8001305734236492,0.7755912658463101,0.7113307908143771,0.7432804319703468,0.7093745223068926,0.7136235471678958,0.026279873536632137,0.007277255528198298],[0.7967787408236354,0.0,0.7212589566331432,0.7346662570383116,0.7344585269368029,0.7486161178792743,0.7755270422741524,0.751742304099584,0.6990235795662276,0.6974290175326378,0.7184990869896243,0.7012766660332298,0.01547204874570669,0.0071513474582293075],[0.773966176323649,0.7212589566331432,0.0,0.763433693436621,0.7866452492471361,0.8144923072657761,0.8662819668730102,0.8288037204514818,0.7583071666524637,0.7766125519509621,0.7394029552808644,0.7541001924468331,0.01732356955116481,0.0018222520625550758],[0.7354895626438687,0.7346662570383116,0.763433693436621,0.0,0.7950502225664272,0.8032232834487539,0.832097203536091,0.8304315339531632,0.7297730028924112,0.7111746974434301,0.7270474473717142,0.731402329851797,0.002003115476529123,0.0018168835966710349],[0.7807930626756651,0.7344585269368029,0.7866452492471361,0.7950502225664272,0.0,0.8470221469943544,0.8774705305364356,0.8311008130492479,0.751961133873888,0.7327973634060415,0.7491527110659723,0.753640000070454,0.08638948366903404,0.0018721243093898802],[0.7723659016295318,0.7486161178792743,0.8144923072657761,0.8032232834487539,0.8470221469943544,0.0,0.9077380552707203,0.8602400264866924,0.7662981147727678,0.746893347580931,0.7568539487285911,0.7613873667513278,0.01798064810973072,0.01477001971906881],[0.8001305734236492,0.7755270422741524,0.8662819668730102,0.832097203536091,0.8774705305364356,0.9077380552707203,0.0,0.9028945791785888,0.8153627908953794,0.81649202087583,0.7950362097541256,0.8108392791638794,0.01862700954881364,0.0019593598460934092],[0.7755912658463101,0.751742304099584,0.8288037204514818,0.8304315339531632,0.8311008130492479,0.8602400264866924,0.9028945791785888,0.0,0.7799272316073343,0.7707316298883345,0.7600145357488187,0.7752692149128211,0.01805573446308378,0.0018992678887065106],[0.7113307908143771,0.6990235795662276,0.7583071666524637,0.7297730028924112,0.751961133873888,0.7662981147727678,0.8153627908953794,0.7799272316073343,0.0,0.7488539239099357,0.7206408824187462,0.7347729954744475,0.015470794519035137,0.0071507677411622875],[0.7432804319703468,0.6974290175326378,0.7766125519509621,0.7111746974434301,0.7327973634060415,0.746893347580931,0.81649202087583,0.7707316298883345,0.7488539239099357,0.0,0.7286557861983356,0.7525207895730002,0.053538032851235345,0.008833459290074503],[0.7093745223068926,0.7184990869896243,0.7394029552808644,0.7270474473717142,0.7491527110659723,0.7568539487285911,0.7950362097541256,0.7600145357488187,0.7206408824187462,0.7286557861983356,0.0,0.7788605170898559,0.012519309018235156,0.0017769009828172107],[0.7136235471678958,0.7012766660332298,0.7541001924468331,0.731402329851797,0.753640000070454,0.7613873667513278,0.8108392791638794,0.7752692149128211,0.7347729954744475,0.7525207895730002,0.7788605170898559,0.0,0.012594297410950575,0.0017875442977575023],[0.026279873536632137,0.01547204874570669,0.01732356955116481,0.002003115476529123,0.08638948366903404,0.01798064810973072,0.01862700954881364,0.01805573446308378,0.015470794519035137,0.053538032851235345,0.012519309018235156,0.012594297410950575,0.0,0.0784047505730247],[0.007277255528198298,0.0071513474582293075,0.0018222520625550758,0.0018168835966710349,0.0018721243093898802,0.01477001971906881,0.0019593598460934092,0.0018992678887065106,0.0071507677411622875,0.008833459290074503,0.0017769009828172107,0.0017875442977575023,0.0784047505730247,0.0]],"method":"embedding (all-MiniLM-L6-v2) | link: field-level (links uninformative) | order: UPGMA + dendrogram cut","folder":"Component Families","meta":[{"label":"nemo","tags":["ocean"]},{"label":"pisces","tags":["ocean-biogeochemistry"]},{"label":"hadam","tags":["atmosphere"]},{"label":"tactic","tags":["aerosol"]},{"label":"surfex","tags":["land-surface"]},{"label":"gelato","tags":["sea-ice"]},{"label":"arpege-climat","tags":["atmosphere"]},{"label":"reprobus","tags":["atmospheric-chemistry"]},{"label":"NICAM","tags":["atmosphere"]},{"label":"CAM","tags":["atmosphere"]},{"label":"IFS","tags":["atmosphere"]},{"label":"GEOS","tags":["atmosphere"]},{"label":"CLM","tags":["land-surface"]},{"label":"BISICLES","tags":["land-ice"]}],"tree":{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"nemo","leaf":true,"spectral_index":0,"value":0.0},{"name":"pisces","leaf":true,"spectral_index":1,"value":0.0}],"value":0.17745301332530294},{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"hadam","leaf":true,"spectral_index":2,"value":0.0},{"name":"","leaf":false,"children":[{"name":"tactic","leaf":true,"spectral_index":3,"value":0.0},{"name":"","leaf":false,"children":[{"name":"surfex","leaf":true,"spectral_index":4,"value":0.0},{"name":"","leaf":false,"children":[{"name":"gelato","leaf":true,"spectral_index":5,"value":0.0},{"name":"","leaf":false,"children":[{"name":"arpege-climat","leaf":true,"spectral_index":6,"value":0.0},{"name":"reprobus","leaf":true,"spectral_index":7,"value":0.0}],"value":0.09435102973843668}],"value":0.11569726595262297}],"value":0.12738241076700582}],"value":0.14580735380208232}],"value":0.1663032138356227},{"name":"","leaf":false,"children":[{"name":"NICAM","leaf":true,"spectral_index":8,"value":0.0},{"name":"","leaf":false,"children":[{"name":"CAM","leaf":true,"spectral_index":9,"value":0.0},{"name":"","leaf":false,"children":[{"name":"IFS","leaf":true,"spectral_index":10,"value":0.0},{"name":"GEOS","leaf":true,"spectral_index":11,"value":0.0}],"value":0.1637371622695516}],"value":0.1827510135140883}],"value":0.18759379045096827}],"value":0.19311037746195345}],"value":0.22732870408489983},{"name":"","leaf":false,"children":[{"name":"CLM","leaf":true,"spectral_index":12,"value":0.0},{"name":"BISICLES","leaf":true,"spectral_index":13,"value":0.0}],"value":0.8332112581170805}],"value":0.9599593647667929},"clusters":[0,0,0,0,0,0,0,0,0,0,0,0,1,2]};
var EMD_ENTRIES = [{"label":"nemo","url":"../Component_Families/nemo/"},{"label":"pisces","url":"../Component_Families/pisces/"},{"label":"hadam","url":"../Component_Families/hadam/"},{"label":"tactic","url":"../Component_Families/tactic/"},{"label":"surfex","url":"../Component_Families/surfex/"},{"label":"gelato","url":"../Component_Families/gelato/"},{"label":"arpege-climat","url":"../Component_Families/arpege-climat/"},{"label":"reprobus","url":"../Component_Families/reprobus/"},{"label":"NICAM","url":"../Component_Families/NICAM/"},{"label":"CAM","url":"../Component_Families/CAM/"},{"label":"IFS","url":"../Component_Families/IFS/"},{"label":"GEOS","url":"../Component_Families/GEOS/"},{"label":"CLM","url":"../Component_Families/CLM/"},{"label":"BISICLES","url":"../Component_Families/BISICLES/"}];
var EMD_SCHEMA  = {"name":"record","children":[{"name":"collaborative_institutions","type":"scalar"},{"name":"common_scientific_basis","type":"scalar"},{"name":"computational_requirements","type":"scalar"},{"name":"description","type":"scalar"},{"name":"documentation","type":"scalar"},{"name":"established","type":"scalar"},{"name":"evolution","type":"scalar"},{"name":"family_type","type":"scalar"},{"name":"license","type":"scalar"},{"name":"primary_institution","type":"scalar"},{"name":"programming_languages","type":"scalar"},{"name":"references","type":"scalar"},{"name":"representative_member","type":"scalar"},{"name":"scientific_domains","type":"scalar"},{"name":"shared_code_base","type":"scalar"},{"name":"software_dependencies","type":"scalar"},{"name":"source_code_repository","type":"scalar"},{"name":"ui_label","type":"scalar"},{"name":"validation_key","type":"scalar"},{"name":"variation_dimensions","type":"scalar"},{"name":"website","type":"scalar"}]};

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
      .attr('x', x).attr('y', x)
      .attr('width', sz).attr('height', sz)
      .attr('fill', 'none')
      .attr('stroke', clusterColor(r.k))
      .attr('stroke-width', 2)
      .attr('rx', rad + 1)
      .attr('pointer-events', 'none')
      .attr('opacity', 0.5);
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
    .attr('opacity', function (d) { return d.tgt._clique >= 0 ? 0.8 : 0.35; })
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
