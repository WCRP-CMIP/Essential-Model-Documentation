#!/usr/bin/env python3
"""Generate model HTML pages from JSON-LD metadata."""

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
OUTPUT_DIR = SCRIPT_DIR.parent / "1_Explore_The_EMD" / "Models"

# Old directories to clean up
OLD_DIRS = [
    SCRIPT_DIR.parent / "model",
    SCRIPT_DIR.parent / "Model",
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
    """Get display name: name (preferred), ui_label, or validation_key."""
    # For models, 'name' is the primary display field
    name = data.get("name", "")
    if name and isinstance(name, str) and name.strip():
        return name.strip()
    
    ui_label = data.get("ui_label", "")
    if ui_label and isinstance(ui_label, str) and ui_label.strip():
        return ui_label.strip()
    
    validation_key = data.get("validation_key", "")
    if validation_key and isinstance(validation_key, str) and validation_key.strip():
        return validation_key.strip()
    
    return data.get("@id", "unknown")


def safe_get_label(obj, default=""):
    """Safely extract a label from various object types."""
    if obj is None:
        return default
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return obj.get("ui_label", "") or obj.get("name", "") or obj.get("@id", "") or default
    return default


def parse_institution(inst):
    """Parse institution data."""
    if is_none_value(inst):
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


def parse_family(f):
    """Parse model family reference."""
    if is_none_value(f) or f == "none":
        return None
    if isinstance(f, str):
        return {
            "id": f,
            "name": f.replace("-", " ").title(),
            "description": "",
            "page": f"../ESM_Families/{f}.html",
        }
    if isinstance(f, dict):
        fid = f.get("@id", "")
        return {
            "id": fid,
            "name": f.get("ui_label") or f.get("name") or fid.replace("-", " ").title(),
            "description": f.get("description", ""),
            "page": f"../ESM_Families/{fid}.html",
        }
    return None


def parse_component_config(cc):
    """Parse component config reference."""
    if is_none_value(cc):
        return None
    if isinstance(cc, str):
        return {"id": cc, "name": cc.replace("-", " ").replace("_", " ").title(),
                "description": "", "component": "", "h_grid": "", "h_grid_id": "",
                "v_grid": "", "v_grid_id": ""}
    if isinstance(cc, dict):
        hcg = cc.get("horizontal_computational_grid")
        vcg = cc.get("vertical_computational_grid")
        mc  = cc.get("model_component")
        h_id = hcg.get("@id", "") if isinstance(hcg, dict) else (hcg or "")
        v_id = vcg.get("@id", "") if isinstance(vcg, dict) else (vcg or "")
        return {
            "id": cc.get("@id", ""),
            "name": cc.get("ui_label") or cc.get("@id", "").replace("-", " ").replace("_", " ").title(),
            "description": cc.get("description", ""),
            "component": safe_get_label(mc),
            "h_grid": safe_get_label(hcg),
            "h_grid_id": h_id,
            "h_grid_page": f"../Horizontal_Computational_Grids/{h_id}.html" if h_id else "",
            "v_grid": safe_get_label(vcg),
            "v_grid_id": v_id,
            "v_grid_page": f"../Vertical_Computational_Grids/{v_id}.html" if v_id else "",
        }
    return None


def parse_list_items(items, parser_func=None):
    """Parse a list of items, optionally using a parser function."""
    if is_none_value(items):
        return []
    if isinstance(items, str):
        return [items] if items and items != "none" else []
    if isinstance(items, dict):
        return [parser_func(items)] if parser_func else [items]
    if isinstance(items, list):
        result = []
        for item in items:
            if is_none_value(item) or item == "none":
                continue
            if parser_func:
                parsed = parser_func(item)
                if parsed:
                    result.append(parsed)
            else:
                result.append(item)
        return result
    return []


def parse_nested_list(items):
    """Parse nested list structure (for embedded_components, coupling_groups)."""
    if is_none_value(items):
        return []
    if isinstance(items, list):
        result = []
        for item in items:
            if isinstance(item, list):
                # Each sublist is a group
                group = [safe_get_label(i) if isinstance(i, dict) else str(i) for i in item if not is_none_value(i)]
                if group:
                    result.append(group)
            elif not is_none_value(item):
                result.append([safe_get_label(item) if isinstance(item, dict) else str(item)])
        return result
    return []


def prepare_template_context(data):
    """Prepare context for Jinja2 template."""
    model_id = data.get("@id") or data.get("validation_key") or "unknown"
    name = get_display_name(data)
    description = data.get("description") or "No description available."
    
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]
    
    # Parse related data
    family = parse_family(data.get("family"))
    references = parse_references(data.get("references"))
    
    # Components
    component_configs = parse_list_items(data.get("component_configs"), parse_component_config)
    dynamic_components = parse_list_items(data.get("dynamic_components"))
    prescribed_components = parse_list_items(data.get("prescribed_components"))
    omitted_components = parse_list_items(data.get("omitted_components"))
    
    # Nested structures
    embedded_components = parse_nested_list(data.get("embedded_components"))
    coupling_groups = parse_nested_list(data.get("coupling_groups"))
    
    # Calendar
    calendar = data.get("calendar", [])
    if isinstance(calendar, str):
        calendar = [calendar]
    elif is_none_value(calendar):
        calendar = []
    
    # Release year
    release_year = data.get("release_year", "")
    if release_year == "none" or is_none_value(release_year):
        release_year = ""
    
    # Highlight keywords
    extra_kw = [name]
    if family:
        extra_kw.append(family.get("name", ""))
    description_highlighted = highlight_keywords(description, extra_kw + HIGHLIGHT_KEYWORDS)
    
    return {
        "id": model_id,
        "name": name,
        "description": escape_html(description),
        "description_highlighted": description_highlighted,
        "family": family,
        "validation_key": data.get("validation_key", ""),
        "context_url": data.get("@context", ""),
        "types": types,
        "release_year": release_year,
        "calendar": calendar,
        "component_configs": component_configs,
        "dynamic_components": dynamic_components,
        "prescribed_components": prescribed_components,
        "omitted_components": omitted_components,
        "embedded_components": embedded_components,
        "coupling_groups": coupling_groups,
        "references": references,
        "icons": ICONS,
        "raw_json": json.dumps(data, indent=2),
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    }


