#!/usr/bin/env python3
"""
Build script to generate model component HTML pages from JSON-LD metadata.

This script fetches JSON-LD data from the EMD registry and generates
styled HTML pages for each model component using Jinja2 templates.

Usage:
    python generate_model_components.py

Requirements:
    pip install cmipld jinja2
"""

import json
import sys
from pathlib import Path
from typing import Any, Optional

# Resolve script directory (works regardless of working directory)
SCRIPT_DIR = Path(__file__).resolve().parent

# Add scripts dir to path for imports
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    import cmipld
except ImportError:
    print("Error: cmipld package not installed. Run: pip install cmipld")
    sys.exit(1)

try:
    from jinja2 import Environment
except ImportError:
    print("Error: jinja2 package not installed. Run: pip install jinja2")
    sys.exit(1)

from helpers import (
    ICONS,
    HIGHLIGHT_KEYWORDS,
    is_none_value,
    escape_html,
    create_jinja_env,
    create_section_macro,
    create_domain_card_macro,
)
from helpers.utils import parse_references, highlight_keywords


# Configuration
BASE_URL = "https://emd.mipcvs.dev/model_component"
TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"
OUTPUT_DIR = SCRIPT_DIR.parent / "model_component"

# List of model component JSON files to process
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

# Dynamic keywords collected from processed components
collected_keywords: set = set()


def safe_get_label(obj: Any, default: str = "") -> str:
    """Safely extract ui_label or @id from an object that may be dict or string.
    
    This is critical for handling JSON-LD nested objects like arrangement and
    vertical_coordinate which come as full dict objects but we only want the label.
    """
    if obj is None:
        return default
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        # Try ui_label first, then @id, then default
        return obj.get("ui_label", "") or obj.get("@id", "") or default
    return default


def parse_domain(domain_data: Any) -> Optional[dict]:
    """Parse a scientific domain into a standardized dict."""
    if is_none_value(domain_data):
        return None
    
    # Handle string "none" case
    if isinstance(domain_data, str):
        if domain_data.lower() == "none":
            return None
        return {
            "id": domain_data,
            "name": domain_data,
            "description": "",
            "validation_key": "",
            "aliases": [],
        }
    
    if isinstance(domain_data, dict):
        # Handle aliases - can be string or list
        aliases = domain_data.get("alias", [])
        if isinstance(aliases, str):
            aliases = [aliases]
        
        return {
            "id": domain_data.get("@id", ""),
            "name": domain_data.get("ui_label") or domain_data.get("description") or domain_data.get("@id", "Unknown"),
            "description": domain_data.get("description", ""),
            "validation_key": domain_data.get("validation_key", ""),
            "aliases": aliases,
        }
    
    return None


def parse_domains(domains_data: Any) -> list:
    """Parse multiple domains into a list."""
    if is_none_value(domains_data):
        return []
    
    if isinstance(domains_data, dict):
        parsed = parse_domain(domains_data)
        return [parsed] if parsed else []
    
    if isinstance(domains_data, list):
        result = []
        for item in domains_data:
            parsed = parse_domain(item)
            if parsed:
                result.append(parsed)
        return result
    
    return []


def parse_family(family_data: Any) -> Optional[dict]:
    """Parse family data into a standardized dict."""
    if is_none_value(family_data):
        return None
    
    if isinstance(family_data, str):
        return {
            "id": family_data,
            "name": family_data,
            "description": "",
        }
    
    if isinstance(family_data, dict):
        return {
            "id": family_data.get("@id", ""),
            "name": family_data.get("ui_label") or family_data.get("@id", "Unknown"),
            "description": family_data.get("description", ""),
            "validation_key": family_data.get("validation_key", ""),
            "primary_institution": family_data.get("primary_institution", ""),
        }
    
    return None


def parse_cell_variable_type(cvt: Any) -> Optional[dict]:
    """Parse cell_variable_type which can be string, dict, or list."""
    if cvt is None:
        return None
    
    # Handle list of variable types (e.g., ["mass", "x-velocity", "y-velocity"])
    if isinstance(cvt, list):
        names = []
        for item in cvt:
            if isinstance(item, str):
                # Convert kebab-case to Title Case
                names.append(item.replace("-", " ").title())
            elif isinstance(item, dict):
                names.append(item.get("ui_label", "") or item.get("@id", ""))
        return {
            "id": cvt[0] if isinstance(cvt[0], str) else cvt[0].get("@id", ""),
            "name": ", ".join(names),
            "description": "",
        }
    
    # Handle dict
    if isinstance(cvt, dict):
        return {
            "id": cvt.get("@id", ""),
            "name": cvt.get("ui_label", "") or cvt.get("@id", ""),
            "description": cvt.get("description", ""),
        }
    
    # Handle string
    if isinstance(cvt, str):
        return {
            "id": cvt,
            "name": cvt.replace("-", " ").title(),
            "description": "",
        }
    
    return None


