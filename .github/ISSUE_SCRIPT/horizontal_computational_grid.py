"""
Handler for Horizontal Computational Grid registration (Stage 2a)
"""

import os
import sys

# Import from cmipld utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'CMIP-LD'))
from cmipld.utils.id_generation import generate_id_from_issue


def run(parsed_issue, issue, dry_run=False):
    """
    Process horizontal computational grid submission.
    Generate @id from author + timestamp if not provided.
    
    Returns dict: {'path/to/file.json': data}
    """
    # If no validation_key, generate @id from author + timestamp
    if not parsed_issue.get('validation_key') and issue.get('author') and issue.get('created_at'):
        id_result = generate_id_from_issue(issue.get('author'), issue.get('created_at'))
        
        data = {
            "@context": "_context",
            "@id": id_result['id'],
            "@type": ["wcrp:horizontal_computational_grid"],
        }
        
        # Store submission metadata
        if id_result['epoch']:
            data['_submitted_by'] = id_result['author']
            data['_submitted_at_epoch'] = id_result['epoch']
        
        # Return as dict with file path
        file_path = os.path.join('horizontal_computational_grid', f"{id_result['id']}.json")
        
        return {file_path: data}
    
    # Otherwise let generic handler build from validation_key
    return None


def update(data, parsed_issue, issue, dry_run=False):
    """
    Enrich horizontal grid data with computed fields and validation.
    
    Args:
        data: Initial JSON-LD data built from issue
        parsed_issue: Parsed issue body sections
        issue: Full issue metadata
        dry_run: If True, don't perform side effects
    
    Returns:
        Enriched data dict
    """
    
    # Ensure required @type array
    if '@type' not in data:
        data['@type'] = ['wcrp:horizontal_computational_grid']
    
    # Parse and validate arrangement type
    arrangement = data.get('arrangement', '').lower()
    valid_arrangements = ['arakawa-a', 'arakawa-b', 'arakawa-c', 'arakawa-e', 'spectral', 'gaussian']
    
    if arrangement and arrangement not in valid_arrangements:
        # Try to match partial strings
        for valid in valid_arrangements:
            if valid in arrangement:
                data['arrangement'] = valid
                break
    
    # Parse subgrid references
    if 'horizontal_subgrids' in data:
        subgrids = data['horizontal_subgrids']
        if isinstance(subgrids, str):
            # Parse comma-separated list
            subgrids = [s.strip() for s in subgrids.split(',')]
            data['horizontal_subgrids'] = subgrids
    
    return data
