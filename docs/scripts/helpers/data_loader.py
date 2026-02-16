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
    """Check if we're on a production branch (main, pages, etc.)."""
    branch = get_current_branch()
    return branch in ("main", "pages", "gh-pages", "production")


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
    
    if branch == "docs":
        print(f"  Branch: {branch} - using remote prefix URLs")
        return False
    else:
        # Production or other branches - mount local files
        try:
            prefix = cmipld.prefix()
            cmipld.map_current(prefix)
            print(f"  Branch: {branch} - mounted local files as '{prefix}:'")
            return True
        except Exception as e:
            print(f"  Warning: Could not mount local files: {e}")
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


def fetch_data(endpoint: str, depth: int = 2) -> List[Dict[str, Any]]:
    """
    Fetch data contents from an endpoint.
    
    Works for both local (mounted) and remote data.
    """
    if not CMIPLD_AVAILABLE:
        print(f"  Warning: cmipld not available for {endpoint}")
        return []
    
    # Ensure initialized
    init_loader()
    
    try:
        # Get prefix (works for both local and remote)
        prefix = cmipld.prefix()
        url = f"{prefix}:{endpoint}/_graph.json"
        
        data = cmipld.get(url, depth=depth)
        if data and 'contents' in data:
            return data['contents']
        return []
    except Exception as e:
        print(f"  Warning: Could not fetch {endpoint}: {e}")
        return []


def fetch_entry(endpoint: str, entry_id: str, depth: int = 2) -> Optional[Dict[str, Any]]:
    """
    Fetch a single entry from an endpoint.
    """
    if not CMIPLD_AVAILABLE:
        return None
    
    # Ensure initialized
    init_loader()
    
    try:
        prefix = cmipld.prefix()
        url = f"{prefix}:{endpoint}/{entry_id}"
        return cmipld.get(url, depth=depth)
    except Exception as e:
        print(f"  Warning: Could not fetch {endpoint}/{entry_id}: {e}")
        return None


def list_entries(endpoint: str) -> List[str]:
    """
    List all entry IDs for an endpoint.
    """
    if not CMIPLD_AVAILABLE:
        return []
    
    # Ensure initialized
    init_loader()
    
    try:
        prefix = cmipld.prefix()
        url = f"{prefix}:{endpoint}/_graph.json"
        data = cmipld.get(url, depth=0)
        
        if data and 'contents' in data:
            entries = []
            for item in data['contents']:
                if isinstance(item, dict):
                    entry_id = item.get('@id') or item.get('validation_key')
                    if entry_id and not entry_id.startswith('_'):
                        entries.append(entry_id)
            return sorted(entries)
    except Exception as e:
        print(f"  Warning: Could not list entries for {endpoint}: {e}")
    
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
    
    def get(self, endpoint: str, entry_id: str, depth: int = 2) -> Optional[Dict[str, Any]]:
        return fetch_entry(endpoint, entry_id, depth)
    
    def get_all(self, endpoint: str, depth: int = 2) -> List[Dict[str, Any]]:
        return fetch_data(endpoint, depth)
    
    def get_graph_contents(self, endpoint: str, depth: int = 2) -> List[Dict[str, Any]]:
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
