#!/usr/bin/env python3
"""
pr_timeline.py
==============
Collect the full event history of every *merged* pull request in a GitHub
repository, for use as the data source of a D3 calendar-timeline visualisation
(PR_Timeline.html).

For each merged PR the script records, as individual timestamped events:

  - opened         when the PR was created             (+ author)
  - body_edit      each time the description changed    (+ editor)
  - comment        each conversation comment            (+ author)
  - review_comment each inline code-review comment       (+ author, path)
  - review         each submitted review                (+ reviewer, state)
  - merged         when the PR was merged               (+ merged_by)
  - closed         when the PR was closed (if != merge) (+ actor)

Output: a single JSON file (default: docs/assets/pr_timeline_data.json)
with a flat, long-format `events` array (one row per event — ideal for D3)
and a `pull_requests` array of per-PR summary metadata.

Rate-limit friendly
-------------------
The script is INCREMENTAL by default: it loads any existing output file and
re-fetches only PRs whose GitHub `updated_at` has changed since the last run.
A re-run with no new activity costs only the handful of calls needed to list
PRs (~5), not one-per-PR. It also CHECKPOINTS: on any error it writes the
progress made so far, so a transient failure never forces a full re-fetch.
Use --refresh to ignore the cache and rebuild from scratch.

Per changed/new PR it makes ~4 calls (issue comments, review comments,
reviews, and one GraphQL call covering both merged_by and body edits), all
sequential — well within GitHub's 5000 req/hour authenticated limit.

Authentication
--------------
Uses the GitHub CLI (`gh`) for all API access — no token needed; it relies on
your existing `gh` login. If unauthenticated: `gh auth login`.

Usage
-----
    python pr_timeline.py                  # incremental update
    python pr_timeline.py --refresh        # full rebuild, ignore cache
    python pr_timeline.py --no-body-edits  # skip body-edit history
    python pr_timeline.py --limit 5        # debug: first 5 merged PRs

Requirements: the `gh` CLI on PATH (https://cli.github.com). Stdlib otherwise.
"""

import argparse
import collections
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── configuration ───────────────────────────────────────────────────────────
DEFAULT_REPO = "WCRP-CMIP/Essential-Model-Documentation"
SCRIPT_DIR   = Path(__file__).resolve().parent
DEFAULT_OUT  = SCRIPT_DIR.parent / "assets" / "pr_timeline_data.json"
PER_PAGE     = 100
MAX_RETRIES  = 4          # transient-error retries per gh call


# ── gh CLI helpers ────────────────────────────────────────────────────────────
TRANSIENT_HINTS = (
    "bad credentials", "401", "rate limit", "secondary rate", "abuse",
    "timeout", "timed out", "502", "503", "504", "connection reset",
)


def _run_gh(args):
    """Run `gh <args>`, returning stdout. Retries transient failures w/ backoff."""
    for attempt in range(MAX_RETRIES + 1):
        proc = subprocess.run(["gh", *args], capture_output=True, text=True)
        if proc.returncode == 0:
            return proc.stdout
        msg = (proc.stderr.strip() or proc.stdout.strip())
        low = msg.lower()
        if any(h in low for h in TRANSIENT_HINTS) and attempt < MAX_RETRIES:
            wait = 3 * (2 ** attempt)
            tail = msg.splitlines()[-1][:90] if msg else "?"
            print(f"  ! gh transient error ({tail}); retry {attempt + 1}/"
                  f"{MAX_RETRIES} in {wait}s", flush=True)
            time.sleep(wait)
            continue
        raise RuntimeError(f"`gh {' '.join(args)}` failed:\n{msg}")
    raise RuntimeError("unreachable")


def _decode_concatenated(text):
    """Parse one-or-more concatenated top-level JSON values from `text`."""
    decoder = json.JSONDecoder()
    idx, n, values = 0, len(text), []
    while idx < n:
        while idx < n and text[idx].isspace():
            idx += 1
        if idx >= n:
            break
        value, end = decoder.raw_decode(text, idx)
        values.append(value)
        idx = end
    return values


def gh_api(path, paginate=False):
    """GET a REST endpoint via `gh api`. Returns a list (arrays are flattened)."""
    args = ["api", "-H", "X-GitHub-Api-Version:2022-11-28"]
    if paginate:
        args.append("--paginate")
    args.append(path)
    values = _decode_concatenated(_run_gh(args))
    if values and all(isinstance(v, list) for v in values):
        flat = []
        for v in values:
            flat.extend(v)
        return flat
    return values[0] if len(values) == 1 else values


PR_META_QUERY = (
    "query($owner:String!,$repo:String!,$number:Int!){"
    "repository(owner:$owner,name:$repo){"
    "pullRequest(number:$number){"
    "mergedBy{login} "
    "userContentEdits(first:100){nodes{editedAt editor{login}}}}}}"
)


