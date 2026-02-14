#!/usr/bin/env python3
"""
Data definitions for horizontal_computational_grid template.

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
    
    arrangement = get_cv_list('emd:arrangement') or [
        'arakawa-a', 'arakawa-b', 'arakawa-c', 'arakawa-d', 'arakawa-e', 'unstaggered'
    ]

except ImportError:
    arrangement = [
        'arakawa-a', 'arakawa-b', 'arakawa-c', 'arakawa-d', 'arakawa-e', 'unstaggered'
    ]

# Try to generate prefill links for existing entries
try:
    from cmipld.generate.template_utils import get_existing_entries_markdown
    existing_entries = get_existing_entries_markdown('horizontal_computational_grid')
    if not existing_entries:
        existing_entries = "_No existing computational grids registered yet._"
except:
    existing_entries = "_Prefill links unavailable - run from repository root._"

# Standard options
issue_kind = ['New', 'Modify']

# Data dictionary for template substitution
DATA = {
    'arrangement': arrangement,
    'issue_kind': issue_kind,
    'existing_entries': existing_entries,
}
