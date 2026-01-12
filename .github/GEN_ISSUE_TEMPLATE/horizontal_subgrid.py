# Horizontal Subgrid Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Horizontal Subgrid',
    'description': 'Register a horizontal subgrid',
    'title': 'Add/Modify: Horizontal Subgrid: <Type subgrid ID here>',
    'labels': ['emd-submission', 'horizontal-grid', 'Review'],
    'issue_category': 'horizontal_subgrid'
}

# Try to load from cmipld if available, otherwise use hardcoded values
try:
    import cmipld
    from cmipld.utils.ldparse import name_extract

    DATA = {
        'cell_variable_type': name_extract(cmipld.get('universal:cell_variable_type/graph.jsonld', depth=0)),
        'issue_kind': ['New', 'Modify']
    }
except ImportError:
    # Fallback hardcoded values
    DATA = {
        'cell_variable_type': [
            'mass',
            'x-velocity',
            'y-velocity',
            'velocity'
        ],
        'issue_kind': ['New', 'Modify']
    }
