"""Generate project collections and terms from extracted CV data."""

import argparse
import sys
from pathlib import Path
from typing import Dict

from utils import (
    load_json,
    write_json,
    create_project_context,
    create_project_term
)


def generate_project_descriptor(
    descriptor_name: str,
    cv_data: Dict,
    project_path: Path,
    project_name: str = "emd"
) -> int:
    """
    Generate project descriptor directory with context and terms.

    Args:
        descriptor_name: Name of the descriptor
        cv_data: CV data dictionary
        project_path: Path to project repository
        project_name: Name of the project (default: "emd")

    Returns:
        Number of terms created
    """
    descriptor_path = project_path / descriptor_name

    # Create descriptor directory
    descriptor_path.mkdir(parents=True, exist_ok=True)

    # Create context file
    context_file = descriptor_path / "000_context.jsonld"
    context = create_project_context(descriptor_name)
    write_json(context_file, context)

    print(f"  Created context: {context_file}")

    # Create term files (minimal references to universe)
    term_count = 0
    for term_data in cv_data['terms']:
        term_id = term_data['id']
        term_file = descriptor_path / f"{term_id}.json"

        # Create minimal project term (reference to universe)
        term = create_project_term(term_id, descriptor_name)

        write_json(term_file, term)
        term_count += 1

    print(f"  Created {term_count} term files")

    return term_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate project collections from extracted CV data'
    )
    parser.add_argument('--input', required=True, help='Input JSON file (extracted CVs)')
    parser.add_argument('--project-path', required=True, help='Path to project repository')
    parser.add_argument('--project-name', default='emd', help='Project name (default: emd)')

    args = parser.parse_args()

    input_path = Path(args.input)
    project_path = Path(args.project_path)
    project_name = args.project_name

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Load extracted CVs
    print(f"Loading extracted CVs from: {input_path}")
    cvs = load_json(input_path)

    if not cvs:
        print("Error: No CVs found in input file")
        sys.exit(1)

    # Generate project collections
    print(f"\nGenerating project collections in: {project_path}")
    print(f"Project name: {project_name}\n")

    total_terms = 0
    descriptors_created = []

    for descriptor_name, cv_data in sorted(cvs.items()):
        print(f"Processing {descriptor_name} (Section {cv_data['section']})")

        term_count = generate_project_descriptor(
            descriptor_name,
            cv_data,
            project_path,
            project_name
        )

        total_terms += term_count
        descriptors_created.append(descriptor_name)
        print()

    # Print summary
    print("=== Project Generation Summary ===")
    print(f"Project: {project_name}")
    print(f"Total descriptors created: {len(descriptors_created)}")
    print(f"Total terms created: {total_terms}")

    print(f"\nDescriptors:")
    for name in descriptors_created:
        print(f"  - {name}")

    print("\nProject generation complete!")


if __name__ == '__main__':
    main()
