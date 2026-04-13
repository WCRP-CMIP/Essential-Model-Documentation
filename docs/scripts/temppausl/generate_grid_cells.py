#!/usr/bin/env python3
"""Generate horizontal grid cell HTML pages from JSON-LD metadata."""

import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("Error: jinja2 not installed")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable

from helpers import ICONS, is_none_value, escape_html
from helpers.data_loader import init_loader, list_entries, fetch_entry


TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"
OUTPUT_DIR   = SCRIPT_DIR.parent / "EMD_Repository" / "Horizontal_Grid_Cell"

OLD_DIRS = [
    SCRIPT_DIR.parent / "horizontal_grid_cell",
    SCRIPT_DIR.parent / "Horizontal_Grid_Cell",
    SCRIPT_DIR.parent / "10_EMD_Repository" / "07_Horizontal_Grid_Cells",
    SCRIPT_DIR.parent / "EMD_Repository" / "07_Horizontal_Grid_Cells",
]


# ── helpers ───────────────────────────────────────────────────────────────────

def _val(obj, fallback=""):
    """Extract a scalar from a CV object, plain string, or None."""
    if obj is None or is_none_value(obj):
        return fallback
    if isinstance(obj, dict):
        return (obj.get("@value")
                or obj.get("ui_label", "").strip()
                or obj.get("validation_key", "")
                or obj.get("@id", "").split("/")[-1]
                or fallback)
    return str(obj) if obj else fallback


def _label(obj, fallback=""):
    """Human-readable label: prefer ui_label → validation_key → @id stem."""
    raw = _val(obj, fallback)
    return raw.replace("-", " ").replace("_", " ").title() if raw else fallback


def _cv(obj):
    """Return {id, name} for a CV reference, or None."""
    if not obj or is_none_value(obj):
        return None
    if isinstance(obj, str):
        return {"id": obj, "name": obj.replace("-", " ").replace("_", " ").title()}
    return {
        "id":   obj.get("@id", "").split("/")[-1],
        "name": _label(obj),
    }


def _ensure_list(val):
    if is_none_value(val):
        return []
    return val if isinstance(val, list) else [val]


def safe_filename(name):
    if not name:
        return "unknown"
    for ch in ('/', '\\', ':', '<', '>', '"', '|', '?', '*', ' '):
        name = name.replace(ch, '_')
    return name.strip('_') or "unknown"


# ── context builder ───────────────────────────────────────────────────────────

def prepare_context(data):
    """Build the Jinja2 template context for one horizontal_grid_cell entry."""
    entry_id = data.get("@id", "")
    vk       = _val(data.get("validation_key"), entry_id.split("/")[-1])
    name     = _val(data.get("ui_label")) or vk
    desc     = _val(data.get("description"), "No description provided.")

    # Resolution fields — may be absent
    x_res   = data.get("x_resolution")
    y_res   = data.get("y_resolution")
    units   = _label(data.get("units"), "")
    n_cells = data.get("n_cells")

    # Spectral truncation (only for spectral-gaussian grids)
    trunc_method = _cv(data.get("truncation_method"))
    trunc_number = data.get("truncation_number")

    # Geographic origin (may be absent / None)
    s_lat = data.get("southernmost_latitude")
    w_lon = data.get("westernmost_longitude")

    # CV references
    grid_type   = _cv(data.get("grid_type"))
    grid_map    = _cv(data.get("grid_mapping"))
    temp_refine = _cv(data.get("temporal_refinement"))
    regions     = [_cv(r) for r in _ensure_list(data.get("region")) if r]

    return {
        "id":           entry_id,
        "validation_key": vk,
        "name":         name,
        "description":  escape_html(desc),
        "page_type":    "Horizontal Grid Cell",
        # resolution
        "x_resolution":           x_res,
        "y_resolution":           y_res,
        "units":                  units,
        "n_cells":                n_cells,
        # spectral
        "truncation_method":      trunc_method,
        "truncation_number":      trunc_number,
        # origin
        "southernmost_latitude":  s_lat,
        "westernmost_longitude":  w_lon,
        # CV
        "grid_type":              grid_type,
        "grid_mapping":           grid_map,
        "temporal_refinement":    temp_refine,
        "regions":                regions,
        # meta
        "icons":          ICONS,
        "raw_json":       json.dumps(data, indent=2),
        "depth":          "../../",
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    }


# ── per-entry processor ───────────────────────────────────────────────────────

def process_entry(env, template, entry_id, pbar=None):
    def _log(msg):
        (pbar.write if pbar else print)(msg)

    try:
        data = fetch_entry("horizontal_grid_cell", entry_id)
        if not data:
            _log(f"  No data for {entry_id}")
            return False

        ctx      = prepare_context(data)
        filename = safe_filename(ctx["validation_key"]) + ".html"
        out_path = OUTPUT_DIR / filename
        if pbar:
            pbar.set_description(f"{entry_id[:25]}")
            pbar.write(f"  {entry_id} → {filename}")

        out_path.write_text(template.render(**ctx), encoding="utf-8")
        return True

    except Exception as e:
        _log(f"  Error {entry_id}: {e}")
        return False


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("Horizontal Grid Cell Page Generator")
    print("=" * 40)
    init_loader()

    # Remove legacy directories
    import shutil
    for old in OLD_DIRS:
        if old.exists() and old != OUTPUT_DIR:
            shutil.rmtree(old)
            print(f"  Removed old dir: {old.name}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  Output dir: {OUTPUT_DIR.name}")

    env      = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)
    template = env.get_template("grid_cells.html.j2")

    entries = list_entries("horizontal_grid_cell")
    print(f"\nHorizontal Grid Cell: {len(entries)}")
    if not entries:
        print("  No entries found.")
        return 0

    success = 0
    with tqdm(entries, desc="Grid cells", unit="file") as pbar:
        for entry_id in pbar:
            if process_entry(env, template, entry_id, pbar):
                success += 1

    print(f"\nDone: {success}/{len(entries)} grid cell pages generated in {OUTPUT_DIR.name}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
else:
    main()
