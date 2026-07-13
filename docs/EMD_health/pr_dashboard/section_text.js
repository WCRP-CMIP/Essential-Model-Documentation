/* ================================================================
   pr_dashboard/section_text.js

   Single source of truth for every editable string on the PR
   dashboard: browser title, page header, summary cards, status /
   error messages, and the three section-specific configs (title,
   intro, captions, axis labels, key labels, small-multiples header,
   and initial data config).

   Notes:
   - Strings can contain plain HTML (<b>, <code>, <a href="..."> etc.)
     wherever they're rendered via .innerHTML.
   - Anything unset falls back to the module's built-in default —
     see chart_lib.js and each *_response / throughput module.
   - `data` blocks are per-section initial control state; edit these
     to change which window / smoothing / band / scale each chart
     loads with.
   ================================================================ */
window.PRDashText = {

  // ---- browser + page header ----
  browserTitle: "PR Dashboard — Essential Model Documentation",

  pageTitle: "PR Dashboard",
  pageDescription:
    "Rolling analytics across every PR in the Essential Model Documentation repository. " +
    "See how quickly PRs are responded to, how long authors take to reply to " +
    "change requests, and whether the backlog is growing or shrinking."+
    "\n\n <br><br> The current readings suggest that the time taken for reviewers to respond is not being negatively impacted by increases in the number of submissions. Delays in authors responding to change requests explain a large number of the currently open PRs, however with the drop in sessions this is now shrinking. Similarly the number of new submissions and the number that have been processed follow the same trend, and even reducing suggesting that the reviewers are able to manage the current workload without any additional delays.",

  // ---- loading / error states ----
  loading:        "Loading…",
  errorNoPRs:     "No PRs in the dataset.",
  errorLoadFail:  "Could not load the PR data — ${err}",

  // ---- summary strip (four cards along the top) ----
  summary: {
    total: {
      label: "Total PRs",
      sub:   "all PRs in the dataset",
    },
    breakdown: {
      label: "Status breakdown",
      sub:   "merged · closed · open",
      // Suffixes shown as small subscripts next to the numbers
      mergedSuffix: "m",
      closedSuffix: "c",
      openSuffix:   "o",
    },
    events: {
      label: "Events",
      sub:   "total logged events",
    },
    range: {
      label: "Date range",
      sub:   "first → last opened",
    },
  },

  // ---- section 1: First Response ----
  firstResponse: {
    title:               "First response",
    intro:
      "Time from a PR being opened to the first non-author response (comment, " +
      "review, or merge/close). The percentile band shows how the wait is " +
      "distributed across PRs opened within the sliding window; the dashed " +
      "purple line on the right axis is the count of PRs still open (not " +
      "yet merged / closed).",
    caption:             "Days to first response · median with percentile band · hover for values.",
    leftAxisLabel:       "Days to first response",
    rightAxisLabel:      "Open PRs (not yet merged/closed)",
    primaryKeyLabel:     "Median response time",
    secondaryLabel:      "Open PRs — right axis",
    smallMultiplesTitle: "Per-category first response",
    smallMultiplesSub:   "canonical categories · shared axes with main",
    data: {
      band:                "iqr",       // "iqr" (25–75) | "p10" (10–90) | "p05" (5–95)
      halfWindowDays:      7,           // ±N days
      smoothingRadiusDays: 3,           // additional ±N-day rolling mean
      scale:               "linear",    // "linear" | "log"
      minSamples:          1,           // min PRs in a window to plot a point
    },
  },

  // ---- section 2: Change Reply ----
  changeReply: {
    title:               "Change reply",
    intro:
      "For each <code>CHANGES_REQUESTED</code> review, how long does it take for the " +
      "author (or any non-reviewer) to respond. A single PR can " +
      "contribute multiple cycles if it went through several review " +
      "rounds - this is not captured here. The right-axis line is the count of " +
      "<b>open PRs currently carrying a <code>changes-requested</code> label</b>: " +
      "one contribution per PR (not per cycle), from the PR's first CR review " +
      "until the PR closes.",
    caption:             "Days from CR to next author response · hover for values.",
    leftAxisLabel:       "Days to author response",
    rightAxisLabel:      "Open PRs with changes-requested",
    primaryKeyLabel:     "Median response time",
    secondaryLabel:      "Open PRs with CR — right axis",
    smallMultiplesTitle: "Per-category change reply",
    smallMultiplesSub:   "canonical categories · shared axes with main",
    // CR events are much sparser than opened-PR events — most days have
    // one or two cycles at most — so this section defaults to a narrower
    // ±1d sliding window and accepts single-cycle days (minSamples=1).
    data: {
      band:                "iqr",
      halfWindowDays:      1,
      smoothingRadiusDays: 3,
      scale:               "linear",
      minSamples:          1,
    },
  },

  // ---- section 3: Throughput ----
  throughput: {
    title:               "Throughput — totals",
    intro:
      "The rolling counts of PRs <b>closed</b> (merged or " +
      "closed-without-merge) in solid blue, and PRs <b>submitted</b> " +
      "(opened) in dotted amber. This allows us to see whether the backlog of open PRs is growing or shrinking over time. " +
      "When the dotted line runs above the solid " +
      "one, the backlog is growing that window; when solid is above dotted, " +
      "the backlog is shrinking.",
    caption:             "Rolling counts of closed vs submitted PRs per window.",
    leftAxisLabel:       "PRs per window",
    primaryKeyLabel:     "Closed",
    smallMultiplesTitle: "Per-category throughput",
    smallMultiplesSub:   "closed (line) vs submitted (dotted) · shared axes",
    // Throughput has no percentile band — the "band" key is ignored here.
    data: {
      halfWindowDays:      7,
      smoothingRadiusDays: 3,
      scale:               "linear",
    },
  },

  // ---- "View timeline" button at the bottom ----
  timelineButton: {
    label: "View the full per-PR event timeline →",
    href:  "PR_Timeline.html",
    note:  "A per-PR gantt-style view of every review, comment, and merge event.",
  },
};
