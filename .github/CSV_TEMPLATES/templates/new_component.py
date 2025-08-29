# Component Submission Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Model Component Submission',
    'description': 'Submit metadata for a model component as specified in the EMD specification.',
    'title': '[EMD] Model Component Submission',
    'labels': ['emd-submission', 'component'],
    'issue_category': 'component'
}

import cmipld
from cmipld.utils.ldparse import *



# Data for this template - includes all CV data needed for component documentation
DATA = {
    'realms': name_multikey_extract(
            cmipld.get('universal:realm/graph.jsonld')['@graph'],
            ['id','validation-key','ui-label'],'validation-key'
    ),
    
    'grid_descriptors': [
        'N48', 'N96', 'N216', 'N512', 'N1280',
        'ORCA2', 'eORCA2', 'ORCA1', 'eORCA1', 
        'ORCA025', 'eORCA025', 'ORCA012', 'eORCA012',
        'T42', 'T63', 'T85', 'T106', 'T127', 'T255',
        'TL95', 'TL159', 'TL255', 'TL319', 'TL511', 'TL959', 'TL1279',
        'Tco199', 'Tco399', 'R30', 'C96'
    ],
    'horizontal_grid_types': {
        'regular_latitude_longitude': {'id': 'regular_latitude_longitude', 'validation-key': 'regular_latitude_longitude'},
        'regular_gaussian': {'id': 'regular_gaussian', 'validation-key': 'regular_gaussian'},
        'reduced_gaussian': {'id': 'reduced_gaussian', 'validation-key': 'reduced_gaussian'},
        'spectral_gaussian': {'id': 'spectral_gaussian', 'validation-key': 'spectral_gaussian'},
        'spectral_reduced_gaussian': {'id': 'spectral_reduced_gaussian', 'validation-key': 'spectral_reduced_gaussian'},
        'linear_spectral_gaussian': {'id': 'linear_spectral_gaussian', 'validation-key': 'linear_spectral_gaussian'},
        'quadratic_spectral_gaussian': {'id': 'quadratic_spectral_gaussian', 'validation-key': 'quadratic_spectral_gaussian'},
        'cubic_octahedral_spectral_reduced_gaussian': {'id': 'cubic_octahedral_spectral_reduced_gaussian', 'validation-key': 'cubic_octahedral_spectral_reduced_gaussian'},
        'rotated_pole': {'id': 'rotated_pole', 'validation-key': 'rotated_pole'},
        'stretched': {'id': 'stretched', 'validation-key': 'stretched'},
        'displaced_pole': {'id': 'displaced_pole', 'validation-key': 'displaced_pole'},
        'tripolar': {'id': 'tripolar', 'validation-key': 'tripolar'},
        'cubed_sphere': {'id': 'cubed_sphere', 'validation-key': 'cubed_sphere'},
        'icosahedral_geodesic': {'id': 'icosahedral_geodesic', 'validation-key': 'icosahedral_geodesic'},
        'icosahedral_geodesic_dual': {'id': 'icosahedral_geodesic_dual', 'validation-key': 'icosahedral_geodesic_dual'},
        'yin_yang': {'id': 'yin_yang', 'validation-key': 'yin_yang'},
        'unstructured_triangular': {'id': 'unstructured_triangular', 'validation-key': 'unstructured_triangular'},
        'unstructured_polygonal': {'id': 'unstructured_polygonal', 'validation-key': 'unstructured_polygonal'},
        'plane_projection': {'id': 'plane_projection', 'validation-key': 'plane_projection'},
        'not-applicable': {'id': 'not-applicable', 'validation-key': 'not-applicable'}
    },
    'grid_mappings': [
        'albers_conical_equal_area', 'azimuthal_equidistant', 'geostationary',
        'lambert_azimuthal_equal_area', 'lambert_conformal_conic', 'lambert_cylindrical_equal_area',
        'latitude_longitude', 'orthographic', 'polar_stereographic',
        'rotated_latitude_longitude', 'sinusoidal', 'stereographic',
        'transverse_mercator', 'vertical_perspective'
    ],
    'horizontal_regions': {
        'global': {'id': 'global', 'validation-key': 'global'},
        'global_land': {'id': 'global_land', 'validation-key': 'global_land'},
        'global_ocean': {'id': 'global_ocean', 'validation-key': 'global_ocean'},
        'antarctica': {'id': 'antarctica', 'validation-key': 'antarctica'},
        'greenland': {'id': 'greenland', 'validation-key': 'greenland'},
        'limited_area': {'id': 'limited_area', 'validation-key': 'limited_area'}
    },
    'temporal_refinements': {
        'static': {'id': 'static', 'validation-key': 'static'},
        'dynamically_stretched': {'id': 'dynamically_stretched', 'validation-key': 'dynamically_stretched'},
        'adaptive': {'id': 'adaptive', 'validation-key': 'adaptive'}
    },
    'grid_arrangements': ['arakawa_A', 'arakawa_B', 'arakawa_C', 'arakawa_D', 'arakawa_E'],
    'truncation_methods': ['triangular', 'rhomboidal'],
    'nominal_resolutions': [
        '0.5 km', '1 km', '2.5 km', '5 km', '10 km', '25 km', '50 km',
        '100 km', '250 km', '500 km', '1000 km', '2500 km', '5000 km', '10000 km'
    ],
    'vertical_coordinates': {
        'no-vertical-grid': {'id': 'no-vertical-grid', 'validation-key': 'no-vertical-grid'},
        'height': {'id': 'height', 'validation-key': 'height'},
        'geopotential_height': {'id': 'geopotential_height', 'validation-key': 'geopotential_height'},
        'air_pressure': {'id': 'air_pressure', 'validation-key': 'air_pressure'},
        'air_potential_temperature': {'id': 'air_potential_temperature', 'validation-key': 'air_potential_temperature'},
        'atmosphere_ln_pressure_coordinate': {'id': 'atmosphere_ln_pressure_coordinate', 'validation-key': 'atmosphere_ln_pressure_coordinate'},
        'atmosphere_sigma_coordinate': {'id': 'atmosphere_sigma_coordinate', 'validation-key': 'atmosphere_sigma_coordinate'},
        'atmosphere_hybrid_sigma_pressure_coordinate': {'id': 'atmosphere_hybrid_sigma_pressure_coordinate', 'validation-key': 'atmosphere_hybrid_sigma_pressure_coordinate'},
        'atmosphere_hybrid_height_coordinate': {'id': 'atmosphere_hybrid_height_coordinate', 'validation-key': 'atmosphere_hybrid_height_coordinate'},
        'atmosphere_sleve_coordinate': {'id': 'atmosphere_sleve_coordinate', 'validation-key': 'atmosphere_sleve_coordinate'},
        'depth': {'id': 'depth', 'validation-key': 'depth'},
        'sea_water_pressure': {'id': 'sea_water_pressure', 'validation-key': 'sea_water_pressure'},
        'sea_water_potential_temperature': {'id': 'sea_water_potential_temperature', 'validation-key': 'sea_water_potential_temperature'},
        'ocean_sigma_coordinate': {'id': 'ocean_sigma_coordinate', 'validation-key': 'ocean_sigma_coordinate'},
        'ocean_s_coordinate': {'id': 'ocean_s_coordinate', 'validation-key': 'ocean_s_coordinate'},
        'ocean_s_coordinate_g1': {'id': 'ocean_s_coordinate_g1', 'validation-key': 'ocean_s_coordinate_g1'},
        'ocean_s_coordinate_g2': {'id': 'ocean_s_coordinate_g2', 'validation-key': 'ocean_s_coordinate_g2'},
        'ocean_sigma_z_coordinate': {'id': 'ocean_sigma_z_coordinate', 'validation-key': 'ocean_sigma_z_coordinate'},
        'ocean_double_sigma_coordinate': {'id': 'ocean_double_sigma_coordinate', 'validation-key': 'ocean_double_sigma_coordinate'},
        'land_ice_sigma_coordinate': {'id': 'land_ice_sigma_coordinate', 'validation-key': 'land_ice_sigma_coordinate'},
        'z*': {'id': 'z*', 'validation-key': 'z*'}
    },
    'vertical_units': {
        'm': {'id': 'm'},
        'Pa': {'id': 'Pa'},
        'K': {'id': 'K'}
    },
    # Issue tracking fields
    'issue_category_options': ['component'],
    'issue_kind_options': ['new', 'modify']
}