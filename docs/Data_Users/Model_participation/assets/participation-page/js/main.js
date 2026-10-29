// main.js — Model participation: one row per institution, with the component
// and model (source) families it leads (primary) or collaborates on, its
// country, a link to its ROR page, and the data it has published to ESGF.
//
//   <div id="emd-model-participation-page"></div>
//   <script type="module"> import { initParticipation } from "./assets/participation-page/js/main.js"; initParticipation(); </script>
//
// Loading is staged so the page is usable at once:
//   1. model families  -> table (institutions + tags) renders immediately
//   2. institution registry records -> country + ROR links fill in
//   3. the models list -> each model's Arrow file is read -> "Published data"
//      column fills in last, with a loading bar in its title
//
// Optional query params:
//   ?base=<url>      EMD registry root (default: the published site)
//   ?universe=<url>  institution registry root
//   ?arrow=<url>     ESGF Arrow collection root (default .../CMIP7)
//   ?modelpage=<url> EMD Model page (default https://emd.wcrp-cmip.org/docs/Data_Users/Model_viewer/)
//   ?type=model|component   ?mode=primary   ?q=<search>   (initial view)

import { Resolver, DEFAULT_BASE, short } from "./resolver.js";
import { el, clear } from "./dom.js";
import { buildRows, totalOf, countryOf, groupPublished, publishedFor, summariseRows, modelFamilyId, UNASSIGNED } from "./participation.js";

const PARAMS = new URLSearchParams(location.search);
const BASE = (PARAMS.get("base") || DEFAULT_BASE).replace(/\/?$/, "/");
const FOLDER = "model_family";
const SOURCE = "https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/src-data/model_family/";

// A model links to its page in the EMD documentation: <page>?model=<model id>.
const MODEL_PAGE = (PARAMS.get("modelpage") || "https://emd.wcrp-cmip.org/docs/Data_Users/Model_viewer/").replace(/\/?$/, "/");

// Institution records (with their location and ROR id) live in the WCRP universe registry.
const UNIVERSE = (PARAMS.get("universe") || "https://wcrp-cmip.github.io/WCRP-universe/").replace(/\/?$/, "/");
const ORG_FOLDER = "organisation";

// ESGF Arrow bundle: one file per model, named after it: <root>/<validation_key>.arrow.
// The collection folder is upper-case and the host is case-sensitive.
const ARROW_ROOT = (PARAMS.get("arrow") || "https://esgf-arrow.pages.dev/CMIP7").replace(/\/+$/, "");
// How many Arrow files are downloaded and read at once.
const ARROW_CONCURRENCY = 4;

// institution id -> { names, codes, label, ror, tip } once looked up; null when
// the registry has no record for it. Absent while still loading.
const countries = new Map();
const countryText = r => { const c = countries.get(r.id); return c ? c.names.join(", ") : ""; };

// Published data read from the models' Arrow files. status: waiting -> loading -> done | error.
const pub = { status: "waiting", byFamily: new Map(), unattributed: [], failed: [], checked: 0, published: 0, error: "" };
const pubDatasets = r => (pub.status === "done" ? publishedFor(r, pub.byFamily).datasets : 0);

const MODES = [
  { key: "all", label: "Primary + collaborators" },
  { key: "primary", label: "Primary only" },
];
const TYPES = [
  { key: "all", label: "All families" },
  { key: "model", label: "Model (source) families only" },
  { key: "component", label: "Component families only" },
];
const COLUMNS = [
  { key: "name", label: "Institution" },
  { key: "components", label: "Component families" },
  { key: "models", label: "Model families" },
  { key: "published", label: "Published data" },
];
const byName = (a, b) => a.label.localeCompare(b.label);
const SORTERS = {
  total: (a, b) => totalOf(a) - totalOf(b) || byName(a, b),
  name: byName,
  components: (a, b) => a.components.length - b.components.length || byName(a, b),
  models: (a, b) => a.models.length - b.models.length || byName(a, b),
  published: (a, b) => pubDatasets(a) - pubDatasets(b) || byName(a, b),
};

