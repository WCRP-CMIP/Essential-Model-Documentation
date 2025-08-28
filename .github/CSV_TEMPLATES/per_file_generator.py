#!/usr/bin/env python3
"""
Per-File Template Generator

Processes each CSV/Python template pair independently.
Python files contain simple data dictionaries that get fed directly to Jinja2.
"""

import csv
import sys
import yaml
from pathlib import Path
from jinja2 import Template

def load_template_data(py_file):
    """Load simple data dictionary from Python file."""
    
    # Execute the Python file and extract data
    namespace = {}
    with open(py_file, 'r', encoding='utf-8') as f:
        exec(f.read(), namespace)
    
    # Extract the data - look for common variable names
    data = {}
    config = {}
    
    # Get template configuration
    if 'TEMPLATE_CONFIG' in namespace:
        config = namespace['TEMPLATE_CONFIG']
    
    # Get data - try different possible names
    if 'DATA' in namespace:
        data = namespace['DATA']
    elif 'TEMPLATE_DATA' in namespace:
        data = namespace['TEMPLATE_DATA']
    elif 'CV_DATA' in namespace:
        data = namespace['CV_DATA']
    
    return config, data

def load_csv_fields(csv_file):
    """Load field definitions from CSV."""
    
    fields = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fields.append(row)
    
    # Sort by field_order
    fields.sort(key=lambda x: int(x['field_order']))
    return fields

def generate_field_yaml(field_def, data):
    """Generate YAML for a single field with minimal logic."""
    
    field_type = field_def['field_type']
    field_id = field_def['field_id']
    label = field_def['label']
    description = field_def['description']
    data_source = field_def['data_source']
    required = field_def['required'].lower() == 'true'
    placeholder = field_def['placeholder']
    options_type = field_def['options_type']
    default_value = field_def['default_value']
    
    # Start field YAML
    yaml_lines = [f"  - type: {field_type}"]
    
    # Markdown fields are special
    if field_type == 'markdown':
        yaml_lines.append("    attributes:")
        
        # Handle multiline markdown
        if '\\n' in description:
            formatted_desc = description.replace('\\n', '\n        ')
            yaml_lines.append("      value: |")
            yaml_lines.append(f"        {formatted_desc}")
        else:
            yaml_lines.append("      value: |")
            yaml_lines.append(f"        {description}")
        
        return '\n'.join(yaml_lines)
    
    # All other field types
    yaml_lines.append(f"    id: {field_id}")
    yaml_lines.append("    attributes:")
    yaml_lines.append(f"      label: {label}")
    
    # Handle description
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
    
    # Handle field-specific attributes
    if field_type in ['input', 'textarea'] and placeholder:
        yaml_lines.append(f"      placeholder: \"{placeholder}\"")
    
    # Handle options for dropdowns and checkboxes
    if field_type in ['dropdown', 'checkboxes'] and data_source != 'none':
        yaml_lines.append("      options:")
        
        # Get data from the data dictionary
        if data_source in data:
            source_data = data[data_source]
            
            if options_type == 'dict_keys':
                if isinstance(source_data, dict):
                    for key in source_data.keys():
                        yaml_lines.append(f"        - \"{key}\"")
            
            elif options_type == 'list':
                if isinstance(source_data, list):
                    for item in source_data:
                        yaml_lines.append(f"        - \"{item}\"")
            
            elif options_type == 'dict_checkbox':
                if isinstance(source_data, dict):
                    for key in source_data.keys():
                        yaml_lines.append(f"        - label: \"{key}\"")
            
            elif options_type == 'list_with_na':
                yaml_lines.append("        - \"Not applicable\"")
                if isinstance(source_data, list):
                    for item in source_data:
                        yaml_lines.append(f"        - \"{item}\"")
        
        # Handle hardcoded options
        elif options_type == 'hardcoded':
            # Look for hardcoded data in the data dict
            hardcoded_key = f"{field_id}_options"
            if hardcoded_key in data:
                for option in data[hardcoded_key]:
                    yaml_lines.append(f"        - \"{option}\"")
        
        # Handle tier options
        elif options_type == 'tier_hardcoded':
            for tier in ['0', '1', '2', '3']:
                yaml_lines.append(f"        - \"{tier}\"")
    
    # Add default value
    if default_value:
        yaml_lines.append(f"      default: {default_value}")
    
    # Add validation
    if required:
        yaml_lines.append("    validations:")
        yaml_lines.append("      required: true")
    
    return '\n'.join(yaml_lines)

