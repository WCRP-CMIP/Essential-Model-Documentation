#!/usr/bin/env python3
"""
Model Family Documentation Template Configuration
"""

class ModelFamilyDocumentationTemplate:
    """Template configuration for model family documentation forms."""
    
    TEMPLATE_CONFIG = {
        'name': 'Model Family Documentation',
        'description': 'Document a model family that encompasses multiple model configurations and components.',
        'title': '[EMD] Model Family Documentation',
        'labels': ['emd-submission', 'model_family']
    }
    
    CV_DATA = {
        'licenses': {
            'CC0-1.0': {'id': 'CC0-1.0', 'validation-key': 'CC0-1.0'},
            'CC-BY-4.0': {'id': 'CC-BY-4.0', 'validation-key': 'CC-BY-4.0'},
            'MIT': {'id': 'MIT', 'validation-key': 'MIT'},
            'GPL-3.0': {'id': 'GPL-3.0', 'validation-key': 'GPL-3.0'},
            'Apache-2.0': {'id': 'Apache-2.0', 'validation-key': 'Apache-2.0'}
        }
    }
    
    # Custom hardcoded options for specific fields
    HARDCODED_OPTIONS = {
        'family_type': [
            'Model Family (complete Earth system models)',
            'Component Family (individual model components)'
        ]
    }
    
    TEMPLATE_NOTES = """
    This template documents model families that share code bases but may differ in:
    - Resolution configurations
    - Parameter choices  
    - Component inclusion
    - Scientific enhancements
    """

TEMPLATE_INFO = ModelFamilyDocumentationTemplate.TEMPLATE_CONFIG
