#!/usr/bin/env python3
"""Generate model component HTML pages from JSON-LD metadata."""

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
OUTPUT_DIR = SCRIPT_DIR.parent / "1_Explore_The_EMD" / "Model_Components"

# Old directories to clean up
OLD_DIRS = [
    SCRIPT_DIR.parent / "model_component",
    SCRIPT_DIR.parent / "Model_Component",
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
        return {"id": f, "name": f.replace("-", " ").title(),
                "description": "", "page": f"../Component_Families/{f}.html"}
    if isinstance(f, dict):
        fid = f.get("@id", "")
        return {
            "id": fid,
            "name": f.get("ui_label") or f.get("name") or fid.replace("-", " ").title(),
            "description": f.get("description", ""),
            "page": f"../Component_Families/{fid}.html",
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
    component_id = data.get("@id") or data.get("validation_key") or "unknown"
    name = get_display_name(data)
    description = data.get("description") or "No description available."
    
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]
    
    # Parse related data
    family = parse_family(data.get("family"))
    component_domain = parse_domain(data.get("component"))
    code_base = parse_code_base(data.get("code_base"))
    references = parse_references(data.get("references"))
    
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


def process_component(env, template, entry_id, pbar=None):
    """Process a single model component."""
    if pbar:
        pbar.set_description(f"Processing {entry_id[:30]}")
    
    try:
        data = fetch_entry("model_component", entry_id)
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
    print("Model Component Page Generator")
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
        template = env.get_template("model_component.html.j2")
    except Exception as e:
        print(f"Template error: {e}")
        return 1
    
    # Get all component entries
    entries = list_entries("model_component")
    print(f"Found {len(entries)} model components")
    
    if not entries:
        print("No model components found - check data source")
        return 0
    
    success = 0
    with tqdm(entries, desc="Generating components", unit="file") as pbar:
        for entry_id in pbar:
            if process_component(env, template, entry_id, pbar):
                success += 1
    
    print(f"Done: {success}/{len(entries)} components generated in {OUTPUT_DIR.name}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
else:
    main()
