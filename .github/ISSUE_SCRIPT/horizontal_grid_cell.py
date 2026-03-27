"""
Handler for Horizontal Grid Cell registration (Stage 1)

Produces one file:
  horizontal_grid_cell/g{NNN}.json

The @id is the next available g### based on existing files in the repo.
The permanent g### ID is assigned here; no tempgrid renaming needed.
"""

import os

from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')

IGNORE = {'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators',
          'additional_information'}


def _next_gid(repo_root: str) -> str:
    """Return the next available g### ID by scanning existing files."""
    grid_dir = os.path.join(repo_root, 'horizontal_grid_cell')
    existing = []
    if os.path.isdir(grid_dir):
        for f in os.listdir(grid_dir):
            if f.startswith('g') and f[1:-5].isdigit() and f.endswith('.json'):
                existing.append(int(f[1:-5]))
    return f"g{max(existing, default=99) + 1}"


def run(parsed_issue, issue, dry_run=False):
    if parsed_issue.get('validation_key'):
        return None  # fall back to generic handler

    repo_root = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
    gid       = _next_gid(repo_root)

    region = parsed_issue.get('region', '')
    region_list = [r.strip() for r in region.split(',') if r.strip()] if region else []

    grid_type = parsed_issue.get('grid_type', '')
    x_res     = parsed_issue.get('x_resolution', '')
    y_res     = parsed_issue.get('y_resolution', '')
    units     = parsed_issue.get('units', parsed_issue.get('horizontal_units', ''))

    description = (
        parsed_issue.get('additional_information') or
        f"Horizontal grid cell with a {grid_type.replace('_', ' ')} grid type"
        + (f" and {x_res} x {y_res} {units} resolution" if x_res and y_res else "")
        + "."
    )

    cell_data = {
        "@context":       "_context",
        "@id":            gid,
        "@type":          ["wcrp:horizontal_grid_cell", "esgvoc:horizontal_grid_cell"],
        "validation_key": gid,
        "description":    description,
    }
    if units:
        cell_data['horizontal_units'] = units

    for k, v in parsed_issue.items():
        if k in IGNORE or not v or k in cell_data:
            continue
        if isinstance(v, str) and v.lower() in ('_no response_', 'none', 'not specified', ''):
            continue
        cell_data[k] = v.strip() if isinstance(v, str) else v
    if region_list:
        cell_data['region'] = region_list

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    print(f"  [+ new] Grid cell '{gid}'", flush=True)

    return {
        os.path.join('horizontal_grid_cell', f"{gid}.json"): cell_data,
        '_author':       issue.get('author'),
        '_contributors': contributors,
        '_make_pull':    True,
        '_atid':         gid,
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    atid = files_to_write.get('_atid', '')

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

    if atid:
        import json as _json
        file_path = os.path.join('horizontal_grid_cell', f"{atid}.json")
        clean     = {k: v for k, v in files_to_write.get(file_path, {}).items()
                     if not k.startswith('_')}
        print("\n" + "=" * 60, flush=True)
        print(f"Stage 1 — Grid cell '{atid}' created:", flush=True)
        print(_json.dumps(clean, indent=4), flush=True)
        print("=" * 60, flush=True)
        print(
            f"\n  ✅ Grid Cell ID: '{atid}'\n"
            f"     Use this g### in Stage 2a (Horizontal Computational Grid)",
            flush=True,
        )
