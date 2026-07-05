// components/overview.js — description + key-facts card.
import { el } from "../dom.js";
import { parse, realmLabel } from "../crs.js";

export function mountOverview(root, model) {
  const desc = (model.description || "").trim();

  // Derive quick counts from the CRS + component arrays.
  const dyn = (model.dynamic_components || []).length;
  const pre = (model.prescribed_components || []).length;
  const omit = (model.omitted_components || []).length;
  const comps = (model.model_components || model.component_configs || []).length;

  let coupleCount = 0;
  if (model.crs) coupleCount = parse(model.crs).couplingPairs.length;
  else if (Array.isArray(model.coupled_components)) coupleCount = model.coupled_components.length;

  const stat = (n, label) => el("div", { class: "stat" }, [
    el("div", { class: "stat-num" }, String(n)),
    el("div", { class: "stat-label" }, label),
  ]);

  const card = el("section", { class: "card overview" }, [
    el("h2", { class: "card-title" }, "Overview"),
    desc && el("p", { class: "overview-desc" }, desc),
    el("div", { class: "stat-row" }, [
      stat(dyn, dyn === 1 ? "dynamic realm" : "dynamic realms"),
      pre  && stat(pre, "prescribed"),
      omit && stat(omit, "omitted"),
      comps && stat(comps, comps === 1 ? "component" : "components"),
      coupleCount && stat(coupleCount, coupleCount === 1 ? "coupling" : "couplings"),
    ].filter(Boolean)),
  ]);

  root.appendChild(card);
}
