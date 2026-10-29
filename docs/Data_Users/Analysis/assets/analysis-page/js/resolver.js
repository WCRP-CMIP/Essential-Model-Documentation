// resolver.js — fetch EMD collections from the published site
// (https://wcrp-cmip.github.io/Essential-Model-Documentation/<folder>/<id>.json)
// with a shared in-browser cache. Same base URL as the Model + grid_cells pages.

export const DEFAULT_BASE = "https://wcrp-cmip.github.io/Essential-Model-Documentation/";

// Structural / bookkeeping keys that shouldn't be treated as data.
export const META_KEYS = new Set([
  "@context", "@type", "@id", "type", "validation_key",
  "ui_label", "alias", "name", "label", "id",
]);

// Candidate names for the folder-index (graph) file.
const GRAPH_CANDIDATES = ["_graph", "graph"];

export class Resolver {
  constructor(base = DEFAULT_BASE) {
    this.base = base.replace(/\/?$/, "/");
    this.cache = new Map();       // key = "<folder>/<id>" → doc
    this._inflight = new Map();   // key → Promise, to dedupe concurrent fetches
  }

  async fetchDoc(folder, id) {
    const key = `${folder}/${id}`;
    if (this.cache.has(key)) return this.cache.get(key);
    if (this._inflight.has(key)) return this._inflight.get(key);

    const url = this.base + key + ".json";
    const p = (async () => {
      const res = await fetch(url, { headers: { Accept: "application/json" }, mode: "cors" });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText} — ${url}`);
      const doc = await res.json();
      this.cache.set(key, doc);
      this._inflight.delete(key);
      return doc;
    })();
    this._inflight.set(key, p);
    return p;
  }

  async graph(folder) {
    let lastErr = null;
    for (const name of GRAPH_CANDIDATES) {
      try { return await this.fetchDoc(folder, name); }
      catch (e) { lastErr = e; }
    }
    throw lastErr || new Error(`no graph file found in ${folder}`);
  }

  // Load every record in a collection folder. Handles two graph shapes:
  //   { "@graph": [ ...records ] }
  //   { contents: [ ...ids/refs ] }  (fetch each id individually)
  async collection(folder) {
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

    if (full.length && full.length >= objEntries.length * 0.5) {
      return full;
    }

    // Thin graph — fetch each record individually.
    const ids = [...new Set(entries
      .map(e => (typeof e === "string" ? e : e && e["@id"]))
      .filter(Boolean)
      .map(short)
      .filter(id => !isIndexId(id)))];
    const resolved = await Promise.all(ids.map(async id => {
      try { return await this.fetchDoc(folder, id); }
      catch (_) { return null; }
    }));
    return resolved.filter(Boolean);
  }
}

// Strip a URL/JSON-LD id down to its last path segment (without extension).
export const short = s =>
  typeof s === "string" ? s.split("/").pop().split(":").pop().replace(/\.json$/i, "")
  : (s && typeof s === "object" && s["@id"]) ? short(s["@id"])
  : String(s ?? "");
