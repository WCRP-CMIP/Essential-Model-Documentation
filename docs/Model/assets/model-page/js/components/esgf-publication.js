// components/esgf-publication.js — one "ESGF Publication Data" box.
//
// Loads the model's ESGF datasets once (by validation_key) and composes every
// arrow-derived view as a titled subsection of a single collapsible card:
//   Dataset submissions · Simulated start dates · Output grids · Frequencies · Variables
// Subsection titles stand in for captions, so no per-subsection sub-text.

import { el, card } from "../dom.js";
import { Resolver } from "../resolver.js";
import { loadDatasetsForBox } from "../esgf.js";
import { cumulativeChartNode } from "./cumulative-chart.js";
import { outputGridsNode } from "./output-grids.js";
import { frequenciesNode, variablesNode } from "./dataset-facets.js";

function subsection(title, node, { first = false, collapsed = false } = {}) {
  const wrap = first ? "" : "border-top:1px solid var(--line);margin-top:1.1rem;padding-top:1.1rem;";
  const titleStyle = "font-size:.95rem;font-weight:700;color:var(--ink)";
  if (collapsed) {
    return el("details", { style: wrap }, [
      el("summary", { style: `cursor:pointer;margin-bottom:.55rem;${titleStyle}` }, title),
      node,
    ]);
  }
  return el("section", { style: wrap }, [
    title ? el("h3", { style: `margin:0 0 .55rem;${titleStyle}` }, title) : null,
    node,
  ]);
}

// Headline totals shown above the publications graph.
function summaryNode(rows) {
  const distinct = key => new Set(rows.map(r => r[key]).filter(v => v != null && v !== "")).size;
  const items = [
    ["Datasets", rows.length],
    ["Variables", distinct("variable_id")],
    ["Activities", distinct("activity_id")],
    ["Experiments", distinct("experiment_id")],
    ["Institutions", distinct("institution_id")],
  ];
  return el("div", { style: "display:flex;flex-wrap:wrap;justify-content:center;gap:1.6rem;margin-bottom:.7rem" },
    items.map(([label, n]) => el("div", { style: "text-align:center" }, [
      el("div", { style: "font-size:1.4rem;font-weight:750;color:var(--accent);line-height:1" }, n.toLocaleString()),
      el("div", { style: "font-size:.62rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin-top:.2rem" }, label),
    ])),
  );
}

export async function mountEsgfPublication(root, model, { base, esgfRoot } = {}) {
  const rows = await loadDatasetsForBox("ESGF Publication", model, esgfRoot);
  if (!rows) return;

  const resolver = base ? new Resolver(base) : null;
  const subsEl = el("div", {});
  let first = true;
  const add = (title, node, opts = {}) => {
    if (!node) return;
    subsEl.appendChild(subsection(title, node, { first, ...opts }));
    first = false;
  };

  add("", el("div", {}, [summaryNode(rows), cumulativeChartNode(rows, "updated")]));
  add("Output grids", await outputGridsNode(rows, resolver));
  add("Frequencies", frequenciesNode(rows));
  add("Variables", variablesNode(rows), { collapsed: true });

  if (!subsEl.children.length) return;
  root.appendChild(card("ESGF Publication", [subsEl], { extraClass: "esgf-publication" }));
}
