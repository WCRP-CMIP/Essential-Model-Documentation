#!/usr/bin/env python3
"""
Pre-build hook: clean build directory.
"""

import shutil
from pathlib import Path


def on_pre_build(config, **kwargs):
    """Clean build directory and remove old SUMMARY.md."""
    docs_dir = Path(config['docs_dir']).resolve()
    site_dir = Path(config['site_dir'])
    
    # Delete old SUMMARY.md to force regeneration
    summary_path = docs_dir / 'SUMMARY.md'
    if summary_path.exists():
        summary_path.unlink()
    
    # Clean old build
    if site_dir.exists():
        shutil.rmtree(site_dir)
    
    site_dir.mkdir(parents=True, exist_ok=True)
