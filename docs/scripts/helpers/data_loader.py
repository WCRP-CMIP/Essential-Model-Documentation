"""
Data loading utilities for EMD build scripts.

Uses cmipld to fetch JSON-LD data. On the production branch, maps
the repository prefix to local files. On all other branches, fetches
from remote prefix URLs.

Automatically restarts the LDR server if it has been killed (e.g. by
a subprocess that imported cmipld independently).
"""

import subprocess
import time
from typing import Optional, List, Dict, Any

# ── cmipld import ────────────────────────────────────────────────────────────

try:
    import cmipld
    HAS_CMIPLD = True
except ImportError:
    cmipld = None
    HAS_CMIPLD = False


# ── helpers ──────────────────────────────────────────────────────────────────

def get_current_branch() -> str:
    try:
        r = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                           capture_output=True, text=True, check=True)
        return r.stdout.strip()
    except Exception:
        return "unknown"


def _ensure_server():
    """Make sure the LDR server is responding. Start or restart if not."""
    if not HAS_CMIPLD:
        return False
    try:
        cmipld.client.get_mappings()
        return True
    except Exception:
        pass

    # Server is dead — restart it
    print("  LDR server not responding — restarting...")
    try:
        subprocess.run(["ldr", "server", "stop"], capture_output=True, timeout=5)
    except Exception:
        pass
    try:
        subprocess.run(["ldr", "server", "start"], capture_output=True, timeout=10)
    except Exception:
        pass

    # Re-import cmipld so the client picks up the new server
    import sys
    for key in [k for k in sys.modules if k.startswith("cmipld")]:
        del sys.modules[key]
    try:
        import cmipld as _fresh
        globals()['cmipld'] = _fresh
    except Exception:
        pass

    # Wait for it
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        try:
            cmipld.client.get_mappings()
            print("  LDR server restarted")
            return True
        except Exception:
            time.sleep(0.5)

    print("  Warning: LDR server did not recover")
    return False


def _is_connection_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "connection refused" in msg or "max retries" in msg


# ── initialisation ───────────────────────────────────────────────────────────

_initialized = False


def init_loader():
    """Ensure cmipld is ready. On production, map prefix to local files."""
    global _initialized
    if _initialized:
        return
    _initialized = True

    if not HAS_CMIPLD:
        print("  Warning: cmipld not available")
        return

    _ensure_server()

    branch = get_current_branch()
    if branch == "production":
        print(branch,'\n\n\n')
        try:
            # prefix = cmipld.prefix()
            # print ('prefix',prefix)
            cmipld.map_current(prefix)
            print(f"  Branch: {branch} — mounted local files as '{prefix}'")
        except Exception as e:
            print(f"  Warning: Could not mount local files: {e}")
    else:
        print(f"  Branch: {branch} — using remote prefix URLs")


# ── data fetching (with automatic server recovery) ──────────────────────────

def _with_retry(fn):
    """Call fn(). On connection error, restart server and retry once."""
    try:
        return fn()
    except Exception as e:
        if _is_connection_error(e):
            _ensure_server()
            # Re-apply local mapping if on production
            if get_current_branch() == "production":
                try:
                    cmipld.map_current(cmipld.prefix())
                except Exception:
                    pass
            return fn()
        raise


def _normalise_contents(raw) -> List[Dict[str, Any]]:
    """Coerce the 'contents' field to a list of dicts."""
    if not raw:
        return []
    items = list(raw.values()) if isinstance(raw, dict) else raw
    return [i for i in items if isinstance(i, dict)]


def fetch_data(endpoint: str, depth: int = 4) -> List[Dict[str, Any]]:
    """Fetch all entries from an endpoint's _graph.json."""
    if not HAS_CMIPLD:
        return []
    init_loader()
    try:
        url = f"{cmipld.prefix()}:{endpoint}/_graph.json"
        data = _with_retry(lambda: cmipld.get(url, depth=depth))
        return _normalise_contents(data.get('contents')) if data else []
    except Exception as e:
        print(f"  Warning: Could not fetch {endpoint}: {e}")
        return []


def fetch_entry(endpoint: str, entry_id: str, depth: int = 4) -> Optional[Dict[str, Any]]:
    """Fetch a single entry."""
    if not HAS_CMIPLD:
        return None
    init_loader()
    try:
        url = f"{cmipld.prefix()}:{endpoint}/{entry_id}"
        return _with_retry(lambda: cmipld.get(url, depth=depth))
    except Exception as e:
        print(f"  Warning: Could not fetch {endpoint}/{entry_id}: {e}")
        return None


def list_entries(endpoint: str) -> List[str]:
    """List all entry IDs for an endpoint."""
    if not HAS_CMIPLD:
        return []
    init_loader()
    try:
        url = f"{cmipld.prefix()}:{endpoint}/_graph.json"
        
        data = _with_retry(lambda: cmipld.get(url, depth=0))
        
        print(data)
        
        if data and 'contents' in data:
            return sorted(
                item.get('@id') or item.get('validation_key')
                for item in data['contents']
                if isinstance(item, dict)
                and (item.get('@id') or item.get('validation_key'))
                and not (item.get('@id', '')).startswith('_')
            )
    except Exception as e:
        print(f"  Warning: Could not list entries for {endpoint}: {e}")
    return []
