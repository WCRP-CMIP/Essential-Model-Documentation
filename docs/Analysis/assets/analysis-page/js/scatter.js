// scatter.js — 3D grid-cell similarity map with a force-directed model overlay.
//
// Layer 1 (grid cells): PCoA-initialised PaCMAP in 3D.
//   1. PCoA (classical MDS) on the Gower distance matrix — Jacobi
//      eigendecomposition of the double-centred squared-distance matrix gives
//      a deterministic globally-correct 3D starting layout.
//   2. PaCMAP refines it with three pair types (neighbour, mid-near, far)
//      and an Adam optimizer over three phases, sharpening local clusters
//      while preserving PCoA's global geography.
//   3. Final step: normalise every point to unit length so the layout lives
//      on the surface of the unit sphere — that gives the model overlay
//      a clean shell to sit on. No links are drawn between grid cells.
//
// Layer 2 (models): each model is pulled by two spring forces at once — an
// inset-target spring toward each of its linked grid cells (grid position ×
// MODEL_INSET, MODEL_INSET < 1) AND a separate, explicit spring pulling
// straight toward the centre of the sphere (0,0,0). A model with one link
// balances between that grid's inset point and the centre, settling
// partway in; a model with several divergent links is pulled toward the
// centre even more strongly, since the grid springs disagree with each
// other while the centring spring pulls consistently inward. A hard-sphere
// collision pass prevents overlap; there's no inter-model repulsion, so
// models are free to sit close together when their grids agree.
//
// Links: one curved path per (model, grid) pair, coloured by realm. No
// routing through intermediate component nodes. When a model links to the
// same grid cell more than once (e.g. two components share a grid), the
// duplicate curves are bowed apart symmetrically so each is visible.
//
// Depth cueing: every frame, grid and model nodes (and links) fade toward
// DEPTH_FADE_MIN opacity the further back they sit in the current rotation,
// on top of the existing depth-based size scaling — so the sphere reads as
// a genuine 3D volume rather than a flat disc of same-looking dots.
//
// Interactions: drag rotates, wheel zooms toward the cursor (1–3×), hover
// highlights connected items and populates a detail panel, click pins,
// restart-rotation button in the legend resumes auto-rotation.

import { el, clear, attachTooltip } from "./dom.js";
import { short } from "./resolver.js";
import { renderCrsInline } from "./crs.js";

// ==== configuration ========================================================
const W = 500, H = 500;
const PAD = 22;
const R_GRID  = 2.5;     // grid-cell node radius (base)
const R_MODEL = 4.8;     // model node radius (base)
const MIN_ZOOM = 1;
const MAX_ZOOM = 3;
const LINK_BOW_UNIT = 9;   // px of curve separation per duplicate-link offset step
// Depth cueing: nodes further from the viewer fade out. Uses fill-opacity
// (grid) / stroke-opacity (model) rather than the CSS "opacity" property, so
// it composes cleanly with .muted's opacity dimming instead of an inline
// style silently overriding it. Skipped for active/linked nodes so a
// highlighted node stays fully vivid regardless of depth.
const DEPTH_FADE_MIN = 0.3;   // opacity of the far-most node in the current view

// PaCMAP (with PCoA init)
const PACMAP_ITERS = 450;
const CHUNK = 15;
const PACMAP_K = 10;                    // neighbours per point in NB pairs

// force-directed model layer: springs pull each model toward an inset point
// on each linked grid cell (see file header), plus a separate explicit
// spring pulling every model toward the centre of the sphere — no repulsion
// between models, collision (hard-sphere non-overlap) is the only
// inter-model interaction.
const FORCE_ITERS  = 250;
const MODEL_INSET  = 0.55;   // spring target = grid position × this (< 1 pulls inward)
const MODEL_FALLBACK_R = 0.15;  // radius for models with zero resolved links
const SPRING_K     = 0.05;   // attraction toward each linked grid
const CENTER_K     = 0.025;  // attraction straight toward the sphere centre (0,0,0)
const DAMPING      = 0.82;
// Collision radius per model in 3D unit-sphere space. R_MODEL is a screen
// radius; scale = min(W,H)/2 - PAD = 228 px, so 1 unit of 3D ≈ 228 px on
// screen. A collision radius of 0.032 gives min centre-to-centre 0.064 =
// ~14.6 px, comfortably clear of the ~5-6 px on-screen model radius.
const MODEL_COLLISION_R = 0.032;
const MODEL_COLLISION_PASSES = 4;   // sub-iterations per force step

// Post-PaCMAP relaxation: nudge apart any grid points that ended up nearly
// coincident (common for identical/very similar records) to reduce visual
// overlap, re-normalising back onto the sphere after each pass. Best-effort
// — not a hard non-overlap guarantee like the model collision pass, since
// grid counts can be much larger than model counts.
const GRID_MIN_SEP = 0.05;
const GRID_RELAX_PASSES = 60;

// interaction
const DRAG_THRESHOLD = 4;
const AUTO_ROTATE_SPEED = 0.35;

// ==== palettes =============================================================
// Grid-cell colour by grid_type (same palette as grid_cells page).
const GRID_PALETTE = [
  "#4c6ef5", "#f76707", "#12b886", "#e64980", "#7048e8", "#f59f00",
  "#0ca678", "#d6336c", "#1c7ed6", "#845ef7", "#82c91e", "#e8590c",
];
const OTHER_GRID_COLOUR = "#adb5bd";

// Realm colour palette — matches docs/Model/assets/model-page/js/crs.js
// (the documentation's earth-tone spectral palette).
const REALM_PALETTE = {
  "atmosphere":              "#e76f51",
  "atmospheric-chemistry":   "#f4a261",
  "aerosol":                 "#e9c46a",
  "land-surface":            "#8ab17d",
  "land-ice":                "#7cadbe",
  "ocean":                   "#264653",
  "ocean-biogeochemistry":   "#287271",
  "sea-ice":                 "#2a9d8f",
  "river":                   "#5c8ae6",
  "iceberg":                 "#c8d5e0",
};
const OTHER_REALM_COLOUR = "#868e96";
const realmColour = realm => REALM_PALETTE[realm] || OTHER_REALM_COLOUR;

// ==== small utils ==========================================================
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const SVGNS = "http://www.w3.org/2000/svg";
const isNil = v => v == null || (typeof v === "string" && !v.trim()) || (Array.isArray(v) && v.length === 0);
const prettyKey = k => String(k).replace(/^@/, "").replace(/[_-]+/g, " ").replace(/\b\w/g, c => c.toUpperCase());

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

// Read a numeric value that may be a bare number or a {value, unit}-style object.
function numericValue(v) {
  if (v == null) return null;
  if (typeof v === "number") return isFinite(v) ? v : null;
  if (typeof v === "string") { const n = Number(v); return isFinite(n) ? n : null; }
  if (typeof v === "object" && v.value != null) return numericValue(v.value);
  return null;
}

