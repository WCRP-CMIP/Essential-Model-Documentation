# Grid Cell and Subgrid Template Data
import sys
import os

# Try to import from cmipld, fall back to empty if not available
try:
    sys.path.insert(0, os.path.expanduser('~/WIPwork/CMIP-LD'))
    from cmipld.generate.template_utils import get_existing_entries_markdown, get_repo_info
    
    # Get existing grid cells for prefill links
    existing_grid_cells = get_existing_entries_markdown('horizontal_grid_cells')
    if not existing_grid_cells:
        existing_grid_cells = "_No existing grid cells registered yet._"
except ImportError:
    existing_grid_cells = "_Prefill links unavailable - run from repository root._"

DATA = {
    'grid_type': [
        'regular-latitude-longitude',
        'reduced-gaussian',
        'tripolar',
        'displaced-pole',
        'icosahedral',
        'cubed-sphere',
        'adaptive-mesh'
    ],
    'grid_mapping': [
        'latitude-longitude',
        'rotated-latitude-longitude',
        'stereographic',
        'lambert-conformal'
    ],
    'region': [
        'global',
        'regional',
        'arctic',
        'antarctic',
        'tropical'
    ],
    'temporal_refinement': [
        'static',
        'adaptive'
    ],
    'units': [
        'degree',
        'km',
        'm'
    ],
    'truncation_method': [
        'triangular',
        'rhomboidal',
        'linear'
    ],
    'cell_variable_type': [
        'mass',
        'zonal-velocity',
        'meridional-velocity',
        'vorticity',
        'divergence'
    ],
    'subgrid_option': [
        'Create new subgrid',
        'No subgrid (grid cells only)'
    ],
    'issue_kind': ['New', 'Modify'],
    
    # Dynamic content for prefill links
    'existing_grid_cells': existing_grid_cells
}
