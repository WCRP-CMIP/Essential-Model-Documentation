// components/references.js — hyperlinked reference list (DOIs + citations).
import { el, refNode } from "../dom.js";

export function mountReferences(root, model) {
  const refs = (model.references || []).map(r => String(r).trim()).filter(Boolean);
  if (!refs.length) return;

  root.appendChild(el("section", { class: "card references" }, [
    el("h2", { class: "card-title" }, refs.length === 1 ? "Reference" : "References"),
    el("ol", { class: "ref-list" }, refs.map(r => el("li", {}, refNode(r)))),
  ]));
}
