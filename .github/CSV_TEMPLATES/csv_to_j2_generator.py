#!/usr/bin/env python3
"""
CSV-to-Jinja2 Template Generator

Reads a CSV file containing template field definitions and generates 
Jinja2 (.j2) template files for GitHub issue forms.

CSV Columns:
- template_name: Name of the template (e.g., 'component_submission')
- section_order: Order of fields in the template
- field_type: Type of field (dropdown, input, textarea, checkboxes, markdown)
- field_id: Unique ID for the field
- label: Display label for the field
- description: Help text description
- data_source: Where to get options data from (e.g., 'realms', 'licenses')
- required: Whether field is required (true/false)
- placeholder: Placeholder text for inputs
- options_type: How to format options (dict_keys, list, dict_checkbox, etc.)
- default_value: Default value if any
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

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
    
    if field_type != 'markdown':
        field_yaml += f"    id: {field_id}\n"
    
    field_yaml += f"    attributes:\n"
    field_yaml += f"      label: {label}\n"
    
    if description:
        # Handle multi-line descriptions
        if '\n' in description or len(description) > 80:
            field_yaml += f"      description: |\n"
            for line in description.split('\n'):
                field_yaml += f"        {line}\n"
        else:
            field_yaml += f"      description: {description}\n"
    
    # Handle different field types and their specific attributes
    if field_type == 'markdown':
        field_yaml += f"      value: |\n        {description}\n"
        
    elif field_type in ['input', 'textarea']:
        if placeholder:
            field_yaml += f"      placeholder: \"{placeholder}\"\n"
            
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
            
    elif field_type == 'checkboxes':
        field_yaml += f"      options:\n"
        
        if options_type == 'dict_checkbox':
            field_yaml += f"{{% for key in {data_source}.keys() %}}\n"
            field_yaml += f"        - label: \"{{{{ key }}}}\"\n"
            field_yaml += f"{{% endfor %}}\n"
    
    # Add validation section if required
    if required and field_type != 'markdown':
        field_yaml += f"    validations:\n"
        field_yaml += f"      required: true\n"
    
    return field_yaml

def generate_template_header(template_name):
    """Generate the header section for a template."""
    
    # Map template names to proper titles and labels
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
    
    print(f"🔨 Generating {template_name}.j2...")
    
    # Start with template header
    template_content = generate_template_header(template_name)
    
    # Add each field
    for field_def in field_definitions:
        field_content = generate_field_jinja2(field_def)
        template_content += field_content + "\n"
    
    return template_content.rstrip() + "\n"

def main():
    """Main function to generate Jinja2 templates from CSV."""
    
    print("🏗️  CSV-to-Jinja2 Template Generator")
    print("=" * 40)
    
    # Setup paths
    script_dir = Path(__file__).parent
    csv_file = script_dir / "template_definitions.csv"
    output_dir = script_dir.parent / "ISSUE_GENERATE"
    
    # Check CSV exists
    if not csv_file.exists():
        print(f"❌ CSV file not found: {csv_file}")
        return False
    
    # Read CSV definitions
    templates = read_csv_definitions(csv_file)
    
    # Generate Jinja2 templates
    print(f"\n🔨 Generating Jinja2 templates...")
    
    success_count = 0
    total_count = len(templates)
    
    for template_name, field_defs in templates.items():
        try:
            # Generate template content
            j2_content = generate_jinja2_template(template_name, field_defs)
            
            # Write to file
            output_file = output_dir / f"{template_name}.j2"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(j2_content)
            
            print(f"  ✅ {template_name}.j2 ({len(j2_content)} chars)")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ {template_name}: {e}")
    
    # Summary
    print(f"\n🎯 Generation Results:")
    print(f"  ✅ Successfully generated: {success_count}/{total_count}")
    print(f"  📁 Output directory: {output_dir}")
    
    if success_count > 0:
        print(f"\n🚀 Jinja2 templates ready!")
        print(f"💡 Next: Use your existing generator to create .yml files")
        return True
    else:
        print(f"\n❌ Generation failed - check CSV format and field definitions")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
