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
  jinja2          — (used by other generators, installed alongside)
"""

import sys
from pathlib import Path

# ── Early dependency check ──────────────────────────────────────────────────
def _check_deps():
    missing = []
    for pkg in ('numpy', 'cmipld'):
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"  ⚠ Missing dependencies: {', '.join(missing)}", flush=True)
        print(f"    Install with: pip install {' '.join(missing)}", flush=True)
        print(f"    Or add to requirements.txt and re-run.", flush=True)
        sys.exit(1)

_check_deps()

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

# ── imports ─────────────────────────────────────────────────────────────────
try:
    from helpers.data_loader import init_loader, fetch_data
except ImportError as e:
    sys.exit(f"Cannot import helpers.data_loader: {e}")

try:
    from cmipld.utils.similarity.folder_similarity import (
        FolderSimilarity, _get_field_value,
    )
except ImportError as e:
    sys.exit(f"Cannot import FolderSimilarity: {e}")


# ── per-directory configuration ─────────────────────────────────────────────

# Maps directory stem → cmipld endpoint string.
ENDPOINT_OVERRIDES: dict[str, str] = {
    "Component_Families":            "model_family",
    "Earth_System_Model_Families":   "model_family",
    "Models":                        "model",
    "Model_Components":              "model_component",
    "Horizontal_Computational_Grids": "horizontal_computational_grid",
    "Vertical_Computational_Grids":  "vertical_computational_grid",
}

# Pre-filter: keep only items where field == value.
# Format: {dir_stem: (field_suffix, required_value)}
PRE_FILTER: dict[str, tuple[str, str]] = {
    "Component_Families":          ("family_type", "component"),
    "Earth_System_Model_Families": ("family_type", "model"),
}

# Secondary client-side filter field (renders interactive buttons in HTML).
# Format: {dir_stem: field_suffix}
FILTER_FIELD: dict[str, str] = {
    "Component_Families":          "scientific_domains",
    "Earth_System_Model_Families": "scientific_domains",
}


def _endpoint(dir_stem: str) -> str:
    return ENDPOINT_OVERRIDES.get(dir_stem, dir_stem.lower())


def _pre_filter(items: list, field_suffix: str, required_value: str) -> list:
    """Keep only items where field_suffix == required_value."""
    kept = [
        item for item in items
        if _get_field_value(item, field_suffix) == required_value
    ]
    return kept


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

        # Fetch (cached per endpoint)
        if endpoint not in _cache:
            print(f"  Fetching {endpoint}…", flush=True)
            _cache[endpoint] = fetch_data(endpoint, depth=2)

        items = list(_cache[endpoint])  # copy so pre-filter doesn't mutate cache
        print(f"  Fetched  : {len(items)} items", flush=True)

        # Pre-filter
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

    if failed:
        sys.exit(1)


run()
