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
from helpers.utils import parse_domain, parse_coupled_with, parse_code_base, parse_references, highlight_keywords


# Configuration
BASE_URL = "https://emd.mipcvs.dev/model_component"
TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"
OUTPUT_DIR = SCRIPT_DIR.parent / "model_component"

# List of model component JSON files to process
MODEL_COMPONENTS = [
    "arpege-climat-version-6-3.json",
    "piscesv2-gas.json",
    "bisicles-ukesm-ismip6-1.0.json",
    "reprobus-c-v2-0.json",
    "clm4.json",
    "surfex-v8-modeling-platform.json",
    "gelato.json",
    "tactic.json",
    "hadam3.json",
]

# Dynamic keywords collected from processed components
collected_keywords: set = set()


def collect_keywords_from_data(data: dict) -> list:
    """Extract potential keywords from component data."""
    keywords = []
    
    # Component name
    name = data.get("name")
    if name:
        keywords.append(name)
    
    # Family name
    family = data.get("family")
    if family and not is_none_value(family):
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
    family = data.get("family") or ""
    
    # Extra keywords for this specific component
    extra_keywords = [name]
    if family:
        extra_keywords.append(family)
    
    # Use combined keywords for highlighting
    all_keywords = get_all_keywords()
    description_highlighted = highlight_keywords(description, extra_keywords + all_keywords)
    
    # Types
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]
    
    # Component domain
    component_data = data.get("component")
    if isinstance(component_data, dict):
        component = parse_domain(component_data) or {
            "title": "Unknown",
            "id": "",
            "aliases": [],
            "validation_key": "",
        }
    else:
        component = {
            "title": "Unknown",
            "id": "",
            "aliases": [],
            "validation_key": "",
        }
    
    # Add validation_key to aliases for display
    if component.get("validation_key"):
        component["aliases"] = component["aliases"] + [component["validation_key"]]
    
    # Embedded in
    embedded_in = parse_domain(data.get("embedded_in"))
    
    # Grids
    h_grid = data.get("horizontal_computational_grid", "")
    v_grid = data.get("vertical_computational_grid", "")
    grids = {
        "horizontal": None if is_none_value(h_grid) else h_grid,
        "vertical": None if is_none_value(v_grid) else v_grid,
    }
    
    # Coupled with
    coupled_with = parse_coupled_with(data.get("coupled_with"))
    
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
        "component": component,
        "embedded_in": embedded_in,
        "grids": grids,
        "coupled_with": coupled_with,
        "code_base": parse_code_base(data.get("code_base")),
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


main()
