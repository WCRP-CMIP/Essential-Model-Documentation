#!/usr/bin/env python3
"""
Regenerate missing CRS strings in model JSON files.

Usage:
    python regenerate_crs.py                    # Process all model files
    python regenerate_crs.py model1.json model2.json  # Process specific files
"""

import os
import sys
import json
import glob
from pathlib import Path

# Import CRS utilities
from cmipld.utils import crs as _crs


def _norm_component(s: str) -> str:
    """Normalize component names to CV slugs."""
    _COMPONENT_NORM = {
        'sea ice':                     'sea-ice',
        'land surface and subsurface': 'land-surface',
        'land surface':                'land-surface',
        'land ice':                    'land-ice',
        'ocean biogeochemistry':       'ocean-biogeochemistry',
        'atmospheric chemistry':       'atmospheric-chemistry',
    }
    sl = s.strip().lower()
    return _COMPONENT_NORM.get(sl, sl.replace(' ', '_'))


def load_model_json(filepath: str) -> dict:
    """Load a model JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_model_json(filepath: str, data: dict) -> None:
    """Save a model JSON file with pretty formatting."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')  # Add trailing newline


def regenerate_crs_for_model(data: dict, model_id: str) -> tuple[bool, str]:
    """
    Attempt to regenerate CRS for a model record.
    
    Returns: (success: bool, message: str)
    """
    # Check if CRS already exists
    if 'crs' in data and data['crs']:
        return False, f"  {model_id}: CRS already present"
    
    # Extract required fields for CRS generation
    dynamic = [_norm_component(c) for c in data.get('dynamic_components', [])]
    prescribed = [_norm_component(c) for c in data.get('prescribed_components', [])]
    
    # Parse embedded components (should already be normalized)
    embedded_pairs = data.get('embedded_components', [])
    
    # Parse coupling groups (should already be normalized)
    coupling_groups = data.get('coupled_components', [])
    
    # Validate CRS
    crs_errors = _crs.validate(dynamic, embedded_pairs, coupling_groups, prescribed=prescribed)
    
    if crs_errors:
        msg = f"  {model_id}: CRS validation failed:\n"
        for error in crs_errors:
            msg += f"    - {error}\n"
        return False, msg
    
    # Build CRS
    try:
        crs_string = _crs.build(dynamic, embedded_pairs, coupling_groups, prescribed=prescribed)
        data['crs'] = crs_string
        return True, f"  ✓ {model_id}: Generated CRS = {crs_string}"
    except Exception as e:
        return False, f"  ✗ {model_id}: Error building CRS: {str(e)}"


def main():
    # Determine repo root and model directory
    script_dir = Path(__file__).parent.parent.parent
    model_dir = script_dir / 'model'
    
    if not model_dir.exists():
        print(f"Error: model directory not found at {model_dir}")
        sys.exit(1)
    
    # Get list of files to process
    if len(sys.argv) > 1:
        # Process specific files passed as arguments
        files_to_process = []
        for arg in sys.argv[1:]:
            # Support both full paths and just filenames
            if os.path.isabs(arg):
                files_to_process.append(arg)
            else:
                full_path = model_dir / arg
                if full_path.exists():
                    files_to_process.append(str(full_path))
                else:
                    print(f"Warning: File not found: {full_path}")
    else:
        # Process all model JSON files
        files_to_process = sorted(glob.glob(str(model_dir / '*.json')))
    
    if not files_to_process:
        print("No model files to process")
        return
    
    print(f"Processing {len(files_to_process)} model file(s)...\n")
    
    updated_files = []
    failed_files = []
    skipped_files = []
    
    for filepath in files_to_process:
        model_id = Path(filepath).stem
        
        try:
            data = load_model_json(filepath)
            success, message = regenerate_crs_for_model(data, model_id)
            print(message)
            
            if success:
                save_model_json(filepath, data)
                updated_files.append(model_id)
            elif "already present" in message:
                skipped_files.append(model_id)
            else:
                failed_files.append(model_id)
        
        except json.JSONDecodeError as e:
            print(f"  ✗ {model_id}: Invalid JSON: {str(e)}")
            failed_files.append(model_id)
        except Exception as e:
            print(f"  ✗ {model_id}: Unexpected error: {str(e)}")
            failed_files.append(model_id)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Updated:  {len(updated_files)} file(s)")
    if updated_files:
        for f in updated_files:
            print(f"  • {f}")
    print(f"Skipped:  {len(skipped_files)} file(s) (CRS already present)")
    print(f"Failed:   {len(failed_files)} file(s)")
    if failed_files:
        for f in failed_files:
            print(f"  • {f}")
    
    # Exit with error if any failures
    if failed_files:
        sys.exit(1)


if __name__ == '__main__':
    main()
