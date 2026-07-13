/* ================================================================
   pr_dashboard/throughput.js
   Totals: PRs closed vs submitted in a rolling window.

   Both counts share the primary (left) Y axis — no right axis, no
   percentile band. Uses the PRChart template with:
     showBand: false      → primary line only (blue, closed count)
     extra                → amber-dotted line on same axis (submitted)
     hasSecondary: false  → no right axis
     hasSmallMultiples: true → per-category closed + submitted panels

   The `primary` series is shaped like a stats series (median/p25/p75
   all equal to the count) so the shared drawing code renders it as a
   single line and computes yTop from it.
   ================================================================ */
(function (global) {
  const { MS_PER_DAY, smoothSeries } = PRLib;

  function countInWindow(items, targetDate, key, halfWin) {
    const start = targetDate.getTime() - halfWin * MS_PER_DAY;
    const end   = targetDate.getTime() + halfWin * MS_PER_DAY;
    let n = 0;
    for (const it of items) {
      const d = it[key];
      if (!d) continue;
      const t = d.getTime();
      if (t >= start && t <= end) n++;
    }
    return n;
  }

  function smoothCount(series, radiusDays, keys) {
    if (!radiusDays || series.length < 2) return series;
    keys = keys || ['count', 'value'];
    const rMs = radiusDays * MS_PER_DAY;
    return series.map(pt => {
      const t = pt.date.getTime();
      const win = series.filter(p => Math.abs(p.date.getTime() - t) <= rMs);
      const out = { date: pt.date };
      for (const k of keys) if (pt[k] != null) out[k] = d3.mean(win, d => d[k]);
      return out;
    });
  }

  function buildRecords(prs) {
    return prs.map(pr => {
      const opened = pr.created_at ? new Date(pr.created_at) : null;
      if (!opened || isNaN(opened)) return null;
      const terminalDate = pr.merged_at ? new Date(pr.merged_at)
                          : pr.closed_at ? new Date(pr.closed_at) : null;
      return {
        opened,
        terminalDate,
        category: PRLib.categorize(pr.title || ""),
      };
    }).filter(Boolean);
  }

  /**
   * Compute {primary, extra} for a given set of records on a shared x-domain.
   * primary = closed count per window (shaped as stats); extra.data =
   * submitted count per window (as {date, value}).
   */
  function computeFor(records, opts, xDomain) {
    const halfWin = opts.halfWindowDays;
    const smoothR = opts.smoothingRadiusDays;

    const days = d3.timeDays(
      d3.timeDay.floor(xDomain[0]),
      d3.timeDay.offset(d3.timeDay.ceil(xDomain[1]), 1)
    );

    const rawClosed = days.map(d => ({
      date: d,
      count: countInWindow(records, d, "terminalDate", halfWin),
    }));
    const closed = smoothCount(rawClosed, smoothR, ['count']);

    const rawSubmitted = days.map(d => ({
      date: d,
      value: countInWindow(records, d, "opened", halfWin),
    }));
    const submitted = smoothCount(rawSubmitted, smoothR, ['value']);

    const primary = closed.map(p => ({
      date: p.date,
      n: p.count,
      median: p.count,
      p05: p.count, p10: p.count, p25: p.count,
      p75: p.count, p90: p.count, p95: p.count,
    }));

    return {
      primary,
      extra: {
        data: submitted,
        className: "prd-secondary-line",
      },
    };
  }

  function computeSeries(prs, events, opts) {
    const records = buildRecords(prs);
    if (!records.length) return null;

    const allDates = [];
    for (const r of records) {
      allDates.push(r.opened);
      if (r.terminalDate) allDates.push(r.terminalDate);
    }
    const [minD, maxD] = d3.extent(allDates);
    const xDomain = [minD, maxD];

    const main = computeFor(records, opts, xDomain);

    // Stash the submitted series so tooltipRows can look up nearest points.
    this._lastSubmitted = main.extra.data;

    // Per-category small multiples
    const smallMultiples = [];
    for (const catDef of PRLib.CATEGORY_DEFS) {
      const catRecs = records.filter(r => r.category === catDef.name);
      if (!catRecs.length) continue;
      const catSeries = computeFor(catRecs, opts, xDomain);
      smallMultiples.push({
        name: catDef.name,
        color: catDef.color,
        count: catRecs.length,
        primary: catSeries.primary,
        extra: catSeries.extra,
      });
    }

    return {
      ...main, xDomain, smallMultiples,
      _closedTotal: records.filter(r => r.terminalDate).length,
      _submittedTotal: records.length,
    };
  }

  /**
   * Summary cards for the Throughput section.
   * Values come from the latest points of the smoothed primary/extra
   * series, so they reflect the currently-selected window.
   */
  function summaryStats(prs, events, opts, series) {
    const s = (this.cfg && this.cfg.summary) || {};
    const closedTot = series ? series._closedTotal : 0;
    const submTot   = series ? series._submittedTotal : 0;

    // "Recent" = mean of last 14 window points on each line.
    let recentClosed = "—", recentSubmitted = "—", net = "—";
    if (series && series.primary && series.primary.length) {
      const lastP = series.primary.slice(-14);
      const c = d3.mean(lastP, p => p.median);
      if (c != null && isFinite(c)) recentClosed = PRLib.fmtNum(c);
    }
    if (series && series.extra && series.extra.data && series.extra.data.length) {
      const lastE = series.extra.data.slice(-14);
      const v = d3.mean(lastE, p => p.value);
      if (v != null && isFinite(v)) recentSubmitted = PRLib.fmtNum(v);
    }
    if (recentClosed !== "—" && recentSubmitted !== "—") {
      const delta = parseFloat(recentSubmitted) - parseFloat(recentClosed);
      net = (delta > 0 ? "+" : "") + PRLib.fmtNum(delta);
    }

    return [
      {
        label: (s.closed && s.closed.label)  || "Closed (recent avg)",
        value: recentClosed,
        sub:   (s.closed && s.closed.sub)    || `avg per ±${opts.halfWindowDays}d window`,
      },
      {
        label: (s.submitted && s.submitted.label) || "Submitted (recent avg)",
        value: recentSubmitted,
        sub:   (s.submitted && s.submitted.sub)   || `avg per ±${opts.halfWindowDays}d window`,
        valueStyle: "color:#f59e0b",
      },
      {
        label: (s.net && s.net.label) || "Backlog delta",
        value: net,
        sub:   (s.net && s.net.sub)   || "submitted − closed (recent)",
        valueStyle: net.startsWith("+") ? "color:#ef4444" : (net.startsWith("−") || net.startsWith("-") ? "color:#059669" : ""),
      },
      {
        label: (s.total && s.total.label) || "All-time totals",
        value: `${closedTot}<span class="u" style="font-size:.7em;color:var(--emd-text-tertiary)"> / ${submTot}</span>`,
        sub:   (s.total && s.total.sub)   || "closed / submitted",
        valueStyle: "font-size:1.05rem",
      },
    ];
  }

  global.ThroughputChart = {
    create(container, text) {
      const t = text || {};
      return new PRChart({
        container,
        title:               t.title               || "Throughput — totals",
        intro:               t.intro               || "",
        caption:             t.caption             || "Rolling count of PRs closed (merged or closed-without-merge) and submitted per window.",
        leftAxisLabel:       t.leftAxisLabel       || "PRs per window",
        primaryColor:        "#1976d2",
        primaryKeyLabel:     t.primaryKeyLabel     || "Closed",
        showBand:            false,
        hasSecondary:        false,
        hasSmallMultiples:   true,
        smallMultiplesTitle: t.smallMultiplesTitle || "Per-category throughput",
        smallMultiplesSub:   t.smallMultiplesSub   || "closed (line) vs submitted (dotted) · shared axes",
        initialOpts:         t.data || {},   // ← user-editable overrides from section_text.js
        summary:             t.summary || {},
        summaryStats,
        controls: [
          { key: "halfWindowDays", label: "Window", cast: "num", options: [
            { val: "7",  label: "±7d (2w)", active: true },
            { val: "14", label: "±14d (4w)" },
            { val: "30", label: "±30d (2m)" },
          ]},
          { key: "smoothingRadiusDays", label: "Smoothing", cast: "num", options: [
            { val: "0", label: "Raw" },
            { val: "3", label: "±3d", active: true },
            { val: "7", label: "±7d" },
          ]},
          { key: "scale", label: "Y-scale", options: [
            { val: "linear", label: "Linear", active: true },
            { val: "log",    label: "Log" },
          ]},
        ],
        extraKey: () => `
          <span class="prd-key-item">
            <svg width="22" height="8"><line x1="0" y1="4" x2="22" y2="4" stroke="#f59e0b" stroke-width="2" stroke-dasharray="2 3"/></svg>
            Submitted (opened)
          </span>`,
        unitSuffix: "",
        tooltipRows: function (nP, _nS, opts) {
          if (!nP) return "";
          const fmtDate = d3.timeFormat("%b %d, %Y");
          const submitted = this._lastSubmitted || [];
          let nSub = null;
          if (submitted.length) {
            const idx = d3.bisector(d => d.date).left(submitted, nP.date);
            const cand = [submitted[idx-1], submitted[idx]].filter(Boolean);
            if (cand.length) {
              nSub = cand.reduce((a, b) => Math.abs(b.date - nP.date) < Math.abs(a.date - nP.date) ? b : a);
            }
          }
          const closedVal = nP.median != null ? nP.median.toFixed(1) : "—";
          const subVal    = nSub && nSub.value != null ? nSub.value.toFixed(1) : "—";
          const net = (nP.median != null && nSub && nSub.value != null) ? (nSub.value - nP.median) : null;
          const netTxt = net != null ? `${net > 0 ? "+" : ""}${net.toFixed(1)}` : "—";
          return `
            <div class="tt-date">${fmtDate(nP.date)} · window ±${opts.halfWindowDays}d</div>
            <div class="tt-row">
              <span class="tt-swatch" style="background:#1976d2"></span>
              <span class="tt-name">Closed</span>
              <span class="tt-stats">${closedVal}</span>
            </div>
            <div class="tt-row">
              <span class="tt-swatch" style="background:#f59e0b"></span>
              <span class="tt-name">Submitted</span>
              <span class="tt-stats">${subVal}</span>
            </div>
            <div class="tt-row" style="color:#94a3b8;margin-top:.25rem">
              <span class="tt-name" style="padding-left:14px">Net (S − C)</span>
              <span class="tt-stats">${netTxt}</span>
            </div>`;
        },
        computeSeries,
      });
    },
  };

})(window);
