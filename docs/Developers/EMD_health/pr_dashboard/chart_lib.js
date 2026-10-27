/* ================================================================
   pr_dashboard/chart_lib.js
   Shared library + PRChart template used by each section.
   Loaded once — exposes window.PRLib and window.PRChart.
   ================================================================ */
(function (global) {

  // ---------- constants ----------
  const MS_PER_DAY  = 1000 * 60 * 60 * 24;
  const MS_PER_HOUR = 1000 * 60 * 60;

  // Canonical CMIP entity categories (used only when a chart wants
  // to breakdown by category — the emd-submission filter is orthogonal).
  const CATEGORY_DEFS = [
    { name: 'Horizontal Grid Cell',           re: /horizontal[\s_-]*grid[\s_-]*cell/i,          color: '#4E79A7' },
    { name: 'Horizontal Computational Grid',  re: /horizontal[\s_-]*computational/i,            color: '#F28E2B' },
    { name: 'Vertical Computational Grid',    re: /vertical[\s_-]*computational/i,              color: '#59A14F' },
    { name: 'Model Family',                   re: /(?:model|earth[\s_-]*system[\s_-]*model)[\s_-]*famil/i, color: '#E15759' },
    { name: 'Model Component',                re: /model[\s_-]*component/i,                     color: '#B07AA1' },
    { name: 'Model',                          re: /\bmodel\b/i,                                  color: '#76B7B2' },
  ];
  function categorize(title) {
    for (const c of CATEGORY_DEFS) if (c.re.test(title || "")) return c.name;
    return null;
  }

  // ---------- bot detection ----------
  function isBot(actor) {
    if (!actor) return true;
    const a = actor.toLowerCase();
    return a.endsWith('[bot]') || a === 'github-actions' || a.startsWith('copilot');
  }

  // ---------- filter ----------
  // Change this predicate to broaden/narrow the cohort.
  // The user asked for `emd-submission`-tagged PRs. To broaden to any PR that
  // touched the EMD workflow, return true if the PR has ANY of the workflow
  // labels: emd-submission, changes-requested, approved, changes-made,
  // reviewer-comment, pull_req.
  const EMD_SUBMISSION_LABEL = "emd-submission";
  function hasEmdSubmissionLabel(pr) {
    return (pr.labels || []).indexOf(EMD_SUBMISSION_LABEL) !== -1;
  }
  // Optional broader filter — swap in if the strict tag yields too few PRs.
  const WORKFLOW_LABELS = new Set([
    "emd-submission", "changes-requested", "approved",
    "changes-made", "reviewer-comment", "pull_req"
  ]);
  function hasAnyWorkflowLabel(pr) {
    return (pr.labels || []).some(l => WORKFLOW_LABELS.has(l));
  }

  // ---------- smoothing ----------
  function smoothSeries(series, radiusDays, keys) {
    keys = keys || ['p05','p10','p25','median','p75','p90','p95','n'];
    if (!radiusDays || series.length < 2) return series;
    const rMs = radiusDays * MS_PER_DAY;
    return series.map(pt => {
      const t = pt.date.getTime();
      const win = series.filter(p => Math.abs(p.date.getTime() - t) <= rMs);
      const out = { date: pt.date };
      for (const k of keys) out[k] = d3.mean(win, d => d[k]);
      return out;
    });
  }

  // ---------- quantile stats ----------
  // The caller is responsible for applying a minSamples floor to `values`.
  // This routine works for n ≥ 1: d3.quantile handles single-element and
  // two-element arrays (all quantiles collapse to the value when n=1;
  // two-element arrays interpolate linearly).
  function windowStatsFrom(values, targetDate) {
    if (!values || !values.length) return null;
    values.sort((a, b) => a - b);
    return {
      date: targetDate, n: values.length,
      p05: d3.quantile(values, 0.05),
      p10: d3.quantile(values, 0.10),
      p25: d3.quantile(values, 0.25),
      median: d3.quantile(values, 0.50),
      p75: d3.quantile(values, 0.75),
      p90: d3.quantile(values, 0.90),
      p95: d3.quantile(values, 0.95),
    };
  }

  // ---------- helpers ----------
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, ch => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[ch]));
  }
  function fmtNum(v) {
    if (v == null || isNaN(v)) return "—";
    const a = Math.abs(v);
    if (a >= 100) return d3.format(".0f")(v);
    if (a >= 10)  return d3.format(".1f")(v);
    return d3.format(".2~f")(v);
  }
  function debounce(fn, wait) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), wait); }; }

  global.PRLib = {
    MS_PER_DAY, MS_PER_HOUR,
    CATEGORY_DEFS, categorize,
    isBot,
    EMD_SUBMISSION_LABEL,
    hasEmdSubmissionLabel, hasAnyWorkflowLabel, WORKFLOW_LABELS,
    smoothSeries, windowStatsFrom,
    escapeHtml, fmtNum, debounce,
  };

  // ================================================================
  // PRChart — base template.
  //
  // Each section (First Response / Change Reply / Throughput) is a
  // PRChart instance. The subclass supplies computeSeries() and
  // series-specific labels; everything else — DOM scaffolding, axes,
  // band+line drawing, tooltip, crosshair, chart key — comes from here.
  //
  // Usage:
  //     const chart = new PRChart({
  //       container,             // parent DOM element
  //       title, caption,        // panel header
  //       leftAxisLabel,         // for the primary Y axis
  //       rightAxisLabel,        // optional; if provided, secondary line uses right axis
  //       primaryColor,          // primary line + band color (default blue)
  //       hasSecondary,          // does this chart have a right-axis secondary line?
  //       secondaryLabel,        // key label for the right-axis line
  //       tooltipRows,           // function(nearestPrimary, nearestSecondary, opts) => html
  //       computeSeries,         // function(prs, events, opts) => { primary, secondary, xDomain }
  //     });
  //     chart.update(prs, events, opts);
  // ================================================================
  class PRChart {
    constructor(cfg) {
      this.cfg = cfg;
      this._buildScaffold();
    }

    _buildScaffold() {
      const c = this.cfg;
      const host = c.container;
      host.innerHTML = "";
      host.classList.add("prd-section");

      // ---------- Section-level header: h2 title + intro paragraph ----------
      const secHead = document.createElement("div");
      secHead.className = "prd-section-header";
      const h = document.createElement("h2");
      h.textContent = c.title;
      secHead.appendChild(h);
      if (c.intro) {
        const p = document.createElement("p");
        p.className = "prd-section-intro";
        p.innerHTML = c.intro;
        secHead.appendChild(p);
      }
      host.appendChild(secHead);

      // ---------- Per-section summary strip (populated by _renderSummary) ----------
      // Rendered above the controls so it reads as an extension of the header.
      if (c.summaryStats) {
        const summary = document.createElement("div");
        summary.className = "prd-section-summary";
        host.appendChild(summary);
        this.summaryEl = summary;
      }

      // ---------- Per-section controls strip ----------
      // Initialises this._opts with each control's initial value.
      this._opts = {};
      if (c.controls && c.controls.length) {
        const ctrlHost = document.createElement("div");
        ctrlHost.className = "prd-controls";
        host.appendChild(ctrlHost);
        this._buildControls(ctrlHost, c.controls);
      }
      // Merge in any config defaults (e.g. minSamples that isn't a control).
      if (c.defaults) Object.assign(this._opts, c.defaults);

      // ---------- Main-chart panel ----------
      const panel = document.createElement("div");
      panel.className = "prd-panel";
      host.appendChild(panel);
      this.panelEl = panel;

      const cap = document.createElement("p");
      cap.className = "prd-panel-caption";
      cap.textContent = c.caption || "";
      panel.appendChild(cap);
      this.captionEl = cap;

      const status = document.createElement("div");
      status.className = "prd-status";
      status.textContent = "Loading…";
      panel.appendChild(status);
      this.statusEl = status;

      const svg = d3.create("svg").attr("class", "prd-main").style("display", "none");
      panel.appendChild(svg.node());
      this.svg = svg;

      const key = document.createElement("div");
      key.className = "prd-key";
      panel.appendChild(key);
      this.keyEl = key;

      const tt = document.createElement("div");
      tt.className = "prd-tooltip";
      panel.appendChild(tt);
      this.tooltipEl = tt;

      // ---------- Small-multiples section (below the panel) ----------
      if (c.hasSmallMultiples) {
        const smHead = document.createElement("div");
        smHead.className = "prd-sm-section-header";
        smHead.innerHTML =
          `<h3>${c.smallMultiplesTitle || "Per-category detail"}</h3>` +
          `<span>${c.smallMultiplesSub || "shared axes with main"}</span>`;
        host.appendChild(smHead);

        const smGrid = document.createElement("div");
        smGrid.className = "prd-small-multiples";
        host.appendChild(smGrid);
        this.smGridEl = smGrid;
      }
    }

    /**
     * Build the segmented-button controls declared in cfg.controls.
     * Each descriptor:
     *   { key, label, cast?, options: [{val, label, active?}] }
     * Initial active option per control:
     *   1. cfg.initialOpts[key] wins if it matches one of the option `val`s
     *   2. otherwise the option flagged {active: true}
     *   3. otherwise the first option
     * The chosen value goes into this._opts[key]; clicking a different
     * button updates this._opts and calls this._rerender().
     */
    _buildControls(host, controls) {
      const initial = this.cfg.initialOpts || {};
      const casters = { num: v => +v };
      for (const ctrl of controls) {
        const wrapper = document.createElement("div");
        wrapper.className = "prd-ctrl";
        const label = document.createElement("label");
        label.textContent = ctrl.label;
        wrapper.appendChild(label);

        const seg = document.createElement("div");
        seg.className = "prd-seg";
        const castFn = casters[ctrl.cast] || null;

        // Resolve the initial option
        let initialOpt = null;
        if (initial[ctrl.key] !== undefined) {
          const wanted = String(initial[ctrl.key]);
          initialOpt = ctrl.options.find(o => String(o.val) === wanted) || null;
        }
        if (!initialOpt) initialOpt = ctrl.options.find(o => o.active) || ctrl.options[0];
        this._opts[ctrl.key] = castFn ? castFn(initialOpt.val) : initialOpt.val;

        for (const opt of ctrl.options) {
          const btn = document.createElement("button");
          btn.textContent = opt.label;
          if (opt === initialOpt) btn.classList.add("active");
          btn.addEventListener("click", () => {
            seg.querySelectorAll("button").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            this._opts[ctrl.key] = castFn ? castFn(opt.val) : opt.val;
            this._rerender();
          });
          seg.appendChild(btn);
        }
        wrapper.appendChild(seg);
        host.appendChild(wrapper);
      }

      // Any keys in initialOpts that DON'T correspond to a control (e.g.
      // minSamples) are copied straight onto _opts so computeSeries sees them.
      const controlKeys = new Set(controls.map(c => c.key));
      for (const [k, v] of Object.entries(initial)) {
        if (!controlKeys.has(k)) this._opts[k] = v;
      }
    }

    _rerender() {
      if (!this._prs) return;
      this.update(this._prs, this._events, {});   // opts already stored
    }

    /**
     * Resolve a cfg field that can be either a static value or an
     * (opts) => value function. Used for anything that changes with the
     * current opts (e.g. axis labels + unit suffix when a unit toggle
     * is present).
     */
    _txt(field, opts) {
      const v = this.cfg[field];
      return typeof v === "function" ? v(opts || this._opts || {}) : v;
    }

    /**
     * Populate the per-section summary strip.
     * cfg.summaryStats(prs, events, opts, series) → array of
     *   { label, value, sub, valueStyle? } objects.
     * Called on every update (after series is computed).
     */
    _renderSummary(series, opts) {
      if (!this.summaryEl || !this.cfg.summaryStats) return;
      let stats;
      try {
        stats = this.cfg.summaryStats.call(
          this, this._prs, this._events, opts, series
        );
      } catch (e) {
        console.error("summaryStats failed:", e);
        this.summaryEl.innerHTML = "";
        return;
      }
      if (!stats || !stats.length) {
        this.summaryEl.innerHTML = "";
        return;
      }
      this.summaryEl.innerHTML = stats.map(s => `
        <div class="prd-stat">
          <div class="prd-stat-label">${s.label}</div>
          <div class="prd-stat-value"${s.valueStyle ? ` style="${s.valueStyle}"` : ""}>${s.value}</div>
          <div class="prd-stat-sub">${s.sub || ""}</div>
        </div>
      `).join("");
    }

    setStatus(text, isError) {
      this.statusEl.textContent = text;
      this.statusEl.style.display = "block";
      this.statusEl.classList.toggle("error", !!isError);
      this.svg.style("display", "none");
    }

    update(prs, events, opts) {
      const cfg = this.cfg;

      // Cache latest data so control-triggered re-renders don't need it re-passed.
      this._prs = prs;
      this._events = events;
      // Merge any externally-provided opts on top of the internal state.
      if (opts) Object.assign(this._opts, opts);
      const useOpts = this._opts;
      // Track band for the chart key.
      if (useOpts.band) this._lastBand = useOpts.band;

      let series;
      try {
        series = cfg.computeSeries.call(cfg, prs, events, useOpts);
      } catch (e) {
        console.error(e);
        this.setStatus("Error computing series: " + e.message, true);
        return;
      }
      if (!series || !series.primary || !series.primary.length) {
        this.setStatus("No data for this chart with the current settings.", false);
        this._renderKey(null);
        this._renderSummary(null, useOpts);
        if (this.smGridEl) this.smGridEl.innerHTML = "";
        return;
      }
      this.statusEl.style.display = "none";
      this.svg.style("display", "block");
      this._renderMain(series, useOpts);
      this._renderKey(series);
      this._renderSummary(series, useOpts);
      if (this.cfg.hasSmallMultiples) this._renderSmallMultiples(series, useOpts);
    }

    _renderMain(series, opts) {
      const cfg = this.cfg;
      const svg = this.svg;
      svg.selectAll("*").remove();

      const containerWidth = cfg.container.clientWidth - 32;
      const width  = Math.max(320, containerWidth);
      const height = 400;
      const useRight = cfg.hasSecondary && series.secondary && series.secondary.length;
      const margin = { top: 14, right: useRight ? 60 : 22, bottom: 40, left: 60 };
      const innerW = width - margin.left - margin.right;
      const innerH = height - margin.top - margin.bottom;

      svg.attr("width", width).attr("height", height).attr("viewBox", `0 0 ${width} ${height}`);
      const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

      // scales
      const x = d3.scaleTime().domain(series.xDomain).range([0, innerW]);

      const bandKey = opts.band || "iqr";
      const [lo, hi] = ({ iqr: ["p25","p75"], p10: ["p10","p90"], p05: ["p05","p95"] })[bandKey];
      const yTop = d3.max(series.primary, p => p[hi] || p.median || 0) * 1.08 || 1;
      const yLog = opts.scale === "log";
      const yDom = yLog ? [Math.max(0.01, yTop * 0.001), yTop] : [0, yTop];
      const y = (yLog ? d3.scaleLog() : d3.scaleLinear())
        .domain(yDom).range([innerH, 0]).clamp(true);

      const yRightMax = useRight ? (d3.max(series.secondary, p => p.count) || 1) * 1.1 : 1;
      const yRight = useRight
        ? (yLog ? d3.scaleLog().domain([0.5, yRightMax]) : d3.scaleLinear().domain([0, yRightMax]))
            .range([innerH, 0]).nice()
        : null;

      // grid + axes
      g.append("g").attr("class", "prd-grid")
        .call(d3.axisLeft(y).ticks(6).tickSize(-innerW).tickFormat(""));
      g.append("g").attr("class", "prd-axis")
        .attr("transform", `translate(0,${innerH})`)
        .call(d3.axisBottom(x).ticks(Math.min(10, Math.floor(innerW / 90))).tickSizeOuter(0));
      g.append("g").attr("class", "prd-axis")
        .call(d3.axisLeft(y).ticks(6).tickFormat(PRLib.fmtNum))
        .append("text").attr("class", "prd-axis-label")
          .attr("transform", "rotate(-90)").attr("x", -innerH/2).attr("y", -46).attr("text-anchor", "middle")
          .text(this._txt("leftAxisLabel", opts));

      if (useRight) {
        g.append("g").attr("class", "prd-axis prd-axis-right")
          .attr("transform", `translate(${innerW},0)`)
          .call(d3.axisRight(yRight).ticks(6).tickFormat(d3.format("d")))
          .append("text").attr("class", "prd-axis-label")
            .attr("transform", "rotate(-90)").attr("x", -innerH/2).attr("y", 42).attr("text-anchor", "middle")
            .attr("fill", "#7c3aed")
            .text(this._txt("rightAxisLabel", opts));
      }

      // draw band + median (primary)
      const yFloor = yLog ? Math.max(0.01, yTop * 0.001) : 0;
      const yOf = v => y(Math.max(v, yFloor));
      const area = d3.area()
        .x(d => x(d.date))
        .y0(d => yOf(d[lo]))
        .y1(d => yOf(d[hi]))
        .curve(d3.curveBasis)
        .defined(d => d[lo] != null && d[hi] != null);
      const line = d3.line()
        .x(d => x(d.date))
        .y(d => yOf(d.median))
        .curve(d3.curveBasis)
        .defined(d => d.median != null);

      const color = cfg.primaryColor || "#1976d2";
      if (series.primary.some(p => p[lo] != null && p[hi] != null)) {
        g.append("path").datum(series.primary)
          .attr("class", "prd-band")
          .attr("fill", color)
          .attr("d", area);
      }
      g.append("path").datum(series.primary)
        .attr("class", "prd-median-line")
        .attr("stroke", color)
        .attr("d", line);

      // secondary (right axis) — dashed purple line
      if (useRight) {
        const yROf = v => yRight(yLog ? Math.max(0.5, v) : v);
        const secondaryLine = d3.line()
          .x(d => x(d.date))
          .y(d => yROf(d.count))
          .curve(d3.curveBasis)
          .defined(d => d.count != null);
        g.append("path").datum(series.secondary)
          .attr("class", "prd-pending-line")
          .attr("d", secondaryLine);
      }

      // Optional additional series (e.g. throughput's second on-left-axis dotted line)
      if (series.extra) {
        const extraLine = d3.line()
          .x(d => x(d.date))
          .y(d => yOf(d.value))
          .curve(d3.curveBasis)
          .defined(d => d.value != null);
        g.append("path").datum(series.extra.data)
          .attr("class", series.extra.className || "prd-secondary-line")
          .attr("stroke", series.extra.stroke || null)
          .attr("d", extraLine);
      }

      // crosshair + tooltip
      const crosshair = g.append("line").attr("class", "prd-crosshair")
        .attr("y1", 0).attr("y2", innerH).style("opacity", 0);
      const focus = g.append("g");
      const tip = d3.select(this.tooltipEl);

      const bisect = d3.bisector(d => d.date).left;
      const nearestOf = (arr, t) => {
        if (!arr || !arr.length) return null;
        const idx = bisect(arr, t);
        const cand = [arr[idx-1], arr[idx]].filter(Boolean);
        if (!cand.length) return null;
        return cand.reduce((a, b) => Math.abs(b.date - t) < Math.abs(a.date - t) ? b : a);
      };

      g.append("rect")
        .attr("width", innerW).attr("height", innerH).attr("fill", "transparent")
        .on("mouseenter", () => { crosshair.style("opacity", 1); tip.style("opacity", 1); })
        .on("mouseleave", () => { crosshair.style("opacity", 0); tip.style("opacity", 0); focus.selectAll("*").remove(); })
        .on("mousemove", (event) => {
          const [mx] = d3.pointer(event, event.currentTarget);
          const date = x.invert(mx);
          crosshair.attr("x1", mx).attr("x2", mx);
          focus.selectAll("*").remove();

          const nP = nearestOf(series.primary, date);
          const nS = useRight ? nearestOf(series.secondary, date) : null;
          if (nP) {
            focus.append("circle")
              .attr("cx", x(nP.date)).attr("cy", yOf(nP.median))
              .attr("r", 3.5).attr("fill", color).attr("stroke", "white").attr("stroke-width", 1.4);
          }

          const rect = cfg.container.getBoundingClientRect();
          tip.style("left", (event.clientX - rect.left + 14) + "px")
             .style("top",  (event.clientY - rect.top + 8) + "px");

          const html = cfg.tooltipRows
            ? cfg.tooltipRows(nP, nS, opts)
            : PRChart.defaultTooltip(nP, nS, opts, color, cfg);
          tip.html(html);
        });
    }

    _renderSmallMultiples(series, opts) {
      if (!this.smGridEl) return;
      const cfg = this.cfg;
      const cats = series.smallMultiples || [];
      this.smGridEl.innerHTML = "";
      if (!cats.length) {
        this.smGridEl.innerHTML =
          `<div class="prd-sm-empty">No canonical categories with data.</div>`;
        return;
      }

      // Match PR_First_Response's geometry approach: compute card width from
      // the actual grid layout, size the SVG's viewBox to the card's inner
      // width, and let default `preserveAspectRatio="xMidYMid meet"` scale it.
      const hostRect = this.smGridEl.getBoundingClientRect();
      const cs = getComputedStyle(this.smGridEl);
      const gridCols = (cs.gridTemplateColumns || "").split(" ").length || 3;
      const gap = 12;                              // .75rem = 12px between cards
      const cardWidth = (hostRect.width - (gridCols - 1) * gap) / gridCols;
      const chartHeight = 140;
      const margin = { top: 6, right: 8, bottom: 22, left: 32 };
      // Card padding: .55rem .7rem = ~11 + 11 = ~22px + 2px border = 24px
      const innerW = Math.max(60, cardWidth - 24 - margin.left - margin.right);
      const innerH = chartHeight - margin.top - margin.bottom;
      const vbW = innerW + margin.left + margin.right;
      const vbH = chartHeight;

      // Shared scales — same domain + scale type as the main chart.
      const x = d3.scaleTime().domain(series.xDomain).range([0, innerW]);
      const bandKey = opts.band || "iqr";
      const [lo, hi] = ({ iqr: ["p25","p75"], p10: ["p10","p90"], p05: ["p05","p95"] })[bandKey];
      const yTop = d3.max(series.primary, p => p[hi] || p.median || 0) * 1.08 || 1;
      const yLog = opts.scale === "log";
      const yDom = yLog ? [Math.max(0.01, yTop * 0.001), yTop] : [0, yTop];
      const y = (yLog ? d3.scaleLog() : d3.scaleLinear())
        .domain(yDom).range([innerH, 0]).clamp(true);
      const yFloor = yLog ? Math.max(0.01, yTop * 0.001) : 0;
      const yOf = v => y(Math.max(v, yFloor));

      const tickFmt = d3.timeFormat("%b '%y");
      const area = d3.area()
        .x(d => x(d.date))
        .y0(d => yOf(d[lo]))
        .y1(d => yOf(d[hi]))
        .curve(d3.curveBasis)
        .defined(d => d[lo] != null && d[hi] != null);
      const line = d3.line()
        .x(d => x(d.date))
        .y(d => yOf(d.median))
        .curve(d3.curveBasis)
        .defined(d => d.median != null);

      for (const cat of cats) {
        const card = document.createElement("div");
        card.className = "prd-sm-card";
        card.innerHTML =
          `<div class="prd-sm-card-header">
             <div class="prd-sm-title">
               <span class="prd-sm-swatch" style="background:${cat.color}"></span>
               <span title="${PRLib.escapeHtml(cat.name)}">${PRLib.escapeHtml(cat.name)}</span>
             </div>
             <div class="prd-sm-count">${cat.count} PR${cat.count === 1 ? "" : "s"}</div>
           </div>`;

        const svg = d3.create("svg")
          .attr("class", "prd-sm-svg")
          .attr("viewBox", `0 0 ${vbW} ${vbH}`);
        const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

        g.append("g").attr("class", "prd-grid")
          .call(d3.axisLeft(y).ticks(3).tickSize(-innerW).tickFormat(""));
        g.append("g").attr("class", "prd-axis")
          .attr("transform", `translate(0,${innerH})`)
          .call(d3.axisBottom(x).ticks(3).tickFormat(tickFmt).tickSizeOuter(0));
        g.append("g").attr("class", "prd-axis")
          .call(d3.axisLeft(y).ticks(3).tickFormat(PRLib.fmtNum));

        // Band + median in category color
        if (cfg.showBand !== false && cat.primary && cat.primary.length) {
          g.append("path").datum(cat.primary)
            .attr("class", "prd-band")
            .attr("fill", cat.color)
            .attr("d", area);
        }
        if (cat.primary && cat.primary.length) {
          g.append("path").datum(cat.primary)
            .attr("class", "prd-median-line")
            .attr("stroke", cat.color)
            .attr("d", line);
        }

        // Extra series (throughput's submitted dotted line)
        if (cat.extra) {
          const extraLine = d3.line()
            .x(d => x(d.date))
            .y(d => yOf(d.value))
            .curve(d3.curveBasis)
            .defined(d => d.value != null);
          g.append("path").datum(cat.extra.data)
            .attr("class", cat.extra.className || "prd-secondary-line")
            .attr("stroke", cat.extra.stroke || null)
            .attr("d", extraLine);
        }

        card.appendChild(svg.node());
        this.smGridEl.appendChild(card);
      }
    }

    _renderKey(series) {
      const cfg = this.cfg;
      const bLabel = ({ iqr: "25–75", p10: "10–90", p05: "5–95" })[this._lastBand || "iqr"];
      const parts = [];
      const color = cfg.primaryColor || "#1976d2";
      if (cfg.showBand !== false) {
        parts.push(`
          <span class="prd-key-item">
            <svg width="22" height="8"><line x1="0" y1="4" x2="22" y2="4" stroke="${color}" stroke-width="2"/></svg>
            ${cfg.primaryKeyLabel || "Median"}
          </span>
          <span class="prd-key-item">
            <svg width="22" height="10"><rect width="22" height="10" fill="${color}" opacity="0.17" rx="1"/></svg>
            Percentile band
          </span>`);
      } else {
        parts.push(`
          <span class="prd-key-item">
            <svg width="22" height="8"><line x1="0" y1="4" x2="22" y2="4" stroke="${color}" stroke-width="2"/></svg>
            ${cfg.primaryKeyLabel || "Primary"}
          </span>`);
      }
      if (cfg.extraKey) parts.push(cfg.extraKey());
      if (cfg.hasSecondary) parts.push(`
        <span class="prd-key-item">
          <svg width="22" height="8"><line x1="0" y1="4" x2="22" y2="4" stroke="#7c3aed" stroke-width="2" stroke-dasharray="4 3"/></svg>
          ${cfg.secondaryLabel || "Secondary (right axis)"}
        </span>`);
      this.keyEl.innerHTML = parts.join("");
    }

    setBand(band) { this._lastBand = band; }

    static defaultTooltip(nP, nS, opts, color, cfg) {
      if (!nP) return "";
      const fmtDate = d3.timeFormat("%b %d, %Y");
      const bLabel = ({ iqr: "25–75", p10: "10–90", p05: "5–95" })[opts.band || "iqr"];
      const [lo, hi] = ({ iqr: ["p25","p75"], p10: ["p10","p90"], p05: ["p05","p95"] })[opts.band || "iqr"];
      // Resolve unitSuffix if it's a (opts) => string function.
      const unit = typeof cfg.unitSuffix === "function" ? cfg.unitSuffix(opts) : (cfg.unitSuffix || "");
      let h = `<div class="tt-date">${fmtDate(nP.date)}</div>`;
      h += `<div class="tt-row">
        <span class="tt-swatch" style="background:${color}"></span>
        <span class="tt-name">${cfg.primaryKeyLabel || "Median"}</span>
        <span class="tt-stats">${PRLib.fmtNum(nP.median)}${unit}</span>
      </div>`;
      if (nP[lo] != null && nP[hi] != null) {
        h += `<div class="tt-row" style="color:#94a3b8">
          <span class="tt-name" style="padding-left:14px">${bLabel} band</span>
          <span class="tt-stats">${PRLib.fmtNum(nP[lo])}–${PRLib.fmtNum(nP[hi])}${unit}</span>
        </div>`;
      }
      if (nP.n != null) {
        h += `<div class="tt-row" style="color:#94a3b8">
          <span class="tt-name" style="padding-left:14px">Samples</span>
          <span class="tt-stats">n=${Math.round(nP.n)}</span>
        </div>`;
      }
      if (nS) {
        h += `<div class="tt-row" style="margin-top:.35rem">
          <span class="tt-swatch" style="background:#7c3aed"></span>
          <span class="tt-name">${cfg.secondaryLabel || "Secondary"}</span>
          <span class="tt-stats">${nS.count}</span>
        </div>`;
      }
      return h;
    }
  }

  global.PRChart = PRChart;

})(window);
