#!/usr/bin/env python3
"""
CV Field Converter

Batch convert all controlled vocabulary fields from ui_label to validation_key
format across all EMD JSON files.

Usage:
    python convert_cv_fields.py [--field grid_type] [--dry-run] [--backup]
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class CVFieldConverter:
    """Converts CV field values from ui_label to validation_key format."""
    
    # Mapping from ui_label to validation_key for each field
    CONVERSIONS = {
        'grid_type': {
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
        },
        'truncation_method': {
            'Triangular': 'triangular',
            'Rhomboidal': 'rhomboidal',
        },
    }
    
    def __init__(self, root_dir: str = '.', backup: bool = False):
        """Initialize converter."""
        self.root_dir = Path(root_dir)
        self.backup = backup
        self.stats = {
            'files_scanned': 0,
            'files_modified': 0,
            'fields_converted': 0,
            'errors': [],
            'changes': [],
        }
    
    def create_backup(self, filepath: Path) -> bool:
        """Create backup of file before modification."""
        if not self.backup:
            return True
        
        backup_dir = filepath.parent / '.backups'
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"{filepath.stem}_{timestamp}{filepath.suffix}"
        
        try:
            shutil.copy2(filepath, backup_path)
            return True
        except Exception as e:
            print(f"  ⚠ Failed to create backup: {e}")
            return False
    
    def convert_file(self, filepath: Path, dry_run: bool = False, 
                    target_field: str = None) -> Tuple[bool, List[Dict]]:
        """
        Convert CV fields in a file.
        
        Returns:
            Tuple of (modified, list_of_changes)
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            self.stats['errors'].append({
                'file': str(filepath),
                'error': f'Failed to read: {e}'
            })
            return False, []
        
        changes = []
        modified = False
        
        for field, conversions in self.CONVERSIONS.items():
            # Skip if target field specified and it doesn't match
            if target_field and field != target_field:
                continue
            
            # Skip if field not in this file
            if field not in data:
                continue
            
            old_value = data[field]
            
            # Check if value needs conversion
            if old_value in conversions:
                new_value = conversions[old_value]
                
                if not dry_run:
                    data[field] = new_value
                
                changes.append({
                    'field': field,
                    'old_value': old_value,
                    'new_value': new_value,
                })
                modified = True
        
        # Write file if modified and not dry-run
        if modified and not dry_run:
            if self.backup:
                self.create_backup(filepath)
            
            try:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                self.stats['errors'].append({
                    'file': str(filepath),
                    'error': f'Failed to write: {e}'
                })
                return False, changes
        
        return modified, changes
    
    def convert_directory(self, folder_name: str, dry_run: bool = False,
                         target_field: str = None) -> int:
        """
        Convert CV fields in all JSON files in a directory.
        
        Returns: Number of modified files
        """
        folder_path = self.root_dir / folder_name
        if not folder_path.exists():
            print(f"⚠ Directory not found: {folder_path}")
            return 0
        
        json_files = sorted(folder_path.glob('*.json'))
        if not json_files:
            return 0
        
        mode_str = " (DRY RUN)" if dry_run else ""
        print(f"\n📝 Converting {len(json_files)} files in {folder_name}{mode_str}...")
        
        modified_count = 0
        
        for filepath in json_files:
            # Skip graph and context files
            if '_graph' in filepath.name or filepath.name == '_context':
                continue
            
            self.stats['files_scanned'] += 1
            modified, changes = self.convert_file(filepath, dry_run, target_field)
            
            if modified:
                modified_count += 1
                self.stats['files_modified'] += 1
                self.stats['fields_converted'] += len(changes)
                
                for change in changes:
                    self.stats['changes'].append({
                        'file': filepath.name,
                        **change
                    })
                
                symbols = "  📝" if dry_run else "  ✅"
                print(f"{symbols} {filepath.name}: {len(changes)} field(s)")
                for change in changes:
                    print(f"      {change['field']}: '{change['old_value']}' → '{change['new_value']}'")
        
        return modified_count
    
    def convert_all(self, dry_run: bool = False, target_field: str = None) -> int:
        """Convert all EMD directories."""
        folders = [
            'horizontal_grid_cell',
            'horizontal_computational_grid',
            'horizontal_subgrid',
            'vertical_computational_grid',
            'model',
            'model_component',
            'model_family',
        ]
        
        total_modified = 0
        for folder in folders:
            modified = self.convert_directory(folder, dry_run, target_field)
            total_modified += modified
        
        return total_modified
    
    def print_summary(self, dry_run: bool = False) -> None:
        """Print summary report."""
        print("\n" + "=" * 70)
        print("CONVERSION SUMMARY")
        if dry_run:
            print("(DRY RUN - No changes applied)")
        print("=" * 70)
        
        print(f"\n📊 Statistics:")
        print(f"  Files scanned: {self.stats['files_scanned']}")
        print(f"  Files modified: {self.stats['files_modified']}")
        print(f"  Fields converted: {self.stats['fields_converted']}")
        
        if self.stats['errors']:
            print(f"\n❌ Errors: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:
                print(f"  • {error['file']}: {error['error']}")
            if len(self.stats['errors']) > 5:
                print(f"  ... and {len(self.stats['errors']) - 5} more")
        
        if self.stats['changes']:
            print(f"\n✅ Changes Summary:")
            
            # Group changes by field
            by_field = {}
            for change in self.stats['changes']:
                field = change['field']
                if field not in by_field:
                    by_field[field] = []
                by_field[field].append(change)
            
            for field in sorted(by_field.keys()):
                changes = by_field[field]
                print(f"\n  {field}: {len(changes)} conversion(s)")
                for change in changes[:3]:
                    print(f"    • {change['file']}: '{change['old_value']}' → '{change['new_value']}'")
                if len(changes) > 3:
                    print(f"    ... and {len(changes) - 3} more")
        
        if not dry_run and self.stats['files_modified'] > 0:
            print(f"\n✅ Successfully converted {self.stats['files_modified']} file(s)")
            if self.backup:
                print("   Backups created in .backups/ directories")
        elif dry_run and self.stats['files_modified'] > 0:
            print(f"\n📋 Would convert {self.stats['files_modified']} file(s)")
            print("   Run without --dry-run to apply changes")
        else:
            print("\n✅ No conversions needed - all files are up to date")
        
        print("\n" + "=" * 70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert CV fields from ui_label to validation_key format'
    )
    parser.add_argument(
        '--field',
        help='Convert specific field only'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without applying changes'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create backups before modifying files'
    )
    parser.add_argument(
        '--root',
        default='.',
        help='Root directory of EMD project'
    )
    
    args = parser.parse_args()
    
    converter = CVFieldConverter(args.root, backup=args.backup)
    
    total_modified = converter.convert_all(dry_run=args.dry_run, target_field=args.field)
    converter.print_summary(dry_run=args.dry_run)
    
    return 0 if args.dry_run or total_modified >= 0 else 1


if __name__ == '__main__':
    exit(main())
