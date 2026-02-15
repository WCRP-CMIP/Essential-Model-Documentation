#!/usr/bin/env python3
"""
Data definitions for model template.

Provides dropdown options and dynamic content for template generation.

Note: This template references model_family and component_config from other folders.
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
    
    model_family = get_cv_list('emd:model_family') or []
    component = get_cv_list('emd:component') or [
        'aerosol', 'atmosphere', 'atmospheric-chemistry',
        'land-ice', 'land-surface', 'ocean',
        'ocean-biogeochemistry', 'sea-ice'
    ]
    calendar = get_cv_list('emd:calendar') or [
        'standard', 'proleptic-gregorian', '365-day', '360-day'
    ]

except ImportError:
    model_family = []
    component = [
        'aerosol', 'atmosphere', 'atmospheric-chemistry',
        'land-ice', 'land-surface', 'ocean',
        'ocean-biogeochemistry', 'sea-ice'
    ]
    calendar = ['standard', 'proleptic-gregorian', '365-day', '360-day']

# Try to generate prefill links for existing entries
try:
    from cmipld.generate.template_utils import get_existing_entries_markdown
    existing_entries = get_existing_entries_markdown('model')
    if not existing_entries:
        existing_entries = "_No existing models registered yet._"
except:
    existing_entries = "_Prefill links unavailable - run from repository root._"

# Standard options
issue_kind = ['New', 'Modify']

# Data dictionary for template substitution
DATA = {
    'model_family': model_family,
    'component': component,
    'calendar': calendar,
    'issue_kind': issue_kind,
    'existing_entries': existing_entries,
}
