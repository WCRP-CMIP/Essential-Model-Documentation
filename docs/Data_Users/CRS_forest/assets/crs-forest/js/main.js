// main.js — CRS random forest (experimental): likeness of models from an unsupervised random
// forest over their CRS structure, and the yes/no questions behind it. Algorithm: ./forest.js.
// Features come from the CRS similarity page's tokenizer; the CRS parser and drawing helpers are the
// Model viewer's own, so all three pages read a CRS the same way.

import { trainForest, proximity, likenessTree } from "./forest.js";
import { buildTreeSvg } from "./tree-svg.js";
import { tokenize, describe, kindOfToken, upgma, cut } from "../../../../CRS_similarity/assets/crs-similarity/js/similarity.js";
import { realmColor } from "../../../../Model_viewer/assets/model-page/js/crs.js";
import { shortRealm } from "../../../../Model_viewer/assets/model-page/js/components/crs-diagram.js";
import { exportSvg, DOWNLOAD_ICON } from "../../../../Model_viewer/assets/model-page/js/svg-export.js";   // as the Model viewer's downloads

const BASE = "https://wcrp-cmip.github.io/Essential-Model-Documentation/";
const VIEWER = "../Model_viewer/?model=";
const TREE_OPTIONS = [500, 1000, 2000];   // forest sizes offered at the top of the page

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
const pct = x => `${Math.round(x * 100)}%`;

// The CRS string with each realm code in its realm colour (as on the CRS similarity page).
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
    if (ch === "[") depth++; else if (ch === "]") depth = Math.max(0, depth - 1);
    code.append(h("span", { class: "pun" }, ch));
    i++;
  }
  return code;
}

// A question as chips in realm colours: "aer ⊂ atm", "atm ↔ ice", or one realm.
const realmChip = c => { const el = h("span", { class: "cs-rchip" }, shortRealm(c)); el.style.setProperty("--realm", realmColor(c)); return el; };
function chipsFor(token) {
  const kind = kindOfToken(token), rest = token.slice(kind.length + 1);
  if (kind === "embed") { const [p, c] = rest.split(">"); return h("span", { class: "cs-item boxed" }, [realmChip(c), h("span", { class: "cs-glyph" }, "⊂"), realmChip(p)]); }
  if (kind === "couple") { const [a, b] = rest.split("~"); return h("span", { class: "cs-item boxed" }, [realmChip(a), h("span", { class: "cs-glyph" }, "↔"), realmChip(b)]); }
  if (kind === "role") {                        // how the realm is run, as one word: "aer embedded"
    const [c, role] = rest.split("=");
    return h("span", { class: "cs-item boxed" }, [realmChip(c), h("span", { class: "rf-role" }, role === "dynamic" ? "interactive" : role)]);
  }
  return h("span", { class: "cs-item" }, [realmChip(rest)]);        // "has <realm>"
}

// ---- data --------------------------------------------------------------------------------
const state = { models: [], noCrs: [], tokens: [], questions: [], X: [], forest: null, P: null, tree: null, groups: [], seed: 42, trees: 500, threshold: 0.5, treeRoot: null };

async function loadModels() {
  const index = await (await fetch(BASE + "model/_graph.json")).json();
  const ids = (index.contents || index["@graph"] || []).map(e => (typeof e === "string" ? e : e["@id"]));
  const recs = await Promise.all(ids.map(id => fetch(`${BASE}model/${id}.json`).then(r => (r.ok ? r.json() : null)).catch(() => null)));
  return recs
    .map((m, k) => m && { id: ids[k], name: m.validation_key || ids[k], family: m.family || "", crs: (m.crs || "").trim() })
    .filter(Boolean)
    .sort((a, b) => a.name.localeCompare(b.name));
}

