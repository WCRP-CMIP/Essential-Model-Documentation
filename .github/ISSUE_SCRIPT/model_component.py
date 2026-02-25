"""
Handler for Model Component registration (Stage 3)
"""

def run(parsed_issue, issue, dry_run=False):
    """
    Process model component submission.
    Returns None to let generic handler build initial data.
    """
    return None


def update(data, parsed_issue, issue, dry_run=False):
    """
    Enrich component data with computed fields and configuration ID generation.
    
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
        data['@type'] = ['wcrp:model_component']
    
    # Map scientific domain to short code
    domain_map = {
        'aerosol': 'ae',
        'atmosphere': 'atm',
        'atmospheric-chemistry': 'atmchem',
        'land-ice': 'li',
        'land-surface': 'ls',
        'ocean': 'oc',
        'ocean-biogeochemistry': 'ocbgc',
        'sea-ice': 'si',
    }
    
    component = data.get('component', '').lower()
    domain_code = domain_map.get(component, component[:3])
    
    # Generate component_config ID format: {domain}_{name}_{c###}_{v###}
    # This will be completed during PR processing with actual grid IDs
    component_name = data.get('name', 'unknown').lower().replace(' ', '-')
    h_grid = parsed_issue.get('horizontal_computational_grid', '').strip()
    v_grid = parsed_issue.get('vertical_computational_grid', '').strip()
    
    if h_grid and v_grid:
        config_id = f"{domain_code}_{component_name}_{h_grid}_{v_grid}"
        data['component_config_id'] = config_id
    else:
        # Partial ID - will be completed during review
        data['component_config_id_partial'] = f"{domain_code}_{component_name}"
    
    # Parse DOI references
    if 'reference_dois' in data:
        dois = data['reference_dois']
        if isinstance(dois, str):
            dois = [d.strip() for d in dois.split('\n') if d.strip()]
            data['reference_dois'] = dois
    
    # Validate grid references (should exist from Stage 2)
    h_ref = parsed_issue.get('horizontal_computational_grid', '')
    v_ref = parsed_issue.get('vertical_computational_grid', '')
    
    if h_ref and not h_ref.startswith('c'):
        # Try to auto-fix c### format
        if h_ref.isdigit():
            data['horizontal_computational_grid'] = f"c{h_ref}"
    
    if v_ref and not v_ref.startswith('v'):
        if v_ref.isdigit():
            data['vertical_computational_grid'] = f"v{v_ref}"
    
    return data
