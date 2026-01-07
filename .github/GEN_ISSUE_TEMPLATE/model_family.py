#!/usr/bin/env python3
"""
Data definitions for model_family template.

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
    
    institution = get_cv_list('emd:institution') or []
    component = get_cv_list('emd:component') or [
        'aerosol', 'atmosphere', 'atmospheric-chemistry',
        'land-ice', 'land-surface', 'ocean',
        'ocean-biogeochemistry', 'sea-ice'
    ]

except ImportError:
    institution = []
    component = [
        'aerosol', 'atmosphere', 'atmospheric-chemistry',
        'land-ice', 'land-surface', 'ocean',
        'ocean-biogeochemistry', 'sea-ice'
    ]

# Try to generate prefill links for existing entries
try:
    from cmipld.generate.template_utils import get_existing_entries_markdown
    existing_entries = get_existing_entries_markdown('model_family')
    if not existing_entries:
        existing_entries = "_No existing model families registered yet._"
except:
    existing_entries = "_Prefill links unavailable - run from repository root._"

# Standard options
issue_kind = ['New', 'Modify']
family_type = ['Earth System Model', 'Component']

# Data dictionary for template substitution
DATA = {
    'institution': institution,
    'component': component,
    'family_type': family_type,
    'issue_kind': issue_kind,
    'existing_entries': existing_entries,
}
