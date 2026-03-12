"""
Handler for Vertical Computational Grid registration (Stage 2b)
"""

import json
import os
import time

from cmipld.utils.id_generation import generate_id_from_issue
from cmipld.utils.esgvoc import pycmipld, DATA_DESCRIPTOR_CLASS_MAPPING
from cmipld.utils.similarity import ReportBuilder


kind = __file__.split('/')[-1].replace('.py', '')


def generate_markdown_report(data, graph_data=None):
    folder_url = f"emd:{kind}s"
    return ReportBuilder(
        folder_url     = folder_url,
        kind           = kind,
        item           = data,
        graph_data     = graph_data,
        link_threshold = 80.0,
    ).build()


def run(parsed_issue, issue, dry_run=False):
    if parsed_issue.get('validation_key'):
        return None

    author     = issue.get('author') or 'unknown'
    created_at = issue.get('created_at') or ''

    if created_at:
        id_result = generate_id_from_issue(author, created_at)
        atid = id_result['id']
    else:
        atid = f"{author}_{int(time.time())}"

    data = {
        "@context":       "_context",
        "@id":            atid,
        "@type":          ["wcrp:vertical_computational_grid", "esgvoc:vertical_computational_grid"],
        "validation_key": atid,
        **parsed_issue,
    }

    additional_collaborators = parsed_issue.get('additional_collaborators',
                                                parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in additional_collaborators.split(',') if c.strip()] \
        if additional_collaborators else []

    file_path = os.path.join('vertical_computational_grid', f"{atid}.json")
    
    
    print(json.dumps(data, indent=2))

    return {
        file_path:       data,
        '_author':       issue.get('author'),
        '_contributors': contributors,
        '_make_pull':    True,
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        data['_validation_report'] = generate_markdown_report(data)
