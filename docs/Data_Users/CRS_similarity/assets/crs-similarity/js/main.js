// main.js — CRS similarity (experimental): load every model's CRS and group the models by structure.
// The algorithm lives in ./similarity.js; the CRS parser is the Model viewer's own (one parser).

import { tokenize, similarityMatrix, upgma, cut, describe, sortTokens, kindOfToken, sharedStructure, differenceStructure, KINDS, DEFAULT_WEIGHTS } from "./similarity.js";
import { realmColor, realmLabel } from "../../../../Model_viewer/assets/model-page/js/crs.js";
import { crsSvg, shortRealm } from "../../../../Model_viewer/assets/model-page/js/components/crs-diagram.js";   // the Model viewer's own drawing

const BASE = "https://wcrp-cmip.github.io/Essential-Model-Documentation/";
const VIEWER = "../Model_viewer/?model=";
const SVG_NS = "http://www.w3.org/2000/svg";

function h(tag, attrs = {}, kids = []) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === "class") n.className = v;
    else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v === true ? "" : v);
  }
  for (const c of [].concat(kids)) if (c != null && c !== false) n.append(c instanceof Node ? c : String(c));
  return n;
}
function s(tag, attrs = {}) {
  const n = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  return n;
}
const fmt = x => x.toFixed(2);
const cssRgb = name => getComputedStyle(document.documentElement).getPropertyValue(name).split(",").map(Number);

// The CRS string with each realm code in its realm colour; embedded codes paler.
function crsCode(crs) {
  const code = h("code", { class: "cs-crs" });
  let i = 0, depth = 0;
  while (i < crs.length) {
    const ch = crs[i];
    if (ch >= "A" && ch <= "Z") {
      let tok = ch; i++;
      while (i < crs.length && crs[i] >= "a" && crs[i] <= "z") { tok += crs[i]; i++; }
      const sp = h("span", { class: "tok" + (depth ? " emb" : "") }, tok);
      sp.style.setProperty("--realm", realmColor(tok));
      code.append(sp);
      continue;
    }
    if (ch === "[") depth++;
    else if (ch === "]") depth = Math.max(0, depth - 1);
    code.append(h("span", { class: "pun" }, ch));
    i++;
  }
  return code;
}

// ---- state -------------------------------------------------------------------------------
const state = {
  models: [], noCrs: [], tokens: [],
  S: null, tree: null, order: [], groups: [],
  weights: { ...DEFAULT_WEIGHTS }, threshold: 0.55, pair: [0, 1],
};

async function loadModels() {
  const index = await (await fetch(BASE + "model/_graph.json")).json();
  const ids = (index.contents || index["@graph"] || []).map(e => (typeof e === "string" ? e : e["@id"]));
  const recs = await Promise.all(ids.map(id =>
    fetch(`${BASE}model/${id}.json`).then(r => (r.ok ? r.json() : null)).catch(() => null)));
  return recs
    .map((m, k) => m && { id: ids[k], name: m.validation_key || ids[k], family: m.family || "", crs: (m.crs || "").trim() })
    .filter(Boolean)
    .sort((a, b) => a.name.localeCompare(b.name));
}

function compute() {
  state.S = similarityMatrix(state.tokens, state.weights);
  state.tree = upgma(state.S.map(row => row.map(x => 1 - x)));
  state.order = state.tree.leaves;
  const pos = new Map(state.order.map((m, k) => [m, k]));
  state.groups = cut(state.tree, 1 - state.threshold)
    .map(g => [...g].sort((a, b) => pos.get(a) - pos.get(b)))
    .sort((a, b) => b.length - a.length || pos.get(a[0]) - pos.get(b[0]));
}

function meanWithin(g) {
  if (g.length < 2) return 1;
  let sum = 0, n = 0;
  for (let a = 0; a < g.length; a++) for (let b = a + 1; b < g.length; b++) { sum += state.S[g[a]][g[b]]; n++; }
  return sum / n;
}

