// forest.js — an unsupervised random forest over CRS structure features (Breiman's method).
//
// There is no label to predict, so each tree learns to tell the REAL models from SHUFFLED ones:
// synthetic rows in which every feature is drawn independently from its real distribution. That
// keeps each feature's frequency but breaks the combinations, so to separate real from shuffled a
// tree has to ask about the combinations real models actually have (e.g. "land ice interactive"
// together with "land ice ↔ ocean coupled").
//
// Likeness (proximity) of two real models = the share of trees in which they end in the same leaf.
// Because every split is a yes/no question about one feature, we can also say WHY: which question
// separated a pair in each tree, and which shared answers kept them together.
//
// X is an array of rows (one per real model), each an array of 0/1 feature values.

/** Small seeded random number generator (mulberry32), so a run can be repeated exactly. */
export function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const gini = (c0, c1) => { const n = c0 + c1; if (!n) return 0; const q = c1 / n; return 2 * q * (1 - q); };

function sampleFeatures(p, k, rand) {
  const all = Array.from({ length: p }, (_, i) => i);
  for (let i = 0; i < k; i++) { const j = i + Math.floor(rand() * (p - i)); [all[i], all[j]] = [all[j], all[i]]; }
  return all.slice(0, k);
}

// One tree: rows `idx` of the training set (rows R, labels y: 1 real, 0 shuffled). At each node it
// tries `mtry` random features and keeps the yes/no split that best separates real from shuffled
// (largest Gini decrease); if none of those splits anything it tries every feature. Grows until a
// node is pure or cannot be split. Importance gathers each feature's total decrease (weighted by size).
function growTree(R, y, idx, p, mtry, rand, importance) {
  let c1 = 0;
  for (const i of idx) c1 += y[i];
  const c0 = idx.length - c1;
  const node = { n: idx.length, real: c1 };
  if (c0 === 0 || c1 === 0) return node;
  const parent = gini(c0, c1);
  const bestOf = feats => {
    let best = null;
    for (const f of feats) {
      let l0 = 0, l1 = 0, r0 = 0, r1 = 0;
      for (const i of idx) { if (R[i][f]) { if (y[i]) r1++; else r0++; } else { if (y[i]) l1++; else l0++; } }
      const nl = l0 + l1, nr = r0 + r1;
      if (!nl || !nr) continue;
      const dec = parent - (nl * gini(l0, l1) + nr * gini(r0, r1)) / idx.length;
      if (!best || dec > best.dec) best = { f, dec };
    }
    return best;
  };
  const best = bestOf(sampleFeatures(p, mtry, rand)) || bestOf(Array.from({ length: p }, (_, i) => i));
  if (!best) return node;                                   // every row identical on every feature
  importance[best.f] += best.dec * idx.length;
  const no = [], yes = [];
  for (const i of idx) (R[i][best.f] ? yes : no).push(i);
  node.f = best.f;
  node.no = growTree(R, y, no, p, mtry, rand, importance);
  node.yes = growTree(R, y, yes, p, mtry, rand, importance);
  return node;
}

/** Train the forest. Each tree gets its own shuffled rows and a bootstrap sample of real + shuffled.
 *  Returns { trees, importance (mean decrease per feature, summing to 1), p, mtry, seed }. */
export function trainForest(X, { trees = 500, seed = 1, mtry } = {}) {
  const n = X.length, p = X[0].length, rand = rng(seed);
  mtry = mtry || Math.max(1, Math.round(Math.sqrt(p)));
  const importance = new Float64Array(p), forest = [];
  for (let t = 0; t < trees; t++) {
    const shuffled = Array.from({ length: n }, () => Array.from({ length: p }, (_, f) => X[Math.floor(rand() * n)][f]));
    const R = [...X, ...shuffled], y = [...X.map(() => 1), ...shuffled.map(() => 0)];
    const boot = Array.from({ length: R.length }, () => Math.floor(rand() * R.length));
    forest.push(growTree(R, y, boot, p, mtry, rand, importance));
  }
  const total = importance.reduce((a, b) => a + b, 0) || 1;
  return { trees: forest, importance: [...importance].map(v => v / total), p, mtry, seed };
}

/** The leaf a row ends in. */
export function leafOf(tree, x) {
  let node = tree;
  while (node.f !== undefined) node = x[node.f] ? node.yes : node.no;
  return node;
}

/** Likeness of every pair of real models: the share of trees in which both end in the same leaf. */
export function proximity(model, X) {
  const n = X.length, P = Array.from({ length: n }, () => new Array(n).fill(0));
  for (const tree of model.trees) {
    const leaves = X.map(x => leafOf(tree, x));
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) if (leaves[i] === leaves[j]) { P[i][j]++; P[j][i]++; }
  }
  const T = model.trees.length;
  for (let i = 0; i < n; i++) { for (let j = 0; j < n; j++) P[i][j] /= T; P[i][i] = 1; }
  return P;
}

/** One readable decision tree over the REAL models, built from the forest's likeness P.
 *  At each node, of the questions that split the node's models into two non-empty sides, it takes
 *  the one that leaves the least un-likeness inside the two sides (the sum of 1 - likeness over the
 *  pairs within each side: like variance reduction in a regression tree; ties go to the more
 *  important question). It stops when the node's models are already alike enough (mean likeness
 *  >= minLikeness), when no question separates them, or at maxDepth.
 *  Node: { models, likeness, f?, yes?, no? } (f = the question's index; a leaf has no f). */
export function likenessTree(P, X, importance, { minLikeness = 0.5, maxDepth = 6 } = {}) {
  const p = X[0].length;
  const pairsSum = S => { let s = 0; for (let a = 0; a < S.length; a++) for (let b = a + 1; b < S.length; b++) s += 1 - P[S[a]][S[b]]; return s; };
  const meanLikeness = S => { if (S.length < 2) return 1; let s = 0, n = 0; for (let a = 0; a < S.length; a++) for (let b = a + 1; b < S.length; b++) { s += P[S[a]][S[b]]; n++; } return s / n; };
  const grow = (S, depth) => {
    const node = { models: S, likeness: meanLikeness(S) };
    if (S.length < 2 || node.likeness >= minLikeness || depth >= maxDepth) return node;
    let best = null;
    for (let f = 0; f < p; f++) {
      const yes = S.filter(i => X[i][f]), no = S.filter(i => !X[i][f]);
      if (!yes.length || !no.length) continue;
      const within = pairsSum(yes) + pairsSum(no);
      if (!best || within < best.within - 1e-12 || (Math.abs(within - best.within) <= 1e-12 && importance[f] > importance[best.f])) best = { f, within, yes, no };
    }
    if (!best) return node;                                   // the models answer every question alike
    node.f = best.f;
    node.yes = grow(best.yes, depth + 1);
    node.no = grow(best.no, depth + 1);
    return node;
  };
  return grow(X.map((_, i) => i), 0);
}
