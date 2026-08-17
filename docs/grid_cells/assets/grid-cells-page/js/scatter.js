// scatter.js — 2D t-SNE similarity map of grid cells.
//
// Pipeline:
//   1. Compute Gower distance between every pair of records.
//   2. Project to 2D with t-SNE using the Gower matrix as input.
//   3. One-shot 2D collision relaxation so no two nodes overlap.
//   4. Build kNN graph in the 2D layout for connecting edges.
//
// Node size = R (base) + linearly-scaled n_cells boost + hover/pin multiplier.
//
// The aside column is dual-purpose: at rest it hosts the filter controls
// (mounted by main.js via setAside), and swaps to node details on hover.
//
// Interactions
//   Hover a node   → temporary highlight + tooltip + node details in the aside
//   Leave the node → aside reverts to the filter controls (unless pinned)
//   Click a node   → pin the highlight (persists through mouseleave)
//   Click blank    → unpin
//   Scroll         → zoom in (up to 3×)
//   Row hover      → highlight matching node
//   Row click      → pin matching node
//   Row dblclick   → pin + scroll to graph

import { el, clear, attachTooltip } from "./dom.js";
import { short } from "./resolver.js";
import { termInfo, numericValue } from "./schema.js";

// ---- geometry --------------------------------------------------------------
const W = 500, H = 500;
const R = 3;                     // base node radius
const PAD = 22;                  // margin from viewBox edge
const GAP = 2;                   // extra spacing between node edges
const KNN = 1;                   // links per node
const COLOUR_KEY = "grid_type";

const MIN_ZOOM = 1;
// Raised from 3: with drag-to-pan, deeper zoom is usable for dense clusters.
const MAX_ZOOM = 12;

// t-SNE knobs
const TSNE_ITERS = 320;
const CHUNK = 25;

// ---- palette ---------------------------------------------------------------
// 16 well-separated hues — one per grid_type with a spare. Colours are
// assigned by descending frequency, so the most common types get the most
// distinguishable colours at the top of the list.
//   cubed-sphere, displaced-pole, hierarchical-discrete-global-grid,
//   icosahedral-geodesic, icosahedral-geodesic-dual, linear-spectral-gaussian,
//   plane-projection, reduced-gaussian, regular-gaussian,
//   regular-latitude-longitude, spectral-gaussian, spectral-reduced-gaussian,
//   tripolar, unstructured-triangular, yin-yang  (15) + 1 spare
const PALETTE = [
  "#1c7ed6", // blue
  "#f76707", // orange
  "#12b886", // teal
  "#e64980", // pink
  "#7048e8", // violet
  "#f59f00", // amber
  "#82c91e", // lime
  "#15aabf", // cyan
  "#d6336c", // raspberry
  "#e8590c", // burnt orange
  "#0ca678", // emerald
  "#be4bdb", // magenta
  "#f03e3e", // red
  "#4c6ef5", // indigo
  "#087f5b", // deep teal
  "#9c36b5", // deep purple
];
const OTHER_COLOUR = "#adb5bd";

const isNil = v => v == null || (typeof v === "string" && !v.trim());
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const prettyKey = k => String(k).replace(/^@/, "").replace(/[_-]+/g, " ").replace(/\b\w/g, c => c.toUpperCase());

// ---- feature selection -----------------------------------------------------
const NEVER_PROJECT = new Set([
  "@id", "@context", "@type", "type", "id", "validation_key",
  "ui_label", "alias", "name", "label",
  "description", "notes", "comment", "comments",
]);

// ---- Gower distance --------------------------------------------------------
function gowerDistance(rows, columns) {
  const numCols = columns.filter(c => c.kind === "numeric" && !NEVER_PROJECT.has(c.key));
  const catCols = columns.filter(c => c.kind === "category" && !NEVER_PROJECT.has(c.key));

  const numRanges = numCols.map(c => {
    let mn = Infinity, mx = -Infinity;
    for (const r of rows) {
      const v = numericValue(r[c.key]);
      if (v == null) continue;
      if (v < mn) mn = v;
      if (v > mx) mx = v;
    }
    const range = (isFinite(mn) && isFinite(mx)) ? (mx - mn) : 0;
    return { key: c.key, range: range || 1 };
  });

  const numVals = rows.map(r => numRanges.map(({ key }) => numericValue(r[key])));
  const catVals = rows.map(r => catCols.map(c => {
    const t = termInfo(r[c.key]);
    return t ? t.label : null;
  }));

  const n = rows.length;
  const D = new Float64Array(n * n);
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      let sum = 0, count = 0;
      for (let k = 0; k < numRanges.length; k++) {
        const a = numVals[i][k], b = numVals[j][k];
        if (a == null || b == null) continue;
        sum += Math.abs(a - b) / numRanges[k].range;
        count++;
      }
      for (let k = 0; k < catCols.length; k++) {
        const a = catVals[i][k], b = catVals[j][k];
        if (a == null || b == null) continue;
        sum += a === b ? 0 : 1;
        count++;
      }
      const d = count ? sum / count : 0;
      D[i * n + j] = d;
      D[j * n + i] = d;
    }
  }
  return D;
}

