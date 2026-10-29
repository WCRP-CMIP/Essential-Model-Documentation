/* ================================================================
   pr_dashboard/dashboard.js
   Loads the all-states PR JSON once and drives three self-contained
   PRChart instances. Every visible label on the page comes from
   window.PRDashText (see section_text.js). Each section renders its
   own summary strip; there is no dashboard-wide summary anymore.
   ================================================================ */
(function () {
  const DATA_URL = "assets/pr_all_timeline_data.json";
  const T = window.PRDashText || {};

  // ---------- DOM references ----------
  const $status  = document.getElementById("prd-status");
  const $secFR = document.getElementById("prd-first-response");
  const $secCR = document.getElementById("prd-author-response");
  const $secTP = document.getElementById("prd-throughput");

  // Browser tab title.
  if (T.browserTitle) document.title = T.browserTitle;

  // Page-header title + description are populated as soon as the script
  // parses (before data loads) so users see the labelled shell straight away.
  if (T.pageTitle) {
    const h1 = document.querySelector(".page-header h1");
    if (h1) h1.textContent = T.pageTitle;
  }
  if (T.pageDescription) {
    const p = document.querySelector(".page-header p");
    if (p) p.innerHTML = T.pageDescription;
  }
  // Loading placeholder.
  if ($status && T.loading) $status.textContent = T.loading;

  function setStatus(msg, isError) {
    if (!$status) return;
    $status.textContent = msg;
    $status.classList.toggle("error", !!isError);
    $status.style.display = msg ? "block" : "none";
  }

  // ---------- load & init ----------
  d3.json(DATA_URL).then(init).catch(err => {
    console.error(err);
    const tpl = T.errorLoadFail || "Could not load the PR data — ${err}";
    setStatus(tpl.replace("${err}", err.message || String(err)), true);
  });

  function init(raw) {
    const all = raw.pull_requests || [];
    const prs = all;
    const events = raw.events || [];

    if (!prs.length) {
      setStatus(T.errorNoPRs || "No PRs in the dataset.", true);
      return;
    }
    setStatus("");

    // Build the three self-contained sections. Each one draws its own
    // header, summary strip, controls, chart, and small multiples.
    const charts = [
      FirstResponseChart.create($secFR,  T.firstResponse),
      AuthorResponseChart.create($secCR, T.changeReply),
      ThroughputChart.create($secTP,     T.throughput),
    ];
    for (const ch of charts) ch.update(prs, events, {});

    renderTimelineButton();

    window.addEventListener("resize", PRLib.debounce(() => {
      for (const ch of charts) ch.update(prs, events, {});
    }, 200));
  }

  // ---------- timeline button ----------
  function renderTimelineButton() {
    const host = document.getElementById("prd-timeline-button");
    if (!host) return;
    const tb = T.timelineButton || {};
    const label = tb.label || "View the full per-PR event timeline →";
    const href  = tb.href  || "PR_Timeline.html";
    const note  = tb.note  || "";
    host.innerHTML =
      `<a href="${href}" class="prd-timeline-btn">${label}</a>` +
      (note ? `<div class="prd-timeline-note">${note}</div>` : "");
  }

})();
