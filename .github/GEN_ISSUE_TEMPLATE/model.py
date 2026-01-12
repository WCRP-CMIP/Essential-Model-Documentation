# Model Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Model',
    'description': 'Register a top-level Earth system model for EMD/CMIP7',
    'title': 'Add/Modify: Model: <Type model name here>',
    'labels': ['emd-submission', 'model', 'Review'],
    'issue_category': 'model'
}

# Try to load from cmipld if available, otherwise use hardcoded values
try:
    import cmipld
    from cmipld.utils.ldparse import name_extract

    DATA = {
        'component': name_extract(cmipld.get('universal:scientific_domain/graph.jsonld', depth=0)),
        'calendar': name_extract(cmipld.get('universal:calendar/graph.jsonld', depth=0)),
        'model_family': name_extract(cmipld.get('emd:model_family/graph.jsonld', depth=0)),
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
        'calendar': [
            'proleptic-gregorian',
            'standard',
            'julian',
            '360-day',
            '365-day',
            '366-day',
            'utc',
            'tai',
            'none'
        ],
        'model_family': [
            'access',
            'arpege-climat',
            'bcc-csm',
            'cam',
            'cesm',
            'cnrm-cm',
            'cnrm-esm',
            'ec-earth',
            'gfdl',
            'hadgem3',
            'ipsl-cm',
            'miroc',
            'mpi-esm',
            'noresm',
            'ukesm'
        ],
        'issue_kind': ['New', 'Modify']
    }
