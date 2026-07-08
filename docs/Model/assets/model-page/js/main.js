// main.js — orchestrator. ?model=<id> → fetch model → mount all components.
//
// Usage (in mkdocs or standalone):
//   <div id="emd-model-page"></div>
//   <script type="module" src="assets/model-page/js/main.js"></script>
// Optional query params: ?model=<id>&base=<url>&depth=<n>

import { Resolver, DEFAULT_BASE } from "./resolver.js";
import { el, clear } from "./dom.js";
import { mountHeader } from "./components/header.js";
import { mountOverview } from "./components/overview.js";
import { mountModelFamily, mountComponentsDetail } from "./components/linked-info.js";
import { mountGrids } from "./components/grids.js";
import { mountReferences } from "./components/references.js";
import { mountCrsDiagram } from "./components/crs-diagram.js";
import { mountHierarchy } from "./components/hierarchy.js";
import { mountRawJson } from "./components/raw-json.js";

const PARAMS = new URLSearchParams(location.search);
<<<<<<< HEAD
=======
const HAD_MODEL_PARAM = !!(PARAMS.get("model") || PARAMS.get("id"));   // was a model requested in the URL?
>>>>>>> 183310cba7594af95d231d50e4a90f156e1095e8
const BASE = (PARAMS.get("base") || DEFAULT_BASE).replace(/\/?$/, "/");
const DEPTH = parseInt(PARAMS.get("depth"), 10) || 8;
const FALLBACK = ["access-esm1-6", "awi-esm3-4-2-veg-hr", "canesm5-1", "canesm6-0-mr",
  "cnrm-esm2-1e", "ec-earth3-esm-1-1", "ukcm2-0-ll", "ukcm2a-0-hh"];

const norm = s => (s || "").trim().replace(/^model\//, "").replace(/\.json$/i, "");

function setQuery(id) {
  const p = new URLSearchParams(location.search);
  p.set("model", id);
  try { history.replaceState(null, "", location.pathname + "?" + p.toString()); } catch (_) {}
}

async function main() {
  const mount = document.getElementById("emd-model-page") || document.body;
  const resolver = new Resolver(BASE);

  // model list for the picker (async, non-blocking)
  let models = FALLBACK.slice();
  resolver.modelList().then(list => { if (list.length) { models = list; if (window._rerenderPicker) window._rerenderPicker(list); } }).catch(() => {});

  let current = norm(PARAMS.get("model") || PARAMS.get("id")) || "ec-earth3-esm-1-1";

<<<<<<< HEAD
=======
  // Show the "click here to change model" nudge only on a first visit with no
  // model in the URL; a single timer removes it 3s after it first appears.
  let pickerHintActive = !HAD_MODEL_PARAM;
  let hintTimerStarted = false;

>>>>>>> 183310cba7594af95d231d50e4a90f156e1095e8
  async function load(id) {
    current = norm(id);
    setQuery(current);
    clear(mount);
    const shell = el("div", { class: "emd-page loading" });
    mount.appendChild(shell);
    const spinner = el("div", { class: "page-spinner" }, [el("div", { class: "spinner-ring" }), el("span", {}, `Loading ${current}…`)]);
    shell.appendChild(spinner);

    let model;
    try { model = await resolver.model(current); }
    catch (e) {
      clear(shell); shell.classList.remove("loading");
      shell.appendChild(el("div", { class: "page-error" }, `Could not load model “${current}”: ${e.message}`));
      return;
    }

    clear(shell); shell.classList.remove("loading");

    // header (with picker)
    const headerHost = el("div"); shell.appendChild(headerHost);
<<<<<<< HEAD
    const renderHeader = list => { clear(headerHost); mountHeader(headerHost, model, { models: list, current, onModelChange: load }); };
    renderHeader(models);
    window._rerenderPicker = list => { models = list; if (current) renderHeader(list); };

=======
    const renderHeader = list => { clear(headerHost); mountHeader(headerHost, model, { models: list, current, onModelChange: load, pickerHint: pickerHintActive }); };
    renderHeader(models);
    window._rerenderPicker = list => { models = list; if (current) renderHeader(list); };

    if (pickerHintActive && !hintTimerStarted) {
      hintTimerStarted = true;
      setTimeout(() => {
        pickerHintActive = false;
        document.querySelectorAll(".picker-hint").forEach(n => n.remove());
      }, 4000);   // fade in 1s + hold 2s + fade out 1s
    }

>>>>>>> 183310cba7594af95d231d50e4a90f156e1095e8
    // body — single column
    const body = el("div", { class: "page-body" }); shell.appendChild(body);
    const colMain = el("div", { class: "col-main" });
    body.appendChild(colMain);

    mountOverview(colMain, model);
    mountCrsDiagram(colMain, model);
    mountReferences(colMain, model);

    // full-width stack below, in order:
    //   model family → schema (hierarchy) → components in detail → grids → raw JSON
    const full = el("div", { class: "page-full" }); shell.appendChild(full);

    await mountModelFamily(full, model, { base: BASE });
    mountHierarchy(full, { modelId: current, base: BASE, depth: DEPTH });
    await mountComponentsDetail(full, model, { base: BASE });
    await mountGrids(full, model, { base: BASE });
    mountRawJson(full, model, { base: BASE });   // always the very last section
  }

  window.addEventListener("popstate", () => {
    const id = norm(new URLSearchParams(location.search).get("model"));
    if (id && id !== current) load(id);
  });

  load(current);
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", main);
else main();
