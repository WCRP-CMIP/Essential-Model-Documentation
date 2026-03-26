"""
Handler for Horizontal Grid Cell registration (Stage 1)

Produces one file:
  horizontal_grid_cell/{atid}.json  — the grid cell (g### equivalent)

The resulting g### ID is then referenced in Stage 2a (Horizontal Computational Grid)
to build horizontal_subgrid and horizontal_computational_grid records.
"""

import os
import time

from cmipld.utils.id_generation import generate_id_from_issue
from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')

IGNORE = {'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators',
          'units', 'additional_information'}


def run(parsed_issue, issue, dry_run=False):
    if parsed_issue.get('validation_key'):
        return None  # fall back to generic handler

    author     = issue.get('author') or 'unknown'
    created_at = issue.get('created_at') or ''
    atid       = f"tempgrid_{generate_id_from_issue(author, created_at)['id']}" \
                 if created_at else f"tempgrid_{author}_{int(time.time())}"

    region = parsed_issue.get('region', '')
    region_list = [r.strip() for r in region.split(',') if r.strip()] if region else []

    grid_type = parsed_issue.get('grid_type', '')
    x_res     = parsed_issue.get('x_resolution', '')
    y_res     = parsed_issue.get('y_resolution', '')
    units     = parsed_issue.get('units', '')

    description = (
        parsed_issue.get('additional_information') or
        f"Horizontal grid cell with a {grid_type.replace('_', ' ')} grid type"
        + (f" and {x_res} x {y_res} {units} resolution" if x_res and y_res else "")
        + "."
    )

    cell_data = {
        "@context":         "_context",
        "@id":              atid,
        "@type":            ["wcrp:horizontal_grid_cell", "esgvoc:horizontal_grid_cell"],
        "validation_key":   atid,
        "description":      description,
        "horizontal_units": units or None,
    }
    for k, v in parsed_issue.items():
        if k in IGNORE or not v or k in cell_data:
            continue
        cell_data[k] = v.strip() if isinstance(v, str) else v
    if region_list:
        cell_data['region'] = region_list

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    return {
        os.path.join('horizontal_grid_cell', f"{atid}.json"): cell_data,
        '_author':       issue.get('author'),
        '_contributors': contributors,
        '_make_pull':    True,
        '_atid':         atid,
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    atid = files_to_write.get('_atid', '')

    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        print(f"  Generating review report for {file_path} …", flush=True)
        try:
            data['_validation_report'] = ReportBuilder(
                folder_url=f"emd:{kind}s", kind=kind,
                item=data, link_threshold=80.0,
            ).build()
        except Exception as e:
            print(f"  ⚠ Report generation failed: {e}", flush=True)
            data['_validation_report'] = ''

        if 'horizontal_units' in data:
            data['units'] = data.pop('horizontal_units')

    if atid:
        print("\n" + "=" * 60, flush=True)
        print(f"Stage 1 grid cell created: {atid}", flush=True)
        print("=" * 60, flush=True)
        print(
            f"\n  Use this ID in Stage 2a (Horizontal Computational Grid)\n"
            f"  to build horizontal_subgrid and horizontal_computational_grid\n"
            f"  records by selecting it in the 'Grid Cells' slot fields.",
            flush=True,
        )
