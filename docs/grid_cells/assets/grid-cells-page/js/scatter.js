// scatter.js — PCoA → t-SNE hybrid similarity map of grid cells.
//
// Pipeline:
//   1. Compute Gower distance between every pair of records. Gower is
//      designed for mixed numeric/categorical data.
//   2. Run PCoA (classical MDS on Gower) for a globally-correct 2-D layout
//      and record its variance-explained numbers.
//   3. Refine that layout with t-SNE seeded from the PCoA coordinates. Since
//      the initialisation is already globally sensible, t-SNE only tightens
//      the local clusters instead of rearranging the whole plot from noise.
//      This gives sharper cluster separation than PCoA alone while preserving
//      the meaningful global topology PCoA provides.
//   4. Relax with collision detection so no two nodes overlap.
//   5. Link every node to its k nearest neighbours in the projection.
//
// The status line reports PCoA's variance-explained (a real metric) plus a
// note that t-SNE has refined the layout.
//
// Colour is by grid type using a hand-picked palette.
// Hover a node → tooltip with grid id + alias + type; detail panel opens.
// Click a node → scroll the matching table row into view + open its detail.

import { el, clear, attachTooltip } from "./dom.js";
import { short } from "./resolver.js";
import { termInfo, numericValue } from "./schema.js";

// ---- geometry --------------------------------------------------------------
const W = 500, H = 500;          // square plot area
const R = 6;                     // node radius
const PAD = 18;                  // keep nodes inside this margin
const GAP = 2;                   // extra spacing between node edges
const KNN = 3;                   // links per node
const COLOUR_KEY = "grid_type";

// ---- palette ---------------------------------------------------------------
const PALETTE = [
  "#4c6ef5", "#f76707", "#12b886", "#e64980", "#7048e8", "#f59f00",
  "#0ca678", "#d6336c", "#1c7ed6", "#845ef7", "#82c91e", "#e8590c",
];
const OTHER_COLOUR = "#adb5bd";

const isNil = v => v == null || (typeof v === "string" && !v.trim());
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const prettyKey = k => String(k).replace(/^@/, "").replace(/[_-]+/g, " ").replace(/\b\w/g, c => c.toUpperCase());

// ---- feature selection -----------------------------------------------------
// Only *faceted* columns feed the projection — the numeric and category
// columns that have filter panels. We never project on:
//   • identifier / metadata (@id, @context, @type, type, id, validation_key)
//   • human-facing labels (ui_label, alias, name, label)
//   • free text (description, notes, comment, etc.)
const NEVER_PROJECT = new Set([
  "@id", "@context", "@type", "type", "id", "validation_key",
  "ui_label", "alias", "name", "label",
  "description", "notes", "comment", "comments",
]);

