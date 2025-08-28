#!/usr/bin/env python3
"""
Quick test of the multiline description fix
"""

def test_newline_replacement():
    """Test the newline replacement logic."""
    
    print("🧪 Testing Newline Replacement Logic")
    print("=" * 40)
    
    # Test the exact string from the CSV
    csv_description = "A short phrase that can help in interpreting the unique\\nexperiment_id's.\\n\\nAs examples, the CMIP6 titles are listed [here](https://wcrp-cmip.github.io/CMIP6_CVs/docs/CMIP6_experiment_id.html) in the third column labeled \"experiments\"."
    
    print("📝 Original CSV description:")
    print(f"'{csv_description}'")
    print(f"Length: {len(csv_description)}")
    print(f"Contains \\n: {'\\n' in csv_description}")
    print()
    
    # Apply the processing logic
    if '\\n' in csv_description:
        formatted_description = csv_description.replace('\\n', '\n        ')
        yaml_output = f"      description: |\n        {formatted_description}"
        
        print("🔨 Generated YAML:")
        print(yaml_output)
        print()
        
        print("📋 How it will appear in GitHub:")
        lines = formatted_description.split('\n        ')
        for line in lines:
            print(f"        {line}")
    else:
        print("❌ No \\n found in description")

if __name__ == '__main__':
    test_newline_replacement()
