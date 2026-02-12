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


def get_all_families():
    """Discover all model family files from the graph endpoint."""
    try:
        # Try to get the graph which lists all entities
        graph_data = cmipld.get(f"{BASE_URL}/graph.jsonld", depth=0)
        if graph_data and isinstance(graph_data, list):
            return [f"{item.get('@id')}.json" for item in graph_data if item.get('@id') and not item.get('@id').startswith('_')]
    except Exception:
        pass
    
    # Fallback: try known files from src-data branch structure
    return [
        "access.json", "arpege-climat.json", "bcc-csm.json", "bisicles.json",
        "cam.json", "canesm.json", "cesm.json", "clm.json", "cnrm-cm.json",
        "ec-earth.json", "fgoals.json", "gelato.json", "geos.json", "gfdl-cm4.json",
        "giss-e2.json", "hadam.json", "hadcm2.json", "hadgem3.json", "icon.json",
        "ifs.json", "ipsl-cm.json", "miroc.json", "mpi-esm.json", "nemo.json",
        "nicam.json", "pisces.json", "reprobus.json", "surfex.json", "tactic.json",
        "ukesm1.json"
    ]


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
        
        # Handle various name formats
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


def prepare_template_context(data):
    """Prepare context for Jinja2 template."""
    family_id = data.get("@id", "unknown")
    
    # Get name from various possible fields
    name = data.get("ui_label") or data.get("name") or data.get("validation_key") or family_id
    if not name or name == "":
        name = family_id.replace("-", " ").title()
    
    description = data.get("description") or "No description available."
    
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]
    
    # Parse related data
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
    
    # Highlight keywords in description
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


def process_family(env, template, filename, pbar=None):
    """Process a single model family file."""
    url = f"{BASE_URL}/{filename}"
    output_path = OUTPUT_DIR / filename.replace(".json", ".html")
    
    if pbar:
        pbar.set_description(f"Processing {filename[:30]}")
    
    try:
        data = cmipld.get(url)
        if not data:
            if pbar:
                pbar.write(f"No data for {filename}")
            return False
        
        context = prepare_template_context(data)
        html = template.render(**context)
        output_path.write_text(html, encoding="utf-8")
        return True
    except Exception as e:
        if pbar:
            pbar.write(f"Error {filename}: {e}")
        else:
            print(f"Error {filename}: {e}")
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
    
    # Discover all family files
    model_families = get_all_families()
    print(f"Found {len(model_families)} model families")
    
    success = 0
    with tqdm(model_families, desc="Generating families", unit="file") as pbar:
        for filename in pbar:
            if process_family(env, template, filename, pbar):
                success += 1
    
    print(f"Done: {success}/{len(model_families)} families generated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
