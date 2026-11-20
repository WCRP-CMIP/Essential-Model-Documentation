"""Run the EMD post-build steps on a site built by Zensical.

MkDocs ran src/mkdocs/hooks/post_build.py as a hook. Zensical runs no hooks, so
`make build` calls this file after `zensical build`. It runs the same function on
the built site in build/:

  1. strip number prefixes from folder and file names, and fix the links;
  2. write the root redirect;
  3. update docs/nav_order.json with any new pages;
  4. build the sidebar from it and inject it into every page;
  5. add search to standalone pages, analytics, and the 404 address lookup.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "mkdocs" / "hooks"))

import post_build  # noqa: E402

if __name__ == "__main__":
    post_build.on_post_build({"site_dir": ROOT / "build", "docs_dir": ROOT / "docs"})
