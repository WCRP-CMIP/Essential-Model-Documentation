// components/raw-json.js — expandable, copyable, colourised model JSON.
//
// Two views, toggled by a segmented control:
//   • Simple   — the raw model record exactly as stored.
//   • Resolved — the same record with every @id reference inlined to the full
//                linked record (model_components → each config → its
//                model_component + grids → subgrids → cells, family, …).
// The visible text is syntax-highlighted and copyable.

import { el } from "../dom.js";
import { Resolver, FOLDER, short } from "../resolver.js";

// ---- syntax highlight -----------------------------------------------------
function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function highlight(jsonText) {
  return escapeHtml(jsonText).replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
    m => {
      let cls = "j-num";
      if (/^"/.test(m)) cls = /:$/.test(m) ? "j-key" : "j-str";
      else if (/^(true|false)$/.test(m)) cls = "j-bool";
      else if (m === "null") cls = "j-null";
      return `<span class="${cls}">${m}</span>`;
    }
  );
}

// ---- deep-resolve @id references -----------------------------------------
async function resolveDeep(resolver, node, key, depth, seen) {
  if (Array.isArray(node)) {
    return Promise.all(node.map(v => resolveDeep(resolver, v, key, depth, seen)));
  }
  if (node && typeof node === "object") {
    const out = {};
    for (const [k, v] of Object.entries(node)) out[k] = await resolveDeep(resolver, v, k, depth, seen);
    return out;
  }
  if (typeof node === "string" && depth > 0 && FOLDER[key]) {
    const folder = FOLDER[key];
    const id = short(node);
    const cacheKey = `${folder}/${id}`;
    if (seen.has(cacheKey)) return node;      // cycle / already inlined higher up
    try {
      const doc = await resolver.fetchDoc(folder, id);
      const nextSeen = new Set(seen); nextSeen.add(cacheKey);
      return await resolveDeep(resolver, doc, null, depth - 1, nextSeen);
    } catch (_) { return node; }              // leave the bare id if it won't resolve
  }
  return node;
}

export function mountRawJson(root, model, { base } = {}) {
  const resolver = base ? new Resolver(base) : null;
  const simpleText = JSON.stringify(model, null, 2);
  let resolvedText = null;               // built lazily on first switch
  let mode = "simple";

  // --- controls
  const seg = el("div", { class: "json-seg" });
  const btnSimple = el("button", { type: "button", class: "seg-btn active" }, "Simple");
  const btnResolved = el("button", { type: "button", class: "seg-btn" }, "Resolved");
  seg.append(btnSimple, btnResolved);

  const copyBtn = el("button", { class: "json-copy", type: "button" }, "Copy");
<<<<<<< HEAD

  const summary = el("summary", { class: "json-summary" }, [
    el("span", { class: "json-summary-label" }, "Model record (JSON)"),
    el("span", { class: "json-controls" }, [seg, copyBtn]),
=======
  const wrapBtn = el("button", { class: "json-wrap-btn active", type: "button", title: "Toggle line wrapping" }, "Wrap");

  const summary = el("summary", { class: "json-summary" }, [
    el("span", { class: "json-summary-label" }, "Model record (JSON)"),
    el("span", { class: "json-controls" }, [seg, wrapBtn, copyBtn]),
>>>>>>> 183310cba7594af95d231d50e4a90f156e1095e8
  ]);

  const code = el("code");
  code.innerHTML = highlight(simpleText);
<<<<<<< HEAD
  const pre = el("pre", { class: "json-pre" }, code);
=======
  const pre = el("pre", { class: "json-pre wrap" }, code);   // wrap on by default
>>>>>>> 183310cba7594af95d231d50e4a90f156e1095e8

  const currentText = () => (mode === "resolved" ? (resolvedText ?? "") : simpleText);

  function render(text) { code.innerHTML = highlight(text); }

  async function setMode(next) {
    if (next === mode) return;
    mode = next;
    btnSimple.classList.toggle("active", mode === "simple");
    btnResolved.classList.toggle("active", mode === "resolved");
    if (mode === "simple") { render(simpleText); return; }
    // resolved
    if (resolvedText != null) { render(resolvedText); return; }
    if (!resolver) { render('// resolved view unavailable (no base configured)'); return; }
    code.textContent = "// resolving linked records…";
    try {
      const resolved = await resolveDeep(resolver, model, null, 6, new Set());
      resolvedText = JSON.stringify(resolved, null, 2);
      if (mode === "resolved") render(resolvedText);
    } catch (e) {
      code.textContent = `// could not resolve: ${e.message}`;
    }
  }

  btnSimple.addEventListener("click", e => { e.preventDefault(); e.stopPropagation(); setMode("simple"); });
  btnResolved.addEventListener("click", e => { e.preventDefault(); e.stopPropagation(); setMode("resolved"); });

<<<<<<< HEAD
=======
  // line-wrap toggle (off by default → long lines scroll horizontally)
  wrapBtn.addEventListener("click", e => {
    e.preventDefault(); e.stopPropagation();
    const on = pre.classList.toggle("wrap");
    wrapBtn.classList.toggle("active", on);
  });

>>>>>>> 183310cba7594af95d231d50e4a90f156e1095e8
  copyBtn.addEventListener("click", async e => {
    e.preventDefault(); e.stopPropagation();
    const text = currentText();
    try {
      if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(text);
      else {
        const ta = el("textarea", { class: "json-copy-fallback" }); ta.value = text;
        document.body.appendChild(ta); ta.select(); document.execCommand("copy"); ta.remove();
      }
      copyBtn.textContent = "Copied ✓"; copyBtn.classList.add("ok");
      setTimeout(() => { copyBtn.textContent = "Copy"; copyBtn.classList.remove("ok"); }, 1600);
    } catch (_) {
      copyBtn.textContent = "Copy failed";
      setTimeout(() => { copyBtn.textContent = "Copy"; }, 1600);
    }
  });

  root.appendChild(el("details", { class: "card raw-json" }, [summary, pre]));
}
