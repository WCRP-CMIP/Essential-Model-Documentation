# Vertical Grid Properties Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Vertical Grid Properties Documentation',
    'description': 'Document vertical grid specifications as compound objects for EMD compliance.',
    'title': '[EMD] Vertical Grid Properties',
    'labels': ['emd-submission', 'vertical-grid'],
    'issue_category': 'vertical-grid'
}

import cmipld
from cmipld.utils.ldparse import *

# Data for this template
DATA = {
    'vertical_coordinates': {
        'no-vertical-grid': {'id': 'no-vertical-grid', 'validation-key': 'no-vertical-grid'},
        ** name_multikey_extract(
            cmipld.get('universal:native-vertical-grid-coordinate/graph.jsonld')['@graph'],
            ['id','validation-key','ui-label'],'validation-key'
        )
    },
    'vertical_units': name_multikey_extract(
        cmipld.get('universal:native-vertical-grid-units/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    # Issue tracking fields
    'issue_category_options': ['vertical-grid'],
    'issue_kind_options': ['new', 'modify']
}
