# Experiment Documentation Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Experiment Documentation',
    'description': 'Submit metadata for a CMIP7 experiment configuration.',
    'title': '[EMD] Experiment Documentation',
    'labels': ['emd-submission', 'experiment'],
    'issue_category': 'experiment'
}

# Data for this template
DATA = {
    'experiments': {
        'piControl': {'id': 'piControl', 'validation-key': 'piControl'},
        'historical': {'id': 'historical', 'validation-key': 'historical'},
        'ssp126': {'id': 'ssp126', 'validation-key': 'ssp126'},
        'ssp245': {'id': 'ssp245', 'validation-key': 'ssp245'},
        'ssp585': {'id': 'ssp585', 'validation-key': 'ssp585'},
        '1pctCO2': {'id': '1pctCO2', 'validation-key': '1pctCO2'},
        'abrupt-4xCO2': {'id': 'abrupt-4xCO2', 'validation-key': 'abrupt-4xCO2'}
    },
    'activities': {
        'CMIP': {'id': 'CMIP', 'validation-key': 'CMIP'},
        'ScenarioMIP': {'id': 'ScenarioMIP', 'validation-key': 'ScenarioMIP'},
        'DAMIP': {'id': 'DAMIP', 'validation-key': 'DAMIP'},
        'AerChemMIP': {'id': 'AerChemMIP', 'validation-key': 'AerChemMIP'},
        'C4MIP': {'id': 'C4MIP', 'validation-key': 'C4MIP'},
        'DCPP': {'id': 'DCPP', 'validation-key': 'DCPP'}
    },
    'source_types': {
        'AOGCM': {'id': 'AOGCM', 'validation-key': 'AOGCM'},
        'AGCM': {'id': 'AGCM', 'validation-key': 'AGCM'},
        'OGCM': {'id': 'OGCM', 'validation-key': 'OGCM'},
        'ESM': {'id': 'ESM', 'validation-key': 'ESM'},
        'BGCM': {'id': 'BGCM', 'validation-key': 'BGCM'},
        'AER': {'id': 'AER', 'validation-key': 'AER'},
        'CHEM': {'id': 'CHEM', 'validation-key': 'CHEM'}
    },
    # Issue tracking fields
    'issue_category_options': ['experiment'],
    'issue_kind_options': ['new', 'modify']
}
