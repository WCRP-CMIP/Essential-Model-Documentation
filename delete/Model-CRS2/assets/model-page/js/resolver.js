// resolver.js — fetch EMD JSON-LD and resolve @id references in the browser.
//
// All files come from the published EMD site:
//   https://wcrp-cmip.github.io/Essential-Model-Documentation/<folder>/<id>.json
// (overridable via ?base=). No backend, no build step.

export const DEFAULT_BASE = "https://wcrp-cmip.github.io/Essential-Model-Documentation/";

// field name -> repo folder for id resolution
export const FOLDER = {
  "model_components":              "component_config",
  "component_configs":             "component_config",   // legacy alias
  "horizontal_computational_grid": "horizontal_computational_grid",
  "vertical_computational_grid":   "vertical_computational_grid",
  "horizontal_subgrids":           "horizontal_subgrid",
  "horizontal_grid_cell":          "horizontal_grid_cell",
  "horizontal_grid_cells":         "horizontal_grid_cell",
  "model_component":               "model_component",
  "family":                        "model_family",
};

// keys we never follow as structural graph edges
const META = new Set(["@context", "@type", "@id", "validation_key", "ui_label",
  "description", "alias", "references", "release_year", "calendar", "crs", "name"]);
const MODEL_META = new Set(["coupling_groups", "coupled_components", "omitted_components",
  "prescribed_components", "dynamic_components", "embedded_components", "family"]);
const INLINE_VOCAB = new Set(["arrangement", "grid_mapping", "grid_type",
  "cell_variable_type", "vertical_coordinate", "realm", "units", "region",
  "temporal_refinement", "truncation_method"]);
const SCALAR = new Set(["n_cells", "n_z", "n_z_range", "x_resolution", "y_resolution",
  "westernmost_longitude", "southernmost_latitude", "truncation_number",
  "bottom_layer_thickness", "top_layer_thickness", "total_thickness"]);

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

  // Fetch a model file (no resolution — raw record).
  model(id) { return this.fetchDoc("model", id); }

  // Fetch the folder index and return the list of model ids from `contents`.
  async modelList() {
    const doc = await this.fetchDoc("model", "_graph");
    const entries = Array.isArray(doc.contents) ? doc.contents : [];
    return [...new Set(entries
      .map(e => (typeof e === "string" ? e : e && e["@id"]))
      .filter(Boolean)
      .map(id => id.split("/").pop().split(":").pop())
      .filter(id => id && !id.startsWith("_")))].sort();
  }

  static isMeta(k)   { return META.has(k); }
  static isModelMeta(k) { return MODEL_META.has(k); }
  static isInline(k) { return INLINE_VOCAB.has(k); }
  static isScalar(k) { return SCALAR.has(k); }
  static folderFor(k) { return FOLDER[k]; }
}

export const short = s =>
  typeof s === "string" ? s.split("/").pop().split(":").pop() : String(s ?? "");
