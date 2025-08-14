#!/usr/bin/env python3
"""
Usage Examples for Per-File Template Generator
"""

if __name__ == '__main__':
    print("🚀 Per-File Template Generator Usage Examples")
    print("=" * 50)
    
    print("\n📋 Basic Usage:")
    print("  python per_file_generator.py")
    print("    → Uses default directories: ./templates → ../ISSUE_TEMPLATE")
    
    print("\n📁 Custom Directories:")
    print("  python per_file_generator.py -t ./my_templates")
    print("    → Custom template dir, default output")
    print("  python per_file_generator.py -t ./templates -o ./output") 
    print("    → Custom both directories")
    
    print("\n🔍 List Available Templates:")
    print("  python per_file_generator.py --list")
    print("    → Shows all template pairs with status")
    
    print("\n🎯 Generate Specific Template:")
    print("  python per_file_generator.py --template component_submission")
    print("    → Only generates component_submission template")
    
    print("\n🧪 Validation Only:")
    print("  python per_file_generator.py --validate-only")
    print("    → Tests all templates without generating files")
    print("  python per_file_generator.py --template model_family --validate-only")
    print("    → Validates only model_family template")
    
    print("\n🔍 Verbose Output:")
    print("  python per_file_generator.py -v")
    print("    → Shows detailed processing information")
    
    print("\n💡 Help:")
    print("  python per_file_generator.py --help")
    print("    → Shows all available options")
    
    print("\n🎯 Common Workflows:")
    print("  # Check what templates are available")
    print("  python per_file_generator.py --list")
    print("  ")
    print("  # Test a specific template")
    print("  python per_file_generator.py --template component_submission --validate-only")
    print("  ")
    print("  # Generate all templates")
    print("  python per_file_generator.py")
    print("  ")
    print("  # Generate to custom location")
    print("  python per_file_generator.py -o /path/to/github/repo/.github/ISSUE_TEMPLATE")
