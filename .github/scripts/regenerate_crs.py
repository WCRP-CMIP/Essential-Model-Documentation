#!/usr/bin/env python3
"""
Regenerate / audit CRS strings in model JSON files.

Usage
-----
  # Fill blanks only (original behaviour)
  python regenerate_crs.py

  # Recompute every CRS from scratch, write if changed
  python regenerate_crs.py --rebuild

  # Check-only: report drift/errors but write nothing (exit 1 if any)
  python regenerate_crs.py --check

  # Specific files (any mode)
  python regenerate_crs.py --rebuild model1.json model2.json

Modes
-----
  (default)  Skip files that already have a non-empty 'crs' field.
  --rebuild  Recompute every CRS from dynamic/embedded/coupled fields and
             overwrite if the result differs from what is stored.
  --check    Like --rebuild but never writes; exits 1 if any file has drift,
             a missing CRS, or a validation error.  Suitable for CI.
"""

import argparse
import json
import glob
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Import CRS utilities from the sibling CMIP-LD checkout.  Fall back to a
# plain sys.path insert so the script works whether or not the package is
# installed.
# ---------------------------------------------------------------------------
try:
    from cmipld.utils import crs as _crs
except ModuleNotFoundError:
    import importlib.util, os
    _candidates = [
        Path(__file__).parents[4] / "CMIP-LD" / "cmipld" / "utils" / "crs.py",
        Path(__file__).parents[3] / "CMIP-LD" / "cmipld" / "utils" / "crs.py",
    ]
    for _p in _candidates:
        if _p.exists():
            _spec = importlib.util.spec_from_file_location("crs", _p)
            _crs = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_crs)
            break
    else:
        sys.exit(
            "ERROR: could not import cmipld.utils.crs — install cmipld or "
            "place CMIP-LD next to Essential-Model-Documentation."
        )


_COMPONENT_NORM = {
    'sea ice':                     'sea-ice',
    'land surface and subsurface': 'land-surface',
    'land surface':                'land-surface',
    'land ice':                    'land-ice',
    'ocean biogeochemistry':       'ocean-biogeochemistry',
    'atmospheric chemistry':       'atmospheric-chemistry',
}


def _norm(s: str) -> str:
    sl = s.strip().lower()
    return _COMPONENT_NORM.get(sl, sl.replace(' ', '-'))


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def save_json(path: str, data: dict) -> None:
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')


def compute_crs(data: dict) -> tuple[str | None, list[str]]:
    """
    Validate and build a CRS from a model record.
    Returns (crs_string, errors).  crs_string is None on any error.
    """
    dynamic    = [_norm(c) for c in data.get('dynamic_components', [])]
    prescribed = [_norm(c) for c in data.get('prescribed_components', [])]
    embedded   = data.get('embedded_components', [])
    coupled    = data.get('coupled_components', [])

    errors = _crs.validate(dynamic, embedded, coupled, prescribed=prescribed)
    if errors:
        return None, errors

    try:
        return _crs.build(dynamic, embedded, coupled, prescribed=prescribed), []
    except Exception as e:
        return None, [str(e)]


def process_file(filepath: str, mode: str) -> tuple[str, str | None]:
    """
    Process one model JSON file.

    Returns (status, message) where status is one of:
      'written'   — CRS updated on disk
      'ok'        — CRS already correct, nothing written
      'skipped'   — CRS present and mode is 'fill' (skip existing)
      'missing'   — no CRS and mode is 'check'
      'drift'     — stored CRS differs from computed, mode is 'check'
      'error'     — validation/build failure
    """
    model_id = Path(filepath).stem
    try:
        data = load_json(filepath)
    except json.JSONDecodeError as e:
        return 'error', f"{model_id}: invalid JSON: {e}"

    stored = data.get('crs') or ''
    new_crs, errors = compute_crs(data)

    if errors:
        msg = f"{model_id}: validation error(s):\n" + \
              ''.join(f"    - {e}\n" for e in errors)
        return 'error', msg

    if mode == 'fill' and stored:
        return 'skipped', f"{model_id}: skipped (CRS present)"

    if stored == new_crs:
        return 'ok', f"{model_id}: ok ({new_crs})"

    # There is a difference.
    if mode == 'check':
        if not stored:
            return 'missing', f"{model_id}: missing CRS (would be: {new_crs})"
        return 'drift', (
            f"{model_id}: drift\n"
            f"    stored  : {stored}\n"
            f"    computed: {new_crs}"
        )

    # fill or rebuild — write the new value.
    data['crs'] = new_crs
    save_json(filepath, data)
    action = 'generated' if not stored else 'updated'
    return 'written', f"{model_id}: {action} -> {new_crs}"


def parse_args():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    grp = p.add_mutually_exclusive_group()
    grp.add_argument('--rebuild', action='store_true',
                     help='Recompute all CRS values, overwrite if changed')
    grp.add_argument('--check',   action='store_true',
                     help='Report drift/errors without writing (exit 1 if any)')
    p.add_argument('files', nargs='*',
                   help='Specific model filenames or paths (default: all)')
    return p.parse_args()


def main():
    args = parse_args()
    mode = 'check' if args.check else ('rebuild' if args.rebuild else 'fill')

    script_dir = Path(__file__).parent.parent.parent
    model_dir  = script_dir / 'model'
    if not model_dir.exists():
        sys.exit(f"ERROR: model directory not found at {model_dir}")

    # Resolve file list
    if args.files:
        paths = []
        for f in args.files:
            p = Path(f) if Path(f).is_absolute() else model_dir / f
            if p.exists():
                paths.append(str(p))
            else:
                print(f"WARNING: not found: {p}")
    else:
        paths = sorted(glob.glob(str(model_dir / '*.json')))

    if not paths:
        sys.exit("No model files to process.")

    mode_label = {'fill': 'fill (blanks only)', 'rebuild': 'rebuild (all)', 'check': 'check (read-only)'}
    print(f"Mode: {mode_label[mode]}  |  {len(paths)} file(s)\n")

    counts = {k: [] for k in ('written', 'ok', 'skipped', 'missing', 'drift', 'error')}

    for filepath in paths:
        status, msg = process_file(filepath, mode)
        counts[status].append(Path(filepath).stem)
        # Print non-ok lines; in check mode print everything
        if status != 'ok' or mode == 'check':
            prefix = {'written': '✓', 'ok': ' ', 'skipped': '-',
                      'missing': '!', 'drift': '!', 'error': '✗'}.get(status, '?')
            print(f"  {prefix} {msg}")

    # Summary
    print("\n" + "=" * 60)
    print(f"{'CHECK SUMMARY' if mode == 'check' else 'SUMMARY'}")
    print("=" * 60)
    if mode == 'fill':
        print(f"  Written : {len(counts['written'])}")
        print(f"  Skipped : {len(counts['skipped'])}  (CRS already present)")
    elif mode == 'rebuild':
        print(f"  Updated : {len(counts['written'])}")
        print(f"  Unchanged: {len(counts['ok'])}")
    else:  # check
        print(f"  OK      : {len(counts['ok'])}")
        print(f"  Missing : {len(counts['missing'])}")
        print(f"  Drift   : {len(counts['drift'])}")

    if counts['error']:
        print(f"  Errors  : {len(counts['error'])}")
        for m in counts['error']:
            print(f"    • {m}")

    bad = counts['error'] + counts['missing'] + counts['drift']
    if bad:
        sys.exit(1)


if __name__ == '__main__':
    main()
