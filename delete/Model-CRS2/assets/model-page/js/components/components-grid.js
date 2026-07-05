// components/components-grid.js — realm/component cards.
//
// One card per realm. Dynamic realms are full-colour; prescribed are muted +
// dashed with a "prescribed" tag; omitted are ghosted. Embedded children are
// nested inside their parent card. Each card links to its component_config
// record on the EMD site, and lists the realms it is coupled to.

import { el } from "../dom.js";
import { parse, toCode, realmLabel, realmColor } from "../crs.js";

const REALM_OF = id => String(id).split("_")[0];      // "atmosphere_arpege…" -> "atmosphere"

export function mountComponents(root, model, { base }) {
  const dynamic    = new Set(model.dynamic_components || []);
  const prescribed = new Set(model.prescribed_components || []);
  const omitted    = new Set(model.omitted_components || []);

  // realm -> component_config id (from model_components)
  const compFor = new Map();
  for (const cc of (model.model_components || model.component_configs || [])) {
    compFor.set(REALM_OF(cc), cc);
  }

  // child realm -> parent realm (embedded_components is [child, parent])
  const parentOf = new Map();
  for (const p of (model.embedded_components || [])) {
    if (Array.isArray(p) && p.length === 2) parentOf.set(p[0], p[1]);
  }

  // realm -> [coupled realms]
  const coupledWith = new Map();
  const addCouple = (a, b) => {
    if (!coupledWith.has(a)) coupledWith.set(a, new Set());
    coupledWith.get(a).add(b);
  };
  for (const pair of (model.coupled_components || [])) {
    if (Array.isArray(pair) && pair.length === 2) { addCouple(pair[0], pair[1]); addCouple(pair[1], pair[0]); }
  }

  // Determine the set of realms to show and their state.
  const stateOf = realm =>
    prescribed.has(realm) ? "prescribed" :
    omitted.has(realm)    ? "omitted" :
    dynamic.has(realm)    ? "dynamic" : "dynamic";

  const allRealms = new Set([
    ...dynamic, ...prescribed, ...omitted, ...parentOf.keys(), ...parentOf.values(),
  ]);
  // Top-level realms = those not embedded in another.
  const topRealms = [...allRealms].filter(r => !parentOf.has(r));
  // children grouped by parent
  const childrenOf = new Map();
  for (const [child, parent] of parentOf) {
    if (!childrenOf.has(parent)) childrenOf.set(parent, []);
    childrenOf.get(parent).push(child);
  }

  const orderKey = r => toCode(r);   // canonical-ish ordering by code
  topRealms.sort((a, b) => orderKey(a).localeCompare(orderKey(b)));

  function realmCard(realm, nested = false) {
    const state = stateOf(realm);
    const cc = compFor.get(realm);
    const color = realmColor(realm);
    const couples = [...(coupledWith.get(realm) || [])].sort();
    const kids = (childrenOf.get(realm) || []).slice().sort((a, b) => orderKey(a).localeCompare(orderKey(b)));

    const componentName = cc ? cc.split("_").slice(1, -2).join("_") || cc.split("_")[1] : null;

    return el("div", {
      class: `realm-card state-${state}${nested ? " nested" : ""}`,
      style: `--realm: ${color}`,
    }, [
      el("div", { class: "realm-head" }, [
        el("span", { class: "realm-dot" }),
        el("span", { class: "realm-name" }, realmLabel(realm)),
        state !== "dynamic" && el("span", { class: `tag tag-${state}` }, state),
      ]),
      componentName && el("div", { class: "realm-component" }, componentName),
      cc && el("a", {
        class: "realm-link",
        href: `${base}component_config/${cc}.json`,
        target: "_blank", rel: "noopener",
      }, "component config ↗"),
      couples.length && el("div", { class: "realm-couples" }, [
        el("span", { class: "couples-key" }, "couples with"),
        ...couples.map(c => el("span", { class: "couple-chip" }, realmLabel(c))),
      ]),
      kids.length && el("div", { class: "realm-children" },
        kids.map(k => realmCard(k, true))),
    ]);
  }

  const grid = el("div", { class: "realm-grid" }, topRealms.map(r => realmCard(r)));

  root.appendChild(el("section", { class: "card components" }, [
    el("h2", { class: "card-title" }, "Realms & components"),
    el("p", { class: "card-sub" },
      "Dynamic realms are prognostic and interactive. Prescribed realms are imposed " +
      "from external data (not interactively coupled). Omitted realms are absent from " +
      "this configuration. Embedded realms are nested inside their host."),
    grid,
  ]));
}
