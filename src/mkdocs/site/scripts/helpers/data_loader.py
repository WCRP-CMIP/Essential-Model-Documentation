"""
Branch-aware data loading utilities.

Handles loading data differently depending on whether we're on:
- docs branch: fetch from remote via cmipld prefix URLs
- production branch: mount local files with cmipld.map_current()
"""

import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

# Try to import cmipld
try:
    import cmipld
    CMIPLD_AVAILABLE = True
except ImportError:
    cmipld = None
    CMIPLD_AVAILABLE = False


def get_current_branch() -> str:
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def get_repo_root() -> Optional[Path]:
    """Get the repository root directory."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def is_docs_branch() -> bool:
    """Check if we're on the docs branch."""
    return get_current_branch() == "docs"


def is_production_branch() -> bool:
    """Check if we're on the production branch."""
    return get_current_branch() == "production"


def setup_for_branch():
    """
    Setup cmipld for the current branch.
    
    On production: mount local files with map_current()
    On docs: use remote prefix URLs
    
    Returns True if local files are mounted.
    """
    if not CMIPLD_AVAILABLE:
        print("  Warning: cmipld not available")
        return False
    
    branch = get_current_branch()

    if branch == "production":
        # Mount local files so cmipld resolves prefix: URLs to the local repo
        try:
            prefix = cmipld.prefix()
            cmipld.map_current(prefix)
            print(f"  Branch: {branch} - mounted local files as '{prefix}:'")
            return True
        except Exception as e:
            print(f"  Warning: Could not mount local files: {e}")
            return False
    else:
        # All other branches (docs, main, src-data, feature branches, CI) —
        # fetch from remote prefix URLs, no local mapping
        print(f"  Branch: {branch} - using remote prefix URLs")
        return False


# Singleton to track if we've initialized
_initialized = False
_use_local = False


def init_loader():
    """Initialize the data loader (call once at script start)."""
    global _initialized, _use_local
    if not _initialized:
        _use_local = setup_for_branch()
        _initialized = True
    return _use_local


def get_use_local() -> bool:
    """Get whether we're using local files."""
    global _initialized, _use_local
    if not _initialized:
        init_loader()
    return _use_local


def _restart_ldr() -> bool:
    """
    Drop and re-import cmipld to restart the LDR server after it has been
    killed (e.g. by generate_contributors.py's subprocess exiting).
    Resets the loader state so the next call to init_loader() re-runs setup.
    """
    global _initialized, _use_local, _default_loader, cmipld, CMIPLD_AVAILABLE
    import sys, time

    for key in [k for k in sys.modules if k.startswith("cmipld")]:
        del sys.modules[key]

    try:
        import cmipld as _cmipld
        cmipld = _cmipld
        CMIPLD_AVAILABLE = True
        # Wait up to 10 s for the server to be ready
        deadline = time.monotonic() + 10.0
        while time.monotonic() < deadline:
            try:
                cmipld.client.get_mappings()
                break
            except Exception:
                time.sleep(0.5)
        # Reset loader state so init_loader() re-runs branch setup
        _initialized = False
        _use_local = False
        _default_loader = None
        init_loader()
        return True
    except Exception as e:
        print(f"  Warning: Could not restart LDR server: {e}")
        CMIPLD_AVAILABLE = False
        return False


def _is_connection_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "connection refused" in msg or "max retries" in msg or "connectionerror" in msg



def _get_graph(endpoint: str, depth: int):
    """Fetch the graph file for an endpoint.
    Tries _graph.json first (the generated convention), then _graph.jsonld
    (the source-branch name) as a fallback for endpoints not yet graphified.
    """
    prefix = cmipld.prefix()
    for name in ('_graph.json', '_graph.jsonld'):
        url = f"{prefix}:{endpoint}/{name}"
        try:
            data = cmipld.get(url, depth=depth)
            if data and '_error' not in data:
                return data
        except Exception:
            pass
    return None
    """
    Coerce the 'contents' field to a plain list of dicts regardless of how
    the JSON-LD compaction serialised it at any depth.

    depth=2  -> list of dicts (normal case)
    depth>=4 -> may be a dict keyed by @id, or values may be bare strings
                (unresolved @id refs) — those are filtered out.
    """
    if not raw:
        return []
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict):
        items = list(raw.values())
    else:
        return []
    # Drop bare strings, None, or any non-object that slipped through
    return [i for i in items if isinstance(i, dict)]


