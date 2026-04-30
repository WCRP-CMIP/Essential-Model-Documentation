# Horizontal Grid Cells

**Stage 1.** Grid cells define the fundamental 2D horizontal geometry — the shape, resolution, and extent of a single tile. A regular 1° atmosphere grid and a tripolar ocean grid are each their own record. Every grid cell is assigned a `g###` ID used in Stage 2.

---

!!! info "Generated files"
    This page is auto-generated during the build from live registry data. Three files are produced for each record type:

    - **`Horizontal_Grid_Cells.md`** — this page, embedded in the MkDocs site layout
    - **`Horizontal_Grid_Cells_data.json`** — processed similarity matrices, dendrogram tree, and key schema
    - **`Horizontal_Grid_Cells_raw.json`** — raw JSON-LD records as fetched from the cmipld registry (depth 2)

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
<span class="emd-section-label">View a specific Grid Cell</span>
<div class="emd-selector-row">
  <select id="emd-entry-select">
    <option value="">Select an entry…</option>
    <option value="../Horizontal_Grid_Cells/g118/">g118</option>
    <option value="../Horizontal_Grid_Cells/g116/">g116</option>
    <option value="../Horizontal_Grid_Cells/g103/">g103</option>
    <option value="../Horizontal_Grid_Cells/g104/">g104</option>
    <option value="../Horizontal_Grid_Cells/g107/">g107</option>
    <option value="../Horizontal_Grid_Cells/g119/">g119</option>
    <option value="../Horizontal_Grid_Cells/g120/">g120</option>
    <option value="../Horizontal_Grid_Cells/g105/">g105</option>
    <option value="../Horizontal_Grid_Cells/g101/">g101</option>
    <option value="../Horizontal_Grid_Cells/g114/">g114</option>
    <option value="../Horizontal_Grid_Cells/g112/">g112</option>
    <option value="../Horizontal_Grid_Cells/g106/">g106</option>
    <option value="../Horizontal_Grid_Cells/g113/">g113</option>
    <option value="../Horizontal_Grid_Cells/g117/">g117</option>
    <option value="../Horizontal_Grid_Cells/g111/">g111</option>
    <option value="../Horizontal_Grid_Cells/g100/">g100</option>
    <option value="../Horizontal_Grid_Cells/g108/">g108</option>
    <option value="../Horizontal_Grid_Cells/g110/">g110</option>
    <option value="../Horizontal_Grid_Cells/g115/">g115</option>
    <option value="../Horizontal_Grid_Cells/g109/">g109</option>
  </select>
  <button id="emd-go-btn" onclick="emdGotoEntry()">Open →</button>
  <button class="emd-font-btn" id="emd-font-toggle" onclick="emdToggleFont()">✨ Pretty font</button>
