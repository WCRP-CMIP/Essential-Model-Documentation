#!/usr/bin/env python3
"""
Complete CSV-Based Template Generator

This script:
1. Contains all CV data as dictionaries and lists
2. Generates Jinja2 templates from CSV definitions
3. Renders those templates with CV data to create final YAML files
4. All in one place for easy management
"""

import csv
import yaml
from pathlib import Path
from collections import defaultdict
from jinja2 import Template

def get_cv_data():
    """Return all controlled vocabulary data as dicts and lists."""
    
    return {
        # Dictionary data for .keys() iteration
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
            '1pctCO2': {'id': '1pctCO2', 'validation-key': '1pctCO2'},
            'abrupt-4xCO2': {'id': 'abrupt-4xCO2', 'validation-key': 'abrupt-4xCO2'}
        },
        'activities': {
            'CMIP': {'id': 'CMIP', 'validation-key': 'CMIP'},
            'ScenarioMIP': {'id': 'ScenarioMIP', 'validation-key': 'ScenarioMIP'},
            'DAMIP': {'id': 'DAMIP', 'validation-key': 'DAMIP'},
            'AerChemMIP': {'id': 'AerChemMIP', 'validation-key': 'AerChemMIP'},
            'C4MIP': {'id': 'C4MIP', 'validation-key': 'C4MIP'},
            'DCPP': {'id': 'DCPP', 'validation-key': 'DCPP'}
        },
        'licenses': {
            'CC0-1.0': {'id': 'CC0-1.0', 'validation-key': 'CC0-1.0'},
            'CC-BY-4.0': {'id': 'CC-BY-4.0', 'validation-key': 'CC-BY-4.0'},
            'MIT': {'id': 'MIT', 'validation-key': 'MIT'},
            'GPL-3.0': {'id': 'GPL-3.0', 'validation-key': 'GPL-3.0'},
            'Apache-2.0': {'id': 'Apache-2.0', 'validation-key': 'Apache-2.0'}
        },
        'source_types': {
            'AOGCM': {'id': 'AOGCM', 'validation-key': 'AOGCM'},
            'AGCM': {'id': 'AGCM', 'validation-key': 'AGCM'},
            'OGCM': {'id': 'OGCM', 'validation-key': 'OGCM'},
            'ESM': {'id': 'ESM', 'validation-key': 'ESM'},
            'BGCM': {'id': 'BGCM', 'validation-key': 'BGCM'},
            'AER': {'id': 'AER', 'validation-key': 'AER'},
            'CHEM': {'id': 'CHEM', 'validation-key': 'CHEM'}
        },
        'institutions': {
            'NCAR': {'id': 'NCAR', 'validation-key': 'NCAR'},
            'MOHC': {'id': 'MOHC', 'validation-key': 'MOHC'},
            'MPI-M': {'id': 'MPI-M', 'validation-key': 'MPI-M'},
            'CNRM-CERFACS': {'id': 'CNRM-CERFACS', 'validation-key': 'CNRM-CERFACS'},
            'IPSL': {'id': 'IPSL', 'validation-key': 'IPSL'},
            'NOAA-GFDL': {'id': 'NOAA-GFDL', 'validation-key': 'NOAA-GFDL'}
        },
        'horizontal_grid_types': {
            'regular_lat_lon': {'id': 'regular_lat_lon', 'validation-key': 'regular_lat_lon'},
            'gaussian': {'id': 'gaussian', 'validation-key': 'gaussian'},
            'spectral': {'id': 'spectral', 'validation-key': 'spectral'},
            'cubed_sphere': {'id': 'cubed_sphere', 'validation-key': 'cubed_sphere'},
            'icosahedral': {'id': 'icosahedral', 'validation-key': 'icosahedral'}
        },
        'horizontal_regions': {
            'global': {'id': 'global', 'validation-key': 'global'},
            'regional': {'id': 'regional', 'validation-key': 'regional'},
            'limited_area': {'id': 'limited_area', 'validation-key': 'limited_area'}
        },
        'vertical_coordinates': {
            'hybrid_sigma_pressure': {'id': 'hybrid_sigma_pressure', 'validation-key': 'hybrid_sigma_pressure'},
            'sigma': {'id': 'sigma', 'validation-key': 'sigma'},
            'pressure': {'id': 'pressure', 'validation-key': 'pressure'},
            'height': {'id': 'height', 'validation-key': 'height'},
            'terrain_following': {'id': 'terrain_following', 'validation-key': 'terrain_following'}
        },
        'vertical_units': {
            'Pa': {'id': 'Pa', 'validation-key': 'Pa'},
            'hPa': {'id': 'hPa', 'validation-key': 'hPa'},
            'm': {'id': 'm', 'validation-key': 'm'},
            'km': {'id': 'km', 'validation-key': 'km'}
        },
        'calendars': {
            'gregorian': {'id': 'gregorian', 'validation-key': 'gregorian'},
            'noleap': {'id': 'noleap', 'validation-key': 'noleap'},
            '360_day': {'id': '360_day', 'validation-key': '360_day'},
            'julian': {'id': 'julian', 'validation-key': 'julian'}
        },
        
        # List data for simple iteration  
        'grid_descriptors': [
            'N48', 'N96', 'N216', 'N512', 'N1280',
            'ORCA2', 'eORCA2', 'ORCA1', 'eORCA1', 
            'ORCA025', 'eORCA025', 'ORCA012', 'eORCA012',
            'T42', 'T63', 'T85', 'T106', 'T127', 'T255',
            'TL95', 'TL159', 'TL255', 'TL319', 'TL511',
            'Tco199', 'Tco399', 'R30', 'C96', 'ne30np4'
        ],
        'grid_mappings': [
            'latitude_longitude', 'polar_stereographic',
            'lambert_conformal_conic', 'rotated_latitude_longitude',
            'albers_conical_equal_area', 'lambert_azimuthal_equal_area',
            'orthographic', 'stereographic', 'transverse_mercator'
        ],
        'grid_arrangements': [
            'arakawa_A', 'arakawa_B', 'arakawa_C', 'arakawa_D', 'arakawa_E'
        ],
        'truncation_methods': [
            'triangular', 'rhomboidal'
        ],
        'nominal_resolutions': [
            '1 km', '2.5 km', '5 km', '10 km', '25 km', '50 km',
            '100 km', '250 km', '500 km', '1000 km', '2500 km'
        ],
        'scientific_domains': [
            'Atmospheric dynamics', 'Ocean circulation', 'Land surface processes',
            'Sea ice dynamics', 'Land ice dynamics', 'Biogeochemical cycles',
            'Atmospheric chemistry', 'Aerosol processes', 'Hydrology',
            'Vegetation dynamics', 'Human dimensions', 'Paleoclimate applications',
            'Weather prediction', 'Seasonal forecasting'
        ],
        'typical_applications': [
            'Climate projections', 'Historical climate analysis',
            'Idealized experiments', 'Process studies',
            'Model intercomparison projects (MIPs)', 'Impact assessments',
            'Policy support', 'Educational purposes', 'Seasonal prediction',
            'Decadal prediction', 'Paleoclimate reconstruction'
        ]
    }

