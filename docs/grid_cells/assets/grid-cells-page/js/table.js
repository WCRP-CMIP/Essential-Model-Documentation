// table.js — render the grid-cell table with sortable columns, nested-value
// tooltips, and an expandable per-row detail panel (depth ≤ 2).
//
// A cell holding linked terms shows each term's ui-label; hovering a term
// reveals its description in a floating tooltip. The leftmost column is the
// grid id (what people search for) and doubles as the row-expand toggle. The
// record's own top-level `ui_label` and `alias` are shown as a subtitle under
// the id so users can spot the grid they want without expanding every row.

import { el, clear, attachTooltip } from "./dom.js";
import { short } from "./resolver.js";
import { cellValue, termInfo, numericValue, ID_COL } from "./schema.js";

const GH_BASE = "https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/src-data";
const ghUrl = id => id ? `${GH_BASE}/horizontal_grid_cell/${short(id)}.json` : null;

const isNil = v => v == null || (typeof v === "string" && !v.trim());

// Number of decimal places we display for non-integer values.
const DECIMALS = 6;

// Format a number for display. Integers get thousands separators; non-integers
// are rounded to DECIMALS places. Returns { text, rounded } where `rounded` is
// true iff the displayed value dropped precision from the true value — callers
// append an ellipsis (…) and show the exact value in a tooltip when so.
function fmtNum(n) {
  if (Number.isInteger(n)) return { text: n.toLocaleString(), rounded: false };
  const factor = 10 ** DECIMALS;
  const roundedVal = Math.round(n * factor) / factor;
  const text = String(roundedVal);
  // Rounded if the true value has more precision than what we're showing.
  const rounded = roundedVal !== n;
  return { text, rounded };
}

// Columns forced to the end of the table, in this order. Everything else keeps
// its schema order in between the id (first) and these (last).
const TAIL_KEYS = ["temporal_refinement", "units"];

// Render a single value into a cell node (shared by table cells + detail rows).
// Linked terms → chips with ui_label; description → hover tooltip. Rounded
// numbers get a trailing ellipsis plus a tooltip carrying the exact value.
function renderValue(raw) {
  const cv = cellValue(raw);
  if (cv.empty) return el("span", { class: "gc-empty" }, "—");
  if (cv.terms) {
    const wrap = el("span", { class: "gc-terms" });
    cv.terms.forEach((t, i) => {
      const chip = el("span", { class: "gc-term" }, t.label);
      if (t.description) attachTooltip(chip, t.description);
      wrap.appendChild(chip);
      if (i < cv.terms.length - 1) wrap.appendChild(document.createTextNode(" "));
    });
    return wrap;
  }
  if (typeof cv.number === "number") {
    const { text, rounded } = fmtNum(cv.number);
    const span = el("span", { class: "gc-num" }, rounded ? `${text}…` : text);
    if (rounded) attachTooltip(span, `Exact value: ${cv.number}`);
    return span;
  }
  return el("span", {}, String(cv.text));
}

// Sort comparator for a column.
function makeCmp(col, dir) {
  const s = dir === "asc" ? 1 : -1;
  return (ra, rb) => {
    const a = ra[col.key], b = rb[col.key];
    if (col.kind === "numeric") {
      const na = firstNum(a), nb = firstNum(b);
      if (na == null && nb == null) return 0;
      if (na == null) return 1;      // blanks always last
      if (nb == null) return -1;
      return (na - nb) * s;
    }
    const sa = sortKey(a), sb = sortKey(b);
    if (!sa && !sb) return 0;
    if (!sa) return 1;
    if (!sb) return -1;
    return sa.localeCompare(sb, undefined, { numeric: true, sensitivity: "base" }) * s;
  };
}
const firstNum = raw => {
  if (isNil(raw)) return null;
  const arr = Array.isArray(raw) ? raw : [raw];
  for (const x of arr) { const n = numericValue(x); if (n != null) return n; }
  return null;
};
const sortKey = raw => {
  if (isNil(raw)) return "";
  const arr = Array.isArray(raw) ? raw : [raw];
  return arr.map(x => { const t = termInfo(x); return t ? t.label : String(x); }).join(", ").toLowerCase();
};

// Small helper: turn `record.alias` into a comma-separated string (may be
// either a string or an array in the source).
const aliasText = rec => {
  const a = rec.alias;
  if (isNil(a)) return "";
  if (Array.isArray(a)) return a.filter(Boolean).join(", ");
  return String(a);
};

