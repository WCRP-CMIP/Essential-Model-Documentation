// components/dataset-facets.js — frequency + variable nodes for the ESGF box.
//
// frequenciesNode: chips sorted by dataset count (descending).
// variablesNode: a centred, sized word cloud (font-size scales with the number
//   of datasets each variable appears in; count shown on each). The orchestrator
//   renders it inside a collapsed subsection.

import { el } from "../dom.js";

const countBy = (rows, key) => {
  const m = new Map();
  for (const r of rows) { const v = r[key]; if (v == null || v === "") continue; m.set(v, (m.get(v) || 0) + 1); }
  return m;
};

// Deterministic hue per frequency → each renders as a distinct GitHub-style label.
const hueFor = s => { let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0; return h % 360; };
const freqLabel = (v, n) => {
  const hue = hueFor(v);
  const style = "display:inline-flex;align-items:center;gap:.4em;padding:.14em .62em;"
    + "border-radius:4px;font-size:.72rem;font-weight:600;white-space:nowrap;"
    + `background:hsl(${hue} 70% 93%);color:hsl(${hue} 45% 30%);border:1px solid hsl(${hue} 50% 80%)`;
  return el("span", { style, title: `${v} — ${n.toLocaleString()} datasets` }, [
    el("span", {}, v),
    el("span", { style: "opacity:.6;font-weight:500;font-variant-numeric:tabular-nums" }, n.toLocaleString()),
  ]);
};

export function frequenciesNode(rows) {
  const freqs = countBy(rows, "frequency");
  if (!freqs.size) return null;
  const nodes = [...freqs.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))   // by amount, descending
    .map(([v, n]) => freqLabel(v, n));
  return el("div", { style: "display:flex;flex-wrap:wrap;gap:.4rem" }, nodes);
}

export function variablesNode(rows) {
  const vars = countBy(rows, "variable_id");
  if (!vars.size) return null;

  const entries = [...vars.entries()];
  const counts = entries.map(([, n]) => n);
  const smin = Math.sqrt(Math.min(...counts)), smax = Math.sqrt(Math.max(...counts));
  const MIN_REM = 0.62, MAX_REM = 1.2;
  const frac = n => (smax === smin ? 0.5 : (Math.sqrt(n) - smin) / (smax - smin));

  entries.sort((a, b) => a[0].localeCompare(b[0]));   // alphabetical → findable

  const cloud = el("div", {
    style: "display:flex;flex-wrap:wrap;align-items:center;justify-content:center;text-align:center;gap:.15rem .5rem;line-height:1.5",
  });
  for (const [v, n] of entries) {
    const f = frac(n);
    const fs = (MIN_REM + f * (MAX_REM - MIN_REM)).toFixed(2);
    const weight = 500 + Math.round(f * 300);
    const opacity = (0.62 + f * 0.38).toFixed(2);
    cloud.appendChild(el("span", {
      title: `${v} — ${n.toLocaleString()} dataset${n === 1 ? "" : "s"}`,
      style: `font-size:${fs}rem;font-weight:${weight};opacity:${opacity};white-space:nowrap`,
    }, [
      el("code", { style: "font-family:ui-monospace,Menlo,monospace;color:var(--ink)" }, v),
    ]));
  }
  return cloud;
}