// ---- seeded RNG (used for the random init) ---------------------------------
function mulberry32(a) {
  return function () {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
function gauss(rng) {
  let u = 0, v = 0;
  while (u === 0) u = rng();
  while (v === 0) v = rng();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

// ---- t-SNE probability matrix from a distance matrix ----------------------
function distToProb(Dsq, n, perplexity) {
  const P = new Float64Array(n * n);
  const logU = Math.log(perplexity);
  const row = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    let beta = 1, betamin = -Infinity, betamax = Infinity;
    for (let iter = 0; iter < 60; iter++) {
      let sum = 0;
      for (let j = 0; j < n; j++) {
        if (i === j) { row[j] = 0; continue; }
        const p = Math.exp(-Dsq[i * n + j] * beta);
        row[j] = p; sum += p;
      }
      if (sum <= 0) sum = 1e-12;
      let Hh = 0;
      for (let j = 0; j < n; j++) {
        const p = row[j] / sum;
        if (p > 1e-12) Hh -= p * Math.log(p);
      }
      if (Math.abs(Hh - logU) < 1e-5) break;
      if (Hh > logU) {
        betamin = beta;
        beta = betamax === Infinity ? beta * 2 : (beta + betamax) / 2;
      } else {
        betamax = beta;
        beta = betamin === -Infinity ? beta / 2 : (beta + betamin) / 2;
      }
    }
    let sum = 0;
    for (let j = 0; j < n; j++) sum += row[j];
    if (sum <= 0) sum = 1e-12;
    for (let j = 0; j < n; j++) P[i * n + j] = row[j] / sum;
  }
  const S = new Float64Array(n * n);
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      S[i * n + j] = Math.max((P[i * n + j] + P[j * n + i]) / (2 * n), 1e-12);
    }
  }
  return S;
}

// ---- 2D t-SNE (incremental stepper) ----------------------------------------
// .Y, .step(), .iter, .total — same interface used elsewhere in this module.
function makeTsne2d(D, n, { perplexity = 20, seed = 7, iters = TSNE_ITERS } = {}) {
  const rng = mulberry32(seed);
  const Y = [], grad = [], vel = [], gains = [];
  for (let i = 0; i < n; i++) {
    Y.push([gauss(rng) * 1e-4, gauss(rng) * 1e-4]);
    grad.push([0, 0]); vel.push([0, 0]); gains.push([1, 1]);
  }
  if (n < 3) return { Y, step: () => true, iter: 0, total: 0 };

  const Dsq = new Float64Array(n * n);
  for (let i = 0; i < n * n; i++) Dsq[i] = D[i] * D[i];
  const perp = Math.max(2, Math.min(perplexity, Math.floor((n - 1) / 3)));
  const P = distToProb(Dsq, n, perp);
  const num = new Float64Array(n * n);
  const eta = 200;
  let iter = 0;

  function step() {
    const exag = iter < 100 ? 4 : 1;
    const momentum = iter < 250 ? 0.5 : 0.8;

    let sumQ = 0;
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        const dx = Y[i][0] - Y[j][0], dy = Y[i][1] - Y[j][1];
        const q = 1 / (1 + dx * dx + dy * dy);
        num[i * n + j] = q; num[j * n + i] = q;
        sumQ += 2 * q;
      }
    }
    if (sumQ <= 0) sumQ = 1e-12;

    for (let i = 0; i < n; i++) {
      let gx = 0, gy = 0;
      for (let j = 0; j < n; j++) {
        if (i === j) continue;
        const nij = num[i * n + j];
        const q = nij / sumQ;
        const mult = (P[i * n + j] * exag - q) * nij;
        gx += 4 * mult * (Y[i][0] - Y[j][0]);
        gy += 4 * mult * (Y[i][1] - Y[j][1]);
      }
      grad[i][0] = gx; grad[i][1] = gy;
    }
    for (let i = 0; i < n; i++) {
      for (let d = 0; d < 2; d++) {
        const same = (grad[i][d] > 0) === (vel[i][d] > 0);
        gains[i][d] = same ? gains[i][d] * 0.8 : gains[i][d] + 0.2;
        if (gains[i][d] < 0.01) gains[i][d] = 0.01;
        vel[i][d] = momentum * vel[i][d] - eta * gains[i][d] * grad[i][d];
        Y[i][d] += vel[i][d];
      }
    }
    let mx = 0, my = 0;
    for (let i = 0; i < n; i++) { mx += Y[i][0]; my += Y[i][1]; }
    mx /= n; my /= n;
    for (let i = 0; i < n; i++) { Y[i][0] -= mx; Y[i][1] -= my; }

    iter++;
    return iter >= iters;
  }

  return { Y, step, get iter() { return iter; }, total: iters };
}

