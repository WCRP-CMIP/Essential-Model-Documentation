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
import { mountComponents } from "./components/components-grid.js";
import { mountReferences } from "./components/references.js";
import { mountCrsDiagram } from "./components/crs-diagram.js";
import { mountHierarchy } from "./components/hierarchy.js";

const PARAMS = new URLSearchParams(location.search);
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

  let current = norm(PARAMS.get("model") || PARAMS.get("id")) || "cnrm-esm2-1e";

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
    const renderHeader = list => { clear(headerHost); mountHeader(headerHost, model, { models: list, current, onModelChange: load }); };
    renderHeader(models);
    window._rerenderPicker = list => { models = list; if (current) renderHeader(list); };

    // body grid
    const body = el("div", { class: "page-body" }); shell.appendChild(body);
    const colMain = el("div", { class: "col-main" });
    const colSide = el("div", { class: "col-side" });
    body.appendChild(colMain); body.appendChild(colSide);

    mountOverview(colMain, model);
    mountCrsDiagram(colMain, model);
    mountComponents(colMain, model, { base: BASE });
    mountReferences(colSide, model);

    // hierarchy spans full width below
    const full = el("div", { class: "page-full" }); shell.appendChild(full);
    mountHierarchy(full, { modelId: current, base: BASE, depth: DEPTH });
  }

  window.addEventListener("popstate", () => {
    const id = norm(new URLSearchParams(location.search).get("model"));
    if (id && id !== current) load(id);
  });

  load(current);
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", main);
else main();
