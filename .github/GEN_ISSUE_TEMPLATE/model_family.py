# Model Family Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Model Family',
    'description': 'Register a model family (group of related models)',
    'title': 'Add/Modify: Model Family: <Type family name here>',
    'labels': ['emd-submission', 'model-family', 'Review'],
    'issue_category': 'model_family'
}

# Try to load from cmipld if available, otherwise use hardcoded values
try:
    import cmipld
    from cmipld.utils.ldparse import name_extract

    DATA = {
        'component': name_extract(cmipld.get('universal:scientific_domain/graph.jsonld', depth=0)),
        'institution': name_extract(cmipld.get('universal:organisation/graph.jsonld', depth=0)),
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
        'institution': [
            'awi',
            'bcc',
            'cccma',
            'cmcc',
            'cnrm-cerfacs',
            'csiro',
            'dkrz',
            'ec-earth-consortium',
            'gfdl',
            'inpe',
            'ipsl',
            'miroc',
            'mohc',
            'mpi-m',
            'nasa-giss',
            'ncar',
            'ncc',
            'nerc',
            'niwa',
            'noaa-gfdl'
        ],
        'issue_kind': ['New', 'Modify']
    }
