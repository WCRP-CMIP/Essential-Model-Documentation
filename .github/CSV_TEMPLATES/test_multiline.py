#!/usr/bin/env python3
"""
Test script to demonstrate multiline description handling
"""

def test_multiline_formatting():
    """Test the multiline description formatting."""
    
    # Example from CSV with \n characters
    csv_description = "A short phrase that can help in interpreting the unique\\nexperiment_id's.\\n\\nAs examples, the CMIP6 titles are listed [here](https://wcrp-cmip.github.io/CMIP6_CVs/docs/CMIP6_experiment_id.html) in the third column labeled \"experiments\"."
    
    print("📝 Original CSV description:")
    print(repr(csv_description))
    print()
    
    # Process like the generator does
    if '\\n' in csv_description:
        formatted_description = csv_description.replace('\\n', '\n        ')
        yaml_output = f"      description: |\n        {formatted_description}\n"
    
    print("🔨 Generated YAML output:")
    print(yaml_output)
    
    print("📋 Final rendered result would be:")
    print("      description: |")
    print("        A short phrase that can help in interpreting the unique")
    print("        experiment_id's.")
    print("        ")
    print("        As examples, the CMIP6 titles are listed [here](https://wcrp-cmip.github.io/CMIP6_CVs/docs/CMIP6_experiment_id.html) in the third column labeled \"experiments\".")

if __name__ == '__main__':
    test_multiline_formatting()
