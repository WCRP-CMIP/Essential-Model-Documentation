# Grid Properties Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Grid Properties Documentation',
    'description': 'Document standardized grid specifications for model components.',
    'title': '[EMD] Grid Properties Documentation',
    'labels': ['emd-submission', 'grid'],
    'issue_category': 'grid'
}

import cmipld
from cmipld.utils.ldparse import *

# Data for this template
DATA = {
    'realms': name_multikey_extract(
        cmipld.get('universal:realm/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    'grid_descriptors': [
        # Using hardcoded list as grid-descriptor CV not in universal repo
        'N48', 'N96', 'N216', 'N512', 'N1280',
        'ORCA2', 'eORCA2', 'ORCA1', 'eORCA1', 
        'ORCA025', 'eORCA025', 'ORCA012', 'eORCA012',
        'T42', 'T63', 'T85', 'T106', 'T127', 'T255',
        'TL95', 'TL159', 'TL255', 'TL319', 'TL511', 'TL959', 'TL1279',
        'Tco199', 'Tco399', 'R30', 'C96'
    ],
    'horizontal_grid_types': {
        'no-horizontal-grid': {'id': 'no-horizontal-grid'},
        ** name_multikey_extract(
            cmipld.get('universal:native-horizontal-grid-type/graph.jsonld')['@graph'],
            ['id','validation-key','ui-label'],'validation-key'
        )
    },
    'grid_mappings': [
        # Using hardcoded list as grid-mapping CV not in universal repo
        'albers_conical_equal_area', 'azimuthal_equidistant', 'geostationary',
        'lambert_azimuthal_equal_area', 'lambert_conformal_conic', 'lambert_cylindrical_equal_area',
        'latitude_longitude', 'orthographic', 'polar_stereographic',
        'rotated_latitude_longitude', 'sinusoidal', 'stereographic',
        'transverse_mercator', 'vertical_perspective'
    ],
    'horizontal_regions': name_multikey_extract(
        cmipld.get('universal:native-horizontal-grid-region/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    'temporal_refinements': name_multikey_extract(
        cmipld.get('universal:native-horizontal-grid-temporal-refinement/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    'grid_arrangements': [
        # Using hardcoded list as arrangement CV not in universal repo
        'arakawa_A', 'arakawa_B', 'arakawa_C', 'arakawa_D', 'arakawa_E'
    ],
    'nominal_resolutions': name_multikey_extract(
        cmipld.get('universal:resolution/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    'vertical_coordinates': {
        'no-vertical-dimension': {'id': 'no-vertical-dimension'},
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
    'issue_category_options': ['grid'],
    'issue_kind_options': ['new', 'modify']
}
