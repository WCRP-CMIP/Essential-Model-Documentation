#!/usr/bin/env python3
"""
FINAL FIX: Template generator with proper YAML formatting
Addresses the line break/indentation issues in Jinja2 templates.
"""

import json
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def create_template_data():
    """Create properly structured template data."""
    
    # Use simple fallback data to avoid external dependencies
    return {
        # Dicts for .keys() iteration
        'realms': {
            'atmos': {'id': 'atmos', 'validation-key': 'atmos'},
            'ocean': {'id': 'ocean', 'validation-key': 'ocean'},
            'land': {'id': 'land', 'validation-key': 'land'},
            'seaice': {'id': 'seaice', 'validation-key': 'seaice'},
            'ocnbgchem': {'id': 'ocnbgchem', 'validation-key': 'ocnbgchem'},
            'landice': {'id': 'landice', 'validation-key': 'landice'}
        },
        'experiments': {
            'piControl': {'id': 'piControl'},
            'historical': {'id': 'historical'},
            'ssp126': {'id': 'ssp126'},
            'ssp245': {'id': 'ssp245'},
            'ssp585': {'id': 'ssp585'}
        },
        'activities': {
            'CMIP': {'id': 'CMIP'},
            'ScenarioMIP': {'id': 'ScenarioMIP'},
            'DAMIP': {'id': 'DAMIP'}
        },
        'licenses': {
            'CC0-1.0': {'id': 'CC0-1.0'},
            'CC-BY-4.0': {'id': 'CC-BY-4.0'},
            'MIT': {'id': 'MIT'}
        },
        'source_types': {
            'AOGCM': {'id': 'AOGCM'},
            'AGCM': {'id': 'AGCM'},
            'ESM': {'id': 'ESM'}
        },
        'institutions': {
            'NCAR': {'id': 'NCAR'},
            'MOHC': {'id': 'MOHC'}
        },
        'horizontal_grid_types': {
            'regular_lat_lon': {'id': 'regular_lat_lon', 'validation-key': 'regular_lat_lon'},
            'gaussian': {'id': 'gaussian', 'validation-key': 'gaussian'}
        },
        'horizontal_regions': {
            'global': {'id': 'global', 'validation-key': 'global'}
        },
        'vertical_coordinates': {
            'hybrid_sigma_pressure': {'id': 'hybrid_sigma_pressure', 'validation-key': 'hybrid_sigma_pressure'},
            'pressure': {'id': 'pressure', 'validation-key': 'pressure'}
        },
        'vertical_units': {
            'Pa': {'id': 'Pa', 'validation-key': 'Pa'},
            'm': {'id': 'm', 'validation-key': 'm'}
        },
        'calendars': {
            'gregorian': {'id': 'gregorian', 'validation-key': 'gregorian'},
            'noleap': {'id': 'noleap', 'validation-key': 'noleap'}
        },
        
        # Lists for simple iteration
        'grid_descriptors': ["N96", "N216", "ORCA1", "T63"],
        'grid_mappings': ["latitude_longitude", "polar_stereographic"],
        'grid_arrangements': ["arakawa_A", "arakawa_C"],
        'nominal_resolutions': ["50 km", "100 km"],
        'scientific_domains': ["Atmospheric dynamics", "Ocean circulation"],
        'typical_applications': ["Climate projections", "Process studies"]
    }

