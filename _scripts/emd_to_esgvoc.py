"""
Main orchestrator script for EMD CV extraction to esgvoc format.

This script coordinates the full pipeline:
1. Extract CV tables from EMD Word document
2. Generate universe data descriptors and terms
3. Generate project collections and terms
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> int:
    """
    Run a command and print status.

    Args:
        cmd: Command and arguments as list
        description: Description of what the command does

    Returns:
        Return code
    """
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")

    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Extract EMD CVs and convert to esgvoc format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python emd_to_esgvoc.py \\
    --docx "/path/to/EMD.docx" \\
    --universe-path /path/to/WCRP-universe \\
    --project-path /path/to/Essential-Model-Documentation \\
    --project-name emd \\
    --preserve-existing
        """
    )
    parser.add_argument(
        '--docx',
        required=True,
        help='Path to EMD Word document'
    )
    parser.add_argument(
        '--universe-path',
        required=True,
        help='Path to WCRP-universe repository'
    )
    parser.add_argument(
        '--project-path',
        required=True,
        help='Path to project repository'
    )
    parser.add_argument(
        '--project-name',
        default='emd',
        help='Project name (default: emd)'
    )
    parser.add_argument(
        '--preserve-existing',
        action='store_true',
        default=True,
        help='Preserve existing universe terms (default: True)'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing universe terms'
    )
    parser.add_argument(
        '--temp-file',
        default='data/extracted_cvs.json',
        help='Temporary file for extracted CVs (default: data/extracted_cvs.json)'
    )

    args = parser.parse_args()

    # Validate paths
    docx_path = Path(args.docx)
    universe_path = Path(args.universe_path)
    project_path = Path(args.project_path)
    temp_file = Path(args.temp_file)

    if not docx_path.exists():
        print(f"Error: Word document not found: {docx_path}")
        sys.exit(1)

    if not universe_path.exists():
        print(f"Error: Universe path not found: {universe_path}")
        sys.exit(1)

    print("="*60)
    print("EMD CV Extraction to esgvoc Format")
    print("="*60)
    print(f"Word document: {docx_path}")
    print(f"Universe path: {universe_path}")
    print(f"Project path: {project_path}")
    print(f"Project name: {args.project_name}")
    print(f"Preserve existing: {not args.overwrite}")

    # Step 1: Extract CVs from Word
    cmd_extract = [
        sys.executable,
        'scripts/extract_word_cvs.py',
        '--docx', str(docx_path),
        '--output', str(temp_file)
    ]

    ret = run_command(cmd_extract, "Step 1: Extracting CVs from Word document")
    if ret != 0:
        print(f"\nError: Extraction failed with code {ret}")
        sys.exit(ret)

    # Step 2: Generate universe terms
    cmd_universe = [
        sys.executable,
        'scripts/generate_universe_terms.py',
        '--input', str(temp_file),
        '--universe-path', str(universe_path)
    ]

    if args.overwrite:
        cmd_universe.append('--overwrite')
    else:
        cmd_universe.append('--preserve-existing')

    ret = run_command(cmd_universe, "Step 2: Generating universe data descriptors")
    if ret != 0:
        print(f"\nError: Universe generation failed with code {ret}")
        sys.exit(ret)

    # Step 3: Generate project terms
    cmd_project = [
        sys.executable,
        'scripts/generate_project_terms.py',
        '--input', str(temp_file),
        '--project-path', str(project_path),
        '--project-name', args.project_name
    ]

    ret = run_command(cmd_project, "Step 3: Generating project collections")
    if ret != 0:
        print(f"\nError: Project generation failed with code {ret}")
        sys.exit(ret)

    # All done!
    print("\n" + "="*60)
    print("Pipeline Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review generated files manually")
    print("2. Configure esgvoc to test the generated CVs")
    print("3. Commit changes to git repositories")


if __name__ == '__main__':
    main()