// ---- Gower distance --------------------------------------------------------
// Mixed-type distance:
//   numeric attribute k → |xᵢ − xⱼ| / range_k
//   categorical attr  k → 0 if labels match, 1 otherwise
// Contributions are averaged across attributes present on both sides.
// Missing on either side → that attribute is skipped for that pair.
function gowerDistance(rows, columns) {
  const numCols = columns.filter(c => c.kind === "numeric" && !NEVER_PROJECT.has(c.key));
  const catCols = columns.filter(c => c.kind === "category" && !NEVER_PROJECT.has(c.key));

  // per-numeric range
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

  // extract per-record numeric values and category labels for speed
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

// ---- Jacobi eigendecomposition (symmetric matrix) --------------------------
// Standard cyclic-sweep Jacobi. Returns eigenvalues and an eigenvector matrix
// where column j is the j-th eigenvector (V[i*n + j]). For n ≤ ~500 this is
// plenty fast (< 100ms) and numerically well-behaved on symmetric input.
function jacobi(source, n) {
  const A = new Float64Array(source);   // working copy — will end diagonal
  const V = new Float64Array(n * n);    // identity → accumulates rotations
  for (let i = 0; i < n; i++) V[i * n + i] = 1;

  const MAX_SWEEPS = 100;
  const TOL = 1e-10;

  for (let sweep = 0; sweep < MAX_SWEEPS; sweep++) {
    // convergence check: sum of |off-diagonal|
    let off = 0;
    for (let i = 0; i < n - 1; i++) {
      for (let j = i + 1; j < n; j++) off += Math.abs(A[i * n + j]);
    }
    if (off < TOL) break;

    // zero every off-diagonal (p, q) in one cyclic sweep
    for (let p = 0; p < n - 1; p++) {
      for (let q = p + 1; q < n; q++) {
        const apq = A[p * n + q];
        if (Math.abs(apq) < 1e-14) continue;
        const app = A[p * n + p], aqq = A[q * n + q];

        // Rotation angle
        let t;
        if (Math.abs(app - aqq) < 1e-30) {
          t = apq >= 0 ? 1 : -1;
        } else {
          const theta = (aqq - app) / (2 * apq);
          t = 1 / (Math.abs(theta) + Math.sqrt(1 + theta * theta));
          if (theta < 0) t = -t;
        }
        const c = 1 / Math.sqrt(1 + t * t);
        const s = t * c;

        // Update A
        A[p * n + p] = app - t * apq;
        A[q * n + q] = aqq + t * apq;
        A[p * n + q] = 0;
        A[q * n + p] = 0;
        for (let r = 0; r < n; r++) {
          if (r === p || r === q) continue;
          const arp = A[r * n + p], arq = A[r * n + q];
          A[r * n + p] = c * arp - s * arq;
          A[p * n + r] = A[r * n + p];
          A[r * n + q] = s * arp + c * arq;
          A[q * n + r] = A[r * n + q];
        }
        // Accumulate rotations into V
        for (let r = 0; r < n; r++) {
          const vrp = V[r * n + p], vrq = V[r * n + q];
          V[r * n + p] = c * vrp - s * vrq;
          V[r * n + q] = s * vrp + c * vrq;
        }
      }
    }
  }

  const eigenvalues = new Float64Array(n);
  for (let i = 0; i < n; i++) eigenvalues[i] = A[i * n + i];
  return { eigenvalues, eigenvectors: V };
}

// ---- PCoA (classical MDS) --------------------------------------------------
// Given a distance matrix D (n×n), returns 2-D coordinates plus the fraction
// of positive variance captured by each of the two chosen axes.
function pcoa(D, n) {
  if (n < 2) return { Y: Array.from({ length: n }, () => [0, 0]), varExplained: [0, 0] };

  // 1. squared distances
  const D2 = new Float64Array(n * n);
  for (let i = 0; i < n * n; i++) D2[i] = D[i] * D[i];

  // 2. double-centre: B_ij = -½ · (D²_ij − rowMean_i − colMean_j + grandMean)
  const rowMean = new Float64Array(n);
  let grand = 0;
  for (let i = 0; i < n; i++) {
    let s = 0;
    for (let j = 0; j < n; j++) s += D2[i * n + j];
    rowMean[i] = s / n;
    grand += s;
  }
  grand /= n * n;

  const B = new Float64Array(n * n);
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      // symmetry of D2 → colMean_j = rowMean[j]
      B[i * n + j] = -0.5 * (D2[i * n + j] - rowMean[i] - rowMean[j] + grand);
    }
  }

  // 3. eigendecompose
  const { eigenvalues, eigenvectors } = jacobi(B, n);

  // 4. sort by eigenvalue descending, keep top 2
  const idx = Array.from({ length: n }, (_, i) => i);
  idx.sort((a, b) => eigenvalues[b] - eigenvalues[a]);
  const [p1, p2] = [idx[0], idx[1] != null ? idx[1] : idx[0]];

  // 5. coordinates = eigenvector · √eigenvalue (clamp small negatives to 0)
  const Y = [];
  const s1 = Math.sqrt(Math.max(0, eigenvalues[p1]));
  const s2 = Math.sqrt(Math.max(0, eigenvalues[p2]));
  for (let i = 0; i < n; i++) {
    Y.push([eigenvectors[i * n + p1] * s1, eigenvectors[i * n + p2] * s2]);
  }

  // 6. variance explained (relative to sum of positive eigenvalues — Gower
  //    isn't strictly Euclidean, so some eigenvalues may be negative and
  //    are dropped from the total, following the standard PCoA convention).
  let posSum = 0;
  for (let i = 0; i < n; i++) if (eigenvalues[i] > 0) posSum += eigenvalues[i];
  const varExplained = posSum > 0
    ? [Math.max(0, eigenvalues[p1]) / posSum * 100,
       Math.max(0, eigenvalues[p2]) / posSum * 100]
    : [0, 0];

  return { Y, varExplained };
}

// ---- t-SNE refinement ------------------------------------------------------
// Given a distance matrix D and an initial 2-D layout Y0 (from PCoA), run
// t-SNE for a modest number of iterations. Because Y0 is already globally
// sensible, t-SNE only tightens local structure — avoiding the classic t-SNE
// pathology where random init creates spurious clusters and warps distances.
//
// Perplexity is deliberately low (15) to prioritise local sharpening.

// Distance-to-P: symmetric joint-probability matrix via per-point Gaussian
// bandwidth selected by binary search on the target perplexity.
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
  // symmetrise
  const S = new Float64Array(n * n);
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      S[i * n + j] = Math.max((P[i * n + j] + P[j * n + i]) / (2 * n), 1e-12);
    }
  }
  return S;
}

