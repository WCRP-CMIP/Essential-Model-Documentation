# Vertical Computational Grid Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Vertical Computational Grid',
    'description': 'Register a vertical computational grid',
    'title': 'Add/Modify: Vertical Computational Grid: <Type grid ID here>',
    'labels': ['emd-submission', 'vertical-grid', 'Review'],
    'issue_category': 'vertical_computational_grid'
}

# Try to load from cmipld if available, otherwise use hardcoded values
try:
    import cmipld
    from cmipld.utils.ldparse import name_extract

    DATA = {
        'vertical_coordinate': name_extract(cmipld.get('universal:vertical_coordinate/graph.jsonld', depth=0)),
        'issue_kind': ['New', 'Modify']
    }
except ImportError:
    # Fallback hardcoded values
    DATA = {
        'vertical_coordinate': [
            'atmosphere-hybrid-height-coordinate',
            'atmosphere-hybrid-sigma-pressure-coordinate',
            'atmosphere-sigma-coordinate',
            'depth',
            'height',
            'land-ice-sigma-coordinate',
            'ocean-s-coordinate',
            'ocean-sigma-z-coordinate'
        ],
        'issue_kind': ['New', 'Modify']
    }
