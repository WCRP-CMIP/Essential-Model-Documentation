#!/usr/bin/env python3
"""
Universal Template Generator

Reads paired CSV and Python files to generate GitHub issue templates.
Takes template directory and output directory as arguments.

Usage:
    python universal_generator.py [template_dir] [output_dir]
    
Template Structure:
    template_dir/
    ├── template_name.csv      # Field definitions
    ├── template_name.py       # Template configuration class
    └── ...

The generator:
1. Finds all .csv/.py pairs in template directory
2. Loads template configuration from Python class
3. Reads field definitions from CSV
4. Generates YAML issue templates
5. Validates output and saves to output directory
"""

import csv
import sys
import yaml
import importlib.util
from pathlib import Path
from collections import defaultdict

def collect_all_cv_data(template_pairs):
    """Collect all CV data from template Python files."""
    
    all_cv_data = {}
    
    for template_name, csv_file, py_file in template_pairs:
        try:
            # Load the template module
            spec = importlib.util.spec_from_file_location("template_config", py_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get CV data from template class or module
            template_cv_data = {}
            
            # Try different ways to get CV_DATA
            if hasattr(module, 'CV_DATA'):
                template_cv_data = module.CV_DATA
            else:
                # Try to find a class with CV_DATA
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if hasattr(attr, 'CV_DATA'):
                        template_cv_data = attr.CV_DATA
                        break
            
            # Merge this template's CV data into the global collection
            for key, value in template_cv_data.items():
                if key in all_cv_data:
                    # If key already exists, merge (prefer newer data)
                    if isinstance(value, dict) and isinstance(all_cv_data[key], dict):
                        all_cv_data[key].update(value)
                    elif isinstance(value, list) and isinstance(all_cv_data[key], list):
                        # Merge lists, removing duplicates while preserving order
                        existing_items = set(all_cv_data[key])
                        for item in value:
                            if item not in existing_items:
                                all_cv_data[key].append(item)
                                existing_items.add(item)
                    else:
                        all_cv_data[key] = value
                else:
                    all_cv_data[key] = value
                    
        except Exception as e:
            print(f"⚠️  Warning: Could not load CV data from {py_file}: {e}")
    
    return all_cv_data

def find_template_pairs(template_dir):
    """Find all CSV/Python template pairs in directory."""
    
    template_dir = Path(template_dir)
    csv_files = list(template_dir.glob('*.csv'))
    py_files = list(template_dir.glob('*.py'))
    
    # Find matching pairs
    pairs = []
    for csv_file in csv_files:
        template_name = csv_file.stem
        py_file = template_dir / f"{template_name}.py"
        
        if py_file.exists():
            pairs.append((template_name, csv_file, py_file))
        else:
            print(f"⚠️  CSV file {csv_file.name} has no matching Python file")
    
    # Check for orphaned Python files
    for py_file in py_files:
        template_name = py_file.stem
        csv_file = template_dir / f"{template_name}.csv"
        if not csv_file.exists():
            print(f"⚠️  Python file {py_file.name} has no matching CSV file")
    
    return pairs

def load_template_config(py_file):
    """Load template configuration from Python file."""
    
    spec = importlib.util.spec_from_file_location("template_config", py_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Try to get configuration from different possible locations
    if hasattr(module, 'TEMPLATE_INFO'):
        config = module.TEMPLATE_INFO
    elif hasattr(module, 'TEMPLATE_CONFIG'):
        config = module.TEMPLATE_CONFIG
    else:
        # Try to find a class with TEMPLATE_CONFIG
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if hasattr(attr, 'TEMPLATE_CONFIG'):
                config = attr.TEMPLATE_CONFIG
                break
        else:
            raise ValueError(f"No template configuration found in {py_file}")
    
    # Also get hardcoded options if available
    hardcoded_options = {}
    if hasattr(module, 'HARDCODED_OPTIONS'):
        hardcoded_options = module.HARDCODED_OPTIONS
    else:
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if hasattr(attr, 'HARDCODED_OPTIONS'):
                hardcoded_options = attr.HARDCODED_OPTIONS
                break
    
    return config, hardcoded_options

def load_csv_fields(csv_file):
    """Load field definitions from CSV file."""
    
    fields = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fields.append(row)
    
    # Sort by field_order
    fields.sort(key=lambda x: int(x['field_order']))
    return fields

def generate_field_yaml(field_def, cv_data, hardcoded_options):
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
    
    # Start building the field YAML
    field_yaml = f"  - type: {field_type}\n"
    
    # Handle markdown fields differently
    if field_type == 'markdown':
        field_yaml += f"    attributes:\n"
        # Handle multiline descriptions in markdown
        if '\\n' in description:
            formatted_description = description.replace('\\n', '\n        ')
            field_yaml += f"      value: |\n        {formatted_description}\n"
        else:
            field_yaml += f"      value: |\n        {description}\n"
        return field_yaml
    
    # For all other field types
    field_yaml += f"    id: {field_id}\n"
    field_yaml += f"    attributes:\n"
    field_yaml += f"      label: {label}\n"
    
    if description:
        # Handle multiline descriptions
        if '\\n' in description:
            formatted_description = description.replace('\\n', '\n        ')
            field_yaml += f"      description: |\n        {formatted_description}\n"
        elif '\n' in description:
            formatted_description = description.replace('\n', '\n        ')
            field_yaml += f"      description: |\n        {formatted_description}\n"
        elif '**' in description or len(description) > 80:
            field_yaml += f"      description: |\n        {description}\n"
        else:
            field_yaml += f"      description: {description}\n"
    
    # Handle field-specific attributes
    if field_type in ['input', 'textarea']:
        if placeholder:
            field_yaml += f"      placeholder: \"{placeholder}\"\n"
            
    elif field_type == 'dropdown':
        field_yaml += f"      options:\n"
        
        # Generate options based on type
        if options_type == 'dict_keys' and data_source != 'none':
            if data_source in cv_data:
                field_yaml += f"        # Generated from {data_source}\n"
                for key in cv_data[data_source].keys():
                    field_yaml += f"        - \"{key}\"\n"
        elif options_type == 'list' and data_source != 'none':
            if data_source in cv_data:
                field_yaml += f"        # Generated from {data_source}\n"
                for item in cv_data[data_source]:
                    field_yaml += f"        - \"{item}\"\n"
        elif options_type == 'list_with_na':
            field_yaml += f"        - \"Not applicable\"\n"
            if data_source != 'none' and data_source in cv_data:
                for item in cv_data[data_source]:
                    field_yaml += f"        - \"{item}\"\n"
        elif options_type == 'dict_with_extra':
            if data_source != 'none' and data_source in cv_data:
                for key in cv_data[data_source].keys():
                    field_yaml += f"        - \"{key}\"\n"
            field_yaml += f"        - \"Open Source\"\n"
            field_yaml += f"        - \"Registration Required\"\n"
            field_yaml += f"        - \"Proprietary\"\n"
        elif options_type == 'hardcoded' or options_type.endswith('_hardcoded'):
            # Use hardcoded options from template config
            if field_id in hardcoded_options:
                for option in hardcoded_options[field_id]:
                    field_yaml += f"        - \"{option}\"\n"
            elif options_type == 'tier_hardcoded':
                for tier in ['0', '1', '2', '3']:
                    field_yaml += f"        - \"{tier}\"\n"
        
        if default_value:
            field_yaml += f"      default: {default_value}\n"
            
    elif field_type == 'checkboxes':
        field_yaml += f"      options:\n"
        
        if options_type == 'dict_checkbox' and data_source != 'none':
            if data_source in cv_data:
                field_yaml += f"        # Generated from {data_source}\n"
                for key in cv_data[data_source].keys():
                    field_yaml += f"        - label: \"{key}\"\n"
    
    # Add validation section if required
    if required:
        field_yaml += f"    validations:\n"
        field_yaml += f"      required: true\n"
    
    return field_yaml

def generate_template_yaml(template_name, config, fields, cv_data, hardcoded_options):
    """Generate complete YAML template."""
    
    # Generate header
    yaml_content = f"""name: {config['name']}
description: {config['description']}
title: "{config['title']}"
labels: {config['labels']}
body:
"""
    
    # Generate each field
    for field_def in fields:
        field_yaml = generate_field_yaml(field_def, cv_data, hardcoded_options)
        yaml_content += field_yaml + "\n"
    
    return yaml_content.rstrip() + "\n"

def validate_yaml_output(content):
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
    """Main function with command line argument support."""
    
    print("🏗️  Universal Template Generator")
    print("=" * 35)
    
    # Parse command line arguments
    if len(sys.argv) >= 3:
        template_dir = Path(sys.argv[1])
        output_dir = Path(sys.argv[2])
    elif len(sys.argv) == 2:
        template_dir = Path(sys.argv[1])
        output_dir = Path.cwd() / "output"
    else:
        # Default paths
        script_dir = Path(__file__).parent
        template_dir = script_dir / "templates"
        output_dir = script_dir.parent / "ISSUE_TEMPLATE"
    
    print(f"📁 Template directory: {template_dir}")
    print(f"📁 Output directory: {output_dir}")
    
    # Validate directories
    if not template_dir.exists():
        print(f"❌ Template directory does not exist: {template_dir}")
        return False
    
    output_dir.mkdir(exist_ok=True)
    
    # Find template pairs
    template_pairs = find_template_pairs(template_dir)
    print(f"🔍 Found {len(template_pairs)} template pairs")
    
    if not template_pairs:
        print("❌ No valid template pairs found")
        return False
    
    # Collect all CV data from templates
    cv_data = collect_all_cv_data(template_pairs)
    print(f"📊 Collected CV data: {len([k for k, v in cv_data.items() if isinstance(v, dict)])} dicts, {len([k for k, v in cv_data.items() if isinstance(v, list)])} lists")
    
    # Process each template
    success_count = 0
    
    for template_name, csv_file, py_file in template_pairs:
        try:
            print(f"\n📝 Processing {template_name}:")
            
            # Load configuration
            config, hardcoded_options = load_template_config(py_file)
            print(f"    ✅ Loaded config: {config['name']}")
            
            # Load fields
            fields = load_csv_fields(csv_file)
            print(f"    ✅ Loaded {len(fields)} fields from CSV")
            
            # Generate YAML
            yaml_content = generate_template_yaml(template_name, config, fields, cv_data, hardcoded_options)
            
            # Validate
            is_valid, message = validate_yaml_output(yaml_content)
            
            if is_valid:
                # Save file
                output_file = output_dir / f"{template_name}.yml"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
                print(f"    ✅ Generated {template_name}.yml ({len(yaml_content)} chars)")
                success_count += 1
            else:
                print(f"    ❌ Validation failed: {message}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    # Summary
    print(f"\n🎯 Generation Complete:")
    print(f"  ✅ Success: {success_count}/{len(template_pairs)}")
    print(f"  📁 Output: {output_dir}")
    
    if success_count == len(template_pairs):
        print(f"\n🎉 All templates generated successfully!")
        return True
    else:
        print(f"\n⚠️  Some templates failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
