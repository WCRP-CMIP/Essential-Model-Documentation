#!/usr/bin/env python3
"""Generate component family HTML pages from JSON-LD metadata."""

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
from helpers.data_loader import init_loader, fetch_data, fetch_entry

import cmipld
cmipld.map_current("emd")


TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"
OUTPUT_DIR = SCRIPT_DIR.parent / "10_EMD_Repository" / "03_Component_Families"

# Old directories to clean up
OLD_DIRS = [
    SCRIPT_DIR.parent / "component_family",
]


def parse_institution(inst):
    """Parse institution data into a rich dict for the template."""
    if is_none_value(inst) or inst == "none":
        return None
    if isinstance(inst, str):
        return {"id": inst, "name": inst.replace("-", " ").title(), "acronym": "",
                "url": "", "location": None, "ror": "", "established": None}
    if isinstance(inst, dict):
        loc = inst.get("location")
        location = None
        if isinstance(loc, dict):
            location = {
                "name": loc.get("name", ""),
                "country": loc.get("country_name", ""),
                "country_code": loc.get("country_code", ""),
                "subdivision": loc.get("country_subdivision_name", ""),
                "continent": loc.get("continent_name", ""),
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

        urls = inst.get("url", "")
        url_list = urls if isinstance(urls, list) else ([urls] if urls else [])
        primary_url = next((u for u in url_list if u and "wikipedia" not in u), "")
        if not primary_url and url_list:
            primary_url = url_list[0]

        acronym = inst.get("acronyms", "")
        if isinstance(acronym, list):
            acronym = acronym[0] if acronym else ""

        established = inst.get("established")
        if is_none_value(established):
            established = None

        return {
            "id": inst.get("@id", ""),
            "name": name,
            "acronym": acronym,
            "url": primary_url,
            "location": location,
            "ror": inst.get("ror", ""),
            "established": established,
        }
    return None


def parse_domain(d):
    """Parse a scientific domain object into a dict for the template.

    Label priority: ui_label -> validation_key -> @id last segment.
    domain_key is normalised to hyphens (e.g. land-surface) to match CSS.
    """
    if is_none_value(d) or d == "none":
        return None

    def _normalise_key(raw):
        """Strip URL/prefix, take last path segment, normalise to hyphens."""
        slug = raw.split("/")[-1].split(":")[-1]
        return slug.replace("_", "-")

    if isinstance(d, str):
        key = _normalise_key(d)
        return {
            "id": _normalise_key(d),
            "domain_key": key,
            "name": key.replace("-", " ").title(),
            "description": "",
            "alias": "",
        }
    if isinstance(d, dict):
        raw_id = d.get("@id", "")
        key = _normalise_key(raw_id)
        name = (
            d.get("ui_label")
            or d.get("validation_key", "").replace("_", " ").replace("-", " ").title()
            or (key.replace("-", " ").title() if key else "")
        )
        return {
            "id": key,
            "domain_key": key,
            "name": name,
            "description": d.get("description", ""),
            "alias": d.get("alias", "") or d.get("aliases", ""),
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
    family_id = data.get("@id") or data.get("validation_key") or "unknown"
    
    name = data.get("ui_label") or data.get("name") or data.get("validation_key") or family_id
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
    
    # Component family specific fields
    shared_code_base = data.get("shared_code_base", "")
    source_code_repository = data.get("source_code_repository", "")
    programming_languages = data.get("programming_languages", [])
    if isinstance(programming_languages, str):
        programming_languages = [programming_languages]
    
    license_info = data.get("license", "")
    
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
        "family_type": "Component Family",
        "primary_institution": primary_institution,
        "collaborative_institutions": collaborative_institutions,
        "scientific_domains": scientific_domains,
        "established": established,
        "shared_code_base": shared_code_base,
        "source_code_repository": source_code_repository,
        "programming_languages": programming_languages,
        "license": license_info,
        "references": references,
        "icons": ICONS,
        "raw_json": json.dumps(data, indent=2),
        "depth": "../../",
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    }


def setup_jinja_env():
    """Setup Jinja2 environment."""
    return Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)


def process_family(env, template, data, pbar=None):
    """Process a single component family."""
    entry_id = data.get("@id") or data.get("validation_key") or "unknown"
    output_path = OUTPUT_DIR / f"{entry_id}.html"
    
    if pbar:
        pbar.set_description(f"Processing {entry_id[:30]}")
    
    try:
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


def remove_old_dirs():
    """Remove old directories."""
    import shutil
    for old_dir in OLD_DIRS:
        if old_dir.exists() and old_dir != OUTPUT_DIR:
            shutil.rmtree(old_dir)
            print(f"  Removed old directory: {old_dir.name}")


def main():
    print("Component Family Page Generator")
    print("=" * 40)
    
    # Initialize branch-aware data loading
    init_loader()
    
    # Remove old directories
    remove_old_dirs()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Clear old files
    clear_output_dir()
    
    env = setup_jinja_env()
    try:
        template = env.get_template("family.html.j2")
    except Exception as e:
        print(f"Template error: {e}")
        return 1
    
    # Get all model_family entries and filter for component families
    all_families = fetch_data("model_family", depth=4)
    families = [f for f in all_families if isinstance(f, dict) and f.get("family_type") == "component"]
    
    print(f"Found {len(families)} component families")
    
    if not families:
        print("No component families found - check data source")
        return 0
    
    success = 0
    with tqdm(families, desc="Generating component families", unit="file") as pbar:
        for data in pbar:
            if process_family(env, template, data, pbar):
                success += 1
    
    print(f"Done: {success}/{len(families)} component families generated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
else:
    main()
