#!/usr/bin/env python3
"""
Component Submission Template Configuration
"""

class ComponentSubmissionTemplate:
    """Template configuration for component submission forms."""
    
    # Header information for the GitHub issue template
    TEMPLATE_CONFIG = {
        'name': 'Model Component Submission',
        'description': 'Submit metadata for a model component as specified in the EMD specification.',
        'title': '[EMD] Model Component Submission',
        'labels': ['emd-submission', 'component']
    }
    
    # CV data needed for this template
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
        'grid_descriptors': [
            'N48', 'N96', 'N216', 'N512', 'N1280',
            'ORCA2', 'eORCA2', 'ORCA1', 'eORCA1', 
            'ORCA025', 'eORCA025', 'ORCA012', 'eORCA012',
            'T42', 'T63', 'T85', 'T106', 'T127', 'T255'
        ]
    }
    
    # Additional template-specific configurations
    TEMPLATE_NOTES = """
    This template captures essential information about model components including:
    - Component identification and family
    - Scientific description
    - Technical implementation details
    - Grid specifications
    - References and documentation
    """

# For backward compatibility, also export as dict
TEMPLATE_INFO = ComponentSubmissionTemplate.TEMPLATE_CONFIG
