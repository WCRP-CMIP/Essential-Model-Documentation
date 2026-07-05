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

// --- minimal Markdown → HTML (inline emphasis, code, links, paragraphs) ----
// Descriptions in the EMD records are free text that may contain light
// markdown; parse it before inserting as HTML rather than dumping raw text.
export function mdToHtml(src) {
  const s = String(src == null ? "" : src).trim();
  if (!s) return "";
  const esc = t => t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const inline = t => {
    let x = esc(t);
    // links [text](url) — do first so URL punctuation isn't touched by emphasis
    x = x.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener">$1</a>');
    // inline code
    x = x.replace(/`([^`]+)`/g, (_, c) => `<code>${c}</code>`);
    // bold then italic
    x = x.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    x = x.replace(/__([^_]+)__/g, "<strong>$1</strong>");
    x = x.replace(/(^|[^*])\*([^*\s][^*]*?)\*(?!\*)/g, "$1<em>$2</em>");
    return x;
  };
  return s.split(/\n{2,}/).map(p => `<p>${inline(p).replace(/\n/g, "<br>")}</p>`).join("");
}

// A description clamped to `lines` lines with a more/less toggle. Renders md.
// The toggle hides itself if the content doesn't actually overflow.
export function clampedMd(text, { lines = 2, cls = "" } = {}) {
  const html = mdToHtml(text);
  if (!html) return null;
  const body = el("div", { class: `clamp ${cls}`.trim(), html });
  body.style.setProperty("--clamp-lines", String(lines));
  const toggle = el("button", { class: "clamp-toggle", type: "button" }, "more");
  let expanded = false;
  toggle.addEventListener("click", e => {
    e.preventDefault(); e.stopPropagation();
    expanded = !expanded;
    body.classList.toggle("expanded", expanded);
    toggle.textContent = expanded ? "less" : "more";
  });
  const wrap = el("div", { class: "clamp-wrap" }, [body, toggle]);
  // Hide the toggle when the text fits within the clamp (measured post-layout).
  requestAnimationFrame(() => {
    if (body.scrollHeight - body.clientHeight < 2) toggle.style.display = "none";
  });
  return wrap;
}

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
