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

export function createTable(columns, rows, { onHoverRow, onLeaveRow, onSelectRow, onDoubleClickRow } = {}) {
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

  // Pagination. `view` is the full sorted selection; `pageRows()` is the slice
  // actually rendered. CSV always exports `view`, never just the page.
  let pageSize = 50;          // 0 = show all
  let page = 1;
  // Expanded detail rows are tracked by id so they survive paging and sorting
  // (previously the open/closed state lived only in the DOM).
  const expandedIds = new Set();

  function pageCount() {
    return pageSize === 0 ? 1 : Math.max(1, Math.ceil(view.length / pageSize));
  }
  function pageRows() {
    if (pageSize === 0) return view;
    const start = (page - 1) * pageSize;
    return view.slice(start, start + pageSize);
  }
  function pageOf(id) {
    if (pageSize === 0) return 1;
    const i = view.findIndex(r => short(r["@id"]) === id);
    return i < 0 ? -1 : Math.floor(i / pageSize) + 1;
  }

  const thead = el("thead");
  const headRow = el("tr");
  headRow.appendChild(sortableTh(ID_COL, () => setSort("@id", "id")));
  tableCols.forEach(c => headRow.appendChild(sortableTh(c, () => setSort(c.key, c.kind))));
  thead.appendChild(headRow);

  const tbody = el("tbody");
  const tableEl = el("table", { class: "gc-table" }, [thead, tbody]);
  const wrap = el("div", { class: "gc-table-wrap" }, [tableEl]);

  // id -> { tr, idBtn, detailTr } so the scatter can highlight / reveal rows
  const rowById = new Map();

  // Sortable header. The click target must be reachable by keyboard: a bare
  // <th onclick> is not focusable and announces no sort state, so keyboard
  // and screen-reader users cannot sort the table at all.
  function sortableTh(col, onClick) {
    const arrow = el("span", { class: "gc-sort-arrow", "aria-hidden": "true" }, "");
    const th = el("th", {
      class: `gc-th gc-th-${col.kind}`, dataset: { key: col.key },
      scope: "col", role: "columnheader", tabindex: "0",
      onclick: onClick, title: `Sort by ${col.label}`,
      "aria-label": `${col.label}, activate to sort`,
    }, [el("span", { class: "gc-th-label" }, col.label), arrow]);
    th.addEventListener("keydown", ev => {
      if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); onClick(); }
    });
    return th;
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
      if (th.dataset.key === sort.key) {
        th.classList.add("sorted");
        arrow.textContent = sort.dir === "asc" ? " ▲" : " ▼";
        // announce sort state — the arrow glyph is aria-hidden decoration
        th.setAttribute("aria-sort", sort.dir === "asc" ? "ascending" : "descending");
      } else {
        th.classList.remove("sorted");
        arrow.textContent = "";
        th.removeAttribute("aria-sort");
      }
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

  // ---------- CSV export ----------
  // Exports the COMPLETE current selection (all filtered rows, current sort),
  // not just the visible page. Includes every field present on the records,
  // not only the columns the table chooses to display.
  function csvCell(v) {
    let s;
    if (v === null || v === undefined) s = "";
    else if (Array.isArray(v)) s = v.map(x => csvScalar(x)).join("; ");
    else s = csvScalar(v);
    // spreadsheet formula-injection guard
    if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
    return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  function csvScalar(v) {
    if (v === null || v === undefined) return "";
    if (typeof v === "object") {
      const t = termInfo(v);
      if (t && t.label) return t.label;
      return v["@id"] ? short(v["@id"]) : JSON.stringify(v);
    }
    return String(v);
  }

  function downloadCsv() {
    if (!view.length) return;
    // union of all keys across the selection, id first
    const keys = new Set();
    view.forEach(r => Object.keys(r).forEach(k => {
      if (k !== "@id" && k !== "@context" && k !== "@type") keys.add(k);
    }));
    const cols = ["@id", ...[...keys].sort()];
    const lines = [cols.map(c => csvCell(c.replace(/^@/, ""))).join(",")];
    view.forEach(r => {
      lines.push(cols.map(k => csvCell(k === "@id" ? short(r["@id"]) : r[k])).join(","));
    });
    const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
    const blob = new Blob(["\uFEFF" + lines.join("\r\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = el("a", { href: url, download: `emd-grid-cells-${view.length}-rows-${stamp}.csv` });
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  // ---------- pager ----------
  const pageInfo = el("span", { class: "gc-page-info" }, "");
  const btnFirst = el("button", { class: "gc-page-btn", type: "button", title: "First page", "aria-label": "First page", onclick: () => goPage(1) }, "«");
  const btnPrev  = el("button", { class: "gc-page-btn", type: "button", title: "Previous page", "aria-label": "Previous page", onclick: () => goPage(page - 1) }, "‹");
  const btnNext  = el("button", { class: "gc-page-btn", type: "button", title: "Next page", "aria-label": "Next page", onclick: () => goPage(page + 1) }, "›");
  const btnLast  = el("button", { class: "gc-page-btn", type: "button", title: "Last page", "aria-label": "Last page", onclick: () => goPage(pageCount()) }, "»");
  const pagePos  = el("span", { class: "gc-page-pos" }, "");

  const sizeSelect = el("select", {
    class: "gc-page-size", id: "gc-page-size",
    onchange: ev => { pageSize = parseInt(ev.target.value, 10); page = 1; render(); },
  }, [25, 50, 100, 250, 0].map(n =>
    el("option", { value: String(n), ...(n === 50 ? { selected: "" } : {}) }, n === 0 ? "All" : String(n))));

  const csvBtn = el("button", {
    class: "gc-csv-btn", type: "button", onclick: downloadCsv,
    title: "Download the full filtered selection as CSV",
  }, "Download CSV");

  const pager = el("div", { class: "gc-pager" }, [
    pageInfo,
    el("span", { class: "gc-pager-spacer" }),
    csvBtn,
    el("label", { class: "gc-page-size-label", for: "gc-page-size" }, ["Rows", sizeSelect]),
    el("div", { class: "gc-page-btns" }, [btnFirst, btnPrev, pagePos, btnNext, btnLast]),
  ]);

  function goPage(n) {
    page = Math.min(Math.max(1, n), pageCount());
    render();
    wrap.scrollTop = 0;
  }

  function paintPager() {
    const total = view.length;
    const pages = pageCount();
    if (page > pages) page = pages;
    const from = total === 0 ? 0 : (pageSize === 0 ? 1 : (page - 1) * pageSize + 1);
    const to = pageSize === 0 ? total : Math.min(page * pageSize, total);
    pageInfo.textContent = total ? `Showing ${from}–${to} of ${total}` : "No rows";
    pagePos.textContent = `${page} / ${pages}`;
    btnFirst.disabled = btnPrev.disabled = page <= 1;
    btnNext.disabled = btnLast.disabled = page >= pages;
    csvBtn.disabled = total === 0;
    // page controls are pointless when everything is on one page
    pager.classList.toggle("single-page", pages <= 1);
  }

  function render() {
    const cmpCol = sort.kind === "id"
      ? { key: "@id", kind: "text" }
      : columns.find(c => c.key === sort.key) || { key: sort.key, kind: sort.kind };
    view = rows.slice().sort(makeCmp(cmpCol, sort.dir));

    clear(tbody);
    rowById.clear();
    if (!view.length) {
      paintPager();
      tbody.appendChild(el("tr", {}, [
        el("td", { class: "gc-norows", colspan: tableCols.length + 1 }, "No grid cells match the current filters."),
      ]));
      return;
    }
    paintPager();
    const frag = document.createDocumentFragment();
    pageRows().forEach(rec => {
      const id = short(rec["@id"]);
      const alias = aliasText(rec);
      const uiLabel = !isNil(rec.ui_label) ? String(rec.ui_label) : "";

      const tr = el("tr", { class: "gc-row", dataset: { id } });
      // report hover so the similarity map can highlight the matching node
      tr.addEventListener("mouseenter", () => onHoverRow && onHoverRow(id));
      tr.addEventListener("mouseleave", () => onLeaveRow && onLeaveRow());
      // single click on the row → highlight the node in the graph
      tr.addEventListener("click", () => onSelectRow && onSelectRow(id));
      // double click → highlight AND scroll to the graph
      tr.addEventListener("dblclick", () => onDoubleClickRow && onDoubleClickRow(id));

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

      // detail row — restored from expandedIds so paging/sorting preserves it
      const isOpen = expandedIds.has(id);
      const detailTr = el("tr", { class: "gc-detail-row" }, [
        el("td", { class: "gc-detail-cell", colspan: tableCols.length + 1 }, buildDetail(rec)),
      ]);
      if (!isOpen) detailTr.setAttribute("hidden", "");
      else { tr.classList.add("expanded"); idBtn.setAttribute("aria-expanded", "true"); caret.textContent = "▼"; }
      frag.appendChild(detailTr);

      idBtn.addEventListener("click", ev => {
        // Don't let the button click bubble to the row — the row's own click
        // handler already fires from the ambient click; this stops the row's
        // "highlight" firing twice on the same click.
        ev.stopPropagation();
        const open = detailTr.hasAttribute("hidden");
        if (open) {
          detailTr.removeAttribute("hidden");
          tr.classList.add("expanded");
          idBtn.setAttribute("aria-expanded", "true");
          caret.textContent = "▼";
          expandedIds.add(id);
        } else {
          detailTr.setAttribute("hidden", "");
          tr.classList.remove("expanded");
          idBtn.setAttribute("aria-expanded", "false");
          caret.textContent = "▶";
          expandedIds.delete(id);
        }
      });

      rowById.set(id, { tr, idBtn, detailTr, caret });
    });
    tbody.appendChild(frag);
  }

  // external API: re-render with a filtered row set.
  // Filters changing means the selection changed, so return to page 1 —
  // staying on page 7 of a now-2-page result would show an empty table.
  function update(filteredRows) { rows = filteredRows; page = 1; render(); }

  // Highlight a single row (called when its scatter node is hovered).
  let highlighted = null;
  function highlight(id) {
    if (highlighted === id) return;
    clearHighlight();
    const entry = rowById.get(id);
    if (!entry) return;
    entry.tr.classList.add("gc-row-linked");
    highlighted = id;
  }
  function clearHighlight() {
    if (highlighted != null) {
      const prev = rowById.get(highlighted);
      if (prev) prev.tr.classList.remove("gc-row-linked");
      highlighted = null;
    }
  }

  // Reveal a row: scroll to it, open its detail, briefly pulse it.
  // Called when a scatter node is clicked.
  //
  // With pagination the target row may not be on the current page — without
  // the page jump below, clicking a node would silently do nothing.
  function reveal(id) {
    const target = pageOf(id);
    if (target === -1) return;            // not in the current selection at all
    if (target !== page) { page = target; render(); }

    const entry = rowById.get(id);
    if (!entry) return;
    // open the detail if closed
    if (entry.detailTr.hasAttribute("hidden")) entry.idBtn.click();
    // scroll into view, if the environment supports it
    if (typeof entry.tr.scrollIntoView === "function") {
      entry.tr.scrollIntoView({ block: "center", behavior: "smooth" });
    }
    // pulse animation
    entry.tr.classList.remove("gc-row-pulse");
    // force reflow so the animation restarts if triggered rapidly
    void entry.tr.offsetWidth;
    entry.tr.classList.add("gc-row-pulse");
  }

  paintHeaders();
  render();

  return {
    root: el("div", { class: "gc-table-outer" }, [wrap, pager]),
    update, highlight, clearHighlight, reveal,
    get count() { return view.length; },
  };
}

const prettyKey = k => String(k).replace(/^@/, "").replace(/[_-]+/g, " ").replace(/\b\w/g, c => c.toUpperCase());