// The yes/no questions: realms present, how each is run, what sits inside what, what is coupled.
// Questions that divide the models identically (or exactly oppositely, e.g. "sea ice embedded" and
// "sea ice interactive") are one question asked in different words: they are merged, so their
// importance is not shared out between them. Questions every model answers the same way are dropped.
function buildQuestions(T) {
  const n = T.length, ORDER = ["embed", "couple", "role", "realm"];          // preferred wording first
  const all = new Set();
  for (const M of T) for (const t of M.keys()) if (ORDER.includes(kindOfToken(t))) all.add(t);
  const byPattern = new Map();
  for (const t of [...all].sort((a, b) => ORDER.indexOf(kindOfToken(a)) - ORDER.indexOf(kindOfToken(b)) || a.localeCompare(b))) {
    const bits = T.map(M => (M.has(t) ? 1 : 0)), yes = bits.reduce((a, b) => a + b, 0);
    if (yes === 0 || yes === n) continue;
    const flip = bits[0] === 1, key = bits.map(b => b ^ (flip ? 1 : 0)).join("");
    if (!byPattern.has(key)) byPattern.set(key, { token: t, flip, bits, same: [], opposite: [] });
    else { const q = byPattern.get(key); (q.flip === flip ? q.same : q.opposite).push(t); }
  }
  return [...byPattern.values()];
}

const qLabel = q => describe(q.token);
const qTitle = q => [qLabel(q), q.same.length ? `same as: ${q.same.map(describe).join("; ")}` : "", q.opposite.length ? `opposite of: ${q.opposite.map(describe).join("; ")}` : ""].filter(Boolean).join("\n");
const qChip = q => { const el = chipsFor(q.token); el.title = qTitle(q); return el; };

function compute() {
  state.forest = trainForest(state.X, { trees: state.trees, seed: state.seed });
  state.P = proximity(state.forest, state.X);
  state.tree = upgma(state.P.map(row => row.map(x => 1 - x)));
  regroup();
}
function regroup() {
  const pos = new Map(state.tree.leaves.map((m, k) => [m, k]));
  state.groups = cut(state.tree, 1 - state.threshold)
    .map(g => [...g].sort((a, b) => pos.get(a) - pos.get(b)))
    .sort((a, b) => b.length - a.length || pos.get(a[0]) - pos.get(b[0]));
}

// ---- controls ----------------------------------------------------------------------------
// Forest size and seed. Changing either regrows the forest and redraws everything.
function renderControls() {
  const box = document.getElementById("rf-controls");
  box.textContent = "";
  const regrow = () => { compute(); renderAll(); };
  const size = h("select", { "aria-label": "Number of trees" }, TREE_OPTIONS.map(n => h("option", { value: String(n), selected: n === state.trees }, `${n} trees`)));
  size.addEventListener("change", () => { state.trees = +size.value; regrow(); });
  const seed = h("input", { type: "number", min: "1", step: "1", value: String(state.seed), class: "rf-seed", "aria-label": "Seed" });
  seed.addEventListener("change", () => { state.seed = Math.max(1, Math.floor(+seed.value) || 1); regrow(); });
  // a random seed; it shows in the seed box, so the run can be repeated
  const rerun = h("button", { class: "cs-btn", type: "button", onclick: () => { state.seed = 1 + Math.floor(Math.random() * 99999); regrow(); } }, "Select a random seed");
  box.append(h("div", { class: "rf-controls" }, [
    h("label", { class: "rf-field" }, ["Forest", size]),
    h("label", { class: "rf-field" }, ["Seed", seed]),
    rerun,
    h("span", {}, `${state.models.length} models · ${state.questions.length} yes/no questions`),
    h("span", { class: "rf-hint" }, "A different seed grows a different forest, and more trees give steadier numbers; what stays the same is robust."),
  ]));
}

