# Top Level Model Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Top Level Model Submission',
    'description': 'Submit metadata for the top-level model properties as specified in the EMD specification.',
    'title': '[EMD] Top Level Model Submission',
    'labels': ['emd-submission', 'top_level_model'],
    'issue_category': 'top_level_model'
}

import cmipld
from cmipld.utils.ldparse import *

# Data for this template - model-level CV data
DATA = {
    'realms': name_multikey_extract(
        cmipld.get('universal:realm/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    'calendars': {
        'no-calendar': {'id': 'no-calendar', 'validation-key': 'no-calendar'},
        ** name_multikey_extract(
            cmipld.get('universal:model-calendar/graph.jsonld')['@graph'],
            ['id','validation-key','ui-label'],'validation-key'
        )
    },
    # Issue tracking fields
    'issue_category_options': ['top_level_model'],
    'issue_kind_options': ['new', 'modify']
}
