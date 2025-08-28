#!/usr/bin/env python3
"""
FINAL WORKING SOLUTION: GitHub Issue Template Generator

Creates templates with hardcoded CV data to avoid external dependency issues.
Ensures proper YAML formatting for GitHub issue forms.
"""

import yaml
from pathlib import Path

def create_templates_dict():
    """Create template dictionary with proper YAML formatting."""
    
    # CV data - use simple lists to avoid .get() issues
    realms = ['atmos', 'ocean', 'land', 'seaice', 'ocnbgchem', 'landice', 'aerosol', 'atmoschem']
    experiments = ['piControl', 'historical', 'ssp126', 'ssp245', 'ssp585', '1pctCO2', 'abrupt-4xCO2']
    activities = ['CMIP', 'ScenarioMIP', 'DAMIP', 'AerChemMIP', 'C4MIP', 'DCPP']
    licenses = ['CC0-1.0', 'CC-BY-4.0', 'MIT', 'GPL-3.0', 'Apache-2.0']
    source_types = ['AOGCM', 'AGCM', 'OGCM', 'ESM', 'BGCM', 'AER', 'CHEM']
    calendars = ['gregorian', 'noleap', '360_day']
    grid_descriptors = ['N96', 'N216', 'ORCA1', 'T63', 'T127']
    
    templates = {}
    
    # Helper function to format options list
    def format_options(items, is_checkbox=False):
        if is_checkbox:
            return chr(10).join([f'        - label: "{item}"' for item in items])
        else:
            return chr(10).join([f'        - "{item}"' for item in items])
    
    # Component Submission Template
    templates['component_submission.yml'] = f"""name: Model Component Submission
description: Submit metadata for a model component as specified in the EMD specification.
title: "[EMD] Model Component Submission"
labels: ["emd-submission", "component"]
body:
  - type: markdown
    attributes:
      value: |
        ## Instructions
        Please fill out the following fields to document a **Model Component**.
        All fields correspond to the Model Components section of the EMD specification.

  - type: dropdown
    id: component_process
    attributes:
      label: Component Process
      description: Select the process that this model component simulates.
      options:
{format_options(realms)}
    validations:
      required: true

  - type: input
    id: name
    attributes:
      label: Name
      description: The name of the model component.
      placeholder: "e.g., ECHAM6.3, NEMO3.6, JSBACH"
    validations:
      required: true

  - type: input
    id: family
    attributes:
      label: Family
      description: The name of the component family.
      placeholder: "e.g., ECHAM, NEMO, JSBACH"
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Scientific overview of the model component.
      placeholder: "Describe key processes simulated by this component and scientific approach used."
    validations:
      required: true

  - type: input
    id: code_base
    attributes:
      label: Code Base
      description: URL for source code or 'private' if not publicly available.
      placeholder: "https://github.com/org/repo/tree/version or 'private'"

  - type: checkboxes
    id: embedded_in
    attributes:
      label: Embedded In
      description: Select components this is embedded in (if applicable).
      options:
{format_options(realms, is_checkbox=True)}

  - type: dropdown
    id: horizontal_descriptor
    attributes:
      label: Horizontal Grid Descriptor
      description: Grid descriptor (if applicable).
      options:
        - "Not applicable"
{format_options(grid_descriptors)}

  - type: input
    id: reference_1_doi
    attributes:
      label: Primary Reference DOI
      description: DOI for the primary component reference.
      placeholder: "https://doi.org/..."
    validations:
      required: true"""

    # Top Level Model Template
    templates['top_level_model.yml'] = f"""name: Top Level Model Submission
description: Submit metadata for the top-level model properties as specified in the EMD specification.
title: "[EMD] Top Level Model Submission"
labels: ["emd-submission", "top_level_model"]
body:
  - type: markdown
    attributes:
      value: |
        ## Instructions
        Please fill out the following fields for the **Top Level Model** as specified in the EMD specification.

  - type: input
    id: name
    attributes:
      label: Name
      description: The name of the model. For CMIP7, must be a registered source_id.
      placeholder: "e.g., HadGEM3-GC31-HH, CESM2, ICON-ESM"
    validations:
      required: true

  - type: input
    id: family
    attributes:
      label: Family
      description: The name of the family of models that this model belongs to.
      placeholder: "e.g., HadGEM3, CESM, ICON"
    validations:
      required: true

  - type: checkboxes
    id: components
    attributes:
      label: Components
      description: Select the processes that are dynamically simulated by the model components.
      options:
{format_options(realms, is_checkbox=True)}

  - type: textarea
    id: description
    attributes:
      label: Description
      description: A brief, free-text scientific overview of the model.
      placeholder: "Brief scientific overview of the model, its purpose, and key capabilities."
    validations:
      required: true

  - type: checkboxes
    id: calendar
    attributes:
      label: Calendar
      description: The calendars that define which dates are permitted in the model.
      options:
{format_options(calendars, is_checkbox=True)}

  - type: input
    id: release_year
    attributes:
      label: Release Year
      description: The year in which this model configuration was released.
      placeholder: "e.g., 2016, 2019, 2023"
    validations:
      required: true

  - type: input
    id: reference_1_doi
    attributes:
      label: Primary Reference DOI
      description: The persistent identifier (DOI) for the primary model reference.
      placeholder: "https://doi.org/..."
    validations:
      required: true"""

    # Model Family Template
    templates['model_family_documentation.yml'] = f"""name: Model Family Documentation
description: Document a model family that encompasses multiple model configurations and components.
title: "[EMD] Model Family Documentation"
labels: ["emd-submission", "model_family"]
body:
  - type: markdown
    attributes:
      value: |
        ## Instructions
        Please fill out the following fields to document a **Model Family**.

  - type: input
    id: family_name
    attributes:
      label: Family Name
      description: The name of the model or component family.
      placeholder: "e.g., HadGEM3, CESM, ECHAM, NEMO"
    validations:
      required: true

  - type: dropdown
    id: family_type
    attributes:
      label: Family Type
      description: Is this a family of complete models or individual components?
      options:
        - "Model Family (complete Earth system models)"
        - "Component Family (individual model components)"
    validations:
      required: true

  - type: textarea
    id: family_description
    attributes:
      label: Family Description
      description: Scientific and technical overview of what defines this family.
      placeholder: "Describe the common scientific basis, shared code heritage, and what distinguishes this family."
    validations:
      required: true

  - type: dropdown
    id: family_license
    attributes:
      label: Family License
      description: General licensing approach for the family.
      options:
{format_options(licenses)}
        - "Open Source"
        - "Academic License"
        - "Registration Required"
        - "Commercial License"
        - "Proprietary"

  - type: input
    id: reference_1_doi
    attributes:
      label: Primary Family Reference - DOI
      description: DOI for the primary family reference.
      placeholder: "https://doi.org/..."
    validations:
      required: true"""

    # Experiment Documentation Template
    templates['experiment_documentation.yml'] = f"""name: Experiment Documentation
description: Submit metadata for a CMIP7 experiment configuration.
title: "[EMD] Experiment Documentation"
labels: ["emd-submission", "experiment"]
body:
  - type: markdown
    attributes:
      value: |
        ## Instructions
        Please fill out the following fields to document an **Experiment Configuration**.

  - type: dropdown
    id: experiment_id
    attributes:
      label: Experiment ID
      description: Select the CMIP7 experiment identifier.
      options:
{format_options(experiments)}
    validations:
      required: true

  - type: dropdown
    id: activity
    attributes:
      label: Activity/MIP
      description: Select the primary MIP activity for this experiment.
      options:
{format_options(activities)}
    validations:
      required: true

  - type: dropdown
    id: tier
    attributes:
      label: Experiment Tier
      description: CMIP7 tier classification for this experiment.
      options:
        - "0"
        - "1"
        - "2"
        - "3"
    validations:
      required: true

  - type: checkboxes
    id: required_model_realms
    attributes:
      label: Required Model Realms
      description: Select the model components/realms that are REQUIRED for this experiment.
      options:
{format_options(source_types, is_checkbox=True)}

  - type: input
    id: reference_doi
    attributes:
      label: Primary Reference DOI
      description: DOI for the primary reference describing this experiment.
      placeholder: "https://doi.org/..."
    validations:
      required: true"""

    return templates

