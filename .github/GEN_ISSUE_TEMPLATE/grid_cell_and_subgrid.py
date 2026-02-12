# Grid Cell and Subgrid Template Data

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
    'issue_kind': ['New', 'Modify']
}
