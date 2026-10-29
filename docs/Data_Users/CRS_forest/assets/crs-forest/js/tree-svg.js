// tree-svg.js — the summary decision tree as a standalone SVG, for the Download SVG button.
// Same layout as on the page (left to right: question -> "yes" / "no" -> ... -> end groups), drawn
// with explicit colours in a fixed light palette, so the file looks the same in any viewer.

const NS = "http://www.w3.org/2000/svg";
const C = { ink: "#14223a", muted: "#5d6b82", line: "#c9d1de", box: "#f7f5ef", leaf: "#ffffff", accent: "#1f4e79", yes: "#2196f3" };
const FONT = "Helvetica, Arial, sans-serif";
const QW = 230, LW = 210, HGAP = 70, VGAP = 12, PAD = 8, LINE = 14;

const el = (tag, attrs = {}, text) => {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, String(v));
  if (text != null) n.textContent = text;
  return n;
};
function wrap(text, max = 32) {
  const lines = []; let cur = "";
  for (const w of text.split(" ")) { if (cur && (cur + " " + w).length > max) { lines.push(cur); cur = w; } else cur = cur ? `${cur} ${w}` : w; }
  if (cur) lines.push(cur);
  return lines;
}

// A question's chips: realm short names in realm-coloured outlines, with ⊂ / ↔ or the role word.
function chips(g, token, x, y, { realmColor, shortRealm }) {
  const kind = token.slice(0, token.indexOf(":")), rest = token.slice(kind.length + 1);
  let parts;
  if (kind === "embed") { const [p, c] = rest.split(">"); parts = [{ r: c }, { t: "⊂" }, { r: p }]; }
  else if (kind === "couple") { const [a, b] = rest.split("~"); parts = [{ r: a }, { t: "↔" }, { r: b }]; }
  else if (kind === "role") { const [c, role] = rest.split("="); parts = [{ r: c }, { t: role === "dynamic" ? "interactive" : role }]; }
  else parts = [{ r: rest }];
  let cx = x;
  for (const p of parts) {
    if (p.r) {
      const label = shortRealm(p.r), w = label.length * 6.4 + 10;
      g.append(el("rect", { x: cx, y, width: w, height: 16, rx: 2, fill: "none", stroke: realmColor(p.r), "stroke-width": 1.4 }));
      g.append(el("text", { x: cx + w / 2, y: y + 11.5, "text-anchor": "middle", "font-size": 10, "font-weight": 700, fill: C.ink }, label));
      cx += w + 4;
    } else {
      g.append(el("text", { x: cx, y: y + 11.5, "font-size": 10, fill: C.muted }, p.t));
      cx += p.t.length * 5.6 + 6;
    }
  }
}

/** Build the SVG for a tree from forest.js likenessTree().
 *  helpers: { question(f) -> { token, label }, modelName(i), realmColor, shortRealm } */
export function buildTreeSvg(root, helpers) {
  const { question, modelName } = helpers;
  const isLeaf = node => node.f === undefined;
  const qLines = node => wrap(`${question(node.f).label}?`);
  const boxH = node => (isLeaf(node) ? 22 + node.models.length * LINE + PAD : 28 + qLines(node).length * LINE + 16 + PAD);
  const subH = node => (isLeaf(node) ? boxH(node) + VGAP : Math.max(boxH(node) + VGAP, subH(node.yes) + subH(node.no)));

  // Lay out: each node's children are stacked (yes above no); the node sits midway between them.
  const boxes = [], edges = [];
  let maxX = 0;
  const place = (node, depth, top) => {
    const x = PAD + depth * (QW + HGAP);
    let cy;
    if (isLeaf(node)) cy = top + boxH(node) / 2;
    else {
      const hy = subH(node.yes), hn = subH(node.no), off = (Math.max(boxH(node) + VGAP, hy + hn) - (hy + hn)) / 2;
      const yesY = place(node.yes, depth + 1, top + off), noY = place(node.no, depth + 1, top + off + hy);
      cy = (yesY + noY) / 2;
      edges.push({ x1: x + QW, y: cy, x2: x + QW + HGAP, yesY, noY });
    }
    const w = isLeaf(node) ? LW : QW;
    boxes.push({ node, x, y: cy - boxH(node) / 2, w, h: boxH(node) });
    maxX = Math.max(maxX, x + w);
    return cy;
  };
  place(root, 0, PAD);
  const W = maxX + PAD, H = subH(root) + 2 * PAD;
  const svg = el("svg", { xmlns: NS, viewBox: `0 0 ${W} ${H}`, width: W, height: H, "font-family": FONT });

  for (const e of edges) {                                  // connectors first, boxes on top
    const xm = e.x1 + HGAP * 0.35;
    svg.append(el("path", { d: `M${e.x1},${e.y} H${xm} M${xm},${e.yesY} V${e.noY} M${xm},${e.yesY} H${e.x2} M${xm},${e.noY} H${e.x2}`, fill: "none", stroke: C.muted, "stroke-width": 1.4 }));
    svg.append(el("text", { x: xm + 6, y: e.yesY - 4, "font-size": 9.5, "font-weight": 700, fill: C.yes }, "YES"));
    svg.append(el("text", { x: xm + 6, y: e.noY - 4, "font-size": 9.5, "font-weight": 700, fill: C.muted }, "NO"));
  }
  for (const b of boxes) {
    const g = el("g", {});
    const n = b.node.models.length;
    if (isLeaf(b.node)) {
      g.append(el("rect", { x: b.x, y: b.y, width: b.w, height: b.h, rx: 4, fill: C.leaf, stroke: C.accent, "stroke-width": 1.5 }));
      g.append(el("text", { x: b.x + 8, y: b.y + 15, "font-size": 10, fill: C.muted }, `${n} model${n > 1 ? "s" : ""}${n > 1 ? ` · ${Math.round(b.node.likeness * 100)}% alike` : ""}`));
      b.node.models.forEach((i, k) => g.append(el("text", { x: b.x + 8, y: b.y + 30 + k * LINE, "font-size": 11, "font-weight": 600, fill: C.accent }, modelName(i))));
    } else {
      const q = question(b.node.f);
      g.append(el("rect", { x: b.x, y: b.y, width: b.w, height: b.h, rx: 4, fill: C.box, stroke: C.line, "stroke-width": 1.5 }));
      chips(g, q.token, b.x + 8, b.y + 7, helpers);
      qLines(b.node).forEach((line, k) => g.append(el("text", { x: b.x + 8, y: b.y + 38 + k * LINE, "font-size": 11, "font-weight": 600, fill: C.ink }, line)));
      g.append(el("text", { x: b.x + 8, y: b.y + 38 + qLines(b.node).length * LINE + 4, "font-size": 9.5, fill: C.muted }, `${n} models`));
    }
    svg.append(g);
  }
  return svg;
}
