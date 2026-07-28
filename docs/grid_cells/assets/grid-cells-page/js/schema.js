// schema.js — inspect the grid-cell records and derive a table schema.
//
// Responsibilities:
//   • discover which top-level keys become columns (skipping @meta keys)
//   • classify each column as "numeric" (range filter) or "category" (value
//     filter) or "text" (contains filter), based on the values present
//   • flatten each record into a row of display + filter values, resolving
//     nested { @id, ui_label, description } objects to their ui-label (with the
//     description carried alongside for a hover tooltip)
//
// Nesting rule: we descend at most DEPTH_LIMIT (=2) levels into nested objects
// when producing a display value. Beyond that we stop and show the id/label.

import { META_KEYS, short } from "./resolver.js";

export const DEPTH_LIMIT = 3;

// A column that always leads: the grid-cell id (the thing users search for).
export const ID_COL = { key: "@id", label: "Grid ID", kind: "id" };


const isNil = v => v == null || (typeof v === "string" && !v.trim());
const titleCase = s => String(s).replace(/[_-]+/g, " ").replace(/\b\w/g, c => c.toUpperCase());

// Human label for a column key.
export function columnLabel(key) {
  return titleCase(key);
}

// Does a value look like a linked/nested term? i.e. an object with @id, or a
// bare string id we might have a ui_label for elsewhere.
const isLinkObj = v => v && typeof v === "object" && !Array.isArray(v);

// Extract { label, description, id } from a nested term, descending up to
// `depth` levels. Stops at DEPTH_LIMIT. Falls back to the short id.
export function termInfo(v, depth = DEPTH_LIMIT) {
  if (isNil(v)) return null;
  if (typeof v === "string") return { label: short(v), description: "", id: v };
  if (isLinkObj(v)) {
    const id = v["@id"] || v.validation_key || "";
    const label = v.ui_label || v.label || (id ? short(id) : "") || v.validation_key || "";
    const description = v.description || "";
    // We only need label + description for display; deeper descent is only
    // relevant if there were no label — then peek one level in (bounded).
    if (!label && depth > 1) {
      for (const val of Object.values(v)) {
        const inner = termInfo(val, depth - 1);
        if (inner && inner.label) return inner;
      }
    }
    return { label: label || short(id) || "—", description, id };
  }
  return { label: String(v), description: "", id: "" };
}

// Produce the display cell payload for a raw value on a record.
//   scalar        → { text }
//   nested term   → { terms:[{label,description}] }
//   array         → { terms:[…] }  (each element resolved as a term)
export function cellValue(raw) {
  if (isNil(raw)) return { text: "", empty: true };
  if (Array.isArray(raw)) {
    const terms = raw.map(x => termInfo(x)).filter(Boolean);
    if (!terms.length) return { text: "", empty: true };
    return { terms };
  }
  if (isLinkObj(raw)) {
    const t = termInfo(raw);
    return t ? { terms: [t] } : { text: "", empty: true };
  }
  if (typeof raw === "number") return { text: raw, number: raw };
  // string that is actually numeric?
  if (typeof raw === "string" && raw.trim() !== "" && !isNaN(Number(raw)) && /\d/.test(raw)) {
    return { text: raw, number: Number(raw) };
  }
  return { text: String(raw) };
}

// Categorical filter tokens for a raw value (used to build the value-filter
// checklist and to test membership).
export function categoryTokens(raw) {
  if (isNil(raw)) return [];
  const arr = Array.isArray(raw) ? raw : [raw];
  return arr.map(x => {
    const t = termInfo(x);
    return t ? t.label : String(x);
  }).filter(s => s && s.trim());
}

// Numeric value for a raw value, or null if not numeric.
export function numericValue(raw) {
  if (typeof raw === "number") return raw;
  if (typeof raw === "string" && raw.trim() !== "" && !isNaN(Number(raw))) return Number(raw);
  return null;
}

// Build the schema from all records.
//   returns { columns:[{key,label,kind,min,max,options}], rows:[record] }
// kind ∈ "numeric" | "category" | "text"
export function buildSchema(records) {
  const keyStats = new Map();  // key -> { count, numeric, nonNumeric, values:Set, hasDesc }

  for (const rec of records) {
    for (const [k, v] of Object.entries(rec)) {
      if (META_KEYS.has(k)) continue;
      if (isNil(v)) continue;
      if (!keyStats.has(k)) keyStats.set(k, { count: 0, numeric: 0, nonNumeric: 0, values: new Set(), hasDesc: false });
      const st = keyStats.get(k);
      st.count++;
      const arr = Array.isArray(v) ? v : [v];
      for (const item of arr) {
        const num = numericValue(item);
        if (num != null && !isLinkObj(item)) st.numeric++;
        else {
          st.nonNumeric++;
          const t = termInfo(item);
          if (t) { st.values.add(t.label); if (t.description) st.hasDesc = true; }
        }
      }
    }
  }

  // Order columns: most-populated first, description last (it's long).
  const keys = [...keyStats.keys()];
  const DESC_KEYS = new Set(["description"]);
  keys.sort((a, b) => {
    if (DESC_KEYS.has(a) !== DESC_KEYS.has(b)) return DESC_KEYS.has(a) ? 1 : -1;
    return keyStats.get(b).count - keyStats.get(a).count;
  });

  const columns = keys.map(key => {
    const st = keyStats.get(key);
    const numericDominant = st.numeric > 0 && st.nonNumeric === 0;
    if (numericDominant) {
      let min = Infinity, max = -Infinity;
      for (const rec of records) {
        const raw = rec[key]; if (isNil(raw)) continue;
        const arr = Array.isArray(raw) ? raw : [raw];
        for (const item of arr) { const n = numericValue(item); if (n != null) { min = Math.min(min, n); max = Math.max(max, n); } }
      }
      return { key, label: columnLabel(key), kind: "numeric", min, max };
    }
    const distinct = st.values.size;
    if (distinct > 0 && distinct <= 40 && key !== "description") {
      return { key, label: columnLabel(key), kind: "category", options: [...st.values].sort(cmpValues) };
    }
    if (key === "description") return null;  // not a filterable column
    return { key, label: columnLabel(key), kind: "text" };
  });

  return { columns: columns.filter(Boolean), rows: records.slice() };
}

// Sort category values naturally (numbers within strings sort numerically).
export function cmpValues(a, b) {
  return String(a).localeCompare(String(b), undefined, { numeric: true, sensitivity: "base" });
}
