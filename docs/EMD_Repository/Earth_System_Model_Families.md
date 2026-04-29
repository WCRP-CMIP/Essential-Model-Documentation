# Earth System Model Families

**Optional.** ESM families group coupled model configurations across generations (e.g. HadGEM3, CNRM-CM, CESM). A family ID is referenced by the final model record at Stage 4.

---

!!! info "Generated files"
    This page is auto-generated during the build from live registry data. Three files are produced for each record type:

    - **`Earth_System_Model_Families.md`** — this page, embedded in the MkDocs site layout
    - **`Earth_System_Model_Families_data.json`** — processed similarity matrices, dendrogram tree, and key schema
    - **`Earth_System_Model_Families_raw.json`** — raw JSON-LD records as fetched from the cmipld registry (depth 2)

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
<span class="emd-section-label">View a specific ESM Family</span>
<div class="emd-selector-row">
  <select id="emd-entry-select">
    <option value="">Select an entry…</option>
    <option value="../Earth_System_Model_Families/ec-earth/">ec-earth</option>
    <option value="../Earth_System_Model_Families/ACCESS/">ACCESS</option>
    <option value="../Earth_System_Model_Families/ICON/">ICON</option>
    <option value="../Earth_System_Model_Families/UKESM1/">UKESM1</option>
    <option value="../Earth_System_Model_Families/CESM/">CESM</option>
    <option value="../Earth_System_Model_Families/GFDL-CM4/">GFDL-CM4</option>
    <option value="../Earth_System_Model_Families/MPI-ESM/">MPI-ESM</option>
    <option value="../Earth_System_Model_Families/IPSL-CM/">IPSL-CM</option>
    <option value="../Earth_System_Model_Families/MIROC/">MIROC</option>
    <option value="../Earth_System_Model_Families/BCC-CSM/">BCC-CSM</option>
    <option value="../Earth_System_Model_Families/CanESM/">CanESM</option>
    <option value="../Earth_System_Model_Families/CNRM-CM/">CNRM-CM</option>
    <option value="../Earth_System_Model_Families/GISS-E2/">GISS-E2</option>
    <option value="../Earth_System_Model_Families/FGOALS/">FGOALS</option>
    <option value="../Earth_System_Model_Families/HadGEM3/">HadGEM3</option>
    <option value="../Earth_System_Model_Families/HadCM2/">HadCM2</option>
  </select>
  <button id="emd-go-btn" onclick="emdGotoEntry()">Open →</button>
  <button class="emd-font-btn" id="emd-font-toggle" onclick="emdToggleFont()">✨ Pretty font</button>
