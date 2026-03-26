"""
Handler for Model (source_id) registration (Stage 4)

Produces one file:
  model/{source_id}.json  — the complete CMIP source_id record

The source_id references component_config IDs from Stage 3 under
'dynamic_components' and 'prescribed_components'.
"""

import os
import re
from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')

# Parsed label keys → canonical field names where they differ
FIELD_MAP = {
    'model_name':    'name',
    'model_family':  'family',
    'release_year':  'release_year',
    'reference_dois': 'references',
    'calendar_s_':   'calendar',   # "Calendar(s)" → calendar(s) → calendar_s_ after parse
    'calendar(s)':   'calendar',   # fallback if parens preserved
}

# Multi-select fields that arrive as comma-separated strings → lists
LIST_FIELDS = {
    'dynamic_components', 'prescribed_components', 'omitted_components',
    'calendar', 'calendar_s_', 'calendar(s)',
    'component_config_ids', 'component_configs',
    'embedded_components',
    'coupling_group_1', 'coupling_group_2', 'coupling_group_3',
    'coupling_group_4', 'coupling_group_5',
}

IGNORE = {
    'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators',
    'model_name', 'model_family',
}

def _slugify(s: str) -> str:
    return s.strip().lower().replace(' ', '-').replace('_', '-')


def _parse_list(value) -> list:
    if isinstance(value, list):
        return [v.strip() for v in value if v.strip()]
    delim = '\n' if '\n' in str(value) else ','
    return [v.strip() for v in str(value).split(delim) if v.strip()]


def run(parsed_issue, issue, dry_run=False):
    # "Model Name" → parsed key 'model_name'; field_id is 'name'
    source_id = (parsed_issue.get('model_name') or parsed_issue.get('name') or '').strip()
    if not source_id:
        return None  # fall back to generic handler

    family = (parsed_issue.get('model_family') or parsed_issue.get('family') or '').strip()

    data = {
        "@context":       "_context",
        "@id":            source_id,
        "@type":          ["wcrp:model", "esgvoc:model"],
        "validation_key": source_id,
        "name":           source_id,
    }

    if family and family.lower() not in ('not specified', 'none', ''):
        data['family'] = family

    # Consolidate coupling groups into a single list-of-lists
    coupling_groups = []
    for i in range(1, 6):
        raw = parsed_issue.get(f'coupling_group_{i}', '')
        if raw:
            group = _parse_list(raw)
            if group:
                coupling_groups.append(group)

    # Map and copy remaining fields
    for k, v in parsed_issue.items():
        if not v or k in IGNORE:
            continue
        canonical = FIELD_MAP.get(k, k)
        if canonical.startswith('coupling_group_'):
            continue  # handled above
        if canonical in LIST_FIELDS or k in LIST_FIELDS:
            data[canonical] = _parse_list(v)
        else:
            data[canonical] = v.strip() if isinstance(v, str) else v

    # Rename component_config_ids → component_configs if needed
    if 'component_config_ids' in data:
        data['component_configs'] = data.pop('component_config_ids')

    if coupling_groups:
        data['coupling_groups'] = coupling_groups

    # Normalise release_year to int
    if 'release_year' in data:
        try:
            data['release_year'] = int(data['release_year'])
        except (ValueError, TypeError):
            pass

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []
    file_path    = os.path.join('model', f"{source_id}.json")

    return {
        file_path:       data,
        '_author':       issue.get('author'),
        '_contributors': contributors,
        '_make_pull':    True,
        '_source_id':    source_id,
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    source_id   = files_to_write.get('_source_id', '')
    model_path  = next((p for p in files_to_write if not p.startswith('_')), None)
    model_data  = files_to_write.get(model_path, {}) if model_path else {}

    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        print(f"  Generating review report for {file_path} …", flush=True)
        try:
            data['_validation_report'] = ReportBuilder(
                folder_url=f"emd:{kind}", kind=kind,
                item=data, link_threshold=80.0,
            ).build()
        except Exception as e:
            print(f"  ⚠ Report generation failed: {e}", flush=True)
            data['_validation_report'] = ''

    # Print the completed source_id record and explain its role
    if model_data and source_id:
        import json
        clean = {k: v for k, v in model_data.items() if not k.startswith('_')}
        configs = clean.get('component_configs', [])

        print("\n" + "=" * 60, flush=True)
        print(f"Model (source_id) record created: {source_id}", flush=True)
        print("=" * 60, flush=True)
        print(json.dumps(clean, indent=4), flush=True)
        print("=" * 60, flush=True)
        print(
            f"\n✅ source_id: '{source_id}'\n"
            f"   This is your CMIP source_id — the complete model identifier\n"
            f"   used in all CMIP data and metadata submissions.\n",
            flush=True,
        )
        if configs:
            print(
                f"   Component configs linked ({len(configs)}):",
                flush=True,
            )
            for c in configs:
                print(f"     • {c}", flush=True)
            print(
                f"\n   Each config ID encodes the component, its name, and its grids\n"
                f"   (format: <domain>_<component>_<h###>_<v###>).\n"
                f"   These were registered in Stage 3 and are now bound to this model.",
                flush=True,
            )
        else:
            print(
                "   ⚠ No component_configs linked — add Stage 3 config IDs\n"
                "     under 'component_configs' to complete the registration.",
                flush=True,
            )
