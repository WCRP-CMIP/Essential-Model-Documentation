#!/usr/bin/env python3
"""
COMPREHENSIVE FIX: Template generator with proper data handling and YAML validation
"""

import json
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def create_fallback_data():
    """Create complete fallback data structure for when CV loading fails."""
    return {
        # These should be dicts for .keys() iteration
        'realms': {
            'atmos': {'id': 'atmos', 'validation-key': 'atmos'},
            'ocean': {'id': 'ocean', 'validation-key': 'ocean'},
            'land': {'id': 'land', 'validation-key': 'land'},
            'seaice': {'id': 'seaice', 'validation-key': 'seaice'},
            'ocnbgchem': {'id': 'ocnbgchem', 'validation-key': 'ocnbgchem'},
            'landice': {'id': 'landice', 'validation-key': 'landice'},
            'aerosol': {'id': 'aerosol', 'validation-key': 'aerosol'},
            'atmoschem': {'id': 'atmoschem', 'validation-key': 'atmoschem'}
        },
        'experiments': {
            'piControl': {'id': 'piControl', 'validation-key': 'piControl'},
            'historical': {'id': 'historical', 'validation-key': 'historical'},
            'ssp126': {'id': 'ssp126', 'validation-key': 'ssp126'},
            'ssp245': {'id': 'ssp245', 'validation-key': 'ssp245'},
            'ssp585': {'id': 'ssp585', 'validation-key': 'ssp585'},
            '1pctCO2': {'id': '1pctCO2', 'validation-key': '1pctCO2'}
        },
        'activities': {
            'CMIP': {'id': 'CMIP', 'validation-key': 'CMIP'},
            'ScenarioMIP': {'id': 'ScenarioMIP', 'validation-key': 'ScenarioMIP'},
            'DAMIP': {'id': 'DAMIP', 'validation-key': 'DAMIP'},
            'AerChemMIP': {'id': 'AerChemMIP', 'validation-key': 'AerChemMIP'}
        },
        'institutions': {
            'NCAR': {'id': 'NCAR', 'validation-key': 'NCAR'},
            'MOHC': {'id': 'MOHC', 'validation-key': 'MOHC'},
            'MPI-M': {'id': 'MPI-M', 'validation-key': 'MPI-M'},
            'CNRM-CERFACS': {'id': 'CNRM-CERFACS', 'validation-key': 'CNRM-CERFACS'}
        },
        'licenses': {
            'CC0-1.0': {'id': 'CC0-1.0', 'validation-key': 'CC0-1.0'},
            'CC-BY-4.0': {'id': 'CC-BY-4.0', 'validation-key': 'CC-BY-4.0'},
            'MIT': {'id': 'MIT', 'validation-key': 'MIT'},
            'GPL-3.0': {'id': 'GPL-3.0', 'validation-key': 'GPL-3.0'}
        },
        'source_types': {
            'AOGCM': {'id': 'AOGCM', 'validation-key': 'AOGCM'},
            'AGCM': {'id': 'AGCM', 'validation-key': 'AGCM'},
            'OGCM': {'id': 'OGCM', 'validation-key': 'OGCM'},
            'ESM': {'id': 'ESM', 'validation-key': 'ESM'},
            'BGCM': {'id': 'BGCM', 'validation-key': 'BGCM'}
        },
        'horizontal_grid_types': {
            'regular_lat_lon': {'id': 'regular_lat_lon', 'validation-key': 'regular_lat_lon'},
            'gaussian': {'id': 'gaussian', 'validation-key': 'gaussian'},
            'spectral': {'id': 'spectral', 'validation-key': 'spectral'},
            'cubed_sphere': {'id': 'cubed_sphere', 'validation-key': 'cubed_sphere'}
        },
        'horizontal_regions': {
            'global': {'id': 'global', 'validation-key': 'global'},
            'regional': {'id': 'regional', 'validation-key': 'regional'}
        },
        'vertical_coordinates': {
            'hybrid_sigma_pressure': {'id': 'hybrid_sigma_pressure', 'validation-key': 'hybrid_sigma_pressure'},
            'sigma': {'id': 'sigma', 'validation-key': 'sigma'},
            'pressure': {'id': 'pressure', 'validation-key': 'pressure'},
            'height': {'id': 'height', 'validation-key': 'height'}
        },
        'vertical_units': {
            'Pa': {'id': 'Pa', 'validation-key': 'Pa'},
            'm': {'id': 'm', 'validation-key': 'm'},
            'hPa': {'id': 'hPa', 'validation-key': 'hPa'}
        },
        'calendars': {
            'gregorian': {'id': 'gregorian', 'validation-key': 'gregorian'},
            'noleap': {'id': 'noleap', 'validation-key': 'noleap'},
            '360_day': {'id': '360_day', 'validation-key': '360_day'}
        },
        
        # These are lists for simple iteration
        'grid_descriptors': ["N48", "N96", "N216", "N512", "ORCA1", "ORCA025", "T63", "T127"],
        'grid_mappings': ["latitude_longitude", "polar_stereographic", "lambert_conformal_conic"],
        'grid_arrangements': ["arakawa_A", "arakawa_B", "arakawa_C"],
        'truncation_methods': ["triangular", "rhomboidal"],
        'nominal_resolutions': ["10 km", "25 km", "50 km", "100 km", "250 km"],
        'scientific_domains': ["Atmospheric dynamics", "Ocean circulation", "Land surface processes"],
        'typical_applications': ["Climate projections", "Historical climate analysis", "Process studies"]
    }

