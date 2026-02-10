# Horizontal Computational Grid Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Horizontal Computational Grid',
    'description': 'Register a horizontal computational grid',
    'title': 'Add/Modify: Horizontal Computational Grid: <Type grid ID here>',
    'labels': ['emd-submission', 'horizontal-grid', 'Review'],
    'issue_category': 'horizontal_computational_grid'
}

# Try to load from cmipld if available, otherwise use hardcoded values
try:
    import cmipld
    from cmipld.utils.ldparse import name_extract

    DATA = {
        'arrangement': name_extract(cmipld.get('universal:arrangement/graph.jsonld', depth=0)),
        'issue_kind': ['New', 'Modify']
    }
except ImportError:
    # Fallback hardcoded values
    DATA = {
        'arrangement': [
            'arakawa-a',
            'arakawa-b',
            'arakawa-c',
            'arakawa-d',
            'arakawa-e'
        ],
        'issue_kind': ['New', 'Modify']
    }
