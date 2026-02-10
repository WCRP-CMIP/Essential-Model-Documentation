#!/usr/bin/env python3
"""Generate model family HTML pages from JSON-LD metadata."""

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

BASE_URL = "https://emd.mipcvs.dev/model_family"
TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"
OUTPUT_DIR = SCRIPT_DIR.parent / "model_family"

# Model families to generate
MODEL_FAMILIES = [
    "arpege-climat.json",
    "bcc-csm.json",
    "bisicles.json",
    "cam.json",
    "canesm.json",
    "cesm.json",
    "clm.json",
]


def parse_institution(inst):
    if is_none_value(inst) or inst == "none": return None
    if isinstance(inst, str): return {"id": inst, "name": inst, "acronym": "", "url": "", "location": None}
    if isinstance(inst, dict):
        loc = inst.get("location")
        location = {"name": loc.get("name",""), "country": loc.get("country_name",""), "continent": loc.get("continent_name","")} if isinstance(loc, dict) else None
        name = inst.get("ui_label") or (inst.get("labels")[0] if isinstance(inst.get("labels"), list) and inst.get("labels") else inst.get("labels") if isinstance(inst.get("labels"), str) else inst.get("@id", ""))
        url = inst.get("url", "")
        if isinstance(url, list) and url: url = url[0]
        return {"id": inst.get("@id", ""), "name": name, "acronym": inst.get("acronyms", ""), "url": url, "location": location}
    return None


def parse_domain(d):
    if is_none_value(d) or d == "none": return None
    if isinstance(d, str): return {"id": d, "name": d.replace("-", " ").title(), "description": "", "alias": ""}
    if isinstance(d, dict): return {
        "id": d.get("@id", ""),
        "name": d.get("ui_label", "") or d.get("description", "") or d.get("@id", "").replace("-", " ").title(),
        "description": d.get("description", ""),
        "alias": d.get("alias", "")
    }
    return None


def prepare_template_context(data):
    family_id = data.get("@id", "unknown")
    name = data.get("ui_label") or data.get("validation_key") or family_id.upper()
    if not name or name == "":
        name = family_id.upper()
    description = data.get("description") or "No description available."
    types = data.get("@type", [])
    if isinstance(types, str): types = [types]
    
    primary_institution = parse_institution(data.get("primary_institution"))
    scientific_domain = parse_domain(data.get("scientific_domains"))
    references = parse_references(data.get("references"))
    established = data.get("established", "")
    if established == "none": established = ""
    
    extra_kw = [name]
    description_highlighted = highlight_keywords(description, extra_kw + HIGHLIGHT_KEYWORDS)
    
    return {
        "id": family_id, "name": name, "description": escape_html(description),
        "description_highlighted": description_highlighted,
        "validation_key": data.get("validation_key", ""),
        "context_url": data.get("@context", ""), "types": types,
        "primary_institution": primary_institution,
        "scientific_domain": scientific_domain,
        "established": established,
        "references": references,
        "icons": ICONS, "raw_json": json.dumps(data),
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    }


def setup_jinja_env():
    return Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)


def process_family(env, template, filename, pbar=None):
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
    print("Model Family Page Generator")
    print("=" * 40)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Clear old files
    clear_output_dir()
    
    env = setup_jinja_env()
    try:
        template = env.get_template("model_family.html.j2")
    except Exception as e:
        print(f"Template error: {e}")
        return 1
    
    success = 0
    with tqdm(MODEL_FAMILIES, desc="Generating families", unit="file") as pbar:
        for filename in pbar:
            if process_family(env, template, filename, pbar):
                success += 1
    
    print(f"Done: {success}/{len(MODEL_FAMILIES)} families generated")
    # cmipld.client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
