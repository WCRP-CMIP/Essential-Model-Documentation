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
    "cnrm-esm2-1e.json",
    # Add more models here as needed
]

# Dynamic keywords collected from processed models
collected_keywords: set = set()


def parse_scientific_domain(domain_data: Any) -> Optional[dict]:
    """Parse a scientific domain (dynamic/omitted/prescribed component)."""
    if is_none_value(domain_data):
        return None
    
    if isinstance(domain_data, str):
        return {
            "id": domain_data,
            "name": domain_data,
            "description": "",
            "type": "Domain",
        }
    
    if isinstance(domain_data, dict):
        return {
            "id": domain_data.get("@id", ""),
            "name": domain_data.get("ui_label") or domain_data.get("name") or domain_data.get("@id", "Unknown"),
            "description": domain_data.get("description", ""),
            "type": "Dynamic",
            "validation_key": domain_data.get("validation_key", ""),
        }
    
    return None


def parse_scientific_domains(domains_data: Any) -> list:
    """Parse scientific domains into a list."""
    if is_none_value(domains_data):
        return []
    
    if isinstance(domains_data, dict):
        parsed = parse_scientific_domain(domains_data)
        return [parsed] if parsed else []
    
    if isinstance(domains_data, list):
        result = []
        for item in domains_data:
            parsed = parse_scientific_domain(item)
            if parsed:
                result.append(parsed)
        return result
    
    if isinstance(domains_data, str):
        return [{"id": domains_data, "name": domains_data, "description": "", "type": "Domain"}]
    
    return []


def parse_calendar(calendar_data: Any) -> Optional[dict]:
    """Parse calendar data."""
    if is_none_value(calendar_data):
        return None
    
    if isinstance(calendar_data, str):
        return {"id": calendar_data, "name": calendar_data, "description": ""}
    
    if isinstance(calendar_data, dict):
        return {
            "id": calendar_data.get("@id", ""),
            "name": calendar_data.get("ui_label") or calendar_data.get("name") or calendar_data.get("@id", "Unknown"),
            "description": calendar_data.get("description", ""),
            "validation_key": calendar_data.get("validation_key", ""),
        }
    
    return None


def collect_keywords_from_data(data: dict) -> list:
    """Extract potential keywords from model data."""
    keywords = []
    
    # Model name
    name = data.get("name")
    if name:
        keywords.append(name)
    
    # Family
    family = data.get("family")
    if family and not is_none_value(family):
        keywords.append(family)
    
    # Dynamic components
    dynamic_components = data.get("dynamic_components") or []
    if isinstance(dynamic_components, dict):
        dynamic_components = [dynamic_components]
    
    for comp in dynamic_components:
        if isinstance(comp, dict):
            comp_name = comp.get("ui_label") or comp.get("name")
            if comp_name:
                keywords.append(comp_name)
        elif isinstance(comp, str) and not is_none_value(comp):
            keywords.append(comp)
    
    # Omitted components
    omitted = data.get("omitted_components")
    if isinstance(omitted, dict):
        label = omitted.get("ui_label") or omitted.get("name")
        if label:
            keywords.append(label)
    elif isinstance(omitted, list):
        for item in omitted:
            if isinstance(item, dict):
                label = item.get("ui_label") or item.get("name")
                if label:
                    keywords.append(label)
    
    # Calendar
    calendar = data.get("calendar")
    if isinstance(calendar, dict):
        cal_name = calendar.get("ui_label") or calendar.get("name")
        if cal_name:
            keywords.append(cal_name)
    
    return keywords


def get_all_keywords() -> list:
    """Get combined list of default and collected keywords."""
    return HIGHLIGHT_KEYWORDS + list(collected_keywords)


def prepare_template_context(data: dict) -> dict:
    """Prepare the template context from raw JSON-LD data."""
    
    # Collect keywords from this model
    new_keywords = collect_keywords_from_data(data)
    collected_keywords.update(new_keywords)
    
    # Basic info
    model_id = data.get("@id", "unknown")
    name = data.get("name") or model_id.upper()
    description = data.get("description") or "No description available."
    family = data.get("family") or ""
    
    # Extra keywords for this specific model
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
    
    # Release year
    release_year = data.get("release_year") or data.get("year") or ""
    
    # Dynamic components (scientific domains)
    dynamic_components = parse_scientific_domains(data.get("dynamic_components"))
    
    # Omitted components
    omitted_components = parse_scientific_domains(data.get("omitted_components"))
    
    # Prescribed components
    prescribed_components = parse_scientific_domains(data.get("prescribed_components"))
    
    # Calendar
    calendar = parse_calendar(data.get("calendar"))
    
    # References
    references = parse_references(data.get("references"))
    
    return {
        "id": model_id,
        "name": name,
        "family": family,
        "description": escape_html(description),
        "description_highlighted": description_highlighted,
        "release_year": str(release_year) if release_year else "",
        "validation_key": data.get("validation_key", ""),
        "context_url": data.get("@context", ""),
        "types": types,
        "dynamic_components": dynamic_components,
        "omitted_components": omitted_components,
        "prescribed_components": prescribed_components,
        "calendar": calendar,
        "references": references,
        "icons": ICONS,
        "raw_json": json.dumps(data),  # Raw JSON for copy protection
    }


def setup_jinja_env() -> Environment:
    """Create and configure Jinja2 environment with model-specific macros."""
    env = create_jinja_env(TEMPLATE_DIR)
    
    # Add model-specific macros
    env.globals["section"] = create_section_macro("model")
    
    def domain_card_macro(name, domain_type, domain_id, description):
        """Render a scientific domain card."""
        desc_html = f'<p class="model-card-description">{escape_html(description)}</p>' if description else ''
        return f'''<div class="model-domain-card">
                        <div class="model-card-header">
                            <span class="model-card-title">{escape_html(name)}</span>
                            <span class="model-card-type">{escape_html(domain_type)}</span>
                        </div>
                        <div class="model-card-id">@id: {escape_html(domain_id)}</div>
                        {desc_html}
                    </div>'''
    
    env.globals["domain_card"] = domain_card_macro
    
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


def run():
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


run()
