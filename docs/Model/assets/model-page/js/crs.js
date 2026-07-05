// crs.js — Canonical Realm String: parse + render helpers (browser port of
// cmipld/utils/crs.py, including the '^' prescribed marker).
//
//   parent[child1child2]  — embedded realms (canonical-sorted)
//   parent(c1,c2)         — forward-only couplings
//   code^                 — prescribed realm (bare root, non-interactive)

export const REALM_CODES = {
  "atmosphere":            "A",
  "atmospheric-chemistry": "Ac",
  "aerosol":               "Ae",
  "land-ice":              "Li",
  "land-surface":          "L",
  "ocean":                 "O",
  "ocean-biogeochemistry": "Ob",
  "sea-ice":               "Si",
};
export const CODE_TO_REALM = Object.fromEntries(
  Object.entries(REALM_CODES).map(([k, v]) => [v, k])
);
export const CANONICAL_ORDER = ["A", "Ac", "Ae", "Li", "L", "O", "Ob", "Si"];

// Per-realm label + accent colour — the single source of truth for realm
// colours across the whole page (CRS spheres, hierarchy nodes, component rows,
// grid "used by" tags, etc.). This is the documentation's earth-tone spectral
// palette, matching docs/stylesheets/scientific_domains.css (.sd-* tokens):
// a warm→cool ramp running atmosphere (terracotta) → land (green) → ocean (teal).
export const REALM_META = {
  "atmosphere":            { label: "Atmosphere",             color: "#e76f51" },  // terracotta
  "atmospheric-chemistry": { label: "Atmospheric chemistry",  color: "#f4a261" },  // sandy orange
  "aerosol":               { label: "Aerosol",                color: "#e9c46a" },  // gold
  "land-surface":          { label: "Land surface",           color: "#8ab17d" },  // sage green
  "land-ice":              { label: "Land ice",               color: "#7cadbe" },  // dusty blue
  "ocean":                 { label: "Ocean",                  color: "#264653" },  // deep teal-navy
  "ocean-biogeochemistry": { label: "Ocean biogeochemistry",  color: "#287271" },  // teal
  "sea-ice":               { label: "Sea ice",                color: "#2a9d8f" },  // green-teal
};

// Convenience: plain {realm-name: colour} and {CODE: colour} maps, in case a
// component wants the palette directly rather than via realmColor().
export const REALM_COLORS = Object.fromEntries(
  Object.entries(REALM_META).map(([name, m]) => [name, m.color])
);
export const CODE_COLORS = Object.fromEntries(
  Object.entries(REALM_CODES).map(([name, code]) => [code, REALM_META[name].color])
);

export const rank = code => {
  const i = CANONICAL_ORDER.indexOf(code);
  return i < 0 ? CANONICAL_ORDER.length : i;
};
export const sortCodes = codes => [...codes].sort((a, b) => rank(a) - rank(b));

export const toCode = name => {
  if (!name) return name;
  const n = String(name).trim().toLowerCase().replace(/_/g, "-");
  return REALM_CODES[n] || n;
};
export const toName = code => CODE_TO_REALM[code] || code;
export const realmLabel = x => REALM_META[CODE_TO_REALM[x] || x]?.label || (CODE_TO_REALM[x] || x);
export const realmColor = x => REALM_META[CODE_TO_REALM[x] || x]?.color || "#7a8499";

// Parse a CRS string → {embeddings, couplingPairs, roots, prescribed}
export function parse(crs) {
  const embeddings = [];
  const couplingPairs = [];
  const prescribed = [];
  const roots = [];
  const parentStack = [];
  let i = 0;
  const n = (crs || "").length;

  const readCode = pos => {
    if (pos >= n) return ["", pos];
    let code = crs[pos]; pos++;
    if (pos < n && crs[pos] >= "a" && crs[pos] <= "z") { code += crs[pos]; pos++; }
    return [code, pos];
  };

  while (i < n) {
    const ch = crs[i];
    if (ch >= "A" && ch <= "Z") {
      let code; [code, i] = readCode(i);
      if (i < n && crs[i] === "^") { prescribed.push(code); i++; }
      const parent = parentStack[parentStack.length - 1];
      if (parent) embeddings.push([parent, code]);
      else roots.push(code);
      if (i < n && crs[i] === "[") { parentStack.push(code); i++; }
    } else if (ch === "]") {
      parentStack.pop(); i++;
    } else if (ch === "(") {
      const owner = roots.length ? roots[roots.length - 1]
                  : (parentStack.length ? parentStack[parentStack.length - 1] : null);
      i++;
      while (i < n && crs[i] !== ")") {
        if (crs[i] === ",") { i++; continue; }
        if (crs[i] >= "A" && crs[i] <= "Z") {
          let coupled; [coupled, i] = readCode(i);
          if (owner) {
            const pair = sortCodes([owner, coupled]);
            if (!couplingPairs.some(p => p[0] === pair[0] && p[1] === pair[1]))
              couplingPairs.push(pair);
          }
        } else i++;
      }
      if (i < n && crs[i] === ")") i++;
    } else i++;
  }
  return { embeddings, couplingPairs, roots: sortCodes(roots), prescribed: sortCodes(prescribed) };
}
