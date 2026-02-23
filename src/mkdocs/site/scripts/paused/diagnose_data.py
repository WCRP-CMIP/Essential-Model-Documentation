#!/usr/bin/env python3
"""
Diagnostic script to verify cmipld data loading is working.
Run this in your shell where cmipld is installed.
"""

import sys

print("=" * 60)
print("CMIPLD Data Loading Diagnostic")
print("=" * 60)

# Check cmipld
try:
    import cmipld
    print("✅ cmipld is available")
    print(f"   Version: {getattr(cmipld, '__version__', 'unknown')}")
except ImportError as e:
    print(f"❌ cmipld not available: {e}")
    print("\n   Install with: pip install cmipld")
    sys.exit(1)

# Check git branch
import subprocess
try:
    result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                          capture_output=True, text=True, check=True)
    branch = result.stdout.strip()
    print(f"✅ Git branch: {branch}")
except Exception as e:
    print(f"❌ Could not get git branch: {e}")
    branch = "unknown"

# Check prefix
try:
    prefix = cmipld.prefix()
    print(f"✅ Prefix: {prefix}")
except Exception as e:
    print(f"❌ Could not get prefix: {e}")
    prefix = "emd"

# Test fetching model_family list
print("\n" + "-" * 40)
print("Testing data fetching...")
print("-" * 40)

try:
    url = f"{prefix}:model_family/_graph.json"
    print(f"   Fetching: {url}")
    data = cmipld.get(url, depth=0)
    if data and 'contents' in data:
        entries = [item.get('@id') for item in data['contents'] if isinstance(item, dict)]
        print(f"✅ model_family: {len(entries)} entries found")
        print(f"   First 5: {entries[:5]}")
    else:
        print(f"❌ No contents in response")
except Exception as e:
    print(f"❌ Error fetching model_family: {e}")

# Test fetching a single entry
try:
    url = f"{prefix}:model_family/nemo"
    print(f"\n   Fetching: {url}")
    data = cmipld.get(url, depth=2)
    if data:
        print(f"✅ Single entry fetch works")
        print(f"   ui_label: {data.get('ui_label', 'N/A')}")
        print(f"   validation_key: {data.get('validation_key', 'N/A')}")
        print(f"   family_type: {data.get('family_type', 'N/A')}")
    else:
        print(f"❌ No data returned")
except Exception as e:
    print(f"❌ Error fetching single entry: {e}")

# Test fetching model list
try:
    url = f"{prefix}:model/_graph.json"
    print(f"\n   Fetching: {url}")
    data = cmipld.get(url, depth=0)
    if data and 'contents' in data:
        entries = [item.get('@id') for item in data['contents'] if isinstance(item, dict)]
        print(f"✅ model: {len(entries)} entries found")
        print(f"   Entries: {entries}")
    else:
        print(f"❌ No contents in response")
except Exception as e:
    print(f"❌ Error fetching model: {e}")

# Test fetching model_component list
try:
    url = f"{prefix}:model_component/_graph.json"
    print(f"\n   Fetching: {url}")
    data = cmipld.get(url, depth=0)
    if data and 'contents' in data:
        entries = [item.get('@id') for item in data['contents'] if isinstance(item, dict)]
        print(f"✅ model_component: {len(entries)} entries found")
        print(f"   First 5: {entries[:5]}")
    else:
        print(f"❌ No contents in response")
except Exception as e:
    print(f"❌ Error fetching model_component: {e}")

# Test grid endpoints
for endpoint in ["horizontal_computational_grid", "vertical_computational_grid"]:
    try:
        url = f"{prefix}:{endpoint}/_graph.json"
        print(f"\n   Fetching: {url}")
        data = cmipld.get(url, depth=0)
        if data and 'contents' in data:
            entries = [item.get('@id') for item in data['contents'] if isinstance(item, dict)]
            print(f"✅ {endpoint}: {len(entries)} entries found")
        else:
            print(f"⚠️  {endpoint}: No contents (may not exist yet)")
    except Exception as e:
        print(f"⚠️  {endpoint}: {e}")

print("\n" + "=" * 60)
print("Diagnostic complete!")
print("=" * 60)
print("\nIf all checks pass, run:")
print("  cd src/mkdocs && python pre_build.py")
print("=" * 60)
