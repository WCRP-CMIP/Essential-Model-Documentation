"""
Handler for Vertical Computational Grid registration (Stage 2b)

Produces one file per submission:
  vertical_computational_grid/tempgrid_{author}-{timestamp}.json

The tempgrid-rename.yml workflow renames this to v### on merge to src-data,
scanning existing v### files and assigning max+1.
"""

import os
import time

from cmipld.utils.id_generation import generate_id_from_issue
from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')

FIELD_MAP = {
    'top_layer_thickness_(m)':    'top_layer_thickness',
    'bottom_layer_thickness_(m)': 'bottom_layer_thickness',
    'total_thickness_(m)':        'total_thickness',
    'number_of_levels':           'n_z',
    'number_of_levels_(range)':   'n_z_range',
}
IGNORE = {'issue_kind', 'additional_collaborators', 'collaborators', 'issue_category',
          'additional_information', 'description'}


def _parse_list(value) -> list:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    delim = '\n' if '\n' in str(value) else ','
    return [v.strip() for v in str(value).split(delim) if v.strip()]


def run(parsed_issue, issue, dry_run=False):
    if parsed_issue.get('validation_key'):
        return None

    author     = issue.get('author') or 'unknown'
    created_at = issue.get('created_at') or ''
    temp_id    = f"tempgrid_{generate_id_from_issue(author, created_at)['id']}" \
                 if created_at else f"tempgrid_{author}_{int(time.time())}"
    file_path  = os.path.join(kind, f"{temp_id}.json")

    data = {
        "@context":       "_context",
        "@id":            temp_id,
        "@type":          ["wcrp:vertical_computational_grid",
                           "esgvoc:vertical_computational_grid"],
        "validation_key": temp_id,
    }

    # Only set description if user explicitly entered something
    description = (parsed_issue.get('description') or
                   parsed_issue.get('additional_information') or '').strip()
    if description and description.lower() not in ('_no response_', 'none', 'not specified'):
        data['description'] = description

    skip = IGNORE | {'issue_kind', 'issue_type'}
    for raw_key, val in parsed_issue.items():
        if raw_key in skip or not val:
            continue
        if isinstance(val, str) and val.lower() in ('_no response_', 'none', 'not specified', ''):
            continue
        key = FIELD_MAP.get(raw_key, raw_key)
        if key in ('n_z', 'top_layer_thickness', 'bottom_layer_thickness',
                   'total_thickness', 'truncation_number'):
            try:
                data[key] = float(val) if '.' in str(val) else int(val)
            except (ValueError, TypeError):
                data[key] = val
        elif key == 'n_z_range':
            data[key] = _parse_list(val)
        else:
            data[key] = val

    for old_key in FIELD_MAP:
        data.pop(old_key, None)

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    print(f"  [+ new] Vertical grid '{temp_id}'", flush=True)

    return {
        file_path:       data,
        '_author':       issue.get('author'),
        '_contributors': contributors,
        '_make_pull':    True,
        '_atid':         temp_id,
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    atid = files_to_write.get('_atid', '')

    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        print(f"  Generating review report for {file_path} ...", flush=True)
        try:
            data['_validation_report'] = ReportBuilder(
                folder_url=f"emd:{kind}", kind=kind,
                item=data, link_threshold=80.0,
            ).build()
        except Exception as e:
            print(f"  WARNING Report generation failed: {e}", flush=True)
            data['_validation_report'] = ''

    if atid:
        import json as _json
        file_path = os.path.join(kind, f"{atid}.json")
        clean     = {k: v for k, v in files_to_write.get(file_path, {}).items()
                     if not k.startswith('_')}
        print("\n" + "=" * 60, flush=True)
        print(f"Stage 2b - Vertical grid '{atid}' created:", flush=True)
        print(_json.dumps(clean, indent=4), flush=True)
        print("=" * 60, flush=True)
        print(
            f"\n  Temporary ID: '{atid}'\n"
            f"     Will be renamed to v### on PR merge.\n"
            f"     Use the final v### in Stage 3 (Model Component).",
            flush=True,
        )
