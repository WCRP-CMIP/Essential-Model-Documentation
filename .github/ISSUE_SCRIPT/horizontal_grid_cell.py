"""
Handler for Horizontal Grid Cell registration (Stage 1)

Produces one file per submission:
  horizontal_grid_cell/g{NNN}.json

The @id is the next available g### based on existing files in the repo.
"""

import os
import json

from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')

IGNORE = {'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators'}


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
    repo_root  = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
    gid        = _next_gid(repo_root)
    file_path  = os.path.join('horizontal_grid_cell', f"{gid}.json")

    # Build data from parsed issue fields
    data = {
        "@context":       "_context",
        "@id":            gid,
        "@type":          ["wcrp:horizontal_grid_cell", "esgvoc:horizontal_grid_cell"],
        "validation_key": gid,
    }

    # Copy all non-ignored, non-empty fields from parsed issue
    skip = IGNORE | {'issue_kind', 'issue_type'}
    for key, val in parsed_issue.items():
        if key in skip or not val:
            continue
        if isinstance(val, str) and val.lower() in ('_no response_', 'none', 'not specified', ''):
            continue
        data[key] = val

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    print(f"  [+ new] Grid cell '{gid}'", flush=True)

    return {
        file_path:       data,
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
        file_path   = os.path.join('horizontal_grid_cell', f"{atid}.json")
        data_obj    = files_to_write.get(file_path, {})
        clean       = {k: v for k, v in data_obj.items() if not k.startswith('_')}
        print(f"\n  ✅ Grid Cell ID: '{atid}'", flush=True)
        print(f"  Use this ID (g###) in Stage 2a (Horizontal Computational Grid)", flush=True)
        print(_json.dumps(clean, indent=4), flush=True)
