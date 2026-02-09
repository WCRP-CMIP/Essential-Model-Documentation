# Model Component Template Data
# Loads CVs from CMIP-LD to avoid hardcoding

import cmipld
from cmipld.utils.ldparse import name_multikey_extract

# Data for this template - loaded from CVs
DATA = {
    # Component types from CV
    'component': name_multikey_extract(
        cmipld.get('constants:scientific_domain/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    
    # Component families from registered families
    'component_family': name_multikey_extract(
        cmipld.get('emd:model_family/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    
    # Issue metadata
    'issue_kind': ['New', 'Modify']
}


def generate_component_and_config(issue_data):
    """
    Generate model_component and component_config from issue data.
    
    Auto-generates:
    - Component ID from name (kebab-case)
    - Component config ID with domain prefix
    - Component config description
    - Component config ui_label
    
    Returns:
        dict: {
            'component_id': 'arpege-climat-version-6-3',
            'component_config_id': 'atmosphere_arpege-climat-version-6-3_c100_v100',
            'entities': {
                'model_component': {...},
                'component_config': {...}
            }
        }
    """
    # Generate component ID from name
    component_id = generate_id_from_name(issue_data['name'])
    
    # Get inputs
    component_type = issue_data['component']
    h_grid = issue_data.get('horizontal_computational_grid')
    v_grid = issue_data.get('vertical_computational_grid')
    
    # Generate component_config ID with domain prefix
    h_part = h_grid if h_grid else 'none'
    v_part = v_grid if v_grid else 'none'
    component_config_id = f"{component_type}_{component_id}_{h_part}_{v_part}"
    
    # Auto-generate component_config description
    config_desc = generate_component_config_description(
        issue_data['name'], h_grid, v_grid
    )
    
    # Auto-generate component_config ui_label
    ui_label = generate_component_config_ui_label(
        issue_data['name'], h_grid, v_grid
    )
    
    # Create component entity
    component = {
        'validation_key': component_id.replace('-', '_'),
        'ui_label': '',
        'description': issue_data['description'],
        'component': component_type,
        'name': issue_data['name'],
        '@context': '_context',
        '@type': ['emd', 'wcrp:model_component', 'esgvoc:ModelComponent'],
        '@id': component_id
    }
    
    # Add optional fields
    if issue_data.get('family'):
        component['family'] = issue_data['family']
    if issue_data.get('code_base'):
        component['code_base'] = issue_data['code_base']
    if issue_data.get('reference_dois'):
        component['references'] = parse_dois(issue_data['reference_dois'])
    
    # Create component_config entity
    component_config = {
        'validation_key': component_config_id.replace('-', '_'),
        'ui_label': ui_label,
        'description': config_desc,
        'model_component': component_id,
        '@context': '_context',
        '@type': ['emd', 'wcrp:component_config', 'esgvoc:ComponentConfig'],
        '@id': component_config_id
    }
    
    # Add grid references
    if h_grid:
        component_config['horizontal_computational_grid'] = h_grid
    if v_grid:
        component_config['vertical_computational_grid'] = v_grid
    
    return {
        'component_id': component_id,
        'component_config_id': component_config_id,
        'entities': {
            'model_component': component,
            'component_config': component_config
        }
    }


def generate_id_from_name(name):
    """Convert component name to kebab-case ID."""
    import re
    # Convert to lowercase, replace spaces/special chars with hyphens
    id_str = re.sub(r'[^a-z0-9]+', '-', name.lower())
    # Remove leading/trailing hyphens
    id_str = id_str.strip('-')
    return id_str


def generate_component_config_description(name, h_grid, v_grid):
    """Auto-generate component_config description."""
    parts = [f"Configuration for {name}"]
    
    if h_grid:
        parts.append(f"with horizontal grid {h_grid}")
    if v_grid:
        parts.append(f"and vertical grid {v_grid}" if h_grid else f"with vertical grid {v_grid}")
    
    return ' '.join(parts) + '.'


def generate_component_config_ui_label(name, h_grid, v_grid):
    """Auto-generate component_config ui_label."""
    parts = [name]
    
    grid_parts = []
    if h_grid:
        grid_parts.append(h_grid)
    if v_grid:
        grid_parts.append(v_grid)
    
    if grid_parts:
        parts.append(f"with {' and '.join(grid_parts)}")
    
    return ' '.join(parts)


def parse_dois(doi_text):
    """Parse DOI URLs from textarea (one per line)."""
    if not doi_text:
        return []
    
    dois = [line.strip() for line in doi_text.split('\n') if line.strip()]
    return dois
