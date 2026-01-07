#!/usr/bin/env python3
"""Generate computational grid HTML pages from JSON-LD metadata."""

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
OUTPUT_DIR_H = SCRIPT_DIR.parent / "10_EMD_Repository" / "05_Horizontal_Computational_Grids"
OUTPUT_DIR_V = SCRIPT_DIR.parent / "10_EMD_Repository" / "06_Vertical_Computational_Grids"

OLD_DIRS = [
    SCRIPT_DIR.parent / "horizontal_computational_grid",
    SCRIPT_DIR.parent / "vertical_computational_grid",
    SCRIPT_DIR.parent / "Horizontal Computational Grid",
    SCRIPT_DIR.parent / "Vertical Computational Grid",
    SCRIPT_DIR.parent / "Horizontal_Computational_Grid",
    SCRIPT_DIR.parent / "Vertical_Computational_Grid",
]


def safe_filename(name):
    if not name:
        return "unknown"
    name = str(name)
    for ch in ('/', '\\', ':', '<', '>', '"', '|', '?', '*'):
        name = name.replace(ch, '-') if ch in ('/', '\\', ':') else name.replace(ch, '')
    return name.strip()


def get_display_name(data):
    """Get display name: ui_label -> validation_key -> @id (last segment).
    Works on any dict, including nested CV objects."""
    if not data or not isinstance(data, dict):
        return str(data) if data else "unknown"
    name = (
        data.get("ui_label") or
        data.get("validation_key") or
        (data.get("@id", "").split("/")[-1].split(":")[-1].replace("-", " ").replace("_", " ").title())
    )
    return (name or "unknown").strip()


def _ensure_list(val):
    """Coerce scalar/None to a list."""
    if is_none_value(val):
        return []
    return val if isinstance(val, list) else [val]


def _label(obj, fallback=""):
    """Get the best human-readable label from a CV object."""
    if not obj or is_none_value(obj):
        return fallback
    if isinstance(obj, str):
        return obj.replace("-", " ").replace("_", " ").title()
    return (obj.get("ui_label") or obj.get("validation_key") or
            obj.get("@id", fallback).split("/")[-1].replace("-", " ").replace("_", " ").title()
            or fallback)


def _cv_obj(obj, fallback=None):
    """Parse a CV item to {id, name, description}."""
    if not obj or is_none_value(obj):
        return fallback
    if isinstance(obj, str):
        return {"id": obj, "name": obj.replace("-", " ").replace("_", " ").title(), "description": ""}
    return {
        "id": obj.get("@id", ""),
        "name": _label(obj),
        "description": obj.get("description", ""),
    }

def parse_grid_cells(gc):
    """Parse a horizontal_grid_cells object into a rich dict for the template."""
    if not gc or is_none_value(gc):
        return None
    if isinstance(gc, str):
        return {"id": gc, "name": gc, "description": "", "n_cells": None,
                "x_resolution": None, "y_resolution": None, "units": "",
                "regions": [], "grid_type": None, "grid_mapping": None,
                "temporal_refinement": None, "southernmost_latitude": None,
                "westernmost_longitude": None}
    regions = [_cv_obj(r) for r in _ensure_list(gc.get("region")) if r and not is_none_value(r)]
    return {
        "id": gc.get("@id", ""),
        "name": gc.get("ui_label", "").strip() or gc.get("validation_key", "") or gc.get("@id", ""),
        "description": gc.get("description", ""),
        "n_cells": gc.get("n_cells"),
        "x_resolution": gc.get("x_resolution"),
        "y_resolution": gc.get("y_resolution"),
        "units": _label(gc.get("units")),
        "southernmost_latitude": gc.get("southernmost_latitude"),
        "westernmost_longitude": gc.get("westernmost_longitude"),
        "regions": regions,
        "grid_type": _cv_obj(gc.get("grid_type")),
        "grid_mapping": _cv_obj(gc.get("grid_mapping")),
        "temporal_refinement": _cv_obj(gc.get("temporal_refinement")),
    }


def parse_subgrid(sg):
    """Parse a horizontal_subgrid object into a rich dict for the template."""
    if not sg or is_none_value(sg):
        return None
    if isinstance(sg, str):
        return {"id": sg, "name": sg, "description": "", "variable_types": [], "grid_cells": None}
    variable_types = [_cv_obj(v) for v in _ensure_list(sg.get("cell_variable_type"))
                      if v and not is_none_value(v)]
    return {
        "id": sg.get("@id", ""),
        "name": sg.get("ui_label", "").strip() or sg.get("validation_key", "") or sg.get("@id", ""),
        "description": sg.get("description", ""),
        "variable_types": variable_types,
        "grid_cells": parse_grid_cells(sg.get("horizontal_grid_cells")),
    }