def read_csv_definitions(csv_path):
    """Read template definitions from CSV file."""
    
    print(f"📖 Reading template definitions from {csv_path.name}...")
    
    templates = defaultdict(list)
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            template_name = row['template_name']
            templates[template_name].append(row)
    
    # Sort each template's fields by section_order
    for template_name in templates:
        templates[template_name].sort(key=lambda x: int(x['section_order']))
    
    print(f"✅ Loaded {len(templates)} templates:")
    for name, fields in templates.items():
        print(f"   - {name}: {len(fields)} fields")
    
    return dict(templates)

def generate_field_jinja2(field_def):
    """Generate Jinja2 code for a single field based on CSV definition."""
    
    field_type = field_def['field_type']
    field_id = field_def['field_id']
    label = field_def['label']
    description = field_def['description']
    data_source = field_def['data_source']
    required = field_def['required'].lower() == 'true'
    placeholder = field_def['placeholder']
    options_type = field_def['options_type']
    default_value = field_def['default_value']
    
    # Start building the field YAML
    field_yaml = f"  - type: {field_type}\n"
    
    # Handle markdown fields differently - they don't have id, label, or description
    if field_type == 'markdown':
        field_yaml += f"    attributes:\n"
        field_yaml += f"      value: |\n        {description}\n"
        return field_yaml
    
    # For all other field types, add id and attributes
    field_yaml += f"    id: {field_id}\n"
    field_yaml += f"    attributes:\n"
    field_yaml += f"      label: {label}\n"
    
    if description:
        # Handle multiline descriptions - look for literal \n in the string
        if '\\n' in description:
            # Replace literal \n with actual newlines and proper indentation
            formatted_description = description.replace('\\n', '\n        ')
            field_yaml += f"      description: |\n        {formatted_description}\n"
        elif '\n' in description:
            # Handle actual newline characters
            formatted_description = description.replace('\n', '\n        ')
            field_yaml += f"      description: |\n        {formatted_description}\n"
        elif '**' in description or len(description) > 80:
            field_yaml += f"      description: |\n        {description}\n"
        else:
            field_yaml += f"      description: {description}\n"
            
    # Handle input and textarea fields
    if field_type in ['input', 'textarea']:
        if placeholder:
            field_yaml += f"      placeholder: \"{placeholder}\"\n"
            
    # Handle dropdown fields            
    elif field_type == 'dropdown':
        field_yaml += f"      options:\n"
        
        # Generate options based on options_type
        if options_type == 'dict_keys':
            field_yaml += f"{{% for key in {data_source}.keys() %}}\n"
            field_yaml += f"        - \"{{{{ key }}}}\"\n"
            field_yaml += f"{{% endfor %}}\n"
            
        elif options_type == 'list':
            field_yaml += f"{{% for item in {data_source} %}}\n"
            field_yaml += f"        - \"{{{{ item }}}}\"\n"
            field_yaml += f"{{% endfor %}}\n"
            
        elif options_type == 'list_with_na':
            field_yaml += f"        - \"Not applicable\"\n"
            field_yaml += f"{{% for item in {data_source} %}}\n"
            field_yaml += f"        - \"{{{{ item }}}}\"\n"
            field_yaml += f"{{% endfor %}}\n"
            
        elif options_type == 'dict_with_extra':
            field_yaml += f"{{% for key in {data_source}.keys() %}}\n"
            field_yaml += f"        - \"{{{{ key }}}}\"\n"
            field_yaml += f"{{% endfor %}}\n"
            field_yaml += f"        - \"Open Source\"\n"
            field_yaml += f"        - \"Registration Required\"\n"
            field_yaml += f"        - \"Proprietary\"\n"
            
        elif options_type == 'hardcoded':
            if field_id == 'family_type':
                field_yaml += f"        - \"Model Family (complete Earth system models)\"\n"
                field_yaml += f"        - \"Component Family (individual model components)\"\n"
                
        elif options_type == 'tier_hardcoded':
            field_yaml += f"        - \"0\"\n"
            field_yaml += f"        - \"1\"\n"
            field_yaml += f"        - \"2\"\n"
            field_yaml += f"        - \"3\"\n"
        
        if default_value:
            field_yaml += f"      default: {default_value}\n"
            
    # Handle checkbox fields
    elif field_type == 'checkboxes':
        field_yaml += f"      options:\n"
        
        if options_type == 'dict_checkbox':
            field_yaml += f"{{% for key in {data_source}.keys() %}}\n"
            field_yaml += f"        - label: \"{{{{ key }}}}\"\n"
            field_yaml += f"{{% endfor %}}\n"
    
    # Add validation section if required
    if required:
        field_yaml += f"    validations:\n"
        field_yaml += f"      required: true\n"
    
    return field_yaml