// ---- how much the forest relies on each question -----------------------------------------
// How differently the models answer question g, between those answering yes and no to question f.
function association(f, g) {
  const yes = [], no = [];
  state.X.forEach((x, i) => (x[f] ? yes : no).push(i));
  const gYes = yes.filter(i => state.X[i][g]).length, gNo = no.filter(i => state.X[i][g]).length;
  return { yesN: yes.length, noN: no.length, gYes, gNo, diff: gYes / yes.length - gNo / no.length };
}
// The realm(s) a question is about: the realm placed inside another, the two coupled realms, or the realm itself.
function subjects(token) {
  const kind = kindOfToken(token), rest = token.slice(kind.length + 1);
  if (kind === "embed") return [rest.split(">")[1]];
  if (kind === "couple") return rest.split("~");
  return [rest.split("=")[0]];
}
// The question about OTHER realms whose answer goes most with f's (so the example shows design choices
// that travel together, not the same fact asked twice, e.g. "aerosol inside atmosphere" / "aerosol embedded").
const strongest = f => {
  const own = new Set(subjects(state.questions[f].token));
  return state.questions.map((_, g) => g).filter(g => g !== f && !subjects(state.questions[g].token).some(c => own.has(c)))
    .map(g => ({ g, ...association(f, g) })).sort((a, b) => Math.abs(b.diff) - Math.abs(a.diff))[0];
};

// Two worked examples from the current forest: the top question and the lowest one, with the reason in numbers.
function renderExamples(imp) {
  const box = document.getElementById("rf-examples");
  box.textContent = "";
  const n = state.models.length, yesOf = f => state.questions[f].bits.reduce((a, b) => a + b, 0);
  const quote = f => `“${qLabel(state.questions[f])}?”`;
  const example = (kind, f, value, text) => h("div", { class: `rf-example ${kind}` }, [
    h("div", { class: "rf-example-head" }, [h("b", {}, kind === "high" ? "High score" : "Low score"), qChip(state.questions[f]), h("span", { class: "rf-q-val" }, `${(value * 100).toFixed(1)}%`)]),
    h("p", {}, text),
  ]);
  const [hv, hf] = imp[0], s = strongest(hf);
  box.append(example("high", hf, hv,
    `${quote(hf)} Of the ${s.yesN} models that answer yes, ${s.gYes} also answer yes to ${quote(s.g)}; of the ${s.noN} that answer no, ${s.gNo} ${s.gNo === 1 ? "does" : "do"}. ` +
    `One answer goes with the other, so knowing the first tells you about the second (and more like it): the trees lean on it.`));
  const [lv, lf] = imp[imp.length - 1], yl = yesOf(lf);
  let why;
  if (yl <= 3 || yl >= n - 3) {
    const k = Math.min(yl, n - yl);
    why = `Only ${k} of the ${n} models answer${k === 1 ? "s" : ""} ${yl <= 3 ? "yes" : "no"}, so it sets apart ${k === 1 ? "just one model" : `just ${k} models`} and says little about the rest.`;
  } else {
    const t = strongest(lf);
    why = `${yl} of the ${n} models answer yes, but those models are much like the ones that answer no on everything else (at most a ${Math.round(Math.abs(t.diff) * 100)}-point difference in any other answer), so it says little about the rest.`;
  }
  box.append(example("low", lf, lv, `${quote(lf)} ${why}`));
}

function renderQuestions() {
  const host = document.getElementById("rf-questions");
  host.textContent = "";
  const imp = state.forest.importance.map((v, f) => [v, f]).sort((a, b) => b[0] - a[0]);
  const max = imp[0][0] || 1;
  const yesCount = q => q.bits.reduce((a, b) => a + b, 0);
  renderExamples(imp);
  host.append(h("div", { class: "rf-imp" }, imp.map(([v, f]) => {   // every question, highest to lowest
    const q = state.questions[f];
    return h("div", { class: "rf-q" }, [
      h("span", { class: "rf-q-chip" }, qChip(q)),
      h("span", { class: "rf-q-label", title: qTitle(q) }, [qLabel(q), h("span", { class: "rf-q-note" }, ` · ${yesCount(q)} of ${state.models.length} yes`)]),
      h("span", { class: "rf-bar" }, h("span", { style: `width:${(100 * v / max).toFixed(1)}%` })),
      h("span", { class: "rf-q-val" }, `${(v * 100).toFixed(1)}%`),
    ]);
  })));
}

