#!/usr/bin/env python3
"""Generate model component HTML pages from JSON-LD metadata."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    import cmipld
except ImportError:
    print("Error: cmipld not installed")
    sys.exit(1)

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("Error: jinja2 not installed")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm not installed
    def tqdm(iterable, **kwargs):
        return iterable

from helpers import ICONS, HIGHLIGHT_KEYWORDS, is_none_value, escape_html
from helpers.utils import parse_references, highlight_keywords

BASE_URL = "https://emd.mipcvs.dev/model_component"
TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"
OUTPUT_DIR = SCRIPT_DIR.parent / "model_component"

# Multiple model components to generate
MODEL_COMPONENTS = [
    "arpege-climat-version-6-3.json",
    "bisicles-ukesm-ismip6-1.0.json",
    "clm4.json",
    "gelato.json",
    "hadam3.json",
    "nemo-v3-6.json",
    "piscesv2-gas.json",
    "reprobus-c-v2-0.json",
    "surfex-v8-modeling-platform.json",
    "tactic.json",
]


def parse_domain(d):
    if is_none_value(d): return None
    if d == "none": return None
    if isinstance(d, str): return {"id": d, "name": d.replace("-", " ").title(), "description": "", "aliases": []}
    if isinstance(d, dict): return {
        "id": d.get("@id", ""),
        "name": d.get("ui_label") or d.get("description") or d.get("@id", "").replace("-", " ").title(),
        "description": d.get("description", ""),
        "aliases": [d.get("alias")] if d.get("alias") else []
    }
    return None


def parse_family(f):
    if is_none_value(f): return None
    if isinstance(f, str): return {"id": f, "name": f.replace("-", " ").title(), "description": ""}
    if isinstance(f, dict): return {
        "id": f.get("@id", ""),
        "name": f.get("ui_label") or f.get("@id", "").replace("-", " ").title(),
        "description": f.get("description", "")
    }
    return None


def parse_coupled_with(coupled):
    if is_none_value(coupled): return []
    if isinstance(coupled, list): return [p for c in coupled if (p := parse_domain(c))]
    p = parse_domain(coupled)
    return [p] if p else []


def parse_horizontal_grid(g):
    if is_none_value(g): return None
    if isinstance(g, str): return {"id": g, "description": "", "arrangement": None, "subgrids": []}
    if not isinstance(g, dict): return None
    
    arr = g.get("arrangement")
    arrangement = arr.replace("-", " ").title() if isinstance(arr, str) else (arr.get("ui_label") or arr.get("description", "") if isinstance(arr, dict) else None)
    
    subgrids = []
    for sg in (g.get("horizontal_subgrids") or []):
        if not isinstance(sg, dict): continue
        cvt = sg.get("cell_variable_type")
        cell_type = {"id": cvt, "name": cvt.title()} if isinstance(cvt, str) else ({"id": cvt.get("@id", ""), "name": cvt.get("ui_label") or cvt.get("@id", "").title()} if isinstance(cvt, dict) else None)
        
        gcr = sg.get("horizontal_grid_cells")
        grid_cells = {"id": gcr} if isinstance(gcr, str) else ({
            "id": gcr.get("@id", ""), "grid_type": gcr.get("grid_type", ""),
            "n_cells": gcr.get("n_cells"), "x_resolution": gcr.get("x_resolution"),
            "y_resolution": gcr.get("y_resolution"),
            "region": gcr.get("region", {}).get("ui_label") if isinstance(gcr.get("region"), dict) else None,
            "truncation_number": gcr.get("truncation_number"), "truncation_method": gcr.get("truncation_method"),
        } if isinstance(gcr, dict) else None)
        
        subgrids.append({"id": sg.get("@id", ""), "description": sg.get("description", ""), "cell_variable_type": cell_type, "grid_cells": grid_cells})
    
    return {"id": g.get("@id", ""), "description": g.get("description", ""), "arrangement": arrangement, "subgrids": subgrids}


def parse_vertical_grid(g):
    if is_none_value(g): return None
    if isinstance(g, str): return {"id": g, "description": "", "n_z": None, "coordinate": None}
    if not isinstance(g, dict): return None
    
    coord = g.get("vertical_coordinate")
    coordinate = coord.replace("-", " ").title() if isinstance(coord, str) else (coord.get("ui_label") or coord.get("description", "") if isinstance(coord, dict) else None)
    
    return {
        "id": g.get("@id", ""), "description": g.get("description", ""), "n_z": g.get("n_z"),
        "coordinate": coordinate, "top_thickness": g.get("top_layer_thickness"),
        "bottom_thickness": g.get("bottom_layer_thickness"), "total_thickness": g.get("total_thickness")
    }


def parse_code_base(cb):
    if is_none_value(cb): return {"value": None, "is_private": False, "is_url": False}
    if isinstance(cb, str):
        return {"value": cb, "is_private": cb.lower() == "private", "is_url": cb.startswith("http")}
    return {"value": str(cb), "is_private": False, "is_url": False}


def prepare_template_context(data):
    component_id = data.get("@id", "unknown")
    name = data.get("name") or component_id.upper()
    description = data.get("description") or "No description available."
    types = data.get("@type", [])
    if isinstance(types, str): types = [types]
    
    family = parse_family(data.get("family"))
    component_domain = parse_domain(data.get("component"))
    embedded_in = parse_domain(data.get("embedded_in"))
    coupled_with = parse_coupled_with(data.get("coupled_with"))
    horizontal_grid = parse_horizontal_grid(data.get("horizontal_computational_grid"))
    vertical_grid = parse_vertical_grid(data.get("vertical_computational_grid"))
    code_base = parse_code_base(data.get("code_base"))
    references = parse_references(data.get("references"))
    
    extra_kw = [name]
    if family: extra_kw.append(family.get("name", ""))
    description_highlighted = highlight_keywords(description, extra_kw + HIGHLIGHT_KEYWORDS)
    
    return {
        "id": component_id, "name": name, "description": escape_html(description),
        "description_highlighted": description_highlighted, "family": family,
        "validation_key": data.get("validation_key", ""), "context_url": data.get("@context", ""),
        "types": types, "component_domain": component_domain, "embedded_in": embedded_in,
        "coupled_with": coupled_with, "horizontal_grid": horizontal_grid, "vertical_grid": vertical_grid,
        "code_base": code_base, "references": references, "icons": ICONS,
        "raw_json": json.dumps(data), "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    }


def setup_jinja_env():
    return Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)


def process_component(env, template, filename, pbar=None):
    url = f"{BASE_URL}/{filename}"
    output_path = OUTPUT_DIR / filename.replace(".json", ".html")
    if pbar:
        pbar.set_description(f"Processing {filename[:30]}")
    try:
        data = cmipld.get(url)
        if not data:
            return False
        context = prepare_template_context(data)
        html = template.render(**context)
        output_path.write_text(html, encoding="utf-8")
        return True
    except Exception as e:
        if pbar:
            pbar.write(f"Error {filename}: {e}")
        return False


def clear_output_dir():
    """Remove all .html files from output directory."""
    if OUTPUT_DIR.exists():
        files = list(OUTPUT_DIR.glob("*.html"))
        for f in files:
            f.unlink()


def main():
    print("Model Component Page Generator")
    print("=" * 40)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Clear old files
    clear_output_dir()
    
    env = setup_jinja_env()
    try:
        template = env.get_template("model_component.html.j2")
    except Exception as e:
        print(f"Template error: {e}")
        return 1
    
    success = 0
    with tqdm(MODEL_COMPONENTS, desc="Generating components", unit="file") as pbar:
        for filename in pbar:
            if process_component(env, template, filename, pbar):
                success += 1
    
    print(f"Done: {success}/{len(MODEL_COMPONENTS)} components generated")
    # cmipld.client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
