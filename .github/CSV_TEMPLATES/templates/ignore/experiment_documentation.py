# Experiment Documentation Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Experiment Documentation',
    'description': 'Submit metadata for a CMIP7 experiment configuration.',
    'title': '[EMD] Experiment Documentation',
    'labels': ['emd-submission', 'experiment'],
    'issue_category': 'experiment'
}

import cmipld
from cmipld.utils.ldparse import *

# Data for this template
DATA = {
    'experiments': {
        # Note: experiments would come from CMIP7 CVs, not universal
        # Using fallback data since not in universal repo
        'piControl': {'id': 'piControl', 'validation-key': 'piControl'},
        'historical': {'id': 'historical', 'validation-key': 'historical'},
        'ssp126': {'id': 'ssp126', 'validation-key': 'ssp126'},
        'ssp245': {'id': 'ssp245', 'validation-key': 'ssp245'},
        'ssp585': {'id': 'ssp585', 'validation-key': 'ssp585'},
        '1pctCO2': {'id': '1pctCO2', 'validation-key': '1pctCO2'},
        'abrupt-4xCO2': {'id': 'abrupt-4xCO2', 'validation-key': 'abrupt-4xCO2'}
    },
    'activities': name_multikey_extract(
        cmipld.get('universal:activity/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    'source_types': name_multikey_extract(
        cmipld.get('universal:source-type/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    # Issue tracking fields
    'issue_category_options': ['experiment'],
    'issue_kind_options': ['new', 'modify']
}
