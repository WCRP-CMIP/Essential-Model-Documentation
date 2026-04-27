"""
Handler for Horizontal Grid Cell registration (Stage 1)

Produces one file per submission:
  horizontal_grid_cell/tempgrid_{author}-{timestamp}.json

The tempgrid-rename.yml workflow renames this to g### on merge to src-data,
scanning existing g### files and assigning max+1.
"""

import os
import re
import time

from cmipld.utils.id_generation import generate_id_from_issue
from cmipld.utils.similarity import ReportBuilder
from cmipld.utils.ldparse import ui_label_to_key

kind = __file__.split('/')[-1].replace('.py', '')

IGNORE = {'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators',
          'additional_information'}

FIELD_MAP = {
    'number_of_cells':        'n_cells',
    'coordinate_system':      'grid_mapping',   # label "Coordinate System" != id grid_mapping
    'additional_information': 'description',    # header renamed in template
}

_NUMERIC_KEYS = re.compile(r'_(resolution|number|longitude|latitude|cells|truncation)')

# CV fields that may be submitted as ui_label — map field name to graph URL
CV_FIELDS = {
    'grid_type':          'constants:grid_type/_graph.json',
    'grid_mapping':       'constants:grid_mapping/_graph.json',
    'region':             'constants:region/_graph.json',
    'temporal_refinement':'constants:temporal_refinement/_graph.json',
    'units':              'constants:units/_graph.json',
    'truncation_method':  'constants:truncation_method/_graph.json',
}

# Cache reverse maps so we only fetch each graph once per run
_CV_REVERSE_MAP: dict[str, dict] = {}

def resolve_cv_value(field: str, value: str) -> str:
    """
    Resolve a CV field value to its validation_key.
    Accepts both ui_label and validation_key as input.
    If unrecognised, returns the value as-is with a warning.
    """
    if not value or field not in CV_FIELDS:
        return value
    if field not in _CV_REVERSE_MAP:
        try:
            _CV_REVERSE_MAP[field] = ui_label_to_key(CV_FIELDS[field])
        except Exception:
            _CV_REVERSE_MAP[field] = {}
    resolved = _CV_REVERSE_MAP[field].get(value)
    if resolved is None:
        print(f"  WARNING: unrecognised {field} value {value!r} — storing as-is", flush=True)
        return value
    return resolved

def to_num(key, val):
    """Coerce val to int or float if the key matches a numeric field pattern."""
    if not _NUMERIC_KEYS.search(key):
        return val
    try:
        f = float(val)
        return int(f) if f == int(f) else f
    except (ValueError, TypeError):
        return val


def run(parsed_issue, issue, dry_run=False):
    if parsed_issue.get('validation_key'):
        return None  # fall back to generic handler

    author     = issue.get('author') or 'unknown'
    created_at = issue.get('created_at') or ''
    temp_id    = f"tempgrid_{generate_id_from_issue(author, created_at)['id']}" \
                 if created_at else f"tempgrid_{author}_{int(time.time())}"
    file_path  = os.path.join('horizontal_grid_cell', f"{temp_id}.json")

    region = (parsed_issue.get('region') or '').strip()
    region = resolve_cv_value('region', region)
    units  = (parsed_issue.get('units') or parsed_issue.get('horizontal_units') or '').strip()
    units  = resolve_cv_value('units', units)

    grid_type = resolve_cv_value('grid_type', parsed_issue.get('grid_type', ''))
    x_res     = parsed_issue.get('x_resolution', '')
    y_res     = parsed_issue.get('y_resolution', '')
    ui_label  = (
        f"Horizontal grid cell with a {grid_type.replace('-', ' ')} grid type"
        + (f" and {x_res} x {y_res} {units} resolution" if x_res and y_res else "")
        + "."
    )

    description = (parsed_issue.get('description') or parsed_issue.get('additional_information') or '').strip()
    if not description or description.lower() in ('_no response_', 'none', 'not specified'):
        description = ''

    data = {
        "@context":       "_context",
        "@id":            temp_id,
        "@type":          ["emd", "wcrp:horizontal_grid_cell", "esgvoc:HorizontalGridCell"],
        "validation_key": temp_id,   # must match @id so rename workflow can update it
        "ui_label":       ui_label,
        "description":    description,
    }
    if units:
        data['units'] = units

    skip = IGNORE | {'issue_kind', 'issue_type', 'region', 'units', 'horizontal_units', 'description', 'additional_information'}
    for key, val in parsed_issue.items():
        if key in skip or not val or key in data:
            continue
        if isinstance(val, str) and val.lower() in ('_no response_', 'none', 'not specified', ''):
            continue
        key = FIELD_MAP.get(key, key)
        val = val.strip().lower() if isinstance(val, str) else val
        val = resolve_cv_value(key, val) if isinstance(val, str) else val
        data[key] = to_num(key, val)
    if region and region.lower() not in ('_no response_', 'none', 'not specified'):
        data['region'] = [region]

    # Ensure all spec keys are always present (as "" if not set)
    ALL_KEYS = [
        'validation_key', 'ui_label', 'description', 'grid_mapping', 'grid_type',
        'n_cells', 'region', 'southernmost_latitude', 'temporal_refinement',
        'truncation_method', 'truncation_number', 'units', 'westernmost_longitude',
        'x_resolution', 'y_resolution',
    ]
    for k in ALL_KEYS:
        if k not in data:
            data[k] = ""

    # parse the grid usage fields.
    data['alias'] = data['alias'].split(',') if data.get('alias') else []

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    # Build pydantic-compatible copy for validation (used by new_issue.py STEP 1
    # before update() is called — does not affect what gets written to file)
    pydantic_data = {k: v for k, v in data.items() if not k.startswith('_')}
    region_val = pydantic_data.get('region', '')
    if isinstance(region_val, list):
        pydantic_data['region'] = region_val[0] if region_val else None
    elif not region_val:
        pydantic_data['region'] = None
    if 'units' in pydantic_data and 'horizontal_units' not in pydantic_data:
        pydantic_data['horizontal_units'] = pydantic_data.pop('units')

    

    print(f"  [+ new] Grid cell '{temp_id}'", flush=True)

    return {
        file_path:        data,
        '_pydantic_data': {file_path: pydantic_data},
        '_author':        issue.get('author'),
        '_contributors':  contributors,
        '_make_pull':     True,
        '_atid':          temp_id,
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    atid = files_to_write.get('_atid', '')

    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        print(f"  Generating review report for {file_path} ...", flush=True)
        try:
            # Use pydantic-compatible copy if available, else fall back to data
            pydantic_overrides = files_to_write.get('_pydantic_data', {})
            validation_item = pydantic_overrides.get(file_path, data)
            report = ReportBuilder(
                folder_url=f"emd:{kind}", kind=kind,
                item=validation_item, link_threshold=85.0,
            ).build()
            data['_validation_report'] = report
            print(f"  Report generated ({len(report)} chars)", flush=True)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print(f"  WARNING Report generation failed: {e}\n{tb}", flush=True)
            data['_validation_report'] = (
                f"## Review Report\n\n"
                f"> [!WARNING]\n"
                f"> Report generation failed: `{e}`\n"
            )

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
