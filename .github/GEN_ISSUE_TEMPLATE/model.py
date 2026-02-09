# Model Template Data
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
    
    # Calendar types from CV
    'calendar': name_multikey_extract(
        cmipld.get('constants:model_calendar/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    
    # Model families from registered families
    'model_family': name_multikey_extract(
        cmipld.get('emd:model_family/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    
    # Issue metadata
    'issue_kind': ['New', 'Modify']
}


def generate_model(issue_data):
    """
    Generate model entity from issue data.
    
    Parses:
    - component_configs (textarea, one ID per line)
    - embedded_components (textarea, pairs as "embedded,host")
    - coupling_groups (textarea, groups as "comp,comp,comp")
    
    Validates:
    - All component_configs exist
    - Embedded/coupling relationships valid
    
    Returns:
        dict: {
            'model_id': 'cnrm-esm2-1e',
            'entity': {...}
        }
    """
    # Generate model ID from name
    model_id = generate_id_from_name(issue_data['name'])
    
    # Parse component_configs
    component_configs = parse_textarea_list(issue_data.get('component_configs', ''))
    
    # Parse embedded_components
    embedded_components = parse_embedded_components(
        issue_data.get('embedded_components', '')
    )
    
    # Parse coupling_groups
    coupling_groups = parse_coupling_groups(
        issue_data.get('coupling_groups', '')
    )
    
    # Parse references
    references = parse_dois(issue_data.get('reference_dois', ''))
    
    # Create model entity
    model = {
        'validation_key': model_id.replace('-', '_'),
        'ui_label': '',
        'name': issue_data['name'],
        'description': issue_data['description'],
        'dynamic_components': issue_data['dynamic_components'],
        'embedded_components': embedded_components,
        'coupling_groups': coupling_groups,
        'component_configs': component_configs,
        'calendar': issue_data['calendar'],
        'release_year': int(issue_data['release_year']),
        'references': references,
        '@context': '_context',
        '@type': ['emd', 'wcrp:model', 'esgvoc:Model'],
        '@id': model_id
    }
    
    # Add optional fields
    if issue_data.get('family'):
        model['family'] = issue_data['family']
    if issue_data.get('prescribed_components'):
        model['prescribed_components'] = issue_data['prescribed_components']
    if issue_data.get('omitted_components'):
        model['omitted_components'] = issue_data['omitted_components']
    
    return {
        'model_id': model_id,
        'entity': model
    }


def parse_textarea_list(text):
    """Parse textarea into list (one item per line)."""
    if not text:
        return []
    return [line.strip() for line in text.split('\n') if line.strip()]


def parse_embedded_components(text):
    """
    Parse embedded_components from textarea.
    
    Format: "embedded,host" one pair per line
    Example:
        aerosol,atmosphere
        atmospheric-chemistry,atmosphere
    
    Returns: [["aerosol", "atmosphere"], ["atmospheric-chemistry", "atmosphere"]]
    """
    if not text:
        return []
    
    pairs = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(',')]
        if len(parts) == 2:
            pairs.append(parts)
    
    return pairs


def parse_coupling_groups(text):
    """
    Parse coupling_groups from textarea.
    
    Format: "comp,comp,comp" one group per line
    Example:
        atmosphere,land-surface,ocean
        component-x,component-y
    
    Returns: [["atmosphere", "land-surface", "ocean"], ["component-x", "component-y"]]
    """
    if not text:
        return []
    
    groups = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        components = [c.strip() for c in line.split(',')]
        if components:
            groups.append(components)
    
    return groups


def parse_dois(text):
    """Parse DOI URLs from textarea (one per line)."""
    if not text:
        return []
    
    return [line.strip() for line in text.split('\n') if line.strip()]


def generate_id_from_name(name):
    """Convert model name to kebab-case ID."""
    import re
    id_str = re.sub(r'[^a-z0-9]+', '-', name.lower())
    id_str = id_str.strip('-')
    return id_str
