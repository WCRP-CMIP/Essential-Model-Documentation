#!/usr/bin/env python3
"""Generate model family HTML pages from JSON-LD metadata.

Splits families into two categories:
- Component Families (family_type: "component") -> Component_Family/
- Model Families (family_type: "model") -> Source_Family/
"""

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

from helpers import ICONS, HIGHLIGHT_KEYWORDS, is_none_value, escape_html
from helpers.utils import parse_references, highlight_keywords
from helpers.data_loader import init_loader, list_entries, fetch_entry

TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"

# Output directories with proper casing
OUTPUT_DIR_COMPONENT = SCRIPT_DIR.parent / "Component_Family"
OUTPUT_DIR_SOURCE = SCRIPT_DIR.parent / "Source_Family"

# Old directories to clean up
OLD_DIRS = [
    SCRIPT_DIR.parent / "model_family",
    SCRIPT_DIR.parent / "component_family", 
    SCRIPT_DIR.parent / "source_family",
]


def safe_filename(name):
    """Convert a display name to a safe filename."""
    if not name:
        return "unknown"
    name = str(name)
    name = name.replace('/', '-').replace('\\', '-').replace(':', '-')
    name = name.replace('<', '').replace('>', '').replace('"', '')
    name = name.replace('|', '-').replace('?', '').replace('*', '')
    return name.strip()


def get_display_name(data):
    """Get display name from data: ui_label (if non-empty) or validation_key."""
    ui_label = data.get("ui_label", "")
    validation_key = data.get("validation_key", "")
    
    # Use ui_label only if it's a non-empty string
    if ui_label and isinstance(ui_label, str) and ui_label.strip():
        return ui_label.strip()
    
    # Fall back to validation_key
    if validation_key and isinstance(validation_key, str) and validation_key.strip():
        return validation_key.strip()
    
    # Last resort: use @id
    return data.get("@id", "unknown")


def parse_institution(inst):
    """Parse institution data - handles both string IDs and resolved objects."""
    if is_none_value(inst) or inst == "none":
        return None
    if isinstance(inst, str):
        return {"id": inst, "name": inst.replace("-", " ").title(), "acronym": "", "url": "", "location": None}
    if isinstance(inst, dict):
        loc = inst.get("location")
        location = None
        if isinstance(loc, dict):
            location = {
                "name": loc.get("name", ""),
                "country": loc.get("country_name", ""),
                "continent": loc.get("continent_name", "")
            }
        
        name = inst.get("ui_label") or inst.get("name")
        if not name:
            labels = inst.get("labels")
            if isinstance(labels, list) and labels:
                name = labels[0]
            elif isinstance(labels, str):
                name = labels
            else:
                name = inst.get("@id", "").replace("-", " ").title()
        
        url = inst.get("url", "")
        if isinstance(url, list) and url:
            url = url[0]
        
        acronym = inst.get("acronyms", "")
        if isinstance(acronym, list) and acronym:
            acronym = acronym[0]
        
        return {
            "id": inst.get("@id", ""),
            "name": name,
            "acronym": acronym,
            "url": url,
            "location": location
        }
    return None


def parse_domain(d):
    """Parse scientific domain data."""
    if is_none_value(d) or d == "none":
        return None
    if isinstance(d, str):
        return {
            "id": d,
            "name": d.replace("-", " ").replace("_", " ").title(),
            "description": "",
            "alias": ""
        }
    if isinstance(d, dict):
        return {
            "id": d.get("@id", ""),
            "name": d.get("ui_label", "") or d.get("description", "") or d.get("@id", "").replace("-", " ").title(),
            "description": d.get("description", ""),
            "alias": d.get("alias", "")
        }
    return None


def parse_domains(domains):
    """Parse a list of scientific domains."""
    if is_none_value(domains):
        return []
    if isinstance(domains, str):
        p = parse_domain(domains)
        return [p] if p else []
    if isinstance(domains, dict):
        p = parse_domain(domains)
        return [p] if p else []
    if isinstance(domains, list):
        return [p for d in domains if (p := parse_domain(d))]
    return []


