// crs.js — Canonical Realm String helpers, ported from
// docs/Model/assets/model-page/js/crs.js and crs-diagram.js.
//
// Exports:
//   parse(crs)              → { embeddings, couplingPairs, roots, prescribed }
//   realmColor / realmLabel / toCode / toName / sortCodes  — palette helpers
//   renderCrsInline(model)  → DocumentFragment for the analysis detail panel
//                             (coloured CRS string + compact spheres diagram)

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

// Documentation earth-tone palette — matches Model/assets/model-page/js/crs.js.
export const REALM_META = {
  "atmosphere":            { label: "Atmosphere",             color: "#e76f51" },
  "atmospheric-chemistry": { label: "Atmospheric chemistry",  color: "#f4a261" },
  "aerosol":               { label: "Aerosol",                color: "#e9c46a" },
  "land-surface":          { label: "Land surface",           color: "#8ab17d" },
  "land-ice":              { label: "Land ice",               color: "#7cadbe" },
  "ocean":                 { label: "Ocean",                  color: "#264653" },
  "ocean-biogeochemistry": { label: "Ocean biogeochemistry",  color: "#287271" },
  "sea-ice":               { label: "Sea ice",                color: "#2a9d8f" },
};

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

// ==== CRS parse ============================================================
// parent[c1c2]  — embedded realms         (canonical-sorted after parse)
// parent(c1,c2) — bidirectional coupling
// code^         — prescribed realm (bare root, non-interactive)
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

// ==== inline renderer (for the analysis-page detail panel) ================
// Compact port of docs/Model/assets/model-page/js/components/crs-diagram.js.
// Produces: coloured CRS string above a small "spheres" SVG. Root realms sit
// on a ring; embedded children pack into the parent circle; couplings drawn
// as thin dashed arcs; prescribed realms as outlined halos.
const NS = "http://www.w3.org/2000/svg";
const svgEl = (tag, attrs = {}) => {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  return n;
};

// Colour each realm code by its palette entry; codes inside [...] are shown
// paler via a CSS class; structural glyphs [] () , ^ are muted.
function renderCrsCode(crs) {
  const code = document.createElement("code");
  code.className = "an-crs-code";
  const n = crs.length;
  let i = 0, inEmbed = 0;
  while (i < n) {
    const ch = crs[i];
    if (ch >= "A" && ch <= "Z") {
      let tok = ch; i++;
      while (i < n && crs[i] >= "a" && crs[i] <= "z") { tok += crs[i]; i++; }
      const sp = document.createElement("span");
      sp.className = "an-crs-tok" + (inEmbed ? " embedded" : "");
      sp.style.setProperty("--realm", realmColor(tok));
      sp.textContent = tok;
      code.appendChild(sp);
      continue;
    }
    if (ch === "[") inEmbed++;
    else if (ch === "]") inEmbed = Math.max(0, inEmbed - 1);
    const sp = document.createElement("span");
    sp.className = "an-crs-tok-struct";
    sp.textContent = ch;
    code.appendChild(sp);
    i++;
  }
  return code;
}

