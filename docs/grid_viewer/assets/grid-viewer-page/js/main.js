// main.js — orchestrator for the grid-cells table page.
//
// Usage (standalone or in mkdocs):
//   <div id="emd-grid-cells-page"></div>
//   <script type="module" src="assets/grid-cells-page/js/main.js"></script>
// Optional query params: ?base=<url>
//
// Fetches the horizontal_grid_cell collection, derives a table schema, and
// mounts the search + add-a-filter panel + table. Category columns get value
// filters; numeric columns get range filters; text columns (alias) get a
// contains box; the grid id gets a prominent search box.

import { Resolver, DEFAULT_BASE, FOLDER, short } from "./resolver.js";
import { el, clear } from "./dom.js";
import { buildSchema } from "./schema.js";
import { createFilters } from "./filters.js";
import { createTable } from "./table.js";
import { createScatter } from "./scatter.js";

const PARAMS = new URLSearchParams(location.search);
const BASE = (PARAMS.get("base") || DEFAULT_BASE).replace(/\/?$/, "/");

// Per-collection configuration. Each viewer page calls initGridViewer() with
// its own config, so both pages run this same module rather than forking it.
const DEFAULT_CONFIG = {
  folder: FOLDER,                 // registry collection to load
  title: "Horizontal grid cells", // page heading
  colourKey: "grid_type",         // scatter node colour field
  tableTitle: "Grid cells",
  noun: "grid cells",             // used in the count pill
};

let CONFIG = DEFAULT_CONFIG;

function header() {
  return el("header", { class: "gc-header" }, [
    el("a", { class: "eyebrow eyebrow-home", href: "../../" }, "EMD DOCUMENTATION"),
    el("h1", { class: "gc-title" }, CONFIG.title),
  ]);
}

