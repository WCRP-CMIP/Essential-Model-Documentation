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
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Resolve script directory (works regardless of working directory)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Add script directory to path for helpers import
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    import cmipld
except ImportError:
    print("Error: cmipld package not found. Install with: pip install cmipld")
    sys.exit(1)

try:
    from jinja2 import Environment
except ImportError:
    print("Error: jinja2 package not found. Install with: pip install jinja2")
    sys.exit(1)

from helpers import create_jinja_env, create_section_macro, create_domain_card_macro

# Configuration
BASE_URL = "https://emd.mipcvs.dev/model_component"
TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"
OUTPUT_DIR = PROJECT_ROOT / "model_component"

# Model components to generate
MODEL_COMPONENTS = [
    "arpege-climat-version-6-3.json",
]

# Icons (SVG paths)
ICONS = {
    "description": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>',
    "domain": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>',
    "grid": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>',
    "coupling": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>',
    "tech": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg>',
    "reference": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>',
    "chevron": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" /></svg>',
}

# Keywords to highlight (collected from data)
collected_keywords = set()

# Base keywords that are always highlighted
BASE_KEYWORDS = {
    "atmosphere", "ocean", "land", "ice", "aerosol", "chemistry",
    "carbon", "biogeochemistry", "climate", "earth system",
    "coupled", "model", "component", "grid", "spectral", "gaussian",
    "hybrid", "coordinate", "arakawa", "latitude", "longitude"
}


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def parse_domain(domain_data: Any) -> Optional[dict]:
    """Parse a scientific domain from various input formats."""
    if not domain_data:
        return None
    
    if domain_data == "none":
        return None
        
    if isinstance(domain_data, str):
        return {
            "id": domain_data,
            "name": domain_data.replace("-", " ").title(),
            "description": "",
            "aliases": []
        }
    
    if isinstance(domain_data, dict):
        return {
            "id": domain_data.get("@id", ""),
            "name": domain_data.get("ui_label") or domain_data.get("description") or domain_data.get("@id", "").replace("-", " ").title(),
            "description": domain_data.get("description", ""),
            "aliases": [domain_data.get("alias")] if domain_data.get("alias") else []
        }
    
    return None


def parse_family(family_data: Any) -> Optional[dict]:
    """Parse family information."""
    if not family_data:
        return None
    
    if isinstance(family_data, str):
        return {
            "id": family_data,
            "name": family_data.replace("-", " ").title(),
            "description": ""
        }
    
    if isinstance(family_data, dict):
        return {
            "id": family_data.get("@id", ""),
            "name": family_data.get("ui_label") or family_data.get("@id", "").replace("-", " ").title(),
            "description": family_data.get("description", "")
        }
    
    return None


def parse_coupled_with(coupled_data: Any) -> list:
    """Parse coupled_with field which can be a list or single item."""
    if not coupled_data:
        return []
    
    if isinstance(coupled_data, list):
        return [parse_domain(item) for item in coupled_data if parse_domain(item)]
    
    domain = parse_domain(coupled_data)
    return [domain] if domain else []


def parse_horizontal_grid(grid_data: Any) -> Optional[dict]:
    """Parse horizontal computational grid data."""
    if not grid_data:
        return None
    
    if isinstance(grid_data, str):
        return {"id": grid_data, "description": "", "arrangement": None, "subgrids": []}
    
    if not isinstance(grid_data, dict):
        return None
    
    # Parse arrangement
    arrangement = None
    arr_data = grid_data.get("arrangement")
    if arr_data:
        if isinstance(arr_data, str):
            arrangement = arr_data.replace("-", " ").title()
        elif isinstance(arr_data, dict):
            arrangement = arr_data.get("ui_label") or arr_data.get("description", "")
    
    # Parse subgrids
    subgrids = []
    subgrid_data = grid_data.get("horizontal_subgrids", [])
    if isinstance(subgrid_data, list):
        for sg in subgrid_data:
            if isinstance(sg, dict):
                # Parse cell variable type
                cell_var_type = sg.get("cell_variable_type")
                cell_type_info = None
                if cell_var_type:
                    if isinstance(cell_var_type, str):
                        cell_type_info = {"id": cell_var_type, "name": cell_var_type.title()}
                    elif isinstance(cell_var_type, dict):
                        cell_type_info = {
                            "id": cell_var_type.get("@id", ""),
                            "name": cell_var_type.get("ui_label") or cell_var_type.get("@id", "").title()
                        }
                
                # Parse grid cells reference
                grid_cells_ref = sg.get("horizontal_grid_cells")
                grid_cells_info = None
                if grid_cells_ref:
                    if isinstance(grid_cells_ref, str):
                        grid_cells_info = {"id": grid_cells_ref}
                    elif isinstance(grid_cells_ref, dict):
                        grid_cells_info = {
                            "id": grid_cells_ref.get("@id", ""),
                            "grid_type": grid_cells_ref.get("grid_type", ""),
                            "n_cells": grid_cells_ref.get("n_cells"),
                            "x_resolution": grid_cells_ref.get("x_resolution"),
                            "y_resolution": grid_cells_ref.get("y_resolution"),
                            "region": grid_cells_ref.get("region", {}).get("ui_label") if isinstance(grid_cells_ref.get("region"), dict) else None,
                            "truncation_number": grid_cells_ref.get("truncation_number"),
                            "truncation_method": grid_cells_ref.get("truncation_method"),
                        }
                
                subgrids.append({
                    "id": sg.get("@id", ""),
                    "description": sg.get("description", ""),
                    "cell_variable_type": cell_type_info,
                    "grid_cells": grid_cells_info
                })
    
    return {
        "id": grid_data.get("@id", ""),
        "description": grid_data.get("description", ""),
        "arrangement": arrangement,
        "subgrids": subgrids
    }


