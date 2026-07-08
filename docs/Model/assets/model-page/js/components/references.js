// components/references.js — one card per reference (DOI or free-text citation).
import { el, card } from "../dom.js";

const isUrl = s => /^https?:\/\//i.test(s);
const doiOf = s => {
  const m = String(s).match(/(10\.\d{4,9}\/[^\s]+)/);
  return m ? m[1] : null;
};

function refCard(ref, i) {
  const s = String(ref).trim();
  const doi = doiOf(s);

  const body = [];
  if (isUrl(s)) {
    if (doi) body.push(el("div", { class: "ref-doi" }, [
      el("span", { class: "ref-doi-badge" }, "DOI"),
      el("a", { href: s, target: "_blank", rel: "noopener", class: "ref-link" }, doi),
    ]));
    else body.push(el("a", { href: s, target: "_blank", rel: "noopener", class: "ref-link" },
      s.replace(/^https?:\/\/(www\.)?/i, "")));
  } else {
    // free-text citation; if it contains a bare DOI, link it
    body.push(el("p", { class: "ref-citation" }, s));
    if (doi) body.push(el("a", { href: `https://doi.org/${doi}`, target: "_blank", rel: "noopener", class: "ref-link" }, `doi:${doi}`));
  }

  return el("div", { class: "ref-card" }, [
    el("span", { class: "ref-index" }, String(i + 1)),
    el("div", { class: "ref-card-body" }, body),
  ]);
}

export function mountReferences(root, model) {
  const refs = (model.references || []).map(r => String(r).trim()).filter(Boolean);
  if (!refs.length) return;

  const grid = el("div", { class: "ref-cards" }, refs.map((r, i) => refCard(r, i)));
  root.appendChild(card(refs.length === 1 ? "Reference" : "References", [grid],
    { extraClass: "references" }));
}