def generate_template_yaml(config, fields, data):
    """Generate complete YAML template."""
    
    # Header
    yaml_content = f"""name: {config['name']}
description: {config['description']}
title: "{config['title']}"
labels: {config['labels']}
body:
"""
    
    # Add each field
    for field_def in fields:
        field_yaml = generate_field_yaml(field_def, data)
        yaml_content += field_yaml + "\n\n"
    
    return yaml_content.rstrip() + "\n"

def validate_yaml(content):
    """Simple YAML validation."""
    try:
        parsed = yaml.safe_load(content)
        return isinstance(parsed, dict) and 'name' in parsed and 'body' in parsed
    except:
        return False

def process_template_pair(template_name, csv_file, py_file, output_dir):
    """Process a single template pair."""
    
    print(f"📝 Processing {template_name}...")
    
    try:
        # Load configuration and data
        config, data = load_template_data(py_file)
        if not config:
            print(f"    ❌ No TEMPLATE_CONFIG found in {py_file}")
            return False
        
        print(f"    ✅ Loaded config: {config['name']}")
        print(f"    ✅ Loaded data: {len(data)} items")
        
        # Load fields
        fields = load_csv_fields(csv_file)
        print(f"    ✅ Loaded {len(fields)} fields from CSV")
        
        # Generate YAML
        yaml_content = generate_template_yaml(config, fields, data)
        
        # Validate
        if not validate_yaml(yaml_content):
            print(f"    ❌ Generated invalid YAML")
            return False
        
        # Save file
        output_file = output_dir / f"{template_name}.yml"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        print(f"    ✅ Generated {template_name}.yml ({len(yaml_content)} chars)")
        return True
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def main():
    """Main function - process templates individually."""
    
    print("🔧 Per-File Template Generator")
    print("=" * 30)
    
    # Parse arguments
    if len(sys.argv) >= 3:
        template_dir = Path(sys.argv[1])
        output_dir = Path(sys.argv[2])
    elif len(sys.argv) == 2:
        template_dir = Path(sys.argv[1])
        output_dir = Path.cwd() / "output"
    else:
        script_dir = Path(__file__).parent
        template_dir = script_dir / "templates"
        output_dir = script_dir.parent / "ISSUE_TEMPLATE"
    
    print(f"📁 Template directory: {template_dir}")
    print(f"📁 Output directory: {output_dir}")
    
    # Validate directories
    if not template_dir.exists():
        print(f"❌ Template directory not found: {template_dir}")
        return False
    
    output_dir.mkdir(exist_ok=True)
    
    # Find CSV files and process each one
    csv_files = list(template_dir.glob('*.csv'))
    
    if not csv_files:
        print("❌ No CSV files found")
        return False
    
    print(f"🔍 Found {len(csv_files)} CSV files")
    
    success_count = 0
    
    for csv_file in csv_files:
        template_name = csv_file.stem
        py_file = template_dir / f"{template_name}.py"
        
        if not py_file.exists():
            print(f"⚠️  No Python file for {csv_file.name}")
            continue
        
        # Process this template pair
        if process_template_pair(template_name, csv_file, py_file, output_dir):
            success_count += 1
    
    # Summary
    print(f"\n🎯 Results:")
    print(f"  ✅ Success: {success_count}/{len(csv_files)}")
    print(f"  📁 Output: {output_dir}")
    
    if success_count > 0:
        print(f"🎉 Templates generated successfully!")
        return True
    else:
        print(f"❌ No templates generated")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