def prepare_template_context(data, family_type_label):
    """Prepare context for Jinja2 template."""
    family_id = data.get("@id") or data.get("validation_key") or "unknown"
    
    name = get_display_name(data)
    if not name or name == "":
        name = family_id.replace("-", " ").title()
    
    description = data.get("description") or "No description available."
    
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]
    
    primary_institution = parse_institution(data.get("primary_institution"))
    collaborative_institutions = []
    collab = data.get("collaborative_institutions", [])
    if isinstance(collab, list):
        collaborative_institutions = [parse_institution(i) for i in collab if parse_institution(i)]
    
    scientific_domains = parse_domains(data.get("scientific_domains"))
    references = parse_references(data.get("references"))
    
    established = data.get("established", "")
    if established == "none":
        established = ""
    
    representative_member = data.get("representative_member", "")
    if representative_member == "none":
        representative_member = ""
    
    website = data.get("website", "")
    if website == "none":
        website = ""
    
    extra_kw = [name]
    description_highlighted = highlight_keywords(description, extra_kw + HIGHLIGHT_KEYWORDS)
    
    return {
        "id": family_id,
        "name": name,
        "description": escape_html(description),
        "description_highlighted": description_highlighted,
        "validation_key": data.get("validation_key", ""),
        "context_url": data.get("@context", ""),
        "types": types,
        "family_type": family_type_label,
        "primary_institution": primary_institution,
        "collaborative_institutions": collaborative_institutions,
        "scientific_domains": scientific_domains,
        "established": established,
        "representative_member": representative_member,
        "website": website,
        "references": references,
        "icons": ICONS,
        "raw_json": json.dumps(data, indent=2),
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    }


def setup_jinja_env():
    """Setup Jinja2 environment."""
    return Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)


def process_family(env, template, entry_id, output_dir, family_type_label, pbar=None):
    """Process a single model family."""
    if pbar:
        pbar.set_description(f"Processing {entry_id[:30]}")
    
    try:
        data = fetch_entry("model_family", entry_id)
        if not data:
            if pbar:
                pbar.write(f"  No data for {entry_id}")
            return False
        
        # Get display name for filename
        display_name = get_display_name(data)
        filename = safe_filename(display_name) + ".html"
        output_path = output_dir / filename
        
        if pbar:
            pbar.write(f"  {entry_id} -> {filename}")
        
        context = prepare_template_context(data, family_type_label)
        html = template.render(**context)
        output_path.write_text(html, encoding="utf-8")
        
        return True
    except Exception as e:
        if pbar:
            pbar.write(f"  Error {entry_id}: {e}")
        else:
            print(f"  Error {entry_id}: {e}")
        return False


def clear_output_dir(output_dir):
    """Remove all .html files from output directory."""
    if output_dir.exists():
        files = list(output_dir.glob("*.html"))
        for f in files:
            f.unlink()


def remove_old_dirs():
    """Remove old directories that have been replaced."""
    import shutil
    for old_dir in OLD_DIRS:
        if old_dir.exists():
            shutil.rmtree(old_dir)
            print(f"  Removed old directory: {old_dir.name}")


def main():
    print("Model Family Page Generator")
    print("=" * 40)
    
    # Initialize branch-aware data loading
    init_loader()
    
    # Remove old directories
    remove_old_dirs()
    
    # Create new directories
    OUTPUT_DIR_COMPONENT.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR_SOURCE.mkdir(parents=True, exist_ok=True)
    print(f"  Output dirs: {OUTPUT_DIR_COMPONENT.name}, {OUTPUT_DIR_SOURCE.name}")
    
    # Clear any existing files
    clear_output_dir(OUTPUT_DIR_COMPONENT)
    clear_output_dir(OUTPUT_DIR_SOURCE)
    
    env = setup_jinja_env()
    try:
        template = env.get_template("model_family.html.j2")
    except Exception as e:
        print(f"Template error: {e}")
        return 1
    
    # Get all family entries
    entries = list_entries("model_family")
    print(f"Found {len(entries)} model families")
    
    if not entries:
        print("No model families found - check data source")
        return 0
    
    # First pass: categorize families
    component_families = []
    source_families = []
    
    for entry_id in entries:
        data = fetch_entry("model_family", entry_id)
        if data:
            family_type = data.get("family_type", "")
            if family_type == "component":
                component_families.append(entry_id)
            else:
                # Default to source/model family
                source_families.append(entry_id)
    
    print(f"  Component Families: {len(component_families)}")
    print(f"  Source Families: {len(source_families)}")
    
    success_component = 0
    success_source = 0
    
    # Process component families
    if component_families:
        print(f"\nGenerating Component Families -> {OUTPUT_DIR_COMPONENT.name}/")
        with tqdm(component_families, desc="Component families", unit="file") as pbar:
            for entry_id in pbar:
                if process_family(env, template, entry_id, OUTPUT_DIR_COMPONENT, "Component Family", pbar):
                    success_component += 1
    
    # Process source/model families
    if source_families:
        print(f"\nGenerating Source Families -> {OUTPUT_DIR_SOURCE.name}/")
        with tqdm(source_families, desc="Source families", unit="file") as pbar:
            for entry_id in pbar:
                if process_family(env, template, entry_id, OUTPUT_DIR_SOURCE, "Source Family", pbar):
                    success_source += 1
    
    print(f"\nDone:")
    print(f"  Component Families: {success_component}/{len(component_families)} in {OUTPUT_DIR_COMPONENT.name}/")
    print(f"  Source Families: {success_source}/{len(source_families)} in {OUTPUT_DIR_SOURCE.name}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
