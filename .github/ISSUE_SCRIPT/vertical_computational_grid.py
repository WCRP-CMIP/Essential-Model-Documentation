"""
Handler for Vertical Computational Grid registration (Stage 2b)
"""

import os
import time

from cmipld.utils.id_generation import generate_id_from_issue
from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')

# Keys in the parsed issue that need renaming to canonical field names
FIELD_MAP = {
    'top_layer_thickness_(m)':    'top_layer_thickness',
    'bottom_layer_thickness_(m)': 'bottom_layer_thickness',
    'total_thickness_(m)':        'total_thickness',
    'additional_information':     'description',
    'number_of_levels':           'n_z',
    'number_of_levels_(range)':   'n_z_range',
}
IGNORE = {'issue_kind', 'additional_collaborators', 'collaborators', 'issue_category'}


def run(parsed_issue, issue, dry_run=False):
    if parsed_issue.get('validation_key'):
        return None

    author     = issue.get('author') or 'unknown'
    created_at = issue.get('created_at') or ''
    atid       = generate_id_from_issue(author, created_at)['id'] if created_at \
                 else f"{author}_{int(time.time())}"

    remapped = {
        FIELD_MAP.get(k, k): v
        for k, v in parsed_issue.items()
        if FIELD_MAP.get(k, k) not in IGNORE and v
    }

    data = {
        "@context":       "_context",
        "@id":            atid,
        "@type":          ["wcrp:vertical_computational_grid", "esgvoc:vertical_computational_grid"],
        "validation_key": atid,
        **remapped,
    }

    # Remove any old field names that were renamed via FIELD_MAP
    for old_key in FIELD_MAP:
        data.pop(old_key, None)

    collab_str   = parsed_issue.get('additional_collaborators', parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] if collab_str else []
    file_path    = os.path.join(kind, f"{atid}.json")

    return {file_path: data, '_author': issue.get('author'),
            '_contributors': contributors, '_make_pull': True}


def update(files_to_write, parsed_issue, issue, dry_run=False):
    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        try:
            data['_validation_report'] = ReportBuilder(
                folder_url=f"emd:{kind}s", kind=kind, item=data, link_threshold=80.0
            ).build()
        except Exception as e:
            print(f"  ⚠ Report generation failed: {e}", flush=True)
            data['_validation_report'] = ''
