"""
Handler for Horizontal Grid Cell registration (Stage 1)

Produces one file per submission:
  horizontal_grid_cell/tempgrid_{author}-{timestamp}.json

The tempgrid-rename.yml workflow renames this to g### on merge to src-data,
scanning existing g### files and assigning max+1.
"""

import os
import time

from cmipld.utils.id_generation import generate_id_from_issue
from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')

IGNORE = {'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators',
          'additional_information'}

FIELD_MAP = {
    'number_of_cells': 'n_cells',
}


def run(parsed_issue, issue, dry_run=False):
    if parsed_issue.get('validation_key'):
        return None  # fall back to generic handler

    author     = issue.get('author') or 'unknown'
    created_at = issue.get('created_at') or ''
    temp_id    = f"tempgrid_{generate_id_from_issue(author, created_at)['id']}" \
                 if created_at else f"tempgrid_{author}_{int(time.time())}"
    file_path  = os.path.join('horizontal_grid_cell', f"{temp_id}.json")

    region = (parsed_issue.get('region') or '').strip()
    units  = parsed_issue.get('units', parsed_issue.get('horizontal_units', ''))

    grid_type = parsed_issue.get('grid_type', '')
    x_res     = parsed_issue.get('x_resolution', '')
    y_res     = parsed_issue.get('y_resolution', '')
    ui_label  = (
        f"Horizontal grid cell with a {grid_type.replace('_', ' ')} grid type"
        + (f" and {x_res} x {y_res} {units} resolution" if x_res and y_res else "")
        + "."
    )

    description = (parsed_issue.get('description') or '').strip()
    if not description or description.lower() in ('_no response_', 'none', 'not specified'):
        description = ''

    data = {
        "@context":       "_context",
        "@id":            temp_id,
        "@type":          ["wcrp:horizontal_grid_cell", "esgvoc:horizontal_grid_cell"],
        "validation_key": ui_label,
        "ui_label":       ui_label,
    }
    if description:
        data['description'] = description
    if units:
        data['horizontal_units'] = units

    skip = IGNORE | {'issue_kind', 'issue_type', 'region', 'units', 'horizontal_units', 'description'}
    for key, val in parsed_issue.items():
        if key in skip or not val or key in data:
            continue
        if isinstance(val, str) and val.lower() in ('_no response_', 'none', 'not specified', ''):
            continue
        key = FIELD_MAP.get(key, key)
        data[key] = val.strip() if isinstance(val, str) else val
    if region and region.lower() not in ('_no response_', 'none', 'not specified'):
        data['region'] = region

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    print(f"  [+ new] Grid cell '{temp_id}'", flush=True)

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
        file_path = os.path.join('horizontal_grid_cell', f"{atid}.json")
        clean     = {k: v for k, v in files_to_write.get(file_path, {}).items()
                     if not k.startswith('_')}
        print("\n" + "=" * 60, flush=True)
        print(f"Stage 1 - Grid cell '{atid}' created:", flush=True)
        print(_json.dumps(clean, indent=4), flush=True)
        print("=" * 60, flush=True)
        print(
            f"\n  Temporary ID: '{atid}'\n"
            f"     Will be renamed to g### on PR merge.\n"
            f"     Use the final g### in Stage 2a (Horizontal Computational Grid).",
            flush=True,
        )
