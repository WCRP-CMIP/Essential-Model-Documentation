"""
Handler for Model (source_id) registration (Stage 4)
"""

def run(parsed_issue, issue, dry_run=False):
    """
    Process model submission.
    Returns None to let generic handler build initial data.
    """
    return None


def update(data, parsed_issue, issue, dry_run=False):
    """
    Enrich model data with computed fields, validation, and coupling configuration.
    
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
        data['@type'] = ['wcrp:model']
    
    # Parse component arrays (dynamic, prescribed, omitted)
    component_fields = ['dynamic_components', 'prescribed_components', 'omitted_components']
    for field in component_fields:
        if field in data:
            components = data[field]
            if isinstance(components, str):
                components = [c.strip() for c in components.split(',')]
                data[field] = components
    
    # Parse calendar types
    if 'calendar' in data:
        calendars = data['calendar']
        if isinstance(calendars, str):
            calendars = [c.strip() for c in calendars.split(',')]
            data['calendar'] = calendars
    
    # Validate release year
    if 'release_year' in data:
        try:
            year = int(data['release_year'])
            if 1950 <= year <= 2100:
                data['year_valid'] = True
        except (ValueError, TypeError):
            pass
    
    # Parse DOI references
    if 'reference_dois' in data:
        dois = data['reference_dois']
        if isinstance(dois, str):
            dois = [d.strip() for d in dois.split('\n') if d.strip()]
            data['reference_dois'] = dois
    
    # Parse component configuration IDs
    if 'component_configs' in data:
        configs = data['component_configs']
        if isinstance(configs, str):
            configs = [c.strip() for c in configs.split(',')]
            data['component_configs'] = configs
    
    # Parse coupling configurations
    # Map coupling_group_* fields into structured coupling array
    coupling_groups = []
    for i in range(1, 6):
        field = f'coupling_group_{i}'
        if field in data:
            group = data[field]
            if isinstance(group, str):
                group = [c.strip() for c in group.split(',') if c.strip()]
            if group:  # Only add non-empty groups
                coupling_groups.append({
                    'group_id': i,
                    'components': group
                })
            # Remove the individual field
            del data[field]
    
    if coupling_groups:
        data['coupling_groups'] = coupling_groups
    
    # Parse embedded components
    if 'embedded_components' in data:
        embedded = data['embedded_components']
        if isinstance(embedded, str):
            embedded = [e.strip() for e in embedded.split(',')]
            data['embedded_components'] = embedded
    
    # Ensure all required fields are present
    required_fields = ['name', 'dynamic_components', 'calendar', 'release_year', 'reference_dois']
    for field in required_fields:
        if field not in data:
            data[f'{field}_missing'] = True
    
    return data
