"""
Handler for Horizontal Grid Cell registration (Stage 1)
"""

import os
import time

from cmipld.utils.id_generation import generate_id_from_issue
from cmipld.utils.similarity import ReportBuilder


kind = __file__.split('/')[-1].replace('.py','')


def run(parsed_issue, issue, dry_run=False):
    if not parsed_issue.get('validation_key'):
        author     = issue.get('author') or 'unknown'
        created_at = issue.get('created_at') or ''
        if created_at:
            id_result = generate_id_from_issue(author, created_at)
            atid = f"tempgrid_{id_result['id']}"
        else:
            import time
            atid = f"tempgrid_{author}_{int(time.time())}"
        data = {
            "@context": "_context",
            "@id": atid,
            "@type": ["wcrp:horizontal_grid_cell", "esgvoc:horizontal_grid_cell"],
            "validation_key": atid,
            **parsed_issue
        }
        
    
        data['description'] = f"Horizontal grid cell with a {data['grid_type'].replace('_', ' ')} grid type and {data['x_resolution']} x {data['y_resolution']} {data['units']} grid."
        
        data['horizontal_units'] = data.pop('units', None)  # rename for validation
        # Return as dict with file path and metadata
        file_path = os.path.join('horizontal_grid_cell', f"{data['@id']}.json")
        
        # Parse contributors
        additional_collaborators = parsed_issue.get('additional_collaborators', 
                                                   parsed_issue.get('collaborators', ''))
        contributors = []
        if additional_collaborators:
            contributors = [c.strip() for c in additional_collaborators.split(',') if c.strip()]
        
        return {
            file_path: data,
            '_author': issue.get('author'),
            '_contributors': contributors,
            '_make_pull': True,  # Always make pull request for grid cells
        }
    
    # Otherwise let generic handler build from validation_key
    return None


def update(files_to_write, parsed_issue, issue, dry_run=False):
    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        print(f"  Generating review report for {file_path} …", flush=True)
        try:
            data['_validation_report'] = ReportBuilder(
                folder_url=f"emd:{kind}s", kind=kind, item=data, link_threshold=80.0
            ).build()
        except Exception as e:
            print(f"  ⚠ Report generation failed: {e}", flush=True)
            data['_validation_report'] = ''

        # rename back after report generation
        data['units'] = data.pop('horizontal_units', None)
