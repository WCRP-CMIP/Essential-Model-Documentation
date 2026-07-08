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

  root.appendChild(el("header", { class: "model-header" }, [
    el("div", { class: "header-top" }, [
      el("div", { class: "header-titles" }, [
        el("p", { class: "eyebrow" }, "Essential Model Documentation"),
        el("h1", { class: "model-title" }, title),
      ]),
      models.length ? el("label", { class: "picker-wrap" }, [
        el("span", { class: "picker-label" }, "Model"), picker,
      ]) : null,
    ]),
    facts,
  ]));
}
