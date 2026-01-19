#!/usr/bin/env python3
"""Model page generator - FIXED VERSION"""

import json
import sys
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

from helpers import ICONS, HIGHLIGHT_KEYWORDS, is_none_value, escape_html
from helpers.utils import parse_references, highlight_keywords

BASE_URL = "https://emd.mipcvs.dev/model"
TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"
OUTPUT_DIR = SCRIPT_DIR.parent / "model"
MODELS = ["cnrm-esm2-1e.json"]


def safe_get_label(obj, default=""):
    if obj is None:
        return default
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return obj.get("ui_label", "") or obj.get("name", "") or obj.get("@id", "") or default
    return default


def parse_institution(inst_data):
    if is_none_value(inst_data):
        return None
    if isinstance(inst_data, str):
        return {"id": inst_data, "name": inst_data, "acronym": "", "url": "", "location": None}
    if isinstance(inst_data, dict):
        loc = inst_data.get("location")
        location = None
        if isinstance(loc, dict):
            location = {"name": loc.get("name", ""), "country": loc.get("country_name", ""), "continent": loc.get("continent_name", "")}
        name = inst_data.get("ui_label", "")
        if not name:
            labels = inst_data.get("labels")
            if isinstance(labels, list) and labels:
                name = labels[0]
            elif isinstance(labels, str):
                name = labels
            else:
                name = inst_data.get("@id", "")
        url = inst_data.get("url", "")
        if isinstance(url, list) and url:
            url = url[0]
        return {"id": inst_data.get("@id", ""), "name": name, "acronym": inst_data.get("acronyms", ""), "url": url, "location": location}
    return None


def parse_component(comp_data):
    if is_none_value(comp_data):
        return None
    if isinstance(comp_data, str):
        return {"id": comp_data, "name": comp_data, "description": "", "domain": ""}
    if isinstance(comp_data, dict):
        return {"id": comp_data.get("@id", ""), "name": comp_data.get("name", "") or comp_data.get("@id", ""), "description": comp_data.get("description", ""), "domain": safe_get_label(comp_data.get("component"), ""), "family": safe_get_label(comp_data.get("family"), "")}
    return None


def parse_license(license_data):
    if is_none_value(license_data):
        return None
    if isinstance(license_data, str):
        return {"id": license_data, "name": license_data, "url": ""}
    if isinstance(license_data, dict):
        return {"id": license_data.get("@id", ""), "name": license_data.get("ui_label", "") or license_data.get("@id", ""), "url": license_data.get("url", "")}
    return None


def parse_scientific_domain(domain_data):
    if is_none_value(domain_data):
        return None
    if isinstance(domain_data, str):
        return {"id": domain_data, "name": domain_data, "description": ""}
    if isinstance(domain_data, dict):
        return {"id": domain_data.get("@id", ""), "name": domain_data.get("ui_label", "") or domain_data.get("@id", ""), "description": domain_data.get("description", "")}
    return None


def parse_scientific_domains(domains_data):
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
    return []


def prepare_template_context(data):
    model_id = data.get("@id", "unknown")
    name = data.get("name") or data.get("ui_label") or model_id.upper()
    description = data.get("description") or "No description available."
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]
    
    institution = parse_institution(data.get("institution"))
    license_info = parse_license(data.get("license"))
    
    components_raw = data.get("model_components", [])
    if not isinstance(components_raw, list):
        components_raw = [components_raw] if components_raw else []
    components = [parse_component(c) for c in components_raw if parse_component(c)]
    
    components_by_domain = {}
    for comp in components:
        domain = comp.get("domain", "Other") or "Other"
        if domain not in components_by_domain:
            components_by_domain[domain] = []
        components_by_domain[domain].append(comp)
    
    dynamic_components = parse_scientific_domains(data.get("dynamic_components"))
    omitted_components = parse_scientific_domains(data.get("omitted_components"))
    prescribed_components = parse_scientific_domains(data.get("prescribed_components"))
    
    calendar = None
    cal_data = data.get("calendar")
    if cal_data:
        calendar = {"id": safe_get_label(cal_data, ""), "name": safe_get_label(cal_data, ""), "description": cal_data.get("description", "") if isinstance(cal_data, dict) else ""}
    
    family = safe_get_label(data.get("family"), "")
    
    activity_raw = data.get("activity_participation", [])
    activity = []
    if isinstance(activity_raw, str):
        activity = [activity_raw]
    elif isinstance(activity_raw, dict):
        activity = [safe_get_label(activity_raw)]
    elif isinstance(activity_raw, list):
        for item in activity_raw:
            label = safe_get_label(item)
            if label:
                activity.append(label)
    
    references = parse_references(data.get("references"))
    release_year = data.get("release_year", "")
    
    extra_keywords = [name]
    if institution:
        extra_keywords.append(institution.get("name", ""))
    description_highlighted = highlight_keywords(description, extra_keywords + HIGHLIGHT_KEYWORDS)
    
    return {
        "id": model_id, "name": name, "family": family,
        "description": escape_html(description), "description_highlighted": description_highlighted,
        "validation_key": data.get("validation_key", ""), "context_url": data.get("@context", ""),
        "types": types, "institution": institution, "license": license_info,
        "components": components, "components_by_domain": components_by_domain,
        "component_count": len(components), "domain_count": len(components_by_domain),
        "dynamic_components": dynamic_components, "omitted_components": omitted_components,
        "prescribed_components": prescribed_components, "calendar": calendar,
        "activity": activity, "release_year": str(release_year) if release_year else "",
        "references": references, "icons": ICONS, "raw_json": json.dumps(data),
    }


def setup_jinja_env():
    return Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)


def process_model(env, template, filename):
    url = f"{BASE_URL}/{filename}"
    output_path = OUTPUT_DIR / filename.replace(".json", ".html")
    print(f"  Processing: {filename}")
    try:
        data = cmipld.get(url)
        if not data:
            print(f"    Warning: No data")
            return False
        context = prepare_template_context(data)
        html = template.render(**context)
        output_path.write_text(html, encoding="utf-8")
        print(f"    Generated: {output_path.name}")
        return True
    except Exception as e:
        print(f"    Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("Model Page Generator")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    env = setup_jinja_env()
    try:
        template = env.get_template("model.html.j2")
    except Exception as e:
        print(f"Template error: {e}")
        return 1
    success = sum(1 for f in MODELS if process_model(env, template, f))
    print(f"Done: {success}/{len(MODELS)}")
    cmipld.client.close()
    return 0 if success == len(MODELS) else 1


# if __name__ == "__main__":
#     sys.exit(main())
 
main()