// Refine an initial 2-D layout with t-SNE gradient descent.
//   D           n×n distance matrix (Gower, in our case)
//   Y0          initial coordinates (n × 2), copied and rescaled internally
// Returns the refined coordinates.
function refineTsne(D, n, Y0, { perplexity = 15, iters = 150 } = {}) {
  if (n < 3) return Y0.map(p => p.slice());

  // t-SNE conventionally works on squared distances.
  const Dsq = new Float64Array(n * n);
  for (let i = 0; i < n * n; i++) Dsq[i] = D[i] * D[i];

  // Reduce perplexity if n is small (needs perp < (n-1)/3 to make sense)
  const perp = Math.max(2, Math.min(perplexity, Math.floor((n - 1) / 3)));
  const P = distToProb(Dsq, n, perp);

  // Rescale the PCoA init so its spread matches t-SNE's expected ~1e-4 scale.
  // This is what makes early exaggeration meaningful (large initial forces).
  let maxAbs = 0;
  for (const p of Y0) {
    if (Math.abs(p[0]) > maxAbs) maxAbs = Math.abs(p[0]);
    if (Math.abs(p[1]) > maxAbs) maxAbs = Math.abs(p[1]);
  }
  const scale = maxAbs > 0 ? 1e-4 / maxAbs : 1;
  const Y = Y0.map(p => [p[0] * scale, p[1] * scale]);

  const grad = Y.map(() => [0, 0]);
  const vel  = Y.map(() => [0, 0]);
  const gains = Y.map(() => [1, 1]);
  const num = new Float64Array(n * n);
  const eta = 200;

  // Shorter exaggeration phase than usual (50 vs 100) — the init is already
  // roughly correct, so we don't need long "pull clusters together" pressure.
  const EXAG_END = Math.min(50, Math.floor(iters * 0.33));
  const MOMENTUM_SWITCH = Math.floor(iters * 0.66);

  for (let it = 0; it < iters; it++) {
    const exag = it < EXAG_END ? 4 : 1;
    const momentum = it < MOMENTUM_SWITCH ? 0.5 : 0.8;

    // low-dim Student-t affinities
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

    // gradient
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

    // adaptive-gain momentum step
    for (let i = 0; i < n; i++) {
      for (let d = 0; d < 2; d++) {
        const same = (grad[i][d] > 0) === (vel[i][d] > 0);
        gains[i][d] = same ? gains[i][d] * 0.8 : gains[i][d] + 0.2;
        if (gains[i][d] < 0.01) gains[i][d] = 0.01;
        vel[i][d] = momentum * vel[i][d] - eta * gains[i][d] * grad[i][d];
        Y[i][d] += vel[i][d];
      }
    }

    // re-centre
    let mx = 0, my = 0;
    for (let i = 0; i < n; i++) { mx += Y[i][0]; my += Y[i][1]; }
    mx /= n; my /= n;
    for (let i = 0; i < n; i++) { Y[i][0] -= mx; Y[i][1] -= my; }
  }

  return Y;
}

// ---- fit + collision relax -------------------------------------------------
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