// ---- questions that go together ----------------------------------------------------------
// For every pair of questions about different realms: the four counts and the phi correlation.
function questionPairs() {
  const n = state.models.length, Q = state.questions, MIN = 3;
  const usable = Q.map((q, f) => f).filter(f => { const y = Q[f].bits.reduce((a, b) => a + b, 0); return y >= MIN && n - y >= MIN; });
  const pairs = [];
  for (let a = 0; a < usable.length; a++) for (let b = a + 1; b < usable.length; b++) {
    const f = usable[a], g = usable[b];
    const sf = new Set(subjects(Q[f].token));
    if (subjects(Q[g].token).some(c => sf.has(c))) continue;               // same realm: linked by definition
    let both = 0, onlyF = 0, onlyG = 0, neither = 0;
    for (let i = 0; i < n; i++) { const x = Q[f].bits[i], y = Q[g].bits[i]; if (x && y) both++; else if (x) onlyF++; else if (y) onlyG++; else neither++; }
    const phi = (both * neither - onlyF * onlyG) / Math.sqrt((both + onlyF) * (onlyG + neither) * (both + onlyG) * (onlyF + neither));
    pairs.push({ f, g, both, onlyF, onlyG, neither, phi });
  }
  return pairs;
}

function renderPairs() {
  const host = document.getElementById("rf-pairs");
  host.textContent = "";
  const pairs = questionPairs();
  const row = p => h("div", { class: "rf-pairrow" }, [
    h("span", { class: "rf-q-chip" }, qChip(state.questions[p.f])),
    h("span", { class: "cs-glyph" }, "&"),
    h("span", { class: "rf-q-chip" }, qChip(state.questions[p.g])),
    h("span", { class: "rf-pair-text", title: `${qLabel(state.questions[p.f])}? / ${qLabel(state.questions[p.g])}?` },
      [h("span", { class: "rf-pair-q" }, `${qLabel(state.questions[p.f])} · ${qLabel(state.questions[p.g])}`), h("br"), h("span", { class: "rf-q-note" }, `${p.both} · ${p.onlyF} · ${p.onlyG} · ${p.neither}`)]),
    h("span", { class: "rf-q-val" }, p.phi.toFixed(2)),
  ]);
  const together = pairs.filter(p => p.phi > 0).sort((a, b) => b.phi - a.phi).slice(0, 10);
  const apart = pairs.filter(p => p.phi < 0).sort((a, b) => a.phi - b.phi).slice(0, 10);
  host.append(h("div", { class: "rf-cols rf-cols-even" }, [
    h("div", {}, [h("h3", { class: "rf-h3" }, "Usually together"), ...(together.length ? together.map(row) : [h("p", { class: "cs-none" }, "none")])]),
    h("div", {}, [h("h3", { class: "rf-h3" }, "Rarely together"), ...(apart.length ? apart.map(row) : [h("p", { class: "cs-none" }, "none")])]),
  ]));
}

// ---- likeness groups ---------------------------------------------------------------------
function memberList(g) {
  return h("ul", { class: "rf-members" }, g.map(i => {
    const m = state.models[i];
    return h("li", {}, [
      h("span", {}, [h("a", { href: VIEWER + encodeURIComponent(m.id), title: "Open in the Model viewer" }, m.name), " ", h("span", { class: "fam" }, m.family)]),
      crsCode(m.crs),
    ]);
  }));
}

function meanLikeness(g) {
  let s = 0, n = 0;
  for (let a = 0; a < g.length; a++) for (let b = a + 1; b < g.length; b++) { s += state.P[g[a]][g[b]]; n++; }
  return n ? s / n : 1;
}

// The questions every member answers the same way, most important first: what all have, what none have.
function agreed(g, value, limit) {
  return state.forest.importance.map((v, f) => [v, f]).sort((a, b) => b[0] - a[0])
    .filter(([, f]) => g.every(i => state.X[i][f] === value)).slice(0, limit).map(([, f]) => state.questions[f]);
}

