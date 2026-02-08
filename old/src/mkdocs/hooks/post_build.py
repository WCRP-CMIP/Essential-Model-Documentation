#!/usr/bin/env python3
"""
Post-build hook to add HTML files to search index.
This runs after MkDocs build and enhances the search index with HTML files.
"""
import json
import re
from pathlib import Path


def on_post_build(config):
    """
    Hook that runs after build completes.
    Parses HTML files and adds them to search_index.json.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Warning: beautifulsoup4 not installed. HTML search indexing skipped.")
        print("Install with: pip install beautifulsoup4")
        return
    
    site_dir = Path(config['site_dir'])
    docs_dir = Path(config['docs_dir'])
    
    # Find search index
    search_index_path = site_dir / 'search' / 'search_index.json'
    
    if not search_index_path.exists():
        print("Warning: search_index.json not found")
        return
    
    # Load existing search index
    with open(search_index_path, 'r', encoding='utf-8') as f:
        search_data = json.load(f)
    
    # Directories with HTML files
    html_dirs = ['model', 'model_component', 'model_family', 'bidk']
    max_text_length = 1000
    
    html_count = 0
    
    # Process each directory
    for html_dir in html_dirs:
        src_dir = docs_dir / html_dir
        if not src_dir.exists():
            continue
        
        for html_file in src_dir.glob('*.html'):
            try:
                # Read and parse HTML
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove scripts and styles
                for tag in soup(['script', 'style']):
                    tag.decompose()
                
                # Extract title
                title = None
                h1_tag = soup.find('h1')
                if h1_tag:
                    title = h1_tag.get_text(strip=True)
                
                if not title:
                    title_tag = soup.find('title')
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                
                if not title:
                    emd_title = soup.find(class_='emd-title')
                    if emd_title:
                        title = emd_title.get_text(strip=True)
                
                if not title:
                    title = html_file.stem.replace('-', ' ').title()
                
                # Extract text
                text = soup.get_text(separator=' ', strip=True)
                text = re.sub(r'\s+', ' ', text)
                
                if len(text) > max_text_length:
                    text = text[:max_text_length] + '...'
                
                # Create search entry
                location = f"{html_dir}/{html_file.name}"
                
                search_entry = {
                    'location': location,
                    'title': title,
                    'text': text
                }
                
                # Add to index
                if 'docs' in search_data:
                    search_data['docs'].append(search_entry)
                    html_count += 1
                
            except Exception as e:
                print(f"Warning: Could not index {html_file.name}: {e}")
    
    # Save enhanced index
    if html_count > 0:
        with open(search_index_path, 'w', encoding='utf-8') as f:
            json.dump(search_data, f, ensure_ascii=False)
        
        print(f"✓ HTML Search: Indexed {html_count} HTML files")
    else:
        print("ℹ️ HTML Search: No HTML files found")