// PCoA gives good positions to start with, so only a light relaxation is
// needed to separate exact overlaps and near-duplicates.
function relax(pts, r, { w, h, pad, iters = 80 } = {}) {
  const minD = r * 2 + GAP;
  const cell = minD;
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

// ---- k-nearest-neighbour graph in the projection --------------------------
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

  const SVGNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(SVGNS, "svg");
  svg.setAttribute("class", "gc-scatter-svg");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", "PCoA similarity map of grid cells, coloured by grid type");

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

  const legend = el("div", { class: "gc-scatter-legend" });
  ordered.forEach(([label, count]) => {
    legend.appendChild(el("span", { class: "gc-legend-item", title: `${label} — ${count}` }, [
      el("span", { class: "gc-legend-dot", style: `background:${colourOf.get(label)}` }),
      el("span", { class: "gc-legend-label" }, `${label}`),
      el("span", { class: "gc-legend-count" }, `${count}`),
    ]));
  });

  // Details panel — sits to the right of the legend, populated on hover.
  const detailPanel = el("div", { class: "gc-scatter-detail" }, [
    el("p", { class: "gc-detail-placeholder" }, "Hover a node to see its details."),
  ]);

  // Collapsible: <details open> with a custom-styled <summary>.
  // The summary carries the title + status; the body carries the plot + legend.
  const summary = document.createElement("summary");
  summary.className = "gc-scatter-summary";
  summary.append(
    el("span", { class: "gc-scatter-caret", "aria-hidden": "true" }, "▸"),
    el("h2", { class: "gc-scatter-title" }, "PCoA Similarity Map"),
    status,
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

  const nodeById = new Map();
  const edgeEls = [];
  let visible = null;

  // build an id->record map so the hover handler can look up details fast
  const recById = new Map();
  rows.forEach(r => recById.set(short(r["@id"]), r));

  // Populate the details panel with a compact summary of one record.
  function showDetail(id) {
    const rec = recById.get(id);
    if (!rec) return;
    const alias = isNil(rec.alias) ? "" : (Array.isArray(rec.alias) ? rec.alias.join(", ") : String(rec.alias));
    const uiLabel = isNil(rec.ui_label) ? "" : String(rec.ui_label);
    const description = isNil(rec.description) ? "" : String(rec.description);
    const gridType = termInfo(rec[COLOUR_KEY]);
    const gridTypeLabel = gridType && gridType.label ? gridType.label : "";

    // pick a few notable numeric fields to preview
    const previewKeys = ["n_cells", "truncation_number", "x_resolution", "y_resolution", "grid_mapping", "region"];
    const previewRows = [];
    for (const k of previewKeys) {
      const v = rec[k];
      if (isNil(v)) continue;
      let display;
      if (typeof v === "number") display = v.toLocaleString();
      else {
        const t = termInfo(v);
        display = t ? t.label : String(v);
      }
      previewRows.push({ key: k, display });
    }

    clear(detailPanel);
    detailPanel.append(
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
  }

  function clearDetail() {
    clear(detailPanel);
    detailPanel.append(el("p", { class: "gc-detail-placeholder" }, "Hover a node to see its details."));
  }

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

      const glow = document.createElementNS(SVGNS, "circle");
      glow.setAttribute("class", "gc-glow");
      glow.setAttribute("cx", pts[i].x.toFixed(2));
      glow.setAttribute("cy", pts[i].y.toFixed(2));
      glow.setAttribute("r", R * 2.6);
      glow.setAttribute("fill", "url(#gc-node-glow)");
      glow.setAttribute("color", colour);
      glowLayer.appendChild(glow);

      const c = document.createElementNS(SVGNS, "circle");
      c.setAttribute("class", "gc-node");
      c.setAttribute("cx", pts[i].x.toFixed(2));
      c.setAttribute("cy", pts[i].y.toFixed(2));
      c.setAttribute("r", R);
      c.setAttribute("fill", colour);
      c.dataset.id = id;
      c.dataset.type = label;

      const alias = isNil(rec.alias) ? "" : (Array.isArray(rec.alias) ? rec.alias.join(", ") : String(rec.alias));
      attachTooltip(c, `${id}${alias ? ` · ${alias}` : ""}\n${label}`);

      c.addEventListener("mouseenter", () => { setActive(id); showDetail(id); onHoverNode && onHoverNode(id); });
      c.addEventListener("mouseleave", () => { setActive(null); clearDetail(); onLeaveNode && onLeaveNode(); });
      c.addEventListener("click",       () => { onSelectNode && onSelectNode(id); });

      nodeLayer.appendChild(c);
      nodeById.set(id, { node: c, glow, neighbours: neighbours.get(id) || new Set() });
    });
    applyVisibility();
  }

  // Compute PCoA once, then refine with t-SNE for sharper local structure.
  // On a rAF pair so the page paints "Computing…" first.
  requestAnimationFrame(() => requestAnimationFrame(() => {
    const n = rows.length;
    const D = gowerDistance(rows, columns);
    const { Y: Ypcoa, varExplained } = pcoa(D, n);
    // Refine with t-SNE seeded from PCoA. If n is very small, t-SNE isn't
    // meaningful — fall back to PCoA alone.
    const Yrefined = n >= 6 ? refineTsne(D, n, Ypcoa) : Ypcoa;
    const pts = relax(fitToBox(Yrefined, W, H, PAD + R), R, { w: W, h: H, pad: PAD + R });
    drawGraph(pts);
    const pc1 = varExplained[0].toFixed(1);
    const pc2 = varExplained[1].toFixed(1);
    const refined = n >= 6 ? " · t-SNE refined" : "";
    status.textContent = `PC1 ${pc1}% · PC2 ${pc2}%${refined} · ${n} grid cells`;
  }));

  // --- highlight / visibility --------------------------------------------
  function setActive(id) {
    nodeById.forEach(({ node, glow }) => {
      node.classList.remove("active", "linked", "muted");
      glow.classList.remove("visible");
    });
    edgeEls.forEach(l => l.classList.remove("linked", "muted"));

    if (id == null) return;
    const entry = nodeById.get(id);
    if (!entry) return;
    entry.node.classList.add("active");
    entry.glow.classList.add("visible");

    nodeById.forEach(({ node }, key) => {
      if (key === id) return;
      if (entry.neighbours.has(key)) node.classList.add("linked");
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

  return {
    root,
    highlight: id => setActive(id),
    clearHighlight: () => setActive(null),
    setVisible(ids) { visible = ids; applyVisibility(); },
  };
}
