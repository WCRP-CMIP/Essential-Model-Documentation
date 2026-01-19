#!/usr/bin/env python3
"""Generate model HTML pages from JSON-LD metadata."""

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

BASE_URL = "https://emd.mipcvs.dev/model"
TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"
OUTPUT_DIR = SCRIPT_DIR.parent / "model"
MODELS = ["cnrm-esm2-1e.json"]


def safe_get_label(obj, default=""):
    if obj is None: return default
    if isinstance(obj, str): return obj
    if isinstance(obj, dict): return obj.get("ui_label", "") or obj.get("name", "") or obj.get("@id", "") or default
    return default


def parse_institution(inst):
    if is_none_value(inst): return None
    if isinstance(inst, str): return {"id": inst, "name": inst, "acronym": "", "url": "", "location": None}
    if isinstance(inst, dict):
        loc = inst.get("location")
        location = {"name": loc.get("name",""), "country": loc.get("country_name",""), "continent": loc.get("continent_name","")} if isinstance(loc, dict) else None
        name = inst.get("ui_label") or (inst.get("labels")[0] if isinstance(inst.get("labels"), list) and inst.get("labels") else inst.get("labels") if isinstance(inst.get("labels"), str) else inst.get("@id", ""))
        url = inst.get("url", "")
        if isinstance(url, list) and url: url = url[0]
        return {"id": inst.get("@id", ""), "name": name, "acronym": inst.get("acronyms", ""), "url": url, "location": location}
    return None


def parse_license(lic):
    if is_none_value(lic): return None
    if isinstance(lic, str): return {"id": lic, "name": lic, "url": ""}
    if isinstance(lic, dict): return {"id": lic.get("@id", ""), "name": lic.get("ui_label", "") or lic.get("@id", ""), "url": lic.get("url", "")}
    return None


def parse_domain(d):
    if is_none_value(d): return None
    if isinstance(d, str): return {"id": d, "name": d, "description": "", "aliases": []}
    if isinstance(d, dict):
        # Extract aliases from various possible fields
        aliases = []
        if d.get("aliases"):
            a = d.get("aliases")
            if isinstance(a, list):
                aliases = a
            elif isinstance(a, str):
                aliases = [a]
        elif d.get("labels"):
            a = d.get("labels")
            if isinstance(a, list):
                aliases = a
            elif isinstance(a, str):
                aliases = [a]
        return {
            "id": d.get("@id", ""),
            "name": d.get("ui_label", "") or d.get("@id", ""),
            "description": d.get("description", ""),
            "aliases": aliases
        }
    return None


def parse_domains(domains):
    if is_none_value(domains): return []
    if isinstance(domains, dict):
        p = parse_domain(domains)
        return [p] if p else []
    if isinstance(domains, list): return [p for d in domains if (p := parse_domain(d))]
    return []


def parse_family(f):
    if is_none_value(f): return None
    if isinstance(f, str): return {"id": f, "name": f, "description": ""}
    if isinstance(f, dict): return {"id": f.get("@id", ""), "name": f.get("ui_label", "") or f.get("@id", ""), "description": f.get("description", "")}
    return None


def parse_calendar(c):
    if is_none_value(c): return None
    if isinstance(c, str): return {"id": c, "name": c, "description": ""}
    if isinstance(c, dict): return {"id": c.get("@id", ""), "name": c.get("ui_label", "") or c.get("@id", ""), "description": c.get("description", "")}
    return None


def prepare_template_context(data):
    model_id = data.get("@id", "unknown")
    name = data.get("name") or data.get("ui_label") or model_id.upper()
    description = data.get("description") or "No description available."
    types = data.get("@type", [])
    if isinstance(types, str): types = [types]
    
    institution = parse_institution(data.get("institution"))
    license_info = parse_license(data.get("license"))
    family = parse_family(data.get("family"))
    calendar = parse_calendar(data.get("calendar"))
    dynamic_components = parse_domains(data.get("dynamic_components"))
    omitted_components = parse_domains(data.get("omitted_components"))
    prescribed_components = parse_domains(data.get("prescribed_components"))
    references = parse_references(data.get("references"))
    release_year = data.get("release_year", "")
    
    extra_kw = [name]
    if family: extra_kw.append(family.get("name", ""))
    description_highlighted = highlight_keywords(description, extra_kw + HIGHLIGHT_KEYWORDS)
    
    return {
        "id": model_id, "name": name, "description": escape_html(description),
        "description_highlighted": description_highlighted,
        "validation_key": data.get("validation_key", ""),
        "context_url": data.get("@context", ""), "types": types,
        "institution": institution, "license": license_info, "family": family,
        "calendar": calendar, "dynamic_components": dynamic_components,
        "omitted_components": omitted_components, "prescribed_components": prescribed_components,
        "release_year": release_year, "references": references,
        "icons": ICONS, "raw_json": json.dumps(data),
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    }


def setup_jinja_env():
    return Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)


def process_model(env, template, filename, pbar=None):
    url = f"{BASE_URL}/{filename}"
    output_path = OUTPUT_DIR / filename.replace(".json", ".html")
    if pbar:
        pbar.set_description(f"Processing {filename[:30]}")
    try:
        data = cmipld.get(url)
        if not data:
            return False
        context = prepare_template_context(data)
        html = template.render(**context)
        output_path.write_text(html, encoding="utf-8")
        return True
    except Exception as e:
        if pbar:
            pbar.write(f"Error {filename}: {e}")
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
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Clear old files
    clear_output_dir()
    
    env = setup_jinja_env()
    try:
        template = env.get_template("model.html.j2")
    except Exception as e:
        print(f"Template error: {e}")
        return 1
    
    success = 0
    with tqdm(MODELS, desc="Generating models", unit="file") as pbar:
        for filename in pbar:
            if process_model(env, template, filename, pbar):
                success += 1
    
    print(f"Done: {success}/{len(MODELS)} models generated")
    # cmipld.client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
