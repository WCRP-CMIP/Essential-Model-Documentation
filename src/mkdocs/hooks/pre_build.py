#!/usr/bin/env python3
"""
Pre-build hook for MkDocs.
Executes all Python scripts in docs/scripts/ directory BEFORE build starts.
This ensures generated files are in place when mkdocs copies them.
"""

import os
import sys
import importlib.util
import subprocess
from pathlib import Path


def on_pre_build(config):
    """Hook that runs BEFORE mkdocs build starts."""
    print("\n" + "=" * 60)
    print("PRE-BUILD HOOK - Executing docs/scripts/*.py")
    print("=" * 60)

    # Find scripts directory
    docs_dir = Path(config['docs_dir'])
    scripts_dir = docs_dir / "scripts"

    if not scripts_dir.exists() or not scripts_dir.is_dir():
        print("ℹ️  No docs/scripts/ directory found, skipping script execution")
        print("=" * 60 + "\n")
        return

    print(f"📁 Found scripts directory: {scripts_dir}")

    # Find all Python scripts that start with "generate_"
    scripts = sorted(scripts_dir.glob("generate_*.py"))
    scripts = [s for s in scripts if not s.name.startswith('_')]

    if not scripts:
        print("ℹ️  No generate_*.py scripts found in docs/scripts/")
        print("=" * 60 + "\n")
        return

    print(f"📜 Found {len(scripts)} generator script(s) to execute:")
    for script in scripts:
        print(f"   - {script.name}")

    print("\n" + "-" * 40)

    # Execute each script and WAIT for completion
    for script_path in scripts:
        print(f"\n🔄 Executing: {script_path.name}")

        try:
            # Run script as subprocess and wait for completion
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(scripts_dir),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout per script
            )

            # Print output
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    print(f"   {line}")

            if result.returncode == 0:
                print(f"✅ Completed: {script_path.name}")
            else:
                print(f"⚠️  Completed with warnings: {script_path.name}")
                if result.stderr:
                    print(f"   stderr: {result.stderr}")

        except subprocess.TimeoutExpired:
            print(f"❌ Timeout in {script_path.name}", file=sys.stderr)
        except Exception as e:
            print(f"❌ Error in {script_path.name}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()

    print("\n" + "-" * 40)
    print("=" * 60 + "\n")
