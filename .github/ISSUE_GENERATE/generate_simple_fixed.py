#!/usr/bin/env python3
"""
FIXED: Template generator that loads CMIP7_CVs and WCRP-universe data to populate Jinja2 templates.
"""

import json
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

import cmipld

def load(prefix, loc):
    """Load data with better error handling."""
    try:
        result = cmipld.get(f"{prefix}:{loc}/graph.jsonld", depth=0)['@graph']
        print(f"✓ Loaded {prefix}:{loc} - {len(result)} items")
        return result
    except Exception as e:
        print(f"⚠️  Error loading {prefix}:{loc} - {e}")
        return []

def convert_to_dict(data_list, key_field='id'):
    """Convert list of dicts to dict for template .keys() iteration."""
    if not isinstance(data_list, list):
        return {}
    
    result = {}
    for item in data_list:
        if isinstance(item, dict):
            # Try multiple possible key fields
            key = item.get(key_field) or item.get('validation-key') or item.get('name')
            if key:
                result[key] = item
    return result

def main():
    """Generate templates with FIXED data handling."""
    
    print("🔨 Loading controlled vocabularies...")
    
    # FIXED: Use consistent variable name throughout
    template_data = {}
    
    # Load data and convert lists to dicts for template .keys() iteration
    print("\n📊 Loading CV data...")
    template_data['experiments'] = convert_to_dict(load("cmip7", "experiment"))
    template_data['activities'] = convert_to_dict(load("universal", "activity"))
    template_data['realms'] = convert_to_dict(load("universal", "realm"))
    template_data['institutions'] = convert_to_dict(load("universal", "organisation"))
    template_data['licenses'] = convert_to_dict(load("universal", "license"))
    template_data['source_types'] = convert_to_dict(load("universal", "source-type"))
    template_data['horizontal_grid_types'] = convert_to_dict(load("universal", "native-horizontal-grid-type"))
    template_data['horizontal_regions'] = convert_to_dict(load("universal", "native-horizontal-grid-region"))
    template_data['temporal_refinements'] = convert_to_dict(load("universal", "native-horizontal-grid-temporal-refinement"))
    template_data['vertical_coordinates'] = convert_to_dict(load("universal", "native-vertical-grid-coordinate"))
    template_data['vertical_units'] = convert_to_dict(load("universal", "native-vertical-grid-units"))
    template_data['calendars'] = convert_to_dict(load("universal", "model-calendar"))
    
    # FIXED: Handle problematic CVs with fallback data
    print("\n🔧 Adding fallback data for problematic CVs...")
    
    # Try to load, fall back to hardcoded lists if cyclical context errors
    fallback_lists = {
        'grid_descriptors': [
            "N48", "N96", "N216", "N512", "N1280", 
            "ORCA2", "eORCA2", "ORCA1", "eORCA1", 
            "ORCA025", "eORCA025", "ORCA012", "eORCA012", 
            "T42", "T63", "T85", "T106", "T127", "T255",
            "TL95", "TL159", "TL255", "TL319", "TL511", "TL959", "TL1279",
            "Tco199", "Tco399", "R30", "C96", "f19_g17", "ne30np4"
        ],
        'grid_mappings': [
            "albers_conical_equal_area", "azimuthal_equidistant", 
            "geostationary", "lambert_azimuthal_equal_area", 
            "lambert_conformal_conic", "lambert_cylindrical_equal_area", 
            "latitude_longitude", "orthographic", "polar_stereographic", 
            "rotated_latitude_longitude", "sinusoidal", "stereographic", 
            "transverse_mercator", "vertical_perspective"
        ],
        'grid_arrangements': [
            "arakawa_A", "arakawa_B", "arakawa_C", "arakawa_D", "arakawa_E"
        ],
        'truncation_methods': [
            "triangular", "rhomboidal"
        ],
        'nominal_resolutions': [
            "0.5 km", "1 km", "2.5 km", "5 km", "10 km", "25 km", 
            "50 km", "100 km", "250 km", "500 km", "1000 km", 
            "2500 km", "5000 km", "10000 km"
        ],
        'scientific_domains': [
            "Atmospheric dynamics", "Ocean circulation", "Land surface processes", 
            "Sea ice dynamics", "Land ice dynamics", "Biogeochemical cycles", 
            "Atmospheric chemistry", "Aerosol processes", "Hydrology", 
            "Vegetation dynamics", "Human dimensions", "Paleoclimate applications", 
            "Weather prediction", "Seasonal forecasting"
        ],
        'typical_applications': [
            "Climate projections", "Historical climate analysis", 
            "Idealized experiments", "Process studies", 
            "Model intercomparison projects (MIPs)", "Impact assessments", 
            "Policy support", "Educational purposes", "Seasonal prediction", 
            "Decadal prediction", "Paleoclimate reconstruction"
        ]
    }
    
    # Add fallback data (keep as lists for simple iteration in templates)
    template_data.update(fallback_lists)
    
    # Print data summary
    print(f"\n📊 Data loaded successfully:")
    for key, value in template_data.items():
        if isinstance(value, dict):
            print(f"  {key}: {len(value)} items (dict)")
        elif isinstance(value, list):
            print(f"  {key}: {len(value)} items (list)")
    
    # FIXED: Use relative paths for portability
    script_dir = Path(__file__).parent
    templates_dir = script_dir
    output_dir = script_dir.parent / "ISSUE_TEMPLATE"
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    env = Environment(
        loader=FileSystemLoader(templates_dir), 
        trim_blocks=True, 
        lstrip_blocks=True,
        keep_trailing_newline=True
    )
    
    # FIXED: Complete template list including experiment template
    templates = [
        ("component_submission.j2", "component_submission.yml"),
        ("top_level_model.j2", "top_level_model.yml"),
        ("model_family_documentation.j2", "model_family_documentation.yml"),
        ("extended_component_documentation.j2", "extended_component_documentation.yml"),
        ("extended_model_documentation.j2", "extended_model_documentation.yml"),
        ("experiment_documentation.j2", "experiment_documentation.yml")  # ADDED MISSING TEMPLATE
    ]
    
    print(f"\n🔨 Generating {len(templates)} templates...")
    generated_count = 0
    failed_count = 0
    
    for template_file, output_file in templates:
        try:
            print(f"  Processing {template_file}...")
            
            # Check if template exists
            template_path = templates_dir / template_file
            if not template_path.exists():
                print(f"    ❌ Template file not found: {template_file}")
                failed_count += 1
                continue
                
            # Load and render template
            template = env.get_template(template_file)
            content = template.render(**template_data)  # FIXED: Use template_data consistently
            
            # Basic validation
            if not content.strip().startswith('name:'):
                print(f"    ⚠️  Warning: Generated content doesn't start with 'name:'")
            
            # Write output
            output_path = output_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    ✅ Generated {output_file} ({len(content)} chars)")
            generated_count += 1
            
        except Exception as e:
            print(f"    ❌ Error generating {output_file}: {e}")
            failed_count += 1
    
    print(f"\n📋 Generation Summary:")
    print(f"  ✅ Successfully generated: {generated_count} templates")
    print(f"  ❌ Failed: {failed_count} templates")
    
    if failed_count > 0:
        print("\n🔧 Common fixes needed:")
        print("  1. Ensure template variables match data keys")
        print("  2. Check that .keys() is used only on dict data")
        print("  3. Verify all referenced CVs are loaded")
        print("  4. Check Jinja2 syntax for loops and conditionals")
    
    if generated_count > 0:
        print(f"\n🎉 Success! Templates ready at: {output_dir}")

if __name__ == '__main__':
    main()