def gh_graphql(query, **variables):
    """Run a GraphQL query via `gh api graphql`. Returns the `data` object."""
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, val in variables.items():
        if isinstance(val, bool):
            args += ["-F", f"{key}={str(val).lower()}"]
        elif isinstance(val, int):
            args += ["-F", f"{key}={val}"]
        else:
            args += ["-f", f"{key}={val}"]
    try:
        body = json.loads(_run_gh(args))
    except (RuntimeError, json.JSONDecodeError) as e:
        print(f"  ! GraphQL request failed: {e}", flush=True)
        return None
    if "errors" in body:
        print(f"  ! GraphQL errors: {body['errors']}", flush=True)
    return body.get("data")


# ── data collection ───────────────────────────────────────────────────────────
def actor_login(node):
    """Login from a GitHub user object, or pass through an existing login string."""
    if not node:
        return None
    if isinstance(node, str):
        return node
    return node.get("login")


def list_merged_prs(owner, repo):
    """
    Fetch all closed PRs in one paginated pull and filter to merged ones.
    Uses --jq to trim each page to only the fields we need, reducing payload.
    GitHub has no server-side merged-only filter; state=closed is the closest
    — all merged PRs are closed, so nothing is missed.
    """
    print(f"Fetching pull requests for {owner}/{repo} ...", flush=True)
    # --paginate follows all Link: rel="next" pages automatically (one gh call).
    # --jq filters fields client-side before returning, keeping payload small.
    args = [
        "api", "--paginate",
        "-H", "X-GitHub-Api-Version:2022-11-28",
        "--jq", "[.[] | select(.merged_at != null)]",
        f"/repos/{owner}/{repo}/pulls"
        f"?state=closed&sort=created&direction=asc&per_page={PER_PAGE}",
    ]
    values = _decode_concatenated(_run_gh(args))
    merged = []
    for v in values:
        if isinstance(v, list):
            merged.extend(v)
    print(f"  found {len(merged)} merged PRs", flush=True)
    return merged


def fetch_pr_meta(owner, repo, number, created_at):
    """
    One GraphQL call returning (merged_by_login, body_edits).
    `merged_by` is absent from the REST list endpoint, and body-edit history is
    only exposed via GraphQL `userContentEdits` — so both come from here.
    Edits coinciding with PR creation are dropped. body_edits is a list of
    (timestamp, editor) tuples.
    """
    data = gh_graphql(PR_META_QUERY, owner=owner, repo=repo, number=number)
    if not data:
        return None, []
    try:
        pr = data["repository"]["pullRequest"]
    except (TypeError, KeyError):
        return None, []
    merged_by = actor_login(pr.get("mergedBy"))
    edits = []
    for node in (pr.get("userContentEdits") or {}).get("nodes", []):
        ts = node.get("editedAt")
        if not ts or ts == created_at:
            continue
        edits.append((ts, actor_login(node.get("editor"))))
    return merged_by, edits


def collect_pr_events(owner, repo, pr, body_edits, include_body_edits=True):
    """Build the full ordered event list for a single merged PR."""
    number = pr["number"]
    events = []

    def add(etype, timestamp, actor, **detail):
        if not timestamp:
            return
        events.append({
            "pr": number,
            "title": pr.get("title", ""),
            "type": etype,
            "timestamp": timestamp,
            "actor": actor,
            "detail": detail or None,
        })

    # 1. opened
    add("opened", pr.get("created_at"), actor_login(pr.get("user")))

    # 2. body edits (from the GraphQL meta call)
    if include_body_edits:
        for ts, editor in body_edits:
            add("body_edit", ts, editor)

    # 3. conversation comments
    for c in gh_api(f"/repos/{owner}/{repo}/issues/{number}/comments", paginate=True):
        add("comment", c.get("created_at"), actor_login(c.get("user")))

    # 4. inline review comments
    for c in gh_api(f"/repos/{owner}/{repo}/pulls/{number}/comments", paginate=True):
        add("review_comment", c.get("created_at"), actor_login(c.get("user")),
            path=c.get("path"))

    # 5. submitted reviews
    for r in gh_api(f"/repos/{owner}/{repo}/pulls/{number}/reviews", paginate=True):
        add("review", r.get("submitted_at"), actor_login(r.get("user")),
            state=r.get("state"))

    # 6. merged
    add("merged", pr.get("merged_at"), actor_login(pr.get("merged_by")))

    # 7. closed (only if distinct from the merge event)
    if pr.get("closed_at") and pr.get("closed_at") != pr.get("merged_at"):
        add("closed", pr.get("closed_at"), None)

    events.sort(key=lambda e: e["timestamp"])
    return events


def summarise_pr(pr, events):
    """Compact per-PR record. `updated_at` is the incremental-cache key."""
    return {
        "number": pr["number"],
        "title": pr.get("title", ""),
        "author": actor_login(pr.get("user")),
        "merged_by": actor_login(pr.get("merged_by")),
        "created_at": pr.get("created_at"),
        "updated_at": pr.get("updated_at"),
        "merged_at": pr.get("merged_at"),
        "closed_at": pr.get("closed_at"),
        "url": pr.get("html_url"),
        "labels": [l.get("name") for l in pr.get("labels", [])],
        "event_count": len(events),
    }


