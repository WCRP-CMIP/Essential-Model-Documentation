// participation.js — pure grouping logic for the model-participation table.
// No DOM here, so it can be tested in Node against the live registry.
//
// Input : model_family records (family_type is "model" or "component").
// Output: one row per institution, each with the component families and model
//         families it takes part in, tagged "primary" or "collaborator".

import { short } from "./resolver.js";

const clean = v => (v == null ? "" : String(v).trim());
export const isNone = v => {
  const s = clean(v).toLowerCase();
  return !s || s === "none" || s === "not specified";
};

// Records that exist in the registry only as placeholders, not real families.
const PLACEHOLDER_IDS = new Set(["no-family"]);

// An institution id looks like "mohc" or "access-nri".
const SLUG = /^[a-z0-9][a-z0-9_-]*$/;

// Same convention as the Model page: the id, upper-cased ("mohc" -> "MOHC").
export const instLabel = id => id.replace(/-/g, " ").toUpperCase();

export const UNASSIGNED = "(unassigned)";

// Raw institution tokens from a field. `collaborative_institutions` is a list
// in most records but an empty (or comma-separated) string in others;
// `primary_institution` is a single string. Accept all of those.
const rawTokens = v =>
  (Array.isArray(v) ? v : typeof v === "string" ? v.split(",") : [])
    .map(x => short(x).trim().toLowerCase())
    .filter(x => !isNone(x));

// Turn one raw token into an institution id, or null if it is not one.
// A value that is free text instead of an id (e.g. "cas the institute of ...")
// is read by its leading word, but only if that word is an institution id used
// elsewhere in the registry. Anything else is left out and reported.
function resolveId(token, known) {
  if (SLUG.test(token)) return { id: token };
  const lead = token.split(/\s+/)[0];
  return known.has(lead) ? { id: lead, note: "read as" } : { id: null, note: "ignored" };
}

export function familyOf(rec, known = new Set(), notes = []) {
  const id = short(rec["@id"] || rec.validation_key);
  const take = (field, tokens) => tokens.flatMap(t => {
    const r = resolveId(t, known);
    if (r.note) notes.push({ family: id, field, value: t, note: r.note, id: r.id });
    return r.id ? [r.id] : [];
  });
  const primary = take("primary_institution", rawTokens(rec.primary_institution))[0] || null;
  const collaborators = [...new Set(take("collaborative_institutions", rawTokens(rec.collaborative_institutions)))]
    .filter(c => c !== primary);
  return {
    id,
    // 26 records have an empty ui_label; fall back to validation_key, then id.
    label: clean(rec.ui_label) || clean(rec.validation_key) || id,
    type: clean(rec.family_type).toLowerCase(),
    primary,
    collaborators,
    description: clean(rec.description),
  };
}

const byRoleThenLabel = (a, b) =>
  (a.role === b.role ? 0 : a.role === "primary" ? -1 : 1) || a.label.localeCompare(b.label);

// Build the table rows. With includeCollaborators=false an institution only
// lists the families where it is the primary institution.
// Returns { rows, notes, skipped } — `notes` lists institution values that were
// not valid ids, so the page can show them as data issues.
export function buildRows(records, { includeCollaborators = true } = {}) {
  // Institution ids that are well-formed anywhere in the data.
  const known = new Set(records.flatMap(r =>
    [...rawTokens(r.primary_institution), ...rawTokens(r.collaborative_institutions)].filter(t => SLUG.test(t))));

  const rows = new Map();
  const notes = [];
  const skipped = [];
  const rowFor = id => {
    if (!rows.has(id)) {
      rows.set(id, {
        id,
        label: id === UNASSIGNED ? "Unassigned" : instLabel(id),
        components: [],
        models: [],
      });
    }
    return rows.get(id);
  };

  for (const rec of records) {
    const fam = familyOf(rec, known, notes);
    if (PLACEHOLDER_IDS.has(fam.id) || (fam.type !== "component" && fam.type !== "model")) {
      skipped.push(fam);
      continue;
    }

    const entries = [];
    if (fam.primary) entries.push([fam.primary, "primary"]);
    if (includeCollaborators) for (const c of fam.collaborators) entries.push([c, "collaborator"]);
    if (!entries.length) entries.push([UNASSIGNED, "primary"]);

    for (const [inst, role] of entries) {
      const row = rowFor(inst);
      (fam.type === "component" ? row.components : row.models).push({ ...fam, role });
    }
  }

  const list = [...rows.values()];
  for (const r of list) { r.components.sort(byRoleThenLabel); r.models.sort(byRoleThenLabel); }
  return { rows: list, notes, skipped };
}

export const totalOf = r => r.components.length + r.models.length;

// Country (or countries) of a registry `organisation` record. Two record shapes
// exist in the registry:
//   newer: location = [ { country_name, country_code, name (city), ... } ]
//   older: location =   { country: [ "United Kingdom", "GB" ], city, ... }
// Returns [] when the record has no usable location.
export function countryOf(org) {
  const locs = Array.isArray(org?.location) ? org.location : org?.location ? [org.location] : [];
  const out = [];
  for (const l of locs) {
    const old = Array.isArray(l.country) ? l.country : null;
    const name = l.country_name || (old ? old[0] : l.country) || "";
    if (!name) continue;
    out.push({
      name: String(name),
      code: String(l.country_code || (old ? old[1] : "") || ""),
      city: String(l.name || l.city || ""),
    });
  }
  return out;
}

// ---- Published data (ESGF Arrow files) -------------------------------------
//
// Every model has an Arrow file named after it (<validation_key>.arrow) holding
// the datasets published to ESGF for it. A model record points at its model
// family, and a family at its institutions, so a model's published data is
// attributed to the institutions that take part in that family.

export const modelFamilyId = m => short(m?.family?.["@id"] ?? m?.family ?? "");

// Summarise one model's Arrow rows: datasets still published (not retracted),
// how many were retracted, and when the newest row was updated (epoch-ms -> ISO).
export function summariseRows(rows) {
  let datasets = 0, retracted = 0, updated = 0;
  for (const r of rows) {
    if (r.retracted) retracted++; else datasets++;
    if (r.updated && r.updated > updated) updated = r.updated;
  }
  return { datasets, retracted, updated: updated ? new Date(updated).toISOString() : "" };
}

// Group per-model results by model-family id.
// `results`: [{ key, id, family, datasets, retracted, updated }] for models that
// have published data. Returns { byFamily: Map<familyId, results[]>, unattributed },
// where `unattributed` lists models with data but no family, and so no institution.
export function groupPublished(results) {
  const byFamily = new Map();
  const unattributed = [];
  for (const r of results) {
    if (!r.family) { unattributed.push({ key: r.key, reason: "its EMD model record has no family" }); continue; }
    if (!byFamily.has(r.family)) byFamily.set(r.family, []);
    byFamily.get(r.family).push(r);
  }
  return { byFamily, unattributed };
}

// What a table row has published: the distinct published models across the model
// families listed in that row, and their summed dataset count.
export function publishedFor(row, byFamily) {
  const seen = new Map();
  for (const fam of row.models) for (const p of byFamily.get(fam.id) || []) seen.set(p.key, p);
  const models = [...seen.values()].sort((a, b) => b.datasets - a.datasets || a.key.localeCompare(b.key));
  return { models, datasets: models.reduce((n, p) => n + p.datasets, 0) };
}