// What every member of a group has in common, in readable form: roles, embeddings and couplings.
// A realm's presence is only listed when its role differs within the group (otherwise the role says it).
function sharedFeatures(g) {
  let shared = new Set(state.tokens[g[0]].keys());
  for (const i of g.slice(1)) shared = new Set([...shared].filter(t => state.tokens[i].has(t)));
  const withRole = new Set([...shared].filter(t => kindOfToken(t) === "role").map(t => t.slice(5).split("=")[0]));
  const keep = [...shared].filter(t => {
    const k = kindOfToken(t);
    if (k === "ctx") return false;
    if (k === "realm") return !withRole.has(t.slice(6));
    return true;
  });
  return sortTokens(keep, kindOfToken);
}

// ---- controls ----------------------------------------------------------------------------
function renderControls({ weightsOpen = false } = {}) {
  const box = document.getElementById("cs-controls");
  box.textContent = "";
  const out = h("output", {}, fmt(state.threshold));
  const range = h("input", { type: "range", min: "0.05", max: "0.95", step: "0.01", value: String(state.threshold), "aria-label": "Minimum similarity to group" });
  range.addEventListener("input", () => { state.threshold = +range.value; out.textContent = fmt(state.threshold); update(); });
  box.append(h("label", { class: "cs-threshold" }, ["Group models whose structural similarity is at least", range, out]));

  const grid = h("div", { class: "cs-weights-grid" });
  for (const [kind, label] of Object.entries(KINDS)) {
    const o = h("output", {}, String(state.weights[kind]));
    const r = h("input", { type: "range", min: "0", max: "3", step: "0.5", value: String(state.weights[kind]), "aria-label": `Weight: ${label}` });
    r.addEventListener("input", () => { state.weights[kind] = +r.value; o.textContent = r.value; update(); });
    grid.append(h("label", {}, [label, h("span", {}, [r, o])]));
  }
  const reset = h("button", { class: "cs-btn", type: "button", onclick: () => { state.weights = { ...DEFAULT_WEIGHTS }; renderControls({ weightsOpen: true }); update(); } }, "Reset weights");
  box.append(h("details", { class: "cs-weights", open: weightsOpen }, [
    h("summary", {}, "Adjust what counts"), grid, h("p", { style: "margin:.5rem 0 0" }, reset),
  ]));
}

// ---- groups ------------------------------------------------------------------------------
// What the whole group has in common, drawn as a CRS diagram with the Model viewer's own drawing.
function commonDiagram(g) {
  const st = sharedStructure(g.map(i => state.tokens[i]));
  return h("figure", { class: "cs-diagram" }, [
    crsSvg(st, { varies: st.varies, shortLabels: true }),
    h("figcaption", {}, st.varies.length
      ? `Common structure. Dashed: in every model but run differently (${st.varies.map(c => realmLabel(c)).join(", ")}).`
      : "Common structure"),
  ]);
}

// Compare two models, middle diagram: what both share (dashed: in both but run differently).
function pairSharedFigure(TA, TB) {
  const st = sharedStructure([TA, TB]);
  return h("figure", { class: "cs-diagram cs-pair-diagram" }, [
    crsSvg(st, { varies: st.varies, shortLabels: true }),
    h("figcaption", {}, st.varies.length ? "Both (what they share). Dashed: in both but run differently." : "Both (what they share)"),
  ]);
}

// Compare two models, side diagrams: only what this model has that the other lacks, plus the realms
// those differences attach to (a host, or the other end of a coupling), without which they can't be drawn.
function differenceFigure(T, other, name, otherName) {
  const st = differenceStructure(T, other);
  if (!st.count) {
    return h("figure", { class: "cs-diagram cs-pair-diagram cs-empty" }, [h("figcaption", {}, `${name}: nothing that ${otherName} lacks`)]);
  }
  return h("figure", { class: "cs-diagram cs-pair-diagram" }, [
    crsSvg(st, { shortLabels: true }),
    h("figcaption", {}, [name, h("br"), h("span", { class: "cs-fig-note" }, `not in ${otherName}, with the realms it attaches to`)]),
  ]);
}

function memberList(g) {
  return h("ul", { class: "cs-members" }, g.map(i => {
    const m = state.models[i];
    return h("li", {}, [
      h("span", {}, [h("a", { href: VIEWER + encodeURIComponent(m.id), title: "Open in the Model viewer" }, m.name), " ", h("span", { class: "fam" }, m.family)]),
      crsCode(m.crs),
    ]);
  }));
}