def parse_subgrid(subgrid_data: Any) -> Optional[dict]:
    """Parse a single subgrid entry."""
    if is_none_value(subgrid_data):
        return None
    
    if isinstance(subgrid_data, str):
        return {
            "id": subgrid_data,
            "description": "",
            "cell_variable_type": None,
            "grid_cells": None,
        }
    
    if isinstance(subgrid_data, dict):
        # Parse cell_variable_type (can be string, dict, or list)
        cell_variable_type = parse_cell_variable_type(subgrid_data.get("cell_variable_type"))
        
        # Parse grid_cells reference
        hgc = subgrid_data.get("horizontal_grid_cells")
        grid_cells = None
        if isinstance(hgc, dict):
            grid_cells = {
                "id": hgc.get("@id", ""),
                "grid_type": hgc.get("grid_type", ""),
                "n_cells": hgc.get("n_cells"),
                "region": hgc.get("region", ""),
                "x_resolution": hgc.get("x_resolution"),
                "y_resolution": hgc.get("y_resolution"),
                "truncation_number": hgc.get("truncation_number"),
                "truncation_method": hgc.get("truncation_method"),
            }
        elif isinstance(hgc, str):
            grid_cells = {
                "id": hgc,
                "grid_type": "",
                "n_cells": None,
                "region": "",
                "x_resolution": None,
                "y_resolution": None,
            }
        
        return {
            "id": subgrid_data.get("@id", ""),
            "description": subgrid_data.get("description", ""),
            "cell_variable_type": cell_variable_type,
            "grid_cells": grid_cells,
        }
    
    return None


def parse_grid(grid_data: Any, grid_type: str) -> Optional[dict]:
    """Parse horizontal or vertical grid data."""
    if is_none_value(grid_data):
        return None
    
    # Handle string "none" case
    if isinstance(grid_data, str):
        if grid_data.lower() == "none":
            return None
        return {
            "id": grid_data,
            "description": "",
            "validation_key": grid_data,
        }
    
    if isinstance(grid_data, dict):
        result = {
            "id": grid_data.get("@id", ""),
            "description": grid_data.get("description", ""),
            "validation_key": grid_data.get("validation_key", ""),
        }
        
        if grid_type == "horizontal":
            # CRITICAL: Extract ui_label from arrangement dict using safe_get_label
            result["arrangement"] = safe_get_label(grid_data.get("arrangement", ""))
            
            # Handle subgrids - can be single dict OR list
            subgrids_raw = grid_data.get("horizontal_subgrids", [])
            subgrids = []
            
            if isinstance(subgrids_raw, dict):
                # Single subgrid as dict
                parsed = parse_subgrid(subgrids_raw)
                if parsed:
                    subgrids.append(parsed)
            elif isinstance(subgrids_raw, list):
                # List of subgrids
                for sg in subgrids_raw:
                    parsed = parse_subgrid(sg)
                    if parsed:
                        subgrids.append(parsed)
            
            result["subgrids"] = subgrids
            
        elif grid_type == "vertical":
            result["n_z"] = grid_data.get("n_z", "")
            # CRITICAL: Extract ui_label from vertical_coordinate dict using safe_get_label
            result["coordinate"] = safe_get_label(grid_data.get("vertical_coordinate", ""))
            result["top_thickness"] = grid_data.get("top_layer_thickness", "")
            result["bottom_thickness"] = grid_data.get("bottom_layer_thickness", "")
            result["total_thickness"] = grid_data.get("total_thickness", "")
        
        return result
    
    return None


def parse_code_base(code_base: Any) -> dict:
    """Parse code_base into a structured dict."""
    if is_none_value(code_base):
        return {"value": None, "is_private": False, "is_url": False}
    
    if not isinstance(code_base, str):
        return {"value": str(code_base), "is_private": False, "is_url": False}
    
    is_private = code_base.lower() == "private"
    is_url = code_base.startswith("http://") or code_base.startswith("https://")
    
    return {
        "value": code_base,
        "is_private": is_private,
        "is_url": is_url,
    }


def collect_keywords_from_data(data: dict) -> list:
    """Extract potential keywords from component data."""
    keywords = []
    
    # Component name
    name = data.get("name")
    if name:
        keywords.append(name)
    
    # Family
    family = data.get("family")
    if isinstance(family, dict):
        family_name = family.get("ui_label") or family.get("@id")
        if family_name and not is_none_value(family_name):
            keywords.append(family_name)
    elif isinstance(family, str) and not is_none_value(family):
        keywords.append(family)
    
    # Component domain label
    component = data.get("component")
    if isinstance(component, dict):
        ui_label = component.get("ui_label")
        if ui_label:
            keywords.append(ui_label)
    
    # Coupled domain labels
    coupled_with = data.get("coupled_with")
    if isinstance(coupled_with, list):
        for item in coupled_with:
            if isinstance(item, dict):
                label = item.get("ui_label")
                if label:
                    keywords.append(label)
    elif isinstance(coupled_with, dict):
        label = coupled_with.get("ui_label")
        if label:
            keywords.append(label)
    
    return keywords


