#!/usr/bin/env python3
"""
Check that every in-EMD JSON-LD cross-reference points to a file that exists.

For each JSON record in a directory that has a sibling `_context`, walk the
top-level fields. A field is an *in-EMD reference* iff the sibling `_context`
declares BOTH:
    "@type":    "@id"
    "@context": "https://emd.mipcvs.dev/{dir}/_context"
Values on such fields must exist as `{dir}/{value}.json` at the repo root.

External contexts (constants.mipcvs.dev/...) and fields without a nested
`@context` mapping (e.g. `references` carrying DOI URLs) are treated as
external and skipped.

Outputs:
  - Human-readable table on stdout
  - Markdown summary appended to $GITHUB_STEP_SUMMARY (if set)
  - Counts appended to $GITHUB_OUTPUT (if set): compliant, total, missing
  - Exit code 0 if every in-EMD reference resolves, 1 otherwise.

Pure standard library. Runs on any Python >= 3.8.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EMD_BASE = "https://emd.mipcvs.dev/"
CONTEXT_SUFFIX = "/_context"

# Files inside a directory that carry a _context but are NOT record files.
NON_RECORD_FILES = {"_context", "_graph.json", "output.json"}
MAX_BROKEN_IN_TABLE = 200  # cap the detail table so summary stays under GitHub limits



def load_context(context_path: Path) -> dict:
    """Return the `@context` mapping from a directory-level `_context` file."""
    with context_path.open() as f:
        return json.load(f).get("@context", {})


def resolve_in_emd_target_dir(ctx_url: str) -> str | None:
    """
    If `ctx_url` names an in-EMD context (e.g. https://emd.mipcvs.dev/model_family/_context),
    return the target directory name (e.g. `model_family`). Otherwise None.
    """
    if not isinstance(ctx_url, str):
        return None
    if not ctx_url.startswith(EMD_BASE) or not ctx_url.endswith(CONTEXT_SUFFIX):
        return None
    return ctx_url[len(EMD_BASE):-len(CONTEXT_SUFFIX)]


def is_id_reference(field_def) -> bool:
    """A field def is an @id reference iff it's a dict with `@type == '@id'`."""
    return isinstance(field_def, dict) and field_def.get("@type") == "@id"


def flatten_values(value):
    """Flatten a scalar / list / nested-list into leaf string values."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out = []
        for v in value:
            out.extend(flatten_values(v))
        return out
    return []


def normalise_id(v: str) -> str:
    """Strip a leading './' so `./foo` and `foo` both target `foo.json`."""
    return v[2:] if v.startswith("./") else v



def check_file(json_path: Path, context: dict, results: list) -> None:
    """Extract all in-EMD references from one JSON record and check their targets."""
    try:
        with json_path.open() as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        results.append({
            "source": str(json_path.relative_to(REPO_ROOT)),
            "field": "(parse error)",
            "value": f"line {e.lineno} col {e.colno}",
            "target": "",
            "exists": False,
        })
        return

    if not isinstance(data, dict):
        return
    # Only inspect records that opt in to this directory's context.
    if data.get("@context") not in ("_context", "_context.json"):
        return

    for field_name, field_def in context.items():
        if field_name.startswith("@"):
            continue
        if not is_id_reference(field_def):
            continue
        target_dir = resolve_in_emd_target_dir(field_def.get("@context", ""))
        if target_dir is None:
            continue  # external context (constants.mipcvs.dev/…) — out of scope
        if field_name not in data:
            continue

        for value in flatten_values(data[field_name]):
            # Skip absolute URLs — treated as external overrides
            if "://" in value:
                continue
            v = normalise_id(value)
            target_path = REPO_ROOT / target_dir / f"{v}.json"
            results.append({
                "source": str(json_path.relative_to(REPO_ROOT)),
                "field": field_name,
                "value": value,
                "target": f"{target_dir}/{v}.json",
                "exists": target_path.is_file(),
            })



def emit_stdout(results, compliant, total, missing):
    """Human-readable table for the workflow log."""
    print(f"\nEMD links — {compliant}/{total} compliant, {len(missing)} broken\n")
    if not missing:
        print("All in-repo references resolve.")
        return
    src_w = max(len(r["source"]) for r in missing)
    fld_w = max(len(r["field"]) for r in missing)
    print(f"{'SOURCE':<{src_w}}  {'FIELD':<{fld_w}}  MISSING TARGET")
    print("-" * (src_w + fld_w + 40))
    for r in missing:
        print(f"{r['source']:<{src_w}}  {r['field']:<{fld_w}}  {r['target']}")


def emit_step_summary(path: str, results, compliant, total, missing) -> None:
    """Append a markdown report to $GITHUB_STEP_SUMMARY."""
    by_dir: dict[str, dict[str, int]] = {}
    for r in results:
        d = r["source"].split("/", 1)[0]
        b = by_dir.setdefault(d, {"total": 0, "compliant": 0})
        b["total"] += 1
        if r["exists"]:
            b["compliant"] += 1

    with open(path, "a") as f:
        f.write("## EMD links\n\n")
        f.write(f"**{compliant}/{total} compliant · {len(missing)} broken**\n\n")

        f.write("### By directory\n\n")
        f.write("| Directory | Compliant | Total |\n|---|---:|---:|\n")
        for d in sorted(by_dir):
            b = by_dir[d]
            f.write(f"| `{d}` | {b['compliant']} | {b['total']} |\n")
        f.write("\n")

        if missing:
            f.write("### Broken references\n\n")
            f.write("| Source file | Field | Missing target |\n|---|---|---|\n")
            for r in missing[:MAX_BROKEN_IN_TABLE]:
                f.write(f"| `{r['source']}` | `{r['field']}` | `{r['target']}` |\n")
            if len(missing) > MAX_BROKEN_IN_TABLE:
                f.write(f"\n_+ {len(missing) - MAX_BROKEN_IN_TABLE} more not shown_\n")
            f.write("\n")


def emit_outputs(path: str, compliant, total, missing) -> None:
    """Append counts to $GITHUB_OUTPUT for downstream steps to read."""
    with open(path, "a") as f:
        f.write(f"compliant={compliant}\n")
        f.write(f"total={total}\n")
        f.write(f"missing={len(missing)}\n")



def main() -> int:
    all_results: list[dict] = []

    for context_path in sorted(REPO_ROOT.glob("*/_context")):
        try:
            context = load_context(context_path)
        except json.JSONDecodeError as e:
            print(f"WARN: cannot parse {context_path}: {e}", file=sys.stderr)
            continue

        source_dir = context_path.parent
        for json_path in sorted(source_dir.glob("*.json")):
            if json_path.name in NON_RECORD_FILES:
                continue
            check_file(json_path, context, all_results)

    total = len(all_results)
    missing = [r for r in all_results if not r["exists"]]
    compliant = total - len(missing)

    emit_stdout(all_results, compliant, total, missing)

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        emit_step_summary(summary_path, all_results, compliant, total, missing)

    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        emit_outputs(output_path, compliant, total, missing)

    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
