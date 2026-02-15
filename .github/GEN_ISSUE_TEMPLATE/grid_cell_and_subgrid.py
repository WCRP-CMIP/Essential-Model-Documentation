#!/usr/bin/env python3
"""
Data definitions for grid_cell_and_subgrid template.

Provides dropdown options and dynamic content for template generation.
"""

# Try to fetch from controlled vocabularies
try:
    import cmipld
    
    def get_cv_list(url, key='id'):
        """Fetch controlled vocabulary list from JSON-LD."""
        try:
            data = cmipld.get(url, depth=1)
            if isinstance(data, dict) and '@graph' in data:
                items = data['@graph']
            elif isinstance(data, list):
                items = data
            else:
                return []
            return [item.get(key, '').split('/')[-1] for item in items if item.get(key)]
        except:
            return []
    
    grid_type = get_cv_list('emd:grid_type') or [
        'regular-latitude-longitude', 'reduced-gaussian', 'tripolar',
        'displaced-pole', 'icosahedral', 'cubed-sphere', 'adaptive-mesh'
    ]
    grid_mapping = get_cv_list('emd:grid_mapping') or [
        'latitude-longitude', 'rotated-latitude-longitude', 
        'stereographic', 'lambert-conformal'
    ]
    region = get_cv_list('emd:region') or [
        'global', 'regional', 'arctic', 'antarctic', 'tropical'
    ]
    temporal_refinement = get_cv_list('emd:temporal_refinement') or [
        'static', 'adaptive'
    ]
    units = get_cv_list('emd:units') or ['degrees', 'km', 'm']
    truncation_method = get_cv_list('emd:truncation_method') or [
        'triangular', 'rhomboidal', 'linear'
    ]
    cell_variable_type = get_cv_list('emd:cell_variable_type') or [
        'mass', 'zonal-velocity', 'meridional-velocity', 'vorticity', 'divergence'
    ]

except ImportError:
    # Fallback values if cmipld not available
    grid_type = [
        'regular-latitude-longitude', 'reduced-gaussian', 'tripolar',
        'displaced-pole', 'icosahedral', 'cubed-sphere', 'adaptive-mesh'
    ]
    grid_mapping = [
        'latitude-longitude', 'rotated-latitude-longitude',
        'stereographic', 'lambert-conformal'
    ]
    region = ['global', 'regional', 'arctic', 'antarctic', 'tropical']
    temporal_refinement = ['static', 'adaptive']
    units = ['degrees', 'km', 'm']
    truncation_method = ['triangular', 'rhomboidal', 'linear']
    cell_variable_type = [
        'mass', 'zonal-velocity', 'meridional-velocity', 'vorticity', 'divergence'
    ]

# Try to generate prefill links for existing entries
try:
    from cmipld.generate.template_utils import get_existing_entries_markdown
    existing_grid_cells = get_existing_entries_markdown('grid_cell_and_subgrid')
    if not existing_grid_cells:
        existing_grid_cells = "_No existing grid cells registered yet._"
except:
    existing_grid_cells = "_Prefill links unavailable - run from repository root._"

# Standard options
issue_kind = ['New', 'Modify']
subgrid_option = ['Create new subgrid', 'No subgrid (grid cells only)']

# Data dictionary for template substitution
DATA = {
    'grid_type': grid_type,
    'grid_mapping': grid_mapping,
    'region': region,
    'temporal_refinement': temporal_refinement,
    'units': units,
    'truncation_method': truncation_method,
    'cell_variable_type': cell_variable_type,
    'issue_kind': issue_kind,
    'subgrid_option': subgrid_option,
    'existing_grid_cells': existing_grid_cells,
}