function renderGroups() {
  const host = document.getElementById("cs-groups");
  host.textContent = "";
  const multi = state.groups.filter(g => g.length > 1);
  const singles = state.groups.filter(g => g.length === 1).flat();
  host.append(h("p", { class: "cs-summary" },
    `${state.models.length} models with a CRS string · ${multi.length} groups · ${singles.length} not grouped at this level`
    + (state.noCrs.length ? ` · ${state.noCrs.length} without a CRS string (not shown)` : "")));
  const grid = h("div", { class: "cs-groups" });
  multi.forEach((g, k) => {
    const shared = sharedFeatures(g);
    grid.append(h("div", { class: "cs-group" }, [
      h("h3", {}, [`Group ${k + 1}`, h("span", {}, `${g.length} models · mean similarity ${fmt(meanWithin(g))}`)]),
      commonDiagram(g),                 // left-hand column
      memberList(g),                    // names | CRS strings
      h("div", { class: "cs-shared" }, [
        h("b", {}, "All share: "),
        ...(shared.length ? shared.map(t => h("span", { class: "cs-chip", title: t }, describe(t))) : ["no structural feature beyond the realms themselves"]),
      ]),
    ]));
  });
  if (singles.length) {
    grid.append(h("div", { class: "cs-group singles" }, [
      h("h3", {}, ["Not grouped at this level", h("span", {}, `${singles.length} models`)]),
      memberList(singles),
    ]));
  }
  host.append(grid);
}

// ---- matrix + tree -----------------------------------------------------------------------
function renderMatrix() {
  const host = document.getElementById("cs-matrix");
  host.textContent = "";
  const n = state.order.length, cell = 15, labelW = 150, treeW = 130, pad = 8, top = 8;
  const W = pad + treeW + labelW + n * cell + pad, H = top + n * cell + pad;
  const x0 = pad + treeW + labelW, y0 = top;
  const pos = new Map(state.order.map((m, k) => [m, k]));
  const lo = cssRgb("--heat-lo"), hi = cssRgb("--heat-hi");
  const heat = v => { const t = Math.pow(Math.max(0, Math.min(1, v)), 1.3); return `rgb(${lo.map((c, k) => Math.round(c + (hi[k] - c) * t)).join(",")})`; };
  const svg = s("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Similarity matrix, ordered by the clustering tree" });

  // cells: click one to compare that pair below
  const cells = s("g", {});
  state.order.forEach((a, r) => state.order.forEach((b, c) => {
    const v = state.S[a][b];
    const rect = s("rect", { x: x0 + c * cell, y: y0 + r * cell, width: cell - 1, height: cell - 1, fill: heat(v), class: "cs-cell" });
    const tip = s("title", {}); tip.textContent = `${state.models[a].name} ~ ${state.models[b].name}: ${fmt(v)}`; rect.append(tip);
    rect.addEventListener("click", () => {
      state.pair = [a, b]; renderPair();
      document.getElementById("cs-pair-card").scrollIntoView({ behavior: "smooth", block: "start" });
    });
    cells.append(rect);
  }));
  svg.append(cells);

  // the groups, outlined (each group is a contiguous block in tree order)
  for (const g of state.groups) {
    if (g.length < 2) continue;
    const p = g.map(i => pos.get(i)), a = Math.min(...p), b = Math.max(...p);
    svg.append(s("rect", { x: x0 + a * cell - 1, y: y0 + a * cell - 1, width: (b - a + 1) * cell + 1, height: (b - a + 1) * cell + 1,
      fill: "none", stroke: "var(--accent)", "stroke-width": 1.6, "pointer-events": "none" }));
  }

  // row labels
  state.order.forEach((m, r) => {
    const t = s("text", { x: x0 - 6, y: y0 + r * cell + cell / 2, "text-anchor": "end", "dominant-baseline": "middle", class: "cs-row-label" });
    t.textContent = state.models[m].name;
    svg.append(t);
  });

  // the tree: root on the left, leaves next to the labels; blue where merges are within the cut
  const maxH = state.tree.height || 1, cutD = 1 - state.threshold;
  const tx = height => pad + treeW * (1 - height / maxH);
  const tree = s("g", { class: "cs-tree" });
  (function draw(node) {
    if (!node.left) return y0 + pos.get(node.leaves[0]) * cell + cell / 2;
    const yl = draw(node.left), yr = draw(node.right), x = tx(node.height);
    tree.append(s("path", { d: `M${tx(node.left.height)},${yl} H${x} V${yr} H${tx(node.right.height)}`, class: node.height <= cutD + 1e-12 ? "within" : "" }));
    return (yl + yr) / 2;
  })(state.tree);
  svg.append(tree);
  if (cutD < maxH) {
    const x = tx(cutD);
    svg.append(s("line", { x1: x, y1: y0 - 4, x2: x, y2: y0 + n * cell, stroke: "var(--emd-blue)", "stroke-dasharray": "4 3", "stroke-width": 1.2 }));
  }
  host.append(svg);
}

