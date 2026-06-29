#!/usr/bin/env python3
"""
check_links.py
==============
Verify that every link in an EMD JSON file resolves.

How it works
------------
Each src-data file lives in a folder with a `_context` file alongside it.
The `_context` declares which top-level fields are *links* (`"@type": "@id"`)
and, for each, the remote `@context` URL of the vocabulary the link points
into. That remote context carries an `@base` — the URL prefix every value of
that field is appended to.

For each `@id`-typed field on the loaded file, this script:

  1. Reads the field's value(s).
  2. If the value is already an absolute URL (http/https), checks it directly.
  3. Otherwise, fetches the field's remote context, reads its `@base`, and
     builds `<base><value>`.
  4. Calls `cmipld.client.check_url_exists` on each resulting URL.

Empty strings and `_no response_` placeholders are skipped (not flagged) —
those are EMD's way of marking "not yet filled in" and aren't link errors.

Usage
-----
    python docs/scripts/check_links.py horizontal_grid_cell/g110.json
    python docs/scripts/check_links.py model/canesm5-1.json --verbose
    python docs/scripts/check_links.py model/canesm5-1.json --quiet      # only failures

Exit code: 0 if every link resolves, 1 if any failed (CI-friendly).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Iterable

# cmipld provides the LDR client, which knows the alt-base mappings (so
# https://emd.mipcvs.dev/... is checked against wcrp-cmip.github.io/...
# transparently).
import cmipld

# Cache fetched remote contexts so the same `@base` lookup isn't repeated
# for every value in a list field.
_CTX_CACHE: dict[str, dict] = {}

# Placeholders that mean "unset" — not real links.
_PLACEHOLDERS = {"", "not specified", "_no response_", "none"}


def _is_absolute(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def _flatten(value: Any) -> Iterable[str]:
    """Yield string leaves from a string, list, or nested-list field value."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _flatten(item)
    # other types (numbers, bools, None) aren't links — silently ignore


def _fetch_context(ctx_url: str) -> dict:
    """
    Fetch a remote `_context` document and return its `@context` dict.

    Strategy: resolve the canonical URL via cmipld's `test_load` (which maps
    e.g. https://constants.mipcvs.dev → wcrp-cmip.github.io), then fetch
    that resolved URL directly with urllib. The `preview` field from
    test_load is unreliable for large contexts (it's a truncated snippet),
    so we always fetch the real document.
    """
    if ctx_url in _CTX_CACHE:
        return _CTX_CACHE[ctx_url]

    # Step 1: ask cmipld where this URL actually lives on GitHub Pages.
    try:
        info = cmipld.client.test_load(ctx_url)
        document_url = info.get("documentUrl") if info.get("success") else None
    except Exception:
        document_url = None

    # Step 2: fetch the full JSON-LD doc from the resolved URL.
    ctx: dict = {}
    for try_url in filter(None, [document_url, ctx_url]):
        try:
            req = urllib.request.Request(try_url, headers={"Accept": "application/ld+json, application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                doc = json.loads(resp.read().decode("utf-8"))
            if isinstance(doc, dict):
                ctx = doc.get("@context", {})
                if isinstance(ctx, dict):
                    break
                ctx = {}
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
            continue

    _CTX_CACHE[ctx_url] = ctx
    return ctx


def _base_for(ctx_url: str) -> str | None:
    """Get the `@base` URL declared in a remote context. None if missing."""
    ctx = _fetch_context(ctx_url)
    return ctx.get("@base")


def load_local_context(file_path: Path) -> dict:
    """Load the `_context` sibling file. Errors are fatal — a context is required."""
    ctx_path = file_path.parent / "_context"
    if not ctx_path.is_file():
        sys.exit(f"❌ No _context file alongside {file_path} (looked for {ctx_path})")
    with ctx_path.open(encoding="utf-8") as fh:
        return json.load(fh).get("@context", {})


def link_fields(local_ctx: dict) -> dict[str, str | None]:
    """
    Return {field_name: remote_context_url_or_None} for every `@type: @id` field.

    A field with no `@context` (like `references`) is still a link field, but
    its values must be absolute URLs — we record that with None.
    """
    fields: dict[str, str | None] = {}
    for key, spec in local_ctx.items():
        if key.startswith("@"):
            continue
        if isinstance(spec, dict) and spec.get("@type") == "@id":
            fields[key] = spec.get("@context")  # may be None
    return fields


def check_file(file_path: Path, verbose: bool = True, quiet: bool = False) -> int:
    """Check every link in `file_path`. Returns count of failures."""
    with file_path.open(encoding="utf-8") as fh:
        data = json.load(fh)

    local_ctx = load_local_context(file_path)
    fields    = link_fields(local_ctx)

    if not fields:
        if not quiet:
            print(f"  (no link fields declared in {file_path.parent.name}/_context)")
        return 0

    failures = 0
    checked  = 0

    for field, remote_ctx_url in fields.items():
        if field not in data:
            continue
        values = list(_flatten(data[field]))
        if not values:
            continue

        # Resolve base once per field.
        base: str | None = None
        if remote_ctx_url:
            base = _base_for(remote_ctx_url)
            if base is None and not quiet:
                print(f"  ⚠ {field}: could not read @base from {remote_ctx_url}")

        for raw in values:
            value = raw.strip() if isinstance(raw, str) else raw
            # Skip placeholders — these mark "unset", not broken links.
            if isinstance(value, str) and value.lower() in _PLACEHOLDERS:
                continue

            # Build the URL to check.
            if _is_absolute(value):
                url = value
            elif base:
                url = base.rstrip("/") + "/" + value
            else:
                # Relative value, no base available — can't check.
                if not quiet:
                    print(f"  ⚠ {field} = '{value}': no base URL — cannot check")
                continue

            checked += 1
            try:
                ok = cmipld.client.check_url_exists(url)
                err_note = ""
            except Exception as e:
                ok = False
                err_note = f"  ({type(e).__name__}: {e})"

            if ok:
                if verbose and not quiet:
                    print(f"  ✓ {field}: {url}")
            else:
                failures += 1
                print(f"  ✗ {field}: {url}{err_note}")

    if not quiet:
        status = "OK" if failures == 0 else f"{failures} broken"
        print(f"\n{file_path}: {checked} link(s) checked — {status}")

    return failures


def main() -> int:
    p = argparse.ArgumentParser(
        description="Resolve and validate every link in an EMD JSON file."
    )
    p.add_argument("file", help="Path to the JSON file to check.")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Show every URL checked (default: only failures + summary).")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="Show only broken links; suppress summary.")
    args = p.parse_args()

    path = Path(args.file).expanduser().resolve()
    if not path.is_file():
        sys.exit(f"❌ File not found: {path}")

    # `verbose` and `quiet` are mutually exclusive; quiet wins if both are set.
    verbose = args.verbose and not args.quiet
    failures = check_file(path, verbose=verbose, quiet=args.quiet)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
