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
    <option value="../Earth_System_Model_Families/BCC-CSM/">BCC-CSM</option>
    <option value="../Earth_System_Model_Families/CNRM-CM/">CNRM-CM</option>
    <option value="../Earth_System_Model_Families/FGOALS/">FGOALS</option>
    <option value="../Earth_System_Model_Families/CanESM/">CanESM</option>
    <option value="../Earth_System_Model_Families/GISS-E2/">GISS-E2</option>
    <option value="../Earth_System_Model_Families/MIROC/">MIROC</option>
    <option value="../Earth_System_Model_Families/CESM/">CESM</option>
    <option value="../Earth_System_Model_Families/GFDL-CM4/">GFDL-CM4</option>
    <option value="../Earth_System_Model_Families/IPSL-CM/">IPSL-CM</option>
    <option value="../Earth_System_Model_Families/MPI-ESM/">MPI-ESM</option>
    <option value="../Earth_System_Model_Families/cas-fgoals-g3.5/">cas-fgoals-g3.5</option>
    <option value="../Earth_System_Model_Families/access-esm/">access-esm</option>
    <option value="../Earth_System_Model_Families/ec-earth/">ec-earth</option>
    <option value="../Earth_System_Model_Families/HadGEM3/">HadGEM3</option>
    <option value="../Earth_System_Model_Families/gfdl/">gfdl</option>
    <option value="../Earth_System_Model_Families/HadCM2/">HadCM2</option>
    <option value="../Earth_System_Model_Families/ICON/">ICON</option>
    <option value="../Earth_System_Model_Families/UKESM1/">UKESM1</option>
  </select>
  <button id="emd-go-btn" onclick="emdGotoEntry()">Open →</button>
  <button class="emd-font-btn" id="emd-font-toggle" onclick="emdToggleFont()">✨ Pretty font</button>