def generate_template_header(template_name):
    """Generate the header section for a template."""
    
    template_info = {
        'component_submission': {
            'name': 'Model Component Submission',
            'description': 'Submit metadata for a model component as specified in the EMD specification.',
            'title': '[EMD] Model Component Submission',
            'labels': '["emd-submission", "component"]'
        },
        'top_level_model': {
            'name': 'Top Level Model Submission', 
            'description': 'Submit metadata for the top-level model properties as specified in the EMD specification.',
            'title': '[EMD] Top Level Model Submission',
            'labels': '["emd-submission", "top_level_model"]'
        },
        'model_family_documentation': {
            'name': 'Model Family Documentation',
            'description': 'Document a model family that encompasses multiple model configurations and components.',
            'title': '[EMD] Model Family Documentation', 
            'labels': '["emd-submission", "model_family"]'
        },
        'experiment_documentation': {
            'name': 'Experiment Documentation',
            'description': 'Submit metadata for a CMIP7 experiment configuration.',
            'title': '[EMD] Experiment Documentation',
            'labels': '["emd-submission", "experiment"]'
        }
    }
    
    info = template_info.get(template_name, {
        'name': template_name.replace('_', ' ').title(),
        'description': f'Generated template for {template_name}',
        'title': f'[EMD] {template_name.replace("_", " ").title()}',
        'labels': '["emd-submission"]'
    })
    
    header = f"""name: {info['name']}
description: {info['description']}
title: "{info['title']}"
labels: {info['labels']}
body:
"""
    return header

