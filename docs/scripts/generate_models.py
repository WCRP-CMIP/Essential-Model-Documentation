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
OUTPUT_DIR = SCRIPT_DIR.parent / "model"


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
        
        return {
            "id": inst.get("@id", ""),
            "name": name,
            "acronym": inst.get("acronyms", ""),
            "url": url,
            "location": location
        }
    return None


def parse_license(lic):
    """Parse license data."""
    if is_none_value(lic):
        return None
    if isinstance(lic, str):
        return {"id": lic, "name": lic, "url": ""}
    if isinstance(lic, dict):
        return {
            "id": lic.get("@id", ""),
            "name": lic.get("ui_label", "") or lic.get("@id", ""),
            "url": lic.get("url", "")
        }
    return None


def parse_domain(d):
    """Parse scientific domain / component type."""
    if is_none_value(d):
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
        elif d.get("labels"):
            a = d.get("labels")
            aliases = a if isinstance(a, list) else [a]
        
        return {
            "id": d.get("@id", ""),
            "name": d.get("ui_label", "") or d.get("@id", "").replace("-", " ").title(),
            "description": d.get("description", ""),
            "aliases": aliases
        }
    return None


def parse_domains(domains):
    """Parse a list of domains."""
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


def parse_family(f):
    """Parse model family reference."""
    if is_none_value(f):
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
            "name": f.get("ui_label", "") or f.get("name", "") or f.get("@id", "").replace("-", " ").title(),
            "description": f.get("description", "")
        }
    return None


def parse_calendar(c):
    """Parse calendar type."""
    if is_none_value(c):
        return None
    if isinstance(c, str):
        return {
            "id": c,
            "name": c.replace("_", " ").title(),
            "description": ""
        }
    if isinstance(c, dict):
        return {
            "id": c.get("@id", ""),
            "name": c.get("ui_label", "") or c.get("@id", "").replace("_", " ").title(),
            "description": c.get("description", "")
        }
    return None


def parse_calendars(cals):
    """Parse list of calendars."""
    if is_none_value(cals):
        return []
    if isinstance(cals, str):
        p = parse_calendar(cals)
        return [p] if p else []
    if isinstance(cals, list):
        return [p for c in cals if (p := parse_calendar(c))]
    return []


def parse_embedded_components(embedded):
    """Parse embedded_components which is now a list of [embedded, host] pairs."""
    if is_none_value(embedded):
        return []
    if not isinstance(embedded, list):
        return []
    
    result = []
    for pair in embedded:
        if isinstance(pair, list) and len(pair) == 2:
            result.append({
                "embedded": pair[0],
                "host": pair[1],
                "embedded_name": pair[0].replace("-", " ").replace("_", " ").title(),
                "host_name": pair[1].replace("-", " ").replace("_", " ").title()
            })
    return result


def parse_coupling_groups(groups):
    """Parse coupling_groups which is a list of component groups."""
    if is_none_value(groups):
        return []
    if not isinstance(groups, list):
        return []
    
    result = []
    for group in groups:
        if isinstance(group, list):
            result.append({
                "components": group,
                "component_names": [c.replace("-", " ").replace("_", " ").title() for c in group]
            })
    return result


def parse_component_configs(configs):
    """Parse component_configs list."""
    if is_none_value(configs):
        return []
    if not isinstance(configs, list):
        return []
    return configs


def prepare_template_context(data):
    """Prepare context for Jinja2 template."""
    model_id = data.get("@id") or data.get("validation_key") or "unknown"
    name = data.get("name") or data.get("ui_label") or model_id.upper()
    description = data.get("description") or "No description available."
    
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]
    
    institution = parse_institution(data.get("institution"))
    license_info = parse_license(data.get("license"))
    family = parse_family(data.get("family"))
    calendars = parse_calendars(data.get("calendar"))
    
    dynamic_components = parse_domains(data.get("dynamic_components"))
    omitted_components = parse_domains(data.get("omitted_components"))
    prescribed_components = parse_domains(data.get("prescribed_components"))
    
    embedded_components = parse_embedded_components(data.get("embedded_components"))
    coupling_groups = parse_coupling_groups(data.get("coupling_groups"))
    component_configs = parse_component_configs(data.get("component_configs"))
    
    references = parse_references(data.get("references"))
    release_year = data.get("release_year", "")
    
    extra_kw = [name]
    if family:
        extra_kw.append(family.get("name", ""))
    description_highlighted = highlight_keywords(description, extra_kw + HIGHLIGHT_KEYWORDS)
    
    return {
        "id": model_id,
        "name": name,
        "description": escape_html(description),
        "description_highlighted": description_highlighted,
        "validation_key": data.get("validation_key", ""),
        "context_url": data.get("@context", ""),
        "types": types,
        "institution": institution,
        "license": license_info,
        "family": family,
        "calendar": calendars[0] if calendars else None,
        "calendars": calendars,
        "dynamic_components": dynamic_components,
        "omitted_components": omitted_components,
        "prescribed_components": prescribed_components,
        "embedded_components": embedded_components,
        "coupling_groups": coupling_groups,
        "component_configs": component_configs,
        "release_year": release_year,
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
    output_path = OUTPUT_DIR / f"{entry_id}.html"
    
    if pbar:
        pbar.set_description(f"Processing {entry_id[:30]}")
    
    try:
        data = fetch_entry("model", entry_id)
        if not data:
            if pbar:
                pbar.write(f"No data for {entry_id}")
            return False
        
        context = prepare_template_context(data)
        html = template.render(**context)
        output_path.write_text(html, encoding="utf-8")
        return True
    except Exception as e:
        if pbar:
            pbar.write(f"Error {entry_id}: {e}")
        else:
            print(f"Error {entry_id}: {e}")
        return False


def clear_output_dir():
    """Remove all .html files from output directory."""
    if OUTPUT_DIR.exists():
        files = list(OUTPUT_DIR.glob("*.html"))
        for f in files:
            f.unlink()


def main():
    print("Model Page Generator")
    print("=" * 40)
    
    # Initialize branch-aware data loading
    init_loader()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
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
        return 0  # Not an error, just no data yet
    
    success = 0
    with tqdm(entries, desc="Generating models", unit="file") as pbar:
        for entry_id in pbar:
            if process_model(env, template, entry_id, pbar):
                success += 1
    
    print(f"Done: {success}/{len(entries)} models generated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
