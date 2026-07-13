#!/usr/bin/env python3
"""
pr_all_timeline.py
==================
Sibling of pr_timeline.py that collects EVERY pull request in a repository —
open, closed-not-merged, and merged — labelled with its status.

Per-PR summary adds two fields on top of what pr_timeline.py already writes:

  - status  : one of "open" | "closed" | "merged"
              ("closed" here means closed WITHOUT being merged.)
  - state   : the raw GitHub `state` string ("open" or "closed"), passed
              through untouched for anyone who wants the API-native value.

Events are the same seven types as pr_timeline.py. Open PRs simply have no
`merged` or `closed` event yet; closed-not-merged PRs have a `closed` event
but no `merged` one.

Meta block adds per-status counts:

  - pr_count           total PRs written
  - merged_pr_count    subset with a merge event
  - closed_pr_count    subset closed without being merged
  - open_pr_count      subset still open
  - includes_all_states: true    (sentinel — HTMLs can key off this)

Output: docs/assets/pr_all_timeline_data.json (separate file from
pr_timeline_data.json, so both can coexist).

Everything else — incremental caching by `updated_at`, checkpointing on
error, GraphQL enrichment for merged_by + body edits — is identical to
pr_timeline.py. See that script's docstring for architecture notes.

Usage
-----
    python pr_all_timeline.py                  # incremental
    python pr_all_timeline.py --refresh        # rebuild from scratch
    python pr_all_timeline.py --no-body-edits  # skip GraphQL body edits
    python pr_all_timeline.py --limit 5        # debug: first 5 PRs
    python pr_all_timeline.py --status open    # restrict to one status

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
DEFAULT_OUT  = SCRIPT_DIR.parent / "assets" / "pr_all_timeline_data.json"
PER_PAGE     = 100
MAX_RETRIES  = 4          # transient-error retries per gh call

STATUS_MERGED = "merged"
STATUS_CLOSED = "closed"   # closed WITHOUT being merged
STATUS_OPEN   = "open"


# ── gh CLI helpers ──────────────────────────────────────────────────────────
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


# ── data collection ─────────────────────────────────────────────────────────
def actor_login(node):
    """Login from a GitHub user object, or pass through an existing login string."""
    if not node:
        return None
    if isinstance(node, str):
        return node
    return node.get("login")


def classify_status(pr):
    """
    Bucket a PR into one of three statuses.

    GitHub's `state` is only "open" or "closed" — a merged PR is `state=closed`
    with `merged_at != null`. This helper splits closed into merged vs. closed
    -without-merge so downstream code can treat each cleanly.
    """
    if pr.get("merged_at"):
        return STATUS_MERGED
    if pr.get("state") == "closed":
        return STATUS_CLOSED
    return STATUS_OPEN


def list_all_prs(owner, repo, restrict_status=None):
    """
    Fetch every PR in the repo (state=all): open, closed, and merged.

    Unlike pr_timeline.list_merged_prs which uses a --jq filter to keep only
    merged PRs, we take everything and classify client-side. Ordering is by
    creation date ascending so the incremental loop processes oldest-first.
    """
    print(f"Fetching all pull requests for {owner}/{repo} ...", flush=True)
    args = [
        "api", "--paginate",
        "-H", "X-GitHub-Api-Version:2022-11-28",
        f"/repos/{owner}/{repo}/pulls"
        f"?state=all&sort=created&direction=asc&per_page={PER_PAGE}",
    ]
    values = _decode_concatenated(_run_gh(args))
    prs = []
    for v in values:
        if isinstance(v, list):
            prs.extend(v)

    counts = collections.Counter(classify_status(p) for p in prs)
    print(f"  found {len(prs)} PRs total: "
          f"{counts.get(STATUS_MERGED, 0)} merged, "
          f"{counts.get(STATUS_CLOSED, 0)} closed (no merge), "
          f"{counts.get(STATUS_OPEN, 0)} open",
          flush=True)

    if restrict_status:
        before = len(prs)
        prs = [p for p in prs if classify_status(p) == restrict_status]
        print(f"  filtered to status={restrict_status}: {len(prs)}/{before}",
              flush=True)
    return prs


def fetch_pr_meta(owner, repo, number):
    """
    One GraphQL call returning (merged_by_login, body_edits).

    `merged_by` is absent from the REST list endpoint, and body-edit history is
    only exposed via GraphQL `userContentEdits` — so both come from here.
    Body edits coinciding with PR creation are dropped. `body_edits` is a list
    of (timestamp, editor) tuples. For open or closed-not-merged PRs the
    merged_by return value will be None; that's fine.
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
        if not ts:
            continue
        edits.append((ts, actor_login(node.get("editor"))))
    return merged_by, edits


