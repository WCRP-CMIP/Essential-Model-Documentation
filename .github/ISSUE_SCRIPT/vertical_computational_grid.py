"""
Handler for Vertical Computational Grid registration (Stage 2b)

Produces one file per submission:
  vertical_computational_grid/v{NNN}.json

The @id is the next available v### based on existing files in the repo.
"""

import os
import json

from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')

IGNORE = {'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators'}

FIELD_MAP = {
    'number_of_levels':         'n_z',
    'number_of_levels_(range)': 'n_z_range',
    'top_layer_thickness_(m)':  'top_layer_thickness',
    'bottom_layer_thickness_(m)': 'bottom_layer_thickness',
    'total_depth_(m)':          'total_thickness',
    'total_height_(m)':         'total_thickness',
}


def _next_vid(repo_root: str) -> str:
    """Return the next available v### ID by scanning existing files."""
    vert_dir = os.path.join(repo_root, 'vertical_computational_grid')
    existing = []
    if os.path.isdir(vert_dir):
        for f in os.listdir(vert_dir):
            if f.startswith('v') and f[1:-5].isdigit() and f.endswith('.json'):
                existing.append(int(f[1:-5]))
    return f"v{max(existing, default=99) + 1}"


def _parse_list(value) -> list:
    """Handle both string and list inputs."""
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    delim = '\n' if '\n' in str(value) else ','
    return [v.strip() for v in str(value).split(delim) if v.strip()]


def run(parsed_issue, issue, dry_run=False):
    repo_root  = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
    vid        = _next_vid(repo_root)
    file_path  = os.path.join('vertical_computational_grid', f"{vid}.json")

    data = {
        "@context":       "_context",
        "@id":            vid,
        "@type":          ["wcrp:vertical_computational_grid",
                           "esgvoc:vertical_computational_grid"],
        "validation_key": vid,
    }

    skip = IGNORE | {'issue_kind', 'issue_type'}
    for raw_key, val in parsed_issue.items():
        if raw_key in skip or not val:
            continue
        if isinstance(val, str) and val.lower() in ('_no response_', 'none', 'not specified', ''):
            continue
        key = FIELD_MAP.get(raw_key, raw_key)
        # Numeric fields
        if key in ('n_z', 'top_layer_thickness', 'bottom_layer_thickness',
                   'total_thickness', 'truncation_number'):
            try:
                data[key] = float(val) if '.' in str(val) else int(val)
            except (ValueError, TypeError):
                data[key] = val
        # Range field → list of ints
        elif key == 'n_z_range':
            data[key] = _parse_list(val)
        else:
            data[key] = val

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    print(f"  [+ new] Vertical grid '{vid}'", flush=True)

    return {
        file_path:       data,
        '_author':       issue.get('author'),
        '_contributors': contributors,
        '_make_pull':    True,
        '_atid':         vid,
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
        file_path = os.path.join('vertical_computational_grid', f"{atid}.json")
        data_obj  = files_to_write.get(file_path, {})
        clean     = {k: v for k, v in data_obj.items() if not k.startswith('_')}
        print(f"\n  ✅ Vertical Grid ID: '{atid}'", flush=True)
        print(f"  Use this ID (v###) in Stage 3 (Model Component) as the vertical grid", flush=True)
        print(_json.dumps(clean, indent=4), flush=True)
