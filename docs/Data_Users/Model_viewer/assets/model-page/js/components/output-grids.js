// components/output-grids.js — "Output grids" node for the ESGF Publication box.
//
// Summarises the output grids used (`grid_label`), each resolved to its EMD
// horizontal_grid_cell record for grid type / cell count / region, and linked
// to its source on GitHub. Returns a node (no card wrapper); the orchestrator
// gives it a subsection title.

import { el } from "../dom.js";
import { short } from "../resolver.js";

const clean = v => (v == null ? "" : String(v).trim());
const isNone = v => { const s = clean(v).toLowerCase(); return !s || s === "none"; };
const vocabLabel = v => (Array.isArray(v) ? v.map(short).join(", ") : short(v));
const num = v => { const n = Number(v); return Number.isFinite(n) ? n : null; };

const GH_BASE = "https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/src-data";
const gridCellUrl = code => (code ? `${GH_BASE}/horizontal_grid_cell/${code}.json` : null);

const stat = (n, one, many) => el("div", { style: "text-align:center" }, [
  el("div", { style: "font-size:1rem;font-weight:750;line-height:1;color:var(--accent)" }, n.toLocaleString()),
  el("div", { style: "font-size:.58rem;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin-top:.15rem" }, n === 1 ? one : many),
]);

function gridCard(agg, doc) {
  const facts = [];
  if (doc) {
    if (!isNone(doc.grid_type)) facts.push(["Grid type", vocabLabel(doc.grid_type)]);
    const nc = num(doc.n_cells);
    if (nc != null) facts.push(["Cells", nc.toLocaleString()]);
    if (!isNone(doc.region)) facts.push(["Region", vocabLabel(doc.region)]);
  }
  return el("div", { class: "grid-card grid-output" }, [
    el("div", { class: "grid-card-head" }, [
      el("code", { class: "grid-id" }, agg.label),
      gridCellUrl(agg.label) ? el("a", {
        class: "view-grid-btn", href: gridCellUrl(agg.label),
        target: "_blank", rel: "noopener", title: `Open grid cell ${agg.label}.json on GitHub`,
      }, "view grid ↗") : null,
    ]),
    facts.length ? el("dl", { class: "kv kv-tight" }, facts.flatMap(([k, v]) => [el("dt", {}, k), el("dd", {}, v)])) : null,
    el("div", { style: "display:flex;gap:.9rem;flex-wrap:wrap;margin-top:.5rem" }, [
      stat(agg.datasets, "dataset", "datasets"),
      stat(agg.vars.size, "variable", "variables"),
      stat(agg.exps.size, "experiment", "experiments"),
      agg.retracted ? stat(agg.retracted, "retracted", "retracted") : null,
    ]),
  ]);
}

export async function outputGridsNode(rows, resolver) {
  const byGrid = new Map();
  for (const r of rows) {
    const g = clean(r.grid_label) || "(unlabelled)";
    let e = byGrid.get(g);
    if (!e) { e = { label: g, datasets: 0, retracted: 0, vars: new Set(), exps: new Set() }; byGrid.set(g, e); }
    e.datasets++;
    if (r.retracted) e.retracted++;
    if (r.variable_id) e.vars.add(r.variable_id);
    if (r.experiment_id) e.exps.add(r.experiment_id);
  }
  if (!byGrid.size) return null;
  const aggs = [...byGrid.values()].sort((a, b) => b.datasets - a.datasets || a.label.localeCompare(b.label));

  const docs = await Promise.all(aggs.map(async a => {
    if (!resolver || a.label === "(unlabelled)") return null;
    try { return await resolver.fetchDoc("horizontal_grid_cell", a.label); }
    catch (_) { return null; }
  }));

  return el("div", { class: "grid-cards" }, aggs.map((a, i) => gridCard(a, docs[i])));
}