// The slider is built once (rebuilding it while it is being dragged would end the drag); moving it
// regroups the models and redraws the tree, which stops at the same likeness.
function renderGroupControls() {
  const host = document.getElementById("rf-groups-controls");
  host.textContent = "";
  const out = h("output", {}, state.threshold.toFixed(2));
  const range = h("input", { type: "range", min: "0.05", max: "0.95", step: "0.05", value: String(state.threshold), "aria-label": "Minimum likeness to group" });
  range.addEventListener("input", () => { state.threshold = +range.value; out.textContent = state.threshold.toFixed(2); regroup(); renderGroups(); renderTree(); });
  host.append(h("label", { class: "cs-threshold" }, ["Group models that end in the same leaf in at least this share of trees", range, out]));
}

// A group's card: its models with their CRS, mean likeness, and what they all have / none have.
function groupCard(g, title) {
  const have = agreed(g, 1, 6), none = agreed(g, 0, 4);
  return h("div", { class: "cs-group rf-group" }, [
    h("h3", {}, [title, h("span", {}, g.length > 1 ? `${g.length} models · mean likeness ${pct(meanLikeness(g))}` : "1 model")]),
    memberList(g),
    h("div", { class: "rf-why" }, [
      h("div", { class: "cs-row" }, [h("span", { class: "cs-row-label" }, "All have"), h("span", { class: "cs-row-items" }, have.length ? have.map(qChip) : "—")]),
      h("div", { class: "cs-row" }, [h("span", { class: "cs-row-label" }, "None have"), h("span", { class: "cs-row-items" }, none.length ? none.map(qChip) : "—")]),
    ]),
  ]);
}

// The panel at the bottom of the screen that shows a tree node's models while it is pointed at.
function showHover(models, title) {
  const box = document.getElementById("rf-hover");
  box.textContent = "";
  box.append(h("div", { class: "rf-groups" }, groupCard(models, title)));
  box.hidden = false;
}
function hideHover() { document.getElementById("rf-hover").hidden = true; }

function renderGroups() {
  const host = document.getElementById("rf-groups");
  host.textContent = "";
  const multi = state.groups.filter(g => g.length > 1), singles = state.groups.filter(g => g.length === 1).flat();
  host.append(h("p", { class: "cs-summary" }, `${multi.length} groups · ${singles.length} not grouped at this level`));
  const list = h("div", { class: "rf-groups" });
  multi.forEach((g, k) => list.append(groupCard(g, `Group ${k + 1}`)));
  if (singles.length) list.append(h("div", { class: "cs-group rf-group" }, [h("h3", {}, ["Not grouped at this level", h("span", {}, `${singles.length} models`)]), memberList(singles)]));
  host.append(list);
}

// ---- splits as a decision tree -----------------------------------------------------------
// Drawn left to right: a question box, then its "yes" and "no" branches; each leaf lists its models.
function renderTree() {
  const host = document.getElementById("rf-tree");
  host.textContent = "";
  const root = likenessTree(state.P, state.X, state.forest.importance, { minLikeness: state.threshold, maxDepth: 6 });
  let leaves = 0, depth = 0;
  const draw = (node, d) => {
    depth = Math.max(depth, d);
    if (node.f === undefined) {
      leaves++;
      return h("div", { class: "dt-leaf", onmouseenter: () => showHover(node.models, "End group"), onmouseleave: hideHover }, [
        h("div", { class: "dt-leaf-head" }, `${node.models.length} model${node.models.length > 1 ? "s" : ""}${node.models.length > 1 ? ` · ${pct(node.likeness)} alike` : ""}`),
        h("div", { class: "dt-leaf-models" }, node.models.map(i => h("a", { href: VIEWER + encodeURIComponent(state.models[i].id), title: state.models[i].crs }, state.models[i].name))),
      ]);
    }
    const q = state.questions[node.f];
    return h("div", { class: "dt-node" }, [
      h("div", { class: "dt-q", title: qTitle(q), onmouseenter: () => showHover(node.models, `${qLabel(q)}? (the models asked)`), onmouseleave: hideHover }, [h("span", {}, qChip(q)), h("span", { class: "dt-q-text" }, `${qLabel(q)}?`), h("span", { class: "dt-q-n" }, `${node.models.length} models`)]),
      h("div", { class: "dt-branches" }, [branch("yes", node.yes, d), branch("no", node.no, d)]),
    ]);
  };
  const branch = (label, child, d) => h("div", { class: "dt-branch" }, [h("span", { class: `dt-edge ${label}` }, label), draw(child, d + 1)]);
  hideHover();
  const tree = draw(root, 0);
  state.treeRoot = root;
  const dl = h("button", { class: "cs-btn dt-download", type: "button", title: "Download this tree as an SVG file", onclick: downloadTree });
  dl.innerHTML = `${DOWNLOAD_ICON}<span>Download SVG</span>`;
  host.append(h("div", { class: "dt-bar" }, [h("p", { class: "cs-summary" }, `${leaves} end groups · ${depth} questions deep at most`), dl]), h("div", { class: "dt-scroll" }, tree));
}

