#!/usr/bin/env python3
"""
Build script to generate model HTML pages from JSON-LD metadata.

This script fetches JSON-LD data from the EMD registry and generates
styled HTML pages for each model using Jinja2 templates.

Usage:
    python generate_models.py

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
)
from helpers.utils import parse_references, highlight_keywords


# Configuration
BASE_URL = "https://emd.mipcvs.dev/model"
TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"
OUTPUT_DIR = SCRIPT_DIR.parent / "model"

# List of model JSON files to process
MODELS = [
    "cnrm-esm2-1.json",
    # Add more models here as needed
]

# Dynamic keywords collected from processed models
collected_keywords: set = set()


def collect_keywords_from_data(data: dict) -> list:
    """Extract potential keywords from model data."""
    keywords = []
    
    # Model name
    name = data.get("name")
    if name:
        keywords.append(name)
    
    # Long name
    long_name = data.get("long_name")
    if long_name and long_name != name:
        keywords.append(long_name)
    
    # Model type
    model_type = data.get("model_type") or data.get("type")
    if model_type and not is_none_value(model_type):
        keywords.append(model_type)
    
    # Component names
    components = data.get("components") or data.get("model_component") or data.get("has_component") or []
    if isinstance(components, dict):
        components = [components]
    
    for comp in components:
        if isinstance(comp, dict):
            comp_name = comp.get("name") or comp.get("ui_label")
            if comp_name:
                keywords.append(comp_name)
            # Also get component type
            comp_field = comp.get("component")
            if isinstance(comp_field, dict):
                comp_type = comp_field.get("ui_label")
                if comp_type:
                    keywords.append(comp_type)
        elif isinstance(comp, str) and not is_none_value(comp):
            keywords.append(comp)
    
    # Institution names
    institutions = data.get("institutions") or data.get("institution") or data.get("responsible_parties") or []
    if isinstance(institutions, dict):
        institutions = [institutions]
    
    for inst in institutions:
        if isinstance(inst, dict):
            inst_name = inst.get("name") or inst.get("ui_label")
            if inst_name:
                keywords.append(inst_name)
        elif isinstance(inst, str) and not is_none_value(inst):
            keywords.append(inst)
    
    # Activity participation
    activity = data.get("activity_participation") or data.get("activity") or []
    if isinstance(activity, str):
        activity = [activity]
    for act in activity:
        if act and not is_none_value(act):
            keywords.append(act)
    
    return keywords


def get_all_keywords() -> list:
    """Get combined list of default and collected keywords."""
    return HIGHLIGHT_KEYWORDS + list(collected_keywords)


def parse_component(comp_data: Any) -> Optional[dict]:
    """Parse a model component reference into a standardized dict."""
    if is_none_value(comp_data):
        return None
    
    if isinstance(comp_data, str):
        return {
            "id": comp_data,
            "name": comp_data,
            "description": "",
            "type": "Component",
        }
    
    if isinstance(comp_data, dict):
        comp_type = "Component"
        comp_field = comp_data.get("component")
        if isinstance(comp_field, dict):
            comp_type = comp_field.get("ui_label") or comp_field.get("description") or "Component"
        elif isinstance(comp_field, str) and not is_none_value(comp_field):
            comp_type = comp_field
            
        return {
            "id": comp_data.get("@id", ""),
            "name": comp_data.get("name") or comp_data.get("ui_label") or comp_data.get("@id", "Unknown"),
            "description": comp_data.get("description", ""),
            "type": comp_type,
        }
    
    return None


def parse_components(components_data: Any) -> list:
    """Parse model components into a list of component dicts."""
    if is_none_value(components_data):
        return []
    
    if isinstance(components_data, dict):
        parsed = parse_component(components_data)
        return [parsed] if parsed else []
    
    if isinstance(components_data, list):
        result = []
        for item in components_data:
            parsed = parse_component(item)
            if parsed:
                result.append(parsed)
        return result
    
    if isinstance(components_data, str):
        return [{"id": components_data, "name": components_data, "description": "", "type": "Component"}]
    
    return []


def parse_institution(inst_data: Any) -> Optional[dict]:
    """Parse institution data into a standardized dict."""
    if is_none_value(inst_data):
        return None
    
    if isinstance(inst_data, str):
        return {"id": inst_data, "name": inst_data, "url": ""}
    
    if isinstance(inst_data, dict):
        return {
            "id": inst_data.get("@id", ""),
            "name": inst_data.get("name") or inst_data.get("ui_label") or inst_data.get("@id", "Unknown"),
            "url": inst_data.get("url", ""),
        }
    
    return None


def parse_institutions(institutions_data: Any) -> list:
    """Parse institutions into a list."""
    if is_none_value(institutions_data):
        return []
    
    if isinstance(institutions_data, dict):
        parsed = parse_institution(institutions_data)
        return [parsed] if parsed else []
    
    if isinstance(institutions_data, list):
        result = []
        for item in institutions_data:
            parsed = parse_institution(item)
            if parsed:
                result.append(parsed)
        return result
    
    if isinstance(institutions_data, str):
        return [{"id": institutions_data, "name": institutions_data, "url": ""}]
    
    return []


def prepare_template_context(data: dict) -> dict:
    """Prepare the template context from raw JSON-LD data."""
    
    # Collect keywords from this model
    new_keywords = collect_keywords_from_data(data)
    collected_keywords.update(new_keywords)
    
    # Basic info
    model_id = data.get("@id", "unknown")
    name = data.get("name") or model_id.upper()
    description = data.get("description") or "No description available."
    long_name = data.get("long_name") or name
    
    # Extra keywords for this specific model
    extra_keywords = [name]
    if long_name and long_name != name:
        extra_keywords.append(long_name)
    
    # Use combined keywords for highlighting
    all_keywords = get_all_keywords()
    description_highlighted = highlight_keywords(description, extra_keywords + all_keywords)
    
    # Types
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]
    
    # Model type (ESM, GCM, etc.)
    model_type = data.get("model_type") or data.get("type") or ""
    
    # Release year
    release_year = data.get("release_year") or data.get("year") or ""
    
    # Components
    components = parse_components(data.get("components") or data.get("model_component") or data.get("has_component"))
    
    # Institutions
    institutions = parse_institutions(data.get("institutions") or data.get("institution") or data.get("responsible_parties"))
    
    # Activity participation
    activity = data.get("activity_participation") or data.get("activity") or []
    if isinstance(activity, str):
        activity = [activity] if activity and not is_none_value(activity) else []
    elif isinstance(activity, list):
        activity = [a for a in activity if a and not is_none_value(a)]
    
    # License
    license_info = data.get("license") or ""
    
    # References
    references = parse_references(data.get("references"))
    
    return {
        "id": model_id,
        "name": name,
        "long_name": long_name,
        "description": escape_html(description),
        "description_highlighted": description_highlighted,
        "model_type": model_type,
        "release_year": str(release_year) if release_year else "",
        "validation_key": data.get("validation_key", ""),
        "context_url": data.get("@context", ""),
        "types": types,
        "components": components,
        "institutions": institutions,
        "activity": activity,
        "license": license_info,
        "references": references,
        "icons": ICONS,
        "raw_json": json.dumps(data),  # Raw JSON for copy protection
    }


def setup_jinja_env() -> Environment:
    """Create and configure Jinja2 environment with model-specific macros."""
    env = create_jinja_env(TEMPLATE_DIR)
    
    # Add model-specific macros
    env.globals["section"] = create_section_macro("model")
    
    def component_card_macro(name, comp_type, comp_id, description):
        """Render a component card."""
        desc_html = f'<p class="model-card-description">{escape_html(description)}</p>' if description else ''
        return f'''<a href="../model_component/{escape_html(comp_id)}.html" class="model-component-card">
                        <div class="model-card-header">
                            <span class="model-card-title">{escape_html(name)}</span>
                            <span class="model-card-type">{escape_html(comp_type)}</span>
                        </div>
                        <div class="model-card-id">@id: {escape_html(comp_id)}</div>
                        {desc_html}
                        <div class="model-card-link">View component →</div>
                    </a>'''
    
    def institution_card_macro(name, inst_id, url):
        """Render an institution card."""
        url_html = f'<a href="{escape_html(url)}" target="_blank" class="model-card-url">{escape_html(url)}</a>' if url else ''
        return f'''<div class="model-institution-card">
                        <div class="model-card-header">
                            <span class="model-card-title">{escape_html(name)}</span>
                        </div>
                        <div class="model-card-id">@id: {escape_html(inst_id)}</div>
                        {url_html}
                    </div>'''
    
    env.globals["component_card"] = component_card_macro
    env.globals["institution_card"] = institution_card_macro
    
    return env


def prefetch_all_keywords() -> None:
    """Pre-fetch all models to collect keywords before generating pages."""
    print("  Collecting keywords from all models...")
    
    for filename in MODELS:
        url = f"{BASE_URL}/{filename}"
        try:
            data = cmipld.get(url)
            if data:
                new_keywords = collect_keywords_from_data(data)
                collected_keywords.update(new_keywords)
        except Exception:
            pass  # Silently skip errors during prefetch
    
    print(f"  Collected {len(collected_keywords)} additional keywords\n")


def process_model(env: Environment, template, filename: str) -> bool:
    """Fetch and process a single model."""
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
    print("Model Page Generator")
    print("=" * 60)
    
    # Create output directory
    print(f"\nCreating output directory: {OUTPUT_DIR}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if not TEMPLATE_DIR.exists():
        print(f"Error: Template directory not found: {TEMPLATE_DIR}")
        return 1
    
    print(f"Template directory: {TEMPLATE_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Processing {len(MODELS)} models...\n")
    
    # Pre-fetch to collect all keywords first
    prefetch_all_keywords()
    
    env = setup_jinja_env()
    
    try:
        template = env.get_template("model.html.j2")
    except Exception as e:
        print(f"Error loading template: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    success_count = 0
    fail_count = 0
    
    for filename in MODELS:
        if process_model(env, template, filename):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"Complete: {success_count} succeeded, {fail_count} failed")
    print("=" * 60)
    
    return 0 if fail_count == 0 else 1


main()
