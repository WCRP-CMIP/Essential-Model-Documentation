#!/usr/bin/env python3
"""
Files hook for MkDocs.
Ensures generated HTML files are converted to markdown for search indexing.
"""

from pathlib import Path
from mkdocs.structure.files import File


def on_files(files, config):
    """
    Hook that runs after files are collected but before they're processed.
    This ensures generated files are included in the build and search index.
    """
    docs_dir = Path(config['docs_dir'])
    
    # Directories containing generated files
    generated_dirs = ['model', 'model_component', 'model_family', 'bidk']
    
    # Find all HTML files in generated directories
    for gen_dir in generated_dirs:
        dir_path = docs_dir / gen_dir
        if not dir_path.exists():
            continue
        
        for html_file in dir_path.glob('*.html'):
            # Check if this file is already in the files collection
            rel_path = html_file.relative_to(docs_dir)
            
            # Convert .html to .md path for MkDocs
            md_path = str(rel_path).replace('.html', '.md')
            
            # Check if already exists in files
            exists = any(f.src_path == md_path for f in files)
            
            if not exists:
                # Rename .html to .md so MkDocs can index it
                md_file = html_file.with_suffix('.md')
                
                # If .md doesn't exist, rename .html to .md
                if not md_file.exists():
                    html_file.rename(md_file)
                    print(f"   Converted: {rel_path} → {md_path}")
                
                # Add to files collection
                try:
                    file = File(
                        md_path,
                        docs_dir,
                        config['site_dir'],
                        config['use_directory_urls']
                    )
                    files.append(file)
                    print(f"   Added to index: {md_path}")
                except Exception as e:
                    print(f"   Warning: Could not add {md_path}: {e}")
    
    return files
