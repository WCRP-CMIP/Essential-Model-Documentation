// components/cumulative-chart.js — shared cumulative line + area chart.
//
// Renders a cumulative "count of datasets over time" from ESGF Arrow rows,
// keyed on any epoch-ms date field (`updated` or `start_datetime`). Short,
// basis-smoothed, lime-green to sit alongside the page. Uses the page's global
// D3 v7; degrades gracefully if it isn't present.

import { el } from "../dom.js";

const p2 = n => String(n).padStart(2, "0");
export const fmtD = d => `${d.getUTCFullYear()}-${p2(d.getUTCMonth() + 1)}-${p2(d.getUTCDate())}`;

const LINE = "#38bdf8";   // futuristic light blue line
const FILL = "#e8f6fe";   // pale blue area

// Build cumulative [{t,n}] events + summary from rows for one epoch-ms field.
export function cumulativeSeries(rows, field) {
  const dated = rows.filter(r => r[field] != null).sort((a, b) => a[field] - b[field]);
  if (!dated.length) return null;
  const events = dated.map((r, i) => ({ t: new Date(r[field]), n: i + 1 }));
  return { events, first: events[0].t, last: events[events.length - 1].t, total: events.length };
}

export function drawCumulativeChart(d3, host, events, total) {
  const first = events[0].t, last = events[events.length - 1].t;
  const W = 900, H = 208, m = { t: 12, r: 16, b: 22, l: 40 };

  const svgEl = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svgEl.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svgEl.setAttribute("width", W); svgEl.setAttribute("height", H);
  svgEl.style.width = "100%"; svgEl.style.height = "auto"; svgEl.style.display = "block";
  host.appendChild(svgEl);
  const svg = d3.select(svgEl);

  const singleInstant = +first === +last;
  const x = d3.scaleTime()
    .domain(singleInstant ? [new Date(+first - 3600000), new Date(+last + 3600000)] : [first, last])
    .range([m.l, W - m.r]);
  const y = d3.scaleLinear().domain([0, total]).nice().range([H - m.b, m.t]);
  const [yLo, yHi] = y.domain();
  const yTicks = [yLo, (yLo + yHi) / 2, yHi];

  // horizontal gridlines — one per y tick
  svg.append("g").attr("transform", `translate(${m.l},0)`)
    .call(d3.axisLeft(y).tickValues(yTicks).tickSize(-(W - m.l - m.r)).tickFormat(""))
    .call(g => { g.select(".domain").remove(); g.selectAll("line").attr("stroke", "var(--line,#d9dee7)"); });

  // Smooth, clean curve: downsample the cumulative to a handful of evenly
  // spaced control points, then draw a centripetal Catmull-Rom through them.
  // Far cleaner than tracing every step; the hover below still uses the
  // full-resolution events for an exact running total.
  const span = +last - +first;
  let curvePts;
  if (span === 0) {
    curvePts = [{ t: first, n: 0 }, { t: first, n: total }];
  } else {
    const N = 48, bisR = d3.bisector(d => d.t).right;
    curvePts = [{ t: first, n: 0 }];
    for (let i = 1; i <= N; i++) {
      const t = new Date(+first + span * i / N);
      curvePts.push({ t, n: bisR(events, t) });
    }
  }
  const curve = d3.curveCatmullRom.alpha(0.5);
  const area = d3.area().x(d => x(d.t)).y0(y(0)).y1(d => y(d.n)).curve(curve);
  const line = d3.line().x(d => x(d.t)).y(d => y(d.n)).curve(curve);
  svg.append("path").attr("d", area(curvePts)).attr("fill", FILL).attr("stroke", "none");
  svg.append("path").attr("d", line(curvePts)).attr("fill", "none")
    .attr("stroke", LINE).attr("stroke-width", 2).attr("stroke-linejoin", "round").attr("stroke-linecap", "round");

  // axes — exactly 4 date ticks and 3 count ticks
  const t0 = +first, t1 = +last;
  const xTicks = t0 === t1 ? [first] : [0, 1, 2, 3].map(i => new Date(t0 + (t1 - t0) * i / 3));
  const ax = svg.append("g").attr("transform", `translate(0,${H - m.b})`)
    .call(d3.axisBottom(x).tickValues(xTicks).tickFormat(d3.utcFormat("%b %e")).tickSizeOuter(0));
  const ay = svg.append("g").attr("transform", `translate(${m.l},0)`)
    .call(d3.axisLeft(y).tickValues(yTicks).tickFormat(d3.format("~s")));
  [ax, ay].forEach(g => {
    g.selectAll("text").attr("fill", "var(--muted,#5d6b82)").style("font-size", "10px");
    g.selectAll("path,line").attr("stroke", "var(--line-strong,#c9d2e0)");
  });

  if (singleInstant) {
    svg.append("text").attr("x", (m.l + W - m.r) / 2).attr("y", m.t + 10).attr("text-anchor", "middle")
      .attr("fill", "var(--muted,#5d6b82)").style("font-size", "10px").text("single instant");
  }

  // light hover: guide line + running-total label (no dot — the curve is smoothed)
  const guide = svg.append("line").attr("y1", m.t).attr("y2", H - m.b)
    .attr("stroke", "var(--ink,#14223a)").attr("stroke-width", 1).attr("stroke-dasharray", "3 3").attr("opacity", 0);
  const label = svg.append("text").attr("x", m.l + 2).attr("y", 2).attr("dominant-baseline", "hanging")
    .attr("fill", "var(--ink,#14223a)").style("font-size", "10.5px").style("font-weight", "600").attr("opacity", 0);
  const bisect = d3.bisector(d => d.t).right;

  svg.append("rect").attr("x", m.l).attr("y", m.t).attr("width", W - m.l - m.r).attr("height", H - m.t - m.b)
    .attr("fill", "transparent")
    .on("mousemove", event => {
      const px = d3.pointer(event)[0];
      const date = x.invert(px);
      const n = bisect(events, date);
      const cx = Math.max(m.l, Math.min(W - m.r, px));
      guide.attr("x1", cx).attr("x2", cx).attr("opacity", 0.4);
      label.attr("opacity", 1).text(`${fmtD(date)} · ${n.toLocaleString()}`);
    })
    .on("mouseleave", () => { guide.attr("opacity", 0); label.attr("opacity", 0); });
}

// Padded chart node, for use as a subsection.
export function cumulativeChartNode(rows, field) {
  const s = cumulativeSeries(rows, field);
  if (!s) return null;
  const host = el("div", { class: "subs-chart", style: "padding:0 16.6667%" });
  const d3 = window.d3;
  if (!d3) host.appendChild(el("p", { class: "card-sub" }, "D3 v7 required for the chart."));
  else drawCumulativeChart(d3, host, s.events, s.total);
  return host;
}
