# Horizontal Grid Cells Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Horizontal Grid Cells',
    'description': 'Register horizontal grid cell properties',
    'title': 'Add/Modify: Horizontal Grid Cells: <Type grid cells ID here>',
    'labels': ['emd-submission', 'horizontal-grid', 'Review'],
    'issue_category': 'horizontal_grid_cells'
}

# Try to load from cmipld if available, otherwise use hardcoded values
try:
    import cmipld
    from cmipld.utils.ldparse import name_extract

    DATA = {
        'grid_type': name_extract(cmipld.get('universal:grid_type/graph.jsonld', depth=0)),
        'grid_mapping': name_extract(cmipld.get('universal:grid_mapping/graph.jsonld', depth=0)),
        'region': name_extract(cmipld.get('universal:region/graph.jsonld', depth=0)),
        'temporal_refinement': name_extract(cmipld.get('universal:temporal_refinement/graph.jsonld', depth=0)),
        'units': name_extract(cmipld.get('universal:units/graph.jsonld', depth=0)),
        'truncation_method': name_extract(cmipld.get('universal:truncation_method/graph.jsonld', depth=0)),
        'issue_kind': ['New', 'Modify']
    }
except ImportError:
    # Fallback hardcoded values
    DATA = {
        'grid_type': [
            'regular-latitude-longitude',
            'reduced-gaussian',
            'linear-spectral-gaussian',
            'tripolar',
            'cubed-sphere',
            'unstructured-polygon',
            'plane-projection'
        ],
        'grid_mapping': [
            'latitude-longitude',
            'rotated-latitude-longitude',
            'polar-stereographic',
            'lambert-conformal-conic'
        ],
        'region': [
            'global',
            'antarctica',
            'greenland',
            'limited-area'
        ],
        'temporal_refinement': [
            'static',
            'adaptive',
            'dynamically-stretched'
        ],
        'units': [
            'degree',
            'km',
            'meter'
        ],
        'truncation_method': [
            'triangular',
            'rhomboidal'
        ],
        'issue_kind': ['New', 'Modify']
    }
