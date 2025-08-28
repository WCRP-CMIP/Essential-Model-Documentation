#!/usr/bin/env python3
"""
Example Template: Simple Contact Form
Shows how to create a new template with minimal CV data
"""

class SimpleContactTemplate:
    """Example template configuration."""
    
    TEMPLATE_CONFIG = {
        'name': 'Simple Contact Form',
        'description': 'A simple example contact form template.',
        'title': '[Example] Contact Form',
        'labels': ['example', 'contact']
    }
    
    # Only include CV data that this template actually needs
    CV_DATA = {
        'contact_types': {
            'technical': {'id': 'technical', 'validation-key': 'technical'},
            'scientific': {'id': 'scientific', 'validation-key': 'scientific'},
            'administrative': {'id': 'administrative', 'validation-key': 'administrative'}
        },
        'priority_levels': ['Low', 'Medium', 'High', 'Urgent']
    }
    
    HARDCODED_OPTIONS = {
        'contact_method': ['Email', 'Phone', 'Video Call', 'In Person']
    }
    
    TEMPLATE_NOTES = """
    This is an example template showing:
    - How to define minimal CV data
    - How to use hardcoded options
    - Clean template structure
    """

TEMPLATE_INFO = SimpleContactTemplate.TEMPLATE_CONFIG
