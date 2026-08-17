#!/usr/bin/env python3
"""
CV Field Scanner

Scans all JSON files in EMD directories and reports on controlled vocabulary
field usage, checking whether entries use validation_key or ui_label format.

Usage:
    python scan_cv_fields.py [--field grid_type] [--folder horizontal_grid_cell]
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class CVFieldScanner:
    """Scans for CV field usage patterns."""
    
    # CV fields to track
    CV_FIELDS = [
        'grid_type',
        'grid_mapping',
        'region',
        'temporal_refinement',
        'units',
        'truncation_method',
    ]
    
    # Validation keys by field
    VALID_KEYS = {
        'grid_type': {
            'rotated-pole', 'unstructured-triangular', 'cubic-octahedral-spectral-reduced-gaussian',
            'unstructured-polygonal', 'reduced-gaussian', 'yin-yang', 'spectral-gaussian',
            'icosahedral-geodesic-dual', 'linear-spectral-gaussian', 'cubed-sphere',
            'spectral-reduced-gaussian', 'icosahedral-geodesic', 'hierarchical-discrete-global-grid',
            'unstructured', 'stretched', 'regular-latitude-longitude', 'displaced-pole',
            'icosahedral', 'tripolar', 'unstructured-quadrilateral', 'plane-projection',
            'regular-gaussian', 'quadratic-spectral-gaussian',
        },
        'region': {'global', 'arctic', 'atlantic', 'pacific', 'indian'},
        'grid_mapping': {'latitude-longitude', 'polar-stereographic', 'lambert-conformal'},
        'temporal_refinement': {'static', 'monthly', 'yearly'},
        'units': {'degree', 'meter', 'kilometer'},
        'truncation_method': {'triangular', 'rhomboidal'},
    }
    
    def __init__(self, root_dir: str = '.'):
        """Initialize scanner."""
        self.root_dir = Path(root_dir)
        self.results = defaultdict(lambda: {
            'validation_key': [],
            'ui_label': [],
            'invalid': [],
            'unknown': [],
        })
    
    def scan_file(self, filepath: Path) -> Dict:
        """Scan a single JSON file for CV fields."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            return {'error': str(e)}
        
        findings = {}
        
        for field in self.CV_FIELDS:
            value = data.get(field)
            if not value:
                continue
            
            # Determine if value is validation_key or ui_label format
            if field in self.VALID_KEYS:
                if value in self.VALID_KEYS[field]:
                    findings[field] = ('validation_key', value)
                else:
                    findings[field] = ('format_unknown', value)
            else:
                findings[field] = ('unmapped_field', value)
        
        return findings
    
    def scan_directory(self, folder_name: str) -> int:
        """
        Scan all JSON files in a directory.
        
        Returns: Number of files scanned
        """
        folder_path = self.root_dir / folder_name
        if not folder_path.exists():
            print(f"⚠ Directory not found: {folder_path}")
            return 0
        
        json_files = sorted(folder_path.glob('*.json'))
        if not json_files:
            print(f"⚠ No JSON files found in {folder_name}")
            return 0
        
        print(f"\n📋 Scanning {len(json_files)} files in {folder_name}...")
        
        for filepath in json_files:
            findings = self.scan_file(filepath)
            
            if 'error' in findings:
                print(f"  ❌ Error reading {filepath.name}: {findings['error']}")
                continue
            
            for field, (format_type, value) in findings.items():
                key = f"{folder_name}/{field}"
                
                if format_type == 'validation_key':
                    self.results[key]['validation_key'].append({
                        'file': filepath.name,
                        'value': value
                    })
                elif format_type == 'ui_label':
                    self.results[key]['ui_label'].append({
                        'file': filepath.name,
                        'value': value
                    })
                elif format_type == 'format_unknown':
                    self.results[key]['invalid'].append({
                        'file': filepath.name,
                        'value': value
                    })
                else:
                    self.results[key]['unknown'].append({
                        'file': filepath.name,
                        'value': value
                    })
        
        return len(json_files)
    
    def scan_all(self) -> None:
        """Scan all EMD directories."""
        folders = [
            'horizontal_grid_cell',
            'horizontal_computational_grid',
            'horizontal_subgrid',
            'vertical_computational_grid',
            'model',
            'model_component',
            'model_family',
        ]
        
        total_scanned = 0
        for folder in folders:
            total_scanned += self.scan_directory(folder)
        
        print(f"\n✅ Scanned {total_scanned} total files")
    
    def print_report(self, field: str = None) -> None:
        """Print scanning report."""
        print("\n" + "=" * 70)
        print("CV FIELD USAGE REPORT")
        print("=" * 70)
        
        if field:
            # Report for specific field
            matching_keys = [k for k in self.results.keys() if field in k]
            if not matching_keys:
                print(f"\n⚠ No results for field: {field}")
                return
            
            for key in matching_keys:
                self._print_field_report(key)
        else:
            # Report for all fields
            for key in sorted(self.results.keys()):
                self._print_field_report(key)
        
        print("\n" + "=" * 70)
    
    def _print_field_report(self, key: str) -> None:
        """Print report for a single field."""
        data = self.results[key]
        
        valid_count = len(data['validation_key'])
        invalid_count = len(data['invalid'])
        unknown_count = len(data['unknown'])
        ui_label_count = len(data['ui_label'])
        
        total = valid_count + invalid_count + unknown_count + ui_label_count
        
        print(f"\n{key}:")
        print(f"  ✅ validation_key format: {valid_count}")
        if data['validation_key'][:2]:
            for item in data['validation_key'][:2]:
                print(f"     • {item['file']}: {item['value']}")
            if len(data['validation_key']) > 2:
                print(f"     ... and {len(data['validation_key']) - 2} more")
        
        if ui_label_count:
            print(f"  ⚠️  ui_label format: {ui_label_count}")
            for item in data['ui_label'][:2]:
                print(f"     • {item['file']}: {item['value']}")
            if len(data['ui_label']) > 2:
                print(f"     ... and {len(data['ui_label']) - 2} more")
        
        if invalid_count:
            print(f"  ❌ invalid format: {invalid_count}")
            for item in data['invalid'][:2]:
                print(f"     • {item['file']}: {item['value']}")
            if len(data['invalid']) > 2:
                print(f"     ... and {len(data['invalid']) - 2} more")
        
        if unknown_count:
            print(f"  ❓ unknown: {unknown_count}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scan and report on CV field usage'
    )
    parser.add_argument(
        '--field',
        help='Focus on specific field (e.g., grid_type)'
    )
    parser.add_argument(
        '--folder',
        help='Scan specific folder only'
    )
    parser.add_argument(
        '--root',
        default='.',
        help='Root directory of EMD project'
    )
    
    args = parser.parse_args()
    
    scanner = CVFieldScanner(args.root)
    
    if args.folder:
        scanner.scan_directory(args.folder)
    else:
        scanner.scan_all()
    
    scanner.print_report(args.field)


if __name__ == '__main__':
    main()