// ---- compare two models ------------------------------------------------------------------
function renderPair() {
  const host = document.getElementById("cs-pair");
  host.textContent = "";
  const [a, b] = state.pair;
  const options = sel => state.models.map((m, i) => h("option", { value: String(i), selected: i === sel }, m.name));
  const selA = h("select", { "aria-label": "First model" }, options(a));
  const selB = h("select", { "aria-label": "Second model" }, options(b));
  selA.addEventListener("change", () => { state.pair = [+selA.value, state.pair[1]]; renderPair(); });
  selB.addEventListener("change", () => { state.pair = [state.pair[0], +selB.value]; renderPair(); });
  host.append(h("div", { class: "cs-pair-pick" }, [
    selA, "and", selB,
    h("span", { class: "cs-pair-score", title: "Structural similarity (1 = identical structure)" }, fmt(state.S[a][b])),
  ]));
  host.append(h("div", { class: "cs-pair-crs" }, [crsCode(state.models[a].crs), crsCode(state.models[b].crs)]));   // stacked, centred

  const TA = state.tokens[a], TB = state.tokens[b];
  const both = [...TA.keys()].filter(t => TB.has(t));
  const onlyA = [...TA.keys()].filter(t => !TB.has(t));
  const onlyB = [...TB.keys()].filter(t => !TA.has(t));
  // Each column: a CRS diagram on top, then the matching list. Left = the first model in full,
  // middle = what both share (dashed: in both but run differently), right = the second model in full.
  // Items as compact chips in realm colours, one row per kind; the full wording is on hover.
  const ROWS = [
    ["Realms",      t => t.startsWith("realm:")],
    ["Interactive", t => t.startsWith("role:") && t.endsWith("=dynamic")],
    ["Embedded",    t => t.startsWith("role:") && t.endsWith("=embedded")],
    ["Prescribed",  t => t.startsWith("role:") && t.endsWith("=prescribed")],
    ["Inside",      t => t.startsWith("embed:")],
    ["Coupled",     t => t.startsWith("couple:")],
    ["Context",     t => t.startsWith("ctx:")],
  ];
  const realmChip = c => { const el = h("span", { class: "cs-rchip" }, shortRealm(c)); el.style.setProperty("--realm", realmColor(c)); return el; };
  const chipFor = t => {
    const kind = kindOfToken(t), rest = t.slice(kind.length + 1);
    let parts;
    if (kind === "embed") { const [p, c] = rest.split(">"); parts = [realmChip(c), h("span", { class: "cs-glyph" }, "⊂"), realmChip(p)]; }
    else if (kind === "couple") { const [a, b] = rest.split("~"); parts = [realmChip(a), h("span", { class: "cs-glyph" }, "↔"), realmChip(b)]; }
    else parts = [realmChip(kind === "realm" ? rest : rest.split("=")[0])];
    return h("span", { class: "cs-item", title: describe(t) }, parts);
  };
  const column = (title, toks, fig) => {
    const rows = ROWS.map(([label, test]) => {
      const mine = sortTokens(toks.filter(test), kindOfToken);
      return mine.length ? h("div", { class: "cs-row" }, [h("span", { class: "cs-row-label" }, label), h("span", { class: "cs-row-items" }, mine.map(chipFor))]) : null;
    }).filter(Boolean);
    return h("div", { class: "cs-pair-col" }, [fig, h("h4", {}, `${title} (${toks.length})`), ...(rows.length ? rows : [h("p", { class: "cs-none" }, "nothing")])]);
  };
  const nameA = state.models[a].name, nameB = state.models[b].name;
  host.append(h("div", { class: "cs-pair-cols" }, [
    column(`Only in ${nameA}`, onlyA, differenceFigure(TA, TB, nameA, nameB)),
    column("Shared", both, pairSharedFigure(TA, TB)),
    column(`Only in ${nameB}`, onlyB, differenceFigure(TB, TA, nameB, nameA)),
  ]));
  host.append(h("p", { class: "cs-legend" }, "⊂ inside  ·  ↔ coupled  ·  hover a chip for the full description"));
}