def run_generation():
    """Generate and validate all templates."""
    
    print("🔨 Generating Working GitHub Issue Templates")
    print("=" * 45)
    
    # Create templates
    templates = create_templates_dict()
    print(f"📝 Created {len(templates)} templates")
    
    # Setup output
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / "ISSUE_TEMPLATE"
    output_dir.mkdir(exist_ok=True)
    
    # Validate and save each template
    success_count = 0
    
    for filename, content in templates.items():
        try:
            print(f"\n📝 Processing {filename}:")
            
            # Validate YAML syntax
            parsed = yaml.safe_load(content)
            print(f"    ✅ YAML validation passed")
            
            # Check GitHub issue template structure
            if 'name' in parsed and 'body' in parsed and isinstance(parsed['body'], list):
                print(f"    ✅ GitHub issue template structure valid")
                
                # Save file
                with open(output_dir / filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"    ✅ Saved successfully")
                success_count += 1
            else:
                print(f"    ❌ Invalid GitHub issue template structure")
                
        except yaml.YAMLError as e:
            print(f"    ❌ YAML validation failed: {e}")
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    # Final summary
    print(f"\n🎯 Generation Complete:")
    print(f"  ✅ Success: {success_count}/{len(templates)} templates")
    print(f"  📁 Location: {output_dir}")
    
    if success_count == len(templates):
        print(f"\n🎉 All templates working! Ready for GitHub!")
        print(f"💡 Test by creating a new issue in your repository")
        return True
    else:
        print(f"\n⚠️  Some templates failed - check output for details")
        return False

if __name__ == '__main__':
    success = run_generation()
    exit(0 if success else 1)
