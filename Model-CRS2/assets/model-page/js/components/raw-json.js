// components/raw-json.js — expandable, copyable raw JSON of the model record.
//
// Renders the model's source JSON-LD at the bottom of the page inside a
// <details> so it stays out of the way, with a "Copy" button that writes the
// pretty-printed text to the clipboard.

import { el } from "../dom.js";

export function mountRawJson(root, model, { title = "Model record (JSON)" } = {}) {
  const text = JSON.stringify(model, null, 2);

  const copyBtn = el("button", { class: "json-copy", type: "button" }, "Copy");
  copyBtn.addEventListener("click", async e => {
    e.preventDefault();               // don't toggle the <details>
    e.stopPropagation();
    try {
      if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(text);
      else {                          // fallback for non-secure contexts (http://localhost is fine, but just in case)
        const ta = el("textarea", { class: "json-copy-fallback" }); ta.value = text;
        document.body.appendChild(ta); ta.select(); document.execCommand("copy"); ta.remove();
      }
      copyBtn.textContent = "Copied ✓";
      copyBtn.classList.add("ok");
      setTimeout(() => { copyBtn.textContent = "Copy"; copyBtn.classList.remove("ok"); }, 1600);
    } catch (_) {
      copyBtn.textContent = "Copy failed";
      setTimeout(() => { copyBtn.textContent = "Copy"; }, 1600);
    }
  });

  const summary = el("summary", { class: "json-summary" }, [
    el("span", { class: "json-summary-label" }, title),
    copyBtn,
  ]);

  const pre = el("pre", { class: "json-pre" }, el("code", {}, text));

  root.appendChild(el("details", { class: "card raw-json" }, [summary, pre]));
}
