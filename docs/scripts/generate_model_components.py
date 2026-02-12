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
    def tqdm(iterable, **kwargs):
        return iterable

from helpers import ICONS, HIGHLIGHT_KEYWORDS, is_none_value, escape_html
from helpers.utils import parse_references, highlight_keywords

BASE_URL = "https://emd.mipcvs.dev/model_component"
TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"
OUTPUT_DIR = SCRIPT_DIR.parent / "model_component"


def get_all_components():
    """Discover all model component files from the graph endpoint."""
    try:
        graph_data = cmipld.get(f"{BASE_URL}/graph.jsonld", depth=0)
        if graph_data and isinstance(graph_data, list):
            return [f"{item.get('@id')}.json" for item in graph_data if item.get('@id') and not item.get('@id').startswith('_')]
    except Exception:
        pass
    
    # Fallback to known files
    return [
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
    """Parse scientific domain / component type data."""
    if is_none_value(d) or d == "none":
        return None
    if isinstance(d, str):
        return {
            "id": d,
            "name": d.replace("-", " ").replace("_", " ").title(),
            "description": "",
            "aliases": []
        }
    if isinstance(d, dict):
        aliases = []
        if d.get("aliases"):
            a = d.get("aliases")
            aliases = a if isinstance(a, list) else [a]
        elif d.get("alias"):
            aliases = [d.get("alias")]
        
        return {
            "id": d.get("@id", ""),
            "name": d.get("ui_label") or d.get("description") or d.get("@id", "").replace("-", " ").title(),
            "description": d.get("description", ""),
            "aliases": aliases
        }
    return None


def parse_family(f):
    """Parse model family reference."""
    if is_none_value(f) or f == "none":
        return None
    if isinstance(f, str):
        return {
            "id": f,
            "name": f.replace("-", " ").title(),
            "description": ""
        }
    if isinstance(f, dict):
        return {
            "id": f.get("@id", ""),
            "name": f.get("ui_label") or f.get("name") or f.get("@id", "").replace("-", " ").title(),
            "description": f.get("description", "")
        }
    return None


def parse_code_base(cb):
    """Parse code base information."""
    if is_none_value(cb):
        return {"value": None, "is_private": False, "is_url": False}
    if isinstance(cb, str):
        return {
            "value": cb,
            "is_private": cb.lower() == "private",
            "is_url": cb.startswith("http")
        }
    return {"value": str(cb), "is_private": False, "is_url": False}


def prepare_template_context(data):
    """Prepare context for Jinja2 template."""
    component_id = data.get("@id", "unknown")
    name = data.get("name") or data.get("ui_label") or component_id.replace("-", " ").title()
    description = data.get("description") or "No description available."
    
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]
    
    # Parse related data
    family = parse_family(data.get("family"))
    component_domain = parse_domain(data.get("component"))
    code_base = parse_code_base(data.get("code_base"))
    references = parse_references(data.get("references"))
    
    # Note: horizontal/vertical grids are now in component_config, not in model_component
    # The model_component just defines the component itself
    
    # Highlight keywords
    extra_kw = [name]
    if family:
        extra_kw.append(family.get("name", ""))
    description_highlighted = highlight_keywords(description, extra_kw + HIGHLIGHT_KEYWORDS)
    
    return {
        "id": component_id,
        "name": name,
        "description": escape_html(description),
        "description_highlighted": description_highlighted,
        "family": family,
        "validation_key": data.get("validation_key", ""),
        "context_url": data.get("@context", ""),
        "types": types,
        "component_domain": component_domain,
        "code_base": code_base,
        "references": references,
        # Grid info no longer in model_component - set to None for template compatibility
        "horizontal_grid": None,
        "vertical_grid": None,
        "embedded_in": None,
        "coupled_with": [],
        "icons": ICONS,
        "raw_json": json.dumps(data, indent=2),
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    }


def setup_jinja_env():
    """Setup Jinja2 environment."""
    return Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)


def process_component(env, template, filename, pbar=None):
    """Process a single model component file."""
    url = f"{BASE_URL}/{filename}"
    output_path = OUTPUT_DIR / filename.replace(".json", ".html")
    
    if pbar:
        pbar.set_description(f"Processing {filename[:30]}")
    
    try:
        data = cmipld.get(url)
        if not data:
            if pbar:
                pbar.write(f"No data for {filename}")
            return False
        
        context = prepare_template_context(data)
        html = template.render(**context)
        output_path.write_text(html, encoding="utf-8")
        return True
    except Exception as e:
        if pbar:
            pbar.write(f"Error {filename}: {e}")
        else:
            print(f"Error {filename}: {e}")
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
    
    # Discover all component files
    model_components = get_all_components()
    print(f"Found {len(model_components)} model components")
    
    success = 0
    with tqdm(model_components, desc="Generating components", unit="file") as pbar:
        for filename in pbar:
            if process_component(env, template, filename, pbar):
                success += 1
    
    print(f"Done: {success}/{len(model_components)} components generated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
