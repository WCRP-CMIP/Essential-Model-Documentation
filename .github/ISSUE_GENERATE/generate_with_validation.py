#!/usr/bin/env python3
"""
FIXED: GitHub Issue Template Generator with Proper YAML Syntax
Generates valid GitHub issue forms from Jinja2 templates.

Key Fixes:
1. Proper YAML string quoting for all template variables
2. Consistent data structure handling (dict vs list)
3. Comprehensive error handling and validation
4. All hardcoded values properly quoted
"""

import json
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

import cmipld

def load(prefix, loc):
    """Load data with error handling."""
    try:
        result = cmipld.get(f"{prefix}:{loc}/graph.jsonld", depth=0)['@graph']
        print(f"✓ Loaded {prefix}:{loc} - {len(result)} items")
        return result
    except Exception as e:
        print(f"⚠️  Error loading {prefix}:{loc} - {e}")
        return []

def convert_to_dict(data_list, key_field='id'):
    """Convert list to dict for template .keys() iteration."""
    if not isinstance(data_list, list):
        return {}
    
    result = {}
    for item in data_list:
        if isinstance(item, dict):
            key = item.get(key_field) or item.get('validation-key') or item.get('name')
            if key:
                result[key] = item
    return result

def validate_generated_yaml(content, filename):
    """Validate that generated content is valid YAML."""
    try:
        parsed = yaml.safe_load(content)
        
        # Check GitHub issue template structure
        required_fields = ['name', 'description', 'body']
        missing = [field for field in required_fields if field not in parsed]
        
        if missing:
            print(f"    ❌ Missing fields: {missing}")
            return False
            
        if not isinstance(parsed.get('body'), list):
            print(f"    ❌ 'body' must be a list")
            return False
            
        print(f"    ✅ Valid GitHub issue template")
        return True
        
    except yaml.YAMLError as e:
        print(f"    ❌ YAML error: {e}")
        return False

def main():
    """Generate templates with validation."""
    
    print("🔨 Generating GitHub Issue Templates with YAML Validation")
    print("=" * 60)
    
    print("\n📊 Loading controlled vocabularies...")
    
    # Load and convert data structures
    template_data = {}
    
    # Load CV data as dicts for .keys() iteration
    cv_mappings = [
        ('experiments', 'cmip7', 'experiment'),
        ('activities', 'universal', 'activity'), 
        ('realms', 'universal', 'realm'),
        ('institutions', 'universal', 'organisation'),
        ('licenses', 'universal', 'license'),
        ('source_types', 'universal', 'source-type'),
        ('horizontal_grid_types', 'universal', 'native-horizontal-grid-type'),
        ('horizontal_regions', 'universal', 'native-horizontal-grid-region'),
        ('temporal_refinements', 'universal', 'native-horizontal-grid-temporal-refinement'),
        ('vertical_coordinates', 'universal', 'native-vertical-grid-coordinate'),
        ('vertical_units', 'universal', 'native-vertical-grid-units'),
        ('calendars', 'universal', 'model-calendar')
    ]
    
    for var_name, prefix, loc in cv_mappings:
        data_list = load(prefix, loc)
        template_data[var_name] = convert_to_dict(data_list)
    
    # Add fallback data for problematic CVs (as lists for simple iteration)
    template_data.update({
        'grid_descriptors': [
            "N48", "N96", "N216", "N512", "N1280", 
            "ORCA2", "eORCA2", "ORCA1", "eORCA1", 
            "ORCA025", "eORCA025", "ORCA012", "eORCA012", 
            "T42", "T63", "T85", "T106", "T127", "T255",
            "TL95", "TL159", "TL255", "TL319", "TL511", "TL959", "TL1279",
            "Tco199", "Tco399", "R30", "C96"
        ],
        'grid_mappings': [
            "albers_conical_equal_area", "azimuthal_equidistant", 
            "geostationary", "lambert_azimuthal_equal_area", 
            "lambert_conformal_conic", "lambert_cylindrical_equal_area", 
            "latitude_longitude", "orthographic", "polar_stereographic", 
            "rotated_latitude_longitude", "sinusoidal", "stereographic", 
            "transverse_mercator", "vertical_perspective"
        ],
        'grid_arrangements': ["arakawa_A", "arakawa_B", "arakawa_C", "arakawa_D", "arakawa_E"],
        'truncation_methods': ["triangular", "rhomboidal"],
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
    })
    
    # Print data summary
    print(f"\n📈 Template data loaded:")
    for key, value in template_data.items():
        if isinstance(value, dict):
            print(f"  {key}: {len(value)} items (dict)")
        elif isinstance(value, list):
            print(f"  {key}: {len(value)} items (list)")
    
    # Setup Jinja2 environment
    script_dir = Path(__file__).parent
    templates_dir = script_dir
    output_dir = script_dir.parent / "ISSUE_TEMPLATE" 
    
    output_dir.mkdir(exist_ok=True)
    
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True
    )
    
    # Generate all templates
    templates = [
        ("component_submission.j2", "component_submission.yml"),
        ("top_level_model.j2", "top_level_model.yml"),
        ("model_family_documentation.j2", "model_family_documentation.yml"),
        ("extended_component_documentation.j2", "extended_component_documentation.yml"),
        ("extended_model_documentation.j2", "extended_model_documentation.yml"),
        ("experiment_documentation.j2", "experiment_documentation.yml")
    ]
    
    print(f"\n🔨 Generating {len(templates)} GitHub issue templates...")
    
    valid_count = 0
    total_count = 0
    
    for template_file, output_file in templates:
        total_count += 1
        
        try:
            print(f"\n📝 Processing {template_file}:")
            
            # Check template exists
            template_path = templates_dir / template_file
            if not template_path.exists():
                print(f"    ❌ Template not found")
                continue
            
            # Load and render
            template = env.get_template(template_file)
            content = template.render(**template_data)
            
            # Validate generated YAML
            if validate_generated_yaml(content, output_file):
                # Write file
                output_path = output_dir / output_file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"    ✅ Generated {output_file} ({len(content)} chars)")
                valid_count += 1
            else:
                print(f"    ❌ Generated invalid YAML - not saved")
                
        except Exception as e:
            print(f"    ❌ Generation error: {e}")
    
    # Final summary
    print(f"\n🎯 Generation Results:")
    print(f"  ✅ Successfully generated: {valid_count}/{total_count}")
    print(f"  ❌ Failed validation: {total_count - valid_count}/{total_count}")
    
    if valid_count > 0:
        print(f"\n📁 Output: {output_dir}")
        print(f"🚀 Ready to test on GitHub!")
    else:
        print(f"\n🔧 Please fix template syntax issues before generating.")

if __name__ == '__main__':
    main()
