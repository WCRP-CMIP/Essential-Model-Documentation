#!/usr/bin/env python3
"""
Debug script to check how CSV descriptions are being processed
"""

import csv
from pathlib import Path

def debug_csv_descriptions():
    """Debug CSV description processing."""
    
    print("🔍 Debugging CSV Description Processing")
    print("=" * 40)
    
    script_dir = Path(__file__).parent
    csv_file = script_dir / "template_definitions.csv"
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            description = row['description']
            if description and ('\\n' in description or len(description) > 50):
                print(f"\n📋 Field: {row['field_id']}")
                print(f"Raw CSV content: {repr(description)}")
                print(f"Contains \\\\n: {'\\\\n' in description}")
                print(f"Contains \\n: {'\\n' in description}")
                
                # Test the processing logic
                if '\\\\n' in description or '\\n' in description:
                    formatted = description.replace('\\\\n', '\\n').replace('\\n', '\\n        ')
                    print(f"After processing: {repr(formatted)}")
                    
                    print("Generated YAML would be:")
                    yaml_output = f"      description: |\\n        {formatted}"
                    print(yaml_output)
                    print("-" * 30)

def test_manual_replacement():
    """Test manual string replacement."""
    
    print("\\n🧪 Manual Replacement Test")
    
    # Test different input formats
    test_cases = [
        "Line 1\\nLine 2\\n\\nLine 3",  # Escaped backslash-n
        "Line 1\\nLine 2\\n\\nLine 3",   # Literal backslash-n  
        "Line 1\nLine 2\n\nLine 3",     # Actual newlines
    ]
    
    for i, test_str in enumerate(test_cases, 1):
        print(f"\\nTest case {i}: {repr(test_str)}")
        
        # Apply the same logic as the generator
        if '\\\\n' in test_str or '\\n' in test_str:
            formatted = test_str.replace('\\\\n', '\\n').replace('\\n', '\\n        ')
            print(f"Formatted: {repr(formatted)}")
            print("YAML output:")
            print(f"      description: |\\n        {formatted}")
        else:
            print("No newlines detected")

if __name__ == '__main__':
    debug_csv_descriptions()
    test_manual_replacement()
