# Horizontal Computational Grid Template Data
# Loads CVs from CMIP-LD to avoid hardcoding

import cmipld
from cmipld.utils.ldparse import name_multikey_extract

# Data for this template
DATA = {
    # Arrangement from CV
    'arrangement': name_multikey_extract(
        cmipld.get('constants:arrangement/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    
    # Issue metadata
    'issue_kind': ['New', 'Modify']
}


def generate_horizontal_computational_grid(issue_data):
    """
    Generate horizontal_computational_grid from issue data.
    
    Auto-generates:
    - Grid ID (c###)
    - Links to subgrids
    
    Returns:
        dict: {
            'h_grid_id': 'c100',
            'entity': {...}
        }
    """
    # Get next available ID
    h_grid_id = get_next_id('horizontal_computational_grid')  # e.g., c100
    
    # Parse subgrid IDs from textarea
    subgrid_ids = parse_textarea_list(issue_data.get('horizontal_subgrids', ''))
    
    # Create h_grid entity
    h_grid = {
        'validation_key': h_grid_id,
        'ui_label': '',
        'description': issue_data['description'],
        'arrangement': issue_data['arrangement'],
        'horizontal_subgrids': subgrid_ids,
        '@context': '_context',
        '@type': ['emd', 'wcrp:horizontal_computational_grid', 'esgvoc:HorizontalComputationalGrid'],
        '@id': h_grid_id
    }
    
    return {
        'h_grid_id': h_grid_id,
        'entity': h_grid
    }


def parse_textarea_list(text):
    """Parse textarea into list (one item per line)."""
    if not text:
        return []
    return [line.strip() for line in text.split('\n') if line.strip()]


def get_next_id(entity_type):
    """Get next available ID for entity type."""
    # Implementation would check existing entities and return next ID
    # e.g., check for c100, c101, c102... and return next available
    pass