// Categorical label extraction: string, or a link-object's ui_label/name/@id.
function catLabel(v) {
  if (v == null) return null;
  if (typeof v === "string") return v.trim() || null;
  if (Array.isArray(v)) { const parts = v.map(catLabel).filter(Boolean); return parts.length ? parts.join("|") : null; }
  if (typeof v === "object") {
    return v.ui_label || v.label || v.name || (v["@id"] ? short(v["@id"]) : null);
  }
  return null;
}

// Keys deemed identifiers / labels — never fed into the projection.
const IDENT_KEYS = new Set([
  "@id", "@context", "@type", "type", "id", "validation_key",
  "ui_label", "alias", "name", "label",
  "description", "notes", "comment", "comments",
]);

// ==== schema discovery + Gower distance ====================================
// Rather than depend on a schema module, we auto-pick numeric and categorical
// keys from the row set: a key qualifies if at least ~15% of rows have a
// value there of the right kind.
function pickNumericKeys(rows) {
  const totals = new Map();
  for (const r of rows) {
    for (const [k, v] of Object.entries(r)) {
      if (IDENT_KEYS.has(k)) continue;
      if (numericValue(v) != null) totals.set(k, (totals.get(k) || 0) + 1);
    }
  }
  const min = Math.max(2, Math.floor(rows.length * 0.15));
  return [...totals.entries()].filter(([, c]) => c >= min).map(([k]) => k);
}

function pickCategoricalKeys(rows) {
  const numeric = new Set(pickNumericKeys(rows));
  const totals = new Map();
  for (const r of rows) {
    for (const [k, v] of Object.entries(r)) {
      if (IDENT_KEYS.has(k) || numeric.has(k)) continue;
      if (catLabel(v) != null) totals.set(k, (totals.get(k) || 0) + 1);
    }
  }
  const min = Math.max(2, Math.floor(rows.length * 0.15));
  return [...totals.entries()].filter(([, c]) => c >= min).map(([k]) => k);
}

