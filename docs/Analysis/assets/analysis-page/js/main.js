// main.js — orchestrator for the Analysis page.
//
// Loads three collections from the EMD site (grid cells, models, and the
// horizontal-computational-grid records needed to resolve models → grid cells),
// builds the model-to-grid link list, and mounts the scatter visualization.

import { el, clear } from "./dom.js";
import { Resolver, short } from "./resolver.js";
import { collectAllLinks } from "./model-links.js";
import { createAnalysisScatter } from "./scatter.js";

const MOUNT_ID = "emd-analysis-page";
const DEBUG = new URLSearchParams(location.search).has("debug");

// Optional base override via ?base=... (matches the grid_cells + Model pages).
const params = new URLSearchParams(location.search);
const base = params.get("base") || undefined;

function header() {
  return el("header", { class: "an-header" }, [
    el("div", { class: "an-header-titles" }, [
      el("h1", { class: "an-title" }, "EMD Horizontal Computational Grid Cell - Model Mapping"),
    ]),
    // dark-mode toggle is appended here by index.html's boot script
  ]);
}

function statusMessage(text) {
  return el("div", { class: "an-status" }, text);
}

function errorBlock(err) {
  return el("div", { class: "an-error" }, [
    el("h3", {}, "Could not load Analysis data"),
    el("p", {}, err.message || String(err)),
    el("p", { class: "an-error-hint" },
      "Check the browser console for details. If the site's data isn't " +
      "reachable, this page can't render."),
  ]);
}

async function boot() {
  const mount = document.getElementById(MOUNT_ID);
  if (!mount) return;
  clear(mount);
  mount.appendChild(header());
  const statusEl = statusMessage("Loading grid cells and models…");
  mount.appendChild(statusEl);

  const resolver = new Resolver(base);

  let gridRows = [], models = [], links = [];
  try {
    // Load grid cells and models in parallel.
    statusEl.textContent = "Loading grid cells and models…";
    [gridRows, models] = await Promise.all([
      resolver.collection("horizontal_grid_cell"),
      resolver.collection("model"),
    ]);

    if (DEBUG) {
      console.log(`[analysis] loaded ${gridRows.length} grid cells, ${models.length} models`);
    }

    if (!gridRows.length) throw new Error("No grid cells found in horizontal_grid_cell collection.");
    if (!models.length) throw new Error("No models found in model collection.");

    // Extract links (fetches horizontal_computational_grid records as needed).
    statusEl.textContent = "Extracting model → grid links…";
    const result = await collectAllLinks(models, resolver, { debug: DEBUG });
    links = result.links;
    if (DEBUG) {
      console.log(`[analysis] ${links.length} links, ${result.modelsWithLinks} models with links, ${result.modelsSkipped} skipped`);
    }
  } catch (err) {
    clear(statusEl);
    mount.appendChild(errorBlock(err));
    console.error("[analysis] boot failed:", err);
    return;
  }

  // Remove status; mount the scatter.
  statusEl.remove();
  const { root } = createAnalysisScatter({ gridRows, models, links });
  mount.appendChild(root);
}

boot();