</div>
<div class="emd-stats">
  <span><b>16</b> registered entries</span>
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
var EMD_DATA    = {"ids":["ec-earth","ACCESS","ICON","UKESM1","CESM","GFDL-CM4","MPI-ESM","IPSL-CM","MIROC","BCC-CSM","CanESM","CNRM-CM","GISS-E2","FGOALS","HadGEM3","HadCM2"],"link":[[0.0,0.07046850018709391,0.059989114535496824,0.06552435844533086,0.06456306855515152,0.05692247508249141,0.056504065040650406,0.05692247508249141,0.05755009014525292,0.059554054029859825,0.06281324803998976,0.05859611524985543,0.05734088512433242,0.05859611524985543,0.1146214454003736,0.0667106694012007],[0.07046850018709391,0.0,0.7557347915242653,0.7648475120385233,0.7849636285836542,0.770900974025974,0.7821108168147642,0.7722680280246069,0.7915242652084757,0.7768421052631579,0.8006835269993166,0.7839348370927318,0.7788926862611073,0.7897607655502392,0.06638313385009914,0.11819155844155844],[0.059989114535496824,0.7557347915242653,0.0,0.7892369637291134,0.790984643179765,0.7942627206645898,0.7927050882658359,0.7932242990654205,0.7976323987538941,0.8005698005698005,0.7981516095534787,0.8021274329685544,0.8042042761668929,0.8026741776741777,0.06856461116141672,0.1625699171103174],[0.06552435844533086,0.7648475120385233,0.7892369637291134,0.0,0.8073292530678116,0.824012295153501,0.8285826491719788,0.8193111259931709,0.8163214855602683,0.8022339625137452,0.8070499623814603,0.8030814131342444,0.8026018801002058,0.8059131383783515,0.17287748546034887,0.17109166138258605],[0.06456306855515152,0.7849636285836542,0.790984643179765,0.8073292530678116,0.0,0.8710441575003985,0.8572549019607844,0.8586896221903395,0.8644715447154471,0.8705499760879961,0.8751602104256337,0.8593639406982305,0.8620213613900845,0.8551267336202774,0.08361420854734275,0.12799807013221645],[0.05692247508249141,0.770900974025974,0.7942627206645898,0.824012295153501,0.8710441575003985,0.0,0.8831699346405228,0.8839869281045752,0.8624516253869968,0.8600898692810458,0.8636141956782712,0.862438725490196,0.8911356209150326,0.8597927807486632,0.07249868877970488,0.1337603341711323],[0.056504065040650406,0.7821108168147642,0.7927050882658359,0.8285826491719788,0.8572549019607844,0.8831699346405228,0.0,0.8951146560319043,0.8742163312693498,0.8584558823529411,0.866015156062425,0.8583210784313726,0.8637236611062336,0.8593471479500892,0.07861245805136888,0.1371336605491535],[0.05692247508249141,0.7722680280246069,0.7932242990654205,0.8193111259931709,0.8586896221903395,0.8839869281045752,0.8951146560319043,0.0,0.8612132352941176,0.863440927218345,0.8648146758703481,0.8630269607843137,0.8693816456931031,0.8753899286987523,0.06617226666380907,0.1260225494380424],[0.05755009014525292,0.7915242652084757,0.7976323987538941,0.8163214855602683,0.8644715447154471,0.8624516253869968,0.8742163312693498,0.8612132352941176,0.0,0.8688544891640867,0.8865546218487395,0.8744375644994841,0.8694736842105263,0.870017825311943,0.08272729058725405,0.143369967278418],[0.059554054029859825,0.7768421052631579,0.8005698005698005,0.8022339625137452,0.8705499760879961,0.8600898692810458,0.8584558823529411,0.863440927218345,0.8688544891640867,0.0,0.8917647058823529,0.8847662141779788,0.8841088674275681,0.8841354723707665,0.06401915661596218,0.13453444703444706],[0.06281324803998976,0.8006835269993166,0.7981516095534787,0.8070499623814603,0.8751602104256337,0.8636141956782712,0.866015156062425,0.8648146758703481,0.8865546218487395,0.8917647058823529,0.0,0.8798639455782313,0.8706362545018007,0.881782531194296,0.07411485039586649,0.13304132878076538],[0.05859611524985543,0.7839348370927318,0.8021274329685544,0.8030814131342444,0.8593639406982305,0.862438725490196,0.8583210784313726,0.8630269607843137,0.8744375644994841,0.8847662141779788,0.8798639455782313,0.0,0.8880995475113123,0.8879747703277115,0.06354068771644066,0.13688186487482262],[0.05734088512433242,0.7788926862611073,0.8042042761668929,0.8026018801002058,0.8620213613900845,0.8911356209150326,0.8637236611062336,0.8693816456931031,0.8694736842105263,0.8841088674275681,0.8706362545018007,0.8880995475113123,0.0,0.8963161021984551,0.06641150111356983,0.13766433748828116],[0.05859611524985543,0.7897607655502392,0.8026741776741777,0.8059131383783515,0.8551267336202774,0.8597927807486632,0.8593471479500892,0.8753899286987523,0.870017825311943,0.8841354723707665,0.881782531194296,0.8879747703277115,0.8963161021984551,0.0,0.06665073556333061,0.13688186487482262],[0.1146214454003736,0.06638313385009914,0.06856461116141672,0.17287748546034887,0.08361420854734275,0.07249868877970488,0.07861245805136888,0.06617226666380907,0.08272729058725405,0.06401915661596218,0.07411485039586649,0.06354068771644066,0.06641150111356983,0.06665073556333061,0.0,0.2958999486760911],[0.0667106694012007,0.11819155844155844,0.1625699171103174,0.17109166138258605,0.12799807013221645,0.1337603341711323,0.1371336605491535,0.1260225494380424,0.143369967278418,0.13453444703444706,0.13304132878076538,0.13688186487482262,0.13766433748828116,0.13688186487482262,0.2958999486760911,0.0]],"text":[[0.0,0.07046850018709391,0.059989114535496824,0.06552435844533086,0.06456306855515152,0.05692247508249141,0.056504065040650406,0.05692247508249141,0.05755009014525292,0.059554054029859825,0.06281324803998976,0.05859611524985543,0.05734088512433242,0.05859611524985543,0.1146214454003736,0.0667106694012007],[0.07046850018709391,0.0,0.7557347915242653,0.7648475120385233,0.7849636285836542,0.770900974025974,0.7821108168147642,0.7722680280246069,0.7915242652084757,0.7768421052631579,0.8006835269993166,0.7839348370927318,0.7788926862611073,0.7897607655502392,0.06638313385009914,0.11819155844155844],[0.059989114535496824,0.7557347915242653,0.0,0.7892369637291134,0.790984643179765,0.7942627206645898,0.7927050882658359,0.7932242990654205,0.7976323987538941,0.8005698005698005,0.7981516095534787,0.8021274329685544,0.8042042761668929,0.8026741776741777,0.06856461116141672,0.1625699171103174],[0.06552435844533086,0.7648475120385233,0.7892369637291134,0.0,0.8073292530678116,0.824012295153501,0.8285826491719788,0.8193111259931709,0.8163214855602683,0.8022339625137452,0.8070499623814603,0.8030814131342444,0.8026018801002058,0.8059131383783515,0.17287748546034887,0.17109166138258605],[0.06456306855515152,0.7849636285836542,0.790984643179765,0.8073292530678116,0.0,0.8710441575003985,0.8572549019607844,0.8586896221903395,0.8644715447154471,0.8705499760879961,0.8751602104256337,0.8593639406982305,0.8620213613900845,0.8551267336202774,0.08361420854734275,0.12799807013221645],[0.05692247508249141,0.770900974025974,0.7942627206645898,0.824012295153501,0.8710441575003985,0.0,0.8831699346405228,0.8839869281045752,0.8624516253869968,0.8600898692810458,0.8636141956782712,0.862438725490196,0.8911356209150326,0.8597927807486632,0.07249868877970488,0.1337603341711323],[0.056504065040650406,0.7821108168147642,0.7927050882658359,0.8285826491719788,0.8572549019607844,0.8831699346405228,0.0,0.8951146560319043,0.8742163312693498,0.8584558823529411,0.866015156062425,0.8583210784313726,0.8637236611062336,0.8593471479500892,0.07861245805136888,0.1371336605491535],[0.05692247508249141,0.7722680280246069,0.7932242990654205,0.8193111259931709,0.8586896221903395,0.8839869281045752,0.8951146560319043,0.0,0.8612132352941176,0.863440927218345,0.8648146758703481,0.8630269607843137,0.8693816456931031,0.8753899286987523,0.06617226666380907,0.1260225494380424],[0.05755009014525292,0.7915242652084757,0.7976323987538941,0.8163214855602683,0.8644715447154471,0.8624516253869968,0.8742163312693498,0.8612132352941176,0.0,0.8688544891640867,0.8865546218487395,0.8744375644994841,0.8694736842105263,0.870017825311943,0.08272729058725405,0.143369967278418],[0.059554054029859825,0.7768421052631579,0.8005698005698005,0.8022339625137452,0.8705499760879961,0.8600898692810458,0.8584558823529411,0.863440927218345,0.8688544891640867,0.0,0.8917647058823529,0.8847662141779788,0.8841088674275681,0.8841354723707665,0.06401915661596218,0.13453444703444706],[0.06281324803998976,0.8006835269993166,0.7981516095534787,0.8070499623814603,0.8751602104256337,0.8636141956782712,0.866015156062425,0.8648146758703481,0.8865546218487395,0.8917647058823529,0.0,0.8798639455782313,0.8706362545018007,0.881782531194296,0.07411485039586649,0.13304132878076538],[0.05859611524985543,0.7839348370927318,0.8021274329685544,0.8030814131342444,0.8593639406982305,0.862438725490196,0.8583210784313726,0.8630269607843137,0.8744375644994841,0.8847662141779788,0.8798639455782313,0.0,0.8880995475113123,0.8879747703277115,0.06354068771644066,0.13688186487482262],[0.05734088512433242,0.7788926862611073,0.8042042761668929,0.8026018801002058,0.8620213613900845,0.8911356209150326,0.8637236611062336,0.8693816456931031,0.8694736842105263,0.8841088674275681,0.8706362545018007,0.8880995475113123,0.0,0.8963161021984551,0.06641150111356983,0.13766433748828116],[0.05859611524985543,0.7897607655502392,0.8026741776741777,0.8059131383783515,0.8551267336202774,0.8597927807486632,0.8593471479500892,0.8753899286987523,0.870017825311943,0.8841354723707665,0.881782531194296,0.8879747703277115,0.8963161021984551,0.0,0.06665073556333061,0.13688186487482262],[0.1146214454003736,0.06638313385009914,0.06856461116141672,0.17287748546034887,0.08361420854734275,0.07249868877970488,0.07861245805136888,0.06617226666380907,0.08272729058725405,0.06401915661596218,0.07411485039586649,0.06354068771644066,0.06641150111356983,0.06665073556333061,0.0,0.2958999486760911],[0.0667106694012007,0.11819155844155844,0.1625699171103174,0.17109166138258605,0.12799807013221645,0.1337603341711323,0.1371336605491535,0.1260225494380424,0.143369967278418,0.13453444703444706,0.13304132878076538,0.13688186487482262,0.13766433748828116,0.13688186487482262,0.2958999486760911,0.0]],"method":"field-level | link: text (links uninformative) | order: UPGMA leaf traversal","folder":"Earth System Model Families","meta":[{"label":"ec-earth","tags":["atmosphere","ocean","sea-ice","ocean-biogeochemistry","land-surface","land-ice","atmospheric-chemistry","aerosol"]},{"label":"ACCESS","tags":["atmosphere","land_surface","ocean","sea_ice"]},{"label":"ICON","tags":["atmosphere","ocean"]},{"label":"UKESM1","tags":["atmosphere","land_surface","ocean","ocean_biogeochemistry","atmospheric_chemistry"]},{"label":"CESM","tags":["atmosphere","land_surface","ocean","sea_ice","ocean_biogeochemistry"]},{"label":"GFDL-CM4","tags":["atmosphere","land_surface","ocean","ocean_biogeochemistry"]},{"label":"MPI-ESM","tags":["atmosphere","land_surface","ocean","ocean_biogeochemistry"]},{"label":"IPSL-CM","tags":["atmosphere","land_surface","ocean","ocean_biogeochemistry"]},{"label":"MIROC","tags":["atmosphere","land_surface","ocean","sea_ice"]},{"label":"BCC-CSM","tags":["atmosphere","land_surface","ocean"]},{"label":"CanESM","tags":["atmosphere","land_surface","ocean","sea_ice"]},{"label":"CNRM-CM","tags":["atmosphere","land-surface","ocean"]},{"label":"GISS-E2","tags":["atmosphere","land_surface","ocean"]},{"label":"FGOALS","tags":["atmosphere","land_surface","ocean"]},{"label":"HadGEM3","tags":["atmosphere","ocean","land_surface","sea_ice","ocean_biogeochemistry","atmospheric_chemistry"]},{"label":"HadCM2","tags":["atmosphere","ocean"]}],"tree":{"name":"","leaf":false,"children":[{"name":"ec-earth","leaf":true,"spectral_index":0,"value":0.0},{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"ACCESS","leaf":true,"spectral_index":1,"value":0.0},{"name":"","leaf":false,"children":[{"name":"ICON","leaf":true,"spectral_index":2,"value":0.0},{"name":"","leaf":false,"children":[{"name":"UKESM1","leaf":true,"spectral_index":3,"value":0.0},{"name":"","leaf":false,"children":[{"name":"CESM","leaf":true,"spectral_index":4,"value":0.0},{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"GFDL-CM4","leaf":true,"spectral_index":5,"value":0.0},{"name":"","leaf":false,"children":[{"name":"MPI-ESM","leaf":true,"spectral_index":6,"value":0.0},{"name":"IPSL-CM","leaf":true,"spectral_index":7,"value":0.0}],"value":0.10488534396809568}],"value":0.11642156862745096},{"name":"","leaf":false,"children":[{"name":"MIROC","leaf":true,"spectral_index":8,"value":0.0},{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"BCC-CSM","leaf":true,"spectral_index":9,"value":0.0},{"name":"CanESM","leaf":true,"spectral_index":10,"value":0.0}],"value":0.1082352941176471},{"name":"","leaf":false,"children":[{"name":"CNRM-CM","leaf":true,"spectral_index":11,"value":0.0},{"name":"","leaf":false,"children":[{"name":"GISS-E2","leaf":true,"spectral_index":12,"value":0.0},{"name":"FGOALS","leaf":true,"spectral_index":13,"value":0.0}],"value":0.10368389780154486}],"value":0.1119628410804881}],"value":0.11911778579155975}],"value":0.1261323629930441}],"value":0.1346183639871335}],"value":0.13625750571231204}],"value":0.1883562834545262}],"value":0.20311150812804338}],"value":0.2206280052177653},{"name":"","leaf":false,"children":[{"name":"HadGEM3","leaf":true,"spectral_index":14,"value":0.0},{"name":"HadCM2","leaf":true,"spectral_index":15,"value":0.0}],"value":0.7041000513239088}],"value":0.8913335139975738}],"value":0.935554888028705}};
var EMD_ENTRIES = [{"label":"ec-earth","url":"../Earth_System_Model_Families/ec-earth/"},{"label":"ACCESS","url":"../Earth_System_Model_Families/ACCESS/"},{"label":"ICON","url":"../Earth_System_Model_Families/ICON/"},{"label":"UKESM1","url":"../Earth_System_Model_Families/UKESM1/"},{"label":"CESM","url":"../Earth_System_Model_Families/CESM/"},{"label":"GFDL-CM4","url":"../Earth_System_Model_Families/GFDL-CM4/"},{"label":"MPI-ESM","url":"../Earth_System_Model_Families/MPI-ESM/"},{"label":"IPSL-CM","url":"../Earth_System_Model_Families/IPSL-CM/"},{"label":"MIROC","url":"../Earth_System_Model_Families/MIROC/"},{"label":"BCC-CSM","url":"../Earth_System_Model_Families/BCC-CSM/"},{"label":"CanESM","url":"../Earth_System_Model_Families/CanESM/"},{"label":"CNRM-CM","url":"../Earth_System_Model_Families/CNRM-CM/"},{"label":"GISS-E2","url":"../Earth_System_Model_Families/GISS-E2/"},{"label":"FGOALS","url":"../Earth_System_Model_Families/FGOALS/"},{"label":"HadGEM3","url":"../Earth_System_Model_Families/HadGEM3/"},{"label":"HadCM2","url":"../Earth_System_Model_Families/HadCM2/"}];
var EMD_SCHEMA  = {"name":"record","children":[{"name":"collaborative_institutions","type":"scalar"},{"name":"common_scientific_basis","type":"scalar"},{"name":"computational_requirements","type":"scalar"},{"name":"description","type":"scalar"},{"name":"documentation","type":"scalar"},{"name":"established","type":"scalar"},{"name":"evolution","type":"scalar"},{"name":"family_type","type":"scalar"},{"name":"license","type":"scalar"},{"name":"primary_institution","type":"scalar"},{"name":"programming_languages","type":"scalar"},{"name":"references","type":"scalar"},{"name":"representative_member","type":"scalar"},{"name":"scientific_domains","type":"list"},{"name":"shared_code_base","type":"scalar"},{"name":"software_dependencies","type":"scalar"},{"name":"source_code_repository","type":"scalar"},{"name":"ui_label","type":"scalar"},{"name":"validation_key","type":"scalar"},{"name":"variation_dimensions","type":"scalar"},{"name":"website","type":"scalar"}]};

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
