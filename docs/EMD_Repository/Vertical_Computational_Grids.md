# Vertical Computational Grids

**Stage 2b.** Vertical grids are registered separately from horizontal grids because they vary independently of the horizontal layout. Each record captures coordinate type, level count, and vertical extent, and receives a `v###` ID used in Stage 3.

---

<link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;600;700&display=swap" rel="stylesheet">

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
/* ── accessible font toggle ── */
.emd-font-btn {
  padding: 5px 12px; border-radius: 20px; border: 1.5px solid #ccc;
  background: #fff; font-size: 11px; cursor: pointer;
  font-family: 'Source Code Pro', monospace; color: #888;
  transition: all .2s; white-space: nowrap;
}
.emd-font-btn:hover { border-color: #2065a0; color: #1a4a80; }
.emd-font-btn.active { background: #e8f0ff; border-color: #2065a0;
  color: #1a4a80; font-family: inherit; font-weight: 600; }
/* Accessible mode: also switch the UI controls (the SVGs are already on the
   accessible/sans-serif font by default via the JS `FONT` constant). */
.emd-viz.accessible { font-family: inherit; }
.emd-viz.accessible #emd-entry-select,
.emd-viz.accessible .emd-stats,
.emd-viz.accessible .emd-stats-grid,
.emd-viz.accessible .emd-stat-label,
.emd-viz.accessible .emd-stat-value,
.emd-viz.accessible .emd-section-label,
.emd-viz.accessible .emd-fbtn,
.emd-viz.accessible #emd-go-btn { font-family: inherit !important; }
/* ── stats grid ── */
.emd-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin: 10px 0 18px;
  padding: 14px 16px;
  background: #f7f8fa;
  border-left: 3px solid #0d1035;
  border-radius: 4px;
}
.emd-stat-item { display: flex; flex-direction: column; gap: 3px; }
.emd-stat-label {
  font-family: 'Source Code Pro', monospace;
  color: #888; font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.06em;
}
.emd-stat-value {
  font-family: 'Source Code Pro', monospace;
  color: #0d1035; font-weight: 600; font-size: 13px;
}
</style>

<div class="emd-viz">

<!-- Status / stats box pinned to the top of the page -->
<div class="emd-stats-grid">
  <div class="emd-stat-item">
    <span class="emd-stat-label">Total Records</span>
    <span class="emd-stat-value">30</span>
  </div>
  <div class="emd-stat-item">
    <span class="emd-stat-label">Endpoint</span>
    <span class="emd-stat-value">vertical_computational_grid</span>
  </div>
  <div class="emd-stat-item">
    <span class="emd-stat-label">Raw Data</span>
    <span class="emd-stat-value">13.8 KB</span>
  </div>
  <div class="emd-stat-item">
    <span class="emd-stat-label">Processed Data</span>
    <span class="emd-stat-value">37.9 KB</span>
  </div>
  <div class="emd-stat-item">
    <span class="emd-stat-label">Last Updated</span>
    <span class="emd-stat-value">2026-06-01 22:23 UTC</span>
  </div>
</div>

<div class="emd-section">
<span class="emd-section-label">View a specific Vertical Grid</span>
<div class="emd-selector-row">
  <select id="emd-entry-select">
    <option value="">Select an entry…</option>
    <option value="../view_vertical_computational_grids/?id=v119">v119</option>
    <option value="../view_vertical_computational_grids/?id=v101">v101</option>
    <option value="../view_vertical_computational_grids/?id=v105">v105</option>
    <option value="../view_vertical_computational_grids/?id=v122">v122</option>
    <option value="../view_vertical_computational_grids/?id=v125">v125</option>
    <option value="../view_vertical_computational_grids/?id=v123">v123</option>
    <option value="../view_vertical_computational_grids/?id=v117">v117</option>
    <option value="../view_vertical_computational_grids/?id=v112">v112</option>
    <option value="../view_vertical_computational_grids/?id=v108">v108</option>
    <option value="../view_vertical_computational_grids/?id=v107">v107</option>
    <option value="../view_vertical_computational_grids/?id=v121">v121</option>
    <option value="../view_vertical_computational_grids/?id=v116">v116</option>
    <option value="../view_vertical_computational_grids/?id=tempgrid_JamesAnstey-1777265640">tempgrid_JamesAnstey-1777265640</option>
    <option value="../view_vertical_computational_grids/?id=tempgrid_JamesAnstey-1777265640">tempgrid_JamesAnstey-1777265640</option>
    <option value="../view_vertical_computational_grids/?id=v111">v111</option>
    <option value="../view_vertical_computational_grids/?id=v114">v114</option>
    <option value="../view_vertical_computational_grids/?id=v113">v113</option>
    <option value="../view_vertical_computational_grids/?id=v110">v110</option>
    <option value="../view_vertical_computational_grids/?id=v104">v104</option>
    <option value="../view_vertical_computational_grids/?id=v115">v115</option>
    <option value="../view_vertical_computational_grids/?id=v118">v118</option>
    <option value="../view_vertical_computational_grids/?id=v106">v106</option>
    <option value="../view_vertical_computational_grids/?id=v100">v100</option>
    <option value="../view_vertical_computational_grids/?id=v103">v103</option>
    <option value="../view_vertical_computational_grids/?id=no-vertical">no-vertical</option>
    <option value="../view_vertical_computational_grids/?id=v124">v124</option>
    <option value="../view_vertical_computational_grids/?id=v102">v102</option>
    <option value="../view_vertical_computational_grids/?id=tempgrid-jamesanstey-1779329743">tempgrid-jamesanstey-1779329743</option>
    <option value="../view_vertical_computational_grids/?id=v109">v109</option>
    <option value="../view_vertical_computational_grids/?id=v120">v120</option>
  </select>
  <button id="emd-go-btn" onclick="emdGotoEntry()">Open →</button>
  <button class="emd-font-btn" id="emd-font-toggle" onclick="emdToggleFont()" title="Switch to the page's default font for improved readability">Accessible font</button>
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
var EMD_DATA    = {"ids":["v119","v101","v105","v122","v125","v123","v117","v112","v108","v107","v121","v116","tempgrid_JamesAnstey-1777265640","tempgrid_JamesAnstey-1777265640","v111","v114","v113","v110","v104","v115","v118","v106","v100","v103","no-vertical","v124","v102","tempgrid-jamesanstey-1779329743","v109","v120"],"link":[[0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,0.0,1.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,0.0,1.0,1.0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,0.0,1.0],[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,0.0]],"text":[[0.0,0.21475409836065573,0.47130434782608693,0.38,0.3801198801198801,0.4245069998494656,0.4228571428571429,0.456959706959707,0.38,0.24862637362637363,0.23076923076923078,0.23076923076923078,0.2783882783882784,0.2783882783882784,0.0,0.0,0.0024975024975024975,0.006211180124223602,0.004140786749482402,0.022959183673469385,0.002551020408163265,0.07908163265306123,0.007233273056057866,0.049689440993788817,0.0027472527472527475,0.20233628160457426,0.005226480836236933,0.0,0.03645833333333333,0.004638218923933209],[0.21475409836065573,0.0,0.2299765807962529,0.2857142857142857,0.2861826697892272,0.2875878220140515,0.21428571428571427,0.3333333333333333,0.17142857142857143,0.17857142857142858,0.14285714285714285,0.17857142857142858,0.17857142857142858,0.17857142857142858,0.0,0.03571428571428571,0.09035909445745512,0.038056206088992975,0.035519125683060114,0.03571428571428571,0.0,0.0,0.002185792349726776,0.13943533697632057,0.07377049180327869,0.053239656518345044,0.00273224043715847,0.0,0.020833333333333332,0.003278688524590164],[0.47130434782608693,0.2299765807962529,0.0,0.3657142857142857,0.29440559440559444,0.324311305133223,0.3657142857142857,0.3641025641025641,0.3657142857142857,0.32515698587127156,0.25934065934065936,0.25934065934065936,0.2879120879120879,0.2879120879120879,0.0,0.05714285714285715,0.03206793206793207,0.028571428571428574,0.06373626373626375,0.03112244897959184,0.002551020408163265,0.007653061224489796,0.0162748643761302,0.05201465201465201,0.006868131868131869,0.06296345930492273,0.03205574912891986,0.0,0.020833333333333332,0.0055658627087198514],[0.38,0.2857142857142857,0.3657142857142857,0.0,0.35934065934065934,0.3021978021978022,0.41,0.3525641025641026,0.4266666666666667,0.3108974358974359,0.2692307692307692,0.2692307692307692,0.3108974358974359,0.3108974358974359,0.0,0.041666666666666664,0.0642857142857143,0.0642857142857143,0.028571428571428574,0.15178571428571427,0.1529761904761905,0.008928571428571428,0.09999999999999999,0.047619047619047616,0.0,0.05860805860805861,0.0,0.0,0.023809523809523808,0.0],[0.3801198801198801,0.2861826697892272,0.29440559440559444,0.35934065934065934,0.0,0.5247002997002997,0.37362637362637363,0.4945054945054945,0.25934065934065936,0.33084772370486654,0.29853479853479853,0.27472527472527475,0.35805860805860806,0.35805860805860806,0.028571428571428574,0.08571428571428573,0.13633033633033634,0.08896103896103898,0.030194805194805194,0.02040816326530612,0.05714285714285715,0.03112244897959184,0.058766233766233765,0.19534632034632035,0.08104395604395605,0.1121459840972036,0.05616883116883117,0.0,0.05208333333333333,0.0074211502782931356],[0.4245069998494656,0.2875878220140515,0.324311305133223,0.3021978021978022,0.5247002997002997,0.0,0.4450549450549451,0.4175824175824176,0.25934065934065936,0.3512558869701727,0.3032967032967033,0.39377289377289376,0.36996336996337,0.36996336996337,0.0,0.07142857142857142,0.07242757242757243,0.08121330724070451,0.1487279843444227,0.0,0.0,0.0739795918367347,0.06208559373116335,0.1268754076973255,0.0,0.10866166353971231,0.10394889663182345,0.0,0.05208333333333333,0.03942486085343228],[0.4228571428571429,0.21428571428571427,0.3657142857142857,0.41,0.37362637362637363,0.4450549450549451,0.0,0.4358974358974359,0.5333333333333333,0.31387362637362637,0.30256410256410254,0.3247863247863248,0.47008547008547,0.47008547008547,0.08333333333333333,0.08333333333333333,0.0,0.0,0.07142857142857142,0.002976190476190476,0.002976190476190476,0.03273809523809524,0.0,0.047619047619047616,0.0,0.05860805860805861,0.047619047619047616,0.0,0.023809523809523808,0.0],[0.456959706959707,0.3333333333333333,0.3641025641025641,0.3525641025641026,0.4945054945054945,0.4175824175824176,0.4358974358974359,0.0,0.38589743589743586,0.4310897435897436,0.34829059829059833,0.3621794871794872,0.5074786324786325,0.5074786324786325,0.0,0.0,0.047619047619047616,0.0,0.017857142857142856,0.08333333333333333,0.08333333333333333,0.002976190476190476,0.07142857142857142,0.11904761904761904,0.07142857142857142,0.10256410256410256,0.07142857142857142,0.0,0.023809523809523808,0.07142857142857142],[0.38,0.17142857142857143,0.3657142857142857,0.4266666666666667,0.25934065934065936,0.25934065934065936,0.5333333333333333,0.38589743589743586,0.0,0.3317307692307692,0.30256410256410254,0.3108974358974359,0.433974358974359,0.433974358974359,0.08333333333333333,0.08333333333333333,0.0,0.0,0.028571428571428574,0.002976190476190476,0.002976190476190476,0.008928571428571428,0.0642857142857143,0.047619047619047616,0.0,0.05860805860805861,0.0642857142857143,0.0,0.05238095238095238,0.0],[0.24862637362637363,0.17857142857142858,0.32515698587127156,0.3108974358974359,0.33084772370486654,0.3512558869701727,0.31387362637362637,0.4310897435897436,0.3317307692307692,0.0,0.47870879120879123,0.36515567765567764,0.4548992673992674,0.4548992673992674,0.041666666666666664,0.06547619047619048,0.07397959183673468,0.07397959183673468,0.07653061224489796,0.10416666666666667,0.125,0.026785714285714284,0.1096938775510204,0.047619047619047616,0.0,0.10256410256410256,0.23724489795918366,0.0,0.13095238095238096,0.17857142857142858],[0.23076923076923078,0.14285714285714285,0.25934065934065936,0.2692307692307692,0.29853479853479853,0.3032967032967033,0.30256410256410254,0.34829059829059833,0.30256410256410254,0.47870879120879123,0.0,0.44273504273504277,0.47051282051282056,0.47051282051282056,0.027777777777777776,0.027777777777777776,0.023809523809523808,0.023809523809523808,0.0642857142857143,0.0,0.027777777777777776,0.026785714285714284,0.028571428571428574,0.047619047619047616,0.0,0.10256410256410256,0.18214285714285713,0.0,0.06547619047619047,0.2380952380952381],[0.23076923076923078,0.17857142857142858,0.25934065934065936,0.2692307692307692,0.27472527472527475,0.39377289377289376,0.3247863247863248,0.3621794871794872,0.3108974358974359,0.36515567765567764,0.44273504273504277,0.0,0.5705128205128206,0.5705128205128206,0.03333333333333333,0.0,0.0642857142857143,0.028571428571428574,0.06547619047619048,0.041666666666666664,0.05714285714285714,0.002976190476190476,0.047619047619047616,0.047619047619047616,0.0,0.10256410256410256,0.09523809523809523,0.0,0.09523809523809523,0.07142857142857142],[0.2783882783882784,0.17857142857142858,0.2879120879120879,0.3108974358974359,0.35805860805860806,0.36996336996337,0.47008547008547,0.5074786324786325,0.433974358974359,0.4548992673992674,0.47051282051282056,0.5705128205128206,0.0,1.0,0.11666666666666665,0.15833333333333333,0.028571428571428574,0.028571428571428574,0.06547619047619048,0.11666666666666665,0.11666666666666665,0.002976190476190476,0.11904761904761904,0.047619047619047616,0.0,0.10256410256410256,0.1845238095238095,0.0,0.05952380952380952,0.10714285714285714],[0.2783882783882784,0.17857142857142858,0.2879120879120879,0.3108974358974359,0.35805860805860806,0.36996336996337,0.47008547008547,0.5074786324786325,0.433974358974359,0.4548992673992674,0.47051282051282056,0.5705128205128206,1.0,0.0,0.11666666666666665,0.15833333333333333,0.028571428571428574,0.028571428571428574,0.06547619047619048,0.11666666666666665,0.11666666666666665,0.002976190476190476,0.11904761904761904,0.047619047619047616,0.0,0.10256410256410256,0.1845238095238095,0.0,0.05952380952380952,0.10714285714285714],[0.0,0.0,0.0,0.0,0.028571428571428574,0.0,0.08333333333333333,0.0,0.08333333333333333,0.041666666666666664,0.027777777777777776,0.03333333333333333,0.11666666666666665,0.11666666666666665,0.0,0.5666666666666667,0.4043956043956044,0.42410714285714285,0.14285714285714285,0.18851744186046512,0.2551841085271318,0.11664244186046513,0.07765780730897011,0.0,0.0,0.003125,0.021179401993355478,0.0,0.08571428571428572,0.07314680232558139],[0.0,0.03571428571428571,0.05714285714285715,0.041666666666666664,0.08571428571428573,0.07142857142857142,0.08333333333333333,0.0,0.08333333333333333,0.06547619047619048,0.027777777777777776,0.0,0.15833333333333333,0.15833333333333333,0.5666666666666667,0.0,0.46153846153846156,0.48125,0.2714285714285714,0.28018410852713177,0.1551841085271318,0.19997577519379847,0.1252768549280177,0.0,0.0,0.002232142857142857,0.0687984496124031,0.0,0.028571428571428574,0.005554401993355482],[0.0024975024975024975,0.09035909445745512,0.03206793206793207,0.0642857142857143,0.13633033633033634,0.07242757242757243,0.0,0.047619047619047616,0.0,0.07397959183673468,0.023809523809523808,0.0642857142857143,0.028571428571428574,0.028571428571428574,0.4043956043956044,0.46153846153846156,0.0,0.6196803196803197,0.27342657342657345,0.26804242269358547,0.2670220145303202,0.17078967544083823,0.1773914070425698,0.048618048618048616,0.05261405261405261,0.006193806193806194,0.0717954526094061,0.0,0.075,0.06715842297237647],[0.006211180124223602,0.038056206088992975,0.028571428571428574,0.0642857142857143,0.08896103896103898,0.08121330724070451,0.0,0.0,0.0,0.07397959183673468,0.023809523809523808,0.028571428571428574,0.028571428571428574,0.028571428571428574,0.42410714285714285,0.48125,0.6196803196803197,0.0,0.4195767195767196,0.23301495016611296,0.24730066445182725,0.17140780730897012,0.2104185065253655,0.010582010582010581,0.005494505494505495,0.011814024390243903,0.07054060989114874,0.0,0.10625,0.06548019049057255],[0.004140786749482402,0.035519125683060114,0.06373626373626375,0.028571428571428574,0.030194805194805194,0.1487279843444227,0.07142857142857142,0.017857142857142856,0.028571428571428574,0.07653061224489796,0.0642857142857143,0.06547619047619048,0.06547619047619048,0.06547619047619048,0.14285714285714285,0.2714285714285714,0.27342657342657345,0.4195767195767196,0.0,0.11694352159468438,0.059800664451827246,0.1669435215946844,0.25517531809112615,0.030864197530864196,0.009615384615384614,0.0017421602787456446,0.20624724270498518,0.0,0.025,0.005177546705785909],[0.022959183673469385,0.03571428571428571,0.03112244897959184,0.15178571428571427,0.02040816326530612,0.0,0.002976190476190476,0.08333333333333333,0.002976190476190476,0.10416666666666667,0.0,0.041666666666666664,0.11666666666666665,0.11666666666666665,0.18851744186046512,0.28018410852713177,0.26804242269358547,0.23301495016611296,0.11694352159468438,0.0,0.6142857142857142,0.3422619047619048,0.30357142857142855,0.0,0.0,0.002551020408163265,0.07142857142857142,0.0,0.017857142857142856,0.07142857142857142],[0.002551020408163265,0.0,0.002551020408163265,0.1529761904761905,0.05714285714285715,0.0,0.002976190476190476,0.08333333333333333,0.002976190476190476,0.125,0.027777777777777776,0.05714285714285714,0.11666666666666665,0.11666666666666665,0.2551841085271318,0.1551841085271318,0.2670220145303202,0.24730066445182725,0.059800664451827246,0.6142857142857142,0.0,0.31845238095238093,0.3321428571428572,0.0,0.0,0.002551020408163265,0.08928571428571429,0.0,0.05714285714285715,0.15714285714285717],[0.07908163265306123,0.0,0.007653061224489796,0.008928571428571428,0.03112244897959184,0.0739795918367347,0.03273809523809524,0.002976190476190476,0.008928571428571428,0.026785714285714284,0.026785714285714284,0.002976190476190476,0.002976190476190476,0.002976190476190476,0.11664244186046513,0.19997577519379847,0.17078967544083823,0.17140780730897012,0.1669435215946844,0.3422619047619048,0.31845238095238093,0.0,0.20833333333333331,0.0,0.0,0.0739795918367347,0.06547619047619048,0.0,0.0,0.002551020408163265],[0.007233273056057866,0.002185792349726776,0.0162748643761302,0.09999999999999999,0.058766233766233765,0.06208559373116335,0.0,0.07142857142857142,0.0642857142857143,0.1096938775510204,0.028571428571428574,0.047619047619047616,0.11904761904761904,0.11904761904761904,0.07765780730897011,0.1252768549280177,0.1773914070425698,0.2104185065253655,0.25517531809112615,0.30357142857142855,0.3321428571428572,0.20833333333333331,0.0,0.016877637130801686,0.005494505494505495,0.004355400696864111,0.2981029810298103,0.0,0.125,0.07328385899814471],[0.049689440993788817,0.13943533697632057,0.05201465201465201,0.047619047619047616,0.19534632034632035,0.1268754076973255,0.047619047619047616,0.11904761904761904,0.047619047619047616,0.047619047619047616,0.047619047619047616,0.047619047619047616,0.047619047619047616,0.047619047619047616,0.0,0.0,0.048618048618048616,0.010582010582010581,0.030864197530864196,0.0,0.0,0.0,0.016877637130801686,0.0,0.13701923076923078,0.2576219512195122,0.02032520325203252,0.0,0.0,0.0032467532467532465],[0.0027472527472527475,0.07377049180327869,0.006868131868131869,0.0,0.08104395604395605,0.0,0.0,0.07142857142857142,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.05261405261405261,0.005494505494505495,0.009615384615384614,0.0,0.0,0.0,0.005494505494505495,0.13701923076923078,0.0,0.01876172607879925,0.008241758241758242,0.0,0.005681818181818182,0.020394420394420396],[0.20233628160457426,0.053239656518345044,0.06296345930492273,0.05860805860805861,0.1121459840972036,0.10866166353971231,0.05860805860805861,0.10256410256410256,0.05860805860805861,0.10256410256410256,0.10256410256410256,0.10256410256410256,0.10256410256410256,0.10256410256410256,0.003125,0.002232142857142857,0.006193806193806194,0.011814024390243903,0.0017421602787456446,0.002551020408163265,0.002551020408163265,0.0739795918367347,0.004355400696864111,0.2576219512195122,0.01876172607879925,0.0,0.003484320557491289,0.0,0.004807692307692308,0.009146341463414634],[0.005226480836236933,0.00273224043715847,0.03205574912891986,0.0,0.05616883116883117,0.10394889663182345,0.047619047619047616,0.07142857142857142,0.0642857142857143,0.23724489795918366,0.18214285714285713,0.09523809523809523,0.1845238095238095,0.1845238095238095,0.021179401993355478,0.0687984496124031,0.0717954526094061,0.07054060989114874,0.20624724270498518,0.07142857142857142,0.08928571428571429,0.06547619047619048,0.2981029810298103,0.02032520325203252,0.008241758241758242,0.003484320557491289,0.0,0.0,0.078125,0.3063543599257885],[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],[0.03645833333333333,0.020833333333333332,0.020833333333333332,0.023809523809523808,0.05208333333333333,0.05208333333333333,0.023809523809523808,0.023809523809523808,0.05238095238095238,0.13095238095238096,0.06547619047619047,0.09523809523809523,0.05952380952380952,0.05952380952380952,0.08571428571428572,0.028571428571428574,0.075,0.10625,0.025,0.017857142857142856,0.05714285714285715,0.0,0.125,0.0,0.005681818181818182,0.004807692307692308,0.078125,0.0,0.0,0.09375],[0.004638218923933209,0.003278688524590164,0.0055658627087198514,0.0,0.0074211502782931356,0.03942486085343228,0.0,0.07142857142857142,0.0,0.17857142857142858,0.2380952380952381,0.07142857142857142,0.10714285714285714,0.10714285714285714,0.07314680232558139,0.005554401993355482,0.06715842297237647,0.06548019049057255,0.005177546705785909,0.07142857142857142,0.15714285714285717,0.002551020408163265,0.07328385899814471,0.0032467532467532465,0.020394420394420396,0.009146341463414634,0.3063543599257885,0.0,0.09375,0.0]],"method":"field-level | link: jaccard | order: spectral graph components","folder":"Vertical Computational Grids","meta":[{"label":"v119","tags":[]},{"label":"v101","tags":[]},{"label":"v105","tags":[]},{"label":"v122","tags":[]},{"label":"v125","tags":[]},{"label":"v123","tags":[]},{"label":"v117","tags":[]},{"label":"v112","tags":[]},{"label":"v108","tags":[]},{"label":"v107","tags":[]},{"label":"v121","tags":[]},{"label":"v116","tags":[]},{"label":"tempgrid_JamesAnstey-1777265640","tags":[]},{"label":"tempgrid_JamesAnstey-1777265640","tags":[]},{"label":"v111","tags":[]},{"label":"v114","tags":[]},{"label":"v113","tags":[]},{"label":"v110","tags":[]},{"label":"v104","tags":[]},{"label":"v115","tags":[]},{"label":"v118","tags":[]},{"label":"v106","tags":[]},{"label":"v100","tags":[]},{"label":"v103","tags":[]},{"label":"no-vertical","tags":[]},{"label":"v124","tags":[]},{"label":"v102","tags":[]},{"label":"tempgrid-jamesanstey-1779329743","tags":[]},{"label":"v109","tags":[]},{"label":"v120","tags":[]}],"tree":{"name":"","leaf":false,"children":[{"name":"tempgrid-jamesanstey-1779329743","leaf":true,"spectral_index":7,"value":0.0},{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"v111","leaf":true,"spectral_index":1,"value":0.0},{"name":"v115","leaf":true,"spectral_index":2,"value":0.0}],"value":0.4064281719843745},{"name":"","leaf":false,"children":[{"name":"v109","leaf":true,"spectral_index":8,"value":0.0},{"name":"","leaf":false,"children":[{"name":"v102","leaf":true,"spectral_index":6,"value":0.0},{"name":"v120","leaf":true,"spectral_index":9,"value":0.0}],"value":0.34682282003710574}],"value":0.45703125}],"value":0.46230851763196307},{"name":"","leaf":false,"children":[{"name":"no-vertical","leaf":true,"spectral_index":4,"value":0.0},{"name":"","leaf":false,"children":[{"name":"v119","leaf":true,"spectral_index":0,"value":0.0},{"name":"","leaf":false,"children":[{"name":"v103","leaf":true,"spectral_index":3,"value":0.0},{"name":"v124","leaf":true,"spectral_index":5,"value":0.0}],"value":0.3711890243902439}],"value":0.457251482244608}],"value":0.4712286690504332}],"value":0.4891652564657949}],"value":1.0},"clusters":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,2,2,2,2,3,4,5,6,7,8,9],"group_spans":[[0,13],[14,18],[19,22],[23,23],[24,24],[25,25],[26,26],[27,27],[28,28],[29,29]]};
var EMD_ENTRIES = [{"label":"v119","url":"../view_vertical_computational_grids/?id=v119"},{"label":"v101","url":"../view_vertical_computational_grids/?id=v101"},{"label":"v105","url":"../view_vertical_computational_grids/?id=v105"},{"label":"v122","url":"../view_vertical_computational_grids/?id=v122"},{"label":"v125","url":"../view_vertical_computational_grids/?id=v125"},{"label":"v123","url":"../view_vertical_computational_grids/?id=v123"},{"label":"v117","url":"../view_vertical_computational_grids/?id=v117"},{"label":"v112","url":"../view_vertical_computational_grids/?id=v112"},{"label":"v108","url":"../view_vertical_computational_grids/?id=v108"},{"label":"v107","url":"../view_vertical_computational_grids/?id=v107"},{"label":"v121","url":"../view_vertical_computational_grids/?id=v121"},{"label":"v116","url":"../view_vertical_computational_grids/?id=v116"},{"label":"tempgrid_JamesAnstey-1777265640","url":"../view_vertical_computational_grids/?id=tempgrid_JamesAnstey-1777265640"},{"label":"tempgrid_JamesAnstey-1777265640","url":"../view_vertical_computational_grids/?id=tempgrid_JamesAnstey-1777265640"},{"label":"v111","url":"../view_vertical_computational_grids/?id=v111"},{"label":"v114","url":"../view_vertical_computational_grids/?id=v114"},{"label":"v113","url":"../view_vertical_computational_grids/?id=v113"},{"label":"v110","url":"../view_vertical_computational_grids/?id=v110"},{"label":"v104","url":"../view_vertical_computational_grids/?id=v104"},{"label":"v115","url":"../view_vertical_computational_grids/?id=v115"},{"label":"v118","url":"../view_vertical_computational_grids/?id=v118"},{"label":"v106","url":"../view_vertical_computational_grids/?id=v106"},{"label":"v100","url":"../view_vertical_computational_grids/?id=v100"},{"label":"v103","url":"../view_vertical_computational_grids/?id=v103"},{"label":"no-vertical","url":"../view_vertical_computational_grids/?id=no-vertical"},{"label":"v124","url":"../view_vertical_computational_grids/?id=v124"},{"label":"v102","url":"../view_vertical_computational_grids/?id=v102"},{"label":"tempgrid-jamesanstey-1779329743","url":"../view_vertical_computational_grids/?id=tempgrid-jamesanstey-1779329743"},{"label":"v109","url":"../view_vertical_computational_grids/?id=v109"},{"label":"v120","url":"../view_vertical_computational_grids/?id=v120"}];
var EMD_SCHEMA  = {"name":"","children":[{"name":"bottom_layer_thickness","type":"scalar"},{"name":"description","type":"scalar"},{"name":"n_z","type":"scalar"},{"name":"n_z_range","type":"scalar"},{"name":"top_layer_thickness","type":"scalar"},{"name":"total_thickness","type":"scalar"},{"name":"ui_label","type":"scalar"},{"name":"validation_key","type":"scalar"},{"name":"vertical_coordinate","type":"scalar"}]};