// ---- fit 2D to the viewBox -------------------------------------------------
function fitToBox(Y, w, h, pad) {
  if (!Y.length) return [];
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (const p of Y) {
    if (p[0] < minX) minX = p[0]; if (p[0] > maxX) maxX = p[0];
    if (p[1] < minY) minY = p[1]; if (p[1] > maxY) maxY = p[1];
  }
  const sx = (maxX - minX) || 1, sy = (maxY - minY) || 1;
  const iw = w - pad * 2, ih = h - pad * 2;
  return Y.map(p => ({
    x: pad + ((p[0] - minX) / sx) * iw,
    y: pad + ((p[1] - minY) / sy) * ih,
  }));
}

// ---- one-shot 2D collision relaxation -------------------------------------
// Runs once at build time. Per-pair minimum distance accounts for the
// log-scaled n_cells size boost so the collision radius matches display.
function relax2d(pts, sizes, { w, h, pad, iters = 400 } = {}) {
  const cell = Math.max(...sizes) * 2 + GAP;
  for (let it = 0; it < iters; it++) {
    let moved = false;
    const grid = new Map();
    for (let i = 0; i < pts.length; i++) {
      const k = `${Math.floor(pts[i].x / cell)},${Math.floor(pts[i].y / cell)}`;
      let b = grid.get(k); if (!b) { b = []; grid.set(k, b); }
      b.push(i);
    }
    for (let i = 0; i < pts.length; i++) {
      const a = pts[i];
      const cx = Math.floor(a.x / cell), cy = Math.floor(a.y / cell);
      for (let gx = cx - 1; gx <= cx + 1; gx++) {
        for (let gy = cy - 1; gy <= cy + 1; gy++) {
          const b = grid.get(`${gx},${gy}`);
          if (!b) continue;
          for (const j of b) {
            if (j <= i) continue;
            const o = pts[j];
            const minD = sizes[i] + sizes[j] + GAP;
            let dx = o.x - a.x, dy = o.y - a.y;
            let d = Math.sqrt(dx * dx + dy * dy);
            if (d === 0) { dx = 0.01; dy = 0.007; d = 0.0122; }
            if (d < minD) {
              const push = ((minD - d) / 2) / d;
              a.x -= dx * push; a.y -= dy * push;
              o.x += dx * push; o.y += dy * push;
              moved = true;
            }
          }
        }
      }
    }
    for (const p of pts) { p.x = clamp(p.x, pad, w - pad); p.y = clamp(p.y, pad, h - pad); }
    if (!moved) break;
  }
  return pts;
}

// ---- kNN edges in the 2D projection ----------------------------------------
function knnEdges(pts, k) {
  const n = pts.length;
  if (n < 2) return [];
  const box = W * H;
  const cell = Math.max(30, Math.sqrt(box / n) * 0.9);
  const grid = new Map();
  const key = (gx, gy) => `${gx},${gy}`;
  for (let i = 0; i < n; i++) {
    const kk = key(Math.floor(pts[i].x / cell), Math.floor(pts[i].y / cell));
    let b = grid.get(kk); if (!b) { b = []; grid.set(kk, b); }
    b.push(i);
  }
  const seen = new Set();
  const edges = [];
  for (let i = 0; i < n; i++) {
    const a = pts[i];
    const cx = Math.floor(a.x / cell), cy = Math.floor(a.y / cell);
    let candidates = [];
    for (let radius = 1; candidates.length < k + 1 && radius <= 6; radius++) {
      candidates = [];
      for (let gx = cx - radius; gx <= cx + radius; gx++) {
        for (let gy = cy - radius; gy <= cy + radius; gy++) {
          const b = grid.get(key(gx, gy));
          if (b) for (const j of b) if (j !== i) candidates.push(j);
        }
      }
    }
    if (candidates.length < k) {
      candidates = [];
      for (let j = 0; j < n; j++) if (j !== i) candidates.push(j);
    }
    const dists = candidates.map(j => {
      const dx = pts[j].x - a.x, dy = pts[j].y - a.y;
      return { j, d: Math.sqrt(dx * dx + dy * dy) };
    });
    dists.sort((p, q) => p.d - q.d);
    for (let m = 0; m < Math.min(k, dists.length); m++) {
      const { j, d } = dists[m];
      const pair = i < j ? `${i}-${j}` : `${j}-${i}`;
      if (seen.has(pair)) continue;
      seen.add(pair);
      edges.push({ i: Math.min(i, j), j: Math.max(i, j), d });
    }
  }
  return edges;
}

