"""
Handler for Horizontal Computational Grid registration (Stage 2a)
"""

def run(parsed_issue, issue, dry_run=False):
    """
    Process horizontal computational grid submission.
    Returns None to let generic handler build initial data.
    """
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
