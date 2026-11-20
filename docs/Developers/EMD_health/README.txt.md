# EMD Health Dashboard — how the graphs are computed

All three charts read a single data file, `assets/pr_all_timeline_data.json`,
produced by `scripts/pr_all_timeline.py`. That file has two top-level arrays:

- `pull_requests` — one row per PR with `number`, `title`, `author`,
  `created_at`, `merged_at`, `closed_at`, and a current-state snapshot of
  `labels`.
- `events` — one row per interaction, each with `pr` (PR number), `type`
  (`opened`, `body_edit`, `comment`, `review_comment`, `review`, `merged`,
  `closed`), `timestamp`, `actor`, and — for `review` events — a `detail`
  object that carries the review `state` (`APPROVED`,
  `CHANGES_REQUESTED`, `COMMENTED`).

Nothing else is fetched at runtime; every number on the page is derived
client-side from those two arrays. The category breakdowns (in each small-
multiple grid) map PR titles to a canonical CMIP entity via the regexes in
`chart_lib.js` (`Horizontal Grid Cell`, `Horizontal Computational Grid`,
`Vertical Computational Grid`, `Model Family`, `Model Component`, `Model`).
</content>

## 1. First response

For each PR we look up its events in chronological order (filtered by
`pr` number and events strictly after `created_at`), then find the first
event that qualifies as a "response": either a terminal event (`merged`
or `closed`, any actor) or a `comment` / `review_comment` / `review`
event whose actor is not the PR's author **and not a bot** (bot detection
covers `[bot]` suffixed logins, `github-actions`, and `copilot*`). The
response time is the difference between the PR's `created_at` and that
event's `timestamp`, converted to hours or days depending on the "Unit"
toggle. To draw the main chart we sweep a ±*N*-day sliding window across
the x-axis; at each day *D* we collect every response time whose PR was
opened within `[D − N, D + N]`, then compute the 5 / 10 / 25 / 50 / 75 /
90 / 95th percentiles of that set and apply a rolling-mean smoothing of
radius `smoothingRadiusDays` days. The right-axis dashed line is the
count of PRs currently open — for every PR we build the interval
`[created_at, merged_at || closed_at || dataCutoff]` and at each day *D*
count how many intervals contain *D*. Per-category small multiples repeat
the same computation restricted to PRs whose title matches a canonical
category regex.
</content>

## 2. Change reply

For each PR we walk the events chronologically and identify every
`review` event whose `detail.state` is `CHANGES_REQUESTED`. Each such
review starts a "cycle"; the cycle ends at the first later event of type
`comment`, `review_comment`, `review`, `merged`, or `closed` whose actor
is a real human (bots excluded) and not the reviewer who filed the CR.
If a responder exists we record the cycle with a response time in days;
otherwise the cycle is marked unresponded and dropped from the percentile
stats. The main line and band are computed the same way as First
Response — a ±*N*-day sliding window keyed on the CR date, quantile
summaries, then a light rolling-mean smooth. The right-axis line is
**not** per-cycle. It is per-PR: for every PR that has ever received at
least one `CHANGES_REQUESTED` review we build one interval
`[first CR event, merged_at || closed_at || dataCutoff]`, and at each day
count how many of those intervals contain that day. This matches the
`changes-requested` label semantics — the label is added on the first CR
review and stays on the PR until it closes, so the line rises by 1 the
day a PR first receives a CR and drops by 1 the day the PR merges or
closes, regardless of how many review rounds happened in between.
</content>

## 3. Throughput

Every PR contributes two events to this chart: an "opened" event at
`created_at` and a "closed" event at `merged_at || closed_at` (PRs still
open contribute only the opened event). At each day *D* on the x-axis we
count how many PRs opened in the window `[D − N, D + N]` — that is the
amber dotted **Submitted** line — and, separately, how many PRs closed
(merged or closed-without-merge) in the same window — that is the solid
blue **Closed** line. Both series are then passed through the same
`smoothingRadiusDays` rolling mean. There is no percentile band and no
right axis: both lines share the primary left-axis scale. The gap
between them is the backlog delta shown in the summary card — when
Submitted sits above Closed we are accumulating open PRs faster than we
are clearing them; when Closed sits above Submitted the backlog is
shrinking. Per-category small multiples restrict both counts to PRs whose
title matches a canonical CMIP category, so a growing atmospheric-grid
backlog can be spotted independently of the overall trend.

---

## Notes on limitations

- **Symmetric sliding window.** All three charts use a ±*N*-day window
  centred on the target date. The most recent point on every curve
  therefore counts only past events (there are no future events yet in
  the data), so recent values are biased low. This is inherent to
  symmetric windows — a right-aligned window would fix it but at the
  cost of noisier recent points.
- **All PRs are included.** The dashboard does not filter to just
  `emd-submission`-labelled PRs. Workflow/bot PRs are counted alongside
  content submissions. `PRLib.hasEmdSubmissionLabel` is available to
  narrow the cohort if the numbers look inflated.
- **Labels are current-state snapshots.** The collector records the
  labels a PR carries *now*, not the label history. The right-axis lines
  on the First Response and Change Reply charts therefore reconstruct
  "was this PR carrying the label at date *D*?" from event timestamps
  rather than from a label-change timeline.
</content>