</div>
<div class="emd-stats">
  <span><b>18</b> registered entries</span>
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
var EMD_DATA    = {"ids":["BCC-CSM","CNRM-CM","FGOALS","CanESM","GISS-E2","MIROC","CESM","GFDL-CM4","IPSL-CM","MPI-ESM","cas-fgoals-g3.5","access-esm","ec-earth","HadGEM3","gfdl","HadCM2","ICON","UKESM1"],"link":[[0.0,0.8847662141779788,0.8841354723707665,0.8917647058823529,0.8841088674275681,0.8688544891640867,0.8705499760879961,0.8600898692810458,0.863440927218345,0.8584558823529411,0.08808620689655172,0.05355859681212437,0.059554054029859825,0.06401915661596218,0.05349718985040086,0.13453444703444706,0.8005698005698005,0.8022339625137452],[0.8847662141779788,0.0,0.8879747703277115,0.8798639455782313,0.8880995475113123,0.8744375644994841,0.8593639406982305,0.862438725490196,0.8630269607843137,0.8583210784313726,0.0913390804597701,0.057655038759689914,0.05859611524985543,0.06354068771644066,0.057893214315232665,0.13688186487482262,0.8021274329685544,0.8030814131342444],[0.8841354723707665,0.8879747703277115,0.0,0.881782531194296,0.8963161021984551,0.870017825311943,0.8551267336202774,0.8597927807486632,0.8753899286987523,0.8593471479500892,0.1386896551724138,0.06440129344133785,0.05859611524985543,0.06665073556333061,0.05361186874948343,0.13688186487482262,0.8026741776741777,0.8059131383783515],[0.8917647058823529,0.8798639455782313,0.881782531194296,0.0,0.8706362545018007,0.8865546218487395,0.8751602104256337,0.8636141956782712,0.8648146758703481,0.866015156062425,0.11017241379310345,0.06463156519466945,0.06281324803998976,0.07411485039586649,0.05520910819075956,0.13304132878076538,0.7981516095534787,0.8070499623814603],[0.8841088674275681,0.8880995475113123,0.8963161021984551,0.8706362545018007,0.0,0.8694736842105263,0.8620213613900845,0.8911356209150326,0.8693816456931031,0.8637236611062336,0.09936973180076628,0.05397994512673112,0.05734088512433242,0.06641150111356983,0.07549005427445794,0.13766433748828116,0.8042042761668929,0.8026018801002058],[0.8688544891640867,0.8744375644994841,0.870017825311943,0.8865546218487395,0.8694736842105263,0.0,0.8644715447154471,0.8624516253869968,0.8612132352941176,0.8742163312693498,0.1,0.05442089103736608,0.05755009014525292,0.08272729058725405,0.05406231919993387,0.143369967278418,0.7976323987538941,0.8163214855602683],[0.8705499760879961,0.8593639406982305,0.8551267336202774,0.8751602104256337,0.8620213613900845,0.8644715447154471,0.0,0.8710441575003985,0.8586896221903395,0.8572549019607844,0.08335632183908046,0.07844460412856022,0.06456306855515152,0.08361420854734275,0.06720458991101194,0.12799807013221645,0.790984643179765,0.8073292530678116],[0.8600898692810458,0.862438725490196,0.8597927807486632,0.8636141956782712,0.8911356209150326,0.8624516253869968,0.8710441575003985,0.0,0.8839869281045752,0.8831699346405228,0.08254849137931033,0.05500228638620329,0.05692247508249141,0.07249868877970488,0.10315315315315314,0.1337603341711323,0.7942627206645898,0.824012295153501],[0.863440927218345,0.8630269607843137,0.8753899286987523,0.8648146758703481,0.8693816456931031,0.8612132352941176,0.8586896221903395,0.8839869281045752,0.0,0.8951146560319043,0.09470366379310344,0.05486183694800104,0.05692247508249141,0.06617226666380907,0.053726547648566006,0.1260225494380424,0.7932242990654205,0.8193111259931709],[0.8584558823529411,0.8583210784313726,0.8593471479500892,0.866015156062425,0.8637236611062336,0.8742163312693498,0.8572549019607844,0.8831699346405228,0.8951146560319043,0.0,0.08211745689655173,0.06486183694800104,0.056504065040650406,0.07861245805136888,0.05361186874948343,0.1371336605491535,0.7927050882658359,0.8285826491719788],[0.08808620689655172,0.0913390804597701,0.1386896551724138,0.11017241379310345,0.09936973180076628,0.1,0.08335632183908046,0.08254849137931033,0.09470366379310344,0.08211745689655173,0.0,0.22237352246253855,0.20265509231446996,0.10746951524237883,0.2723704589146868,0.07133555802743789,0.0663448275862069,0.07346474234792716],[0.05355859681212437,0.057655038759689914,0.06440129344133785,0.06463156519466945,0.05397994512673112,0.05442089103736608,0.07844460412856022,0.05500228638620329,0.05486183694800104,0.06486183694800104,0.22237352246253855,0.0,0.2820211368060094,0.1044036912851031,0.2316812321816558,0.06234495772819609,0.054701789913770574,0.05739913176710929],[0.059554054029859825,0.05859611524985543,0.05859611524985543,0.06281324803998976,0.05734088512433242,0.05755009014525292,0.06456306855515152,0.05692247508249141,0.05692247508249141,0.056504065040650406,0.20265509231446996,0.2820211368060094,0.0,0.1146214454003736,0.2026884074185776,0.0667106694012007,0.059989114535496824,0.06552435844533086],[0.06401915661596218,0.06354068771644066,0.06665073556333061,0.07411485039586649,0.06641150111356983,0.08272729058725405,0.08361420854734275,0.07249868877970488,0.06617226666380907,0.07861245805136888,0.10746951524237883,0.1044036912851031,0.1146214454003736,0.0,0.11225126702290644,0.2958999486760911,0.06856461116141672,0.17287748546034887],[0.05349718985040086,0.057893214315232665,0.05361186874948343,0.05520910819075956,0.07549005427445794,0.05406231919993387,0.06720458991101194,0.10315315315315314,0.053726547648566006,0.05361186874948343,0.2723704589146868,0.2316812321816558,0.2026884074185776,0.11225126702290644,0.0,0.06369785737202133,0.05349718985040086,0.06030594814998484],[0.13453444703444706,0.13688186487482262,0.13688186487482262,0.13304132878076538,0.13766433748828116,0.143369967278418,0.12799807013221645,0.1337603341711323,0.1260225494380424,0.1371336605491535,0.07133555802743789,0.06234495772819609,0.0667106694012007,0.2958999486760911,0.06369785737202133,0.0,0.1625699171103174,0.17109166138258605],[0.8005698005698005,0.8021274329685544,0.8026741776741777,0.7981516095534787,0.8042042761668929,0.7976323987538941,0.790984643179765,0.7942627206645898,0.7932242990654205,0.7927050882658359,0.0663448275862069,0.054701789913770574,0.059989114535496824,0.06856461116141672,0.05349718985040086,0.1625699171103174,0.0,0.7892369637291134],[0.8022339625137452,0.8030814131342444,0.8059131383783515,0.8070499623814603,0.8026018801002058,0.8163214855602683,0.8073292530678116,0.824012295153501,0.8193111259931709,0.8285826491719788,0.07346474234792716,0.05739913176710929,0.06552435844533086,0.17287748546034887,0.06030594814998484,0.17109166138258605,0.7892369637291134,0.0]],"text":[[0.0,0.8847662141779788,0.8841354723707665,0.8917647058823529,0.8841088674275681,0.8688544891640867,0.8705499760879961,0.8600898692810458,0.863440927218345,0.8584558823529411,0.08808620689655172,0.05355859681212437,0.059554054029859825,0.06401915661596218,0.05349718985040086,0.13453444703444706,0.8005698005698005,0.8022339625137452],[0.8847662141779788,0.0,0.8879747703277115,0.8798639455782313,0.8880995475113123,0.8744375644994841,0.8593639406982305,0.862438725490196,0.8630269607843137,0.8583210784313726,0.0913390804597701,0.057655038759689914,0.05859611524985543,0.06354068771644066,0.057893214315232665,0.13688186487482262,0.8021274329685544,0.8030814131342444],[0.8841354723707665,0.8879747703277115,0.0,0.881782531194296,0.8963161021984551,0.870017825311943,0.8551267336202774,0.8597927807486632,0.8753899286987523,0.8593471479500892,0.1386896551724138,0.06440129344133785,0.05859611524985543,0.06665073556333061,0.05361186874948343,0.13688186487482262,0.8026741776741777,0.8059131383783515],[0.8917647058823529,0.8798639455782313,0.881782531194296,0.0,0.8706362545018007,0.8865546218487395,0.8751602104256337,0.8636141956782712,0.8648146758703481,0.866015156062425,0.11017241379310345,0.06463156519466945,0.06281324803998976,0.07411485039586649,0.05520910819075956,0.13304132878076538,0.7981516095534787,0.8070499623814603],[0.8841088674275681,0.8880995475113123,0.8963161021984551,0.8706362545018007,0.0,0.8694736842105263,0.8620213613900845,0.8911356209150326,0.8693816456931031,0.8637236611062336,0.09936973180076628,0.05397994512673112,0.05734088512433242,0.06641150111356983,0.07549005427445794,0.13766433748828116,0.8042042761668929,0.8026018801002058],[0.8688544891640867,0.8744375644994841,0.870017825311943,0.8865546218487395,0.8694736842105263,0.0,0.8644715447154471,0.8624516253869968,0.8612132352941176,0.8742163312693498,0.1,0.05442089103736608,0.05755009014525292,0.08272729058725405,0.05406231919993387,0.143369967278418,0.7976323987538941,0.8163214855602683],[0.8705499760879961,0.8593639406982305,0.8551267336202774,0.8751602104256337,0.8620213613900845,0.8644715447154471,0.0,0.8710441575003985,0.8586896221903395,0.8572549019607844,0.08335632183908046,0.07844460412856022,0.06456306855515152,0.08361420854734275,0.06720458991101194,0.12799807013221645,0.790984643179765,0.8073292530678116],[0.8600898692810458,0.862438725490196,0.8597927807486632,0.8636141956782712,0.8911356209150326,0.8624516253869968,0.8710441575003985,0.0,0.8839869281045752,0.8831699346405228,0.08254849137931033,0.05500228638620329,0.05692247508249141,0.07249868877970488,0.10315315315315314,0.1337603341711323,0.7942627206645898,0.824012295153501],[0.863440927218345,0.8630269607843137,0.8753899286987523,0.8648146758703481,0.8693816456931031,0.8612132352941176,0.8586896221903395,0.8839869281045752,0.0,0.8951146560319043,0.09470366379310344,0.05486183694800104,0.05692247508249141,0.06617226666380907,0.053726547648566006,0.1260225494380424,0.7932242990654205,0.8193111259931709],[0.8584558823529411,0.8583210784313726,0.8593471479500892,0.866015156062425,0.8637236611062336,0.8742163312693498,0.8572549019607844,0.8831699346405228,0.8951146560319043,0.0,0.08211745689655173,0.06486183694800104,0.056504065040650406,0.07861245805136888,0.05361186874948343,0.1371336605491535,0.7927050882658359,0.8285826491719788],[0.08808620689655172,0.0913390804597701,0.1386896551724138,0.11017241379310345,0.09936973180076628,0.1,0.08335632183908046,0.08254849137931033,0.09470366379310344,0.08211745689655173,0.0,0.22237352246253855,0.20265509231446996,0.10746951524237883,0.2723704589146868,0.07133555802743789,0.0663448275862069,0.07346474234792716],[0.05355859681212437,0.057655038759689914,0.06440129344133785,0.06463156519466945,0.05397994512673112,0.05442089103736608,0.07844460412856022,0.05500228638620329,0.05486183694800104,0.06486183694800104,0.22237352246253855,0.0,0.2820211368060094,0.1044036912851031,0.2316812321816558,0.06234495772819609,0.054701789913770574,0.05739913176710929],[0.059554054029859825,0.05859611524985543,0.05859611524985543,0.06281324803998976,0.05734088512433242,0.05755009014525292,0.06456306855515152,0.05692247508249141,0.05692247508249141,0.056504065040650406,0.20265509231446996,0.2820211368060094,0.0,0.1146214454003736,0.2026884074185776,0.0667106694012007,0.059989114535496824,0.06552435844533086],[0.06401915661596218,0.06354068771644066,0.06665073556333061,0.07411485039586649,0.06641150111356983,0.08272729058725405,0.08361420854734275,0.07249868877970488,0.06617226666380907,0.07861245805136888,0.10746951524237883,0.1044036912851031,0.1146214454003736,0.0,0.11225126702290644,0.2958999486760911,0.06856461116141672,0.17287748546034887],[0.05349718985040086,0.057893214315232665,0.05361186874948343,0.05520910819075956,0.07549005427445794,0.05406231919993387,0.06720458991101194,0.10315315315315314,0.053726547648566006,0.05361186874948343,0.2723704589146868,0.2316812321816558,0.2026884074185776,0.11225126702290644,0.0,0.06369785737202133,0.05349718985040086,0.06030594814998484],[0.13453444703444706,0.13688186487482262,0.13688186487482262,0.13304132878076538,0.13766433748828116,0.143369967278418,0.12799807013221645,0.1337603341711323,0.1260225494380424,0.1371336605491535,0.07133555802743789,0.06234495772819609,0.0667106694012007,0.2958999486760911,0.06369785737202133,0.0,0.1625699171103174,0.17109166138258605],[0.8005698005698005,0.8021274329685544,0.8026741776741777,0.7981516095534787,0.8042042761668929,0.7976323987538941,0.790984643179765,0.7942627206645898,0.7932242990654205,0.7927050882658359,0.0663448275862069,0.054701789913770574,0.059989114535496824,0.06856461116141672,0.05349718985040086,0.1625699171103174,0.0,0.7892369637291134],[0.8022339625137452,0.8030814131342444,0.8059131383783515,0.8070499623814603,0.8026018801002058,0.8163214855602683,0.8073292530678116,0.824012295153501,0.8193111259931709,0.8285826491719788,0.07346474234792716,0.05739913176710929,0.06552435844533086,0.17287748546034887,0.06030594814998484,0.17109166138258605,0.7892369637291134,0.0]],"method":"field-level | link: field-level (links uninformative) | order: spectral graph components","folder":"Earth System Model Families","meta":[{"label":"BCC-CSM","tags":["atmosphere","land_surface","ocean"]},{"label":"CNRM-CM","tags":["atmosphere","land-surface","ocean"]},{"label":"FGOALS","tags":["atmosphere","land_surface","ocean"]},{"label":"CanESM","tags":["atmosphere","land_surface","ocean","sea_ice"]},{"label":"GISS-E2","tags":["atmosphere","land_surface","ocean"]},{"label":"MIROC","tags":["atmosphere","land_surface","ocean","sea_ice"]},{"label":"CESM","tags":["atmosphere","land_surface","ocean","sea_ice","ocean_biogeochemistry"]},{"label":"GFDL-CM4","tags":["atmosphere","land_surface","ocean","ocean_biogeochemistry"]},{"label":"IPSL-CM","tags":["atmosphere","land_surface","ocean","ocean_biogeochemistry"]},{"label":"MPI-ESM","tags":["atmosphere","land_surface","ocean","ocean_biogeochemistry"]},{"label":"cas-fgoals-g3.5","tags":["atmosphere","land_surface","ocean","sea_ice"]},{"label":"access-esm","tags":["aerosol","atmosphere","land_surface","ocean","ocean-biogeochemistry","sea_ice"]},{"label":"ec-earth","tags":["atmosphere","ocean","sea-ice","ocean-biogeochemistry","land-surface","land-ice","atmospheric-chemistry","aerosol"]},{"label":"HadGEM3","tags":["atmosphere","ocean","land_surface","sea_ice","ocean_biogeochemistry","atmospheric_chemistry"]},{"label":"gfdl","tags":["aerosol","atmosphere","atmospheric-chemistry","land_surface","ocean","ocean-biogeochemistry","sea_ice"]},{"label":"HadCM2","tags":["atmosphere","ocean"]},{"label":"ICON","tags":["atmosphere","ocean"]},{"label":"UKESM1","tags":["atmosphere","land_surface","ocean","ocean_biogeochemistry","atmospheric_chemistry"]}],"tree":{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"access-esm","leaf":true,"spectral_index":2,"value":0.0},{"name":"ec-earth","leaf":true,"spectral_index":3,"value":0.0}],"value":0.7179788631939906},{"name":"","leaf":false,"children":[{"name":"cas-fgoals-g3.5","leaf":true,"spectral_index":1,"value":0.0},{"name":"gfdl","leaf":true,"spectral_index":5,"value":0.0}],"value":0.7276295410853132}],"value":0.7851504364056895},{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"ICON","leaf":true,"spectral_index":7,"value":0.0},{"name":"","leaf":false,"children":[{"name":"BCC-CSM","leaf":true,"spectral_index":0,"value":0.0},{"name":"UKESM1","leaf":true,"spectral_index":8,"value":0.0}],"value":0.1883562834545262}],"value":0.2065546957923228},{"name":"","leaf":false,"children":[{"name":"HadGEM3","leaf":true,"spectral_index":4,"value":0.0},{"name":"HadCM2","leaf":true,"spectral_index":6,"value":0.0}],"value":0.7041000513239088}],"value":0.869721883003276}],"value":0.926351779683929},"clusters":[0,0,0,0,0,0,0,0,0,0,1,2,3,4,5,6,7,8],"group_spans":[[0,9],[10,10],[11,11],[12,12],[13,13],[14,14],[15,15],[16,16],[17,17]]};
var EMD_ENTRIES = [{"label":"BCC-CSM","url":"../Earth_System_Model_Families/BCC-CSM/"},{"label":"CNRM-CM","url":"../Earth_System_Model_Families/CNRM-CM/"},{"label":"FGOALS","url":"../Earth_System_Model_Families/FGOALS/"},{"label":"CanESM","url":"../Earth_System_Model_Families/CanESM/"},{"label":"GISS-E2","url":"../Earth_System_Model_Families/GISS-E2/"},{"label":"MIROC","url":"../Earth_System_Model_Families/MIROC/"},{"label":"CESM","url":"../Earth_System_Model_Families/CESM/"},{"label":"GFDL-CM4","url":"../Earth_System_Model_Families/GFDL-CM4/"},{"label":"IPSL-CM","url":"../Earth_System_Model_Families/IPSL-CM/"},{"label":"MPI-ESM","url":"../Earth_System_Model_Families/MPI-ESM/"},{"label":"cas-fgoals-g3.5","url":"../Earth_System_Model_Families/cas-fgoals-g3.5/"},{"label":"access-esm","url":"../Earth_System_Model_Families/access-esm/"},{"label":"ec-earth","url":"../Earth_System_Model_Families/ec-earth/"},{"label":"HadGEM3","url":"../Earth_System_Model_Families/HadGEM3/"},{"label":"gfdl","url":"../Earth_System_Model_Families/gfdl/"},{"label":"HadCM2","url":"../Earth_System_Model_Families/HadCM2/"},{"label":"ICON","url":"../Earth_System_Model_Families/ICON/"},{"label":"UKESM1","url":"../Earth_System_Model_Families/UKESM1/"}];
var EMD_SCHEMA  = {"name":"record","children":[{"name":"collaborative_institutions","type":"scalar"},{"name":"common_scientific_basis","type":"scalar"},{"name":"computational_requirements","type":"scalar"},{"name":"description","type":"scalar"},{"name":"documentation","type":"scalar"},{"name":"established","type":"scalar"},{"name":"evolution","type":"scalar"},{"name":"family_type","type":"scalar"},{"name":"license","type":"scalar"},{"name":"primary_institution","type":"scalar"},{"name":"programming_languages","type":"scalar"},{"name":"references","type":"scalar"},{"name":"representative_member","type":"scalar"},{"name":"scientific_domains","type":"list"},{"name":"shared_code_base","type":"scalar"},{"name":"software_dependencies","type":"scalar"},{"name":"source_code_repository","type":"scalar"},{"name":"ui_label","type":"scalar"},{"name":"validation_key","type":"scalar"},{"name":"variation_dimensions","type":"scalar"},{"name":"website","type":"scalar"}]};

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
