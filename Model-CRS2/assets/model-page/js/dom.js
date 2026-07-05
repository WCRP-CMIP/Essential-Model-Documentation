// dom.js — tiny hyperscript helper so components stay declarative.
//
//   el("div", {class: "card"}, [ el("h2", {}, "Title"), "text node" ])
//   el("a", {href: url, target: "_blank"}, "link")

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
    // Skip falsy/guard values. Numbers are treated as guards too, so the
    // `arr.length && el(...)` idiom can't leak a stray "0" text node.
    if (c == null || c === false || typeof c === "number") continue;
    node.appendChild(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return node;
}

export const clear = node => { while (node.firstChild) node.removeChild(node.firstChild); };

// A minimisable card: <details class="card"> with a clickable <summary> title
// and the given body node(s). `open` defaults to true. `sub` is an optional
// one-line description shown under the title when expanded.
export function card(title, body, { open = true, sub = null, extraClass = "" } = {}) {
  const summary = el("summary", { class: "card-summary" }, [
    el("span", { class: "card-summary-title" }, title),
  ]);
  const bodyWrap = el("div", { class: "card-body" }, [
    sub ? el("p", { class: "card-sub" }, sub) : null,
    ...(Array.isArray(body) ? body : [body]),
  ]);
  const d = el("details", { class: `card collapsible ${extraClass}`.trim() }, [summary, bodyWrap]);
  if (open) d.setAttribute("open", "");
  return d;
}

export const frag = (children = []) => {
  const f = document.createDocumentFragment();
  for (const c of children) if (c != null && c !== false && typeof c !== "number")
    f.appendChild(c instanceof Node ? c : document.createTextNode(String(c)));
  return f;
};

// Format a reference (DOI URL or free-text citation) into an anchor or span.
export function refNode(ref) {
  const s = String(ref).trim();
  const isUrl = /^https?:\/\//i.test(s);
  if (isUrl) {
    const label = s
      .replace(/^https?:\/\/(dx\.)?doi\.org\//i, "doi:")
      .replace(/^https?:\/\/(www\.)?/i, "");
    return el("a", { href: s, target: "_blank", rel: "noopener", class: "ref-link" }, label);
  }
  return el("span", { class: "ref-text" }, s);
}
