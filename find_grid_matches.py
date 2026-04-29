#!/usr/bin/env python3
"""
find_grid_matches.py
====================
Reads all closed pull requests from the EMD GitHub repository.
For each PR whose submitted JSON is a `horizontal_grid_cell` record,
finds the closest matching entry in Horizontal_Grid_Cells_raw.json,
ignoring the @id, description, and alias fields when comparing.

Usage
-----
  python3 find_grid_matches.py                     # uses gh's inferred repo
  python3 find_grid_matches.py --repo ORG/REPO
  python3 find_grid_matches.py --limit 50          # cap PR fetch (default 200)
  python3 find_grid_matches.py --threshold 0.6     # hide matches below score
  python3 find_grid_matches.py --json              # emit JSON instead of table
  python3 find_grid_matches.py --verbose           # per-field diff for each PR

Outputs a ranked match table, one row per closed horizontal_grid_cell PR.

Requirements
------------
  gh CLI authenticated:  gh auth status

Similarity metric
-----------------
Fields compared (ignoring @id, description, alias, @context, @type,
ui_label, validation_key):

  * Categorical / string  -> 1.0 if equal (case-insensitive), else 0.0
  * Numeric               -> 1 - |a-b| / max(|a|, |b|, 1), clamped [0,1]
  * List                  -> Jaccard similarity of normalised string sets
  * Empty / missing on    -> wildcard: field excluded from the average,
    either side             not penalised

Overall score = mean of all evaluable per-field scores.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SKIP_FIELDS = {
    "@id", "@context", "@type",
    "description", "alias",
    "ui_label", "validation_key",
}

_SCRIPT_DIR = Path(__file__).resolve().parent
_REFERENCE_CANDIDATES = [
    _SCRIPT_DIR / "docs" / "EMD_Repository" / "Horizontal_Grid_Cells_raw.json",
    _SCRIPT_DIR.parent / "docs" / "EMD_Repository" / "Horizontal_Grid_Cells_raw.json",
]

TYPE_MARKER = "horizontal_grid_cell"


# ---------------------------------------------------------------------------
# GitHub helpers (gh CLI)
# ---------------------------------------------------------------------------

def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def fetch_closed_prs(repo: str | None, limit: int) -> list[dict]:
    cmd = ["gh", "pr", "list", "--state", "closed",
           "--limit", str(limit),
           "--json", "number,title,body"]
    if repo:
        cmd += ["--repo", repo]
    print(f"  Fetching up to {limit} closed PRs...", flush=True)
    return json.loads(_run(cmd))


# ---------------------------------------------------------------------------
# PR body parsing
# ---------------------------------------------------------------------------

_JSON_BLOCK = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


def extract_json_from_body(body: str) -> list[dict]:
    """Return all JSON objects found in ```json ... ``` blocks."""
    results = []
    for m in _JSON_BLOCK.finditer(body or ""):
        try:
            results.append(json.loads(m.group(1)))
        except json.JSONDecodeError:
            pass
    return results


def is_horizontal_grid_cell(pr_title: str, record: dict) -> bool:
    """True when the record or PR title identifies it as a horizontal_grid_cell."""
    types = record.get("@type", [])
    if isinstance(types, str):
        types = [types]
    if any(TYPE_MARKER in t for t in types):
        return True
    return TYPE_MARKER in pr_title.lower().replace(" ", "_")


# ---------------------------------------------------------------------------
# Similarity
# ---------------------------------------------------------------------------

def _normalise(v: Any) -> Any:
    """Coerce empty-string-like / None values to None; strip empty list items."""
    if v == "" or v is None:
        return None
    if isinstance(v, list):
        cleaned = [x for x in v if x != "" and x is not None]
        return cleaned if cleaned else None
    return v


def _is_numeric(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _field_similarity(a: Any, b: Any) -> float | None:
    """
    Return [0, 1] similarity, or None when either side is missing/empty
    (wildcard: exclude from mean rather than penalise).
    """
    a, b = _normalise(a), _normalise(b)

    if a is None and b is None:
        return None
    if a is None or b is None:
        return None  # wildcard

    if _is_numeric(a) and _is_numeric(b):
        denom = max(abs(a), abs(b), 1e-9)
        return max(0.0, 1.0 - abs(a - b) / denom)

    if isinstance(a, list) or isinstance(b, list):
        sa = {str(x).strip().lower() for x in (a if isinstance(a, list) else [a])}
        sb = {str(x).strip().lower() for x in (b if isinstance(b, list) else [b])}
        union = sa | sb
        return len(sa & sb) / len(union) if union else None

    return 1.0 if str(a).strip().lower() == str(b).strip().lower() else 0.0


def compare(candidate: dict, reference: dict) -> tuple[float, dict[str, float]]:
    """Return (overall_score, {field: score}) for candidate vs reference."""
    all_keys = (set(candidate) | set(reference)) - SKIP_FIELDS
    scores: dict[str, float] = {}
    for key in sorted(all_keys):
        s = _field_similarity(candidate.get(key), reference.get(key))
        if s is not None:
            scores[key] = round(s, 4)
    overall = (sum(scores.values()) / len(scores)) if scores else 0.0
    return round(overall, 4), scores


def find_best_match(
    candidate: dict, references: list[dict]
) -> tuple[dict | None, float, dict[str, float]]:
    """Return (best_ref, best_score, per_field_scores)."""
    best_ref, best_score, best_fields = None, -1.0, {}
    for ref in references:
        score, fields = compare(candidate, ref)
        if score > best_score:
            best_ref, best_score, best_fields = ref, score, fields
    return best_ref, best_score, best_fields


# ---------------------------------------------------------------------------
# Reference data loading
# ---------------------------------------------------------------------------

def load_reference(path: Path | None) -> list[dict]:
    if path is None:
        for c in _REFERENCE_CANDIDATES:
            if c.exists():
                path = c
                break
    if path is None or not path.exists():
        sys.exit(
            "ERROR: Could not find Horizontal_Grid_Cells_raw.json.\n"
            "Pass --reference /path/to/Horizontal_Grid_Cells_raw.json"
        )
    print(f"  Reference file: {path}", flush=True)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else list(data.values())


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _score_bar(score: float, width: int = 20) -> str:
    filled = round(score * width)
    return "=" * filled + "-" * (width - filled)


def _marker(s: float | None) -> str:
    if s is None:  return " ~ "   # wildcard / not compared
    if s >= 1.0:   return " ok"
    if s >= 0.5:   return " ~="
    return " !!"


def _diff_lines(candidate: dict, ref: dict, field_scores: dict) -> list[str]:
    lines = []
    all_keys = sorted((set(candidate) | set(ref)) - SKIP_FIELDS)
    for k in all_keys:
        a = _normalise(candidate.get(k))
        b = _normalise(ref.get(k))
        if a is None and b is None:
            continue
        s    = field_scores.get(k)
        mark = _marker(s)
        a_s  = repr(a)[:38]
        b_s  = repr(b)[:38]
        lines.append(f"    [{mark}]  {k:<28}  PR={a_s:<40}  REF={b_s}")
    return lines


def print_table(results: list[dict], threshold: float, verbose: bool):
    sep = "-" * 105
    print()
    print(sep)
    print(f"  {'PR':>5}  {'SCORE':>6}  {'MATCH_ID':<20}  PR_VALIDATION_KEY")
    print(sep)
    shown = 0
    for r in results:
        if r["best_score"] < threshold:
            continue
        shown += 1
        score_str = f"{r['best_score']:.1%}"
        match_id  = r["match_id"] or "(no registered match)"
        pr_key    = r["pr_validation_key"] or "(none)"
        bar       = _score_bar(r["best_score"])
        print(f"  #{r['pr_number']:>4}  {score_str:>6}  {match_id:<20}  {pr_key}")
        print(f"         [{bar}]  \"{r['pr_title'][:65]}\"")
        if verbose and r["field_scores"]:
            for line in _diff_lines(r["candidate"], r["match_record"], r["field_scores"]):
                print(line)
        print()
    if shown == 0:
        print("  (no results above threshold)")
    print(sep)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Match closed horizontal_grid_cell PRs against registered entries."
    )
    parser.add_argument(
        "--repo", help="GitHub repo slug (ORG/NAME). Default: inferred by gh CLI."
    )
    parser.add_argument(
        "--limit", type=int, default=200,
        help="Maximum number of closed PRs to fetch (default: 200)."
    )
    parser.add_argument(
        "--threshold", type=float, default=0.0,
        help="Only show matches at or above this score (0-1, default: 0 = show all)."
    )
    parser.add_argument(
        "--reference", type=Path, default=None,
        help="Path to Horizontal_Grid_Cells_raw.json (auto-detected if omitted)."
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Emit results as JSON instead of a table."
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print per-field diff for every match."
    )
    args = parser.parse_args()

    references = load_reference(args.reference)
    print(f"  {len(references)} reference records loaded.", flush=True)

    prs = fetch_closed_prs(args.repo, args.limit)
    print(f"  {len(prs)} closed PRs fetched.", flush=True)

    results: list[dict] = []
    skipped = 0

    for pr in prs:
        records = extract_json_from_body(pr.get("body") or "")
        matched_any = False
        for record in records:
            if not is_horizontal_grid_cell(pr["title"], record):
                continue
            matched_any = True
            best_ref, best_score, field_scores = find_best_match(record, references)
            results.append({
                "pr_number":            pr["number"],
                "pr_title":             pr["title"],
                "pr_validation_key":    record.get("validation_key"),
                "best_score":           best_score,
                "match_id":             best_ref.get("@id") if best_ref else None,
                "match_validation_key": best_ref.get("validation_key") if best_ref else None,
                "field_scores":         field_scores,
                "candidate":            record,
                "match_record":         best_ref or {},
            })
            # A PR typically has one grid-cell record; break after the first.
            # Remove this break to handle PRs that embed multiple records.
            break
        if not matched_any:
            skipped += 1

    print(
        f"\n  {len(results)} horizontal_grid_cell PR(s) found,"
        f" {skipped} PR(s) skipped (different type).\n",
        flush=True,
    )

    # Sort best match first
    results.sort(key=lambda r: r["best_score"], reverse=True)

    if args.json:
        out = [
            {k: v for k, v in r.items() if k not in ("candidate", "match_record")}
            for r in results
            if r["best_score"] >= args.threshold
        ]
        print(json.dumps(out, indent=2))
    else:
        print_table(results, args.threshold, args.verbose)
        poor = [r for r in results if r["best_score"] < 0.5]
        if poor:
            print(f"\n  WARNING: {len(poor)} PR(s) with best score < 50%"
                  " (no close registered match):")
            for r in poor:
                print(f"     PR #{r['pr_number']:>4}  score={r['best_score']:.1%}"
                      f"  key={r['pr_validation_key']}")
        print()


if __name__ == "__main__":
    main()