var ids         = EMD_DATA.ids;
var link        = EMD_DATA.link;
var text        = EMD_DATA.text;
var method      = EMD_DATA.method;
var meta        = EMD_DATA.meta;
var tree        = EMD_DATA.tree;
var clusters    = EMD_DATA.clusters || ids.map(function() { return 0; });
var group_spans = EMD_DATA.group_spans || [];  /* [[start_row, end_row], ...] per group */
var n           = ids.length;

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

var FONT    = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
var FONT_MONO = "'Source Code Pro', monospace";
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

/* ── accessible font toggle ──────────────────────────────────────────── */
window.emdToggleFont = function () {
  var viz = document.querySelector('.emd-viz');
  var btn = document.getElementById('emd-font-toggle');
  viz.classList.toggle('accessible');
  btn.classList.toggle('active');
};

/* ── layout constants ──────────────────────────────────────────────────── */
/* Matrix grows to occupy up to 3/4 of the available container/SVG width. */
var containerEl = document.querySelector('.emd-viz');
var containerW  = (containerEl && containerEl.clientWidth) || window.innerWidth * 0.85;
var availMatW   = containerW * 0.75;
var cellSize    = Math.min(80, Math.floor(availMatW / n));
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

  /* 1. y-positions: each leaf represents a GROUP, not an individual item.
        Pin each leaf to the vertical centre of its group's matrix block.
        spectral_index in the group-level tree = group index (0-based, in
        the order groups appear as rows in the matrix).
        Falls back to uniform spacing if group_spans is not populated. */
  function assignY(node) {
    if (!node.children) {
      var gi  = node.spectral_index || 0;
      var span = group_spans[gi];
      if (span) {
        /* centre of the group block */
        node.dendY = (span[0] + span[1]) / 2 * cellSize + cellSize / 2;
      } else {
        node.dendY = gi * cellSize + cellSize / 2;
      }
    } else {
      node.children.forEach(assignY);
      node.dendY = (node.children[0].dendY + node.children[node.children.length-1].dendY) / 2;
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
    .data(links.filter(function (d) { return d.tgt._clique >= 0; })).join('path')
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

  /* 5. No dashed connectors needed: leaves are already pinned to the
        centre of their group block in the matrix. */

  /* No leaf labels — rows are already labelled by the matrix y-axis */

  /* 6. Internal node dots — only within-cluster nodes */
  root.each(function (d) {
    if (!d.children || d._clique < 0) return;
    dendG.append('circle')
      .attr('cx', d.dendX).attr('cy', d.dendY).attr('r', 1.8)
      .attr('fill', WHITE).attr('stroke', NAVY).attr('stroke-width', 1).attr('opacity', 0.65);
  });
}());

