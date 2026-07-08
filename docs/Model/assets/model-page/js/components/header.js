// components/header.js — model title, family, release year, calendar, CRS badge.
import { el } from "../dom.js";

const SVGNS = "http://www.w3.org/2000/svg";

// Draw the first-visit hint's connector: a curved arrow from the centred note
// down to an underline beneath the model picker. Recomputed from live element
// positions so the arrow always reaches the selector.
function drawModelHintConnector(note) {
  const svg = note.querySelector(".hint-canvas");
  const card = note.querySelector(".hint-note");
  const picker = document.querySelector(".model-picker");
  if (!svg || !card || !picker) return;

  const vw = window.innerWidth, vh = window.innerHeight;
  svg.setAttribute("viewBox", `0 0 ${vw} ${vh}`);
  svg.setAttribute("width", vw);
  svg.setAttribute("height", vh);
  while (svg.firstChild) svg.removeChild(svg.firstChild);

  const p = picker.getBoundingClientRect();
  const n = card.getBoundingClientRect();

  // underline sits just below the picker, spanning its width (small overshoot)
  const uy = p.bottom + 8;
  const ux1 = p.left - 3, ux2 = p.right + 3;

  // arrow tip sits a little BELOW the underline (a clear gap), pointing up at it
  const gap = 13;
  const ex = ux1 + (ux2 - ux1) * 0.30;
  const ey = uy + gap;

  // shaft rises from the note's top edge up to the tip, approaching vertically
  const sx = n.left + n.width * 0.62, sy = n.top - 4;
  const c1x = sx + (ex - sx) * 0.35, c1y = sy - (sy - ey) * 0.30;
  const c2x = ex, c2y = ey + Math.min(90, (sy - ey) * 0.40);   // control directly below tip → vertical approach

  // upward arrowhead at the tip (aligned with the vertical approach)
  const ahLen = 12, ahW = 7;
  const b1 = [ex - ahW, ey + ahLen];
  const b2 = [ex + ahW, ey + ahLen];

  const mk = (tag, attrs) => {
    const e = document.createElementNS(SVGNS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  };
  svg.appendChild(mk("path", { class: "hint-line",
    d: `M ${sx} ${sy} C ${c1x} ${c1y}, ${c2x} ${c2y}, ${ex} ${ey}` }));
  svg.appendChild(mk("path", { class: "hint-line",
    d: `M ${b1[0]} ${b1[1]} L ${ex} ${ey} L ${b2[0]} ${b2[1]}` }));
  svg.appendChild(mk("path", { class: "hint-line",
    d: `M ${ux1} ${uy} Q ${(ux1 + ux2) / 2} ${uy + 3}, ${ux2} ${uy}` }));
}

export function mountHeader(root, model, { onModelChange, models = [], current, pickerHint = false } = {}) {
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

  const pickerWrap = el("label", { class: "picker-wrap" }, [
    el("span", { class: "picker-label" }, "Model"), picker,
  ]);

  // First-visit nudge: a neat handwritten-style notice that fades in from the
  // centre of the screen, with a hand-drawn arrow that reaches the model
  // selector and circles it. Shown by main.js only on a first visit with no
  // ?model= param, and removed after 3 seconds. Full-viewport overlay with
  // pointer-events:none so it never blocks the page; id-guarded against dupes.
  if (pickerHint && !document.getElementById("model-hint-note")) {
    const note = document.createElement("div");
    note.className = "picker-hint";
    note.id = "model-hint-note";
    note.setAttribute("role", "status");
    note.innerHTML =
      '<svg class="hint-canvas" aria-hidden="true"></svg>' +
      '<div class="hint-note"><p class="hint-note-text">Looking for a different model?<br>' +
      'Choose one from the selector, up&#8209;here.</p></div>';
    document.body.appendChild(note);
    // Draw once layout settles, and keep it aligned on resize until removed.
    const redraw = () => {
      if (document.body.contains(note)) drawModelHintConnector(note);
      else window.removeEventListener("resize", redraw);
    };
    requestAnimationFrame(() => requestAnimationFrame(redraw));
    setTimeout(redraw, 1100);   // re-align after the note's 1s pop-in settles
    window.addEventListener("resize", redraw);
  }

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

  // Subtle in-context links: open the standalone schema-view page (for the
  // current model) and the "understanding this page" guide. Both point at real
  // HTML pages so they open in the browser rather than downloading.
  const schemaHref = `assets/emd_model_graph.html?model=${encodeURIComponent(current || "")}`;
  const links = el("nav", { class: "header-links" }, [
    el("a", { class: "header-link", href: schemaHref, target: "_blank", rel: "noopener" }, "Schema view"),
    el("span", { class: "header-link-sep", "aria-hidden": "true" }, "·"),
    el("a", { class: "header-link", href: "assets/viewer_instructions.html", target: "_blank", rel: "noopener" },
      "Understanding this page"),
  ]);

  root.appendChild(el("header", { class: "model-header" }, [
    el("div", { class: "header-top" }, [
      el("div", { class: "header-titles" }, [
        eyebrow,
        el("h1", { class: "model-title" }, title),
        links,
      ]),
      models.length ? pickerWrap : null,
    ]),
    facts,
  ]));
}
