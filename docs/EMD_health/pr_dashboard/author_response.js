/* ================================================================
   pr_dashboard/author_response.js
   Author response after CHANGES_REQUESTED.

   Cycle: each `CHANGES_REQUESTED` review starts a cycle. The cycle
   ends at the first later event (comment / review_comment / review /
   merged / closed) whose actor is a real human other than the
   reviewer. If none exists before the PR terminates or the dataset
   ends, the cycle is UNRESPONDED — its endpoint is the PR's terminal
   event or maxDataDate. That duration feeds the pending-count line
   but not the percentile stats.

   Main series:
     primary   — windowed percentile stats of response time (days),
                 keyed on the CR date.
     secondary — count of pending (unresponded) CRs at each date.
   Small multiples: same percentile band+median per canonical CMIP
   category, sharing the main x-axis and y-scale.
   ================================================================ */
(function (global) {
  const { MS_PER_DAY, isBot, smoothSeries, windowStatsFrom } = PRLib;

  const RESPONDER_TYPES = new Set(['comment', 'review_comment', 'review', 'merged', 'closed']);
  const TERMINAL_TYPES  = new Set(['merged', 'closed']);

  function buildCycles(prs, events) {
    const eventsByPR = d3.group(events || [], e => e.pr);
    const maxDataDate = new Date(d3.max(events, e => new Date(e.timestamp)) || Date.now());

    const cycles = [];       // responded cycles (feed the percentile stats)
    const unresponded = [];  // cycles still awaiting a response — kept for legacy tally
    // Per-PR "carries changes-requested label" intervals. A PR contributes
    // ONE interval [firstCR, terminal], regardless of how many CR cycles it
    // went through. This matches the workflow's label semantics: the
    // `changes-requested` label is added on the first CR review and stays
    // on the PR until it merges or closes.
    const prCRIntervals = [];

    for (const pr of prs) {
      const evs = (eventsByPR.get(pr.number) || [])
        .filter(e => e.timestamp)
        .map(e => ({ ...e, _t: new Date(e.timestamp) }))
        .sort((a, b) => a._t - b._t);
      if (!evs.length) continue;

      const category = PRLib.categorize(pr.title || "");
      const terminalTime = pr.merged_at ? new Date(pr.merged_at).getTime()
                          : pr.closed_at ? new Date(pr.closed_at).getTime()
                          : maxDataDate.getTime();

      let firstCRForPR = null;

      for (let i = 0; i < evs.length; i++) {
        const ev = evs[i];
        if (ev.type !== 'review') continue;
        if (!ev.detail || ev.detail.state !== 'CHANGES_REQUESTED') continue;
        const reviewer = ev.actor;
        const crDate = ev._t;

        if (firstCRForPR === null) firstCRForPR = crDate;

        let responder = null;
        for (let j = i + 1; j < evs.length; j++) {
          const nx = evs[j];
          if (!RESPONDER_TYPES.has(nx.type)) continue;
          if (TERMINAL_TYPES.has(nx.type)) { responder = nx; break; }
          if (isBot(nx.actor)) continue;
          if (nx.actor === reviewer) continue;
          responder = nx;
          break;
        }

        if (responder) {
          const responseDays = (responder._t - crDate) / MS_PER_DAY;
          if (responseDays >= 0 && isFinite(responseDays)) {
            cycles.push({ pr: pr.number, category, crDate, responseDate: responder._t, responseDays });
          }
        } else {
          unresponded.push({ pr: pr.number, category, crDate, endDate: new Date(terminalTime) });
        }
      }

      if (firstCRForPR !== null) {
        prCRIntervals.push({
          pr: pr.number,
          category,
          start: firstCRForPR,
          end: new Date(terminalTime),
          stillOpen: !pr.merged_at && !pr.closed_at,
        });
      }
    }

    return { cycles, unresponded, prCRIntervals, maxDataDate };
  }

  function computeFor(cycles, prCRIntervals, opts, xDomain) {
    const halfWin = opts.halfWindowDays;
    const smoothR = opts.smoothingRadiusDays;
    const minSamples = opts.minSamples || 1;

    const days = d3.timeDays(
      d3.timeDay.floor(xDomain[0]),
      d3.timeDay.offset(d3.timeDay.ceil(xDomain[1]), 1)
    );

    const rawPrimary = days.map(d => {
      const t = d.getTime();
      const values = [];
      for (const c of cycles) {
        if (Math.abs(c.crDate.getTime() - t) <= halfWin * MS_PER_DAY) values.push(c.responseDays);
      }
      return values.length >= minSamples ? windowStatsFrom(values, d) : null;
    }).filter(Boolean);
    const primary = smoothSeries(rawPrimary, smoothR);

    // Secondary line: at each day t, count PRs that have received at least
    // one CHANGES_REQUESTED review by t and haven't been merged/closed by t.
    // This is a PR-level count matching the `changes-requested` label
    // semantics — one contribution per PR, not per cycle.
    const rawSec = days.map(d => {
      const t = d.getTime();
      let n = 0;
      for (const iv of prCRIntervals) {
        if (iv.start.getTime() <= t && t <= iv.end.getTime()) n++;
      }
      return { date: d, count: n };
    });
    // Only apply the light rolling-mean smoothing (matches the primary
    // series). We DON'T re-smooth over halfWin — that would flatten the
    // step-like changes when a PR closes.
    const secSmoothed = smoothSeries(rawSec, smoothR, ['count']);

    return { primary, secondary: secSmoothed };
  }

  function computeSeries(prs, events, opts) {
    const { cycles, unresponded, prCRIntervals, maxDataDate } = buildCycles(prs, events);
    if (!cycles.length && !unresponded.length && !prCRIntervals.length) return null;

    const allCrDates = [
      ...cycles.map(c => c.crDate),
      ...unresponded.map(u => u.crDate),
      ...prCRIntervals.map(p => p.start),
    ];
    if (!allCrDates.length) return null;
    const minD = d3.min(allCrDates);
    const maxD = maxDataDate;
    const xDomain = [minD, maxD];

    const main = computeFor(cycles, prCRIntervals, opts, xDomain);
    if (!main.primary.length) return null;

    // Per-category small multiples
    const smallMultiples = [];
    for (const catDef of PRLib.CATEGORY_DEFS) {
      const catCycles      = cycles.filter(c => c.category === catDef.name);
      const catUnresponded = unresponded.filter(u => u.category === catDef.name);
      const catIntervals   = prCRIntervals.filter(p => p.category === catDef.name);
      if (!catCycles.length && !catUnresponded.length && !catIntervals.length) continue;
      const catSeries = computeFor(catCycles, catIntervals, opts, xDomain);
      if (!catSeries.primary.length) continue;
      smallMultiples.push({
        name: catDef.name,
        color: catDef.color,
        count: catIntervals.length,   // per-PR count, not per-cycle
        primary: catSeries.primary,
      });
    }

    return {
      ...main, xDomain, smallMultiples,
      _cycleCount: cycles.length,
      _unresponded: unresponded.length,
      _openWithCR: prCRIntervals.filter(p => p.stillOpen).length,
      _totalWithCR: prCRIntervals.length,
      _maxDataDate: maxDataDate,
    };
  }

  /**
   * Summary cards for the Change Reply section.
   */
  function summaryStats(prs, events, opts, series) {
    const s = (this.cfg && this.cfg.summary) || {};
    const total = series ? series._cycleCount : 0;
    const openWithCR = series ? series._openWithCR : 0;

    let recent = "—";
    if (series && series.primary && series.primary.length) {
      const last = series.primary.slice(-14);
      const m = d3.mean(last, p => p.median);
      if (m != null && isFinite(m)) recent = PRLib.fmtNum(m) + " d";
    }

    let range = "—";
    if (series && series.xDomain) {
      const fmt = d3.timeFormat("%b %Y");
      range = `${fmt(series.xDomain[0])} → ${fmt(series.xDomain[1])}`;
    }

    return [
      {
        label: (s.cycles && s.cycles.label)  || "CR cycles",
        value: String(total),
        sub:   (s.cycles && s.cycles.sub)    || "responded, in scope",
      },
      {
        label: (s.median && s.median.label)  || "Recent median",
        value: recent,
        sub:   (s.median && s.median.sub)    || "avg of last 14 window points",
      },
      {
        label: (s.pending && s.pending.label) || "Open with CR",
        value: String(openWithCR),
        sub:   (s.pending && s.pending.sub)   || "open PRs carrying changes-requested",
        valueStyle: openWithCR > 0 ? "color:#7c3aed" : "",
      },
      {
        label: (s.range && s.range.label) || "Date range",
        value: range,
        sub:   (s.range && s.range.sub)   || "first → last CR",
        valueStyle: "font-size:.95rem",
      },
    ];
  }

  global.AuthorResponseChart = {
    create(container, text) {
      const t = text || {};
      return new PRChart({
        container,
        title:               t.title               || "Change reply",
        intro:               t.intro               || "",
        caption:             t.caption             || "Time from CHANGES_REQUESTED review to author's next response.",
        leftAxisLabel:       t.leftAxisLabel       || "Days to author response",
        rightAxisLabel:      t.rightAxisLabel      || "Open PRs with changes-requested",
        primaryColor:        "#1976d2",
        primaryKeyLabel:     t.primaryKeyLabel     || "Median response time",
        hasSecondary:        true,
        secondaryLabel:      t.secondaryLabel      || "Open PRs with CR — right axis",
        hasSmallMultiples:   true,
        smallMultiplesTitle: t.smallMultiplesTitle || "Per-category change reply",
        smallMultiplesSub:   t.smallMultiplesSub   || "canonical categories · shared axes with main",
        unitSuffix:          " d",
        defaults:            { minSamples: 1 },
        initialOpts:         t.data || {},   // ← user-editable overrides from section_text.js
        summary:             t.summary || {},
        summaryStats,
        controls: [
          { key: "band", label: "Band", options: [
            { val: "iqr", label: "25–75", active: true },
            { val: "p10", label: "10–90" },
            { val: "p05", label: "5–95" },
          ]},
          { key: "halfWindowDays", label: "Window", cast: "num", options: [
            { val: "1",  label: "±1d", active: true },
            { val: "3",  label: "±3d" },
            { val: "7",  label: "±7d" },
            { val: "14", label: "±14d" },
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
