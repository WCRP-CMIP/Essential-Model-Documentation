// components/header.js — model title, family, release year, calendar, CRS badge.
import { el } from "../dom.js";

export function mountHeader(root, model, { onModelChange, models = [], current } = {}) {
  const title = model.ui_label || model.name || model["@id"] || "Model";
  const family = model.family;
  const year = model.release_year;
  const calendar = Array.isArray(model.calendar) ? model.calendar.join(", ") : model.calendar;
  const crs = model.crs;

  const picker = el("select", {
    class: "model-picker",
    onchange: e => onModelChange && onModelChange(e.target.value),
  }, models.map(id => {
    const o = el("option", { value: id }, id);
    if (id === current) o.selected = true;
    return o;
  }));

  const facts = el("div", { class: "header-facts" }, [
    family && el("span", { class: "chip chip-family" }, [
      el("span", { class: "chip-key" }, "family"), family,
    ]),
    year && el("span", { class: "chip" }, [
      el("span", { class: "chip-key" }, "released"), String(year),
    ]),
    calendar && el("span", { class: "chip" }, [
      el("span", { class: "chip-key" }, "calendar"), calendar,
    ]),
    crs && el("span", { class: "chip chip-crs", title: "Canonical Realm String" }, [
      el("span", { class: "chip-key" }, "CRS"),
      el("code", {}, crs),
    ]),
  ]);

  // "EMD" eyebrow links back to the site home. NAV_PREFIX is injected per-page
  // by the mkdocs post-build step and points at the site root from any depth;
  // fall back to "../" (this page is served at <site>/Model/).
  const homeHref = (typeof window !== "undefined" && window.NAV_PREFIX) ? window.NAV_PREFIX : "../";
  const eyebrow = el("a", { class: "eyebrow eyebrow-home", href: homeHref, title: "Back to home" },
    "Essential Model Documentation");
  // NAV_PREFIX may be set after this renders; refresh the href once it's available.
  requestAnimationFrame(() => { if (window.NAV_PREFIX) eyebrow.href = window.NAV_PREFIX; });

  // Subtle in-context links: jump to the on-page schema graph, and open the
  // "how to use this page" guide.
  const links = el("nav", { class: "header-links" }, [
    el("a", { class: "header-link", href: "#schema" }, "Schema view"),
    el("span", { class: "header-link-sep", "aria-hidden": "true" }, "·"),
    el("a", { class: "header-link", href: "assets/viewer_instructions.md", target: "_blank", rel: "noopener" },
      "Understanding this page"),
  ]);

  root.appendChild(el("header", { class: "model-header" }, [
    el("div", { class: "header-top" }, [
      el("div", { class: "header-titles" }, [
        eyebrow,
        el("h1", { class: "model-title" }, title),
        links,
      ]),
      models.length ? el("label", { class: "picker-wrap" }, [
        el("span", { class: "picker-label" }, "Model"), picker,
      ]) : null,
    ]),
    facts,
  ]));
}