// ---- how it works + data notes -----------------------------------------------------------
const EXPLAIN = {
  realm:  "which realms the model includes.",
  role:   "for each realm, whether it runs as its own interactive component, is embedded in another realm, or is prescribed (^).",
  embed:  "which realm sits inside which, for example land surface inside the atmosphere.",
  couple: "which realms exchange with each other.",
  ctx:    "each realm together with its surroundings: its host, what it holds and what it couples to (one round of Weisfeiler–Lehman relabelling). Two oceans that look alike on their own but sit differently in the model score differently.",
};

function renderMethod() {
  const body = document.getElementById("cs-method-body");
  body.textContent = "";
  body.append(
    h("p", {}, "Each model's CRS is read as a small graph: the realms are the nodes, embedding (A[L]: land inside the atmosphere) and coupling (A(O): atmosphere and ocean exchange) are the edges. The graph is then described by five kinds of feature:"),
    h("ul", {}, Object.entries(KINDS).map(([k, label]) => h("li", {}, [h("b", {}, `${label}: `), EXPLAIN[k]]))),
    h("p", {}, "Every realm appears at most once in a CRS, so two models' graphs line up by their realm codes and comparing the features is a complete structural comparison; no graph matching is needed. Similarity is the weighted overlap (Jaccard) of two models' features, from 0 (nothing in common) to 1 (the same structure). Models are grouped by average-linkage hierarchical clustering (UPGMA) on 1 − similarity, and the slider sets where the tree is cut."),
    h("p", {}, "This is an experimental page: the grouping is only as good as the CRS strings, and the weights are a first guess at what should count."),
  );
  const noCouplings = state.models.filter((m, i) => ![...state.tokens[i].values()].includes("couple"));
  if (noCouplings.length || state.noCrs.length) {
    body.append(h("p", {}, [
      h("b", {}, "Data notes. "),
      noCouplings.length ? `No couplings are listed in the CRS of ${noCouplings.map(m => m.name).join(", ")}, so it can only match on realms and roles; if its realms are in fact coupled, the string is incomplete. ` : "",
      state.noCrs.length ? `No CRS string: ${state.noCrs.map(m => m.name).join(", ")}.` : "",
    ]));
  }
}

// ---- start -------------------------------------------------------------------------------
function update() { compute(); renderGroups(); renderMatrix(); renderPair(); }

async function main() {
  const home = document.getElementById("cs-home");
  const setHome = () => { if (window.NAV_PREFIX) home.href = window.NAV_PREFIX; };
  setHome(); requestAnimationFrame(setHome);
  const status = document.getElementById("cs-status");
  try {
    const all = await loadModels();
    state.models = all.filter(m => m.crs);
    state.noCrs = all.filter(m => !m.crs);
    if (state.models.length < 2) { status.textContent = "Not enough models with a CRS string to compare."; return; }
    state.tokens = state.models.map(m => tokenize(m.crs));
    compute();
    // start the comparison on the most similar pair from different families (the interesting kind)
    let best = [0, 1], bestS = -1;
    state.models.forEach((ma, i) => state.models.forEach((mb, j) => {
      if (j > i && ma.family !== mb.family && state.S[i][j] > bestS) { bestS = state.S[i][j]; best = [i, j]; }
    }));
    state.pair = best;
    status.remove();
    for (const id of ["cs-groups-card", "cs-matrix-card", "cs-pair-card"]) document.getElementById(id).hidden = false;
    renderControls();
    renderGroups(); renderMatrix(); renderPair(); renderMethod();
  } catch (e) {
    status.textContent = `Could not load the models: ${e.message}`;
  }
}
main();
