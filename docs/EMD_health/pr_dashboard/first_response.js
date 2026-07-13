/* ================================================================
   pr_dashboard/first_response.js
   Time to first non-author response.

   Metric: for each PR, the earliest of comment/review/review_comment/
   merged/closed after `opened` that either terminates the PR or is by
   someone other than the author. Response time is opened → that event.

   Unit toggle: control "unit" ∈ { "h" | "d" }. Values are computed
   internally in days, then multiplied by 24 for hours display. Axis
   labels + tooltip suffixes flip with the toggle.

   Main series:
     primary   — sliding-window percentile stats of response time,
                 keyed on the PR opened date, in the current unit.
     secondary — count of currently-open PRs (opened but not yet merged
                 or closed) at each date, drawn on the right axis.

   Small multiples: same percentile band+median per canonical CMIP
   category, sharing the main x-axis and y-scale.
   ================================================================ */
(function (global) {
  const { MS_PER_DAY, smoothSeries, windowStatsFrom } = PRLib;

  const RESPONSE_TYPES = new Set(['comment', 'review_comment', 'review', 'merged', 'closed']);
  const TERMINAL_TYPES = new Set(['merged', 'closed']);

  const STAT_KEYS = ['p05','p10','p25','median','p75','p90','p95'];

  function unitFactor(opts) {
    return (opts && opts.unit === "d") ? 1 : 24;   // default is hours
  }

  function buildRecords(prs, events) {
    const eventsByPR = d3.group(events || [], e => e.pr);
    const maxDataDate = new Date(d3.max(events, e => new Date(e.timestamp)) || Date.now());
    const asOf = maxDataDate.getTime();

    const records = prs.map(pr => {
      const opened = pr.created_at ? new Date(pr.created_at) : null;
      if (!opened || isNaN(opened)) return null;
      const author = pr.author;

      const evs = (eventsByPR.get(pr.number) || [])
        .filter(e => e.timestamp)
        .map(e => ({ ...e, _t: new Date(e.timestamp) }))
        .filter(e => e._t > opened)
        .sort((a, b) => a._t - b._t);

      const first = evs.find(e =>
        RESPONSE_TYPES.has(e.type) &&
        (TERMINAL_TYPES.has(e.type) || e.actor !== author)
      );

      const terminalDate = pr.merged_at ? new Date(pr.merged_at)
                          : pr.closed_at ? new Date(pr.closed_at) : null;

      return {
        number: pr.number,
        title: pr.title || "",
        opened,
        terminalDate,
        category: PRLib.categorize(pr.title || ""),
        responseDate: first ? first._t : null,
        responseDays: first ? (first._t - opened) / MS_PER_DAY : null,
      };
    }).filter(Boolean);

    return { records, maxDataDate, asOf };
  }

  /**
   * Compute {primary, secondary} for a given record set on a fixed x-domain.
   * All response times are multiplied by unitFactor(opts) so downstream
   * rendering can share the same y-scale regardless of unit choice.
   */
  function computeFor(records, opts, xDomain, asOf) {
    const halfWin = opts.halfWindowDays;
    const smoothR = opts.smoothingRadiusDays;
    const minSamples = opts.minSamples || 1;
    const uf = unitFactor(opts);

    const responded = records.filter(r =>
      r.responseDays != null && isFinite(r.responseDays) && r.responseDays >= 0
    );

    const days = d3.timeDays(
      d3.timeDay.floor(xDomain[0]),
      d3.timeDay.offset(d3.timeDay.ceil(xDomain[1]), 1)
    );

    const rawPrimary = days.map(d => {
      const t = d.getTime();
      const values = [];
      for (const r of responded) {
        if (Math.abs(r.opened.getTime() - t) <= halfWin * MS_PER_DAY) {
          values.push(r.responseDays * uf);
        }
      }
      return values.length >= minSamples ? windowStatsFrom(values, d) : null;
    }).filter(Boolean);
    const primary = smoothSeries(rawPrimary, smoothR);

    // Secondary: open-PR count (records still open at each t). Count is
    // unit-independent, so no conversion needed.
    const intervals = records.map(r => ({
      start: r.opened.getTime(),
      end:   r.terminalDate ? r.terminalDate.getTime() : asOf,
    }));
    const rawSec = days.map(d => {
      const t = d.getTime();
      let n = 0;
      for (const iv of intervals) if (iv.start <= t && t <= iv.end) n++;
      return { date: d, count: n };
    });
    let secSmoothed = smoothSeries(rawSec, halfWin, ['count']);
    secSmoothed = smoothSeries(secSmoothed, smoothR, ['count']);

    return { primary, secondary: secSmoothed };
  }

  function computeSeries(prs, events, opts) {
    const { records, maxDataDate, asOf } = buildRecords(prs, events);
    if (!records.length) return null;

    const [minD, maxD] = d3.extent(records, r => r.opened);
    const xDomain = [minD, maxD];

    const main = computeFor(records, opts, xDomain, asOf);
    if (!main.primary.length) return null;

    // Per-category small multiples
    const smallMultiples = [];
    for (const catDef of PRLib.CATEGORY_DEFS) {
      const catRecs = records.filter(r => r.category === catDef.name);
      if (!catRecs.length) continue;
      const catSeries = computeFor(catRecs, opts, xDomain, asOf);
      if (!catSeries.primary.length) continue;
      smallMultiples.push({
        name: catDef.name,
        color: catDef.color,
        count: catRecs.length,
        primary: catSeries.primary,
      });
    }

    // Stash total record count for the summary strip.
    return {
      ...main, xDomain, smallMultiples,
      _totalRecords: records.length,
      _respondedRecords: records.filter(r => r.responseDays != null).length,
      _openCount: records.filter(r => !r.terminalDate).length,
      _maxDataDate: maxDataDate,
    };
  }

  /**
   * Summary cards for this section — pulled from the freshly-computed series
   * plus the raw PR list. Called on every re-render (opts changes).
   */
  function summaryStats(prs, events, opts, series) {
    const s = (this.cfg && this.cfg.summary) || {};   // per-section text overrides
    const unit = (opts && opts.unit === "d") ? "d" : "h";
    const uf = unit === "h" ? 24 : 1;
    const suffix = unit === "h" ? "h" : "d";

    const total = series ? series._totalRecords : prs.length;
    const responded = series ? series._respondedRecords : prs.length;
    const openCount = series ? series._openCount : 0;

    // Recent median = mean of the last 14 primary points' medians.
    let recent = "—";
    if (series && series.primary && series.primary.length) {
      const last = series.primary.slice(-14);
      const m = d3.mean(last, p => p.median);
      if (m != null && isFinite(m)) recent = PRLib.fmtNum(m) + " " + suffix;
    }

    // Date range from series xDomain.
    let range = "—";
    if (series && series.xDomain) {
      const fmt = d3.timeFormat("%b %Y");
      range = `${fmt(series.xDomain[0])} → ${fmt(series.xDomain[1])}`;
    }

    return [
      {
        label: (s.analyzed && s.analyzed.label) || "PRs analyzed",
        value: `${responded}<span class="u" style="font-size:.7em;color:var(--emd-text-tertiary)"> / ${total}</span>`,
        sub:   (s.analyzed && s.analyzed.sub)   || "with a first-response event",
      },
      {
        label: (s.median && s.median.label) || "Recent median",
        value: recent,
        sub:   (s.median && s.median.sub)   || "avg of last 14 window points",
      },
      {
        label: (s.pending && s.pending.label) || "Currently open",
        value: String(openCount),
        sub:   (s.pending && s.pending.sub)   || "not yet merged/closed",
        valueStyle: "color:#7c3aed",
      },
      {
        label: (s.range && s.range.label) || "Date range",
        value: range,
        sub:   (s.range && s.range.sub)   || "first → last opened",
        valueStyle: "font-size:.95rem",
      },
    ];
  }

  global.FirstResponseChart = {
    create(container, text) {
      const t = text || {};

      // Unit-aware axis label + tooltip suffix. Both keys are also
      // editable via section_text.js (leftAxisLabelHours / leftAxisLabelDays).
      const axisByUnit = {
        h: t.leftAxisLabelHours || "Hours to first response",
        d: t.leftAxisLabelDays  || "Days to first response",
      };
      const suffixByUnit = { h: " h", d: " d" };

      return new PRChart({
        container,
        title:               t.title               || "First response",
        intro:               t.intro               || "",
        caption:             t.caption             || "Time from PR opened to first non-author response.",
        // Both dynamic — resolved per render from the current opts.unit.
        leftAxisLabel:       (opts) => axisByUnit[(opts && opts.unit) === "d" ? "d" : "h"],
        rightAxisLabel:      t.rightAxisLabel      || "Open PRs (not yet merged/closed)",
        primaryColor:        "#1976d2",
        primaryKeyLabel:     t.primaryKeyLabel     || "Median response time",
        hasSecondary:        true,
        secondaryLabel:      t.secondaryLabel      || "Open PRs — right axis",
        hasSmallMultiples:   true,
        smallMultiplesTitle: t.smallMultiplesTitle || "Per-category first response",
        smallMultiplesSub:   t.smallMultiplesSub   || "canonical categories · shared axes with main",
        unitSuffix:          (opts) => suffixByUnit[(opts && opts.unit) === "d" ? "d" : "h"],
        defaults:            { minSamples: 1 },
        initialOpts:         t.data || {},
        // Per-section text overrides for the summary cards.
        summary:             t.summary || {},
        summaryStats,
        controls: [
          { key: "unit", label: "Unit", options: [
            { val: "h", label: "Hours", active: true },
            { val: "d", label: "Days" },
          ]},
          { key: "band", label: "Band", options: [
            { val: "iqr", label: "25–75", active: true },
            { val: "p10", label: "10–90" },
            { val: "p05", label: "5–95" },
          ]},
          { key: "halfWindowDays", label: "Window", cast: "num", options: [
            { val: "3",  label: "±3d" },
            { val: "7",  label: "±7d", active: true },
            { val: "14", label: "±14d" },
            { val: "30", label: "±30d" },
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
        computeSeries,
      });
    },
  };

})(window);