def fetch_data(endpoint: str, depth: int = 4) -> List[Dict[str, Any]]:
    """
    Fetch data contents from an endpoint.
    If the LDR server has been killed mid-build, restarts it and retries once.
    """
    if not CMIPLD_AVAILABLE:
        print(f"  Warning: cmipld not available for {endpoint}")
        return []

    init_loader()

    for attempt in range(2):
        try:
            data = _get_graph(endpoint, depth=depth)
            if data and '_error' not in data:
                return _normalise_contents(data.get('contents'))
            return []
        except Exception as e:
            if attempt == 0 and _is_connection_error(e):
                print(f"  Warning: LDR connection lost for {endpoint} — restarting server...")
                if not _restart_ldr():
                    break
            else:
                print(f"  Warning: Could not fetch {endpoint}: {e}")
                break

    return []


def fetch_entry(endpoint: str, entry_id: str, depth: int = 4) -> Optional[Dict[str, Any]]:
    """
    Fetch a single entry from an endpoint.
    If the LDR server has been killed mid-build, restarts it and retries once.
    """
    if not CMIPLD_AVAILABLE:
        return None

    init_loader()

    for attempt in range(2):
        try:
            prefix = cmipld.prefix()
            url = f"{prefix}:{endpoint}/{entry_id}"
            return cmipld.get(url, depth=depth)
        except Exception as e:
            if attempt == 0 and _is_connection_error(e):
                print(f"  Warning: LDR connection lost for {endpoint}/{entry_id} — restarting server...")
                if not _restart_ldr():
                    break
            else:
                print(f"  Warning: Could not fetch {endpoint}/{entry_id}: {e}")
                break

    return None


def list_entries(endpoint: str) -> List[str]:
    """
    List all entry IDs for an endpoint.

    Uses depth=1 so contents come back as proper {"@id": "..."} dicts,
    avoiding the bare-string ambiguity of depth=0.
    """
    if not CMIPLD_AVAILABLE:
        return []

    init_loader()

    for attempt in range(2):
        try:
            data = _get_graph(endpoint, depth=1)
            if not data:
                return []

            raw = data.get('contents') or []
            if isinstance(raw, dict):
                raw = list(raw.values())

            entries = []
            for item in raw:
                if isinstance(item, str):
                    raw_id = item
                elif isinstance(item, dict):
                    raw_id = item.get('@id') or item.get('validation_key') or ''
                else:
                    continue

                if not raw_id:
                    continue

                # Strip prefix: and path, keep just the entry key
                # e.g. "emd:model/cesm2" -> "cesm2"
                entry_id = raw_id.split('/')[-1].split(':')[-1]
                if entry_id and not entry_id.startswith('_'):
                    entries.append(entry_id)

            return sorted(set(entries))

        except Exception as e:
            if attempt == 0 and _is_connection_error(e):
                print(f"  Warning: LDR connection lost listing {endpoint} — restarting server...")
                if not _restart_ldr():
                    break
            else:
                print(f"  Warning: Could not list entries for {endpoint}: {e}")
                break

    return []


# For backwards compatibility
class DataLoader:
    """Branch-aware data loader for EMD content."""
    
    def __init__(self, prefix: str = "emd", base_url: str = "https://emd.mipcvs.dev"):
        self.prefix = prefix
        self.base_url = base_url
        self.use_local = init_loader()
        self.branch = get_current_branch()
    
    def list_entries(self, endpoint: str) -> List[str]:
        return list_entries(endpoint)
    
    def get(self, endpoint: str, entry_id: str, depth: int = 4) -> Optional[Dict[str, Any]]:
        return fetch_entry(endpoint, entry_id, depth)
    
    def get_all(self, endpoint: str, depth: int = 4) -> List[Dict[str, Any]]:
        return fetch_data(endpoint, depth)
    
    def get_graph_contents(self, endpoint: str, depth: int = 4) -> List[Dict[str, Any]]:
        return fetch_data(endpoint, depth)


_default_loader = None

def get_loader(prefix: str = "emd", base_url: str = "https://emd.mipcvs.dev") -> DataLoader:
    """Get or create the default data loader."""
    global _default_loader
    if _default_loader is None:
        _default_loader = DataLoader(prefix, base_url)
    return _default_loader


def reset_loader():
    """Reset the loader state (for testing)."""
    global _default_loader, _initialized, _use_local
    _default_loader = None
    _initialized = False
    _use_local = False
