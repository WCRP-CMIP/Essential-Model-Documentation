#!/usr/bin/env python3
"""
Data definitions for model_component template.

Provides dropdown options and dynamic content for template generation.

Note: This template creates both model_component and component_config entries.
It references grids from horizontal_computational_grid and vertical_computational_grid.
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
    
    component = get_cv_list('emd:component') or [
        'aerosol', 'atmosphere', 'atmospheric-chemistry',
        'land-ice', 'land-surface', 'ocean', 
        'ocean-biogeochemistry', 'sea-ice'
    ]
    component_family = get_cv_list('emd:component_family') or []

except ImportError:
    component = [
        'aerosol', 'atmosphere', 'atmospheric-chemistry',
        'land-ice', 'land-surface', 'ocean',
        'ocean-biogeochemistry', 'sea-ice'
    ]
    component_family = []

# Try to generate prefill links for existing entries
try:
    from cmipld.generate.template_utils import get_existing_entries_markdown
    existing_entries = get_existing_entries_markdown('model_component')
    if not existing_entries:
        existing_entries = "_No existing components registered yet._"
except:
    existing_entries = "_Prefill links unavailable - run from repository root._"

# Standard options
issue_kind = ['New', 'Modify']

# Data dictionary for template substitution
DATA = {
    'component': component,
    'component_family': component_family,
    'issue_kind': issue_kind,
    'existing_entries': existing_entries,
}
