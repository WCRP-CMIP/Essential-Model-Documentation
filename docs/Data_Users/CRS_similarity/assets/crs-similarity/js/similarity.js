// similarity.js — group models by the STRUCTURE of their CRS (Canonical Realm String).
//
// A CRS is a small labelled graph:
//   nodes  = realms (A, Ac, Ae, L, Li, O, Ob, Si), each appearing at most once, with a role:
//            dynamic (its own interactive component), embedded (inside another realm),
//            or prescribed (`^`: forced, not interactive)
//   edges  = embedding  P[C]  (C lives inside P, directed)
//            coupling   P(C)  (P and C exchange, treated as symmetric)
//
// Each model becomes a set of tokens describing that graph:
//   realm   — which realms are present
//   role    — how each realm is run
//   embed   — which realm sits inside which
//   couple  — which realms are coupled
//   ctx     — each realm together with its neighbourhood (one round of Weisfeiler–Lehman
//             relabelling): its role, its host, what it holds and what it couples to
//
// Because every realm appears at most once, the node correspondence between two models is
// fixed by the realm codes, so comparing token sets is a complete structural comparison (no
// graph matching is needed). Similarity = weighted Jaccard overlap of the token sets; groups
// come from average-linkage hierarchical clustering (UPGMA) on 1 - similarity.

import { parse, sortCodes, realmLabel } from "../../../../Model_viewer/assets/model-page/js/crs.js";

export const KINDS = {
  realm:  "Realms present",
  role:   "How each realm is run",
  embed:  "Embedding",
  couple: "Couplings",
  ctx:    "Neighbourhood of each realm",
};
export const DEFAULT_WEIGHTS = { realm: 1, role: 1, embed: 1, couple: 1, ctx: 1 };

/** The CRS as a graph: { nodes, role: {code: role}, parent: {code: host}, embeds: [[P, C]], couples: [[a, b]] } */
export function crsGraph(crs) {
  const { embeddings, couplingPairs, roots, prescribed } = parse(crs || "");
  const nodes = sortCodes([...new Set([...roots, ...embeddings.flat()])]);
  const parent = Object.fromEntries(embeddings.map(([p, c]) => [c, p]));
  const pre = new Set(prescribed);
  const role = Object.fromEntries(nodes.map(c => [c, pre.has(c) ? "prescribed" : parent[c] ? "embedded" : "dynamic"]));
  return { nodes, role, parent, embeds: embeddings, couples: couplingPairs };
}

/** Tokens for one CRS: Map(token -> kind). */
export function tokenize(crs) {
  const g = crsGraph(crs);
  const T = new Map();
  for (const c of g.nodes) {
    T.set(`realm:${c}`, "realm");
    T.set(`role:${c}=${g.role[c]}`, "role");
  }
  for (const [p, c] of g.embeds) T.set(`embed:${p}>${c}`, "embed");
  for (const [a, b] of g.couples) T.set(`couple:${a}~${b}`, "couple");
  for (const c of g.nodes) {
    const kids = sortCodes(g.embeds.filter(([p]) => p === c).map(([, k]) => k));
    const nb = sortCodes([...new Set(g.couples.filter(pr => pr.includes(c)).map(([a, b]) => (a === c ? b : a)))]);
    T.set(`ctx:${c}=${g.role[c]}|in:${g.parent[c] || "-"}|holds:${kids.join(",") || "-"}|couples:${nb.join(",") || "-"}`, "ctx");
  }
  return T;
}

/** Weighted Jaccard overlap of two token maps (1 = identical structure, 0 = nothing in common). */
export function similarity(a, b, weights = DEFAULT_WEIGHTS) {
  let inter = 0, union = 0;
  for (const [t, kind] of a) {
    const w = weights[kind] ?? 1;
    union += w;
    if (b.has(t)) inter += w;
  }
  for (const [t, kind] of b) if (!a.has(t)) union += weights[kind] ?? 1;
  return union > 0 ? inter / union : 1;
}

/** n x n similarity matrix for a list of token maps. */
export function similarityMatrix(tokenMaps, weights = DEFAULT_WEIGHTS) {
  const n = tokenMaps.length;
  const S = Array.from({ length: n }, () => new Array(n).fill(1));
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) S[i][j] = S[j][i] = similarity(tokenMaps[i], tokenMaps[j], weights);
  return S;
}

/** Average-linkage (UPGMA) hierarchical clustering on a distance matrix D.
 *  Returns the root of a binary tree. A leaf is { leaves: [i], height: 0 }; a merge is
 *  { left, right, leaves, height } with height = the average distance at which it merged.
 *  `root.leaves` is a valid left-to-right dendrogram order. n is small (tens), so the plain
 *  O(n^3)-ish search is fine. */
export function upgma(D) {
  let active = D.map((_, i) => ({ leaves: [i], height: 0 }));
  const avg = (a, b) => {
    let s = 0;
    for (const i of a.leaves) for (const j of b.leaves) s += D[i][j];
    return s / (a.leaves.length * b.leaves.length);
  };
  while (active.length > 1) {
    let best = Infinity, bi = 0, bj = 1;
    for (let i = 0; i < active.length; i++) {
      for (let j = i + 1; j < active.length; j++) {
        const d = avg(active[i], active[j]);
        if (d < best - 1e-12) { best = d; bi = i; bj = j; }
      }
    }
    const a = active[bi], b = active[bj];
    const merged = { left: a, right: b, leaves: [...a.leaves, ...b.leaves], height: best };
    active = active.filter((_, k) => k !== bi && k !== bj);
    active.push(merged);
  }
  return active[0];
}

