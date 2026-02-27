"""
Handler for Vertical Computational Grid registration (Stage 2b)
"""

import os
import sys

# Import from cmipld utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'CMIP-LD'))
from cmipld.utils.id_generation import generate_id_from_issue


def run(parsed_issue, issue, dry_run=False):
    """
    Process vertical computational grid submission.
    Generate @id from author + timestamp if not provided.
    
    Returns dict: {'path/to/file.json': data}
    """
    # If no validation_key, generate @id from author + timestamp
    if not parsed_issue.get('validation_key') and issue.get('author') and issue.get('created_at'):
        id_result = generate_id_from_issue(issue.get('author'), issue.get('created_at'))
        
        data = {
            "@context": "_context",
            "@id": id_result['id'],
            "@type": ["wcrp:vertical_computational_grid"],
        }
        
        # Store submission metadata
        if id_result['epoch']:
            data['_submitted_by'] = id_result['author']
            data['_submitted_at_epoch'] = id_result['epoch']
        
        # Return as dict with file path
        file_path = os.path.join('vertical_computational_grid', f"{id_result['id']}.json")
        
        return {file_path: data}
    
    # Otherwise let generic handler build from validation_key
    return None


def update(data, parsed_issue, issue, dry_run=False):
    """
    Enrich vertical grid data with computed fields and validation.
    
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
        data['@type'] = ['wcrp:vertical_computational_grid']
    
    # Parse and validate coordinate type
    coord_type = data.get('vertical_coordinate', '').lower()
    valid_coords = ['pressure', 'height', 'hybrid', 'sigma', 'eta', 'potential-temperature']
    
    if coord_type and coord_type not in valid_coords:
        for valid in valid_coords:
            if valid in coord_type:
                data['vertical_coordinate'] = valid
                break
    
    # Validate numeric fields
    numeric_fields = {
        'n_z': 'Number of levels must be > 0',
        'top_layer_thickness': 'Top layer thickness must be positive',
        'bottom_layer_thickness': 'Bottom layer thickness must be positive',
        'total_thickness': 'Total thickness must be positive'
    }
    
    for field, msg in numeric_fields.items():
        if field in data:
            try:
                value = float(data[field])
                if value <= 0:
                    data[f'{field}_valid'] = False
            except (ValueError, TypeError):
                pass  # Not numeric, skip
    
    return data
