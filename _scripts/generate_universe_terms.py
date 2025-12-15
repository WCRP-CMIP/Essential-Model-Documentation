"""Generate universe data descriptors and terms from extracted CV data."""

import argparse
import sys
from pathlib import Path
from typing import Dict, Set

from utils import (
    load_json,
    write_json,
    create_universe_context,
    create_universe_term
)


def load_existing_terms(descriptor_path: Path) -> Set[str]:
    """
    Load existing term IDs from a descriptor directory.

    Args:
        descriptor_path: Path to descriptor directory

    Returns:
        Set of existing term IDs
    """
    if not descriptor_path.exists():
        return set()

    existing = set()
    for json_file in descriptor_path.glob("*.json"):
        if json_file.name == "000_context.jsonld":
            continue
        # Term ID is the filename without .json extension
        existing.add(json_file.stem)

    return existing


def generate_universe_descriptor(
    descriptor_name: str,
    cv_data: Dict,
    universe_path: Path,
    preserve_existing: bool = True
) -> Dict[str, int]:
    """
    Generate universe descriptor directory with context and terms.

    Args:
        descriptor_name: Name of the descriptor
        cv_data: CV data dictionary
        universe_path: Path to WCRP-universe repository
        preserve_existing: If True, don't overwrite existing terms

    Returns:
        Dictionary with counts: {'created': N, 'skipped': M, 'updated': K}
    """
    descriptor_path = universe_path / descriptor_name
    stats = {'created': 0, 'skipped': 0, 'updated': 0}

    # Check if descriptor exists
    is_new_descriptor = not descriptor_path.exists()

    if is_new_descriptor:
        print(f"  Creating new descriptor: {descriptor_name}")
        descriptor_path.mkdir(parents=True, exist_ok=True)

        # Create context file
        context_file = descriptor_path / "000_context.jsonld"
        write_json(context_file, create_universe_context(descriptor_name))
        print(f"    Created context file: {context_file.name}")
    else:
        print(f"  Updating existing descriptor: {descriptor_name}")

    # Load existing terms
    existing_terms = load_existing_terms(descriptor_path) if preserve_existing else set()
    if existing_terms:
        print(f"    Found {len(existing_terms)} existing terms")

    # Create term files
    for term_data in cv_data['terms']:
        term_id = term_data['id']
        term_file = descriptor_path / f"{term_id}.json"

        # Check if term exists
        if term_id in existing_terms:
            if preserve_existing:
                print(f"    Skipping existing term: {term_id}")
                stats['skipped'] += 1
                continue
            else:
                print(f"    Updating term: {term_id}")
                stats['updated'] += 1
        else:
            print(f"    Creating term: {term_id}")
            stats['created'] += 1

        # Create term JSON
        term = create_universe_term(
            term_id=term_id,
            descriptor_name=descriptor_name,
            description=term_data.get('description', ''),
            drs_name=term_data.get('drs_name', term_id.upper())
        )

        # Add optional fields
        if 'ui_label' in term_data:
            term['ui_label'] = term_data['ui_label']

        write_json(term_file, term)

    return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate universe data descriptors from extracted CV data'
    )
    parser.add_argument('--input', required=True, help='Input JSON file (extracted CVs)')
    parser.add_argument('--universe-path', required=True, help='Path to WCRP-universe repository')
    parser.add_argument(
        '--preserve-existing',
        action='store_true',
        default=True,
        help='Preserve existing terms (default: True)'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing terms'
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    universe_path = Path(args.universe_path)

    # Handle preserve_existing flag
    preserve_existing = not args.overwrite

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    if not universe_path.exists():
        print(f"Error: Universe path not found: {universe_path}")
        sys.exit(1)

    # Load extracted CVs
    print(f"Loading extracted CVs from: {input_path}")
    cvs = load_json(input_path)

    if not cvs:
        print("Error: No CVs found in input file")
        sys.exit(1)

    # Generate universe descriptors
    print(f"\nGenerating universe descriptors in: {universe_path}")
    print(f"Preserve existing terms: {preserve_existing}\n")

    total_stats = {'created': 0, 'skipped': 0, 'updated': 0}
    new_descriptors = []
    updated_descriptors = []

    for descriptor_name, cv_data in sorted(cvs.items()):
        print(f"Processing {descriptor_name} (Section {cv_data['section']})")

        # Track if descriptor is new
        descriptor_path = universe_path / descriptor_name
        is_new = not descriptor_path.exists()

        stats = generate_universe_descriptor(
            descriptor_name,
            cv_data,
            universe_path,
            preserve_existing
        )

        # Update totals
        for key in total_stats:
            total_stats[key] += stats[key]

        if is_new:
            new_descriptors.append(descriptor_name)
        else:
            updated_descriptors.append(descriptor_name)

        print()

    # Print summary
    print("=== Universe Generation Summary ===")
    print(f"Total descriptors processed: {len(cvs)}")
    print(f"  New descriptors created: {len(new_descriptors)}")
    print(f"  Existing descriptors updated: {len(updated_descriptors)}")
    print(f"\nTerms:")
    print(f"  Created: {total_stats['created']}")
    print(f"  Skipped (existing): {total_stats['skipped']}")
    print(f"  Updated: {total_stats['updated']}")

    if new_descriptors:
        print(f"\nNew descriptors:")
        for name in new_descriptors:
            print(f"  - {name}")

    if updated_descriptors:
        print(f"\nUpdated descriptors:")
        for name in updated_descriptors:
            print(f"  - {name}")

    print("\nUniverse generation complete!")


if __name__ == '__main__':
    main()