/** Flat groups: every cluster whose merge height is within maxDistance (as scipy's
 *  fcluster(criterion="distance")). Returns arrays of leaf indices. */
export function cut(node, maxDistance) {
  if (!node.left || node.height <= maxDistance + 1e-12) return [node.leaves];
  return [...cut(node.left, maxDistance), ...cut(node.right, maxDistance)];
}

const KIND_ORDER = Object.keys(KINDS);
/** Tokens sorted for display: by kind (realm, role, embed, couple, ctx), then alphabetically. */
export function sortTokens(tokens, kindOf) {
  return [...tokens].sort((x, y) => (KIND_ORDER.indexOf(kindOf(x)) - KIND_ORDER.indexOf(kindOf(y))) || x.localeCompare(y));
}
export const kindOfToken = t => t.slice(0, t.indexOf(":"));

/** A token in plain words, e.g. "embed:A>L" -> "Land surface inside Atmosphere". */
export function describe(token) {
  const kind = kindOfToken(token), rest = token.slice(kind.length + 1);
  const L = code => realmLabel(code);
  if (kind === "realm") return `has ${L(rest)}`;
  if (kind === "role") { const [c, r] = rest.split("="); return `${L(c)} ${r === "dynamic" ? "interactive" : r}`; }
  if (kind === "embed") { const [p, c] = rest.split(">"); return `${L(c)} inside ${L(p)}`; }
  if (kind === "couple") { const [a, b] = rest.split("~"); return `${L(a)} ↔ ${L(b)}`; }
  if (kind === "ctx") {
    const [head, ...parts] = rest.split("|");
    const [c, role] = head.split("=");
    const f = Object.fromEntries(parts.map(p => p.split(":")));
    const list = v => v.split(",").map(L).join(", ");
    const bits = [role === "dynamic" ? "interactive" : role];
    if (f.in && f.in !== "-") bits.push(`in ${L(f.in)}`);
    if (f.holds && f.holds !== "-") bits.push(`holds ${list(f.holds)}`);
    bits.push(f.couples && f.couples !== "-" ? `couples to ${list(f.couples)}` : "no couplings");
    return `${L(c)}: ${bits.join(", ")}`;
  }
  return token;
}

/** The structure every model in a group has in common, in the shape the CRS diagram takes:
 *  { embeddings, couplingPairs, roots, prescribed, varies }.
 *  A realm present in every model but run differently (its role differs, or it is embedded in
 *  every model but not always in the same host) is listed in `varies` and drawn as such. */
export function sharedStructure(tokenMaps) {
  let shared = new Set(tokenMaps[0].keys());
  for (const T of tokenMaps.slice(1)) shared = new Set([...shared].filter(t => T.has(t)));
  const realms = [...shared].filter(t => t.startsWith("realm:")).map(t => t.slice(6));
  const roleOf = {};
  for (const t of shared) if (t.startsWith("role:")) { const [c, r] = t.slice(5).split("="); roleOf[c] = r; }
  const embeddings = [...shared].filter(t => t.startsWith("embed:")).map(t => t.slice(6).split(">"));
  const couplingPairs = [...shared].filter(t => t.startsWith("couple:")).map(t => t.slice(7).split("~"));
  const embedded = new Set(embeddings.map(([, c]) => c));
  const roots = sortCodes(realms.filter(c => !embedded.has(c)));
  const prescribed = sortCodes(realms.filter(c => roleOf[c] === "prescribed"));
  const varies = sortCodes(realms.filter(c => !roleOf[c] || (roleOf[c] === "embedded" && !embedded.has(c))));
  return { embeddings, couplingPairs, roots, prescribed, varies };
}

/** What model T has that `other` does not, for the comparison's individual diagrams:
 *  realms the other model lacks or runs or places differently (another role, or another host), and
 *  couplings the other model lacks. The realms those attach to (a host, or the other end of a
 *  coupling) are kept as well, since a difference cannot be drawn without them. Returns the shape
 *  the CRS diagram takes plus `count`, the number of differences (0 = nothing the other lacks). */
export function differenceStructure(T, other) {
  const hostOf = M => Object.fromEntries([...M.keys()].filter(t => t.startsWith("embed:")).map(t => t.slice(6).split(">").reverse()));
  const roleOf = M => Object.fromEntries([...M.keys()].filter(t => t.startsWith("role:")).map(t => t.slice(5).split("=")));
  const hT = hostOf(T), hO = hostOf(other), rT = roleOf(T), rO = roleOf(other);
  const differentRealms = Object.keys(rT).filter(c => rO[c] !== rT[c] || (hT[c] || "-") !== (hO[c] || "-"));
  const couplingPairs = [...T.keys()].filter(t => t.startsWith("couple:") && !other.has(t)).map(t => t.slice(7).split("~"));
  const keep = new Set(differentRealms);
  for (const [a, b] of couplingPairs) { keep.add(a); keep.add(b); }             // both ends of a coupling
  for (const c of [...keep]) for (let h = hT[c]; h; h = hT[h]) keep.add(h);      // and every host above a realm
  const realms = sortCodes([...keep]);
  const embeddings = realms.filter(c => hT[c]).map(c => [hT[c], c]);
  const roots = realms.filter(c => !hT[c]);
  const prescribed = roots.filter(c => rT[c] === "prescribed");
  return { embeddings, couplingPairs, roots, prescribed, count: differentRealms.length + couplingPairs.length };
}
