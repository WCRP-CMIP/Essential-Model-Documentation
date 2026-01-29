#!/usr/bin/env python3
"""
Inject README.md content into index.md after the documentation tip section.

This hook finds the tip marker in index.md and injects the project's
README.md content after it, providing project information on the home page.
"""

from pathlib import Path


# Configuration
CONFIG = {
    # Marker to find in index.md (content injected after this section)
    'tip_marker': '!!! tip "Documentation in progress"',
    
    # Section heading for injected content
    'section_heading': '## Project Information',
    
    # Enable/disable injection
    'enabled': True,
}


def on_page_markdown(markdown, page, config, files):
    """
    Hook that processes page markdown before conversion to HTML.
    Only processes index.md to inject README content.
    """
    if not CONFIG['enabled']:
        return markdown
    
    # Only process the main index page
    if page.file.src_path != 'index.md':
        return markdown
    
    tip_marker = CONFIG['tip_marker']
    
    # Check if tip marker exists
    if tip_marker not in markdown:
        return markdown
    
    # Find README.md at project root
    docs_dir = Path(config['docs_dir'])
    project_root = docs_dir.parent
    readme_path = project_root / 'README.md'
    
    if not readme_path.exists():
        print(f"⚠️  README.md not found at {readme_path}")
        return markdown
    
    # Read README content
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read().strip()
        print(f"✅ Injecting README.md ({len(readme_content)} chars) into index.md")
    except Exception as e:
        print(f"⚠️  Error reading README.md: {e}")
        return markdown
    
    # Find the tip section and inject README content after it
    lines = markdown.split('\n')
    new_lines = []
    in_tip_section = False
    tip_section_ended = False
    
    for line in lines:
        new_lines.append(line)
        
        # Detect start of tip section
        if tip_marker in line:
            in_tip_section = True
            continue
        
        # Detect end of tip section (next non-indented content)
        if in_tip_section and not tip_section_ended:
            # Tip section ends when we hit a non-empty, non-indented line
            if line.strip() and not line.startswith('    '):
                # Insert README content before this line
                new_lines.insert(-1, '')
                new_lines.insert(-1, CONFIG['section_heading'])
                new_lines.insert(-1, '')
                new_lines.insert(-1, readme_content)
                new_lines.insert(-1, '')
                tip_section_ended = True
    
    # If tip section was at end of file, append README
    if in_tip_section and not tip_section_ended:
        new_lines.append('')
        new_lines.append(CONFIG['section_heading'])
        new_lines.append('')
        new_lines.append(readme_content)
    
    return '\n'.join(new_lines)
