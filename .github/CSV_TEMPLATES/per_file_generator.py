#!/usr/bin/env python3
"""
Per-File Template Generator - Fixed for Select Multiple Fields

Handles select fields properly without value attributes.
"""

import csv
import sys
import yaml
import argparse
from pathlib import Path

def load_template_data(py_file):
    """Load configuration and data from Python file."""
    namespace = {}
    with open(py_file, 'r', encoding='utf-8') as f:
        exec(f.read(), namespace)
    
    config = namespace.get('TEMPLATE_CONFIG', {})
    data = namespace.get('DATA', {})
    return config, data

def load_csv_fields(csv_file):
    """Load field definitions from CSV."""
    fields = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fields.append(row)
    
    fields.sort(key=lambda x: int(x['field_order']))
    return fields

def generate_field_yaml(field_def, data):
    """Generate YAML for a single field."""
    
    field_type = field_def['field_type']
    field_id = field_def['field_id']
    label = field_def['label']
    description = field_def['description']
    data_source = field_def['data_source']
    required = field_def['required'].lower() == 'true'
    placeholder = field_def['placeholder']
    options_type = field_def['options_type']
    default_value = field_def['default_value']
    
    # Map multi-select to dropdown with multiple attribute
    actual_field_type = 'dropdown' if field_type == 'multi-select' else field_type
    yaml_lines = [f"  - type: {actual_field_type}"]
    
    # Handle markdown differently
    if field_type == 'markdown':
        yaml_lines.append("    attributes:")
        if '\\n' in description:
            formatted_desc = description.replace('\\n', '\n        ')
            yaml_lines.append("      value: |")
            yaml_lines.append(f"        {formatted_desc}")
        else:
            yaml_lines.append("      value: |")
            yaml_lines.append(f"        {description}")
        return '\n'.join(yaml_lines)
    
    # For multi-select fields, add multiple attribute and no id
    if field_type == 'multi-select':
        yaml_lines.append("    attributes:")
        yaml_lines.append("      multiple: true")
        yaml_lines.append(f"      label: {label}")
    else:
        # Regular fields with id
        yaml_lines.append(f"    id: {field_id}")
        yaml_lines.append("    attributes:")
        yaml_lines.append(f"      label: {label}")
    
    # Add description if present
    if description:
        if '\\n' in description:
            formatted_desc = description.replace('\\n', '\n        ')
            yaml_lines.append("      description: |")
            yaml_lines.append(f"        {formatted_desc}")
        elif len(description) > 80:
            yaml_lines.append("      description: |")
            yaml_lines.append(f"        {description}")
        else:
            yaml_lines.append(f"      description: {description}")
    
    # Add placeholder for inputs
    if field_type in ['input', 'textarea'] and placeholder:
        yaml_lines.append(f"      placeholder: \"{placeholder}\"")
    
    # Add options for dropdowns and multi-selects
    if field_type in ['dropdown', 'multi-select']:
        yaml_lines.append("      options:")
        
        if data_source != 'none' and data_source in data:
            source_data = data[data_source]
            
            if options_type == 'dict_keys':
                for key in source_data.keys():
                    yaml_lines.append(f"        - \"{key}\"")
            
            elif options_type == 'list':
                for item in source_data:
                    yaml_lines.append(f"        - \"{item}\"")
            
            elif options_type in ['dict_multiple']:
                # For multi-select, use simple string options (no label needed)
                for key in source_data.keys():
                    yaml_lines.append(f"        - \"{key}\"")
            
            elif options_type == 'dict_with_extra':
                for key in source_data.keys():
                    yaml_lines.append(f"        - \"{key}\"")
                yaml_lines.append("        - \"Open Source\"")
                yaml_lines.append("        - \"Registration Required\"")
                yaml_lines.append("        - \"Proprietary\"")
            
            elif options_type == 'list_with_na':
                yaml_lines.append("        - \"Not applicable\"")
                for item in source_data:
                    yaml_lines.append(f"        - \"{item}\"")
        
        elif options_type == 'hardcoded':
            hardcoded_key = f"{field_id}_options"
            if hardcoded_key in data:
                for option in data[hardcoded_key]:
                    yaml_lines.append(f"        - \"{option}\"")
        
        elif options_type == 'tier_hardcoded':
            for tier in ['0', '1', '2', '3']:
                yaml_lines.append(f"        - \"{tier}\"")
    
    if default_value:
        yaml_lines.append(f"      default: {default_value}")
    
    if required:
        yaml_lines.append("    validations:")
        yaml_lines.append("      required: true")
    
    return '\n'.join(yaml_lines)

def generate_template_yaml(config, fields, data):
    """Generate complete YAML template."""
    
    yaml_content = f"""name: {config['name']}
description: {config['description']}
title: "{config['title']}"
labels: {config['labels']}
body:
"""
    
    for field_def in fields:
        field_yaml = generate_field_yaml(field_def, data)
        yaml_content += field_yaml + "\n\n"
    
    return yaml_content.rstrip() + "\n"

def validate_yaml(content):
    """Validate YAML syntax."""
    try:
        parsed = yaml.safe_load(content)
        return isinstance(parsed, dict) and 'name' in parsed and 'body' in parsed
    except:
        return False

def process_template_pair(template_name, csv_file, py_file, output_dir):
    """Process a single template pair."""
    
    print(f"Processing {template_name}...")
    
    try:
        config, data = load_template_data(py_file)
        if not config:
            print(f"    No TEMPLATE_CONFIG found")
            return False
        
        print(f"    Loaded: {config['name']}")
        
        fields = load_csv_fields(csv_file)
        print(f"    Fields: {len(fields)}")
        
        yaml_content = generate_template_yaml(config, fields, data)
        
        if not validate_yaml(yaml_content):
            print(f"    Invalid YAML generated")
            return False
        
        output_file = output_dir / f"{template_name}.yml"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        print(f"    Generated {template_name}.yml")
        return True
        
    except Exception as e:
        print(f"    Error: {e}")
        return False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate GitHub issue templates')
    parser.add_argument('-t', '--template-dir', type=Path, help='Template directory')
    parser.add_argument('-o', '--output-dir', type=Path, help='Output directory')
    parser.add_argument('--template', type=str, help='Generate specific template')
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_arguments()
    
    print("Per-File Template Generator")
    
    script_dir = Path(__file__).parent
    template_dir = args.template_dir or script_dir / "templates"
    output_dir = args.output_dir or script_dir.parent / "ISSUE_TEMPLATE"
    
    if not template_dir.exists():
        print(f"Template directory not found: {template_dir}")
        return False
    
    output_dir.mkdir(exist_ok=True)
    
    csv_files = list(template_dir.glob('*.csv'))
    if args.template:
        csv_files = [f for f in csv_files if f.stem == args.template]
    
    if not csv_files:
        print("No CSV files found")
        return False
    
    print(f"Processing {len(csv_files)} templates")
    
    success_count = 0
    for csv_file in csv_files:
        template_name = csv_file.stem
        py_file = template_dir / f"{template_name}.py"
        
        if py_file.exists():
            if process_template_pair(template_name, csv_file, py_file, output_dir):
                success_count += 1
    
    print(f"Results: {success_count}/{len(csv_files)} successful")
    return success_count > 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
