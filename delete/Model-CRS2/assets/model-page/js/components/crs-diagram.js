// components/crs-diagram.js — nested-circle ("spheres") rendering of the CRS.
//
// Driven entirely by the parsed CRS string (via crs.js parse(), which handles
// the '^' prescribed marker). Root realms are drawn as circles laid out on a
// ring; embedded realms are packed inside their parent circle; couplings are
// drawn as dashed double-headed arcs between roots; prescribed ('^') realms get
// a dashed ring and a tag. Pure SVG + a light force-free radial layout — no D3.

import { parse, toName, realmLabel, realmColor, sortCodes } from "../crs.js";
import { card } from "../dom.js";

const NS = "http://www.w3.org/2000/svg";
const svg = (tag, attrs = {}) => {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  return n;
};

// short label used inside the small embedded circles
function shortRealm(code) {
  const map = {
    "atmosphere": "atm", "atmospheric-chemistry": "chem", "aerosol": "aer",
    "land-surface": "land", "land-ice": "ice", "ocean": "ocn",
    "ocean-biogeochemistry": "bgc", "sea-ice": "sea-ice",
  };
  return map[toName(code)] || code;
}

export function mountCrsDiagram(root, model) {
  const crs = model.crs;
  const body = [];

  if (!crs) {
    body.push(Object.assign(document.createElement("p"),
      { className: "card-sub", textContent: "No CRS string is defined for this model." }));
    root.appendChild(card("Coupling topology (CRS)", body, { extraClass: "crs-diagram" }));
    return;
  }

  // CRS string display
  const codeLine = document.createElement("div");
  codeLine.className = "crs-string";
  codeLine.appendChild(Object.assign(document.createElement("code"), { textContent: crs }));
  body.push(codeLine);

  const { embeddings, couplingPairs, roots, prescribed } = parse(crs);
  const preSet = new Set(prescribed);

  // parent → [children]
  const childrenOf = new Map();
  for (const [parent, child] of embeddings) {
    if (!childrenOf.has(parent)) childrenOf.set(parent, []);
    childrenOf.get(parent).push(child);
  }
  childrenOf.forEach(arr => arr.sort((a, b) => sortCodes([a, b])[0] === a ? -1 : 1));

  // ---- layout: roots on a ring (single root → centre) --------------------
  const W = 560, H = 560, cx = W / 2, cy = H / 2;
  const PR = 62;                         // parent circle radius
  const CR = Math.round((PR - 8) * 0.46); // child radius
  const ringR = roots.length <= 1 ? 0
    : Math.min(W, H) / 2 - PR - 34;      // radius of the root ring

  const pos = new Map();
  roots.forEach((code, i) => {
    if (roots.length === 1) { pos.set(code, { x: cx, y: cy }); return; }
    const ang = -Math.PI / 2 + (2 * Math.PI * i) / roots.length;
    pos.set(code, { x: cx + ringR * Math.cos(ang), y: cy + ringR * Math.sin(ang) });
  });

  const s = svg("svg", { viewBox: `0 0 ${W} ${H}`, class: "crs-svg", preserveAspectRatio: "xMidYMid meet" });

  // ---- coupling arcs (behind circles) ------------------------------------
  // A curved dashed line denotes a (bidirectional) coupling. No arrowheads:
  // coupling is symmetric, so directional glyphs were misleading.
  const arcs = svg("g", { class: "crs-couples" });
  for (const [a, b] of couplingPairs) {
    const pa = pos.get(a), pb = pos.get(b);
    if (!pa || !pb) continue;
    const dx = pb.x - pa.x, dy = pb.y - pa.y, len = Math.hypot(dx, dy) || 1;
    const ux = dx / len, uy = dy / len;
    // perpendicular, to bow the arc outward from the ring centre
    let nx = -uy, ny = ux;
    const midToCentre = (cx - (pa.x + pb.x) / 2) * nx + (cy - (pa.y + pb.y) / 2) * ny;
    if (midToCentre > 0) { nx = -nx; ny = -ny; }         // always bow away from centre
    const bow = Math.min(70, 22 + len * 0.16);
    const mx = (pa.x + pb.x) / 2 + nx * bow, my = (pa.y + pb.y) / 2 + ny * bow;

    // curved dashed connector (no arrowheads)
    arcs.appendChild(svg("path", {
      d: `M${pa.x},${pa.y} Q${mx},${my} ${pb.x},${pb.y}`,
      class: "crs-couple", fill: "none",
    }));
  }
  s.appendChild(arcs);

  // ---- root realm circles ------------------------------------------------
  for (const code of roots) {
    const p = pos.get(code);
    const color = realmColor(code);
    const isPre = preSet.has(code);
    const kids = childrenOf.get(code) || [];

    const g = svg("g", { class: `crs-node${isPre ? " prescribed" : ""}`, transform: `translate(${p.x},${p.y})` });

    if (isPre) {
      // prescribed: an outer dashed halo ring marks it as externally imposed,
      // plus a soft-filled inner disc — visually distinct from coupling dashes.
      g.appendChild(svg("circle", { r: PR + 5, class: "crs-pre-halo", style: `--realm:${color}` }));
    }
    g.appendChild(svg("circle", { r: PR, class: "crs-sphere", style: `--realm:${color}` }));

    // parent label — nudged up when it has children so it doesn't overlap
    const lbl = svg("text", { x: 0, y: kids.length ? -PR * 0.5 : 0, class: "crs-sphere-label" });
    lbl.textContent = realmLabel(code);
    g.appendChild(lbl);

    if (isPre) {
      const tag = svg("text", { x: 0, y: PR * 0.72, class: "crs-pre-tag" });
      tag.textContent = "prescribed ^";
      g.appendChild(tag);
    }

    // embedded children packed in a row inside the parent
    if (kids.length) {
      const yOff = PR * 0.22;
      const step = kids.length === 1 ? 0 : Math.min(CR * 2 + 4, (PR - CR - 6) * 2 / (kids.length - 1));
      kids.forEach((k, i) => {
        const xOff = kids.length === 1 ? 0 : -step * (kids.length - 1) / 2 + i * step;
        const cg = svg("g", { class: "crs-child-node", transform: `translate(${xOff},${yOff})` });
        cg.appendChild(svg("circle", { r: CR, class: "crs-child-sphere", style: `--realm:${realmColor(k)}` }));
        const t = svg("text", { x: 0, y: 0, class: "crs-child-label" });
        t.textContent = shortRealm(k);
        cg.appendChild(t);
        g.appendChild(cg);
      });
    }
    s.appendChild(g);
  }

  body.push(s);

  // legend
  const legend = document.createElement("div");
  legend.className = "crs-legend";
  legend.innerHTML =
    `<span><i class="lg-sphere"></i>dynamic realm</span>` +
    `<span><i class="lg-sphere lg-pre"></i>prescribed (^)</span>` +
    `<span><i class="lg-child"></i>embedded</span>` +
    `<span><i class="lg-arc"></i>coupling</span>`;
  body.push(legend);

  root.appendChild(card("Coupling topology (CRS)", body, { extraClass: "crs-diagram" }));
}