// The tree as an SVG file, through the Model viewer's exporter (heading, CMIP logo, metadata, credit).
// The exporter copies computed styles, so the drawing is put in the page (off-screen) while it runs.
async function downloadTree() {
  if (!state.treeRoot) return;
  const svg = buildTreeSvg(state.treeRoot, {
    question: f => ({ token: state.questions[f].token, label: qLabel(state.questions[f]) }),
    modelName: i => state.models[i].name, realmColor, shortRealm,
  });
  const holder = h("div", { style: "position:fixed;left:-100000px;top:0;background:#ffffff" }, svg);
  document.body.append(holder);
  try {
    await exportSvg(svg, {
      title: "CRS random forest: summary decision tree",
      fileName: `emd-crs-forest-tree-${state.trees}-trees-seed-${state.seed}`,
      heading: "CRS random forest: summary decision tree",
      subheading: `${state.trees} trees · seed ${state.seed} · branches stop at likeness ${state.threshold.toFixed(2)}`,
      header: 58,
    });
  } finally {
    holder.remove();
  }
}

// ---- how it works ------------------------------------------------------------------------
const link = (href, text) => h("a", { href, target: "_blank", rel: "noopener" }, text);
const REF = {
  breiman2001: "https://doi.org/10.1023/A:1010933404324",
  cutler: "https://www.stat.berkeley.edu/~breiman/RandomForests/cc_home.htm",
  shi2006: "https://doi.org/10.1198/106186006X94072",
  cart: "https://doi.org/10.1201/9781315139470",
  strobl2007: "https://doi.org/10.1186/1471-2105-8-25",
  upgma: "https://en.wikipedia.org/wiki/UPGMA",
};

