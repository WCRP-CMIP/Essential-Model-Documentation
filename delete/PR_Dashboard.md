# PR Dashboard — EMD submissions

Rolling analytics restricted to PRs tagged with the `emd-submission` label:
first-response latency, reply time to `CHANGES_REQUESTED` reviews, and overall
submission-vs-closure throughput. Data is loaded once from
`pr_all_timeline_data.json` and rendered into three sections below by the shared
[`PRChart`](./pr_dashboard/chart_lib.js) template.

The controls at the top of the page apply to **all three** charts simultaneously.

<link rel="stylesheet" href="pr_dashboard/styles.css">

<div class="prd-container">

  <div id="prd-status" class="prd-status">Loading…</div>
  <div id="prd-warning" class="prd-warning" style="display:none"></div>
  <div id="prd-summary" class="prd-summary"></div>

  <div id="prd-controls" class="prd-controls"></div>

  <h2>First response</h2>
  <div id="prd-first-response"></div>

  <h2>Change reply</h2>
  <div id="prd-author-response"></div>

  <h2>Totals — submitted vs closed</h2>
  <div id="prd-throughput"></div>

</div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="pr_dashboard/chart_lib.js"></script>
<script src="pr_dashboard/first_response.js"></script>
<script src="pr_dashboard/author_response.js"></script>
<script src="pr_dashboard/throughput.js"></script>
<script src="pr_dashboard/dashboard.js"></script>

## How to broaden the cohort

The filter is defined by a single predicate in `pr_dashboard/chart_lib.js`:

```js
function hasEmdSubmissionLabel(pr) {
  return (pr.labels || []).indexOf("emd-submission") !== -1;
}
```

If the strict label yields too few PRs, swap the filter call in
`dashboard.js` from `PRLib.hasEmdSubmissionLabel` to
`PRLib.hasAnyWorkflowLabel` to include any PR that touched the EMD workflow
(labels: `emd-submission`, `changes-requested`, `approved`, `changes-made`,
`reviewer-comment`, `pull_req`).
