#!/usr/bin/env python3
"""Generate horizontal computational grid HTML pages from JSON-LD metadata."""

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
from helpers.data_loader import init_loader, fetch_data

TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"
OUTPUT_DIR = SCRIPT_DIR.parent / "horizontal_computational_grid"


def parse_subgrid(sg):
    """Parse subgrid reference."""
    if is_none_value(sg):
        return None
    if isinstance(sg, str):
        return {"id": sg, "name": sg.replace("-", " ").title(), "description": "", "cell_type": ""}
    if isinstance(sg, dict):
        # Get nested grid cells info
        grid_cells = sg.get("horizontal_grid_cells", {})
        grid_cells_id = ""
        if isinstance(grid_cells, dict):
            grid_cells_id = grid_cells.get("@id", "")
        elif isinstance(grid_cells, str):
            grid_cells_id = grid_cells
        
        return {
            "id": sg.get("@id", ""),
            "name": sg.get("ui_label") or sg.get("@id", "").replace("-", " ").title(),
            "description": sg.get("description", ""),
            "cell_variable_type": sg.get("cell_variable_type", ""),
            "grid_cells_id": grid_cells_id
        }
    return None


def parse_subgrids(subgrids):
    """Parse list of subgrids."""
    if is_none_value(subgrids):
        return []
    if isinstance(subgrids, str):
        p = parse_subgrid(subgrids)
        return [p] if p else []
    if isinstance(subgrids, dict):
        p = parse_subgrid(subgrids)
        return [p] if p else []
    if isinstance(subgrids, list):
        return [p for sg in subgrids if (p := parse_subgrid(sg))]
    return []


def prepare_template_context(data):
    """Prepare context for Jinja2 template."""
    grid_id = data.get("@id") or data.get("validation_key") or "unknown"
    
    name = data.get("ui_label") or data.get("name") or grid_id.replace("-", " ").title()
    description = data.get("description") or "No description available."
    
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]
    
    arrangement = data.get("arrangement", "")
    subgrids = parse_subgrids(data.get("horizontal_subgrids"))
    
    return {
        "id": grid_id,
        "name": name,
        "description": escape_html(description),
        "validation_key": data.get("validation_key", ""),
        "context_url": data.get("@context", ""),
        "types": types,
        "page_type": "Horizontal Computational Grid",
        "arrangement": arrangement,
        "subgrids": subgrids,
        "icons": ICONS,
        "raw_json": json.dumps(data, indent=2),
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    }


def setup_jinja_env():
    """Setup Jinja2 environment."""
    return Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)


def process_grid(env, template, data, pbar=None):
    """Process a single horizontal computational grid."""
    entry_id = data.get("@id") or data.get("validation_key") or "unknown"
    output_path = OUTPUT_DIR / f"{entry_id}.html"
    
    if pbar:
        pbar.set_description(f"Processing {entry_id[:30]}")
    
    try:
        context = prepare_template_context(data)
        html = template.render(**context)
        output_path.write_text(html, encoding="utf-8")
        return True
    except Exception as e:
        if pbar:
            pbar.write(f"Error {entry_id}: {e}")
        else:
            print(f"Error {entry_id}: {e}")
        return False


def clear_output_dir():
    """Remove all .html files from output directory."""
    if OUTPUT_DIR.exists():
        files = list(OUTPUT_DIR.glob("*.html"))
        for f in files:
            f.unlink()


def main():
    print("Horizontal Computational Grid Page Generator")
    print("=" * 40)
    
    # Initialize branch-aware data loading
    init_loader()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Clear old files
    clear_output_dir()
    
    env = setup_jinja_env()
    try:
        template = env.get_template("grid.html.j2")
    except Exception as e:
        print(f"Template error: {e}")
        return 1
    
    # Get all horizontal computational grids
    grids = fetch_data("horizontal_computational_grid", depth=2)
    grids = [g for g in grids if isinstance(g, dict)]
    
    print(f"Found {len(grids)} horizontal computational grids")
    
    if not grids:
        print("No horizontal computational grids found - check data source")
        return 0
    
    success = 0
    with tqdm(grids, desc="Generating H grids", unit="file") as pbar:
        for data in pbar:
            if process_grid(env, template, data, pbar):
                success += 1
    
    print(f"Done: {success}/{len(grids)} horizontal computational grids generated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