// ---- per-node n_cells size boost (linear scaling) --------------------------
// n_cells is normalised directly (no log) to [0, NCELLS_BOOST]. Falls back
// to 0 when n_cells is missing or non-positive.
const NCELLS_BOOST = 4;
function buildNCellsBoost(rows) {
  const vals = rows.map(r => {
    const v = Math.log(numericValue(r && r.n_cells||1))**5;

    return v != null && v > 0 ? v : null;
  });
  const valid = vals.filter(v => v != null);
  if (!valid.length) return new Array(rows.length).fill(0);
  let mn = Infinity, mx = -Infinity;
  for (const v of valid) { if (v < mn) mn = v; if (v > mx) mx = v; }
  const span = (mx - mn) || 1;
  return vals.map(v => v == null ? 0 : NCELLS_BOOST * (v - mn) / span);
}

// ---- legend acronyms -------------------------------------------------------
// Collapsed, the legend shows one initial per word ("regular-latitude-longitude"
// → "RLL") so the column stays narrow. Some grid types share initials —
// reduced-gaussian and regular-gaussian both reduce to "RG" — so any colliding
// labels grow the first word's prefix until every acronym in the set is unique
// ("RedG" / "RegG"). Labels may arrive hyphenated or spaced, so split on both.
function buildAcronyms(labels) {
  const wordsOf = l => String(l).split(/[\s_/-]+/).filter(Boolean);
  const at = (l, depth) => {
    const ws = wordsOf(l);
    if (!ws.length) return "?";
    const head = ws[0].slice(0, depth);
    const capped = head.charAt(0).toUpperCase() + head.slice(1).toLowerCase();
    return capped + ws.slice(1).map(w => w.charAt(0).toUpperCase()).join("");
  };

  const out = new Map();
  const taken = new Set();
  let pool = [...new Set(labels)];

  for (let depth = 1; depth <= 8 && pool.length; depth++) {
    const groups = new Map();
    for (const l of pool) {
      const a = at(l, depth);
      if (!groups.has(a)) groups.set(a, []);
      groups.get(a).push(l);
    }
    const stuck = [];
    for (const [a, g] of groups) {
      if (g.length === 1 && !taken.has(a)) { out.set(g[0], a); taken.add(a); }
      else stuck.push(...g);
    }
    pool = stuck;
  }
  // Anything still ambiguous after eight characters falls back to a suffix.
  pool.forEach((l, i) => out.set(l, at(l, 8) + (i + 1)));
  return out;
}

