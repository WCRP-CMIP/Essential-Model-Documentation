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

import { Resolver, DEFAULT_BASE, FOLDER } from "./resolver.js";
import { el, clear } from "./dom.js";
import { buildSchema } from "./schema.js";
import { createFilters } from "./filters.js";
import { createTable } from "./table.js";

const PARAMS = new URLSearchParams(location.search);
const BASE = (PARAMS.get("base") || DEFAULT_BASE).replace(/\/?$/, "/");

function header() {
  return el("header", { class: "gc-header" }, [
    el("a", { class: "eyebrow eyebrow-home", href: "../" }, "EMD DOCUMENTATION"),
    el("h1", { class: "gc-title" }, "Horizontal grid cells"),
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
    el("span", {}, "Loading grid cells…"),
  ]);
  shell.appendChild(spinner);

  const resolver = new Resolver(BASE);
  let records;
  try {
    records = await resolver.collection(FOLDER);
  } catch (e) {
    clear(shell);
    shell.appendChild(el("div", { class: "page-error" }, `Could not load grid cells: ${e.message}`));
    return;
  }

  clear(shell);

  if (!records.length) {
    shell.appendChild(el("div", { class: "page-error" }, "No grid-cell records were found."));
    return;
  }

  const { columns, rows } = buildSchema(records);

  // count pill — sits on the table header row and updates as filters change
  const countPill = el("span", { class: "gc-count-pill", dataset: { role: "count" } },
    `${rows.length} grid cells`);

  // table (built first so filters can call update)
  const table = createTable(columns, rows);

  // filters
  const filters = createFilters(columns, {
    onChange: () => {
      const filtered = rows.filter(filters.test);
      table.update(filtered);
      countPill.textContent = filtered.length === rows.length
        ? `${rows.length} grid cells`
        : `${filtered.length} of ${rows.length} grid cells`;
    },
  });

  // filter panel (search + add-filter + active filters)
  shell.appendChild(el("div", { class: "gc-filter-card" }, [filters.root]));

  // table, with a small header strip carrying the live count
  const tableHead = el("div", { class: "gc-table-head" }, [
    el("h2", { class: "gc-table-title" }, "Grid cells"),
    countPill,
  ]);
  shell.appendChild(el("div", { class: "card gc-table-card" }, [tableHead, table.root]));
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", main);
else main();