export function createTable(columns, rows) {
  // visible columns: id first, then only categories + numeric (kept readable).
  // Text (long) columns live in the detail panel only.
  const dataCols = columns.filter(c => c.kind === "category" || c.kind === "numeric");

  // Push the TAIL_KEYS columns to the end (in the specified order); keep the
  // rest in schema order.
  const head = dataCols.filter(c => !TAIL_KEYS.includes(c.key));
  const tail = TAIL_KEYS
    .map(k => dataCols.find(c => c.key === k))
    .filter(Boolean);
  const tableCols = [...head, ...tail];

  let sort = { key: "@id", dir: "asc", kind: "id" };
  let view = rows.slice();

  const thead = el("thead");
  const headRow = el("tr");
  headRow.appendChild(sortableTh(ID_COL, () => setSort("@id", "id")));
  tableCols.forEach(c => headRow.appendChild(sortableTh(c, () => setSort(c.key, c.kind))));
  thead.appendChild(headRow);

  const tbody = el("tbody");
  const tableEl = el("table", { class: "gc-table" }, [thead, tbody]);
  const wrap = el("div", { class: "gc-table-wrap" }, [tableEl]);

  function sortableTh(col, onClick) {
    const arrow = el("span", { class: "gc-sort-arrow" }, "");
    return el("th", {
      class: `gc-th gc-th-${col.kind}`, dataset: { key: col.key },
      onclick: onClick, title: `Sort by ${col.label}`,
    }, [el("span", { class: "gc-th-label" }, col.label), arrow]);
  }

  function setSort(key, kind) {
    if (sort.key === key) sort.dir = sort.dir === "asc" ? "desc" : "asc";
    else sort = { key, dir: "asc", kind };
    paintHeaders();
    render();
  }

  function paintHeaders() {
    headRow.querySelectorAll("th").forEach(th => {
      const arrow = th.querySelector(".gc-sort-arrow");
      if (th.dataset.key === sort.key) { th.classList.add("sorted"); arrow.textContent = sort.dir === "asc" ? " ▲" : " ▼"; }
      else { th.classList.remove("sorted"); arrow.textContent = ""; }
    });
  }

  // Build the depth-2 detail: the record's own `ui_label` at the top, then
  // every remaining key as a key/value row. Nested values are shown as term
  // chips (label + description tooltip) — we do NOT expand further than one
  // level of nesting (that's the "depth 2" contract).
  function buildDetail(rec) {
    const kids = [];

    if (!isNil(rec.ui_label)) {
      kids.push(el("p", { class: "gc-detail-desc" }, String(rec.ui_label)));
    }

    const grid = el("dl", { class: "gc-detail-grid" });
    const skipInDetail = new Set(["@context", "@type", "type", "@id", "ui_label", "validation_key"]);
    Object.keys(rec).forEach(k => {
      if (skipInDetail.has(k)) return;
      if (isNil(rec[k])) return;
      grid.append(
        el("dt", {}, prettyKey(k)),
        el("dd", {}, renderValue(rec[k])),
      );
    });
    kids.push(grid);

    const gh = ghUrl(rec["@id"]);
    if (gh) kids.push(el("a", { class: "gc-detail-link", href: gh, target: "_blank", rel: "noopener" }, "view source JSON ↗"));

    return el("div", { class: "gc-detail" }, kids);
  }

  function render() {
    const cmpCol = sort.kind === "id"
      ? { key: "@id", kind: "text" }
      : columns.find(c => c.key === sort.key) || { key: sort.key, kind: sort.kind };
    view = rows.slice().sort(makeCmp(cmpCol, sort.dir));

    clear(tbody);
    if (!view.length) {
      tbody.appendChild(el("tr", {}, [
        el("td", { class: "gc-norows", colspan: tableCols.length + 1 }, "No grid cells match the current filters."),
      ]));
      return;
    }
    const frag = document.createDocumentFragment();
    view.forEach(rec => {
      const id = short(rec["@id"]);
      const alias = aliasText(rec);
      const uiLabel = !isNil(rec.ui_label) ? String(rec.ui_label) : "";

      const tr = el("tr", { class: "gc-row", dataset: { id } });

      // id cell = expand toggle + id + optional subtitles (alias, ui_label)
      const caret = el("span", { class: "gc-caret" }, "▶");
      const idHead = el("span", { class: "gc-id-head" }, [caret, el("code", { class: "gc-id" }, id)]);
      const idSub = alias
        ? el("span", { class: "gc-id-sub" }, [el("span", { class: "gc-alias" }, alias)])
        : null;

      const idBtn = el("button", { class: "gc-expand", type: "button", "aria-expanded": "false" },
        [idHead, idSub].filter(Boolean));
      const idCell = el("td", { class: "gc-td gc-td-id" }, [idBtn]);
      tr.appendChild(idCell);

      tableCols.forEach(c => tr.appendChild(el("td", { class: `gc-td gc-td-${c.kind}` }, renderValue(rec[c.key]))));
      frag.appendChild(tr);

      // detail row (hidden until expanded)
      const detailTr = el("tr", { class: "gc-detail-row", hidden: "" }, [
        el("td", { class: "gc-detail-cell", colspan: tableCols.length + 1 }, buildDetail(rec)),
      ]);
      frag.appendChild(detailTr);

      idBtn.addEventListener("click", () => {
        const open = detailTr.hasAttribute("hidden");
        if (open) {
          detailTr.removeAttribute("hidden");
          tr.classList.add("expanded");
          idBtn.setAttribute("aria-expanded", "true");
          caret.textContent = "▼";
        } else {
          detailTr.setAttribute("hidden", "");
          tr.classList.remove("expanded");
          idBtn.setAttribute("aria-expanded", "false");
          caret.textContent = "▶";
        }
      });
    });
    tbody.appendChild(frag);
  }

  // external API: re-render with a filtered row set
  function update(filteredRows) { rows = filteredRows; render(); }

  paintHeaders();
  render();

  return { root: wrap, update, get count() { return view.length; } };
}

const prettyKey = k => String(k).replace(/^@/, "").replace(/[_-]+/g, " ").replace(/\b\w/g, c => c.toUpperCase());
