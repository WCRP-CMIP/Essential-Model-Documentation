# Vertical Computational Grid Template Data
# Loads CVs from CMIP-LD to avoid hardcoding

import cmipld
from cmipld.utils.ldparse import name_multikey_extract

# Data for this template
DATA = {
    # Vertical coordinate from CV
    'vertical_coordinate': name_multikey_extract(
        cmipld.get('constants:vertical_coordinate/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    
    # Issue metadata
    'issue_kind': ['New', 'Modify']
}


def generate_vertical_computational_grid(issue_data):
    """
    Generate vertical_computational_grid from issue data.
    
    Auto-generates:
    - Grid ID (v###)
    
    Returns:
        dict: {
            'v_grid_id': 'v100',
            'entity': {...}
        }
    """
    # Get next available ID
    v_grid_id = get_next_id('vertical_computational_grid')  # e.g., v100
    
    # Create v_grid entity
    v_grid = {
        'validation_key': v_grid_id,
        'ui_label': '',
        'description': issue_data['description'],
        'vertical_coordinate': issue_data['vertical_coordinate'],
        '@context': '_context',
        '@type': ['emd', 'wcrp:vertical_computational_grid', 'esgvoc:VerticalComputationalGrid'],
        '@id': v_grid_id
    }
    
    # Add optional fields
    if issue_data.get('n_z'):
        v_grid['n_z'] = int(issue_data['n_z'])
    if issue_data.get('n_z_range'):
        # Parse "min,max" format
        parts = issue_data['n_z_range'].split(',')
        if len(parts) == 2:
            v_grid['n_z_range'] = [int(parts[0].strip()), int(parts[1].strip())]
    if issue_data.get('top_layer_thickness'):
        v_grid['top_layer_thickness'] = float(issue_data['top_layer_thickness'])
    if issue_data.get('bottom_layer_thickness'):
        v_grid['bottom_layer_thickness'] = float(issue_data['bottom_layer_thickness'])
    if issue_data.get('total_thickness'):
        v_grid['total_thickness'] = float(issue_data['total_thickness'])
    
    return {
        'v_grid_id': v_grid_id,
        'entity': v_grid
    }


def get_next_id(entity_type):
    """Get next available ID for entity type."""
    # Implementation would check existing entities and return next ID
    pass
