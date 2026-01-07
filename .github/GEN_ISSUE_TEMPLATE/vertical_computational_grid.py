#!/usr/bin/env python3
"""
Data definitions for vertical_computational_grid template.

Provides dropdown options and dynamic content for template generation.
"""

# Try to fetch from controlled vocabularies
try:
    import cmipld
    
    def get_cv_list(url, key='id'):
        """Fetch controlled vocabulary list from JSON-LD."""
        try:
            data = cmipld.get(url, depth=1)
            if isinstance(data, dict) and '@graph' in data:
                items = data['@graph']
            elif isinstance(data, list):
                items = data
            else:
                return []
            return [item.get(key, '').split('/')[-1] for item in items if item.get(key)]
        except:
            return []
    
    vertical_coordinate = get_cv_list('emd:vertical_coordinate') or [
        'atmosphere-hybrid-height-coordinate',
        'atmosphere-hybrid-sigma-pressure-coordinate',
        'atmosphere-sigma-coordinate',
        'depth',
        'height',
        'land-ice-sigma-coordinate',
        'ocean-s-coordinate',
        'ocean-sigma-coordinate',
        'ocean-sigma-z-coordinate'
    ]

except ImportError:
    vertical_coordinate = [
        'atmosphere-hybrid-height-coordinate',
        'atmosphere-hybrid-sigma-pressure-coordinate',
        'atmosphere-sigma-coordinate',
        'depth',
        'height',
        'land-ice-sigma-coordinate',
        'ocean-s-coordinate',
        'ocean-sigma-coordinate',
        'ocean-sigma-z-coordinate'
    ]

# Try to generate prefill links for existing entries
try:
    from cmipld.generate.template_utils import get_existing_entries_markdown
    existing_entries = get_existing_entries_markdown('vertical_computational_grid')
    if not existing_entries:
        existing_entries = "_No existing vertical grids registered yet._"
except:
    existing_entries = "_Prefill links unavailable - run from repository root._"

# Standard options
issue_kind = ['New', 'Modify']

# Data dictionary for template substitution
DATA = {
    'vertical_coordinate': vertical_coordinate,
    'issue_kind': issue_kind,
    'existing_entries': existing_entries,
}