def parse_vertical_grid(grid_data: Any) -> Optional[dict]:
    """Parse vertical computational grid data."""
    if not grid_data:
        return None
    
    if isinstance(grid_data, str):
        return {"id": grid_data, "description": "", "n_z": None, "coordinate": None}
    
    if not isinstance(grid_data, dict):
        return None
    
    # Parse vertical coordinate
    coordinate = None
    coord_data = grid_data.get("vertical_coordinate")
    if coord_data:
        if isinstance(coord_data, str):
            coordinate = coord_data.replace("-", " ").title()
        elif isinstance(coord_data, dict):
            coordinate = coord_data.get("ui_label") or coord_data.get("description", "")
    
    return {
        "id": grid_data.get("@id", ""),
        "description": grid_data.get("description", ""),
        "n_z": grid_data.get("n_z"),
        "coordinate": coordinate,
        "top_thickness": grid_data.get("top_layer_thickness"),
        "bottom_thickness": grid_data.get("bottom_layer_thickness"),
        "total_thickness": grid_data.get("total_thickness")
    }


def parse_code_base(code_base: Any) -> dict:
    """Parse code_base field."""
    if not code_base:
        return {"value": None, "is_private": False, "is_url": False}
    
    if isinstance(code_base, str):
        is_private = code_base.lower() == "private"
        is_url = code_base.startswith("http://") or code_base.startswith("https://")
        return {
            "value": code_base,
            "is_private": is_private,
            "is_url": is_url
        }
    
    return {"value": str(code_base), "is_private": False, "is_url": False}


def parse_references(refs: Any) -> list:
    """Parse references field."""
    if not refs:
        return []
    
    if isinstance(refs, str):
        return [refs]
    
    if isinstance(refs, list):
        return [str(r) for r in refs]
    
    return []


def collect_keywords_from_data(data: dict) -> set:
    """Extract keywords from component data for highlighting."""
    keywords = set()
    
    # Add component name words
    name = data.get("name", "")
    if name:
        keywords.update(word.lower() for word in name.split() if len(word) > 3)
    
    # Add family name
    family = data.get("family")
    if isinstance(family, dict):
        family_name = family.get("ui_label") or family.get("@id", "")
        if family_name:
            keywords.update(word.lower() for word in family_name.replace("-", " ").split() if len(word) > 3)
    
    # Add domain names
    component = data.get("component")
    if isinstance(component, dict):
        domain_name = component.get("ui_label") or component.get("description", "")
        if domain_name:
            keywords.add(domain_name.lower())
    
    return keywords


def get_all_keywords() -> list:
    """Get combined list of all keywords for highlighting."""
    all_kw = BASE_KEYWORDS | collected_keywords
    # Sort by length (longest first) to avoid partial replacements
    return sorted(all_kw, key=len, reverse=True)


def highlight_keywords(text: str, extra_keywords: list = None) -> str:
    """Highlight important keywords in text with bold tags."""
    if not text:
        return ""
    
    # Start with escaped text
    result = escape_html(text)
    
    # Keywords to highlight
    keywords = get_all_keywords()
    if extra_keywords:
        keywords = list(extra_keywords) + keywords
    
    # Track which positions have been replaced to avoid double-highlighting
    import re
    
    for keyword in keywords:
        if not keyword or len(keyword) < 3:
            continue
        # Case-insensitive word boundary match
        pattern = re.compile(r'\b(' + re.escape(keyword) + r')\b', re.IGNORECASE)
        # Only replace if not already inside a tag
        def replace_if_not_tagged(match):
            return f'<strong>{match.group(1)}</strong>'
        
        # Simple replacement (may double-highlight in edge cases, but acceptable)
        result = pattern.sub(replace_if_not_tagged, result)
    
    # Clean up any double-strong tags
    result = re.sub(r'<strong><strong>', '<strong>', result)
    result = re.sub(r'</strong></strong>', '</strong>', result)
    
    return result


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
    coupled_with = parse_coupled_with(data.get("coupled_with"))
    
    # Grids
    horizontal_grid = parse_horizontal_grid(data.get("horizontal_computational_grid"))
    vertical_grid = parse_vertical_grid(data.get("vertical_computational_grid"))
    
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
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
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
    output_path = OUTPUT_DIR / filename.replace(".json", ".html")
    
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
    print("\n" + "=" * 60)
    print("Model Component Page Generator")
    print("=" * 60 + "\n")
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}\n")
    
    # Pre-fetch keywords
    prefetch_all_keywords()
    
    # Setup Jinja environment
    env = setup_jinja_env()
    template = env.get_template("model_component.html.j2")
    
    # Process all components
    print("Generating pages...")
    success_count = 0
    fail_count = 0
    
    for filename in MODEL_COMPONENTS:
        if process_component(env, template, filename):
            success_count += 1
        else:
            fail_count += 1
    
    # Summary
    print("\n" + "-" * 60)
    print(f"Complete: {success_count} succeeded, {fail_count} failed")
    print("-" * 60 + "\n")
    
    cmipld.client.close()
    return 0 if fail_count == 0 else 1


# Run on import for mkdocs
main()