function renderMethod() {
  const body = document.getElementById("rf-method-body");
  body.textContent = "";
  const merged = state.questions.filter(q => q.same.length || q.opposite.length).length;
  body.append(
    h("p", {}, "Each model's CRS is turned into yes/no answers: which realms it has, how each realm is run (interactive, embedded, prescribed), which realm sits inside which, and which realms are coupled. Questions every model answers the same way are dropped, and questions that divide the models identically, or exactly oppositely, are one question asked in different words, so they are merged (hover a question to see its other wordings)" + (merged ? `; ${merged} questions here have other wordings.` : ".")),
    h("p", {}, [`The forest is a `, link(REF.breiman2001, "random forest"), ` (Breiman, 2001) of ${state.trees} decision trees. There is no answer to predict, so it is grown the `,
      link(REF.cutler, "unsupervised way"), ` (Breiman and Cutler; `, link(REF.shi2006, "Shi and Horvath, 2006"),
      `): each tree learns to tell the real models from shuffled ones, in which every answer is drawn independently from how often it occurs among real models. Shuffling keeps each answer's frequency but breaks the combinations, so the trees have to ask about the combinations real models actually have. Each tree sees a random resample of the rows and, at every split, a random subset of the questions.`]),
    h("p", {}, [`Two models' likeness is their `, link(REF.cutler, "proximity"), `: the share of trees in which they end in the same leaf. Groups are formed from likeness by average-linkage clustering (`, link(REF.upgma, "UPGMA"), `), as on the CRS similarity page.`]),
    h("p", {}, [`The summary tree is built for this page rather than taken from the forest. It is grown on the real models only, in the manner of a `, link(REF.cart, "CART"),
      ` regression tree (Breiman et al., 1984): at each node it takes the question that leaves the least un-likeness (1 − likeness, summed over the pairs) inside its two branches, and a branch stops at the likeness set by the slider.`]),
    h("p", {}, [`A question's importance is its share of the forest's total decrease in Gini impurity (Breiman, 2001). Impurity-based importance can favour some kinds of feature over others (`,
      link(REF.strobl2007, "Strobl et al., 2007"), `), which matters less here because every question is yes/no. With only a few dozen models the forest is small: use the seed and forest-size controls to see which results hold up.`]),
    h("h3", { class: "rf-h3" }, "References"),
    h("ul", { class: "rf-refs" }, [
      h("li", {}, ["Breiman, L. (2001). Random forests. ", h("i", {}, "Machine Learning"), ", 45, 5–32. ", link(REF.breiman2001, "doi:10.1023/A:1010933404324")]),
      h("li", {}, ["Breiman, L. and Cutler, A. Random Forests: unsupervised learning and proximities. ", link(REF.cutler, "stat.berkeley.edu")]),
      h("li", {}, ["Shi, T. and Horvath, S. (2006). Unsupervised learning with random forest predictors. ", h("i", {}, "Journal of Computational and Graphical Statistics"), ", 15(1), 118–138. ", link(REF.shi2006, "doi:10.1198/106186006X94072")]),
      h("li", {}, ["Breiman, L., Friedman, J., Olshen, R. and Stone, C. (1984). ", h("i", {}, "Classification and Regression Trees"), ". ", link(REF.cart, "doi:10.1201/9781315139470")]),
      h("li", {}, ["Strobl, C., Boulesteix, A.-L., Zeileis, A. and Hothorn, T. (2007). Bias in random forest variable importance measures. ", h("i", {}, "BMC Bioinformatics"), ", 8, 25. ", link(REF.strobl2007, "doi:10.1186/1471-2105-8-25")]),
      h("li", {}, ["Sokal, R. and Michener, C. (1958). A statistical method for evaluating systematic relationships (UPGMA). ", link(REF.upgma, "overview")]),
    ]),
  );
  if (state.noCrs.length) body.append(h("p", {}, [h("b", {}, "Data notes. "), `No CRS string: ${state.noCrs.map(m => m.name).join(", ")}.`]));
}

// ---- start -------------------------------------------------------------------------------
function renderAll() { renderControls(); renderTree(); renderGroupControls(); renderGroups(); renderQuestions(); renderPairs(); renderMethod(); }

async function main() {
  const home = document.getElementById("rf-home");
  const setHome = () => { if (window.NAV_PREFIX) home.href = window.NAV_PREFIX; };
  setHome(); requestAnimationFrame(setHome);
  const status = document.getElementById("rf-status");
  try {
    const all = await loadModels();
    state.models = all.filter(m => m.crs);
    state.noCrs = all.filter(m => !m.crs);
    if (state.models.length < 3) { status.textContent = "Not enough models with a CRS string."; return; }
    state.tokens = state.models.map(m => tokenize(m.crs));
    state.questions = buildQuestions(state.tokens);
    state.X = state.models.map((_, i) => state.questions.map(q => q.bits[i]));
    compute();
    status.remove();
    for (const id of ["rf-controls-card", "rf-tree-card", "rf-groups-card", "rf-questions-card", "rf-pairs-card"]) document.getElementById(id).hidden = false;
    renderAll();
  } catch (e) {
    status.textContent = `Could not build the forest: ${e.message}`;
  }
}
main();
