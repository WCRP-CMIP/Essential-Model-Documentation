"""
Custom MkDocs search plugin that indexes HTML files.

This plugin extends MkDocs Material search to include HTML files in the search index.
Works by parsing HTML files after generation and adding them to search_index.json.
"""
import json
import re
from pathlib import Path
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options


class HTMLSearchPlugin(BasePlugin):
    """
    Plugin to add HTML files to MkDocs search index.
    Compatible with MkDocs Material theme search.
    """
    
    config_scheme = (
        ('html_dirs', config_options.Type(list, default=['model', 'model_component', 'model_family', 'bidk'])),
        ('max_text_length', config_options.Type(int, default=1000)),
    )
    
    def on_post_build(self, config):
        """
        After build completes, parse HTML files and add to search index.
        This runs after the standard search plugin has created search_index.json.
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            print("Warning: beautifulsoup4 not installed. HTML search indexing skipped.")
            return config
        
        site_dir = Path(config['site_dir'])
        docs_dir = Path(config['docs_dir'])
        
        # Load existing search index created by MkDocs
        search_index_path = site_dir / 'search' / 'search_index.json'
        
        if not search_index_path.exists():
            print("Warning: search_index.json not found. HTML indexing skipped.")
            return config
        
        # Read existing search index
        with open(search_index_path, 'r', encoding='utf-8') as f:
            search_data = json.load(f)
        
        # Count how many entries we add
        html_count = 0
        
        # Get configuration
        html_dirs = self.config.get('html_dirs', [])
        max_length = self.config.get('max_text_length', 1000)
        
        # Process each HTML directory
        for html_dir in html_dirs:
            src_dir = docs_dir / html_dir
            if not src_dir.exists():
                continue
            
            # Find all HTML files in source directory
            for html_file in src_dir.glob('*.html'):
                try:
                    # Parse HTML file
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Remove script and style tags
                    for tag in soup(['script', 'style']):
                        tag.decompose()
                    
                    # Extract title (try multiple methods)
                    title = None
                    
                    # Try h1 first
                    h1_tag = soup.find('h1')
                    if h1_tag:
                        title = h1_tag.get_text(strip=True)
                    
                    # Try title tag
                    if not title:
                        title_tag = soup.find('title')
                        if title_tag:
                            title = title_tag.get_text(strip=True)
                    
                    # Try emd-title class
                    if not title:
                        emd_title = soup.find(class_='emd-title')
                        if emd_title:
                            title = emd_title.get_text(strip=True)
                    
                    # Fallback to filename
                    if not title:
                        title = html_file.stem.replace('-', ' ').title()
                    
                    # Extract main text content
                    text_content = soup.get_text(separator=' ', strip=True)
                    
                    # Clean up whitespace
                    text_content = re.sub(r'\s+', ' ', text_content)
                    
                    # Limit text length
                    if len(text_content) > max_length:
                        text_content = text_content[:max_length] + '...'
                    
                    # Build location path (relative to site root)
                    location = f"{html_dir}/{html_file.name}"
                    
                    # Create search entry in MkDocs format
                    search_entry = {
                        'location': location,
                        'title': title,
                        'text': text_content
                    }
                    
                    # Add to search index docs array
                    if 'docs' in search_data:
                        search_data['docs'].append(search_entry)
                        html_count += 1
                    
                except Exception as e:
                    print(f"Warning: Could not index {html_file.name}: {e}")
                    continue
        
        # Save enhanced search index
        if html_count > 0:
            with open(search_index_path, 'w', encoding='utf-8') as f:
                json.dump(search_data, f, ensure_ascii=False, indent=None)
            
            print(f"✓ HTML Search: Indexed {html_count} HTML files")
        else:
            print("ℹ️ HTML Search: No HTML files found to index")
        
        return config