// ---- colour mapping --------------------------------------------------------
function buildColourMap(rows) {
  const counts = new Map();
  for (const rec of rows) {
    const t = termInfo(rec[COLOUR_KEY]);
    const label = t && t.label ? t.label : "Unspecified";
    counts.set(label, (counts.get(label) || 0) + 1);
  }
  const ordered = [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  const map = new Map();
  ordered.forEach(([label], i) => {
    map.set(label, i < PALETTE.length ? PALETTE[i] : OTHER_COLOUR);
  });
  return { map, ordered };
}

// ---- public API ------------------------------------------------------------
export function createScatter(columns, rows, { onHoverNode, onLeaveNode, onSelectNode } = {}) {
  const { map: colourOf, ordered } = buildColourMap(rows);
  const nCellsBoost = buildNCellsBoost(rows);

  const SVGNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(SVGNS, "svg");
  svg.setAttribute("class", "gc-scatter-svg");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", "Similarity map of grid cells");

  const defs = document.createElementNS(SVGNS, "defs");
  defs.innerHTML = `
    <radialGradient id="gc-node-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="currentColor" stop-opacity="0.5"/>
      <stop offset="60%" stop-color="currentColor" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="currentColor" stop-opacity="0"/>
    </radialGradient>
    <filter id="gc-node-shadow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="1.2"/>
      <feOffset dy="0.6" result="offblur"/>
      <feComponentTransfer><feFuncA type="linear" slope="0.35"/></feComponentTransfer>
      <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>`;
  svg.appendChild(defs);

  const edgeLayer = document.createElementNS(SVGNS, "g");
  const glowLayer = document.createElementNS(SVGNS, "g");
  const nodeLayer = document.createElementNS(SVGNS, "g");
  svg.appendChild(edgeLayer);
  svg.appendChild(glowLayer);
  svg.appendChild(nodeLayer);

  const status = el("span", { class: "gc-scatter-status" }, "Computing…");

  // Reset control — restores zoom AND pan origin. Disabled while already at
  // the default view. Declared before applyZoom() first runs.
  const zoomReset = el("button", {
    class: "gc-zoom-reset", type: "button", disabled: true,
    title: "Reset zoom and pan",
    onclick: ev => { ev.preventDefault(); ev.stopPropagation(); resetZoom(); },
  }, "Reset view");

  // Legend is minimal by default — colour dot, acronym and count — so the
  // aside column has room for the filter controls. The toggle expands it to
  // reveal the full grid-type names; hovering any row shows the name anyway.
  const acronymOf = buildAcronyms(ordered.map(([label]) => label));
  const legendList = el("div", { class: "gc-legend-list" });
  ordered.forEach(([label, count]) => {
    const item = el("span", { class: "gc-legend-item" }, [
      el("span", { class: "gc-legend-dot", style: `background:${colourOf.get(label)}` }),
      el("span", { class: "gc-legend-acr" }, acronymOf.get(label) || "?"),
      el("span", { class: "gc-legend-label" }, `${label}`),
      el("span", { class: "gc-legend-count" }, `${count}`),
    ]);
    attachTooltip(item, `${label} — ${count}`);
    legendList.appendChild(item);
  });

  const legend = el("div", { class: "gc-scatter-legend" });
  const legendToggle = el("button", {
    class: "gc-legend-toggle", type: "button",
    "aria-expanded": "false", title: "Show grid type names",
    onclick: () => {
      const open = legend.classList.toggle("expanded");
      legendToggle.setAttribute("aria-expanded", String(open));
      legendToggle.setAttribute("title", open ? "Hide grid type names" : "Show grid type names");
      legendToggle.firstChild.textContent = open ? "Hide" : "Expand";
    },
  }, [el("span", { class: "gc-legend-caret" }, "Expand")]);
  legend.append(legendToggle, legendList);

  // The aside column is dual-purpose. At rest it hosts the filter controls
  // (mounted later via setAside); while a node is hovered or pinned it shows
  // that node's details instead. Both slots stay in the DOM and are toggled
  // with `hidden`, so filter state, scroll position and focus all survive.
  const detailFilters = el("div", { class: "gc-detail-filters" });
  const detailNode = el("div", { class: "gc-detail-node" }, [
    el("p", { class: "gc-detail-placeholder" }, "Hover a node to see its details."),
  ]);
  const detailPanel = el("div", { class: "gc-scatter-detail" }, [detailFilters, detailNode]);
  let hasAside = false;   // true once filter controls are mounted here

  const summary = document.createElement("summary");
  summary.className = "gc-scatter-summary";
  // No figure title — the caret plus the status line (node/link counts and the
  // zoom hint) are enough to identify and operate the panel.
  summary.append(
    el("span", { class: "gc-scatter-caret", "aria-hidden": "true" }, "▸"),
    status,
    zoomReset,
  );

  const details = document.createElement("details");
  details.className = "gc-scatter-card";
  details.open = true;
  details.append(
    summary,
    el("div", { class: "gc-scatter-body" }, [
      el("div", { class: "gc-scatter-plot" }, [svg]),
      legend,
      detailPanel,
    ]),
  );

  const root = details;

  // ---------- state ----------
  const nodeById = new Map();
  const edgeEls = [];
  let visible = null;
  let zoom = 1;
  // Viewport origin in user space. Previously the viewBox was always centred
  // ((W - size) / 2), so zooming pulled toward the middle of the plot rather
  // than toward the cursor. Tracking the origin explicitly lets us anchor.
  let vx = 0, vy = 0;
  let pinnedId = null;

  const recById = new Map();
  rows.forEach(r => recById.set(short(r["@id"]), r));

  // ---------- details panel ----------
  // `force` is set by explicit actions (click / pin / restoring a pin). A plain
  // hover is not forced, so it won't yank the filter UI away while the user is
  // typing into one of the filter controls.
  function showDetail(id, force = false) {
    const rec = recById.get(id);
    if (!rec) return;
    if (!force && hasAside && detailFilters.contains(document.activeElement)) return;
    const alias = isNil(rec.alias) ? "" : (Array.isArray(rec.alias) ? rec.alias.join(", ") : String(rec.alias));
    const uiLabel = isNil(rec.ui_label) ? "" : String(rec.ui_label);
    const description = isNil(rec.description) ? "" : String(rec.description);
    const gridType = termInfo(rec[COLOUR_KEY]);
    const gridTypeLabel = gridType && gridType.label ? gridType.label : "";

    const previewKeys = ["n_cells", "truncation_number", "x_resolution", "y_resolution", "grid_mapping", "region"];
    const previewRows = [];
    for (const k of previewKeys) {
      const v = rec[k];
      if (isNil(v)) continue;
      let display;
      if (typeof v === "number") display = v.toLocaleString();
      else { const t = termInfo(v); display = t ? t.label : String(v); }
      previewRows.push({ key: k, display });
    }

    clear(detailNode);
    detailNode.append(
      el("div", { class: "gc-detail-head" }, [
        el("code", { class: "gc-detail-id" }, id),
        alias ? el("span", { class: "gc-detail-alias" }, alias) : null,
      ].filter(Boolean)),
      gridTypeLabel ? el("div", { class: "gc-detail-type" }, [
        el("span", { class: "gc-legend-dot", style: `background:${colourOf.get(gridTypeLabel) || OTHER_COLOUR}` }),
        el("span", {}, gridTypeLabel),
      ]) : null,
      uiLabel ? el("p", { class: "gc-detail-ui-label" }, uiLabel) : null,
      description ? el("p", { class: "gc-detail-description" }, description) : null,
      previewRows.length ? el("dl", { class: "gc-detail-fields" },
        previewRows.flatMap(({ key, display }) => [
          el("dt", {}, prettyKey(key)),
          el("dd", {}, display),
        ])
      ) : null,
    );
    if (hasAside) { detailFilters.hidden = true; detailNode.hidden = false; }
  }

  // Resting state: show the filter controls if they've been mounted here,
  // otherwise fall back to the original "hover a node" placeholder.
  function clearDetail() {
    clear(detailNode);
    if (hasAside) {
      detailNode.hidden = true;
      detailFilters.hidden = false;
    } else {
      detailNode.hidden = false;
      detailNode.append(el("p", { class: "gc-detail-placeholder" }, "Hover a node to see its details."));
    }
  }

  // Mount arbitrary content (the filter controls) as the aside's resting state.
  function setAside(node) {
    clear(detailFilters);
    detailFilters.appendChild(node);
    hasAside = true;
    clearDetail();
  }

  // ---------- highlight ----------
  function setActive(id) {
    nodeById.forEach(({ node, glow }) => {
      node.classList.remove("active", "linked", "muted");
      glow.classList.remove("visible");
      if (node.dataset.baseR) node.setAttribute("r", node.dataset.baseR);
    });
    edgeEls.forEach(l => l.classList.remove("linked", "muted"));

    if (id == null) return;
    const entry = nodeById.get(id);
    if (!entry) return;
    entry.node.classList.add("active");
    entry.glow.classList.add("visible");
    // scale active/linked nodes up on top of their base radius
    const baseR = parseFloat(entry.node.dataset.baseR || R);
    entry.node.setAttribute("r", (baseR * 1.4).toFixed(2));

    nodeById.forEach(({ node }, key) => {
      if (key === id) return;
      if (entry.neighbours.has(key)) {
        node.classList.add("linked");
        const br = parseFloat(node.dataset.baseR || R);
        node.setAttribute("r", (br * 1.2).toFixed(2));
      }
      else node.classList.add("muted");
    });
    edgeEls.forEach(l => {
      if (l.dataset.a === id || l.dataset.b === id) l.classList.add("linked");
      else l.classList.add("muted");
    });
    nodeLayer.appendChild(entry.node);
  }

  function applyVisibility() {
    nodeById.forEach(({ node, glow }, id) => {
      const on = !visible || visible.has(id);
      node.classList.toggle("filtered-out", !on);
      glow.classList.toggle("filtered-out", !on);
    });
    edgeEls.forEach(l => {
      const on = !visible || (visible.has(l.dataset.a) && visible.has(l.dataset.b));
      l.classList.toggle("filtered-out", !on);
    });
  }

  // ---------- zoom / pan ----------
  // Cursor-anchored: the point under the pointer stays fixed while scaling.
  // Solve for the new origin so that userPoint maps to the same screen spot:
  //   vx' = px - (px - vx) * (newSize / oldSize)
  function applyZoom() {
    const size = W / zoom;
    // keep the viewport inside the plot bounds
    const maxOff = Math.max(0, W - size);
    vx = clamp(vx, 0, maxOff);
    vy = clamp(vy, 0, maxOff);
    svg.setAttribute("viewBox", `${vx} ${vy} ${size} ${size}`);
    if (zoomReset) zoomReset.disabled = zoom === 1 && vx === 0 && vy === 0;
  }

  // Pointer position in SVG user space (accounts for viewBox + CSS scaling).
  function userPoint(ev) {
    const r = svg.getBoundingClientRect();
    const size = W / zoom;
    // preserveAspectRatio="xMidYMid meet" with a square viewBox: the rendered
    // content is a centred square of side min(rect.w, rect.h).
    const side = Math.min(r.width, r.height);
    const offX = r.left + (r.width - side) / 2;
    const offY = r.top + (r.height - side) / 2;
    return {
      x: vx + ((ev.clientX - offX) / side) * size,
      y: vy + ((ev.clientY - offY) / side) * size,
    };
  }

  svg.addEventListener("wheel", ev => {
    ev.preventDefault();
    const p = userPoint(ev);
    const oldSize = W / zoom;
    const factor = ev.deltaY > 0 ? 0.9 : 1.1;
    zoom = clamp(zoom * factor, MIN_ZOOM, MAX_ZOOM);
    const newSize = W / zoom;
    // anchor on the cursor
    vx = p.x - (p.x - vx) * (newSize / oldSize);
    vy = p.y - (p.y - vy) * (newSize / oldSize);
    applyZoom();
  }, { passive: false });

  // Drag to pan. A movement threshold keeps the existing background-click
  // (unpin) and node-click handlers working — a click is not a drag.
  let panning = false, panStart = null, panMoved = false;
  svg.addEventListener("pointerdown", ev => {
    if (ev.button !== 0) return;
    panning = true; panMoved = false;
    panStart = { cx: ev.clientX, cy: ev.clientY, vx, vy };
  });
  svg.addEventListener("pointermove", ev => {
    if (!panning) return;
    const dx = ev.clientX - panStart.cx, dy = ev.clientY - panStart.cy;
    if (!panMoved && Math.hypot(dx, dy) < 4) return;   // below threshold = click
    panMoved = true;
    svg.setPointerCapture(ev.pointerId);
    const r = svg.getBoundingClientRect();
    const side = Math.min(r.width, r.height);
    const scale = (W / zoom) / side;
    vx = panStart.vx - dx * scale;
    vy = panStart.vy - dy * scale;
    applyZoom();
  });
  function endPan(ev) {
    if (!panning) return;
    panning = false;
    if (ev && ev.pointerId != null && svg.hasPointerCapture?.(ev.pointerId)) {
      svg.releasePointerCapture(ev.pointerId);
    }
  }
  svg.addEventListener("pointerup", endPan);
  svg.addEventListener("pointercancel", endPan);

  function resetZoom() {
    zoom = 1; vx = 0; vy = 0;
    applyZoom();
  }

  // SVG mouseleave restores pinned view (or clears)
  svg.addEventListener("mouseleave", () => {
    if (pinnedId != null) { setActive(pinnedId); showDetail(pinnedId, true); }
    else { setActive(null); clearDetail(); }
  });

  // Background click unpins (node clicks stopPropagation, so this is safe).
  // Suppressed after a pan drag — releasing the mouse at the end of a drag
  // must not be read as a click.
  svg.addEventListener("click", () => {
    if (panMoved) { panMoved = false; return; }
    if (pinnedId != null) {
      pinnedId = null;
      setActive(null); clearDetail();
    }
  });

  // ---------- draw ----------
  function drawGraph(pts) {
    clear(edgeLayer); clear(glowLayer); clear(nodeLayer);
    nodeById.clear(); edgeEls.length = 0;

    const edges = knnEdges(pts, KNN);
    edges.sort((a, b) => b.d - a.d);
    const maxD = edges.length ? edges[0].d : 1;
    const idFor = idx => short(rows[idx]["@id"]);

    const neighbours = new Map();
    const addN = (a, b) => {
      if (!neighbours.has(a)) neighbours.set(a, new Set());
      neighbours.get(a).add(b);
    };
    for (const e of edges) { addN(idFor(e.i), idFor(e.j)); addN(idFor(e.j), idFor(e.i)); }

    for (const e of edges) {
      const line = document.createElementNS(SVGNS, "line");
      line.setAttribute("class", "gc-edge");
      line.setAttribute("x1", pts[e.i].x.toFixed(2));
      line.setAttribute("y1", pts[e.i].y.toFixed(2));
      line.setAttribute("x2", pts[e.j].x.toFixed(2));
      line.setAttribute("y2", pts[e.j].y.toFixed(2));
      const strength = 1 - e.d / (maxD * 1.15);
      line.setAttribute("stroke-opacity", (0.08 + strength * 0.18).toFixed(3));
      line.setAttribute("stroke-width", (0.6 + strength * 0.8).toFixed(2));
      line.dataset.a = idFor(e.i);
      line.dataset.b = idFor(e.j);
      edgeLayer.appendChild(line);
      edgeEls.push(line);
    }

    rows.forEach((rec, i) => {
      const id = short(rec["@id"]);
      const t = termInfo(rec[COLOUR_KEY]);
      const label = t && t.label ? t.label : "Unspecified";
      const colour = colourOf.get(label) || OTHER_COLOUR;
      const r = R + nCellsBoost[i];

      const glow = document.createElementNS(SVGNS, "circle");
      glow.setAttribute("class", "gc-glow");
      glow.setAttribute("cx", pts[i].x.toFixed(2));
      glow.setAttribute("cy", pts[i].y.toFixed(2));
      glow.setAttribute("r", (r * 2.6).toFixed(2));
      glow.setAttribute("fill", "url(#gc-node-glow)");
      glow.setAttribute("color", colour);
      glowLayer.appendChild(glow);

      const c = document.createElementNS(SVGNS, "circle");
      c.setAttribute("class", "gc-node");
      c.setAttribute("cx", pts[i].x.toFixed(2));
      c.setAttribute("cy", pts[i].y.toFixed(2));
      c.setAttribute("r", r.toFixed(2));
      c.setAttribute("fill", colour);
      c.dataset.id = id;
      c.dataset.type = label;
      c.dataset.baseR = r.toFixed(2);

      // No tooltip on nodes — hovering surfaces the full record in the aside
      // column instead, so a floating tooltip would just duplicate it.
      c.addEventListener("mouseenter", () => {
        setActive(id); showDetail(id); onHoverNode && onHoverNode(id);
      });
      c.addEventListener("mouseleave", () => {
        if (pinnedId != null) { setActive(pinnedId); showDetail(pinnedId, true); }
        else { setActive(null); clearDetail(); }
        onLeaveNode && onLeaveNode();
      });
      c.addEventListener("click", ev => {
        ev.stopPropagation();
        if (pinnedId === id) {
          pinnedId = null;
          setActive(null); clearDetail();
        } else {
          pinnedId = id;
          setActive(id); showDetail(id, true);
        }
        onSelectNode && onSelectNode(id);
      });

      nodeLayer.appendChild(c);
      nodeById.set(id, { node: c, glow, neighbours: neighbours.get(id) || new Set() });
    });
    applyVisibility();
  }

  // ---------- compute t-SNE in chunks ----------
  const D = gowerDistance(rows, columns);
  const dr = makeTsne2d(D, rows.length, { perplexity: 20, seed: 7 });

  function runChunk() {
    let done = false;
    for (let k = 0; k < CHUNK && !done; k++) done = dr.step();
    if (dr.total) {
      const pct = Math.min(100, Math.round((dr.iter / dr.total) * 100));
      status.textContent = done ? "" : `Computing… ${pct}%`;
    }
    if (done) {
      const fitted = fitToBox(dr.Y, W, H, PAD + R + NCELLS_BOOST);
      // per-node sizes for collision detection = base + n_cells boost
      const sizes = rows.map((_, i) => R + nCellsBoost[i]);
      const pts = relax2d(fitted, sizes, { w: W, h: H, pad: PAD + R + NCELLS_BOOST });
      drawGraph(pts);
      status.textContent = `${rows.length} grid cells · ${edgeEls.length} links · scroll to zoom`;
    } else {
      requestAnimationFrame(runChunk);
    }
  }
  requestAnimationFrame(() => requestAnimationFrame(runChunk));

  return {
    root,
    highlight: id => setActive(id),
    clearHighlight: () => {
      if (pinnedId != null) setActive(pinnedId);
      else setActive(null);
    },
    pin(id) {
      if (pinnedId === id) {
        pinnedId = null;
        setActive(null); clearDetail();
      } else if (nodeById.has(id)) {
        pinnedId = id;
        setActive(id); showDetail(id, true);
      }
    },
    setVisible(ids) { visible = ids; applyVisibility(); },
    setAside,
  };
}
