#!/usr/bin/env python3
"""
Pre-build script runner for MkDocs.

Runs data generation scripts BEFORE mkdocs build starts.
This ensures generated files exist when MkDocs scans the docs directory.

Usage:
    python pre_build.py           # Run from src/mkdocs directory
    python pre_build.py --docs-dir ../../docs

Scripts that generate content (HTML/MD files) should be run here.
Scripts that only need gen-files (like auto_version.py) can stay in run_scripts.py.
"""

import os
import sys
import importlib.util
from pathlib import Path
import argparse


# Scripts that generate content and need to run BEFORE mkdocs build
PRE_BUILD_SCRIPTS = [
    "generate_model_families.py",
    "generate_models.py",
    "generate_model_components.py",
    "generate_summaries.py",
]


def find_scripts_dir(docs_dir: Path) -> Path:
    """Find the scripts directory."""
    scripts_dir = docs_dir / "scripts"
    if scripts_dir.exists():
        return scripts_dir
    return None


def run_script(script_path: Path) -> bool:
    """Run a single script."""
    try:
        spec = importlib.util.spec_from_file_location(
            script_path.stem,
            script_path
        )
        module = importlib.util.module_from_spec(spec)
        
        # Add scripts directory to path
        scripts_dir = script_path.parent
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        
        spec.loader.exec_module(module)
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="Run pre-build scripts")
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("../../docs"),
        help="Path to docs directory (default: ../../docs)"
    )
    args = parser.parse_args()
    
    # Resolve docs directory
    docs_dir = args.docs_dir
    if not docs_dir.is_absolute():
        docs_dir = Path.cwd() / docs_dir
    docs_dir = docs_dir.resolve()
    
    if not docs_dir.exists():
        print(f"❌ Docs directory not found: {docs_dir}")
        return 1
    
    scripts_dir = find_scripts_dir(docs_dir)
    if not scripts_dir:
        print(f"❌ Scripts directory not found in {docs_dir}")
        return 1
    
    print("\n" + "=" * 60)
    print("PRE-BUILD SCRIPTS")
    print("=" * 60)
    print(f"📁 Scripts: {scripts_dir}")
    print(f"📁 Docs: {docs_dir}")
    print("-" * 60)
    
    # Change to docs directory for script context
    original_cwd = Path.cwd()
    os.chdir(docs_dir.parent)  # Go to repo root
    
    success = 0
    failed = 0
    skipped = 0
    
    for script_name in PRE_BUILD_SCRIPTS:
        script_path = scripts_dir / script_name
        
        if not script_path.exists():
            print(f"⏭️  Skipping: {script_name} (not found)")
            skipped += 1
            continue
        
        print(f"\n🔄 Running: {script_name}")
        if run_script(script_path):
            print(f"✅ Completed: {script_name}")
            success += 1
        else:
            print(f"❌ Failed: {script_name}")
            failed += 1
    
    os.chdir(original_cwd)
    
    print("\n" + "-" * 60)
    print(f"Summary: {success} succeeded, {failed} failed, {skipped} skipped")
    print("=" * 60 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