function chip(fam) {
  const tip = [`${fam.id} — ${fam.type} family, ${fam.role === "primary" ? "primary developer" : "collaborator"}`,
               fam.description.slice(0, 280)].filter(Boolean).join("\n");
  return el("a", {
    class: `mp-chip mp-chip--${fam.role} mp-chip--${fam.type}`,
    href: SOURCE + encodeURIComponent(fam.id) + ".json",
    target: "_blank", rel: "noopener", title: tip,
  }, fam.label);
}

const cell = fams => fams.length
  ? el("div", { class: "mp-chips" }, fams.map(chip))
  : el("span", { class: "gc-empty" }, "—");

export async function initParticipation() {
  const mount = document.getElementById("emd-model-participation-page") || document.body;
  const page = el("div", { class: "emd-page gc-page" });
  mount.appendChild(page);

  page.appendChild(el("header", { class: "gc-header" }, [
    el("a", { class: "eyebrow eyebrow-home", href: "../../" }, "EMD DOCUMENTATION"),
    el("h1", { class: "gc-title" }, "Model participation"),
  ]));

  const shell = el("div", { class: "gc-shell" });
  page.appendChild(shell);
  shell.appendChild(el("div", { class: "page-spinner" }, [
    el("div", { class: "spinner-ring" }), el("span", {}, "Loading model families…"),
  ]));

  // ---- stage 1: model families -------------------------------------------
  let records;
  try { records = await new Resolver(BASE).collection(FOLDER); }
  catch (e) {
    clear(shell);
    shell.appendChild(el("div", { class: "page-error" }, `Could not load model families: ${e.message}`));
    return;
  }
  clear(shell);
  if (!records.length) {
    shell.appendChild(el("div", { class: "page-error" }, "No model families were found."));
    return;
  }

  const built = {
    all: buildRows(records, { includeCollaborators: true }),
    primary: buildRows(records, { includeCollaborators: false }),
  };
  const state = {
    mode: PARAMS.get("mode") === "primary" ? "primary" : "all",
    type: TYPES.some(t => t.key === PARAMS.get("type")) ? PARAMS.get("type") : "all",
    query: (PARAMS.get("q") || "").trim().toLowerCase(),
    sortKey: "total", dir: "desc",
  };

  // ---- controls ----------------------------------------------------------
  const search = el("input", {
    class: "gc-search-input", type: "search", value: PARAMS.get("q") || "",
    placeholder: "Search institutions, countries or families…",
    "aria-label": "Search institutions, countries or families",
    oninput: e => { state.query = e.target.value.trim().toLowerCase(); render(); },
  });
  const modeSelect = el("select", {
    class: "mp-select", "aria-label": "Which families an institution lists",
    onchange: e => { state.mode = e.target.value; render(); },
  }, MODES.map(m => el("option", { value: m.key, selected: m.key === state.mode }, m.label)));
  const typeSelect = el("select", {
    class: "mp-select", "aria-label": "Show families of type",
    onchange: e => { state.type = e.target.value; render(); },
  }, TYPES.map(t => el("option", { value: t.key, selected: t.key === state.type }, t.label)));
  const controls = el("div", { class: "mp-controls" }, [
    el("div", { class: "gc-search-row" }, search),
    modeSelect,
    typeSelect,
  ]);

  // ---- table -------------------------------------------------------------
  const countPill = el("span", { class: "gc-count-pill" });
  const tbody = el("tbody");

  // Loading bar shown in the "Published data" column title while stage 3 runs.
  const barFill = el("div", { class: "mp-bar-fill" });
  const bar = el("div", {
    class: "mp-bar", role: "progressbar", "aria-label": "Loading published data",
    "aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": "0",
  }, barFill);
  const setProgress = p => {
    barFill.style.width = p + "%";
    bar.setAttribute("aria-valuenow", String(Math.round(p)));
    if (p >= 100) setTimeout(() => bar.classList.add("done"), 700);
  };

  const heads = COLUMNS.map(col => {
    const arrow = el("span", { class: "gc-sort-arrow", "aria-hidden": "true" });
    const btn = el("button", { class: "mp-sort", type: "button", onclick: () => setSort(col.key) },
      [col.label, arrow]);
    return { col, arrow, th: el("th", { class: "gc-th", scope: "col" }, col.key === "published" ? [btn, bar] : btn) };
  });
  shell.appendChild(el("div", { class: "gc-table-card" }, [
    el("div", { class: "gc-table-head" }, [controls, countPill]),
    el("div", { class: "gc-table-wrap" }, el("table", { class: "gc-table" }, [
      el("thead", {}, el("tr", {}, heads.map(h => h.th))), tbody,
    ])),
  ]));

  shell.appendChild(el("p", { class: "mp-callout" }, [
    el("strong", {}, "Institutions are managed by "),
    el("a", { href: "https://github.com/ESGF/esgf-vocab", target: "_blank", rel: "noopener" }, "ESGVOC (IPSL)"),
    el("strong", {}, ", not by the EMD. "),
    "Names, acronyms and locations come from the ESGVOC institution registry. For corrections to an " +
    "institution’s location or acronym, please contact the ESGVOC team.",
  ]));
  shell.appendChild(el("p", { class: "mp-note" },
    "Tags: a solid blue outline marks the primary developer and a dashed outline a collaborator. " +
    "Each tag links to the family’s source JSON, each institution name to its ROR page, and each " +
    "published model to its EMD documentation page."));
  const pubNote = el("p", { class: "mp-note", hidden: true });
  shell.appendChild(pubNote);

  // Registry values that were not valid institution ids, shown so they can be fixed at source.
  const notes = built.all.notes;
  if (notes.length) {
    shell.appendChild(el("details", { class: "mp-issues" }, [
      el("summary", {}, `Data notes (${notes.length})`),
      el("ul", {}, notes.map(n => el("li", {},
        `${n.family} · ${n.field}: “${n.value}” — ${n.id ? `read as ${n.id.toUpperCase()}` : "not a valid institution id, left out"}`))),
    ]));
  }
  // Filled in as the later stages finish.
  const countryIssues = el("details", { class: "mp-issues", hidden: true });
  const publishedIssues = el("details", { class: "mp-issues", hidden: true });
  shell.appendChild(countryIssues);
  shell.appendChild(publishedIssues);

  function setSort(key) {
    if (state.sortKey === key) state.dir = state.dir === "asc" ? "desc" : "asc";
    else { state.sortKey = key; state.dir = key === "name" ? "asc" : "desc"; }
    render();
  }

  // Apply the family-type filter: drop the other type's tags and any row left empty.
  const typed = rows => state.type === "all" ? rows : rows
    .map(r => ({ ...r,
      components: state.type === "model" ? [] : r.components,
      models: state.type === "component" ? [] : r.models }))
    .filter(r => totalOf(r) > 0);

  const matches = r => !state.query || [r.label, r.id, countryText(r), ...[...r.components, ...r.models]
    .flatMap(f => [f.label, f.id]),
    ...(pub.status === "done" ? publishedFor(r, pub.byFamily).models.flatMap(m => [m.key, m.id]) : [])]
    .join(" ").toLowerCase().includes(state.query);

  // Institution cell: the name (a link to its ROR page once the registry record
  // has loaded and carries a ROR id) over a small line with its country. The id
  // is kept in the tooltip. The country line's tooltip gives the registry's city
  // and entry so a wrong registry record is easy to spot.
  function institutionCell(r) {
    if (r.id === UNASSIGNED) return el("span", { class: "mp-inst" }, r.label);
    const c = countries.get(r.id);
    const name = c && c.ror
      ? el("a", {
          class: "mp-inst mp-inst-link", href: c.ror, target: "_blank", rel: "noopener",
          title: `${r.id} — open ${c.label} on ROR`,
        }, r.label)
      : el("span", { class: "mp-inst", title: r.id }, r.label);

    let sub;
    if (!countries.has(r.id)) sub = el("span", { class: "mp-inst-sub", title: "Looking up…" }, "…");
    else if (!c) sub = el("span", { class: "mp-inst-sub", title: "No registry record found for this id (or it could not be loaded)" }, "—");
    else if (!c.names.length) sub = el("span", { class: "mp-inst-sub", title: `Registry record “${c.label}” has no location` }, "—");
    else sub = el("span", { class: "mp-inst-sub", title: c.tip }, [
      c.names.join(", "),
      c.codes ? el("span", { class: "mp-country-code" }, c.codes) : null,
    ]);
    return [name, sub];
  }

  // Published-data cell: each of the institution's models that has data in ESGF,
  // as a link to that model's EMD page with its dataset count; a total when there
  // is more than one. "…" until stage 3 finishes, "—" when there is none.
  function publishedCell(r) {
    const none = (text, title) => el("span", { class: "mp-pub-none", title }, text);
    if (r.id === UNASSIGNED) return none("—");
    if (state.type === "component") return none("—", "Published data is counted for model families; include them to see it");
    if (pub.status === "error") return none("—", `Could not load published data: ${pub.error}`);
    if (pub.status !== "done") {
      return none("…", pub.status === "waiting" ? "Waiting for the other data to finish loading" : "Reading the models’ Arrow files…");
    }
    const p = publishedFor(r, pub.byFamily);
    if (!p.models.length) return none("—", "No published ESGF data found for this institution’s models");
    return el("div", { class: "mp-pub" }, [
      ...p.models.map(m => el("a", {
        class: "mp-pub-btn", href: `${MODEL_PAGE}?model=${encodeURIComponent(m.id)}`,
        target: "_blank", rel: "noopener",
        title: `Open ${m.key} in the EMD documentation\n${m.datasets.toLocaleString()} datasets published` +
               `${m.retracted ? `; ${m.retracted.toLocaleString()} retracted (not counted)` : ""}` +
               `${m.updated ? `; last updated ${m.updated.slice(0, 10)}` : ""}`,
      }, [
        el("span", { class: "mp-pub-key" }, m.key),
        el("span", { class: "mp-pub-n" }, m.datasets.toLocaleString()),
      ])),
      p.models.length > 1 ? el("div", { class: "mp-pub-total" }, `${p.datasets.toLocaleString()} datasets`) : null,
    ]);
  }

  function render() {
    const { rows } = built[state.mode];
    const sign = state.dir === "asc" ? 1 : -1;
    const shown = typed(rows).filter(matches).sort((a, b) =>
      (a.id === UNASSIGNED) - (b.id === UNASSIGNED) || sign * SORTERS[state.sortKey](a, b));

    modeSelect.value = state.mode;
    heads.forEach(({ col, arrow, th }) => {
      const on = state.sortKey === col.key;
      th.classList.toggle("sorted", on);
      arrow.textContent = on ? (state.dir === "asc" ? " ▲" : " ▼") : "";
      if (on) th.setAttribute("aria-sort", state.dir === "asc" ? "ascending" : "descending");
      else th.removeAttribute("aria-sort");
    });
    countPill.textContent = `${shown.length} institution${shown.length === 1 ? "" : "s"}`;

    clear(tbody);
    if (!shown.length) {
      tbody.appendChild(el("tr", {}, el("td", { class: "gc-td", colspan: COLUMNS.length }, "No matches.")));
      return;
    }
    for (const r of shown) {
      tbody.appendChild(el("tr", { class: "gc-row" }, [
        el("td", { class: "gc-td gc-td-id" }, institutionCell(r)),
        el("td", { class: "gc-td" }, cell(r.components)),
        el("td", { class: "gc-td" }, cell(r.models)),
        el("td", { class: "gc-td mp-td-pub" }, publishedCell(r)),
      ]));
    }
  }

  // Stage 1 is done: show the table now, then load the rest in the background.
  render();
  const ids = built.all.rows.map(r => r.id).filter(id => id !== UNASSIGNED);
  loadAfterwards();

  async function loadAfterwards() {
    // ---- stage 2: country + ROR link ----
    await loadCountries(ids);
    render();
    const missing = ids.filter(id => countries.get(id) === null);
    const noLoc = ids.filter(id => countries.get(id) && !countries.get(id).names.length);
    if (missing.length || noLoc.length) {
      clear(countryIssues);
      countryIssues.hidden = false;
      countryIssues.appendChild(el("summary", {}, `Institutions without a country (${missing.length + noLoc.length})`));
      countryIssues.appendChild(el("ul", {}, [
        missing.length ? el("li", {}, `No registry record found: ${missing.map(i => i.toUpperCase()).join(", ")}`) : null,
        noLoc.length ? el("li", {}, `Registry record has no location: ${noLoc.map(i => i.toUpperCase()).join(", ")}`) : null,
      ]));
    }

    // ---- stage 3: published data, only once everything above has finished ----
    // Go through the models list: every model has an Arrow file named after it
    // (<validation_key>.arrow). A model with no file is simply not published yet.
    pub.status = "loading";
    setProgress(3);
    render();
    try {
      const models = await new Resolver(BASE).collection("model");
      // Load the Arrow reader only now, so it can never delay the page above.
      const { loadModelDatasets } = await import("../../../../Model_viewer/assets/model-page/js/esgf.js");

      const results = [];
      pub.checked = models.length;
      let done = 0;
      const queue = models.slice();
      const worker = async () => {
        for (let m; (m = queue.shift()); ) {
          const key = String(m.validation_key || "").trim();
          try {
            if (!key) throw new Error("no validation_key on the model record");
            const s = summariseRows(await loadModelDatasets(key, { root: ARROW_ROOT }));
            if (s.datasets) results.push({ key, id: short(m["@id"]), family: modelFamilyId(m), ...s });
          } catch (e) {
            if (!/^404\b/.test(e.message)) pub.failed.push({ key: key || short(m["@id"]), message: e.message });
          }
          setProgress(3 + 97 * (++done / models.length));
        }
      };
      await Promise.all(Array.from({ length: ARROW_CONCURRENCY }, worker));
      if (!results.length && pub.failed.length === models.length) throw new Error(pub.failed[0].message);

      const grouped = groupPublished(results);
      pub.byFamily = grouped.byFamily;
      pub.unattributed = grouped.unattributed;
      pub.published = results.length;
      pub.status = "done";
      setProgress(100);

      const total = results.reduce((n, r) => n + r.datasets, 0);
      const newest = results.map(r => r.updated).filter(Boolean).sort().pop();
      pubNote.hidden = false;
      const familiesTotal = new Set(built.all.rows.flatMap(r => r.models.map(f => f.id))).size;
      pubNote.textContent =
        `Published data is read from each model’s ESGF Arrow file (${ARROW_ROOT}/<model>.arrow): ` +
        `${pub.byFamily.size} of ${familiesTotal} model families have published data ` +
        `(${results.length} of ${models.length} models), ${total.toLocaleString()} datasets in all` +
        `${newest ? `, last updated ${newest.slice(0, 10)}` : ""}. Retracted datasets are not counted.`;

      const issues = [
        ...pub.unattributed.map(u => `${u.key} — ${u.reason}, so its data is not shown against an institution`),
        ...pub.failed.map(f => `${f.key} — could not read its Arrow file: ${f.message}`),
      ];
      if (issues.length) {
        clear(publishedIssues);
        publishedIssues.hidden = false;
        publishedIssues.appendChild(el("summary", {}, `Published data issues (${issues.length})`));
        publishedIssues.appendChild(el("ul", {}, issues.map(t => el("li", {}, t))));
      }
    } catch (e) {
      pub.status = "error";
      pub.error = e.message;
      bar.classList.add("error");
      bar.setAttribute("title", `Could not load published data: ${e.message}`);
    }
    render();
  }
}

// Fetch <universe>/organisation/<id>.json for each institution id and keep its
// country and ROR link. A missing or unreadable record is stored as null, so one
// bad id never blocks the rest.
async function loadCountries(ids) {
  const registry = new Resolver(UNIVERSE);
  await Promise.all(ids.map(async id => {
    try {
      const org = await registry.fetchDoc(ORG_FOLDER, id);
      const found = countryOf(org);
      const label = org.ui_label || id;
      const where = found.map(c => c.city).filter(Boolean).join("; ");
      countries.set(id, {
        names: [...new Set(found.map(c => c.name))],
        codes: [...new Set(found.map(c => c.code).filter(Boolean))].join(", "),
        label,
        ror: rorUrl(org.ror),
        tip: [where, `registry entry: ${label}`].filter(Boolean).join(" — "),
      });
    } catch (_) {
      countries.set(id, null);
    }
  }));
}

// The registry stores the bare ROR id ("02haar591"); accept a full URL too.
function rorUrl(v) {
  const id = String(Array.isArray(v) ? v[0] : v ?? "").trim().replace(/^https?:\/\/ror\.org\//i, "");
  return /^[0-9a-z]{9}$/i.test(id) ? `https://ror.org/${id}` : null;
}
