// components/crs-diagram.js — visual rendering of the Canonical Realm String.
//
// Root realms sit in a row. Embedded children are drawn as smaller chips inside
// their parent. Couplings are dashed arcs bowing above the row. Prescribed
// realms (the '^' ones) are dashed/muted and tagged.
//
// Pure SVG, no dependencies. Scales to the container width.

import { parse, toName, realmLabel, realmColor } from "../crs.js";

const NS = "http://www.w3.org/2000/svg";
const svg = (tag, attrs = {}) => {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  return n;
};

export function mountCrsDiagram(root, model) {
  const crs = model.crs;
  const wrap = document.createElement("section");
  wrap.className = "card crs-diagram";
  const h = document.createElement("h2");
  h.className = "card-title";
  h.textContent = "Coupling topology (CRS)";
  wrap.appendChild(h);

  if (!crs) {
    const p = document.createElement("p");
    p.className = "card-sub";
    p.textContent = "No CRS string is defined for this model.";
    wrap.appendChild(p);
    root.appendChild(wrap);
    return;
  }

  const codeLine = document.createElement("div");
  codeLine.className = "crs-string";
  codeLine.appendChild(Object.assign(document.createElement("code"), { textContent: crs }));
  wrap.appendChild(codeLine);

  const { embeddings, couplingPairs, roots, prescribed } = parse(crs);
  const preSet = new Set(prescribed);

  const childrenOf = new Map();
  for (const [parent, child] of embeddings) {
    if (!childrenOf.has(parent)) childrenOf.set(parent, []);
    childrenOf.get(parent).push(child);
  }

  // ---- layout ------------------------------------------------------------
  const W = 720, padX = 40, rowY = 150;
  const boxW = 108, boxH = 62, gap = 44;
  const n = roots.length;
  const totalW = n * boxW + (n - 1) * gap;
  const startX = Math.max(padX, (W - totalW) / 2);
  const pos = new Map();
  roots.forEach((code, i) => pos.set(code, startX + i * (boxW + gap)));

  const H = rowY + boxH + 40;
  const s = svg("svg", { viewBox: `0 0 ${W} ${H}`, class: "crs-svg", preserveAspectRatio: "xMidYMid meet" });

  // coupling arcs (behind boxes)
  for (const [a, b] of couplingPairs) {
    if (!pos.has(a) || !pos.has(b)) continue;
    const x1 = pos.get(a) + boxW / 2, x2 = pos.get(b) + boxW / 2;
    const y = rowY;
    const dx = Math.abs(x2 - x1);
    const lift = Math.min(90, 26 + dx * 0.18);
    const mx = (x1 + x2) / 2, my = y - lift;
    const path = svg("path", {
      d: `M${x1},${y} Q${mx},${my} ${x2},${y}`,
      class: "crs-couple",
    });
    s.appendChild(path);
    // endpoint dots
    for (const x of [x1, x2]) s.appendChild(svg("circle", { cx: x, cy: y, r: 3, class: "crs-couple-dot" }));
  }

  // root realm boxes
  for (const code of roots) {
    const x = pos.get(code), y = rowY;
    const color = realmColor(code);
    const isPre = preSet.has(code);
    const kids = childrenOf.get(code) || [];

    const g = svg("g", { class: `crs-node${isPre ? " prescribed" : ""}`, transform: `translate(${x},${y})` });
    const rect = svg("rect", {
      x: 0, y: 0, width: boxW, height: boxH, rx: 8,
      class: "crs-box", style: `--realm:${color}`,
    });
    g.appendChild(rect);

    const label = svg("text", { x: boxW / 2, y: kids.length ? 20 : boxH / 2 + 4, class: "crs-label" });
    label.textContent = realmLabel(code);
    g.appendChild(label);

    if (isPre) {
      const tag = svg("text", { x: boxW / 2, y: boxH - 8, class: "crs-pre-tag" });
      tag.textContent = "prescribed ^";
      g.appendChild(tag);
    }

    // embedded children as small chips along the bottom of the parent box
    if (kids.length) {
      const cw = (boxW - 12) / kids.length;
      kids.forEach((k, i) => {
        const kc = realmColor(k);
        const cg = svg("g", { transform: `translate(${6 + i * cw},${boxH - 26})` });
        cg.appendChild(svg("rect", {
          x: 0, y: 0, width: cw - 4, height: 20, rx: 5,
          class: "crs-child", style: `--realm:${kc}`,
        }));
        const t = svg("text", { x: (cw - 4) / 2, y: 14, class: "crs-child-label" });
        t.textContent = shortRealm(k);
        cg.appendChild(t);
        g.appendChild(cg);
      });
    }
    s.appendChild(g);
  }

  wrap.appendChild(s);

  // legend
  const legend = document.createElement("div");
  legend.className = "crs-legend";
  legend.innerHTML =
    `<span><i class="lg-box"></i>dynamic realm</span>` +
    `<span><i class="lg-box lg-pre"></i>prescribed (^)</span>` +
    `<span><i class="lg-child"></i>embedded</span>` +
    `<span><i class="lg-arc"></i>coupling</span>`;
  wrap.appendChild(legend);

  root.appendChild(wrap);
}

function shortRealm(code) {
  const name = toName(code);
  const map = {
    "aerosol": "aerosol", "atmospheric-chemistry": "atm-chem",
    "ocean-biogeochemistry": "ocean-bgc", "sea-ice": "sea-ice",
    "land-surface": "land", "land-ice": "land-ice",
  };
  return map[name] || realmLabel(code);
}
