#!/usr/bin/env python3
"""
Generate Contributors.md from git history across all branches.

Runs during the MkDocs build via run_scripts.py.
Requires: cmipld package (pip install cmipld)
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
DOCS_DIR   = SCRIPT_DIR.parent

BRANCHES      = ["main", "src-data", "docs"]
OUTPUT_PATH   = DOCS_DIR / "Contributors.md"   # no numeric prefix


def main():
    print(f"Generating contributors page: {OUTPUT_PATH}", flush=True)

    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "cmipld.generate.get_contributors",
                "--md", str(OUTPUT_PATH),
                "--branches", *BRANCHES,
            ],
            capture_output=False,   # let output stream to console in real time
            cwd=str(DOCS_DIR.parent),
        )

        if result.returncode != 0:
            print(f"  ⚠ get_contributors exited {result.returncode}", flush=True)

    except FileNotFoundError:
        print("  ⚠ cmipld not installed — skipping contributors generation.", flush=True)
    except Exception as e:
        print(f"  ⚠ contributors generation failed: {e}", flush=True)
    finally:
        # The subprocess kills the LDR server when it exits. Restart it so
        # subsequent scripts (zzy_generate_similarity) can still fetch data.
        try:
            subprocess.run(["ldr", "server", "start"],
                           capture_output=True, timeout=15)
        except Exception:
            pass


main()
