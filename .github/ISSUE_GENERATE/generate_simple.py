#!/usr/bin/env python3
"""
Simple template generator that loads CMIP7_CVs and WCRP-universe data to populate Jinja2 templates.
"""

import json
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

import cmipld

def load(prefix,loc):
    try:
        return cmipld.get(f"{prefix}:{loc}/graph.jsonld", depth=0)['@graph']
    except Exception as e:
        print(f"Error loading {prefix}:{loc} - {e}")
        return f'FAILED: {prefix} loc'

data = {}

data['experiments'] = load("cmip7","experiment")
data['activities'] = load("universal","activity")
data['realms'] = load("universal","realm")
data['institutions'] = load("universal","organisation")
data['licenses'] = load("universal","license")
data['source_types'] = load("universal","source-type")     
data['horizontal_grid_types'] = load("universal","native-horizontal-grid-type")
data['horizontal_regions'] = load("universal","native-horizontal-grid-region")
data['temporal_refinements'] = load("universal","native-horizontal-grid-temporal-refinement")
data['vertical_coordinates'] = load("universal","native-vertical-grid-coordinate")
data['vertical_units'] = load("universal","native-vertical-grid-units")
data['calendars'] = load("universal","model-calendar")
data['nominal_resolutions'] = load("universal","nominal-resolution")
data['grid_descriptors'] = load("universal","grid-descriptor")
data['grid_mappings'] = load("universal","grid-mapping")
data['grid_arrangements'] = load("universal","grid-arrangement")
data['truncation_methods'] = load("universal","truncation-method")
data['scientific_domains'] = load("universal","scientific-domain")
data['typical_applications'] = load("universal","typical-application")


'''
Error loading universal:nominal-resolution - ('Cyclical @context URLs detected.',)
Type: jsonld.ContextUrlError
Code: context overflow
Details: {'url': 'https://wcrp-cmip.github.io/WCRP-universe/nominal-resolution/graph.jsonld'}
Error loading universal:grid-descriptor - ('Cyclical @context URLs detected.',)
Type: jsonld.ContextUrlError
Code: context overflow
Details: {'url': 'https://wcrp-cmip.github.io/WCRP-universe/grid-descriptor/graph.jsonld'}
Error loading universal:grid-mapping - ('Cyclical @context URLs detected.',)
Type: jsonld.ContextUrlError
Code: context overflow
Details: {'url': 'https://wcrp-cmip.github.io/WCRP-universe/grid-mapping/graph.jsonld'}
Error loading universal:grid-arrangement - ('Cyclical @context URLs detected.',)
Type: jsonld.ContextUrlError
Code: context overflow
Details: {'url': 'https://wcrp-cmip.github.io/WCRP-universe/grid-arrangement/graph.jsonld'}
Error loading universal:truncation-method - ('Cyclical @context URLs detected.',)
Type: jsonld.ContextUrlError
Code: context overflow
Details: {'url': 'https://wcrp-cmip.github.io/WCRP-universe/truncation-method/graph.jsonld'}
Error loading universal:scientific-domain - ('Cyclical @context URLs detected.',)
Type: jsonld.ContextUrlError
Code: context overflow
Details: {'url': 'https://wcrp-cmip.github.io/WCRP-universe/scientific-domain/graph.jsonld'}
Error loading universal:typical-application - ('Cyclical @context URLs detected.',)
    
'''

def main():
    """Generate templates."""

    
    # Add hardcoded lists for missing CVs
    template_data.update({
        'grid_descriptors': ["N48", "N96", "N216", "N512", "N1280", "ORCA2", "eORCA2", "ORCA1", "eORCA1", "ORCA025", "eORCA025", "ORCA012", "eORCA012", "T42", "T63", "T85", "T106", "T127", "T255", "TL95", "TL159", "TL255", "TL319", "TL511", "TL959", "TL1279", "Tco199", "Tco399", "R30", "C96"],
        'grid_mappings': ["albers_conical_equal_area", "azimuthal_equidistant", "geostationary", "lambert_azimuthal_equal_area", "lambert_conformal_conic", "lambert_cylindrical_equal_area", "latitude_longitude", "orthographic", "polar_stereographic", "rotated_latitude_longitude", "sinusoidal", "stereographic", "transverse_mercator", "vertical_perspective"],
        'grid_arrangements': ["arakawa_A", "arakawa_B", "arakawa_C", "arakawa_D", "arakawa_E"],
        'truncation_methods': ["triangular", "rhomboidal"],
        'nominal_resolutions': ["0.5 km", "1 km", "2.5 km", "5 km", "10 km", "25 km", "50 km", "100 km", "250 km", "500 km", "1000 km", "2500 km", "5000 km", "10000 km"],
        'scientific_domains': ["Atmospheric dynamics", "Ocean circulation", "Land surface processes", "Sea ice dynamics", "Land ice dynamics", "Biogeochemical cycles", "Atmospheric chemistry", "Aerosol processes", "Hydrology", "Vegetation dynamics", "Human dimensions", "Paleoclimate applications", "Weather prediction", "Seasonal forecasting"],
        'typical_applications': ["Climate projections", "Historical climate analysis", "Idealized experiments", "Process studies", "Model intercomparison projects (MIPs)", "Impact assessments", "Policy support", "Educational purposes", "Seasonal prediction", "Decadal prediction", "Paleoclimate reconstruction"]
    })
    
    print(f"Loaded {len(template_data['experiments'])} experiments")
    print(f"Loaded {len(template_data['activities'])} activities") 
    print(f"Loaded {len(template_data['realms'])} realms")
    print(f"Loaded {len(template_data['institutions'])} institutions")
    
    # Setup Jinja2
    templates_dir = Path("/Users/daniel.ellis/WIPwork/Essential-Model-Documentation/.github/ISSUE_GENERATE")
    output_dir = Path("/Users/daniel.ellis/WIPwork/Essential-Model-Documentation/.github/ISSUE_TEMPLATE")
    
    env = Environment(loader=FileSystemLoader(templates_dir), trim_blocks=True, lstrip_blocks=True)
    
    # Generate templates
    templates = [
        ("component_submission.j2", "component_submission.yml"),
        ("top_level_model.j2", "top_level_model.yml"),
        ("model_family_documentation.j2", "model_family_documentation.yml"),
        ("extended_component_documentation.j2", "extended_component_documentation.yml"),
        ("extended_model_documentation.j2", "extended_model_documentation.yml")
    ]
    
    for template_file, output_file in templates:
        print(f"Generating {output_file}...")
        template = env.get_template(template_file)
        content = template.render(**template_data)
        
        with open(output_dir / output_file, 'w') as f:
            f.write(content)
        print(f"  ✓ Generated {output_file}")
    
    print("Done!")

if __name__ == '__main__':
    main()
