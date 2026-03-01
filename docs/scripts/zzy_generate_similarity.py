#!/usr/bin/env python3


import argparse
import sys
from pathlib import Path
import glob

# ── locate the repo root and add paths ─────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent           # docs/scripts/
DOCS_DIR   = SCRIPT_DIR.parent                         # docs/
REPO_ROOT  = DOCS_DIR.parent                           # repo root

# Add the helpers package
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import cmipld

# ── imports ─────────────────────────────────────────────────────────────────
try:
    from helpers.data_loader import init_loader, fetch_data
except ImportError as e:
    sys.exit(f"Cannot import helpers.data_loader: {e}\nRun from docs/scripts/ or repo root.")

try:
    from cmipld.utils.similarity.folder_similarity import FolderSimilarity
except ImportError as e:
    sys.exit(f"Cannot import FolderSimilarity: {e}")



emd = [i for i in glob.glob(f'>{DOCS_DIR}/*/') if 'EMD_Repository' in i]
folders = glob.glob(f'{emd}*')
print(folders)



def run(
    use_embeddings: bool = True,
    dry_run: bool = False,
):

    ok = skipped = failed = 0

    # Track which endpoints we've already fetched (avoid duplicate fetches for
    # dirs that share the same endpoint, e.g. 03 and 04 both use model_family)
    _cache: dict[str, list] = {}

    for out_dir in folders:
        name = out_dir.split('_')[1:]
        label = " ".join(name)
        endpoint = "_".join(name).lower()
        if not endpoint:
            print(f"  ⏭  Skipped — no endpoint mapping for {name}", flush=True)
            skipped += 1
            continue

        dest = out_dir / "001_Similarity.html"
        rel  = dest.relative_to(REPO_ROOT)

        print(f"\n{'─'*60}", flush=True)
        print(f"  Dir      : {label}", flush=True)
        print(f"  Endpoint : {endpoint}", flush=True)
        print(f"  Output   : {rel}", flush=True)

        if dry_run:
            print("  [dry-run] skipping.", flush=True)
            skipped += 1
            continue



        if len(items) < 2:
            print(f"  ⏭  Skipped — need ≥ 2 items (got {len(items)})", flush=True)
            skipped += 1
            continue

        try:
            fs = FolderSimilarity(
                endpoint=endpoint,
                items=items,
                label=label,
                use_embeddings=use_embeddings,
            )
            fs.save(str(dest))
            kb = dest.stat().st_size // 1024
            print(f"  ✅ Written ({kb} KB → {dest.name})", flush=True)
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
    print(f"  Similarity pages  ✅ {ok}  ⏭ {skipped}  ❌ {failed}", flush=True)
    print(f"{'='*60}\n", flush=True)

    if failed:
        sys.exit(1)


run()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

# [if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description="Generate 001_Similarity.html pages for all EMD output dirs."
#     )
#     parser.add_argument(
#         "--dir", "-d",
#         metavar="DIRNAME",
#         help="Only process one output dir by its basename, "
#              "e.g. --dir 05_Horizontal_Computational_Grids",
#     )
#     parser.add_argument(
#         "--no-embed",
#         action="store_true",
#         help="Skip sentence-transformer embeddings (field-level only, faster).",
#     )
#     parser.add_argument(
#         "--dry-run",
#         action="store_true",
#         help="Print targets but do not write any files.",
#     )

#     args = parser.parse_args()
#     run(
#         filter_dir=args.dir,
#         use_embeddings=not args.no_embed,
#         dry_run=args.dry_run,
#     )
