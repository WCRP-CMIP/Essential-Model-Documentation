#!/usr/bin/env python3
"""
Top Level Model Template Configuration
"""

class TopLevelModelTemplate:
    """Template configuration for top-level model submission forms."""
    
    TEMPLATE_CONFIG = {
        'name': 'Top Level Model Submission',
        'description': 'Submit metadata for the top-level model properties as specified in the EMD specification.',
        'title': '[EMD] Top Level Model Submission',
        'labels': ['emd-submission', 'top_level_model']
    }
    
    CV_DATA = {
        'realms': {
            'atmos': {'id': 'atmos', 'validation-key': 'atmos'},
            'ocean': {'id': 'ocean', 'validation-key': 'ocean'},
            'land': {'id': 'land', 'validation-key': 'land'},
            'seaice': {'id': 'seaice', 'validation-key': 'seaice'},
            'ocnbgchem': {'id': 'ocnbgchem', 'validation-key': 'ocnbgchem'},
            'landice': {'id': 'landice', 'validation-key': 'landice'},
            'aerosol': {'id': 'aerosol', 'validation-key': 'aerosol'},
            'atmoschem': {'id': 'atmoschem', 'validation-key': 'atmoschem'}
        },
        'calendars': {
            'gregorian': {'id': 'gregorian', 'validation-key': 'gregorian'},
            'noleap': {'id': 'noleap', 'validation-key': 'noleap'},
            '360_day': {'id': '360_day', 'validation-key': '360_day'},
            'julian': {'id': 'julian', 'validation-key': 'julian'}
        }
    }
    
    TEMPLATE_NOTES = """
    This template captures essential information about complete climate models including:
    - Model identification and family
    - Component processes
    - Scientific overview
    - Calendar specifications
    - Release information and references
    """

TEMPLATE_INFO = TopLevelModelTemplate.TEMPLATE_CONFIG