// Compact spheres diagram — small SVG suitable for a ~250px-wide detail panel.
function renderCrsDiagram(crs, { size = 220 } = {}) {
  const { embeddings, couplingPairs, roots, prescribed } = parse(crs);
  const preSet = new Set(prescribed);

  const childrenOf = new Map();
  for (const [parent, child] of embeddings) {
    if (!childrenOf.has(parent)) childrenOf.set(parent, []);
    childrenOf.get(parent).push(child);
  }

  const W = size, H = size, cx = W / 2, cy = H / 2;
  const PR = Math.round(size * 0.15);                // parent radius (~33)
  const PRE_R = Math.round(PR * 0.72);                // prescribed radius
  const CR = Math.max(6, Math.round((PR - 4) * 0.44));// child radius
  const ringR = roots.length <= 1 ? 0 : Math.min(W, H) / 2 - PR - 6;

  const pos = new Map();
  roots.forEach((code, i) => {
    if (roots.length === 1) { pos.set(code, { x: cx, y: cy }); return; }
    const ang = -Math.PI / 2 + (2 * Math.PI * i) / roots.length;
    pos.set(code, { x: cx + ringR * Math.cos(ang), y: cy + ringR * Math.sin(ang) });
  });

  const s = svgEl("svg", {
    viewBox: `0 0 ${W} ${H}`,
    class: "an-crs-svg",
    preserveAspectRatio: "xMidYMid meet",
    role: "img",
    "aria-label": `CRS diagram: ${crs}`,
  });

  // Coupling arcs behind circles
  for (const [a, b] of couplingPairs) {
    const pa = pos.get(a), pb = pos.get(b);
    if (!pa || !pb) continue;
    const dx = pb.x - pa.x, dy = pb.y - pa.y, len = Math.hypot(dx, dy) || 1;
    let nx = -dy / len, ny = dx / len;
    const midToC = (cx - (pa.x + pb.x) / 2) * nx + (cy - (pa.y + pb.y) / 2) * ny;
    if (midToC > 0) { nx = -nx; ny = -ny; }
    const bow = Math.min(28, 8 + len * 0.16);
    const mx = (pa.x + pb.x) / 2 + nx * bow, my = (pa.y + pb.y) / 2 + ny * bow;
    s.appendChild(svgEl("path", {
      d: `M${pa.x},${pa.y} Q${mx},${my} ${pb.x},${pb.y}`,
      class: "an-crs-couple", fill: "none",
    }));
  }

  // Root realm circles with embedded children packed inside
  for (const code of roots) {
    const p = pos.get(code);
    const color = realmColor(code);
    const isPre = preSet.has(code);
    const kids = childrenOf.get(code) || [];
    const r = isPre ? PRE_R : PR;
    const g = svgEl("g", {
      class: `an-crs-node${isPre ? " prescribed" : ""}`,
      transform: `translate(${p.x},${p.y})`,
    });

    if (isPre) {
      g.appendChild(svgEl("circle", { r: r + 2, class: "an-crs-pre-halo", style: `--realm:${color}` }));
      g.appendChild(svgEl("circle", { r, class: "an-crs-pre-circle", style: `--realm:${color}` }));
    } else {
      g.appendChild(svgEl("circle", { r, class: "an-crs-sphere", style: `--realm:${color}` }));
    }

    // Code label (A, Ac, Ae, L, O, Ob, Si, Li). Small letter set fits neatly.
    const lbl = svgEl("text", { x: 0, y: kids.length ? -r * 0.4 : r * 0.05, class: "an-crs-sphere-label" });
    lbl.textContent = code;
    g.appendChild(lbl);

    if (isPre) {
      const tag = svgEl("text", { x: 0, y: r * 0.65, class: "an-crs-pre-tag" });
      tag.textContent = "presc";
      g.appendChild(tag);
    }

    // Embedded children in a row inside the parent
    if (kids.length) {
      const yOff = r * 0.28;
      const step = kids.length === 1 ? 0 : Math.min(CR * 2 + 3, (r - CR - 4) * 2 / (kids.length - 1));
      kids.forEach((k, i) => {
        const xOff = kids.length === 1 ? 0 : -step * (kids.length - 1) / 2 + i * step;
        const cg = svgEl("g", { class: "an-crs-child", transform: `translate(${xOff},${yOff})` });
        cg.appendChild(svgEl("circle", { r: CR, class: "an-crs-child-sphere", style: `--realm:${realmColor(k)}` }));
        const t = svgEl("text", { x: 0, y: 0, class: "an-crs-child-label" });
        t.textContent = k;
        cg.appendChild(t);
        g.appendChild(cg);
      });
    }
    s.appendChild(g);
  }
  return s;
}

// Public: returns a DocumentFragment (coloured string + diagram) or null.
export function renderCrsInline(model, opts = {}) {
  const crs = model && model.crs;
  if (!crs) return null;
  const frag = document.createDocumentFragment();
  const line = document.createElement("div");
  line.className = "an-crs-string";
  line.appendChild(renderCrsCode(crs));
  frag.appendChild(line);
  frag.appendChild(renderCrsDiagram(crs, opts));
  return frag;
}
