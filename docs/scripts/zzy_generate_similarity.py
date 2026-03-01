#!/usr/bin/env python3
"""
zzy_generate_similarity.py
===========================
Generate Similarity.html for every content subdirectory under
docs/EMD_Repository/.

Runs after all content generators (zzy_) and before the index generator (zzz_).
Dynamically discovers subdirs — no hardcoded list needed.

Endpoint mapping
----------------
Directory name is lowercased with underscores to derive the cmipld endpoint.
Override ENDPOINT_OVERRIDES for dirs whose name doesn't match their endpoint.
"""

import sys
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────────
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

# ── imports ────────────────────────────────────────────────────────────────
try:
    from helpers.data_loader import init_loader, fetch_data
except ImportError as e:
    sys.exit(f"Cannot import helpers.data_loader: {e}")

try:
    from cmipld.utils.similarity.folder_similarity import FolderSimilarity
except ImportError as e:
    sys.exit(f"Cannot import FolderSimilarity: {e}")

# ── endpoint overrides ─────────────────────────────────────────────────────
# When a directory name doesn't match its cmipld endpoint, list it here.
# Key = clean directory stem (e.g. "Component_Families")
# Val = cmipld endpoint string (e.g. "model_family")
ENDPOINT_OVERRIDES = {
    "Component_Families":            "model_family",
    "Earth_System_Model_Families":   "model_family",
    "Models":                        "model",
    "Model_Components":              "model_component",
    "Horizontal_Computational_Grids": "horizontal_computational_grid",
    "Vertical_Computational_Grids":  "vertical_computational_grid",
}


def _endpoint(dir_stem: str) -> str:
    """Derive the cmipld endpoint from a directory stem."""
    return ENDPOINT_OVERRIDES.get(dir_stem, dir_stem.lower())


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
    _cache: dict[str, list] = {}   # endpoint → items (avoid refetching)

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

        items = _cache[endpoint]
        print(f"  Items    : {len(items)}", flush=True)

        if len(items) < 2:
            print(f"  ⏭  Skipped — need ≥ 2 items (got {len(items)})", flush=True)
            skipped += 1
            continue

        try:
            fs = FolderSimilarity(
                endpoint=endpoint,
                items=items,
                label=stem.replace("_", " "),
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