def prepare_horizontal_context(data):
    """Prepare rich context for horizontal computational grid template."""
    grid_id = data.get("@id") or data.get("validation_key") or "unknown"
    name = get_display_name(data)
    description = data.get("description") or "No description available."
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]

    subgrids = [s for sg in _ensure_list(data.get("horizontal_subgrids"))
                if (s := parse_subgrid(sg))]

    return {
        "id": grid_id,
        "name": name,
        "description": escape_html(description),
        "validation_key": data.get("validation_key", ""),
        "types": types,
        "page_type": "Horizontal Computational Grid",
        "arrangement": _cv_obj(data.get("arrangement")),
        "subgrids": subgrids,
        "icons": ICONS,
        "context_url": data.get("@context", ""),
        "raw_json": json.dumps(data, indent=2),
        "depth": "../../",
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    }


def prepare_vertical_context(data):
    """Prepare rich context for vertical computational grid template."""
    grid_id = data.get("@id") or data.get("validation_key") or "unknown"
    name = get_display_name(data)
    description = data.get("description") or "No description available."
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]

    return {
        "id": grid_id,
        "name": name,
        "description": escape_html(description),
        "validation_key": data.get("validation_key", ""),
        "types": types,
        "page_type": "Vertical Computational Grid",
        "vertical_coordinate": _cv_obj(data.get("vertical_coordinate")),
        "n_z": data.get("n_z"),
        "top_layer_thickness": data.get("top_layer_thickness"),
        "bottom_layer_thickness": data.get("bottom_layer_thickness"),
        "total_thickness": data.get("total_thickness"),
        "icons": ICONS,
        "context_url": data.get("@context", ""),
        "raw_json": json.dumps(data, indent=2),
        "depth": "../../",
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    }


def setup_jinja_env():
    return Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)


def process_grid(env, template, endpoint, entry_id, output_dir, prepare_func, pbar=None):
    if pbar:
        pbar.set_description(f"Processing {entry_id[:25]}")
    try:
        data = fetch_entry(endpoint, entry_id)
        if not data:
            if pbar:
                pbar.write(f"  No data for {entry_id}")
            return False
        filename = safe_filename(get_display_name(data)) + ".html"
        output_path = output_dir / filename
        if pbar:
            pbar.write(f"  {entry_id} -> {filename}")
        html = template.render(**prepare_func(data))
        output_path.write_text(html, encoding="utf-8")
        return True
    except Exception as e:
        if pbar:
            pbar.write(f"  Error {entry_id}: {e}")
        else:
            print(f"  Error {entry_id}: {e}")
        return False


def clear_output_dir(output_dir):
    if output_dir.exists():
        for f in output_dir.glob("*.html"):
            f.unlink()


def remove_old_dirs():
    import shutil
    for old_dir in OLD_DIRS:
        if old_dir.exists() and old_dir not in [OUTPUT_DIR_H, OUTPUT_DIR_V]:
            shutil.rmtree(old_dir)
            print(f"  Removed old directory: {old_dir.name}")


def main():
    print("Computational Grid Page Generator")
    print("=" * 40)
    init_loader()
    remove_old_dirs()

    env = setup_jinja_env()
    template = env.get_template("grid.html.j2")

    total_success = 0
    total_count = 0

    # ── Horizontal computational grids ────────────────────────────────────────
    OUTPUT_DIR_H.mkdir(parents=True, exist_ok=True)
    # clear_output_dir(OUTPUT_DIR_H)  # disabled: nav already registered these files
    print(f"  Output dir: {OUTPUT_DIR_H.name}")

    h_entries = list_entries("horizontal_computational_grid")
    print(f"\nHorizontal Computational Grids: {len(h_entries)}")
    if h_entries:
        with tqdm(h_entries, desc="Horizontal grids", unit="file") as pbar:
            for entry_id in pbar:
                if process_grid(env, template, "horizontal_computational_grid",
                                entry_id, OUTPUT_DIR_H, prepare_horizontal_context, pbar):
                    total_success += 1
                total_count += 1

    # ── Vertical computational grids ──────────────────────────────────────────
    OUTPUT_DIR_V.mkdir(parents=True, exist_ok=True)
    # clear_output_dir(OUTPUT_DIR_V)  # disabled: nav already registered these files
    print(f"  Output dir: {OUTPUT_DIR_V.name}")

    v_entries = list_entries("vertical_computational_grid")
    print(f"\nVertical Computational Grids: {len(v_entries)}")
    if v_entries:
        with tqdm(v_entries, desc="Vertical grids", unit="file") as pbar:
            for entry_id in pbar:
                if process_grid(env, template, "vertical_computational_grid",
                                entry_id, OUTPUT_DIR_V, prepare_vertical_context, pbar):
                    total_success += 1
                total_count += 1

    print(f"\nDone: {total_success}/{total_count} grids generated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
else:
    main()