def validate_yaml_output(content, filename):
    """Validate generated YAML content."""
    try:
        parsed = yaml.safe_load(content)
        
        if not isinstance(parsed, dict):
            return False, "Root should be dict"
        
        required = ['name', 'description', 'body']
        missing = [f for f in required if f not in parsed]
        if missing:
            return False, f"Missing: {missing}"
        
        if not isinstance(parsed['body'], list):
            return False, "'body' should be list"
            
        return True, "Valid"
        
    except yaml.YAMLError as e:
        return False, f"YAML error: {e}"

def main():
    """Generate templates with comprehensive validation."""
    
    print("🔨 Generating GitHub Issue Templates (COMPREHENSIVE FIX)")
    print("=" * 60)
    
    # Use fallback data to ensure consistency
    template_data = create_fallback_data()
    print(f"📊 Using fallback data with {len(template_data)} categories")
    
    # Setup paths
    script_dir = Path(__file__).parent
    templates_dir = script_dir
    output_dir = script_dir.parent / "ISSUE_TEMPLATE"
    output_dir.mkdir(exist_ok=True)
    
    # Setup Jinja2
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True
    )
    
    # Template list
    templates = [
        ("component_submission.j2", "component_submission.yml"),
        ("top_level_model.j2", "top_level_model.yml"), 
        ("model_family_documentation.j2", "model_family_documentation.yml"),
        ("extended_component_documentation.j2", "extended_component_documentation.yml"),
        ("extended_model_documentation.j2", "extended_model_documentation.yml"),
        ("experiment_documentation.j2", "experiment_documentation.yml")
    ]
    
    print(f"\n🔨 Processing {len(templates)} templates...")
    
    success_count = 0
    
    for template_file, output_file in templates:
        print(f"\n📝 {template_file}:")
        
        try:
            # Check template exists
            if not (templates_dir / template_file).exists():
                print(f"    ❌ Template not found")
                continue
            
            # Render template
            template = env.get_template(template_file)
            content = template.render(**template_data)
            
            # Validate YAML
            is_valid, message = validate_yaml_output(content, output_file)
            
            if is_valid:
                # Save file
                with open(output_dir / output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"    ✅ Generated and validated ({len(content)} chars)")
                success_count += 1
            else:
                print(f"    ❌ Validation failed: {message}")
                # Optionally save with .broken extension for debugging
                with open(output_dir / f"{output_file}.broken", 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"    💾 Saved broken version as {output_file}.broken for debugging")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    # Summary
    print(f"\n🎯 Final Results:")
    print(f"  ✅ Successfully generated: {success_count}/{len(templates)}")
    print(f"  ❌ Failed: {len(templates) - success_count}/{len(templates)}")
    
    if success_count == len(templates):
        print(f"\n🎉 All templates generated successfully!")
        print(f"📁 Location: {output_dir}")
        print(f"🚀 Ready for GitHub!")
    else:
        print(f"\n🔧 Some templates failed - check .broken files for debugging")

if __name__ == '__main__':
    main()