/* ── key schema horizontal tree ────────────────────────────────────────
   Cleaner left-to-right layout (replaces the previous radial graph).
   The root node ("record") is suppressed — its children represent the
   schema's top-level keys directly. Type-colour-coded nodes with
   compact badges show whether each key is a scalar, link, or list. */
(function () {
  var schemaData = EMD_SCHEMA || {};
  var topLevel   = (schemaData.children || []);
  if (!topLevel.length) {
    d3.select('#emd-key-graph').append('div')
      .style('color', '#888').style('font-size', '12px')
      .style('font-family', FONT).style('padding', '20px 0')
      .text('No schema fields available for this record type.');
    return;
  }

  /* Wrap the real children under a synthetic root so d3.tree() works,
     but we will *never* render the synthetic root. */
  var hierData = {name: '', children: topLevel};
  var rootH    = d3.hierarchy(hierData);

  /* Count leaves to size the SVG height. */
  var leaves = rootH.leaves().length;
  var rowH   = 24;
  var topPad = 18, botPad = 70;
  var h      = Math.max(280, leaves * rowH + topPad + botPad);

  /* Width: use container, fall back to viewport. Reserve room for labels. */
  var contW = (containerEl && containerEl.clientWidth) || window.innerWidth - 48;
  var w     = Math.min(contW, 820);

  var leftPad = 16;
  var labelReserve = 220;  /* horizontal space reserved for labels on the right */

  var svg2 = d3.select('#emd-key-graph').append('svg')
    .attr('width', w).attr('height', h)
    .style('overflow', 'visible');

  var tree = d3.tree()
    .size([h - topPad - botPad, w - leftPad - labelReserve])
    .separation(function (a, b) { return a.parent === b.parent ? 1 : 1.3; });
  tree(rootH);

  var g2 = svg2.append('g')
    .attr('transform', 'translate(' + leftPad + ',' + topPad + ')');

  var typeColor = { scalar: NAVY, link: RED, links: RED, list: MUSTARD };
  var typeLabel = { scalar: 'value', link: 'link',  links: 'links', list: 'list' };

  /* Links — but skip the edges from the synthetic root, draw a short
     vertical anchor line on the left instead. */
  g2.selectAll('.emd-klink')
    .data(rootH.links().filter(function (d) { return d.source.depth > 0; }))
    .join('path')
    .attr('class','emd-klink')
    .attr('fill','none').attr('stroke', NAVY).attr('stroke-width', 1.1).attr('opacity', 0.28)
    .attr('d', d3.linkHorizontal()
      .x(function (d) { return d.y; })
      .y(function (d) { return d.x; }));

  /* Anchor line + ticks from a virtual rail to each depth-1 node. */
  var depth1 = rootH.descendants().filter(function (d) { return d.depth === 1; });
  if (depth1.length > 1) {
    var railX = depth1[0].y - 18;
    var yMin  = d3.min(depth1, function (d) { return d.x; });
    var yMax  = d3.max(depth1, function (d) { return d.x; });
    g2.append('line')
      .attr('x1', railX).attr('x2', railX)
      .attr('y1', yMin).attr('y2', yMax)
      .attr('stroke', NAVY).attr('stroke-width', 1.5).attr('opacity', 0.35);
    depth1.forEach(function (d) {
      g2.append('line')
        .attr('x1', railX).attr('x2', d.y)
        .attr('y1', d.x).attr('y2', d.x)
        .attr('stroke', NAVY).attr('stroke-width', 1.1).attr('opacity', 0.28);
    });
  }

  /* Nodes — skip the synthetic root. */
  var nodes = rootH.descendants().filter(function (d) { return d.depth > 0; });

  var knode = g2.selectAll('.emd-knode')
    .data(nodes).join('g')
    .attr('class','emd-knode')
    .attr('transform', function (d) { return 'translate(' + d.y + ',' + d.x + ')'; });

  knode.append('circle')
    .attr('r', function (d) { return d.depth === 1 ? 5 : 3.5; })
    .attr('fill', function (d) { return typeColor[d.data.type] || NAVY; })
    .attr('stroke', WHITE).attr('stroke-width', 1.5);

  /* Field name label */
  knode.append('text')
    .attr('x', 10).attr('dy', '0.32em')
    .attr('font-family', FONT)
    .attr('font-size', function (d) { return d.depth === 1 ? 11 : 10; })
    .attr('font-weight', function (d) { return d.depth === 1 ? 600 : 400; })
    .attr('fill', NAVY)
    .text(function (d) { return d.data.name; });

  /* Type badge to the right of the label */
  knode.each(function (d) {
    if (!d.data.type) return;
    var label = typeLabel[d.data.type] || d.data.type;
    var nameLen = (d.data.name || '').length;
    var bx = 10 + nameLen * (d.depth === 1 ? 6.4 : 5.8) + 8;
    var bw = label.length * 5.5 + 10;
    var sel = d3.select(this);
    sel.append('rect')
      .attr('x', bx).attr('y', -7)
      .attr('width', bw).attr('height', 14).attr('rx', 7)
      .attr('fill', typeColor[d.data.type] || NAVY).attr('opacity', 0.12);
    sel.append('text')
      .attr('x', bx + bw / 2).attr('y', 0).attr('dy', '0.32em')
      .attr('text-anchor', 'middle')
      .attr('font-family', FONT).attr('font-size', 8)
      .attr('font-weight', 600)
      .attr('fill', typeColor[d.data.type] || NAVY)
      .text(label);
  });

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
