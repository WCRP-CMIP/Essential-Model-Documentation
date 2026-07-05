// components/linked-info.js — resolves and renders the linked records:
//   model  → model_family                          (the model's own family)
//   model  → model_components (component_config)
//            → model_component  (the code that implements the realm)
//                → model_family (family_type: "component")
//
// Exports two mount functions so the orchestrator can place the schema diagram
// between them:
//   mountModelFamily      — "Model family" card
//   mountComponentsDetail — "Components in detail" card (one row per realm)

import { el, card, refNode } from "../dom.js";
import { Resolver, short } from "../resolver.js";
import { realmLabel, realmColor, toCode } from "../crs.js";

const clean = v => (v == null ? "" : String(v).trim());
const isNone = v => { const s = clean(v).toLowerCase(); return !s || s === "none" || s === "not specified"; };
const orgLabel = id => short(id).replace(/-/g, " ").toUpperCase();

const REALM_OF = id => String(id).split("_")[0];

// Truncated description that expands on click.
const TRUNCATE = 220;
function truncatedDesc(text) {
  const full = clean(text);
  if (!full) return null;
  if (full.length <= TRUNCATE) return el("p", { class: "comp-desc" }, full);
  const p = el("p", { class: "comp-desc clamped" });
  const short = full.slice(0, TRUNCATE).replace(/\s+\S*$/, "") + "…";
  const textNode = document.createTextNode(short);
  const toggle = el("button", { class: "desc-toggle", type: "button" }, "more");
  let expanded = false;
  toggle.addEventListener("click", e => {
    e.preventDefault(); e.stopPropagation();
    expanded = !expanded;
    textNode.textContent = expanded ? full + " " : short;
    toggle.textContent = expanded ? "less" : "more";
    p.classList.toggle("clamped", !expanded);
  });
  p.appendChild(textNode); p.appendChild(toggle);
  return p;
}

function familyCard(fam) {
  if (!fam) return null;
  const rows = [];
  const add = (k, v) => { if (!isNone(v)) rows.push([k, v]); };

  add("Type", fam.family_type);
  if (!isNone(fam.primary_institution)) rows.push(["Primary institution", orgLabel(fam.primary_institution)]);
  const collab = (fam.collaborative_institutions || []).filter(x => !isNone(x));
  if (collab.length) rows.push(["Collaborators", collab.map(orgLabel).join(", ")]);
  const domains = (fam.scientific_domains || []).filter(x => !isNone(x));
  if (domains.length) rows.push(["Scientific domains", domains.map(realmLabel).join(", ")]);
  add("Established", fam.established);
  add("Programming languages", fam.programming_languages);
  add("License", fam.license);

  const links = [];
  if (!isNone(fam.website)) links.push(el("a", { href: fam.website, target: "_blank", rel: "noopener", class: "ref-link" }, "website ↗"));
  if (!isNone(fam.source_code_repository)) links.push(el("a", { href: fam.source_code_repository, target: "_blank", rel: "noopener", class: "ref-link" }, "source ↗"));
  const refs = (fam.references || []).filter(x => !isNone(x));

  const body = [
    el("div", { class: "family-head" }, [
      el("span", { class: "family-name" }, fam.ui_label || fam.validation_key || short(fam["@id"])),
      links.length ? el("span", { class: "family-links" }, links) : null,
    ]),
    !isNone(fam.description) ? el("p", { class: "family-desc" }, fam.description) : null,
    rows.length ? el("dl", { class: "kv" }, rows.flatMap(([k, v]) => [
      el("dt", {}, k), el("dd", {}, v),
    ])) : null,
    refs.length ? el("div", { class: "family-refs" }, [
      el("span", { class: "kv-key" }, "references"),
      el("ul", { class: "ref-list inline" }, refs.map(r => el("li", {}, refNode(r)))),
    ]) : null,
  ];

  return card("Model family", body, { extraClass: "family-card" });
}

