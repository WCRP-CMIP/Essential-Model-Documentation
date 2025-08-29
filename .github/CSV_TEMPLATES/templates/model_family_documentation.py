# Model Family Documentation Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Model Family Documentation',
    'description': 'Document a model family that encompasses multiple model configurations and components.',
    'title': '[EMD] Model Family Documentation',
    'labels': ['emd-submission', 'model_family'],
    'issue_category': 'model_family'
}

import cmipld
from cmipld.utils.ldparse import *

# Data for this template
DATA = {
    'licenses': name_multikey_extract(
        cmipld.get('universal:license/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    # Hardcoded options for family_type field
    'family_type_options': [
        'Model Family (complete Earth system models)',
        'Component Family (individual model components)'
    ],
    # Issue tracking fields
    'issue_category_options': ['model_family'],
    'issue_kind_options': ['new', 'modify']
}