def collect_pr_events(owner, repo, pr, body_edits, include_body_edits):
    """
    Same event menu as pr_timeline.py, but robust to PRs without a merge/close:

        opened, body_edit, comment, review_comment, review, merged, closed

    - `merged` is emitted only when merged_at is set (i.e. status == merged).
    - `closed` is emitted only when closed_at is set AND it differs from
      merged_at (which is exactly when the PR was closed without being merged).
    - Open PRs contribute the pre-merge subset of events; the "wait" for any
      terminal signal is implicitly still ongoing.
    """
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

    # 6. merged  (only for merged PRs)
    if pr.get("merged_at"):
        add("merged", pr.get("merged_at"), actor_login(pr.get("merged_by")))

    # 7. closed (only if the PR was closed without being merged, or closed
    #    at a distinct time from the merge — the latter can't really happen
    #    on GitHub but the check is cheap and matches pr_timeline.py)
    if pr.get("closed_at") and pr.get("closed_at") != pr.get("merged_at"):
        add("closed", pr.get("closed_at"), None)

    events.sort(key=lambda e: e["timestamp"])
    return events


def summarise_pr(pr, events):
    """Compact per-PR record — includes status/state fields for filtering."""
    return {
        "number": pr["number"],
        "title": pr.get("title", ""),
        "author": actor_login(pr.get("user")),
        "merged_by": actor_login(pr.get("merged_by")),
        "status": classify_status(pr),      # NEW: "open" | "closed" | "merged"
        "state": pr.get("state"),           # NEW: raw GitHub state ("open"/"closed")
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

    Returns {pr_number: {"summary": <pr dict>, "events": [<event>, ...]}} for
    O(1) lookup by the main loop. Returns {} if the file is absent or
    unreadable. Compatible with either pr_timeline_data.json or a prior
    pr_all_timeline_data.json — the extra `status` field on new records is
    additive, so old caches still load.
    """
    if not path.exists():
        print(f"  No existing file at {path} — starting fresh.", flush=True)
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"  ! Could not read {path} ({e}) — starting fresh.", flush=True)
        return {}

    ev_by_pr = collections.defaultdict(list)
    for e in data.get("events", []):
        ev_by_pr[e["pr"]].append(e)

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

    status_counts = collections.Counter(r.get("status") for r in records)

    output = {
        "meta": {
            "repository": repo,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pr_count": len(records),
            "merged_pr_count": status_counts.get(STATUS_MERGED, 0),
            "closed_pr_count": status_counts.get(STATUS_CLOSED, 0),
            "open_pr_count":   status_counts.get(STATUS_OPEN, 0),
            "event_count": len(events),
            "body_edits_included": include_body_edits,
            "event_types": sorted({e["type"] for e in events}),
            "includes_all_states": True,
        },
        "pull_requests": records,
        "events": events,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return len(events), len(records)


# ── main ────────────────────────────────────────────────────────────────────
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
                        help="process only the first N PRs (debugging)")
    parser.add_argument("--status", choices=[STATUS_OPEN, STATUS_CLOSED, STATUS_MERGED],
                        default=None,
                        help="restrict to a single status (default: all three)")
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

    prs = list_all_prs(owner, repo, restrict_status=args.status)
    if args.limit:
        prs = prs[:args.limit]

    # Seed results with the cache so a mid-run crash never drops prior data.
    # Only carry over cache entries for PRs still in `prs` (e.g. if the user
    # switched --status, the previously-cached other-status PRs get dropped).
    keep_numbers = {p["number"] for p in prs}
    results = {n: v for n, v in cache.items() if n in keep_numbers}
    reused = fetched = 0

    try:
        for i, pr in enumerate(prs, 1):
            number = pr["number"]
            cached = cache.get(number)

            # Skip if already cached AND GitHub hasn't touched it since.
            # `updated_at` bumps on every comment/review/label/merge/close, so
            # matching timestamps guarantee no change. Note: transitions like
            # open → merged always bump updated_at, so cache stays consistent.
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

            status = classify_status(pr)
            print(f"  [{i}/{len(prs)}] PR #{number} [{status}]: "
                  f"{pr.get('title', '')[:50]}", flush=True)

            merged_by, body_edits = fetch_pr_meta(owner, repo, number)
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

    # Final status breakdown, so the run log tells you what actually got saved.
    final_counts = collections.Counter(r["summary"].get("status") for r in results.values())
    print(f"\nDone. {reused} PRs reused from cache, {fetched} (re)fetched.", flush=True)
    print(f"Wrote {n_ev} events from {n_pr} PRs -> {out_path}", flush=True)
    print(f"  by status: "
          f"{final_counts.get(STATUS_MERGED, 0)} merged, "
          f"{final_counts.get(STATUS_CLOSED, 0)} closed, "
          f"{final_counts.get(STATUS_OPEN, 0)} open",
          flush=True)


if __name__ == "__main__":
    main()