async function main() {
  const mount = document.getElementById("emd-grid-cells-page") || document.body;
  const page = el("div", { class: "emd-page gc-page" });
  mount.appendChild(page);

  page.appendChild(header());

  const shell = el("div", { class: "gc-shell" });
  page.appendChild(shell);
  const spinner = el("div", { class: "page-spinner" }, [
    el("div", { class: "spinner-ring" }),
    el("span", {}, `Loading ${CONFIG.noun}…`),
  ]);
  shell.appendChild(spinner);

  const resolver = new Resolver(BASE);
  let records;
  try {
    records = await resolver.collection(CONFIG.folder);
  } catch (e) {
    clear(shell);
    shell.appendChild(el("div", { class: "page-error" }, `Could not load ${CONFIG.noun}: ${e.message}`));
    return;
  }

  clear(shell);

  if (!records.length) {
    shell.appendChild(el("div", { class: "page-error" }, `No ${CONFIG.noun} were found.`));
    return;
  }

  const { columns, rows } = buildSchema(records);

  // count pill — sits on the table header row and updates as filters change
  const countPill = el("span", { class: "gc-count-pill", dataset: { role: "count" } },
    `${rows.length} ${CONFIG.noun}`);

  // On narrow phone screens skip the PCoA similarity map entirely.
  // The cutoff is 640px — phones fall below, iPad portrait (768px) and up work fine.
  const SIM_MIN_WIDTH = 640;
  const showSimilarity = window.innerWidth >= SIM_MIN_WIDTH;

  // The scatter and the table cross-highlight each other, so both are declared
  // first and referenced lazily inside the callbacks.
  let scatter = null, table;

  if (showSimilarity) {
    scatter = createScatter(columns, rows, {
      colourKey: CONFIG.colourKey,
      onHoverNode: id => table && table.highlight(id),
      onLeaveNode: () => table && table.clearHighlight(),
      onSelectNode: id => table && table.reveal(id),
    });
  }

  table = createTable(columns, rows, {
    folder: CONFIG.folder,
    onHoverRow: id => scatter && scatter.highlight(id),
    onLeaveRow: () => scatter && scatter.clearHighlight(),
    // single click on the row → pin the node in the graph
    onSelectRow: id => scatter && scatter.pin(id),
    // double click on the row → pin AND scroll to the graph
    onDoubleClickRow: id => {
      if (!scatter) return;
      scatter.pin(id);
      if (typeof scatter.root.scrollIntoView === "function") {
        scatter.root.scrollIntoView({ block: "center", behavior: "smooth" });
      }
    },
  });

  // filters — rendered compact when they live in the scatter's aside column
  const filters = createFilters(columns, {
    compact: !!scatter,
    onChange: () => {
      const filtered = rows.filter(filters.test);
      table.update(filtered);
      if (scatter) scatter.setVisible(new Set(filtered.map(r => short(r["@id"]))));
      countPill.textContent = filtered.length === rows.length
        ? `${rows.length} ${CONFIG.noun}`
        : `${filtered.length} of ${rows.length} ${CONFIG.noun}`;
    },
  });

  // ---- view toggle (graph / table) ----
  // The two views were previously stacked. They are now switchable, with the
  // filter panel reparented between the scatter's aside column and a standalone
  // card. The filter DOM node itself is moved (not rebuilt), so filter state,
  // scroll position and focus survive the switch.
  const filterCard = el("div", { class: "gc-filter-card", hidden: "" }, []);

  const scatterWrap = el("div", { class: "gc-view gc-view-graph" });
  if (scatter) scatterWrap.appendChild(scatter.root);

  // table, with a small header strip carrying the live count
  const tableHead = el("div", { class: "gc-table-head" }, [
    el("h2", { class: "gc-table-title" }, CONFIG.tableTitle),
    countPill,
  ]);
  const tableCard = el("div", { class: "card gc-table-card" }, [tableHead, table.root]);

  let mode = "graph";
  function setMode(next) {
    if (!scatter) return;               // no graph on narrow screens
    mode = next;
    const graph = next === "graph";
    // Exclusive views: exactly one of the two is visible at a time.
    scatterWrap.hidden = !graph;
    tableCard.hidden = graph;
    btnGraph.setAttribute("aria-pressed", String(graph));
    btnTable.setAttribute("aria-pressed", String(!graph));
    if (graph) {
      scatter.setAside(filters.root);   // move filters back into the aside
      filterCard.hidden = true;
    } else {
      filterCard.appendChild(filters.root);
      filterCard.hidden = false;
    }
  }

  const btnGraph = el("button", {
    class: "gc-view-btn", type: "button", "aria-pressed": "true",
    onclick: () => setMode("graph"),
  }, "Graph");
  const btnTable = el("button", {
    class: "gc-view-btn", type: "button", "aria-pressed": "false",
    onclick: () => setMode("table"),
  }, "Table");
  const viewToggle = el("div", { class: "gc-view-toggle", role: "group", "aria-label": "View mode" },
    [btnGraph, btnTable]);

  if (scatter) {
    shell.appendChild(viewToggle);
    shell.appendChild(scatterWrap);
    shell.appendChild(filterCard);
    shell.appendChild(tableCard);
    // establish the initial view through the same path as a click, so the
    // hidden/aria-pressed state can never drift from the declared default
    setMode("graph");
  } else {
    // No similarity map (narrow screens): filters get their own card, the
    // toggle is pointless, and the table is always visible.
    filterCard.hidden = false;
    filterCard.appendChild(filters.root);
    shell.appendChild(filterCard);
    shell.appendChild(tableCard);
  }
}

// Entry point. Each viewer page calls this with its own collection config:
//
//   import { initGridViewer } from "../assets/grid-viewer-page/js/main.js";
//   initGridViewer({ folder: "vertical_computational_grid", ... });
//
export function initGridViewer(config = {}) {
  CONFIG = { ...DEFAULT_CONFIG, ...config };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", main);
  else main();
}
