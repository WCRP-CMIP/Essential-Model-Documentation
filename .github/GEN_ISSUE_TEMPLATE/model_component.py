# Model Component Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Model Component',
    'description': 'Register a model component (atmosphere, ocean, etc.) for EMD',
    'title': 'Add/Modify: Model Component: <Type component name here>',
    'labels': ['emd-submission', 'model-component', 'Review'],
    'issue_category': 'model_component'
}

# Try to load from cmipld if available, otherwise use hardcoded values
try:
    import cmipld
    from cmipld.utils.ldparse import name_extract

    DATA = {
        'component': name_extract(cmipld.get('universal:scientific_domain/graph.jsonld', depth=0)),
        'embedded_in': name_extract(cmipld.get('universal:scientific_domain/graph.jsonld', depth=0)),
        'component_family': name_extract(cmipld.get('emd:model_family/graph.jsonld', depth=0)),
        'issue_kind': ['New', 'Modify']
    }
except ImportError:
    # Fallback hardcoded values
    DATA = {
        'component': [
            'aerosol',
            'atmosphere',
            'atmospheric-chemistry',
            'land-surface',
            'land-ice',
            'ocean',
            'ocean-biogeochemistry',
            'sea-ice'
        ],
        'embedded_in': [
            'aerosol',
            'atmosphere',
            'atmospheric-chemistry',
            'land-surface',
            'land-ice',
            'ocean',
            'ocean-biogeochemistry',
            'sea-ice'
        ],
        'component_family': [
            'arpege-climat',
            'bisicles',
            'cam',
            'cice',
            'clm',
            'gelato',
            'jules',
            'lim',
            'mom',
            'nemo',
            'pisces',
            'pop',
            'surfex'
        ],
        'issue_kind': ['New', 'Modify']
    }