def setup_jinja_env():
    """Setup Jinja2 environment."""
    return Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)


def process_model(env, template, entry_id, pbar=None):
    """Process a single model."""
    if pbar:
        pbar.set_description(f"Processing {entry_id[:30]}")
    
    try:
        data = fetch_entry("model", entry_id)
        if not data:
            if pbar:
                pbar.write(f"  No data for {entry_id}")
            return False
        
        # Get display name for filename
        display_name = get_display_name(data)
        filename = safe_filename(display_name) + ".html"
        output_path = OUTPUT_DIR / filename
        
        if pbar:
            pbar.write(f"  {entry_id} -> {filename}")
        
        context = prepare_template_context(data)
        html = template.render(**context)
        output_path.write_text(html, encoding="utf-8")
        return True
    except Exception as e:
        if pbar:
            pbar.write(f"  Error {entry_id}: {e}")
        else:
            print(f"  Error {entry_id}: {e}")
        return False


def clear_output_dir():
    """Remove all .html files from output directory."""
    if OUTPUT_DIR.exists():
        files = list(OUTPUT_DIR.glob("*.html"))
        for f in files:
            f.unlink()


def remove_old_dirs():
    """Remove old directories."""
    import shutil
    for old_dir in OLD_DIRS:
        if old_dir.exists() and old_dir != OUTPUT_DIR:
            shutil.rmtree(old_dir)
            print(f"  Removed old directory: {old_dir.name}")


def main():
    print("Model Page Generator")
    print("=" * 40)
    
    # Initialize branch-aware data loading
    init_loader()
    
    # Remove old directories
    remove_old_dirs()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  Output dir: {OUTPUT_DIR.name}")
    
    # Clear old files
    clear_output_dir()
    
    env = setup_jinja_env()
    try:
        template = env.get_template("model.html.j2")
    except Exception as e:
        print(f"Template error: {e}")
        return 1
    
    # Get all model entries
    entries = list_entries("model")
    print(f"Found {len(entries)} models")
    
    if not entries:
        print("No models found - check data source")
        return 0
    
    success = 0
    with tqdm(entries, desc="Generating models", unit="file") as pbar:
        for entry_id in pbar:
            if process_model(env, template, entry_id, pbar):
                success += 1
    
    print(f"Done: {success}/{len(entries)} models generated in {OUTPUT_DIR.name}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
else:
    main()