def get_all_keywords() -> list:
    """Get combined list of default and collected keywords."""
    return HIGHLIGHT_KEYWORDS + list(collected_keywords)


def prepare_template_context(data: dict) -> dict:
    """Prepare the template context from raw JSON-LD data."""
    
    # Collect keywords from this component
    new_keywords = collect_keywords_from_data(data)
    collected_keywords.update(new_keywords)
    
    # Basic info
    component_id = data.get("@id", "unknown")
    name = data.get("name") or component_id.upper()
    description = data.get("description") or "No description available."
    
    # Family (can be string or object)
    family = parse_family(data.get("family"))
    
    # Extra keywords for this specific component
    extra_keywords = [name]
    if family:
        extra_keywords.append(family.get("name", ""))
    
    # Use combined keywords for highlighting
    all_keywords = get_all_keywords()
    description_highlighted = highlight_keywords(description, extra_keywords + all_keywords)
    
    # Types
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]
    
    # Component domain (scientific domain)
    component_domain = parse_domain(data.get("component"))
    
    # Embedded in
    embedded_in = parse_domain(data.get("embedded_in"))
    
    # Coupled with
    coupled_with = parse_domains(data.get("coupled_with"))
    
    # Grids
    horizontal_grid = parse_grid(data.get("horizontal_computational_grid"), "horizontal")
    vertical_grid = parse_grid(data.get("vertical_computational_grid"), "vertical")
    
    # Code base
    code_base = parse_code_base(data.get("code_base"))
    
    # References
    references = parse_references(data.get("references"))
    
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
        "embedded_in": embedded_in,
        "coupled_with": coupled_with,
        "horizontal_grid": horizontal_grid,
        "vertical_grid": vertical_grid,
        "code_base": code_base,
        "references": references,
        "icons": ICONS,
        "raw_json": json.dumps(data),  # Raw JSON for copy protection
    }


def setup_jinja_env() -> Environment:
    """Create and configure Jinja2 environment with component-specific macros."""
    env = create_jinja_env(TEMPLATE_DIR)
    
    # Add component-specific macros
    env.globals["section"] = create_section_macro("component")
    env.globals["domain_card"] = create_domain_card_macro("component")
    
    return env


def prefetch_all_keywords() -> None:
    """Pre-fetch all components to collect keywords before generating pages."""
    print("  Collecting keywords from all components...")
    
    for filename in MODEL_COMPONENTS:
        url = f"{BASE_URL}/{filename}"
        try:
            data = cmipld.get(url)
            if data:
                new_keywords = collect_keywords_from_data(data)
                collected_keywords.update(new_keywords)
        except Exception:
            pass  # Silently skip errors during prefetch
    
    print(f"  Collected {len(collected_keywords)} additional keywords\n")


def process_component(env: Environment, template, filename: str) -> bool:
    """Fetch and process a single model component."""
    url = f"{BASE_URL}/{filename}"
    output_name = filename.replace(".json", ".html")
    output_path = OUTPUT_DIR / output_name
    
    print(f"  Processing: {filename}")
    
    try:
        data = cmipld.get(url)
        
        if not data:
            print(f"    ⚠ Warning: No data returned for {filename}")
            return False
        
        context = prepare_template_context(data)
        html = template.render(**context)
        
        output_path.write_text(html, encoding="utf-8")
        print(f"    ✓ Generated: {output_path.name}")
        return True
        
    except Exception as e:
        print(f"    ✗ Error processing {filename}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    print("=" * 60)
    print("Model Component Page Generator")
    print("=" * 60)
    
    # Create output directory
    print(f"\nCreating output directory: {OUTPUT_DIR}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if not TEMPLATE_DIR.exists():
        print(f"Error: Template directory not found: {TEMPLATE_DIR}")
        return 1
    
    print(f"Template directory: {TEMPLATE_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Processing {len(MODEL_COMPONENTS)} model components...\n")
    
    # Pre-fetch to collect all keywords first
    prefetch_all_keywords()
    
    env = setup_jinja_env()
    
    try:
        template = env.get_template("model_component.html.j2")
    except Exception as e:
        print(f"Error loading template: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    success_count = 0
    fail_count = 0
    
    for filename in MODEL_COMPONENTS:
        if process_component(env, template, filename):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"Complete: {success_count} succeeded, {fail_count} failed")
    print("=" * 60)
    
    return 0 if fail_count == 0 else 1


# if __name__ == "__main__":
#     sys.exit(main())

main()