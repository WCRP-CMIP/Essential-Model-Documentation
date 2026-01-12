# Model Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Model',
    'description': 'Register a top-level Earth system model for EMD/CMIP7',
    'title': 'Add/Modify: Model: <Type model name here>',
    'labels': ['emd-submission', 'model', 'Review'],
    'issue_category': 'model'
}

# Reserved words that cannot be used in GitHub issue template options
GITHUB_RESERVED_WORDS = ['None', 'none', 'True', 'true', 'False', 'false']

def filter_reserved_words(items):
    """Replace reserved words with safe alternatives."""
    result = []
    for item in items:
        if item in GITHUB_RESERVED_WORDS:
            # Replace 'none' with 'no-calendar' for calendar options
            if item.lower() == 'none':
                result.append('no-calendar')
            else:
                result.append(f'{item}-value')
        else:
            result.append(item)
    return result

# Try to load from cmipld if available, otherwise use hardcoded values
try:
    import cmipld
    from cmipld.utils.ldparse import name_extract

    DATA = {
        'component': name_extract(cmipld.get('universal:scientific_domain/graph.jsonld', depth=0)),
        'calendar': filter_reserved_words(name_extract(cmipld.get('universal:calendar/graph.jsonld', depth=0))),
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
            'no-calendar'
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
