// filters.js — filter bar for the grid-cells table.
//
// Filter selection: a horizontal row of pill toggles, one per available
// column. Clicking an inactive pill activates that filter and shows its
// panel below. Clicking the × on an active pill clears and hides it.
//
// Panel types:
//   category → searchable checklist (multi-select)
//   numeric  → dual-handle range slider + min/max inputs
//   text     → contains search box

import { el } from "./dom.js";
import { categoryTokens, numericValue } from "./schema.js";

const isNil = v => v == null || (typeof v === "string" && !v.trim());

export function createFilters(columns, { onChange }) {
  const state = {
    idQuery: "",
    category: new Map(),
    numeric: new Map(),
    text: new Map(),
  };

  columns.forEach(c => {
    if (c.kind === "category") state.category.set(c.key, new Set());
    else if (c.kind === "numeric") state.numeric.set(c.key, { lo: c.min, hi: c.max, min: c.min, max: c.max });
    else if (c.kind === "text") state.text.set(c.key, "");
  });

  const fire = () => onChange && onChange();
  const filterCols = columns.filter(c => c.kind !== "id");

  // ---- search box ----------------------------------------------------------
  const idInput = el("input", {
    type: "search", class: "gc-search-input",
    placeholder: "Search ID, alias, description…", autocomplete: "off",
    oninput: e => { state.idQuery = e.target.value.trim().toLowerCase(); fire(); },
  });
  const searchRow = el("div", { class: "gc-search-row" }, [
    el("span", { class: "gc-search-icon", html: SEARCH_ICON }),
    idInput,
  ]);

  // ---- pill toggle row + active panel area ---------------------------------
  const panelArea = el("div", { class: "gc-panel-area" });
  const active = new Map(); // key → { clear, pill }

  // Build all panels upfront (hidden); show/hide on toggle.
  const allPanels = new Map(); // key → { panel, clear }
  filterCols.forEach(col => {
    let entry;
    if (col.kind === "category") entry = categoryPanel(col, state, fire);
    else if (col.kind === "numeric") entry = numericPanel(col, state, fire);
    else entry = textPanel(col, state, fire);
    entry.panel.hidden = true;
    panelArea.appendChild(entry.panel);
    allPanels.set(col.key, entry);
  });

  // Pill row — laid out as an equal-column grid so each row has the same
  // number of pills. Find the column count C that divides N most evenly:
  //   prefer a perfect divisor closest to sqrt(N) (neither too wide nor too tall).
  const pillRow = el("div", { class: "gc-pill-row" });
  filterCols.forEach(col => {
    const pill = makePill(col, {
      onActivate: () => activateFilter(col.key),
      onRemove:   () => deactivateFilter(col.key),
    });
    pillRow.appendChild(pill.root);
    allPanels.get(col.key).pill = pill;
  });
  // Set grid columns after all pills are appended so we know N.
  const N = filterCols.length;
  if (N > 0) {
    // Pick the column count in the preferred range [3..6] that minimises
    // wasted cells in the last row (fewest empty slots), tiebreak: larger.
    const lo = Math.min(3, N), hi = Math.min(6, N);
    let best = hi, bestWaste = N;
    for (let c = lo; c <= hi; c++) {
      const waste = (c - (N % c)) % c;
      if (waste < bestWaste || (waste === bestWaste && c > best)) {
        bestWaste = waste; best = c;
      }
    }
    pillRow.style.gridTemplateColumns = `repeat(${best}, 1fr)`;
    // Strip trailing borders: no right border on last column of each row;
    // no bottom border on pills in the last row.
    const pills = pillRow.querySelectorAll('.gc-pill');
    pills.forEach((p, i) => {
      if ((i + 1) % best === 0) p.style.borderRight = 'none';
      if (i >= N - best) p.style.borderBottom = 'none';
    });
  }

  function activateFilter(key) {
    if (active.has(key)) return;
    const entry = allPanels.get(key);
    entry.panel.hidden = false;
    entry.panel.classList.add("gc-panel-enter");
    requestAnimationFrame(() => entry.panel.classList.remove("gc-panel-enter"));
    entry.pill.setActive(true);
    active.set(key, entry);
    // focus first control
    const ctrl = entry.panel.querySelector("input:not([type=range]), select");
    if (ctrl) setTimeout(() => ctrl.focus(), 50);
  }

  function deactivateFilter(key) {
    const entry = active.get(key);
    if (!entry) return;
    entry.clear();
    entry.panel.hidden = true;
    entry.pill.setActive(false);
    active.delete(key);
    fire();
  }

  // clear all — resets search + all active filters
  const clearLink = el("button", {
    class: "gc-clear-link", type: "button",
    onclick: () => {
      idInput.value = ""; state.idQuery = "";
      [...active.keys()].forEach(k => deactivateFilter(k));
      fire();
    },
  }, "Clear all");

  const controlRow = el("div", { class: "gc-control-row" }, [searchRow, clearLink]);
  const root = el("div", { class: "gc-filters" }, [controlRow, pillRow, panelArea]);

  function test(row) {
    if (state.idQuery) {
      const id = String(row["@id"] || "").toLowerCase().split("/").pop();
      const alias = String(row.alias || "").toLowerCase();
      const uiLabel = String(row.ui_label || "").toLowerCase();
      const desc = String(row.description || "").toLowerCase();
      if (!id.includes(state.idQuery)
          && !alias.includes(state.idQuery)
          && !uiLabel.includes(state.idQuery)
          && !desc.includes(state.idQuery)) return false;
    }
    for (const [key, sel] of state.category) {
      if (!sel.size) continue;
      const toks = categoryTokens(row[key]);
      if (!toks.some(t => sel.has(t))) return false;
    }
    for (const [key, r] of state.numeric) {
      if (r.lo <= r.min && r.hi >= r.max) continue;
      const raw = row[key];
      if (isNil(raw)) return false;
      const arr = Array.isArray(raw) ? raw : [raw];
      const nums = arr.map(numericValue).filter(n => n != null);
      if (!nums.length || !nums.some(n => n >= r.lo && n <= r.hi)) return false;
    }
    for (const [key, q] of state.text) {
      if (!q) continue;
      const raw = row[key];
      const hay = (Array.isArray(raw) ? raw.join(" ") : String(raw ?? "")).toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  }

  return { root, test, state };
}

// ---- pill toggle -----------------------------------------------------------
// Clicking toggles active state — no separate remove button.
function makePill(col, { onActivate, onRemove }) {
  const root = el("button", {
    class: "gc-pill", type: "button", "aria-pressed": "false",
    title: col.label,
    onclick: () => {
      if (root.classList.contains("active")) onRemove();
      else onActivate();
    },
  }, [el("span", { class: "gc-pill-label" }, col.label)]);

  const setActive = active => {
    root.classList.toggle("active", active);
    root.setAttribute("aria-pressed", String(active));
  };

  return { root, setActive };
}

// ---- panel shell -----------------------------------------------------------
function panelShell(col, bodyChildren) {
  const body = el("div", { class: "gc-panel-body" }, bodyChildren);
  return el("div", { class: `gc-panel gc-panel-${col.kind}`, "data-label": col.label }, [body]);
}

// ---- category checklist ----------------------------------------------------
function categoryPanel(col, state, fire) {
  const sel = state.category.get(col.key);
  const list = el("div", { class: "gc-check-list" });

  const searchInput = col.options.length > 8 ? el("input", {
    type: "search", class: "gc-check-search",
    placeholder: `Search ${col.label.toLowerCase()}…`,
    oninput: e => {
      const q = e.target.value.trim().toLowerCase();
      [...list.children].forEach(r => {
        r.style.display = (r.dataset.label || "").includes(q) ? "" : "none";
      });
    },
  }) : null;

  const boxes = [];
  const countEl = el("span", { class: "gc-check-count" });
  const updateCount = () => {
    countEl.textContent = sel.size ? `${sel.size} of ${col.options.length} selected` : "";
  };

  col.options.forEach(opt => {
    const cb = el("input", {
      type: "checkbox", value: opt,
      onchange: e => { if (e.target.checked) sel.add(opt); else sel.delete(opt); updateCount(); fire(); },
    });
    boxes.push(cb);
    list.appendChild(el("label", {
      class: "gc-check-row", dataset: { label: opt.toLowerCase() },
    }, [cb, el("span", {}, opt)]));
  });
  updateCount();

  const clear = () => {
    sel.clear(); boxes.forEach(b => b.checked = false);
    if (searchInput) { searchInput.value = ""; [...list.children].forEach(r => r.style.display = ""); }
    updateCount();
  };

  const panel = panelShell(col, [
    searchInput,
    list,
    countEl,
  ].filter(Boolean));
  return { panel, clear };
}

// ---- numeric range ---------------------------------------------------------
function numericPanel(col, state, fire) {
  const r = state.numeric.get(col.key);
  const span = (col.max - col.min) || 1;
  const step = niceStep(span);

  const loNum = el("input", { type: "number", class: "gc-num-input", value: fmt(r.lo), step, min: col.min, max: col.max });
  const hiNum = el("input", { type: "number", class: "gc-num-input", value: fmt(r.hi), step, min: col.min, max: col.max });
  const loRange = el("input", { type: "range", class: "gc-range gc-range-lo", min: col.min, max: col.max, step, value: r.lo });
  const hiRange = el("input", { type: "range", class: "gc-range gc-range-hi", min: col.min, max: col.max, step, value: r.hi });
  const fill = el("div", { class: "gc-range-fill" });
  const track = el("div", { class: "gc-range-track" }, [fill]);

  const paint = () => {
    const a = ((r.lo - col.min) / span) * 100, b = ((r.hi - col.min) / span) * 100;
    fill.style.left = a + "%"; fill.style.right = (100 - b) + "%";
  };
  const sync = () => { loNum.value = fmt(r.lo); hiNum.value = fmt(r.hi); loRange.value = r.lo; hiRange.value = r.hi; paint(); };

  loRange.addEventListener("input", () => { r.lo = Math.min(Number(loRange.value), r.hi); sync(); fire(); });
  hiRange.addEventListener("input", () => { r.hi = Math.max(Number(hiRange.value), r.lo); sync(); fire(); });
  loNum.addEventListener("change", () => { r.lo = clamp(Number(loNum.value), col.min, r.hi); sync(); fire(); });
  hiNum.addEventListener("change", () => { r.hi = clamp(Number(hiNum.value), r.lo, col.max); sync(); fire(); });
  paint();

  const clear = () => { r.lo = r.min; r.hi = r.max; sync(); };

  const panel = panelShell(col, [
    el("div", { class: "gc-range-wrap" }, [track, loRange, hiRange]),
    el("div", { class: "gc-num-row" }, [
      el("label", { class: "gc-num-label" }, ["Min", loNum]),
      el("label", { class: "gc-num-label" }, ["Max", hiNum]),
    ]),
  ]);
  return { panel, clear };
}

// ---- text contains ---------------------------------------------------------
function textPanel(col, state, fire) {
  const input = el("input", {
    type: "search", class: "gc-check-search", placeholder: "Contains…",
    oninput: e => { state.text.set(col.key, e.target.value.trim().toLowerCase()); fire(); },
  });
  const clear = () => { input.value = ""; state.text.set(col.key, ""); };
  return { panel: panelShell(col, [input]), clear };
}

// ---- helpers ---------------------------------------------------------------
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const fmt = n => {
  if (!Number.isFinite(n)) return "";
  if (Number.isInteger(n)) return String(n);
  return String(Math.round(n * 1000) / 1000);
};
function niceStep(span) {
  if (span <= 2) return 0.01;
  if (span <= 20) return 0.1;
  if (span <= 200) return 1;
  return Math.pow(10, Math.floor(Math.log10(span)) - 2);
}

// ---- inline icons ----------------------------------------------------------
const SEARCH_ICON = `<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="8.5" cy="8.5" r="5.5"/><path d="m13 13 3.5 3.5"/></svg>`;
