#!/usr/bin/env python3
"""
Data definitions for general_issue template.

Provides dropdown options for template generation.
This template has no dynamic prefill content.
"""

# Static options - no CVs needed
issue_type = [
    'Bug Report',
    'Feature Request', 
    'Question',
    'Documentation Issue',
    'Data Quality Issue'
]

affected_areas = [
    'Grid Registration',
    'Component Registration',
    'Model Registration',
    'Model Family',
    'Documentation',
    'Issue Templates',
    'Workflows'
]

priority = ['Low', 'Medium', 'High', 'Critical']

# Data dictionary for template substitution
DATA = {
    'issue_type': issue_type,
    'affected_areas': affected_areas,
    'priority': priority,
}