def generate_jinja2_template(template_name, field_definitions):
    """Generate complete Jinja2 template from field definitions."""
    
    # Start with template header
    template_content = generate_template_header(template_name)
    
    # Add each field
    for field_def in field_definitions:
        field_content = generate_field_jinja2(field_def)
        template_content += field_content + "\n"
    
    return template_content.rstrip() + "\n"

def validate_yaml_output(content, filename):
    """Validate that generated content is valid YAML."""
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
    """Main function - complete template generation pipeline."""
    
    print("🏗️  Complete CSV-Based Template Generator")
    print("=" * 45)
    
    # Setup paths
    script_dir = Path(__file__).parent
    csv_file = script_dir / "template_definitions.csv"
    j2_output_dir = script_dir.parent / "ISSUE_GENERATE"
    yml_output_dir = script_dir.parent / "ISSUE_TEMPLATE"
    
    # Create output directories
    j2_output_dir.mkdir(exist_ok=True)
    yml_output_dir.mkdir(exist_ok=True)
    
    # Check CSV exists
    if not csv_file.exists():
        print(f"❌ CSV file not found: {csv_file}")
        return False
    
    # Get CV data
    cv_data = get_cv_data()
    print(f"📊 CV data loaded: {len([k for k, v in cv_data.items() if isinstance(v, dict)])} dicts, {len([k for k, v in cv_data.items() if isinstance(v, list)])} lists")
    
    # Read CSV definitions
    templates = read_csv_definitions(csv_file)
    
    print(f"\n🔨 Generating Jinja2 templates and final YAML files...")
    
    j2_success = 0
    yml_success = 0
    total = len(templates)
    
    for template_name, field_defs in templates.items():
        try:
            print(f"\n📝 Processing {template_name}:")
            
            # Step 1: Generate Jinja2 template
            j2_content = generate_jinja2_template(template_name, field_defs)
            
            # Save .j2 file
            j2_file = j2_output_dir / f"{template_name}.j2"
            with open(j2_file, 'w', encoding='utf-8') as f:
                f.write(j2_content)
            print(f"    ✅ Generated {template_name}.j2")
            j2_success += 1
            
            # Step 2: Render template with CV data
            template = Template(j2_content)
            yml_content = template.render(**cv_data)
            
            # Step 3: Validate YAML
            is_valid, message = validate_yaml_output(yml_content, f"{template_name}.yml")
            
            if is_valid:
                # Save .yml file
                yml_file = yml_output_dir / f"{template_name}.yml"
                with open(yml_file, 'w', encoding='utf-8') as f:
                    f.write(yml_content)
                print(f"    ✅ Generated {template_name}.yml ({len(yml_content)} chars)")
                yml_success += 1
            else:
                print(f"    ❌ YAML validation failed: {message}")
                
        except Exception as e:
            print(f"    ❌ Error processing {template_name}: {e}")
    
    # Final summary
    print(f"\n🎯 Generation Complete:")
    print(f"  📝 Jinja2 templates: {j2_success}/{total}")
    print(f"  📄 YAML files: {yml_success}/{total}")
    print(f"  📁 J2 output: {j2_output_dir}")
    print(f"  📁 YAML output: {yml_output_dir}")
    
    if yml_success == total:
        print(f"\n🎉 All templates generated successfully!")
        print(f"🚀 Ready to test on GitHub!")
        return True
    else:
        print(f"\n⚠️  Some templates failed - check output for details")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
