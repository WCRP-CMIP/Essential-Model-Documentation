// dom.js — tiny hyperscript helper + shared UI atoms for the grid-cells page.
//
//   el("div", {class:"card"}, [ el("h2", {}, "Title"), "text" ])
//   el("a", {href:url, target:"_blank"}, "link")

export function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "class") node.className = v;
    else if (k === "html") node.innerHTML = v;
    else if (k === "dataset") Object.assign(node.dataset, v);
    else if (k.startsWith("on") && typeof v === "function") node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v === true ? "" : v);
  }
  const kids = Array.isArray(children) ? children : [children];
  for (const c of kids) {
    if (c == null || c === false) continue;
    node.appendChild(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return node;
}

export const clear = node => { while (node.firstChild) node.removeChild(node.firstChild); };

// A non-collapsible content card matching the model page's .card styling.
export function card(title, body, { sub = null, extraClass = "" } = {}) {
  return el("div", { class: `card ${extraClass}`.trim() }, [
    title ? el("h2", { class: "card-title" }, title) : null,
    sub ? el("p", { class: "card-sub" }, sub) : null,
    ...(Array.isArray(body) ? body : [body]),
  ]);
}

// --- shared singleton tooltip ---------------------------------------------
// A single floating tooltip element reused for every hover target. Attach with
// attachTooltip(node, text). Positioned on mouseenter, hidden on mouseleave.
//
// A native `title` attribute is also set as a robustness fallback: if the
// floating tooltip ever fails to show in some embedding context (mkdocs theme
// quirks, CSS conflicts, etc.), the browser's built-in tooltip still surfaces
// the description on hover.
let _tip = null;
function ensureTip() {
  if (_tip) return _tip;
  _tip = el("div", { class: "gc-tooltip", role: "tooltip" });
  document.body.appendChild(_tip);
  return _tip;
}
export function attachTooltip(node, text) {
  const msg = (text == null ? "" : String(text)).trim();
  if (!msg) return node;
  node.classList.add("has-tip");
  node.setAttribute("title", msg);          // native fallback
  const show = e => {
    const tip = ensureTip();
    tip.textContent = msg;
    tip.classList.add("visible");
    position(tip, e);
  };
  const move = e => { if (_tip && _tip.classList.contains("visible")) position(_tip, e); };
  const hide = () => { if (_tip) _tip.classList.remove("visible"); };
  node.addEventListener("mouseenter", show);
  node.addEventListener("mousemove", move);
  node.addEventListener("mouseleave", hide);
  node.addEventListener("focus", show);
  node.addEventListener("blur", hide);
  return node;
}
function position(tip, e) {
  const pad = 14, tw = tip.offsetWidth, th = tip.offsetHeight;
  let x = e.clientX + pad, y = e.clientY + pad;
  if (x + tw > window.innerWidth - 8) x = e.clientX - tw - pad;
  if (y + th > window.innerHeight - 8) y = e.clientY - th - pad;
  tip.style.left = Math.max(8, x) + "px";
  tip.style.top = Math.max(8, y) + "px";
}
