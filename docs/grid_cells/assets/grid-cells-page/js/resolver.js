// resolver.js — fetch the horizontal_grid_cell collection and resolve nested
// @id references (inline vocab terms) in the browser.
//
// Files come from the published EMD site:
//   https://wcrp-cmip.github.io/Essential-Model-Documentation/<folder>/<id>.json
// (overridable via ?base=). No backend, no build step.

export const DEFAULT_BASE = "https://wcrp-cmip.github.io/Essential-Model-Documentation/";

// The collection this page documents.
export const FOLDER = "horizontal_grid_cell";

// Keys that are structural / bookkeeping and should never become table columns.
// ui_label + alias at the top level are the record's own labels; they are also
// skipped as columns but surfaced separately by the table (as subtitles under
// the id) so people can spot the grid they want at a glance.
export const META_KEYS = new Set([
  "@context", "@type", "@id", "type", "validation_key", "ui_label", "alias",
]);

// Candidate names for the folder index / graph file. The EMD site uses
// "_graph" (with a leading underscore) for the canonical index; older/mirror
// builds may use plain "graph". We try each in order and use the first hit.
const GRAPH_CANDIDATES = ["_graph", "graph"];

// Top-level record keys that hold nested vocab terms we may need to resolve
// (to obtain their ui_label + description for the table + tooltips). Each maps
// to the repo folder that stores that vocabulary's term files.
export const TERM_FOLDER = {
  grid_mapping:        "grid_mapping",
  grid_type:           "grid_type",
  region:              "region",
  temporal_refinement: "temporal_refinement",
  truncation_method:   "truncation_method",
  units:               "units",
  arrangement:         "arrangement",
  cell_variable_type:  "cell_variable_type",
  vertical_coordinate: "vertical_coordinate",
};

const isLinkObj = v => v && typeof v === "object" && !Array.isArray(v);
// A term is "thin" if it lacks the human-facing fields we want to display.
const isThinTerm = t => isLinkObj(t) && !t.description;

export class Resolver {
  constructor(base = DEFAULT_BASE) {
    this.base = base.replace(/\/?$/, "/");
    this.cache = new Map();
  }

  async fetchDoc(folder, id) {
    const key = `${folder}/${id}`;
    if (this.cache.has(key)) return this.cache.get(key);
    const url = this.base + key + ".json";
    const res = await fetch(url, { headers: { Accept: "application/json" }, mode: "cors" });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText} — ${url}`);
    const doc = await res.json();
    this.cache.set(key, doc);
    return doc;
  }

  // Fetch the folder graph file, trying "_graph.json" first, then "graph.json".
  async graph(folder = FOLDER) {
    let lastErr = null;
    for (const name of GRAPH_CANDIDATES) {
      try { return await this.fetchDoc(folder, name); }
      catch (e) { lastErr = e; }
    }
    throw lastErr || new Error("no graph file found");
  }

  // Load every grid-cell record.
  async collection(folder = FOLDER) {
    let graph;
    try { graph = await this.graph(folder); }
    catch (e) { throw new Error(`could not load ${folder} graph — ${e.message}`); }

    const entries =
      Array.isArray(graph) ? graph
      : Array.isArray(graph["@graph"]) ? graph["@graph"]
      : Array.isArray(graph.contents) ? graph.contents
      : [];

    const isIndexId = id => {
      const s = short(id);
      return !s || s.startsWith("_") || s === "graph" || s === "context";
    };

    const objEntries = entries.filter(e => e && typeof e === "object");
    const full = objEntries.filter(e =>
      !isIndexId(e["@id"]) && Object.keys(e).some(k => !META_KEYS.has(k)));

    let records;
    if (full.length && full.length >= objEntries.length * 0.5) {
      records = full;
    } else {
      const ids = [...new Set(entries
        .map(e => (typeof e === "string" ? e : e && e["@id"]))
        .filter(Boolean)
        .map(short)
        .filter(id => !isIndexId(id)))];
      const resolved = await Promise.all(ids.map(async id => {
        try { return await this.fetchDoc(folder, id); }
        catch (_) { return null; }
      }));
      records = resolved.filter(Boolean);
    }

    // Enrich nested vocab terms that are missing their description (the graph
    // may embed only { @id, ui_label } or even bare { @id } references). We
    // fetch each distinct term file once and merge in the missing fields so the
    // table can show ui_label and the hover tooltip can show the description.
    await this.enrichTerms(records);

    return records;
  }

  // For every record, for every known vocab key, resolve thin nested terms in
  // place by fetching <termFolder>/<id>.json and filling ui_label/description.
  // Missing files are tolerated (the term keeps whatever fields it had).
  async enrichTerms(records) {
    // Collect the distinct (folder, id) pairs that need fetching.
    const needed = new Map();   // `${folder}/${id}` -> { folder, id }
    const noteThin = (folder, term) => {
      const id = short(term && (term["@id"] || term.validation_key));
      if (!id) return;
      const key = `${folder}/${id}`;
      if (!needed.has(key)) needed.set(key, { folder, id });
    };

    for (const rec of records) {
      for (const [k, folder] of Object.entries(TERM_FOLDER)) {
        const v = rec[k];
        if (v == null) continue;
        const arr = Array.isArray(v) ? v : [v];
        for (const item of arr) if (isThinTerm(item)) noteThin(folder, item);
      }
    }
    if (!needed.size) return;

    // Fetch them all (deduped, cached) — tolerate individual failures.
    const fetched = new Map();  // `${folder}/${id}` -> doc
    await Promise.all([...needed.values()].map(async ({ folder, id }) => {
      try { fetched.set(`${folder}/${id}`, await this.fetchDoc(folder, id)); }
      catch (_) { /* leave unresolved */ }
    }));

    // Merge fetched fields into the thin terms (fill only what's missing).
    const mergeInto = (folder, term) => {
      const id = short(term && (term["@id"] || term.validation_key));
      const doc = id && fetched.get(`${folder}/${id}`);
      if (!doc) return;
      if (!term.ui_label && doc.ui_label) term.ui_label = doc.ui_label;
      if (!term.description && doc.description) term.description = doc.description;
      if (!term.validation_key && doc.validation_key) term.validation_key = doc.validation_key;
    };
    for (const rec of records) {
      for (const [k, folder] of Object.entries(TERM_FOLDER)) {
        const v = rec[k];
        if (v == null) continue;
        const arr = Array.isArray(v) ? v : [v];
        for (const item of arr) if (isThinTerm(item)) mergeInto(folder, item);
      }
    }
  }
}

export const short = s =>
  typeof s === "string" ? s.split("/").pop().split(":").pop().replace(/\.json$/i, "")
  : (s && typeof s === "object" && s["@id"]) ? short(s["@id"])
  : String(s ?? "");