function componentRow(realm, comp, compFamily, base, ccId) {
  const color = realmColor(realm);
  const refs = (comp?.references || []).filter(x => !isNone(x))
    .flatMap(r => String(r).split(/\s+/).filter(s => /^https?:\/\//.test(s)));  // some refs pack many URLs in one string

  const codeBaseNode = comp && !isNone(comp.code_base)
    ? (/^https?:\/\//.test(comp.code_base)
        ? el("a", { href: comp.code_base, target: "_blank", rel: "noopener", class: "ref-link" }, "code base ↗")
        : el("span", { class: "muted-pill" }, comp.code_base))   // e.g. "private"
    : null;

  return el("div", { class: "comp-row", style: `--realm:${color}` }, [
    el("div", { class: "comp-row-head" }, [
      el("span", { class: "realm-dot" }),
      el("span", { class: "comp-realm" }, realmLabel(realm)),
      comp ? el("span", { class: "comp-name" }, comp.name || comp.ui_label || short(comp["@id"])) : null,
    ]),
    comp ? truncatedDesc(comp.description) : null,
    el("div", { class: "comp-meta" }, [
      compFamily ? el("span", { class: "comp-tag" }, [
        el("span", { class: "kv-key" }, "family"),
        !isNone(compFamily.website)
          ? el("a", { href: compFamily.website, target: "_blank", rel: "noopener", class: "ref-link" },
              compFamily.ui_label || compFamily.validation_key || short(compFamily["@id"]))
          : (compFamily.ui_label || compFamily.validation_key || short(compFamily["@id"])),
        !isNone(compFamily.primary_institution) ? el("span", { class: "muted" }, ` · ${orgLabel(compFamily.primary_institution)}`) : null,
      ]) : null,
      codeBaseNode ? el("span", { class: "comp-tag" }, codeBaseNode) : null,
      el("a", { class: "comp-tag ref-link", href: `${base}component_config/${ccId}.json`, target: "_blank", rel: "noopener" }, "config ↗"),
    ]),
    refs.length ? el("div", { class: "comp-refs" }, [
      el("span", { class: "kv-key" }, "refs"),
      ...refs.map(r => refNode(r)),
    ]) : null,
  ]);
}

export async function mountModelFamily(root, model, { base }) {
  const resolver = new Resolver(base);
  if (!(model.family && !isNone(model.family))) return;
  try {
    const fam = await resolver.fetchDoc("model_family", short(model.family));
    const c = familyCard(fam);
    if (c) root.appendChild(c);
  } catch (_) { /* family record missing — skip */ }
}

export async function mountComponentsDetail(root, model, { base }) {
  const resolver = new Resolver(base);
  const configs = model.model_components || model.component_configs || [];
  if (!configs.length) return;

  const list = el("div", { class: "comp-list" });
  const section = card("Components in detail", [list], {
    sub: "The code implementing each realm, its provenance, and the component family it belongs to.",
    extraClass: "components-detail",
  });
  root.appendChild(section);

  // Resolve each config → model_component → component family, in parallel.
  await Promise.all(configs.map(async ccId => {
    const realm = REALM_OF(ccId);
    let comp = null, compFamily = null;
    try {
      const cc = await resolver.fetchDoc("component_config", ccId);
      const compId = short(cc.model_component);
      if (compId) {
        comp = await resolver.fetchDoc("model_component", compId);
        if (comp && comp.family && !isNone(comp.family)) {
          try { compFamily = await resolver.fetchDoc("model_family", short(comp.family)); }
          catch (_) {}
        }
      }
    } catch (_) { /* leave comp null — still render the realm row */ }
    list.appendChild(componentRow(realm, comp, compFamily, base, ccId));
  }));

  // Keep rows in canonical realm order.
  [...list.children]
    .sort((a, b) => (a.querySelector(".comp-realm")?.textContent || "")
      .localeCompare(b.querySelector(".comp-realm")?.textContent || ""))
    .forEach(n => list.appendChild(n));
}
