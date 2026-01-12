# General Issue Template Configuration

TEMPLATE_CONFIG = {
    'name': 'General Issue',
    'description': 'Report a general issue, bug, or request',
    'title': 'Issue: <Brief description here>',
    'labels': ['emd', 'general'],
    'issue_category': 'general'
}

# Data for this template
DATA = {
    'issue_type_options': [
        'Bug Report',
        'Feature Request',
        'Documentation Issue',
        'CV Term Request',
        'Process Improvement',
        'Question',
        'Other'
    ],
    'affected_areas_options': [
        'Model Registration',
        'Model Component Registration',
        'Model Family Registration',
        'Grid Definitions',
        'References',
        'Documentation',
        'GitHub Actions/Workflows',
        'Issue Templates',
        'Validation Scripts',
        'General Repository Structure',
        'All/Multiple Areas'
    ],
    'priority_options': [
        'Critical - Blocking work',
        'High - Important issue',
        'Medium - Should be addressed',
        'Low - Nice to fix'
    ],
    'help_needed_options': [
        'I can work on this myself',
        'I need help implementing a solution',
        "I'm just reporting this issue"
    ]
}
