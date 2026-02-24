#!/usr/bin/env python3
"""
Collect vocabulary READMEs for MkDocs rendering.

This script scans a source directory for vocabulary folders (those containing
a `_context` file), copies their READMEs to an output directory with renamed
filenames matching the folder names, making them ready for MkDocs rendering.

Usage (command line):
    python collect_vocab_docs.py /path/to/src-data --output docs/vocabularies
    python collect_vocab_docs.py /path/to/src-data -p universal

When imported (e.g., by run_scripts.py), runs automatically with defaults.
"""

import argparse
import shutil
import sys
import os
from pathlib import Path


def find_vocab_directories(source_dir: Path) -> list:
    """Find all directories containing a _context file."""
    vocab_dirs = []
    
    for item in sorted(source_dir.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            context_file = item / '_context'
            if context_file.exists():
                vocab_dirs.append(item)
    
    return vocab_dirs


def collect_readmes(source_dir: Path, output_dir: Path, prefix: str = None) -> dict:
    """
    Collect READMEs from vocabulary directories.
    
    Args:
        source_dir: Directory containing vocabulary subdirectories
        output_dir: Output directory for collected READMEs
        prefix: Optional prefix for documentation (e.g., 'universal')
    
    Returns:
        dict with statistics about the collection
    """
    stats = {
        'found': 0,
        'copied': 0,
        'missing': [],
        'copied_files': []
    }
    
    # Find vocabulary directories
    vocab_dirs = find_vocab_directories(source_dir)
    stats['found'] = len(vocab_dirs)
    
    if not vocab_dirs:
        print(f"  No vocabulary directories found in {source_dir}")
        return stats
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Collect READMEs
    for vocab_dir in vocab_dirs:
        readme_path = vocab_dir / 'README.md'
        vocab_name = vocab_dir.name
        
        if readme_path.exists():
            # Output filename is the folder name + .md
            output_filename = f"{vocab_name}.md"
            output_path = output_dir / output_filename
            
            # Copy the README
            shutil.copy2(readme_path, output_path)
            stats['copied'] += 1
            stats['copied_files'].append(vocab_name)
            print(f"    ✓ {vocab_name}")
        else:
            stats['missing'].append(vocab_name)
            print(f"    ✗ {vocab_name} (no README.md)")
    
    return stats


def run_auto():
    """Auto-run with sensible defaults for MkDocs context."""
    cwd = Path.cwd()
    
    # Find project root (look for docs/ directory)
    project_root = cwd
    if (cwd / 'docs').exists():
        project_root = cwd
    elif (cwd.parent / 'docs').exists():
        project_root = cwd.parent
    elif (cwd.parent.parent / 'docs').exists():
        project_root = cwd.parent.parent
    
    # Find source directory with vocab folders
    source_dir = None
    
    # Check if vocab directories are at project root
    if any((project_root / d / '_context').exists() 
           for d in os.listdir(project_root) 
           if (project_root / d).is_dir() and not d.startswith('.')):
        source_dir = project_root
    
    # Or in src-data/
    elif (project_root / 'src-data').exists():
        source_dir = project_root / 'src-data'
    
    if not source_dir:
        print("  ℹ️  No vocabulary source directory found, skipping")
        return
    
    output_dir = project_root / 'docs' / 'vocabularies'
    
    print(f"\n📚 Collecting vocabulary documentation")
    print(f"   Source: {source_dir}")
    print(f"   Output: {output_dir}")
    
    stats = collect_readmes(source_dir, output_dir, prefix='emd')
    
    print(f"   ✅ Collected {stats['copied']} vocabularies\n")


def main():
    parser = argparse.ArgumentParser(
        description='Collect vocabulary READMEs for MkDocs rendering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s /path/to/WCRP-universe/src-data --output docs/vocabularies
  %(prog)s ./src-data --output ../docs/universal --prefix universal
  %(prog)s . --output docs/vocabs --dry-run
        '''
    )
    parser.add_argument(
        'source',
        type=Path,
        help='Source directory containing vocabulary subdirectories'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('docs/vocabularies'),
        help='Output directory for collected READMEs (default: docs/vocabularies)'
    )
    parser.add_argument(
        '--prefix', '-p',
        type=str,
        default=None,
        help='Vocabulary prefix for documentation (e.g., universal, cmip7)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without copying files'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Remove output directory before collecting'
    )
    
    args = parser.parse_args()
    
    # Validate source directory
    if not args.source.exists():
        print(f"Error: Source directory '{args.source}' does not exist")
        sys.exit(1)
    
    if not args.source.is_dir():
        print(f"Error: '{args.source}' is not a directory")
        sys.exit(1)
    
    source_dir = args.source.resolve()
    output_dir = args.output.resolve()
    
    print(f"Collecting vocabulary documentation")
    print(f"  Source: {source_dir}")
    print(f"  Output: {output_dir}")
    if args.prefix:
        print(f"  Prefix: {args.prefix}")
    print("-" * 50)
    
    # Clean output directory if requested
    if args.clean and output_dir.exists():
        print(f"Cleaning output directory...")
        shutil.rmtree(output_dir)
    
    # Dry run - just show what would be done
    if args.dry_run:
        vocab_dirs = find_vocab_directories(source_dir)
        print(f"\n[DRY RUN] Would collect {len(vocab_dirs)} vocabularies:")
        for vocab_dir in vocab_dirs:
            readme_exists = (vocab_dir / 'README.md').exists()
            status = "✓" if readme_exists else "✗ (no README)"
            print(f"  {status} {vocab_dir.name}")
        return
    
    # Collect READMEs
    stats = collect_readmes(source_dir, output_dir, args.prefix)
    
    # Summary
    print("-" * 50)
    print(f"Summary:")
    print(f"  Vocabularies found: {stats['found']}")
    print(f"  READMEs copied: {stats['copied']}")
    
    if stats['missing']:
        print(f"  Missing READMEs: {len(stats['missing'])}")
        for name in stats['missing']:
            print(f"    - {name}")
    
    print(f"\nOutput directory: {output_dir}")


# Entry point
if __name__ == "__main__":
    main()
else:
    # When imported, auto-run with defaults
    run_auto()
