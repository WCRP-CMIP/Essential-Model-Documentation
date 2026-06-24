#!/usr/bin/env python3
"""
Grid Type Validator & Converter

Scans horizontal_grid_cell folder and validates that grid_type entries
use validation_key format instead of ui_label format. Generates a report
and optionally fixes issues.

Usage:
    python validate_grid_types.py [--fix] [--report]
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class GridTypeValidator:
    """Validates and converts grid type references."""
    
    # Valid grid type validation_keys (from the graph JSON)
    VALID_GRID_TYPES = {
        'rotated-pole',
        'unstructured-triangular',
        'cubic-octahedral-spectral-reduced-gaussian',
        'unstructured-polygonal',
        'reduced-gaussian',
        'yin-yang',
        'spectral-gaussian',
        'icosahedral-geodesic-dual',
        'linear-spectral-gaussian',
        'cubed-sphere',
        'spectral-reduced-gaussian',
        'icosahedral-geodesic',
        'hierarchical-discrete-global-grid',
        'unstructured',
        'stretched',
        'regular-latitude-longitude',
        'displaced-pole',
        'icosahedral',
        'tripolar',
        'unstructured-quadrilateral',
        'plane-projection',
        'regular-gaussian',
        'quadratic-spectral-gaussian',
    }
    
    # Map ui_label to validation_key for common conversions
    LABEL_TO_KEY = {
        'Rotated Pole': 'rotated-pole',
        'Unstructured Triangular': 'unstructured-triangular',
        'Cubic Octahedral Spectral Reduced Gaussian': 'cubic-octahedral-spectral-reduced-gaussian',
        'Unstructured Polygonal': 'unstructured-polygonal',
        'Reduced Gaussian': 'reduced-gaussian',
        'Yin-Yang': 'yin-yang',
        'Spectral Gaussian': 'spectral-gaussian',
        'Icosahedral Geodesic Dual': 'icosahedral-geodesic-dual',
        'Linear Spectral Gaussian': 'linear-spectral-gaussian',
        'Cubed Sphere': 'cubed-sphere',
        'Spectral Reduced Gaussian': 'spectral-reduced-gaussian',
        'Icosahedral Geodesic': 'icosahedral-geodesic',
        'Hierarchical Discrete Global Grid': 'hierarchical-discrete-global-grid',
        'Unstructured': 'unstructured',
        'Stretched': 'stretched',
        'Regular Latitude-Longitude': 'regular-latitude-longitude',
        'Displaced Pole': 'displaced-pole',
        'Icosahedral': 'icosahedral',
        'Tripolar': 'tripolar',
        'Unstructured Quadrilateral': 'unstructured-quadrilateral',
        'Plane Projection': 'plane-projection',
        'Regular Gaussian': 'regular-gaussian',
        'Quadratic Spectral Gaussian': 'quadratic-spectral-gaussian',
    }
    
    def __init__(self, root_dir: str = '.'):
        """Initialize validator."""
        self.root_dir = Path(root_dir)
        self.grid_cell_dir = self.root_dir / 'horizontal_grid_cell'
        self.results = {
            'valid': [],
            'invalid': [],
            'converted': [],
            'errors': []
        }
    
    def validate_file(self, filepath: Path) -> Tuple[bool, Dict]:
        """
        Validate a single grid cell JSON file.
        
        Returns:
            Tuple of (is_valid, info_dict)
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            return False, {
                'file': str(filepath.name),
                'error': f'Failed to read JSON: {e}'
            }
        
        grid_type = data.get('grid_type', '')
        validation_key = data.get('validation_key', '')
        
        info = {
            'file': filepath.name,
            'validation_key': validation_key,
            'grid_type': grid_type,
        }
        
        # Check if grid_type is valid (already in validation_key format)
        if grid_type in self.VALID_GRID_TYPES:
            return True, info
        
        # Check if it's a ui_label that can be converted
        if grid_type in self.LABEL_TO_KEY:
            info['needs_conversion'] = True
            info['should_be'] = self.LABEL_TO_KEY[grid_type]
            return False, info
        
        # Invalid/unknown
        info['error'] = f'Unknown grid_type: {grid_type}'
        return False, info
    
    def run_validation(self) -> Dict:
        """Run validation on all grid cell files."""
        if not self.grid_cell_dir.exists():
            print(f"❌ Grid cell directory not found: {self.grid_cell_dir}")
            return self.results
        
        json_files = sorted(self.grid_cell_dir.glob('g*.json'))
        
        if not json_files:
            print("⚠ No grid cell files found")
            return self.results
        
        print(f"📋 Validating {len(json_files)} grid cell files...")
        
        for filepath in json_files:
            is_valid, info = self.validate_file(filepath)
            
            if is_valid:
                self.results['valid'].append(info)
            elif info.get('needs_conversion'):
                self.results['converted'].append(info)
            elif 'error' in info:
                self.results['invalid'].append(info)
        
        return self.results
    
    def fix_files(self) -> int:
        """
        Fix files that need conversion. Returns number of files fixed.
        """
        fixed_count = 0
        
        for info in self.results.get('converted', []):
            filepath = self.grid_cell_dir / info['file']
            old_value = info['grid_type']
            new_value = info['should_be']
            
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                data['grid_type'] = new_value
                
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print(f"✅ Fixed {info['file']}: {old_value} → {new_value}")
                fixed_count += 1
            except Exception as e:
                print(f"❌ Failed to fix {info['file']}: {e}")
                self.results['errors'].append({
                    'file': info['file'],
                    'error': str(e)
                })
        
        return fixed_count
    
    def print_report(self) -> None:
        """Print validation report."""
        print("\n" + "=" * 70)
        print("GRID TYPE VALIDATION REPORT")
        print("=" * 70)
        
        valid_count = len(self.results['valid'])
        converted_count = len(self.results['converted'])
        invalid_count = len(self.results['invalid'])
        error_count = len(self.results['errors'])
        
        print(f"\n✅ Valid (using validation_key): {valid_count}")
        print(f"⚠️  Need Conversion (ui_label → validation_key): {converted_count}")
        print(f"❌ Invalid: {invalid_count}")
        print(f"🔧 Errors: {error_count}")
        
        if self.results['valid']:
            print("\n Valid Files:")
            for info in self.results['valid'][:5]:
                print(f"  • {info['file']}: {info['grid_type']}")
            if len(self.results['valid']) > 5:
                print(f"  ... and {len(self.results['valid']) - 5} more")
        
        if self.results['converted']:
            print("\n Files Needing Conversion:")
            for info in self.results['converted']:
                print(f"  • {info['file']}: {info['grid_type']} → {info['should_be']}")
        
        if self.results['invalid']:
            print("\n Invalid Files:")
            for info in self.results['invalid']:
                print(f"  • {info['file']}: {info.get('error', 'Unknown error')}")
        
        if self.results['errors']:
            print("\n Errors During Processing:")
            for info in self.results['errors']:
                print(f"  • {info['file']}: {info['error']}")
        
        print("\n" + "=" * 70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate and convert grid type references'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Fix files that need conversion'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Print validation report'
    )
    parser.add_argument(
        '--root',
        default='.',
        help='Root directory of EMD project'
    )
    
    args = parser.parse_args()
    
    validator = GridTypeValidator(args.root)
    validator.run_validation()
    
    if args.report or not args.fix:
        validator.print_report()
    
    if args.fix:
        fixed = validator.fix_files()
        print(f"\n✅ Fixed {fixed} files")
        if fixed > 0:
            print("   Re-run with --report to verify changes")


if __name__ == '__main__':
    main()
