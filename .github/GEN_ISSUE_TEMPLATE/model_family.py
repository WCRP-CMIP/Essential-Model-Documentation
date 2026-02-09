# Model Family Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Model Family Registration',
    'description': 'Register a model family for genealogy tracking',
    'title': '[EMD] Model Family:',
    'labels': ['emd-submission', 'family', 'Review'],
    'issue_category': 'model_family'
}

# Hardcoded data
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
        'csiro-arccss',
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
        'noaa-gfdl',
        'ukmo'
    ],
    'issue_kind': ['New', 'Modify']
}
