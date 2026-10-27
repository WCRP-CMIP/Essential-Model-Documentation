// resolver.js — load every record of one registry folder (here: model_family).
//
// Files come from the published EMD site:
//   https://wcrp-cmip.github.io/Essential-Model-Documentation/<folder>/<id>.json
// (overridable via ?base=). No backend, no build step.
//
// Same approach as the grid viewer's resolver.js, minus the vocab-term
// enrichment, which this page does not need.

export const DEFAULT_BASE = "https://wcrp-cmip.github.io/Essential-Model-Documentation/";

// Keys that are bookkeeping, not content: a graph entry holding only these is
// a bare reference and the full record has to be fetched.
const META_KEYS = new Set([
  "@context", "@type", "@id", "type", "validation_key",
  "ui_label", "alias", "name", "label", "id",
]);

// The EMD site uses "_graph" for the folder index; mirrors may use "graph".
const GRAPH_CANDIDATES = ["_graph", "graph"];

export const short = s =>
  typeof s === "string" ? s.split("/").pop().split(":").pop().replace(/\.json$/i, "")
  : (s && typeof s === "object" && s["@id"]) ? short(s["@id"])
  : String(s ?? "");

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

  async graph(folder) {
    let lastErr = null;
    for (const name of GRAPH_CANDIDATES) {
      try { return await this.fetchDoc(folder, name); }
      catch (e) { lastErr = e; }
    }
    throw lastErr || new Error("no graph file found");
  }

  // Load every record in `folder`. Uses the records embedded in the graph file
  // when it has them; otherwise fetches each referenced file.
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

    if (full.length && full.length >= objEntries.length * 0.5) return full;

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
