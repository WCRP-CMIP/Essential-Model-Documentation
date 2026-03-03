#!/usr/bin/env python3
"""
zzy_generate_similarity.py
===========================
Generate Similarity.html for every content subdirectory under
docs/EMD_Repository/.

Endpoint overrides handle dirs whose name doesn't map cleanly to a cmipld
endpoint.  Pre-filters remove irrelevant items before building the matrix
(e.g. Component_Families only shows family_type=component).

Dependencies (must be installed before this script runs):
  numpy>=1.24.0   — matrix operations
  cmipld          — data fetching
"""

import sys
from pathlib import Path

# ── paths ───────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
DOCS_DIR   = SCRIPT_DIR.parent
REPO_ROOT  = DOCS_DIR.parent
EMD_DIR    = DOCS_DIR / "EMD_Repository"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

for candidate in [
    REPO_ROOT.parent / "CMIP-LD",
    Path.home() / "WIPwork" / "CMIP-LD",
]:
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
        break

# ── imports (non-fatal: warn and skip if unavailable) ───────────────────────
try:
    from helpers.data_loader import init_loader, fetch_data
except ImportError as e:
    print(f"  ⚠ zzy_generate_similarity: cannot import data_loader ({e}) — skipping.", flush=True)
    raise SystemExit(0)   # exit 0: skip gracefully, don't break the build

try:
    import numpy  # noqa: F401 — confirm numpy is available before we start
except ImportError:
    print("  ⚠ zzy_generate_similarity: numpy not installed — skipping.", flush=True)
    print("    Add 'numpy>=1.24.0' to requirements.txt.", flush=True)
    raise SystemExit(0)

try:
    from cmipld.utils.similarity.folder_similarity import (
        FolderSimilarity, _get_field_value,
    )
except ImportError as e:
    print(f"  ⚠ zzy_generate_similarity: cannot import FolderSimilarity ({e}) — skipping.", flush=True)
    raise SystemExit(0)


# ── per-directory configuration ─────────────────────────────────────────────

ENDPOINT_OVERRIDES: dict[str, str] = {
    "Component_Families":            "model_family",
    "Earth_System_Model_Families":   "model_family",
    "Models":                        "model",
    "Model_Components":              "model_component",
    "Horizontal_Computational_Grids": "horizontal_computational_grid",
    "Vertical_Computational_Grids":  "vertical_computational_grid",
    "Horizontal_Grid_Cells":         "horizontal_grid_cells",
}

PRE_FILTER: dict[str, tuple[str, str]] = {
    "Component_Families":          ("family_type", "component"),
    "Earth_System_Model_Families": ("family_type", "model"),
}

FILTER_FIELD: dict[str, str] = {
    "Component_Families":          "scientific_domains",
    "Earth_System_Model_Families": "scientific_domains",
}


def _endpoint(dir_stem: str) -> str:
    return ENDPOINT_OVERRIDES.get(dir_stem, dir_stem.lower())


def _pre_filter(items: list, field_suffix: str, required_value: str) -> list:
    return [item for item in items
            if _get_field_value(item, field_suffix) == required_value]


def run(use_embeddings: bool = True):
    init_loader()

    if not EMD_DIR.exists():
        print(f"  EMD_Repository not found at {EMD_DIR} — skipping.", flush=True)
        return

    subdirs = sorted(
        d for d in EMD_DIR.iterdir()
        if d.is_dir() and not d.name.startswith('.')
    )
    if not subdirs:
        print("  No subdirectories found in EMD_Repository.", flush=True)
        return

    ok = skipped = failed = 0
    _cache: dict[str, list] = {}

    for out_dir in subdirs:
        stem     = out_dir.name
        endpoint = _endpoint(stem)
        dest     = out_dir / FolderSimilarity.OUTPUT_FILENAME

        print(f"\n{'─'*60}", flush=True)
        print(f"  Dir      : {stem}", flush=True)
        print(f"  Endpoint : {endpoint}", flush=True)
        print(f"  Output   : {dest.relative_to(REPO_ROOT)}", flush=True)

        if endpoint not in _cache:
            print(f"  Fetching {endpoint}…", flush=True)
            _cache[endpoint] = fetch_data(endpoint, depth=2)

        items = list(_cache[endpoint])
        print(f"  Fetched  : {len(items)} items", flush=True)

        pf = PRE_FILTER.get(stem)
        if pf:
            field_suf, required = pf
            items = _pre_filter(items, field_suf, required)
            print(f"  Filtered : {len(items)} items (family_type={required})", flush=True)

        if len(items) < 2:
            print(f"  ⏭  Skipped — need ≥ 2 items (got {len(items)})", flush=True)
            skipped += 1
            continue

        try:
            fs = FolderSimilarity(
                endpoint=endpoint,
                items=items,
                label=stem.replace("_", " "),
                filter_field=FILTER_FIELD.get(stem),
                use_embeddings=use_embeddings,
            )
            fs.save(str(dest))
            print(f"  ✅ Written ({dest.stat().st_size // 1024} KB)", flush=True)
            ok += 1
        except ValueError as e:
            print(f"  ⏭  Skipped — {e}", flush=True)
            skipped += 1
        except Exception as e:
            print(f"  ❌ Failed  — {e}", flush=True)
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*60}", flush=True)
    print(f"  Similarity  ✅ {ok}  ⏭ {skipped}  ❌ {failed}", flush=True)
    print(f"{'='*60}\n", flush=True)

    # Log failures but don't abort the build — other pages still render fine
    if failed:
        print(f"  ⚠ {failed} Similarity page(s) failed — build continues.", flush=True)


run()
