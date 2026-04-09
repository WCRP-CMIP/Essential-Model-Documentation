"""
Handler for Model Component registration (Stage 3)

Produces two files per submission:
  1. model_component/{name_slug}.json  — the reusable component record
  2. component_config/{config_id}.json — component + grid binding for use in Stage 4

Config ID format: {component_type}_{name_slug}_{h###}_{v###}
e.g.  ocean_nemo-v3-6_h101_v103
"""

import os
import re
from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')

IGNORE = {'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators',
          'component_type', 'component_name', 'component_family',
          'horizontal_grid', 'vertical_grid', 'name'}


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'[^a-z0-9\-\.]', '', s)
    return s.strip('-')


def _parse_list(value: str) -> list:
    delim = '\n' if '\n' in value else ','
    return [v.strip() for v in value.split(delim) if v.strip()]


def run(parsed_issue, issue, dry_run=False):
    component_type = (parsed_issue.get('component_type') or '').strip().lower()
    component_name = (parsed_issue.get('component_name') or '').strip()
    h_grid         = (parsed_issue.get('horizontal_grid') or '').strip().lower()
    v_grid         = (parsed_issue.get('vertical_grid') or '').strip().lower()
    family         = (parsed_issue.get('component_family') or '').strip().lower()
    description    = (parsed_issue.get('description') or '').strip()

    if not component_name:
        return None  # fall back to generic handler

    name_slug = _slugify(component_name)
    config_id = f"{component_type}_{name_slug}_{h_grid}_{v_grid}"

    # ── 1. model_component record ─────────────────────────────────────────────
    component_data = {
        "@context":       "_context",
        "@id":            name_slug,
        "@type":          ["emd", "wcrp:model_component", "esgvoc:ModelComponent"],
        "validation_key": name_slug,
        "ui_label":       component_name,
        "component":      component_type,
    }
    if family and family.lower() not in ('not specified', 'none', ''):
        component_data["family"] = family

    for k, v in parsed_issue.items():
        if k in IGNORE or not v:
            continue
        if isinstance(v, str) and v.lower() in ('_no response_', 'none', 'not specified', ''):
            continue
        if k == 'reference_dois':
            component_data['references'] = _parse_list(v)
        elif k == 'code_repository':
            component_data['code_base'] = v.strip()
        else:
            component_data[k] = v.strip() if isinstance(v, str) else v

    # ── 2. component_config record ────────────────────────────────────────────
    config_data = {
        "@context":                      "_context",
        "@id":                           config_id,
        "@type":                         ["emd", "wcrp:component_config", "esgvoc:ComponentConfig"],
        "validation_key":                config_id,
        "ui_label":                      config_id,
        "model_component":               name_slug,
        "horizontal_computational_grid": h_grid,
        "vertical_computational_grid":   v_grid,
    }
    if description and description.lower() not in ('none', 'not specified'):
        config_data['description'] = description

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    component_path = os.path.join('model_component', f"{name_slug}.json")
    config_path    = os.path.join('component_config', f"{config_id}.json")

    return {
        component_path:  component_data,
        config_path:     config_data,
        '_author':       issue.get('author'),
        '_contributors': contributors,
        '_make_pull':    True,
        '_config_id':    config_id,
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    config_id   = files_to_write.get('_config_id', '')
    config_path = next((p for p in files_to_write if 'component_config' in p), None)
    config_data = files_to_write.get(config_path, {}) if config_path else {}

    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        # Strip name if JSONValidator re-injected it
        data.pop('name', None)
        print(f"  Generating review report for {file_path} …", flush=True)
        report_kind = 'component_config' if 'component_config' in file_path else 'model_component'
        try:
            data['_validation_report'] = ReportBuilder(
                folder_url=f"emd:{report_kind}", kind=report_kind,
                item=data, link_threshold=80.0,
            ).build()
        except Exception as e:
            print(f"  ⚠ Report generation failed: {e}", flush=True)
            data['_validation_report'] = ''

    if config_data and config_id:
        import json
        clean = {k: v for k, v in config_data.items() if not k.startswith('_')}
        print("\n" + "=" * 60, flush=True)
        print("Component Config file created:", flush=True)
        print("=" * 60, flush=True)
        print(json.dumps(clean, indent=4), flush=True)
        print("=" * 60, flush=True)
        print(
            f"\n✅ Config ID: '{config_id}'\n"
            f"   Use this ID in Stage 4 (Model) under 'component_configs'.\n"
            f"\n   Example:\n"
            f"     \"component_configs\": [\"{config_id}\", ...]",
            flush=True,
        )
