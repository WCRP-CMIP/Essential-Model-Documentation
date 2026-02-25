"""
Handler for Horizontal Grid Cells and Subgrid registration (Stage 1)
"""

def run(parsed_issue, issue, dry_run=False):
    """
    Process horizontal grid cells and subgrid submission.
    Returns None to let generic handler build initial data.
    """
    return None


def update(data, parsed_issue, issue, dry_run=False):
    """
    Enrich grid cells/subgrid data with computed fields.
    
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
        data['@type'] = ['wcrp:horizontal_grid_cells']
    
    # Validate grid parameters
    if 'x_resolution' in data or 'y_resolution' in data:
        try:
            x_res = float(data.get('x_resolution', 0))
            y_res = float(data.get('y_resolution', 0))
            if x_res > 0 and y_res > 0:
                data['resolution_valid'] = True
        except (ValueError, TypeError):
            pass  # Resolution not numeric, skip validation
    
    # Handle subgrid option
    subgrid_option = parsed_issue.get('subgrid_option', '').lower()
    if 'no subgrid' in subgrid_option:
        # Grid cells only, no subgrid
        data['has_subgrid'] = False
    else:
        data['has_subgrid'] = True
    
    # Ensure variable types are captured if subgrid
    if data.get('has_subgrid') and 'cell_variable_type' in data:
        if isinstance(data['cell_variable_type'], str):
            data['cell_variable_type'] = [v.strip() for v in data['cell_variable_type'].split(',')]
    
    return data
