// components/grids.js — grid summary cards.
//
// Walks the model's component_configs, resolves each one's
// horizontal_computational_grid and vertical_computational_grid (and the
// grid cells under each horizontal grid's subgrids), then renders a compact
// card per distinct grid so a reader can see resolutions, level counts and
// arrangements at a glance.

import { el, card } from "../dom.js";
import { Resolver, short } from "../resolver.js";
import { realmLabel } from "../crs.js";

const clean = v => (v == null ? "" : String(v).trim());
const isNone = v => { const s = clean(v).toLowerCase(); return !s || s === "none"; };
const vocabLabel = v => Array.isArray(v) ? v.map(short).join(", ") : short(v);
const REALM_OF = id => String(id).split("_")[0];

function hGridCard(id, doc, cells, usedBy) {
  const rows = [];
  if (!isNone(doc.arrangement)) rows.push(["Arrangement", vocabLabel(doc.arrangement)]);
  const nSub = (doc.horizontal_subgrids || []).length;
  if (nSub) rows.push(["Subgrids", String(nSub)]);
  // Merge grid-cell facts (resolution, type, cell count) from resolved cells.
  const cell = cells[0];
  if (cell) {
    if (!isNone(cell.grid_type)) rows.push(["Grid type", vocabLabel(cell.grid_type)]);
    if (cell.x_resolution && cell.y_resolution)
      rows.push(["Resolution", `${cell.x_resolution} × ${cell.y_resolution}° `]);
    if (Number.isFinite(cell.n_cells)) rows.push(["Cells", cell.n_cells.toLocaleString()]);
    const region = (cell.region || []).filter(x => !isNone(x)).map(short);
    if (region.length) rows.push(["Region", region.join(", ")]);
  }
  return gridCard("horizontal", id, doc, rows, usedBy);
}

function vGridCard(id, doc, usedBy) {
  const rows = [];
  if (Number.isFinite(doc.n_z)) rows.push(["Levels", String(doc.n_z)]);
  if (!isNone(doc.vertical_coordinate)) rows.push(["Coordinate", vocabLabel(doc.vertical_coordinate)]);
  if (Number.isFinite(doc.top_layer_thickness)) rows.push(["Top layer", `${doc.top_layer_thickness} m`]);
  if (Number.isFinite(doc.bottom_layer_thickness)) rows.push(["Bottom layer", `${doc.bottom_layer_thickness} m`]);
  if (Number.isFinite(doc.total_thickness)) rows.push(["Total depth", `${(doc.total_thickness / 1000).toFixed(1)} km`]);
  return gridCard("vertical", id, doc, rows, usedBy);
}

function gridCard(kind, id, doc, rows, usedBy) {
  const title = doc.ui_label && !isNone(doc.ui_label) ? doc.ui_label : id;
  return el("div", { class: `grid-card grid-${kind}` }, [
    el("div", { class: "grid-card-head" }, [
      el("span", { class: `grid-badge grid-badge-${kind}` }, kind === "horizontal" ? "H" : "V"),
      el("code", { class: "grid-id" }, id),
      usedBy.size ? el("span", { class: "grid-usedby" }, [...usedBy].map(realmLabel).sort().join(", ")) : null,
    ]),
    !isNone(doc.description) ? el("p", { class: "grid-desc" }, doc.description) : null,
    rows.length ? el("dl", { class: "kv kv-tight" }, rows.flatMap(([k, v]) => [
      el("dt", {}, k), el("dd", {}, v),
    ])) : null,
  ]);
}

export async function mountGrids(root, model, { base }) {
  const resolver = new Resolver(base);
  const configs = model.model_components || model.component_configs || [];
  if (!configs.length) return;

  // grid id -> { doc, usedBy:Set<realm>, cells:[] }
  const hGrids = new Map(), vGrids = new Map();
  const touch = (map, id) => { if (!map.has(id)) map.set(id, { doc: null, usedBy: new Set(), cells: [] }); return map.get(id); };

  await Promise.all(configs.map(async ccId => {
    const realm = REALM_OF(ccId);
    let cc;
    try { cc = await resolver.fetchDoc("component_config", ccId); } catch (_) { return; }

    const hId = short(cc.horizontal_computational_grid);
    const vId = short(cc.vertical_computational_grid);

    if (hId) {
      const rec = touch(hGrids, hId); rec.usedBy.add(realm);
      if (!rec.doc) {
        try {
          rec.doc = await resolver.fetchDoc("horizontal_computational_grid", hId);
          // resolve the first subgrid's grid cell for resolution/type facts
          const sg = (rec.doc.horizontal_subgrids || [])[0];
          if (sg) {
            try {
              const sub = await resolver.fetchDoc("horizontal_subgrid", short(sg));
              const gcId = short(sub.horizontal_grid_cell);
              if (gcId) rec.cells.push(await resolver.fetchDoc("horizontal_grid_cell", gcId));
            } catch (_) {}
          }
        } catch (_) { rec.doc = { "@id": hId, description: "" }; }
      }
    }
    if (vId) {
      const rec = touch(vGrids, vId); rec.usedBy.add(realm);
      if (!rec.doc) {
        try { rec.doc = await resolver.fetchDoc("vertical_computational_grid", vId); }
        catch (_) { rec.doc = { "@id": vId, description: "" }; }
      }
    }
  }));

  if (!hGrids.size && !vGrids.size) return;

  const grid = el("div", { class: "grid-cards" });
  [...hGrids.entries()].sort((a, b) => a[0].localeCompare(b[0]))
    .forEach(([id, r]) => grid.appendChild(hGridCard(id, r.doc || {}, r.cells, r.usedBy)));
  [...vGrids.entries()].sort((a, b) => a[0].localeCompare(b[0]))
    .forEach(([id, r]) => grid.appendChild(vGridCard(id, r.doc || {}, r.usedBy)));

  root.appendChild(card("Grids", [grid], {
    sub: "Horizontal (H) and vertical (V) computational grids used by this model's components.",
    extraClass: "grids",
  }));
}