# ── incremental cache + output ──────────────────────────────────────────────
def load_cache(path):
    """
    Open the existing output JSON and index it by PR number.

    Returns {pr_number: {"summary": <pr dict>, "events": [<event>, ...]}}
    so the main loop can look up any PR in O(1) and decide whether to reuse
    or re-fetch it.  Returns {} if the file is absent or unreadable.
    """
    if not path.exists():
        print(f"  No existing file at {path} — starting fresh.", flush=True)
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"  ! Could not read {path} ({e}) — starting fresh.", flush=True)
        return {}

    # Group events by PR number
    ev_by_pr = collections.defaultdict(list)
    for e in data.get("events", []):
        ev_by_pr[e["pr"]].append(e)

    # Index PR summaries
    cache = {}
    for p in data.get("pull_requests", []):
        cache[p["number"]] = {
            "summary": p,
            "events":  ev_by_pr[p["number"]],
        }

    print(f"  Opened {path}: {len(cache)} PRs, "
          f"{sum(len(v['events']) for v in cache.values())} events cached.",
          flush=True)
    return cache


def save_output(path, repo, results, include_body_edits):
    """Flatten {number: {summary, events}} into the on-disk JSON shape."""
    records = [results[n]["summary"] for n in sorted(results)]
    events = [e for n in sorted(results) for e in results[n]["events"]]
    events.sort(key=lambda e: e["timestamp"])
    output = {
        "meta": {
            "repository": repo,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "merged_pr_count": len(records),
            "event_count": len(events),
            "body_edits_included": include_body_edits,
            "event_types": sorted({e["type"] for e in events}),
        },
        "pull_requests": records,
        "events": events,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return len(events), len(records)


# ── main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo", default=DEFAULT_REPO,
                        help=f"owner/repo (default: {DEFAULT_REPO})")
    parser.add_argument("--out", default=str(DEFAULT_OUT),
                        help=f"output JSON path (default: {DEFAULT_OUT})")
    parser.add_argument("--refresh", action="store_true",
                        help="ignore the cache and rebuild every PR from scratch")
    parser.add_argument("--no-body-edits", action="store_true",
                        help="skip GraphQL body-edit enrichment")
    parser.add_argument("--limit", type=int, default=0,
                        help="process only the first N merged PRs (debugging)")
    args = parser.parse_args()

    if shutil.which("gh") is None:
        sys.exit("The GitHub CLI (`gh`) is not on PATH. Install it from "
                 "https://cli.github.com and run `gh auth login`.")
    if "/" not in args.repo:
        sys.exit("--repo must be in 'owner/repo' form")
    owner, repo = args.repo.split("/", 1)

    include_body_edits = not args.no_body_edits
    out_path = Path(args.out)

    cache = {} if args.refresh else load_cache(out_path)

    merged = list_merged_prs(owner, repo)
    if args.limit:
        merged = merged[:args.limit]

    # Seed results with the cache so a mid-run crash never drops prior data.
    results = dict(cache)
    reused = fetched = 0

    try:
        for i, pr in enumerate(merged, 1):
            number = pr["number"]
            cached = cache.get(number)

            # Skip if already in the cache AND GitHub hasn't touched it since.
            # GitHub bumps updated_at on every comment, review, label, or merge,
            # so a matching timestamp means nothing new has happened.
            # If the cached entry pre-dates the updated_at field (legacy), we
            # treat it as stale and re-fetch once to prime the key.
            cached_updated = cached["summary"].get("updated_at") if cached else None
            pr_updated     = pr.get("updated_at")
            already_done   = (
                cached is not None
                and not args.refresh
                and cached_updated is not None
                and cached_updated == pr_updated
            )
            if already_done:
                results[number] = cached
                reused += 1
                continue

            print(f"  [{i}/{len(merged)}] PR #{number}: {pr.get('title', '')[:58]}",
                  flush=True)
            merged_by, body_edits = fetch_pr_meta(
                owner, repo, number, pr.get("created_at"))
            pr["merged_by"] = merged_by or pr.get("merged_by")
            events = collect_pr_events(owner, repo, pr, body_edits, include_body_edits)
            results[number] = {"summary": summarise_pr(pr, events), "events": events}
            fetched += 1
    except (Exception, KeyboardInterrupt) as e:
        n_ev, n_pr = save_output(out_path, args.repo, results, include_body_edits)
        print(f"\n! Interrupted: {type(e).__name__}: {e}", flush=True)
        print(f"  Checkpoint saved ({n_pr} PRs, {n_ev} events) -> {out_path}\n"
              f"  Re-run the same command to resume; cached PRs will be skipped.",
              flush=True)
        sys.exit(1)

    n_ev, n_pr = save_output(out_path, args.repo, results, include_body_edits)
    print(f"\nDone. {reused} PRs reused from cache, {fetched} (re)fetched.", flush=True)
    print(f"Wrote {n_ev} events from {n_pr} merged PRs -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
