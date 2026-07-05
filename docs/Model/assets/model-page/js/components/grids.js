// components/grids.js — grid summary cards.
//
// Walks the model's component_configs, resolves each one's
// horizontal_computational_grid and vertical_computational_grid, and (for
// horizontal grids) every horizontal_subgrid and its grid cell. Renders a
// compact card per distinct grid: arrangement + a list of subgrids (each with
// its variable type, grid type and resolution) for H grids; level/coordinate
// facts for V grids.

import { el, card, clampedMd } from "../dom.js";
import { Resolver, short } from "../resolver.js";
import { realmLabel, realmColor } from "../crs.js";

const clean = v => (v == null ? "" : String(v).trim());
const isNone = v => { const s = clean(v).toLowerCase(); return !s || s === "none"; };
const vocabLabel = v => Array.isArray(v) ? v.map(short).join(", ") : short(v);
const REALM_OF = id => String(id).split("_")[0];

// One line describing a subgrid: name · variable type · grid type · resolution
function subgridRow(sg) {
  const bits = [];
  const varType = (sg.doc?.cell_variable_type || []).filter(x => !isNone(x)).map(short);
  if (varType.length) bits.push(varType.join("/"));
  const cell = sg.cell;
  if (cell) {
    if (!isNone(cell.grid_type)) bits.push(vocabLabel(cell.grid_type));
    if (cell.x_resolution && cell.y_resolution) bits.push(`${cell.x_resolution}×${cell.y_resolution}°`);
    if (Number.isFinite(cell.n_cells)) bits.push(`${cell.n_cells.toLocaleString()} cells`);
  }
  return el("li", { class: "subgrid-row" }, [
    el("code", { class: "subgrid-id" }, sg.id),
    bits.length ? el("span", { class: "subgrid-meta" }, bits.join(" · ")) : null,
  ]);
}

function hGridCard(id, doc, subgrids, usedBy) {
  const rows = [];
  if (!isNone(doc.arrangement)) rows.push(["Arrangement", vocabLabel(doc.arrangement)]);

  const body = [
    clampedMd(doc.description, { lines: 2, cls: "grid-desc" }),
    rows.length ? el("dl", { class: "kv kv-tight" }, rows.flatMap(([k, v]) => [
      el("dt", {}, k), el("dd", {}, v),
    ])) : null,
    subgrids.length ? el("details", { class: "subgrid-block" }, [
      el("summary", { class: "subgrid-head" }, subgrids.length === 1 ? "1 subgrid" : `${subgrids.length} subgrids`),
      el("ul", { class: "subgrid-list" }, subgrids.map(subgridRow)),
    ]) : null,
  ];
  return gridCard("horizontal", id, doc, body, usedBy);
}

function vGridCard(id, doc, usedBy) {
  const rows = [];
  if (Number.isFinite(doc.n_z)) rows.push(["Levels", String(doc.n_z)]);
  if (!isNone(doc.vertical_coordinate)) rows.push(["Coordinate", vocabLabel(doc.vertical_coordinate)]);

  // Layer thicknesses grouped into a collapsed "Layer info" box.
  const layerRows = [];
  if (Number.isFinite(doc.top_layer_thickness)) layerRows.push(["Top layer", `${doc.top_layer_thickness} m`]);
  if (Number.isFinite(doc.bottom_layer_thickness)) layerRows.push(["Bottom layer", `${doc.bottom_layer_thickness} m`]);
  if (Number.isFinite(doc.total_thickness)) layerRows.push(["Total depth", `${(doc.total_thickness / 1000).toFixed(1)} km`]);

  const body = [
    clampedMd(doc.description, { lines: 2, cls: "grid-desc" }),
    rows.length ? el("dl", { class: "kv kv-tight" }, rows.flatMap(([k, v]) => [
      el("dt", {}, k), el("dd", {}, v),
    ])) : null,
    layerRows.length ? el("details", { class: "subgrid-block" }, [
      el("summary", { class: "subgrid-head" }, "Layer info"),
      el("dl", { class: "kv kv-tight" }, layerRows.flatMap(([k, v]) => [
        el("dt", {}, k), el("dd", {}, v),
      ])),
    ]) : null,
  ];
  return gridCard("vertical", id, doc, body, usedBy);
}

function gridCard(kind, id, doc, body, usedBy) {
  const realms = [...usedBy];
  return el("div", { class: `grid-card grid-${kind}` }, [
    el("div", { class: "grid-card-head" }, [
      el("span", { class: `grid-badge grid-badge-${kind}` }, kind === "horizontal" ? "H" : "V"),
      el("code", { class: "grid-id" }, id),
      realms.length ? el("span", { class: "grid-usedby" },
        realms.sort().map(r => el("span", { class: "usedby-tag", style: `--realm:${realmColor(r)}` }, realmLabel(r)))
      ) : null,
    ]),
    ...body.filter(Boolean),
  ]);
}

export async function mountGrids(root, model, { base }) {
  const resolver = new Resolver(base);
  const configs = model.model_components || model.component_configs || [];
  if (!configs.length) return;

  // grid id -> { doc, usedBy:Set<realm>, subgrids:[{id,doc,cell}] }
  const hGrids = new Map(), vGrids = new Map();
  const touch = (map, id) => { if (!map.has(id)) map.set(id, { doc: null, usedBy: new Set(), subgrids: [] }); return map.get(id); };

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
          // resolve every subgrid and its grid cell
          const sgIds = (rec.doc.horizontal_subgrids || []).map(short).filter(Boolean);
          rec.subgrids = await Promise.all(sgIds.map(async sgId => {
            const entry = { id: sgId, doc: null, cell: null };
            try {
              entry.doc = await resolver.fetchDoc("horizontal_subgrid", sgId);
              const gcId = short(entry.doc.horizontal_grid_cell);
              if (gcId) { try { entry.cell = await resolver.fetchDoc("horizontal_grid_cell", gcId); } catch (_) {} }
            } catch (_) {}
            return entry;
          }));
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
    .forEach(([id, r]) => grid.appendChild(hGridCard(id, r.doc || {}, r.subgrids, r.usedBy)));
  [...vGrids.entries()].sort((a, b) => a[0].localeCompare(b[0]))
    .forEach(([id, r]) => grid.appendChild(vGridCard(id, r.doc || {}, r.usedBy)));

  root.appendChild(card("Grids", [grid], {
    sub: "Horizontal (H) and vertical (V) computational grids used by this model's components.",
    extraClass: "grids",
  }));
}
