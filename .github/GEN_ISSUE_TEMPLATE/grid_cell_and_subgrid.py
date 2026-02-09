# Grid Cell and Subgrid Template Data
# Loads CVs from CMIP-LD to avoid hardcoding

import cmipld
from cmipld.utils.ldparse import name_multikey_extract

# Data for this template - loaded from CVs
DATA = {
    # Grid types from CV
    'grid_type': name_multikey_extract(
        cmipld.get('constants:grid_type/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    
    # Grid mapping from CV
    'grid_mapping': name_multikey_extract(
        cmipld.get('constants:grid_mapping/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    
    # Region from CV
    'region': name_multikey_extract(
        cmipld.get('constants:region/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    
    # Temporal refinement from CV
    'temporal_refinement': name_multikey_extract(
        cmipld.get('constants:temporal_refinement/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    
    # Units from CV
    'units': name_multikey_extract(
        cmipld.get('constants:units/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    
    # Truncation method from CV
    'truncation_method': name_multikey_extract(
        cmipld.get('constants:truncation_method/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    
    # Cell variable types from CV
    'cell_variable_type': name_multikey_extract(
        cmipld.get('constants:cell_variable_type/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    
    # Issue metadata
    'issue_kind': ['New', 'Modify']
}


def generate_grid_cell_and_subgrid(issue_data):
    """
    Generate horizontal_grid_cells and horizontal_subgrid from issue data.
    
    Auto-generates:
    - Grid cells description from properties
    - Subgrid description from variable types
    - IDs (g###, s###)
    - Cross-reference link
    
    Returns:
        dict: {
            'grid_cells_id': 'g100',
            'subgrid_id': 's100',
            'entities': {
                'horizontal_grid_cells': {...},
                'horizontal_subgrid': {...}
            }
        }
    """
    # Get next available IDs
    grid_cells_id = get_next_id('horizontal_grid_cells')  # e.g., g100
    subgrid_id = get_next_id('horizontal_subgrid')        # e.g., s100
    
    # Auto-generate grid_cells description
    grid_cells_desc = generate_grid_cells_description(issue_data)
    # Example: "Global regular-latitude-longitude grid with 1.25° x 0.9° resolution and 55296 cells."
    
    # Auto-generate subgrid description
    subgrid_desc = generate_subgrid_description(issue_data)
    # Example: "Mass variables on a regular latitude-longitude grid."
    
    # Create grid_cells entity
    grid_cells = {
        'validation_key': grid_cells_id,
        'ui_label': '',
        'description': grid_cells_desc,
        'grid_type': issue_data['grid_type'],
        'grid_mapping': issue_data['grid_mapping'],
        'region': issue_data['region'],
        'temporal_refinement': issue_data['temporal_refinement'],
        '@context': '_context',
        '@type': ['emd', 'wcrp:horizontal_grid_cells', 'esgvoc:HorizontalGridCells'],
        '@id': grid_cells_id
    }
    
    # Add optional fields if provided
    if issue_data.get('x_resolution'):
        grid_cells['x_resolution'] = float(issue_data['x_resolution'])
    if issue_data.get('y_resolution'):
        grid_cells['y_resolution'] = float(issue_data['y_resolution'])
    if issue_data.get('units'):
        grid_cells['units'] = issue_data['units']
    if issue_data.get('n_cells'):
        grid_cells['n_cells'] = int(issue_data['n_cells'])
    if issue_data.get('southernmost_latitude'):
        grid_cells['southernmost_latitude'] = float(issue_data['southernmost_latitude'])
    if issue_data.get('westernmost_longitude'):
        grid_cells['westernmost_longitude'] = float(issue_data['westernmost_longitude'])
    if issue_data.get('truncation_method'):
        grid_cells['truncation_method'] = issue_data['truncation_method']
    if issue_data.get('truncation_number'):
        grid_cells['truncation_number'] = int(issue_data['truncation_number'])
    
    # Create subgrid entity (auto-linked)
    subgrid = {
        'validation_key': subgrid_id,
        'ui_label': '',
        'description': subgrid_desc,
        'cell_variable_type': issue_data['cell_variable_type'],
        'horizontal_grid_cells': grid_cells_id,  # Auto-link
        '@context': '_context',
        '@type': ['emd', 'wcrp:horizontal_subgrid', 'esgvoc:HorizontalSubgrid'],
        '@id': subgrid_id
    }
    
    return {
        'grid_cells_id': grid_cells_id,
        'subgrid_id': subgrid_id,
        'entities': {
            'horizontal_grid_cells': grid_cells,
            'horizontal_subgrid': subgrid
        }
    }


def generate_grid_cells_description(data):
    """Generate description for grid_cells from properties."""
    parts = []
    
    # Region
    if data.get('region'):
        if 'global' in data['region']:
            parts.append('Global')
        else:
            parts.append(' '.join(data['region']))
    
    # Grid type
    parts.append(data.get('grid_type', '').replace('-', ' '))
    parts.append('grid')
    
    # Resolution
    if data.get('x_resolution') and data.get('y_resolution'):
        parts.append(f"with {data['x_resolution']}° x {data['y_resolution']}° resolution")
    
    # Cell count
    if data.get('n_cells'):
        parts.append(f"and {data['n_cells']} cells")
    
    return ' '.join(parts) + '.'


def generate_subgrid_description(data):
    """Generate description for subgrid from variable types."""
    var_types = data.get('cell_variable_type', [])
    grid_type = data.get('grid_type', '').replace('-', ' ')
    
    # Format variable types
    if len(var_types) == 1:
        var_str = var_types[0].replace('_', ' ').replace('-', ' ').capitalize()
    else:
        var_str = ' and '.join(v.replace('_', ' ') for v in var_types).capitalize()
    
    return f"{var_str} variables on a {grid_type} grid."
