# Model Family Documentation Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Model Family Documentation',
    'description': 'Document a model family that encompasses multiple model configurations and components.',
    'title': '[EMD] Model Family Documentation',
    'labels': ['emd-submission', 'model_family'],
    'issue_category': 'model_family'
}

# Data for this template
DATA = {
    'licenses': {
        'CC0-1.0': {'id': 'CC0-1.0', 'validation-key': 'CC0-1.0'},
        'CC-BY-4.0': {'id': 'CC-BY-4.0', 'validation-key': 'CC-BY-4.0'},
        'MIT': {'id': 'MIT', 'validation-key': 'MIT'},
        'GPL-3.0': {'id': 'GPL-3.0', 'validation-key': 'GPL-3.0'},
        'Apache-2.0': {'id': 'Apache-2.0', 'validation-key': 'Apache-2.0'}
    },
    # Hardcoded options for family_type field
    'family_type_options': [
        'Model Family (complete Earth system models)',
        'Component Family (individual model components)'
    ],
    # Issue tracking fields
    'issue_category_options': ['model_family'],
    'issue_kind_options': ['new', 'modify']
}
