"""
Handler for Horizontal Grid Cell registration (Stage 1)
"""

import os
import sys
import json
from typing import Any

# Import from cmipld utils
from cmipld.utils.id_generation import generate_id_from_issue
from cmipld.utils.esgvoc import pycmipld, DATA_DESCRIPTOR_CLASS_MAPPING
from cmipld.utils.similarity import ReportBuilder


kind = __file__.split('/')[-1].replace('.py','')


def generate_markdown_report(data: dict, graph_data: dict | None = None) -> str:
    """
    Generate the full reviewer report using ReportBuilder.

    Sections:
      1. Field status table (pydantic model fields + icon + submitted value)
      2. Pydantic validation errors in a warning admonition (if any)
      3. Link similarity — Mermaid graph + list of >80% overlap items
      4. Content (text) similarity on remaining fields
    """
    folder_url = f"emd:{kind}s"   # e.g. emd:horizontal_grid_cells
    return ReportBuilder(
        folder_url  = folder_url,
        kind        = kind,
        item        = data,
        graph_data  = graph_data,
        link_threshold = 80.0,
    ).build()


def run(parsed_issue, issue, dry_run=False):
    """
    Process horizontal grid cell submission.
    Generate @id from author + timestamp if validation_key not provided.
    """
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
            "@type": ["wcrp:horizontal_grid_cell", "esgvoc:HorizontalGridCells"],
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
    """
    Validate all files with esgvoc pydantic model.
    Generates markdown validation report for each file.
    
    Args:
        files_to_write: Dict of {'path/file.json': data, '_author': ..., '_contributors': [...], '_make_pull': ...}
        parsed_issue: Parsed issue body sections
        issue: Full issue metadata
        dry_run: If True, don't perform side effects
    
    Modifies files_to_write in place, adding '_validation_report' to each data dict.
    Metadata keys (starting with '_') are preserved.
    """
    
    for file_path, data in files_to_write.items():
        # Skip metadata keys (starting with '_')
        if file_path.startswith('_'):
            continue
        

        # Generate and store validation report using the full ReportBuilder pipeline
        data['_validation_report'] = generate_markdown_report(data)
        
        # return the patch post validation. 
        data['units'] = data.pop('horizontal_units', None)  # rename back for validation
