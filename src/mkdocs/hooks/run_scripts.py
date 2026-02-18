#!/usr/bin/env python3
"""
Script runner for MkDocs gen-files plugin.
Executes all Python scripts in docs/scripts/ directory during build.

Scripts can generate markdown files using mkdocs_gen_files.open()
"""

import os
import sys
import importlib.util
import time
from pathlib import Path

print("\n" + "=" * 60)
print("SCRIPT RUNNER - Executing docs/scripts/*.py")
print("=" * 60)

# ── LDR server bootstrap ──────────────────────────────────────────────────────

def _wait_for_ldr(max_wait: float = 15.0, interval: float = 0.5) -> bool:
    """
    Wait until the LDR server on port 3333 is responding.
    Returns True if ready, False if timed out.
    """
    import cmipld
    deadline = time.monotonic() + max_wait
    while time.monotonic() < deadline:
        try:
            cmipld.client.get_mappings()
            return True
        except Exception:
            time.sleep(interval)
    return False


def _start_ldr() -> bool:
    """
    (Re-)initialize the LDR server.  Removes the cached cmipld module so
    it can be freshly imported, which triggers LdrClient to start the server.
    Returns True on success.
    """
    # Drop cached module so re-import restarts LdrClient
    for key in [k for k in sys.modules if k.startswith("cmipld")]:
        del sys.modules[key]

    try:
        import cmipld  # noqa: F401 — side-effect: starts Node.js server
        ready = _wait_for_ldr()
        if ready:
            print("✅ LDR server is ready")
        else:
            print("⚠️  LDR server did not become ready in time")
        return ready
    except Exception as e:
        print(f"❌ Failed to start LDR server: {e}")
        return False


def _ldr_alive() -> bool:
    """Quick check: is the LDR server currently responding?"""
    try:
        import cmipld
        cmipld.client.get_mappings()
        return True
    except Exception:
        return False


print("\n🔧 Initializing LDR server...")
try:
    import cmipld  # noqa: F401
    ldr_ok = _wait_for_ldr(max_wait=15.0)
    if ldr_ok:
        print("✅ LDR server is ready and responsive")
    else:
        print("⚠️  LDR server slow to start — will retry before each script")
except ImportError:
    print("⚠️  cmipld not available - scripts requiring LDR will be skipped")
    ldr_ok = False
except Exception as e:
    print(f"❌ Failed to initialize LDR server: {e}")
    ldr_ok = False

print("\n" + "=" * 60)

# Find scripts directory
cwd = Path.cwd()
script_locations = [
    cwd / "docs" / "scripts",
    cwd.parent / "docs" / "scripts",
    cwd.parent.parent / "docs" / "scripts",
]

scripts_dir = None
for loc in script_locations:
    if loc.exists() and loc.is_dir():
        scripts_dir = loc
        break

if not scripts_dir:
    print("ℹ️  No docs/scripts/ directory found, skipping script execution")
    print("=" * 60)
else:
    print(f"📁 Found scripts directory: {scripts_dir}")
    
    # Find all Python scripts (skip files starting with _)
    scripts = sorted(scripts_dir.glob("*.py"))
    scripts = [s for s in scripts if not s.name.startswith('_')]
    
    if not scripts:
        print("ℹ️  No Python scripts found in docs/scripts/")
    else:
        print(f"📜 Found {len(scripts)} script(s) to execute:")
        for script in scripts:
            print(f"   - {script.name}")
        
        print("\n" + "-" * 40)
        
        # Execute each script
        for script_path in scripts:
            print(f"\n🔄 Executing: {script_path.name}")

            # Ensure LDR is alive before every script (contributors kills it)
            try:
                if not _ldr_alive():
                    print("   ↻ LDR server not responding — restarting...")
                    _start_ldr()
            except Exception:
                pass  # cmipld may not be available; scripts will handle it

            try:
                # Load and execute the script
                spec = importlib.util.spec_from_file_location(
                    script_path.stem, 
                    script_path
                )
                module = importlib.util.module_from_spec(spec)
                
                # Add docs/scripts to path so scripts can import each other
                if str(scripts_dir) not in sys.path:
                    sys.path.insert(0, str(scripts_dir))
                
                spec.loader.exec_module(module)
                print(f"✅ Completed: {script_path.name}")
                
            except Exception as e:
                print(f"❌ Error in {script_path.name}: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
        
        print("\n" + "-" * 40)

print("=" * 60 + "\n")
