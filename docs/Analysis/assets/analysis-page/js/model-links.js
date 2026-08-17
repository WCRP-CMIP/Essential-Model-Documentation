// model-links.js — walk model records to extract (model → grid cell) links,
// tagged by realm (atmosphere / ocean / land-surface / sea-ice / etc.).
//
// Model schema (EMD site):
//   model.model_components   -> ["atmosphere_canam5-1_h108_v114", ...]
//   model.component_configs  -> same, legacy alias
//
// Component id format: <realm>_<comp_name>_h<n>_v<n>
//   - realm can be "atmosphere", "ocean-biogeochemistry", "sea_ice",
//     "land_surface", etc. (mixed underscore/hyphen conventions on the site).
//   - The h### and v### are always the final two underscore-delimited chunks.
//
// From h### we fetch horizontal_computational_grid/<h_id>.json → look at
// horizontal_subgrids[0] (a string like "g127-mass"), strip the "-mass" /
// "-x-velocity" / "-y-velocity" suffix → that's the grid cell id (g###).
//
// Same traversal as docs/Model/assets/model-page/js/components/hierarchy.js.

import { short } from "./resolver.js";

// Canonical realm names (matches the Model page's crs.js). Any variant with
// underscores instead of hyphens gets folded onto these.
const REALM_CANONICAL = [
  "atmosphere",
  "atmospheric-chemistry",
  "aerosol",
  "land-surface",
  "land-ice",
  "ocean",
  "ocean-biogeochemistry",
  "sea-ice",
  "river",
  "iceberg",
];

// Build a lookup that maps every valid form (dashes and underscores) back to
// the canonical hyphenated form.
const REALM_LOOKUP = (() => {
  const m = new Map();
  for (const r of REALM_CANONICAL) {
    m.set(r, r);
    m.set(r.replace(/-/g, "_"), r);
  }
  return m;
})();

export function normaliseRealm(raw) {
  if (raw == null) return "unknown";
  const s = String(raw).trim().toLowerCase();
  return REALM_LOOKUP.get(s) || REALM_LOOKUP.get(s.replace(/_/g, "-")) || s || "unknown";
}

// Parse a component id like `atmosphere_canam5-1_h108_v114` into
// { realm, hId, vId, componentName } — or return null if we can't parse it.
export function parseComponentId(rawId) {
  const id = short(rawId);
  if (!id) return null;
  // Match trailing _h###_v### (allow letters/digits after the h/v for safety).
  const m = id.match(/_h([A-Za-z0-9]+)_v([A-Za-z0-9]+)$/);
  if (!m) return null;
  const hId = "h" + m[1];
  const vId = "v" + m[2];
  const prefix = id.slice(0, m.index);

  // Try each known realm as a prefix (longest first so we don't match
  // "ocean" ahead of "ocean-biogeochemistry"). Prefix + "_" (or "-") + name.
  const realms = [...REALM_CANONICAL].sort((a, b) => b.length - a.length);
  for (const r of realms) {
    for (const sep of ["_", "-"]) {
      // The stored form of the realm in the id may use underscores.
      const forms = new Set([r, r.replace(/-/g, "_")]);
      for (const form of forms) {
        if (prefix.startsWith(form + sep)) {
          return {
            realm: r,
            hId, vId,
            componentName: prefix.slice(form.length + 1),
          };
        }
      }
    }
  }
  // Fallback: take the first _-delimited chunk as the realm string as-is.
  const first = prefix.split("_")[0] || "";
  return {
    realm: normaliseRealm(first),
    hId, vId,
    componentName: prefix.slice(first.length + 1),
  };
}

// Get the primary grid-cell id from a fetched horizontal_computational_grid
// record. horizontal_subgrids may be a string ("g108-mass") or an array of
// such strings. Prefer the "-mass" grid (cell centres); fall back to the
// first entry.
function primaryGridCellFromHGrid(hGridDoc) {
  if (!hGridDoc) return null;
  const raw = hGridDoc.horizontal_subgrids;
  const list = Array.isArray(raw) ? raw : raw != null ? [raw] : [];
  if (!list.length) return null;
  const stripSuffix = s => String(s).replace(/-(mass|x-velocity|y-velocity|u|v)$/i, "");
  const massEntry = list.find(s => /-mass$/i.test(String(s)));
  return short(stripSuffix(massEntry || list[0]));
}

// Extract links from one model. Fetches horizontal_computational_grid records
// as needed (deduped via the resolver's cache). Returns an array of
// { modelId, gridId, realm, componentId, hId }.
export async function extractModelLinks(model, resolver, { debug = false } = {}) {
  const modelId = short(model["@id"] || model.id || model.validation_key || "");
  if (!modelId) return [];

  const compList =
    Array.isArray(model.model_components) ? model.model_components
    : Array.isArray(model.component_configs) ? model.component_configs
    : [];
  if (!compList.length) {
    if (debug) console.warn(`[analysis] model ${modelId} has no model_components / component_configs`);
    return [];
  }

  // Parse each component id → collect all unique h_ids to fetch.
  const parsed = compList.map(parseComponentId).filter(Boolean);
  const needH = [...new Set(parsed.map(p => p.hId))];

  // Fetch h_grids in parallel; failures become nulls.
  const hDocs = new Map();
  await Promise.all(needH.map(async hId => {
    try {
      hDocs.set(hId, await resolver.fetchDoc("horizontal_computational_grid", hId));
    } catch (err) {
      if (debug) console.warn(`[analysis] could not fetch horizontal_computational_grid/${hId}:`, err.message);
      hDocs.set(hId, null);
    }
  }));

  const out = [];
  for (let i = 0; i < parsed.length; i++) {
    const p = parsed[i];
    const gridId = primaryGridCellFromHGrid(hDocs.get(p.hId));
    if (!gridId) {
      if (debug) console.warn(`[analysis] no grid cell resolved for ${short(compList[i])} (${p.hId})`);
      continue;
    }
    out.push({
      modelId,
      gridId,
      realm: p.realm,
      componentId: short(compList[i]),
      hId: p.hId,
    });
  }

  if (!out.length && debug) {
    console.warn(`[analysis] no grid links extracted from model ${modelId}`);
  }
  return out;
}

// Aggregate helper: run extractModelLinks over every model. Returns a flat
// list of links plus a small summary for status reporting.
export async function collectAllLinks(models, resolver, { debug = false } = {}) {
  const links = [];
  let modelsWithLinks = 0, modelsSkipped = 0;
  for (const m of models) {
    const rows = await extractModelLinks(m, resolver, { debug });
    if (rows.length) { links.push(...rows); modelsWithLinks++; }
    else modelsSkipped++;
  }
  if (debug) {
    console.log(`[analysis] extracted ${links.length} links from ${modelsWithLinks} models (${modelsSkipped} skipped)`);
  }
  return { links, modelsWithLinks, modelsSkipped };
}