// Gower distance for a mixed-type record set. Numeric contribution is
// |a-b| / range; categorical is 0/1 on equality; missing pairs are skipped
// per-feature (Gower's original rule).
function gowerDistance(rows) {
  const numKeys = pickNumericKeys(rows);
  const catKeys = pickCategoricalKeys(rows);

  const ranges = numKeys.map(k => {
    let mn = Infinity, mx = -Infinity;
    for (const r of rows) {
      const v = numericValue(r[k]);
      if (v == null) continue;
      if (v < mn) mn = v;
      if (v > mx) mx = v;
    }
    return (isFinite(mn) && isFinite(mx) && mx > mn) ? (mx - mn) : 1;
  });

  const numVals = rows.map(r => numKeys.map(k => numericValue(r[k])));
  const catVals = rows.map(r => catKeys.map(k => catLabel(r[k])));

  const n = rows.length;
  const D = new Float64Array(n * n);
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      let sum = 0, count = 0;
      for (let k = 0; k < numKeys.length; k++) {
        const a = numVals[i][k], b = numVals[j][k];
        if (a == null || b == null) continue;
        sum += Math.abs(a - b) / ranges[k];
        count++;
      }
      for (let k = 0; k < catKeys.length; k++) {
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

// ==== Jacobi eigendecomposition (used by PCoA init) ========================
// Standard cyclic-sweep Jacobi on a symmetric matrix. Returns eigenvalues and
// an eigenvector matrix where column j is the j-th eigenvector.
function jacobi(source, n) {
  const A = new Float64Array(source);
  const V = new Float64Array(n * n);
  for (let i = 0; i < n; i++) V[i * n + i] = 1;

  const MAX_SWEEPS = 100;
  const TOL = 1e-10;

  for (let sweep = 0; sweep < MAX_SWEEPS; sweep++) {
    let off = 0;
    for (let i = 0; i < n - 1; i++) {
      for (let j = i + 1; j < n; j++) off += Math.abs(A[i * n + j]);
    }
    if (off < TOL) break;

    for (let p = 0; p < n - 1; p++) {
      for (let q = p + 1; q < n; q++) {
        const apq = A[p * n + q];
        if (Math.abs(apq) < 1e-14) continue;
        const app = A[p * n + p], aqq = A[q * n + q];
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

// ==== 3D PCoA init =========================================================
// Classical MDS on the Gower distance matrix. Top-3 eigenvectors of the
// double-centred squared-distance matrix give a deterministic globally-
// correct 3D starting layout — much better PaCMAP starting point than random.
function pcoa3dInit(D, n) {
  if (n < 4) { const Y = []; for (let i = 0; i < n; i++) Y.push([0, 0, 0]); return Y; }
  const D2 = new Float64Array(n * n);
  for (let i = 0; i < n * n; i++) D2[i] = D[i] * D[i];

  // Double-centre: B_ij = -½ · (D²_ij − rowMean_i − colMean_j + grandMean)
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
      B[i * n + j] = -0.5 * (D2[i * n + j] - rowMean[i] - rowMean[j] + grand);
    }
  }

  const { eigenvalues, eigenvectors } = jacobi(B, n);
  const idx = Array.from({ length: n }, (_, i) => i);
  idx.sort((a, b) => eigenvalues[b] - eigenvalues[a]);
  const p1 = idx[0], p2 = idx[1] != null ? idx[1] : p1, p3 = idx[2] != null ? idx[2] : p1;
  const s1 = Math.sqrt(Math.max(0, eigenvalues[p1]));
  const s2 = Math.sqrt(Math.max(0, eigenvalues[p2]));
  const s3 = Math.sqrt(Math.max(0, eigenvalues[p3]));
  const Y = [];
  for (let i = 0; i < n; i++) {
    Y.push([
      eigenvectors[i * n + p1] * s1,
      eigenvectors[i * n + p2] * s2,
      eigenvectors[i * n + p3] * s3,
    ]);
  }
  // Scale so the largest coord is O(1) — keeps Adam gradient magnitudes sane.
  let maxAbs = 0;
  for (const p of Y) for (let d = 0; d < 3; d++) if (Math.abs(p[d]) > maxAbs) maxAbs = Math.abs(p[d]);
  const scale = maxAbs > 0 ? 1 / maxAbs : 1;
  return Y.map(p => [p[0] * scale, p[1] * scale, p[2] * scale]);
}

// ==== rank neighbours (for PaCMAP pair sampling) ===========================
function rankNeighbours(D, n) {
  const ranks = new Array(n);
  for (let i = 0; i < n; i++) {
    const dists = new Array(n - 1);
    let k = 0;
    for (let j = 0; j < n; j++) if (j !== i) dists[k++] = { j, d: D[i * n + j] };
    dists.sort((a, b) => a.d - b.d);
    ranks[i] = dists;
  }
  return ranks;
}

// ==== PaCMAP pair sampling =================================================
// Three pair types (Wang, Huang, Rudin, Shaposhnik 2021):
//   NB  neighbour   — each point's k nearest neighbours in high-dim
//   MN  mid-near    — sample 6 random points, take the 2nd closest
//   FP  far         — random non-neighbours (repulsion)
function samplePairs(D, ranks, n, { k = 10, mnRatio = 0.5, fpRatio = 2.0 } = {}, rng) {
  const nMN = Math.max(1, Math.floor(k * mnRatio));
  const nFP = Math.max(1, Math.floor(k * fpRatio));
  const NB = [], MN = [], FP = [];
  for (let i = 0; i < n; i++) {
    const r = ranks[i];
    const nbSet = new Set();
    const nnCount = Math.min(k, r.length);
    for (let m = 0; m < nnCount; m++) { NB.push([i, r[m].j]); nbSet.add(r[m].j); }
    for (let m = 0; m < nMN; m++) {
      const cand = [];
      for (let c = 0; c < 6; c++) {
        let j = Math.floor(rng() * (n - 1));
        if (j >= i) j++;
        cand.push({ j, d: D[i * n + j] });
      }
      cand.sort((a, b) => a.d - b.d);
      if (cand.length >= 2) MN.push([i, cand[1].j]);
    }
    let fpCount = 0, tries = 0;
    while (fpCount < nFP && tries < nFP * 10) {
      let j = Math.floor(rng() * (n - 1));
      if (j >= i) j++;
      if (j !== i && !nbSet.has(j)) { FP.push([i, j]); fpCount++; }
      tries++;
    }
  }
  return { NB, MN, FP };
}

// ==== 3D PaCMAP (with PCoA init, sphere-constrained) =======================
// Pipeline per step: PaCMAP gradient step (three pair types with phase-
// dependent weights) → Adam update → project every point back to unit
// length so the layout stays on the sphere. Same iterator interface as
// before: .Y, .step(), .iter, .total.
//
// Three-phase optimization from the PaCMAP paper:
//   Phase 1 (~22% of iters): heavy MN → establish global structure
//   Phase 2 (~22% of iters): balanced NB / MN / FP → refine mid-scale
//   Phase 3 (~56% of iters): NB + FP only → tighten local clusters
function makePacmap3d(D, n, { seed = 7, iters = PACMAP_ITERS, k = PACMAP_K } = {}) {
  const rng = mulberry32(seed);

  // PCoA init: deterministic globally-correct starting layout.
  const Y = pcoa3dInit(D, n);
  // Project init to sphere so we start on the constraint surface.
  for (let i = 0; i < n; i++) {
    const p = Y[i];
    const nrm = Math.sqrt(p[0]*p[0] + p[1]*p[1] + p[2]*p[2]) || 1;
    p[0] /= nrm; p[1] /= nrm; p[2] /= nrm;
  }
  if (n < 4) return { Y, step: () => true, iter: 0, total: 0 };

  const ranks = rankNeighbours(D, n);
  const { NB, MN, FP } = samplePairs(D, ranks, n, { k: Math.min(k, n - 2) }, rng);

  // Adam optimizer state (per-parameter adaptive learning rate).
  const m = Y.map(() => [0, 0, 0]);
  const v = Y.map(() => [0, 0, 0]);
  const beta1 = 0.9, beta2 = 0.999, eps = 1e-8;
  const lr = 1.0;

  const PHASE1_END = Math.floor(iters * 0.22);   // heavy MN
  const PHASE2_END = Math.floor(iters * 0.44);   // balanced
  // Phase 3 (remaining): NB + FP only

  let iter = 0;

  function step() {
    // Phase-dependent pair weights.
    let wNB, wMN, wFP;
    if (iter < PHASE1_END) {
      const t = iter / PHASE1_END;
      wNB = 2;
      wMN = 1000 * (1 - t) + 3 * t;   // decay 1000 → 3 across phase 1
      wFP = 1;
    } else if (iter < PHASE2_END) {
      wNB = 3; wMN = 3; wFP = 1;
    } else {
      wNB = 1; wMN = 0; wFP = 1;
    }

    // Accumulate gradients.
    const grad = new Array(n);
    for (let i = 0; i < n; i++) grad[i] = [0, 0, 0];

    // NB (attractive): ∂L/∂Y_i = w · 20 · (Y_i - Y_j) / (10 + d²)²
    for (const [i, j] of NB) {
      const dx = Y[i][0] - Y[j][0];
      const dy = Y[i][1] - Y[j][1];
      const dz = Y[i][2] - Y[j][2];
      const d2 = dx*dx + dy*dy + dz*dz;
      const denom = 10 + d2;
      const g = wNB * 20 / (denom * denom);
      grad[i][0] += g * dx; grad[i][1] += g * dy; grad[i][2] += g * dz;
      grad[j][0] -= g * dx; grad[j][1] -= g * dy; grad[j][2] -= g * dz;
    }

    // MN (attractive, slow): ∂L/∂Y_i = w · 20000 · (Y_i - Y_j) / (10000 + d²)²
    if (wMN > 0) {
      for (const [i, j] of MN) {
        const dx = Y[i][0] - Y[j][0];
        const dy = Y[i][1] - Y[j][1];
        const dz = Y[i][2] - Y[j][2];
        const d2 = dx*dx + dy*dy + dz*dz;
        const denom = 10000 + d2;
        const g = wMN * 20000 / (denom * denom);
        grad[i][0] += g * dx; grad[i][1] += g * dy; grad[i][2] += g * dz;
        grad[j][0] -= g * dx; grad[j][1] -= g * dy; grad[j][2] -= g * dz;
      }
    }

    // FP (repulsive): ∂L/∂Y_i = -w · 2 · (Y_i - Y_j) / (1 + d²)²
    for (const [i, j] of FP) {
      const dx = Y[i][0] - Y[j][0];
      const dy = Y[i][1] - Y[j][1];
      const dz = Y[i][2] - Y[j][2];
      const d2 = dx*dx + dy*dy + dz*dz;
      const denom = 1 + d2;
      const g = -wFP * 2 / (denom * denom);
      grad[i][0] += g * dx; grad[i][1] += g * dy; grad[i][2] += g * dz;
      grad[j][0] -= g * dx; grad[j][1] -= g * dy; grad[j][2] -= g * dz;
    }

    // Adam update.
    const t = iter + 1;
    const biasCorr1 = 1 - Math.pow(beta1, t);
    const biasCorr2 = 1 - Math.pow(beta2, t);
    for (let i = 0; i < n; i++) {
      for (let d = 0; d < 3; d++) {
        m[i][d] = beta1 * m[i][d] + (1 - beta1) * grad[i][d];
        v[i][d] = beta2 * v[i][d] + (1 - beta2) * grad[i][d] * grad[i][d];
        const mHat = m[i][d] / biasCorr1;
        const vHat = v[i][d] / biasCorr2;
        Y[i][d] -= lr * mHat / (Math.sqrt(vHat) + eps);
      }
    }

    // Sphere projection: keep the layout on the unit sphere so the model
    // overlay has a clean shell to sit on.
    for (let i = 0; i < n; i++) {
      const p = Y[i];
      const nrm = Math.sqrt(p[0]*p[0] + p[1]*p[1] + p[2]*p[2]) || 1;
      p[0] /= nrm; p[1] /= nrm; p[2] /= nrm;
    }

    iter++;
    return iter >= iters;
  }

  return { Y, step, get iter() { return iter; }, total: iters };
}

// ==== force-directed model layout ==========================================
// Positions each model near its grid cells, then relaxes with two spring
// forces plus collision. Grid cells (`gridPtsById`, on unit sphere) stay
// fixed. Each model is pulled by: (a) a spring toward an inset point on each
// linked grid (grid position × MODEL_INSET, see file header), and (b) a
// separate spring pulling straight toward the sphere centre (0,0,0),
// weighted by CENTER_K — an explicit, always-on attractor independent of
// how many/which grids the model links to.
function layoutModels(modelIds, links, gridPtsById, { iters = FORCE_ITERS } = {}) {
  // Bucket links by model.
  const modelGrids = new Map();
  for (const l of links) {
    if (!modelGrids.has(l.modelId)) modelGrids.set(l.modelId, []);
    modelGrids.get(l.modelId).push(l);
  }

  // Initial position = average of each linked grid's inset target (same
  // points the springs pull toward), so the guess already sits near
  // equilibrium. Models with no known grids get a small random offset near
  // the centre rather than a point on any shell.
  const pos = new Map();
  const vel = new Map();
  const rng = mulberry32(101);
  for (const id of modelIds) {
    const gs = modelGrids.get(id) || [];
    let cx = 0, cy = 0, cz = 0, count = 0;
    for (const l of gs) {
      const g = gridPtsById.get(l.gridId);
      if (!g) continue;
      cx += g[0]; cy += g[1]; cz += g[2]; count++;
    }
    if (count) {
      pos.set(id, [(cx / count) * MODEL_INSET, (cy / count) * MODEL_INSET, (cz / count) * MODEL_INSET]);
    } else {
      pos.set(id, [gauss(rng) * MODEL_FALLBACK_R, gauss(rng) * MODEL_FALLBACK_R, gauss(rng) * MODEL_FALLBACK_R]);
    }
    vel.set(id, [0, 0, 0]);
  }

  const idArr = [...modelIds];
  for (let it = 0; it < iters; it++) {
    const force = new Map();
    for (const id of idArr) force.set(id, [0, 0, 0]);

    // Springs: pull each model toward an inset point on each of its linked
    // grid cells (grid position × MODEL_INSET < 1). A model with divergent
    // links (spread across realms) balances toward the sphere's interior;
    // a model with one link settles just inside the sphere near that grid.
    for (const id of idArr) {
      const p = pos.get(id);
      const gs = modelGrids.get(id) || [];
      for (const l of gs) {
        const g = gridPtsById.get(l.gridId);
        if (!g) continue;
        const tx = g[0] * MODEL_INSET, ty = g[1] * MODEL_INSET, tz = g[2] * MODEL_INSET;
        const f = force.get(id);
        f[0] += SPRING_K * (tx - p[0]);
        f[1] += SPRING_K * (ty - p[1]);
        f[2] += SPRING_K * (tz - p[2]);
      }
    }

    // Centring spring: pulls every model straight toward the sphere centre
    // (0,0,0), independent of and in addition to the grid-attraction springs
    // above. This is what actually makes "the centre" an attractor rather
    // than just a smaller inset target — models with several conflicting
    // grid links get pulled inward more, since the grid springs cancel each
    // other out while this one doesn't.
    for (const id of idArr) {
      const p = pos.get(id);
      const f = force.get(id);
      f[0] += CENTER_K * (0 - p[0]);
      f[1] += CENTER_K * (0 - p[1]);
      f[2] += CENTER_K * (0 - p[2]);
    }

    // Coulomb repulsion removed — models are free to sit close, and only
    // the collision resolution pass below prevents actual overlap.

    // Velocity-Verlet-style integrate with damping.
    for (const id of idArr) {
      const v = vel.get(id), p = pos.get(id), f = force.get(id);
      v[0] = (v[0] + f[0]) * DAMPING;
      v[1] = (v[1] + f[1]) * DAMPING;
      v[2] = (v[2] + f[2]) * DAMPING;
      p[0] += v[0]; p[1] += v[1]; p[2] += v[2];
    }

    // Collision resolution — iterative hard-sphere non-overlap. If two
    // models are within 2·MODEL_COLLISION_R of each other, push them apart
    // along the line connecting their centres by (2r-d)/2 each. Multiple
    // sub-passes converge tangled clusters without needing repulsion forces.
    for (let cpass = 0; cpass < MODEL_COLLISION_PASSES; cpass++) {
      let anyMoved = false;
      for (let a = 0; a < idArr.length; a++) {
        const pa = pos.get(idArr[a]);
        for (let b = a + 1; b < idArr.length; b++) {
          const pb = pos.get(idArr[b]);
          let dx = pa[0] - pb[0], dy = pa[1] - pb[1], dz = pa[2] - pb[2];
          let d2 = dx * dx + dy * dy + dz * dz;
          const minD = MODEL_COLLISION_R * 2;
          if (d2 >= minD * minD) continue;
          let d = Math.sqrt(d2);
          if (d < 1e-9) {
            // coincident — nudge with a deterministic tiny offset then continue
            dx = 0.001; dy = 0.0007; dz = 0.0013;
            d = Math.sqrt(dx*dx + dy*dy + dz*dz);
          }
          const push = (minD - d) / 2;
          const nx = dx / d, ny = dy / d, nz = dz / d;
          pa[0] += nx * push; pa[1] += ny * push; pa[2] += nz * push;
          pb[0] -= nx * push; pb[1] -= ny * push; pb[2] -= nz * push;
          anyMoved = true;
        }
      }
      if (!anyMoved) break;
    }
  }
  return pos;
}

// ==== grid-cell overlap relaxation =========================================
// Nudges apart any pair of grid points closer than `minSep` (identical or
// near-identical records commonly land almost exactly on top of each other
// after PaCMAP), then re-normalises every point back onto the unit sphere
// so the constraint from makePacmap3d still holds. Mutates `Y` in place.
// Best-effort: O(n²) per pass, early-exits once nothing moves.
function relaxSpherePositions(Y, minSep, { passes = GRID_RELAX_PASSES } = {}) {
  const n = Y.length;
  if (n < 2) return;
  for (let pass = 0; pass < passes; pass++) {
    let moved = false;
    for (let i = 0; i < n; i++) {
      const a = Y[i];
      for (let j = i + 1; j < n; j++) {
        const b = Y[j];
        let dx = a[0] - b[0], dy = a[1] - b[1], dz = a[2] - b[2];
        const d2 = dx * dx + dy * dy + dz * dz;
        if (d2 >= minSep * minSep) continue;
        let d = Math.sqrt(d2);
        if (d < 1e-9) { dx = 0.001; dy = 0.0007; dz = 0.0013; d = Math.sqrt(dx*dx + dy*dy + dz*dz); }
        const push = (minSep - d) / 2;
        const nx = dx / d, ny = dy / d, nz = dz / d;
        a[0] += nx * push; a[1] += ny * push; a[2] += nz * push;
        b[0] -= nx * push; b[1] -= ny * push; b[2] -= nz * push;
        moved = true;
      }
    }
    // Re-normalise back onto the unit sphere after each pass.
    for (let i = 0; i < n; i++) {
      const p = Y[i];
      const nrm = Math.sqrt(p[0]*p[0] + p[1]*p[1] + p[2]*p[2]) || 1;
      p[0] /= nrm; p[1] /= nrm; p[2] /= nrm;
    }
    if (!moved) break;
  }
}

// ==== colour map for grid types ============================================
function buildGridColourMap(gridRows) {
  const counts = new Map();
  for (const rec of gridRows) {
    const label = catLabel(rec.grid_type) || "Unspecified";
    counts.set(label, (counts.get(label) || 0) + 1);
  }
  const ordered = [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  const map = new Map();
  ordered.forEach(([label], i) => {
    map.set(label, i < GRID_PALETTE.length ? GRID_PALETTE[i] : OTHER_GRID_COLOUR);
  });
  return { map, ordered };
}

function activeRealmsFromLinks(links) {
  const counts = new Map();
  for (const l of links) counts.set(l.realm, (counts.get(l.realm) || 0) + 1);
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}

// ==== public entrypoint ====================================================
export function createAnalysisScatter({ gridRows, models, links }) {
  const gridById = new Map();
  gridRows.forEach(r => gridById.set(short(r["@id"]), r));
  const { map: gridColourOf, ordered: gridColourOrder } = buildGridColourMap(gridRows);
  const orderedRealms = activeRealmsFromLinks(links);

  // Group links sharing the same (model, grid) pair so duplicate curves can
  // be bowed apart symmetrically: m=1 → [0], m=2 → [-0.5,0.5], m=3 → [-1,0,1] …
  const linkBowIndex = new Array(links.length).fill(0);
  {
    const groups = new Map();   // "modelId::gridId" → [link indices]
    links.forEach((l, i) => {
      const key = `${l.modelId}::${l.gridId}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(i);
    });
    for (const idxArr of groups.values()) {
      const m = idxArr.length;
      idxArr.forEach((idx, k) => { linkBowIndex[idx] = k - (m - 1) / 2; });
    }
  }

  // ---- SVG scaffold ----
  const svg = document.createElementNS(SVGNS, "svg");
  svg.setAttribute("class", "an-scatter-svg");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", "3D PCoA + PaCMAP similarity map of grid cells with model overlay; drag to rotate, scroll to zoom");
  svg.style.cursor = "grab";

  const defs = document.createElementNS(SVGNS, "defs");
  defs.innerHTML = `
    <radialGradient id="an-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="currentColor" stop-opacity="0.5"/>
      <stop offset="60%" stop-color="currentColor" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="currentColor" stop-opacity="0"/>
    </radialGradient>`;
  svg.appendChild(defs);

  const linkLayer = document.createElementNS(SVGNS, "g");
  const gridLayer = document.createElementNS(SVGNS, "g");
  const modelLayer = document.createElementNS(SVGNS, "g");
  linkLayer.setAttribute("class", "an-link-layer");
  gridLayer.setAttribute("class", "an-grid-layer");
  modelLayer.setAttribute("class", "an-model-layer");
  svg.appendChild(linkLayer);
  svg.appendChild(gridLayer);
  svg.appendChild(modelLayer);

  const status = el("span", { class: "an-scatter-status" }, "Computing…");

  // Legend content — shown by default inside the detail panel, in the same
  // spot that would otherwise say "Hover a node to see its details." Hidden
  // while a node's hover/pin detail is shown; reappears once the panel goes
  // back to its blank state (mouse leaves, pin cleared).
  const legendContent = el("div", { class: "an-scatter-legend" });
  // Icon-only, floats over the bottom-right corner of the plot itself
  // (see .an-restart-rotate CSS) rather than sitting in the legend.
  const restartBtn = el("button", {
    class: "an-restart-rotate", type: "button",
    title: "Resume auto-rotation", "aria-label": "Resume auto-rotation",
  }, [
    el("span", { class: "an-restart-icon", "aria-hidden": "true" }, "↻"),
  ]);

  const detailPanel = el("div", { class: "an-scatter-detail" }, [legendContent]);
  const plotEl = el("div", { class: "an-scatter-plot" }, [svg, restartBtn]);

  const root = el("section", { class: "an-scatter-card" }, [
    el("div", { class: "an-scatter-head" }, [
      el("h2", { class: "an-scatter-title" }, "PCoA + PaCMAP Similarity Map + Model Overlay"),
      status,
    ]),
    el("div", { class: "an-scatter-body" }, [
      plotEl,
      detailPanel,
    ]),
  ]);

  // ---- interaction state ----
  const gridEls = new Map();    // gridId → { node, glow, pos3 }
  const modelEls = new Map();   // modelId → { node, pos3 }
  const linkEls = [];           // parallel to `links`
  let rotY = 0.4, rotX = -0.3;
  let zoom = 1;
  // Explicit viewBox state (rather than a single centred zoom factor) so we
  // can zoom toward the cursor: viewX/viewY/viewSize describe the current
  // "svg.viewBox" rect directly.
  let viewX = 0, viewY = 0, viewSize = W;
  let autoRotate = true;
  let rafPending = false;
  let lastFrameTime = 0;
  let dragging = false, dragMoved = false, dragStart = null, dragRotStart = null;
  let pinnedKind = null, pinnedId = null;

  // ---- 3D → 2D projection (Y-first then X rotation, orthographic) ----
  const cx = W / 2, cy = H / 2;
  const scale = Math.min(W, H) / 2 - PAD;
  function project(p3) {
    const cyR = Math.cos(rotY), syR = Math.sin(rotY);
    const cxR = Math.cos(rotX), sxR = Math.sin(rotX);
    const x1 = p3[0] * cyR + p3[2] * syR;
    const z1 = -p3[0] * syR + p3[2] * cyR;
    const y2 = p3[1] * cxR - z1 * sxR;
    const z2 = p3[1] * sxR + z1 * cxR;
    return { x: cx + x1 * scale, y: cy - y2 * scale, z: z2 };
  }

  // ---- render one frame (called every rAF while rotating; also on interact) ----
  function render() {
    const gridPos = new Map();
    for (const [id, e] of gridEls) gridPos.set(id, project(e.pos3));
    const modelPos = new Map();
    for (const [id, e] of modelEls) modelPos.set(id, project(e.pos3));

    let zMin = Infinity, zMax = -Infinity;
    for (const p of gridPos.values()) { if (p.z < zMin) zMin = p.z; if (p.z > zMax) zMax = p.z; }
    for (const p of modelPos.values()) { if (p.z < zMin) zMin = p.z; if (p.z > zMax) zMax = p.z; }
    const zSpan = (zMax - zMin) || 1;

    // Links — quadratic-Bézier curves. Control point is the midpoint nudged
    // along the screen-space perpendicular by this link's bow offset, so
    // duplicate (model, grid) links fan out instead of overlapping exactly.
    for (let i = 0; i < links.length; i++) {
      const l = links[i], ge = linkEls[i];
      if (!ge) continue;
      const gp = gridPos.get(l.gridId);
      const mp = modelPos.get(l.modelId);
      if (!gp || !mp) { ge.style.display = "none"; continue; }
      ge.style.display = "";
      const midX = (mp.x + gp.x) / 2, midY = (mp.y + gp.y) / 2;
      const dx = gp.x - mp.x, dy = gp.y - mp.y;
      const len = Math.hypot(dx, dy) || 1;
      const nx = -dy / len, ny = dx / len;   // unit perpendicular
      const bow = linkBowIndex[i] * LINK_BOW_UNIT;
      const ctrlX = midX + nx * bow, ctrlY = midY + ny * bow;
      ge.setAttribute("d",
        `M${mp.x.toFixed(2)},${mp.y.toFixed(2)} Q${ctrlX.toFixed(2)},${ctrlY.toFixed(2)} ${gp.x.toFixed(2)},${gp.y.toFixed(2)}`);
      // Depth-based opacity only when this link isn't in a highlighted class.
      if (!ge.classList.contains("linked") && !ge.classList.contains("muted")) {
        const zAvg = ((gp.z - zMin) + (mp.z - zMin)) / (2 * zSpan);
        ge.style.strokeOpacity = (0.14 + zAvg * 0.22).toFixed(3);
      }
    }

    // Grid nodes — painter's algorithm (back to front)
    const gridOrder = [...gridEls.keys()].sort((a, b) => gridPos.get(a).z - gridPos.get(b).z);
    for (const id of gridOrder) {
      const e = gridEls.get(id);
      const p = gridPos.get(id);
      const zNorm = (p.z - zMin) / zSpan;
      const r = R_GRID * (0.7 + zNorm * 0.6);
      e.node.setAttribute("cx", p.x.toFixed(2));
      e.node.setAttribute("cy", p.y.toFixed(2));
      e.node.setAttribute("r", r.toFixed(2));
      // Depth fade — skipped for active/linked so a highlighted node stays
      // fully vivid; independent of .muted's "opacity" property.
      if (!e.node.classList.contains("active") && !e.node.classList.contains("linked")) {
        e.node.style.fillOpacity = (DEPTH_FADE_MIN + zNorm * (1 - DEPTH_FADE_MIN)).toFixed(3);
      } else {
        e.node.style.fillOpacity = "";
      }
      if (e.glow) {
        e.glow.setAttribute("cx", p.x.toFixed(2));
        e.glow.setAttribute("cy", p.y.toFixed(2));
        e.glow.setAttribute("r", (r * 2.6).toFixed(2));
      }
      gridLayer.appendChild(e.node);
    }

    // Model nodes — painter's algorithm
    const modelOrder = [...modelEls.keys()].sort((a, b) => modelPos.get(a).z - modelPos.get(b).z);
    for (const id of modelOrder) {
      const e = modelEls.get(id);
      const p = modelPos.get(id);
      const zNorm = (p.z - zMin) / zSpan;
      const r = R_MODEL * (0.75 + zNorm * 0.5);
      e.node.setAttribute("cx", p.x.toFixed(2));
      e.node.setAttribute("cy", p.y.toFixed(2));
      e.node.setAttribute("r", r.toFixed(2));
      // Model nodes are mostly a stroked ring (fill matches the page
      // background), so fade the stroke rather than the fill.
      if (!e.node.classList.contains("active") && !e.node.classList.contains("linked")) {
        e.node.style.strokeOpacity = (DEPTH_FADE_MIN + zNorm * (1 - DEPTH_FADE_MIN)).toFixed(3);
      } else {
        e.node.style.strokeOpacity = "";
      }
      modelLayer.appendChild(e.node);
    }
  }

  // ---- animation loop ----
  function frame(now) {
    rafPending = false;
    if (autoRotate) {
      const dt = (now - lastFrameTime) / 1000;
      lastFrameTime = now;
      rotY += AUTO_ROTATE_SPEED * (Number.isFinite(dt) && dt < 0.1 ? dt : 0.016);
      render();
      requestFrame();
    } else {
      render();
    }
  }
  function requestFrame() {
    if (rafPending) return;
    rafPending = true;
    lastFrameTime = performance.now();
    requestAnimationFrame(frame);
  }
  function stopAutoRotate() { autoRotate = false; }
  function startAutoRotate() { autoRotate = true; lastFrameTime = performance.now(); requestFrame(); }
  restartBtn.addEventListener("click", ev => { ev.stopPropagation(); startAutoRotate(); });

  // ---- highlight helpers ----
  function clearHighlights() {
    gridEls.forEach(({ node, glow }) => {
      node.classList.remove("active", "linked", "muted");
      if (glow) glow.classList.remove("visible");
    });
    modelEls.forEach(({ node }) => node.classList.remove("active", "linked", "muted"));
    linkEls.forEach(l => { if (l) { l.classList.remove("linked", "muted"); l.style.strokeOpacity = ""; } });
    // Re-render so the depth-fade inline opacity (only applied to non-
    // active/linked nodes) picks up the cleared classes immediately, even
    // when auto-rotation is currently stopped and no highlight follows.
    render();
  }
  function highlightGrid(id) {
    clearHighlights();
    const e = gridEls.get(id);
    if (!e) return;
    e.node.classList.add("active");
    if (e.glow) e.glow.classList.add("visible");
    const modelsUsing = new Set();
    for (let i = 0; i < links.length; i++) {
      if (links[i].gridId === id) { modelsUsing.add(links[i].modelId); linkEls[i].classList.add("linked"); }
      else linkEls[i].classList.add("muted");
    }
    modelEls.forEach(({ node }, mid) => { if (modelsUsing.has(mid)) node.classList.add("linked"); else node.classList.add("muted"); });
    gridEls.forEach(({ node }, gid) => { if (gid !== id) node.classList.add("muted"); });
    render();
  }
  function highlightModel(id) {
    clearHighlights();
    const e = modelEls.get(id);
    if (!e) return;
    e.node.classList.add("active");
    const grids = new Set();
    for (let i = 0; i < links.length; i++) {
      if (links[i].modelId === id) { grids.add(links[i].gridId); linkEls[i].classList.add("linked"); }
      else linkEls[i].classList.add("muted");
    }
    gridEls.forEach(({ node, glow }, gid) => {
      if (grids.has(gid)) { node.classList.add("linked"); if (glow) glow.classList.add("visible"); }
      else node.classList.add("muted");
    });
    modelEls.forEach(({ node }, mid) => { if (mid !== id) node.classList.add("muted"); });
    render();
  }

  // ---- detail panel ----
  // Grid-cell preview fields — same set (and order) as the grid_cells page's
  // own detail panel, so a grid cell looks the same wherever it's shown.
  const GRID_PREVIEW_KEYS = ["n_cells", "truncation_number", "x_resolution", "y_resolution", "grid_mapping", "region"];

  function showGridDetail(id) {
    const rec = gridById.get(id);
    if (!rec) return;
    const label = catLabel(rec.grid_type) || "Unspecified";
    const modelsUsing = links.filter(l => l.gridId === id);

    const alias = isNil(rec.alias) ? "" : (Array.isArray(rec.alias) ? rec.alias.join(", ") : String(rec.alias));
    const uiLabel = isNil(rec.ui_label) ? "" : String(rec.ui_label);
    const description = isNil(rec.description) ? "" : String(rec.description);

    const previewRows = [];
    for (const k of GRID_PREVIEW_KEYS) {
      const v = rec[k];
      if (isNil(v)) continue;
      let display;
      if (typeof v === "number") display = v.toLocaleString();
      else display = catLabel(v) || String(v);
      previewRows.push({ key: k, display });
    }

    clear(detailPanel);
    detailPanel.append(
      el("div", { class: "an-detail-kind" }, "Grid cell"),
      el("div", { class: "an-detail-head" }, [
        el("code", { class: "an-detail-id" }, id),
        alias ? el("span", { class: "an-detail-alias" }, alias) : null,
      ].filter(Boolean)),
      el("div", { class: "an-detail-type" }, [
        el("span", { class: "an-legend-dot", style: `background:${gridColourOf.get(label) || OTHER_GRID_COLOUR}` }),
        el("span", {}, label),
      ]),
      uiLabel ? el("p", { class: "an-detail-ui-label" }, uiLabel) : null,
      description ? el("p", { class: "an-detail-description" }, description) : null,
      previewRows.length ? el("dl", { class: "an-detail-fields" },
        previewRows.flatMap(({ key, display }) => [
          el("dt", {}, prettyKey(key)),
          el("dd", {}, display),
        ])
      ) : null,
      modelsUsing.length ? el("p", { class: "an-detail-used-by" },
        `Used by ${modelsUsing.length} model${modelsUsing.length === 1 ? "" : "s"}`) : null,
    );
  }
  function showModelDetail(id) {
    const m = models.find(x => short(x["@id"]) === id);
    const modelLabel = (m && (m.ui_label || m.name)) || id;
    const description = m && m.description ? String(m.description) : "";
    const used = links.filter(l => l.modelId === id);
    const realmCounts = new Map();
    for (const l of used) realmCounts.set(l.realm, (realmCounts.get(l.realm) || 0) + 1);

    clear(detailPanel);
    detailPanel.append(
      el("div", { class: "an-detail-kind" }, "Model"),
      el("code", { class: "an-detail-id" }, id),
      el("p", { class: "an-detail-ui-label" }, modelLabel),
      description ? el("p", { class: "an-detail-description" }, description) : null,
      el("p", { class: "an-detail-used-by" }, `${used.length} grid link${used.length === 1 ? "" : "s"}`),
    );

    // Preferred: CRS diagram (coloured string + embedding-groups spheres).
    // Fallback (no `crs` field on the model): the realm-count tag list.
    const crsBlock = m ? renderCrsInline(m) : null;
    if (crsBlock) {
      const wrap = el("div", { class: "an-detail-crs" }, []);
      wrap.appendChild(crsBlock);
      detailPanel.appendChild(wrap);
    } else if (realmCounts.size) {
      detailPanel.appendChild(el("div", { class: "an-detail-realms" },
        [...realmCounts.entries()].map(([realm, n]) => el("span", { class: "an-detail-realm-tag" }, [
          el("span", { class: "an-legend-dot", style: `background:${realmColour(realm)}` }),
          el("span", {}, `${realm} · ${n}`),
        ]))));
    }
  }
  function clearDetail() {
    clear(detailPanel);
    detailPanel.appendChild(legendContent);
  }
  function restorePinnedOrClear() {
    if (pinnedKind === "grid") { highlightGrid(pinnedId); showGridDetail(pinnedId); }
    else if (pinnedKind === "model") { highlightModel(pinnedId); showModelDetail(pinnedId); }
    else { clearHighlights(); clearDetail(); }
  }

  // ---- SVG events ----
  // Zoom toward the cursor: find where the mouse sits in the *current*
  // viewBox, shrink/grow the viewBox, then solve for the new viewX/viewY
  // that keeps that same point under the cursor. Clamped to [0, W-size] so
  // the view can never pan outside the original canvas (and naturally
  // re-centres once zoom returns to 1).
  svg.addEventListener("wheel", ev => {
    ev.preventDefault();
    stopAutoRotate();
    const factor = ev.deltaY > 0 ? 0.9 : 1.1;
    const newZoom = clamp(zoom * factor, MIN_ZOOM, MAX_ZOOM);
    const newSize = W / newZoom;

    const rect = svg.getBoundingClientRect();
    const fracX = rect.width ? (ev.clientX - rect.left) / rect.width : 0.5;
    const fracY = rect.height ? (ev.clientY - rect.top) / rect.height : 0.5;
    const pointX = viewX + fracX * viewSize;
    const pointY = viewY + fracY * viewSize;

    zoom = newZoom;
    viewSize = newSize;
    viewX = clamp(pointX - fracX * newSize, 0, W - newSize);
    viewY = clamp(pointY - fracY * newSize, 0, H - newSize);
    svg.setAttribute("viewBox", `${viewX} ${viewY} ${viewSize} ${viewSize}`);
  }, { passive: false });

  svg.addEventListener("mousedown", ev => {
    dragging = true; dragMoved = false;
    stopAutoRotate();
    dragStart = { x: ev.clientX, y: ev.clientY };
    dragRotStart = { rotX, rotY };
    svg.style.cursor = "grabbing";
    ev.preventDefault();
  });
  window.addEventListener("mousemove", ev => {
    if (!dragging) return;
    const dx = ev.clientX - dragStart.x, dy = ev.clientY - dragStart.y;
    if (!dragMoved && Math.hypot(dx, dy) > DRAG_THRESHOLD) dragMoved = true;
    if (!dragMoved) return;
    const bbox = svg.getBoundingClientRect();
    const size = Math.min(bbox.width, bbox.height) || W;
    rotY = dragRotStart.rotY + (dx / size) * Math.PI * 1.5;
    rotX = clamp(dragRotStart.rotX - (dy / size) * Math.PI * 1.5, -Math.PI / 2 + 0.1, Math.PI / 2 - 0.1);
    requestFrame();
  });
  window.addEventListener("mouseup", () => {
    if (!dragging) return;
    dragging = false;
    svg.style.cursor = "grab";
  });

  svg.addEventListener("mouseleave", () => { restorePinnedOrClear(); });
  svg.addEventListener("click", () => {
    if (dragMoved) return;
    if (pinnedKind) { pinnedKind = null; pinnedId = null; clearHighlights(); clearDetail(); }
  });

  // ---- build DOM nodes (called once after positions are computed) ----
  function build(gridPositions3d, modelPositions3d) {
    // Links (draw first so grid + model nodes sit on top). Positions set on
    // the first render() call; `d` is recomputed every frame.
    clear(linkLayer); linkEls.length = 0;
    for (const l of links) {
      const path = document.createElementNS(SVGNS, "path");
      path.setAttribute("class", "an-link");
      path.setAttribute("fill", "none");
      path.setAttribute("stroke", realmColour(l.realm));
      path.setAttribute("stroke-width", "0.9");
      path.setAttribute("stroke-opacity", "0.22");
      path.dataset.model = l.modelId;
      path.dataset.grid = l.gridId;
      path.dataset.realm = l.realm;
      linkLayer.appendChild(path);
      linkEls.push(path);
    }

    // Grid-cell nodes
    clear(gridLayer); gridEls.clear();
    for (const rec of gridRows) {
      const id = short(rec["@id"]);
      const p3 = gridPositions3d.get(id);
      if (!p3) continue;
      const label = catLabel(rec.grid_type) || "Unspecified";
      const colour = gridColourOf.get(label) || OTHER_GRID_COLOUR;

      const glow = document.createElementNS(SVGNS, "circle");
      glow.setAttribute("class", "an-glow");
      glow.setAttribute("r", R_GRID * 2.6);
      glow.setAttribute("fill", "url(#an-glow)");
      glow.setAttribute("color", colour);
      gridLayer.appendChild(glow);

      const c = document.createElementNS(SVGNS, "circle");
      c.setAttribute("class", "an-grid-node");
      c.setAttribute("r", R_GRID);
      c.setAttribute("fill", colour);
      c.dataset.id = id;
      c.dataset.kind = "grid";
      attachTooltip(c, `${id}\n${label}`);

      c.addEventListener("mouseenter", () => {
        stopAutoRotate();
        highlightGrid(id); showGridDetail(id);
      });
      c.addEventListener("mouseleave", () => {
        if (pinnedKind === "grid" && pinnedId === id) return;
        restorePinnedOrClear();
      });
      c.addEventListener("click", ev => {
        ev.stopPropagation();
        if (dragMoved) return;
        stopAutoRotate();
        if (pinnedKind === "grid" && pinnedId === id) {
          pinnedKind = null; pinnedId = null;
          clearHighlights(); clearDetail();
        } else {
          pinnedKind = "grid"; pinnedId = id;
          highlightGrid(id); showGridDetail(id);
        }
      });

      gridLayer.appendChild(c);
      gridEls.set(id, { node: c, glow, pos3: p3 });
    }

    // Model nodes
    clear(modelLayer); modelEls.clear();
    for (const m of models) {
      const id = short(m["@id"]);
      const p3 = modelPositions3d.get(id);
      if (!p3) continue;
      const c = document.createElementNS(SVGNS, "circle");
      c.setAttribute("class", "an-model-node");
      c.setAttribute("r", R_MODEL);
      c.dataset.id = id;
      c.dataset.kind = "model";
      attachTooltip(c, `Model: ${m.ui_label || m.name || id}\n${id}`);

      c.addEventListener("mouseenter", () => {
        stopAutoRotate();
        highlightModel(id); showModelDetail(id);
      });
      c.addEventListener("mouseleave", () => {
        if (pinnedKind === "model" && pinnedId === id) return;
        restorePinnedOrClear();
      });
      c.addEventListener("click", ev => {
        ev.stopPropagation();
        if (dragMoved) return;
        stopAutoRotate();
        if (pinnedKind === "model" && pinnedId === id) {
          pinnedKind = null; pinnedId = null;
          clearHighlights(); clearDetail();
        } else {
          pinnedKind = "model"; pinnedId = id;
          highlightModel(id); showModelDetail(id);
        }
      });

      modelLayer.appendChild(c);
      modelEls.set(id, { node: c, pos3: p3 });
    }

    render();
  }

  // ---- legend ----
  function buildLegend() {
    clear(legendContent);
    if (gridColourOrder.length) {
      legendContent.appendChild(el("div", { class: "an-legend-heading" }, "Grid type"));
      for (const [label, count] of gridColourOrder) {
        legendContent.appendChild(el("span", { class: "an-legend-item", title: `${label} — ${count}` }, [
          el("span", { class: "an-legend-dot", style: `background:${gridColourOf.get(label)}` }),
          el("span", { class: "an-legend-label" }, label),
          el("span", { class: "an-legend-count" }, `${count}`),
        ]));
      }
    }
    if (orderedRealms.length) {
      legendContent.appendChild(el("div", { class: "an-legend-heading" }, "Realm (link colour)"));
      for (const [realm, count] of orderedRealms) {
        legendContent.appendChild(el("span", { class: "an-legend-item", title: `${realm} — ${count} link${count === 1 ? "" : "s"}` }, [
          el("span", { class: "an-legend-swatch", style: `background:${realmColour(realm)}` }),
          el("span", { class: "an-legend-label" }, realm),
          el("span", { class: "an-legend-count" }, `${count}`),
        ]));
      }
    }
    legendContent.appendChild(el("div", { class: "an-legend-heading" }, "Model nodes"));
    legendContent.appendChild(el("span", { class: "an-legend-item" }, [
      el("span", { class: "an-legend-model-glyph" }),
      el("span", { class: "an-legend-label" }, `${models.length} model${models.length === 1 ? "" : "s"}`),
    ]));
  }
  buildLegend();

  // ---- pipeline ----
  const D = gowerDistance(gridRows);
  const dr = makePacmap3d(D, gridRows.length);

  function runChunk() {
    let done = false;
    for (let k = 0; k < CHUNK && !done; k++) done = dr.step();
    if (dr.total) {
      const pct = Math.min(100, Math.round((dr.iter / dr.total) * 100));
      status.textContent = done ? "Placing models…" : `Computing… ${pct}%`;
    }
    if (done) {
      // Reduce visual overlap between near-identical grid cells before
      // handing positions to the model layout / renderer.
      relaxSpherePositions(dr.Y, GRID_MIN_SEP);
      const gridPositions3d = new Map();
      gridRows.forEach((r, i) => gridPositions3d.set(short(r["@id"]), dr.Y[i]));
      const modelIds = models.map(m => short(m["@id"]));
      const modelPositions3d = layoutModels(modelIds, links, gridPositions3d);
      build(gridPositions3d, modelPositions3d);
      status.textContent = `${gridRows.length} grid cells · ${models.length} models · ${links.length} links · drag to rotate · scroll to zoom`;
      startAutoRotate();
    } else {
      requestAnimationFrame(runChunk);
    }
  }
  requestAnimationFrame(() => requestAnimationFrame(runChunk));

  return { root };
}