def create_working_templates():
    """Create templates with corrected Jinja2 syntax."""
    
    templates = {}
    
    # Simple component template that works
    templates['component_submission.j2'] = '''name: Model Component Submission
description: Submit metadata for a model component as specified in the EMD specification.
title: "[EMD] Model Component Submission"
labels: ["emd-submission", "component"]
body:
  - type: markdown
    attributes:
      value: |
        ## Instructions
        Please fill out the following fields to document a **Model Component**.

  - type: dropdown
    id: component_process
    attributes:
      label: Component Process
      description: Select the process that this model component simulates.
      options:
{% for key in realms.keys() -%}
        - "{{ key }}"
{% endfor %}
    validations:
      required: true

  - type: input
    id: name
    attributes:
      label: Name
      description: The name of the model component.
      placeholder: "e.g., ECHAM6.3, NEMO3.6"
    validations:
      required: true

  - type: input
    id: family
    attributes:
      label: Family
      description: The name of the component family.
      placeholder: "e.g., ECHAM, NEMO"
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Scientific overview of the model component.
      placeholder: "Describe key processes simulated by this component."
    validations:
      required: true

  - type: input
    id: reference_1_doi
    attributes:
      label: Primary Reference DOI
      description: DOI for the primary component reference.
      placeholder: "https://doi.org/..."
    validations:
      required: true'''

    # Simple top level model template
    templates['top_level_model.j2'] = '''name: Top Level Model Submission
description: Submit metadata for the top-level model properties.
title: "[EMD] Top Level Model Submission"
labels: ["emd-submission", "top_level_model"]
body:
  - type: markdown
    attributes:
      value: |
        ## Instructions
        Please fill out the following fields for the **Top Level Model**.

  - type: input
    id: name
    attributes:
      label: Name
      description: The name of the model.
      placeholder: "e.g., HadGEM3-GC31-HH, CESM2"
    validations:
      required: true

  - type: input
    id: family
    attributes:
      label: Family
      description: The name of the model family.
      placeholder: "e.g., HadGEM3, CESM"
    validations:
      required: true

  - type: checkboxes
    id: components
    attributes:
      label: Components
      description: Select the processes dynamically simulated by the model.
      options:
{% for key in realms.keys() -%}
        - label: "{{ key }}"
{% endfor %}

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Scientific overview of the model.
      placeholder: "Brief scientific overview of the model and its capabilities."
    validations:
      required: true

  - type: input
    id: release_year
    attributes:
      label: Release Year
      description: Year when this model configuration was released.
      placeholder: "e.g., 2019, 2023"
    validations:
      required: true

  - type: input
    id: reference_1_doi
    attributes:
      label: Primary Reference DOI
      description: DOI for the primary model reference.
      placeholder: "https://doi.org/..."
    validations:
      required: true'''

    # Simple model family template
    templates['model_family_documentation.j2'] = '''name: Model Family Documentation
description: Document a model family.
title: "[EMD] Model Family Documentation"
labels: ["emd-submission", "model_family"]
body:
  - type: markdown
    attributes:
      value: |
        ## Instructions
        Please document a **Model Family**.

  - type: input
    id: family_name
    attributes:
      label: Family Name
      description: Name of the model family.
      placeholder: "e.g., HadGEM3, CESM"
    validations:
      required: true

  - type: dropdown
    id: family_type
    attributes:
      label: Family Type
      description: Type of family.
      options:
        - "Model Family (complete Earth system models)"
        - "Component Family (individual model components)"
    validations:
      required: true

  - type: textarea
    id: family_description
    attributes:
      label: Family Description
      description: Scientific overview of the family.
      placeholder: "Describe what defines this family."
    validations:
      required: true

  - type: dropdown
    id: family_license
    attributes:
      label: Family License
      description: General licensing approach.
      options:
{% for key in licenses.keys() -%}
        - "{{ key }}"
{% endfor %}
        - "Open Source"
        - "Registration Required"
        - "Proprietary"

  - type: input
    id: reference_1_doi
    attributes:
      label: Primary Reference DOI
      description: DOI for the primary family reference.
      placeholder: "https://doi.org/..."
    validations:
      required: true'''

    return templates

def main():
    """Generate working templates."""
    
    print("🔨 FINAL FIX: Generating Working GitHub Issue Templates")
    print("=" * 55)
    
    # Create template data
    template_data = create_template_data()
    print(f"📊 Template data ready with {len(template_data)} categories")
    
    # Create working templates
    working_templates = create_working_templates()
    print(f"📝 Created {len(working_templates)} working templates")
    
    # Setup output
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / "ISSUE_TEMPLATE"
    output_dir.mkdir(exist_ok=True)
    
    # Generate templates
    success_count = 0
    
    for template_name, template_content in working_templates.items():
        try:
            print(f"\n🔨 Processing {template_name}:")
            
            # Create Jinja2 template
            from jinja2 import Template
            template = Template(template_content)
            
            # Render
            rendered = template.render(**template_data)
            
            # Validate YAML
            try:
                parsed = yaml.safe_load(rendered)
                print(f"    ✅ YAML validation passed")
                
                # Save
                output_file = template_name.replace('.j2', '.yml')
                with open(output_dir / output_file, 'w', encoding='utf-8') as f:
                    f.write(rendered)
                
                print(f"    ✅ Saved {output_file}")
                success_count += 1
                
            except yaml.YAMLError as e:
                print(f"    ❌ YAML error: {e}")
                
        except Exception as e:
            print(f"    ❌ Template error: {e}")
    
    print(f"\n🎉 Success! Generated {success_count} working templates")
    print(f"📁 Output: {output_dir}")
    
    if success_count > 0:
        print("\n🚀 Templates are ready for GitHub!")
        print("   Test by creating a new issue in your repository")

if __name__ == '__main__':
    main()
