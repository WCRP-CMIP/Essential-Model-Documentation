"""
Handler for Model Family registration (Stage 2, supporting)
"""

def run(parsed_issue, issue, dry_run=False):
    """
    Process model family submission.
    Returns None to let generic handler build initial data.
    """
    return None


def update(data, parsed_issue, issue, dry_run=False):
    """
    Enrich model family data with computed fields and validation.
    
    Args:
        data: Initial JSON-LD data built from issue
        parsed_issue: Parsed issue body sections
        issue: Full issue metadata
        dry_run: If True, don't perform side effects
    
    Returns:
        Enriched data dict
    """
    
    # Determine family type
    family_type = parsed_issue.get('family_type', '').lower()
    if 'component' in family_type:
        data['@type'] = ['wcrp:model_family_component']
    elif 'earth' in family_type or 'coupled' in family_type:
        data['@type'] = ['wcrp:model_family_earth_system']
    else:
        data['@type'] = ['wcrp:model_family']
    
    # Parse institution references (should link to existing organisations)
    if 'primary_institution' in data:
        inst = data['primary_institution']
        if isinstance(inst, str):
            # Store for validation - should reference valid institution
            data['primary_institution_ref'] = inst.strip()
    
    if 'collaborative_institutions' in data:
        collab = data['collaborative_institutions']
        if isinstance(collab, str):
            collab = [c.strip() for c in collab.split(',')]
            data['collaborative_institutions'] = collab
    
    # Parse scientific domains
    if 'scientific_domains' in data:
        domains = data['scientific_domains']
        if isinstance(domains, str):
            domains = [d.strip() for d in domains.split(',')]
            data['scientific_domains'] = domains
    
    # Parse DOI references
    if 'reference_dois' in data:
        dois = data['reference_dois']
        if isinstance(dois, str):
            dois = [d.strip() for d in dois.split('\n') if d.strip()]
            data['reference_dois'] = dois
    
    # Validate year format
    if 'established' in data:
        try:
            year = int(data['established'])
            if 1950 <= year <= 2100:  # Reasonable range
                data['year_valid'] = True
        except (ValueError, TypeError):
            pass
    
    # Ensure website format
    if 'website' in data:
        url = data['website'].strip()
        if url and not url.startswith(('http://', 'https://')):
            data['website'] = f"https://{url}"
    
    return data
