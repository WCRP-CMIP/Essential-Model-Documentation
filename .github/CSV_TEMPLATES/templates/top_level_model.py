# Top Level Model Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Top Level Model Submission',
    'description': 'Submit metadata for the top-level model properties as specified in the EMD specification.',
    'title': '[EMD] Top Level Model Submission',
    'labels': ['emd-submission', 'top_level_model']
}

# Data for this template - model-level CV data
DATA = {
    'realms': {
        'aerosol': {'id': 'aerosol', 'validation-key': 'aerosol'},
        'atmosphere': {'id': 'atmosphere', 'validation-key': 'atmosphere'},
        'atmospheric chemistry': {'id': 'atmospheric chemistry', 'validation-key': 'atmospheric chemistry'},
        'land surface': {'id': 'land surface', 'validation-key': 'land surface'},
        'land ice': {'id': 'land ice', 'validation-key': 'land ice'},
        'ocean': {'id': 'ocean', 'validation-key': 'ocean'},
        'ocean biogeochemistry': {'id': 'ocean biogeochemistry', 'validation-key': 'ocean biogeochemistry'},
        'sea ice': {'id': 'sea ice', 'validation-key': 'sea ice'}
    },
    'calendars': {
        'standard': {'id': 'standard', 'validation-key': 'standard'},
        'proleptic_gregorian': {'id': 'proleptic_gregorian', 'validation-key': 'proleptic_gregorian'},
        'julian': {'id': 'julian', 'validation-key': 'julian'},
        'utc': {'id': 'utc', 'validation-key': 'utc'},
        'tai': {'id': 'tai', 'validation-key': 'tai'},
        '360_day': {'id': '360_day', 'validation-key': '360_day'},
        '365_day': {'id': '365_day', 'validation-key': '365_day'},
        '366_day': {'id': '366_day', 'validation-key': '366_day'},
        'none': {'id': 'none', 'validation-key': 'none'}
    }
}