</div>
<div class="emd-stats">
  <span><b>20</b> registered entries</span>
  <span>Endpoint: <b>horizontal_grid_cell</b></span>
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
var EMD_DATA    = {"ids":["g118","g116","g103","g104","g107","g119","g120","g105","g101","g114","g112","g106","g113","g117","g111","g100","g108","g110","g115","g109"],"link":[[0.0,0.893939393939394,0.5974967061923584,0.5974967061923584,0.6515151515151515,0.7348484848484849,0.2932302055417549,0.3437326347543065,0.2675512310187233,0.3927809850730743,0.4638461538461538,0.4662944582299421,0.4324231324231325,0.3628917378917379,0.378766851704996,0.42660910518053374,0.3844871794871795,0.3844871794871795,0.39089743589743586,0.39089743589743586],[0.893939393939394,0.0,0.5974967061923584,0.5974967061923584,0.6515151515151515,0.8030303030303031,0.3408492531608025,0.3950146860363578,0.3151702786377709,0.4440630363551256,0.47346153846153843,0.41501240694789077,0.39780774780774786,0.4141737891737892,0.43004890298704734,0.3753270538984825,0.42615384615384616,0.36205128205128206,0.4421794871794872,0.3780769230769231],[0.5974967061923584,0.5974967061923584,0.0,0.9755434782608696,0.779891304347826,0.6572463768115943,0.22092245989304812,0.3355263157894737,0.26045883940620784,0.3529693486590038,0.4383333333333333,0.3517025089605735,0.3613516113516113,0.33564814814814814,0.3654066437571592,0.33758503401360546,0.33749999999999997,0.33749999999999997,0.3513888888888889,0.3513888888888889],[0.5974967061923584,0.5974967061923584,0.9755434782608696,0.0,0.779891304347826,0.6572463768115943,0.22092245989304812,0.3355263157894737,0.26045883940620784,0.3529693486590038,0.4383333333333333,0.3517025089605735,0.3613516113516113,0.33564814814814814,0.3654066437571592,0.33758503401360546,0.33749999999999997,0.33749999999999997,0.3513888888888889,0.3513888888888889],[0.6515151515151515,0.6515151515151515,0.779891304347826,0.779891304347826,0.0,0.7166666666666666,0.24364973262032086,0.3625730994152046,0.2534412955465587,0.3740421455938698,0.5511111111111111,0.3593189964157706,0.3815536315536316,0.3549382716049383,0.3582474226804124,0.3579931972789116,0.37138888888888894,0.37138888888888894,0.3575,0.3575],[0.7348484848484849,0.8030303030303031,0.6572463768115943,0.6572463768115943,0.7166666666666666,0.0,0.33293544690603516,0.4328345373237013,0.35675954592363257,0.4720813612801443,0.4955555555555555,0.40098566308243716,0.424013949013949,0.44521604938271614,0.462414089347079,0.4135487528344672,0.46166666666666667,0.39222222222222225,0.44777777777777783,0.3783333333333334],[0.2932302055417549,0.3408492531608025,0.22092245989304812,0.22092245989304812,0.24364973262032086,0.33293544690603516,0.0,0.42595459236326105,0.519281660032434,0.4501209574738986,0.33537051184110006,0.3511904761904762,0.3811688311688312,0.4226791726791727,0.45661512027491413,0.39091350826044696,0.4435714285714286,0.38404761904761914,0.4316666666666667,0.3721428571428572],[0.3437326347543065,0.3950146860363578,0.3355263157894737,0.3355263157894737,0.3625730994152046,0.4328345373237013,0.42595459236326105,0.0,0.6210422505969064,0.6054715408430578,0.5176298589611282,0.6002321981424147,0.5990417219519387,0.5633814929480564,0.6752235982112142,0.6141210870313036,0.6926298589611285,0.623185414516684,0.6661592707258343,0.5967148262813898],[0.2675512310187233,0.3151702786377709,0.26045883940620784,0.26045883940620784,0.2534412955465587,0.35675954592363257,0.519281660032434,0.6210422505969064,0.0,0.47747876478526624,0.39765023418274187,0.4432538882884203,0.40293572691762736,0.47091960327254445,0.5389664167991359,0.43830194799813416,0.509610163592064,0.4455075994895,0.5005603898364079,0.43645782573384384],[0.3927809850730743,0.4440630363551256,0.3529693486590038,0.3529693486590038,0.3740421455938698,0.4720813612801443,0.4501209574738986,0.6054715408430578,0.47747876478526624,0.0,0.4739970700924048,0.5453177962665628,0.6140624625918744,0.5774328249818446,0.6262452509420369,0.6067022963031367,0.621787330316742,0.5523428858722976,0.6070814479638009,0.5376370035193565],[0.4638461538461538,0.47346153846153843,0.4383333333333333,0.4383333333333333,0.5511111111111111,0.4955555555555555,0.33537051184110006,0.5176298589611282,0.39765023418274187,0.4739970700924048,0.0,0.6459293394777266,0.5014430014430014,0.47255291005291,0.4821224022254949,0.4987244897959184,0.5287698412698413,0.5287698412698413,0.49107142857142855,0.49107142857142855],[0.4662944582299421,0.41501240694789077,0.3517025089605735,0.3517025089605735,0.3593189964157706,0.40098566308243716,0.3511904761904762,0.6002321981424147,0.4432538882884203,0.5453177962665628,0.6459293394777266,0.0,0.6390331890331891,0.5035493827160494,0.6357961053837342,0.747874149659864,0.6737301587301587,0.6737301587301587,0.6761111111111111,0.6761111111111111],[0.4324231324231325,0.39780774780774786,0.3613516113516113,0.3613516113516113,0.3815536315536316,0.424013949013949,0.3811688311688312,0.5990417219519387,0.40293572691762736,0.6140624625918744,0.5014430014430014,0.6390331890331891,0.0,0.5609788359788359,0.641065416065416,0.7507756132756134,0.7383333333333333,0.7494444444444444,0.6669047619047618,0.6780158730158728],[0.3628917378917379,0.4141737891737892,0.33564814814814814,0.33564814814814814,0.3549382716049383,0.44521604938271614,0.4226791726791727,0.5633814929480564,0.47091960327254445,0.5774328249818446,0.47255291005291,0.5035493827160494,0.5609788359788359,0.0,0.6396604938271605,0.6092592592592593,0.5807319223985891,0.5112874779541446,0.6521604938271606,0.5827160493827162],[0.378766851704996,0.43004890298704734,0.3654066437571592,0.3654066437571592,0.3582474226804124,0.462414089347079,0.45661512027491413,0.6752235982112142,0.5389664167991359,0.6262452509420369,0.4821224022254949,0.6357961053837342,0.641065416065416,0.6396604938271605,0.0,0.6700963718820862,0.7310714285714286,0.6616269841269843,0.8024999999999999,0.7330555555555555],[0.42660910518053374,0.3753270538984825,0.33758503401360546,0.33758503401360546,0.3579931972789116,0.4135487528344672,0.39091350826044696,0.6141210870313036,0.43830194799813416,0.6067022963031367,0.4987244897959184,0.747874149659864,0.7507756132756134,0.6092592592592593,0.6700963718820862,0.0,0.6887301587301587,0.6887301587301587,0.6577777777777778,0.6577777777777778],[0.3844871794871795,0.42615384615384616,0.33749999999999997,0.33749999999999997,0.37138888888888894,0.46166666666666667,0.4435714285714286,0.6926298589611285,0.509610163592064,0.621787330316742,0.5287698412698413,0.6737301587301587,0.7383333333333333,0.5807319223985891,0.7310714285714286,0.6887301587301587,0.0,0.9305555555555555,0.8952380952380953,0.8257936507936509],[0.3844871794871795,0.36205128205128206,0.33749999999999997,0.33749999999999997,0.37138888888888894,0.39222222222222225,0.38404761904761914,0.623185414516684,0.4455075994895,0.5523428858722976,0.5287698412698413,0.6737301587301587,0.7494444444444444,0.5112874779541446,0.6616269841269843,0.6887301587301587,0.9305555555555555,0.0,0.8257936507936509,0.8952380952380953],[0.39089743589743586,0.4421794871794872,0.3513888888888889,0.3513888888888889,0.3575,0.44777777777777783,0.4316666666666667,0.6661592707258343,0.5005603898364079,0.6070814479638009,0.49107142857142855,0.6761111111111111,0.6669047619047618,0.6521604938271606,0.8024999999999999,0.6577777777777778,0.8952380952380953,0.8257936507936509,0.0,0.9305555555555555],[0.39089743589743586,0.3780769230769231,0.3513888888888889,0.3513888888888889,0.3575,0.3783333333333334,0.3721428571428572,0.5967148262813898,0.43645782573384384,0.5376370035193565,0.49107142857142855,0.6761111111111111,0.6780158730158728,0.5827160493827162,0.7330555555555555,0.6577777777777778,0.8257936507936509,0.8952380952380953,0.9305555555555555,0.0]],"text":[[0.0,0.9869241849852654,0.10077155725139522,0.10077155725139522,0.21423536092400625,0.18484930485370238,0.11485952406610711,0.026606351999003554,0.04196999036915167,0.04552810282603896,0.09469903671258591,0.06457027581756886,0.04558853706077645,0.07186175501759698,0.05926712198262986,0.08134057393531438,0.07195984267815313,0.06994131937860125,0.07295041752698492,0.07084980944331022],[0.9869241849852654,0.0,0.10094971361447957,0.10094971361447957,0.21461411256571267,0.19479582114657437,0.11822595879304142,0.031431134862639765,0.04697768043418556,0.05045290807992317,0.09486645732638288,0.05066102251698107,0.045669134088177965,0.07846104885051958,0.06567808610379935,0.06381878651600714,0.07974378686410247,0.07006497025221756,0.0808415128551317,0.07097506645749081],[0.10077155725139522,0.10094971361447957,0.0,0.6754987171369762,0.32962999680629357,0.28441558623081514,0.01204899478095658,0.1125939289857646,0.01879121423071446,0.03333806573874929,0.13993769585167481,0.03703119056270121,0.03338231885639507,0.05275872730445616,0.04339849644851301,0.046648992214131824,0.05269277252603333,0.05121470385462866,0.053418123405592016,0.05187994794828209],[0.10077155725139522,0.10094971361447957,0.6754987171369762,0.0,0.32962999680629357,0.28441558623081514,0.01204899478095658,0.1125939289857646,0.01879121423071446,0.03333806573874929,0.13993769585167481,0.03703119056270121,0.03338231885639507,0.05275872730445616,0.04339849644851301,0.046648992214131824,0.05269277252603333,0.05121470385462866,0.053418123405592016,0.05187994794828209],[0.21423536092400625,0.21461411256571267,0.32962999680629357,0.32962999680629357,0.0,0.7070403637191788,0.07774060296519911,0.07882364171230868,0.12124167628098138,0.1409307534517757,0.39146495595554054,0.15654278289912438,0.14111782564910358,0.22960225130891157,0.18345943796175998,0.19720033165758155,0.22274933980124478,0.21650106693661944,0.22581563185232498,0.21931326822275912],[0.18484930485370238,0.19479582114657437,0.28441558623081514,0.28441558623081514,0.7070403637191788,0.0,0.08088774904233388,0.08887023677003372,0.12614986133922884,0.14274892354644791,0.26395871083254735,0.13507025392055463,0.12176109425257696,0.22636480914352516,0.18582627738834112,0.17015092217551292,0.22562306450869973,0.18680423040673919,0.22872891528186334,0.1892306900285754],[0.11485952406610711,0.11822595879304142,0.01204899478095658,0.01204899478095658,0.07774060296519911,0.08088774904233388,0.0,0.06808871103145193,0.16534841329513655,0.0997140955196175,0.0813788499294903,0.10019300810682205,0.0903204810047926,0.1207288173263716,0.12647414602569262,0.12621530077926435,0.15356000673577444,0.13856846513770305,0.15567386183603138,0.14036837504758232],[0.026606351999003554,0.031431134862639765,0.1125939289857646,0.1125939289857646,0.07882364171230868,0.08887023677003372,0.06808871103145193,0.0,0.6882582394824935,0.09208711274099618,0.07750226404822264,0.10367812425381774,0.09346219091751043,0.12043884063697838,0.1351788135223297,0.1306055770176497,0.16412887667022508,0.14338843415990205,0.1663882192583364,0.14525095218194986],[0.04196999036915167,0.04697768043418556,0.01879121423071446,0.01879121423071446,0.12124167628098138,0.12614986133922884,0.16534841329513655,0.6882582394824935,0.0,0.14903900786465749,0.119859128675811,0.12210284454812506,0.11007142973371972,0.17963802404666515,0.15721730193077074,0.15381559593673907,0.19088715521799254,0.1688701045879588,0.1935148432157236,0.17106361213982607],[0.04552810282603896,0.05045290807992317,0.03333806573874929,0.03333806573874929,0.1409307534517757,0.14274892354644791,0.0997140955196175,0.09208711274099618,0.14903900786465749,0.0,0.12287581848642727,0.13700620753770992,0.1235062885052339,0.18274206907767832,0.17442799676440227,0.172589684846691,0.2117837139031401,0.18948168391747705,0.21469905685800084,0.19194292183538822],[0.09469903671258591,0.09486645732638288,0.13993769585167481,0.13993769585167481,0.39146495595554054,0.26395871083254735,0.0813788499294903,0.07750226404822264,0.119859128675811,0.12287581848642727,0.0,0.7970795800692779,0.12303892447145691,0.183740578790543,0.15995606385745292,0.1719365827878851,0.19421245381161625,0.18876466031330016,0.1968859167447711,0.19121658458333707],[0.06457027581756886,0.05066102251698107,0.03703119056270121,0.03703119056270121,0.15654278289912438,0.13507025392055463,0.10019300810682205,0.10367812425381774,0.12210284454812506,0.13700620753770992,0.7970795800692779,0.0,0.17695884243139234,0.1871801303505713,0.23005435086246395,0.3434096466944729,0.27932307730986883,0.271487872024968,0.2831681442914488,0.2750143144286141],[0.04558853706077645,0.045669134088177965,0.03338231885639507,0.03338231885639507,0.14111782564910358,0.12176109425257696,0.0903204810047926,0.09346219091751043,0.11007142973371972,0.1235062885052339,0.12303892447145691,0.17695884243139234,0.0,0.16873631930262653,0.2073859246244975,0.22291888371308288,0.25179995266205035,0.2447367900374784,0.25526614562136035,0.2479157541204156],[0.07186175501759698,0.07846104885051958,0.05275872730445616,0.05275872730445616,0.22960225130891157,0.22636480914352516,0.1207288173263716,0.12043884063697838,0.17963802404666515,0.18274206907767832,0.183740578790543,0.1871801303505713,0.16873631930262653,0.0,0.27839789700872325,0.365161818989042,0.43496214749370904,0.400901574308305,0.4908121139294309,0.45453564808966496],[0.05926712198262986,0.06567808610379935,0.04339849644851301,0.04339849644851301,0.18345943796175998,0.18582627738834112,0.12647414602569262,0.1351788135223297,0.15721730193077074,0.17442799676440227,0.15995606385745292,0.23005435086246395,0.2073859246244975,0.27839789700872325,0.0,0.2898044448244013,0.3492645191777779,0.31816869160445627,0.40265544301445466,0.36948560272072517],[0.08134057393531438,0.06381878651600714,0.046648992214131824,0.046648992214131824,0.19720033165758155,0.17015092217551292,0.12621530077926435,0.1306055770176497,0.15381559593673907,0.172589684846691,0.1719365827878851,0.3434096466944729,0.22291888371308288,0.365161818989042,0.2898044448244013,0.0,0.5049115480656129,0.4907484303314399,0.5118619896144572,0.4971229179331714],[0.07195984267815313,0.07974378686410247,0.05269277252603333,0.05269277252603333,0.22274933980124478,0.22562306450869973,0.15356000673577444,0.16412887667022508,0.19088715521799254,0.2117837139031401,0.19421245381161625,0.27932307730986883,0.25179995266205035,0.43496214749370904,0.3492645191777779,0.5049115480656129,0.0,0.9460892329671391,0.8411015022455799,0.7906859941779771],[0.06994131937860125,0.07006497025221756,0.05121470385462866,0.05121470385462866,0.21650106693661944,0.18680423040673919,0.13856846513770305,0.14338843415990205,0.1688701045879588,0.18948168391747705,0.18876466031330016,0.271487872024968,0.2447367900374784,0.400901574308305,0.31816869160445627,0.4907484303314399,0.9460892329671391,0.0,0.7912919667875475,0.8500009099951646],[0.07295041752698492,0.0808415128551317,0.053418123405592016,0.053418123405592016,0.22581563185232498,0.22872891528186334,0.15567386183603138,0.1663882192583364,0.1935148432157236,0.21469905685800084,0.1968859167447711,0.2831681442914488,0.25526614562136035,0.4908121139294309,0.40265544301445466,0.5118619896144572,0.8411015022455799,0.7912919667875475,0.0,0.9446484029118316],[0.07084980944331022,0.07097506645749081,0.05187994794828209,0.05187994794828209,0.21931326822275912,0.1892306900285754,0.14036837504758232,0.14525095218194986,0.17106361213982607,0.19194292183538822,0.19121658458333707,0.2750143144286141,0.2479157541204156,0.45453564808966496,0.36948560272072517,0.4971229179331714,0.7906859941779771,0.8500009099951646,0.9446484029118316,0.0]],"method":"embedding (all-MiniLM-L6-v2) | link: field-level (links uninformative) | order: UPGMA + dendrogram cut","folder":"Horizontal Grid Cells","meta":[{"label":"g118","tags":["tripolar"]},{"label":"g116","tags":["tripolar"]},{"label":"g103","tags":["tripolar"]},{"label":"g104","tags":["tripolar"]},{"label":"g107","tags":["tripolar"]},{"label":"g119","tags":["tripolar"]},{"label":"g120","tags":["spectral-gaussian"]},{"label":"g105","tags":["regular-latitude-longitude"]},{"label":"g101","tags":["linear-spectral-gaussian"]},{"label":"g114","tags":["regular-gaussian"]},{"label":"g112","tags":["tripolar"]},{"label":"g106","tags":["regular-latitude-longitude"]},{"label":"g113","tags":["regular-latitude-longitude"]},{"label":"g117","tags":["hierarchical-discrete-global-grid"]},{"label":"g111","tags":["regular-latitude-longitude"]},{"label":"g100","tags":["regular-latitude-longitude"]},{"label":"g108","tags":["regular-latitude-longitude"]},{"label":"g110","tags":["regular-latitude-longitude"]},{"label":"g115","tags":["regular-latitude-longitude"]},{"label":"g109","tags":["regular-latitude-longitude"]}],"tree":{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"g118","leaf":true,"spectral_index":0,"value":0.0},{"name":"g116","leaf":true,"spectral_index":1,"value":0.0}],"value":0.05956821053767025},{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"g103","leaf":true,"spectral_index":2,"value":0.0},{"name":"g104","leaf":true,"spectral_index":3,"value":0.0}],"value":0.1744789023010771},{"name":"","leaf":false,"children":[{"name":"g107","leaf":true,"spectral_index":4,"value":0.0},{"name":"g119","leaf":true,"spectral_index":5,"value":0.0}],"value":0.2881464848070774}],"value":0.48720418395086773}],"value":0.5973229339437331},{"name":"","leaf":false,"children":[{"name":"g120","leaf":true,"spectral_index":6,"value":0.0},{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"g105","leaf":true,"spectral_index":7,"value":0.0},{"name":"g101","leaf":true,"spectral_index":8,"value":0.0}],"value":0.34534975496029996},{"name":"","leaf":false,"children":[{"name":"g114","leaf":true,"spectral_index":9,"value":0.0},{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"g112","leaf":true,"spectral_index":10,"value":0.0},{"name":"g106","leaf":true,"spectral_index":11,"value":0.0}],"value":0.2784955402264977},{"name":"","leaf":false,"children":[{"name":"g113","leaf":true,"spectral_index":12,"value":0.0},{"name":"","leaf":false,"children":[{"name":"g117","leaf":true,"spectral_index":13,"value":0.0},{"name":"","leaf":false,"children":[{"name":"g111","leaf":true,"spectral_index":14,"value":0.0},{"name":"","leaf":false,"children":[{"name":"g100","leaf":true,"spectral_index":15,"value":0.0},{"name":"","leaf":false,"children":[{"name":"","leaf":false,"children":[{"name":"g108","leaf":true,"spectral_index":16,"value":0.0},{"name":"g110","leaf":true,"spectral_index":17,"value":0.0}],"value":0.061677605738652774},{"name":"","leaf":false,"children":[{"name":"g115","leaf":true,"spectral_index":18,"value":0.0},{"name":"g109","leaf":true,"spectral_index":19,"value":0.0}],"value":0.062398020766306406}],"value":0.16060701684127981}],"value":0.41279240512993065}],"value":0.467227095852213}],"value":0.4999510919610079}],"value":0.5439801394214436}],"value":0.603849723330331}],"value":0.6258169094708897}],"value":0.6612813208460058}],"value":0.7334093871735062}],"value":0.7632889791886096},"clusters":[0,0,1,1,2,2,3,4,4,5,6,6,7,8,9,10,10,10,10,10]};
var EMD_ENTRIES = [{"label":"g118","url":"../Horizontal_Grid_Cells/g118/"},{"label":"g116","url":"../Horizontal_Grid_Cells/g116/"},{"label":"g103","url":"../Horizontal_Grid_Cells/g103/"},{"label":"g104","url":"../Horizontal_Grid_Cells/g104/"},{"label":"g107","url":"../Horizontal_Grid_Cells/g107/"},{"label":"g119","url":"../Horizontal_Grid_Cells/g119/"},{"label":"g120","url":"../Horizontal_Grid_Cells/g120/"},{"label":"g105","url":"../Horizontal_Grid_Cells/g105/"},{"label":"g101","url":"../Horizontal_Grid_Cells/g101/"},{"label":"g114","url":"../Horizontal_Grid_Cells/g114/"},{"label":"g112","url":"../Horizontal_Grid_Cells/g112/"},{"label":"g106","url":"../Horizontal_Grid_Cells/g106/"},{"label":"g113","url":"../Horizontal_Grid_Cells/g113/"},{"label":"g117","url":"../Horizontal_Grid_Cells/g117/"},{"label":"g111","url":"../Horizontal_Grid_Cells/g111/"},{"label":"g100","url":"../Horizontal_Grid_Cells/g100/"},{"label":"g108","url":"../Horizontal_Grid_Cells/g108/"},{"label":"g110","url":"../Horizontal_Grid_Cells/g110/"},{"label":"g115","url":"../Horizontal_Grid_Cells/g115/"},{"label":"g109","url":"../Horizontal_Grid_Cells/g109/"}];
var EMD_SCHEMA  = {"name":"record","children":[{"name":"alias","type":"scalar"},{"name":"description","type":"scalar"},{"name":"grid_mapping","type":"scalar"},{"name":"grid_type","type":"scalar"},{"name":"n_cells","type":"scalar"},{"name":"region","type":"scalar"},{"name":"southernmost_latitude","type":"scalar"},{"name":"temporal_refinement","type":"scalar"},{"name":"truncation_method","type":"scalar"},{"name":"truncation_number","type":"scalar"},{"name":"ui_label","type":"scalar"},{"name":"units","type":"scalar"},{"name":"validation_key","type":"scalar"},{"name":"westernmost_longitude","type":"scalar"},{"name":"x_resolution","type":"scalar"},{"name":"y_resolution","type":"scalar"}]};

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
