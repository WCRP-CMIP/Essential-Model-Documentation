"""
Shared utility functions for page generation scripts.
"""

import re
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .icons import ICONS
from .keywords import HIGHLIGHT_KEYWORDS


# Template directory (relative to helpers folder)
TEMPLATE_DIR = Path(__file__).parent / "templates"


def is_none_value(val: Any) -> bool:
    """Check if value represents 'none' (string 'none', None, or empty)."""
    if val is None:
        return True
    if isinstance(val, str) and val.lower() in ("none", ""):
        return True
    if isinstance(val, list) and len(val) == 0:
        return True
    return False


def format_list(items: Any) -> list:
    """Convert items to a list format, filtering out empty/none values."""
    if items is None:
        return []
    if isinstance(items, str):
        return [items] if items and not is_none_value(items) else []
    if isinstance(items, list):
        return [item for item in items if item and not is_none_value(item)]
    return []


def format_aliases(aliases: Any) -> list:
    """Convert aliases to a list format."""
    if aliases is None:
        return []
    if isinstance(aliases, str):
        return [aliases]
    if isinstance(aliases, list):
        return [a for a in aliases if a]
    return []


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def highlight_keywords(text: str, extra_keywords: Optional[list] = None) -> str:
    """
    Highlight keywords in text by wrapping them in <strong> tags.
    
    Args:
        text: The text to process
        extra_keywords: Additional keywords to highlight (e.g., model name, family)
    
    Returns:
        HTML string with keywords wrapped in <strong> tags
    """
    if not text:
        return ""
    
    # Combine default keywords with any extras
    keywords = HIGHLIGHT_KEYWORDS.copy()
    if extra_keywords:
        keywords.extend([kw for kw in extra_keywords if kw])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if not kw:
            continue
        kw_lower = kw.lower()
        if kw_lower not in seen:
            seen.add(kw_lower)
            unique_keywords.append(kw)
    
    # Sort by length (longest first) to avoid partial replacements
    unique_keywords.sort(key=len, reverse=True)
    
    # First escape the text
    escaped_text = escape_html(text)
    
    # Track replacements to avoid double-bolding
    placeholders = {}
    result = escaped_text
    
    for i, keyword in enumerate(unique_keywords):
        escaped_keyword = re.escape(escape_html(keyword))
        pattern = re.compile(
            r'(?<![a-zA-Z0-9])(' + escaped_keyword + r')(?![a-zA-Z0-9])',
            re.IGNORECASE
        )
        
        placeholder = f"__BOLD_PLACEHOLDER_{i}__"
        
        def replace_with_placeholder(match, ph=placeholder):
            matched_text = match.group(1)
            placeholders[f"{ph}{matched_text}"] = f"<strong>{matched_text}</strong>"
            return f"{ph}{matched_text}"
        
        result = pattern.sub(replace_with_placeholder, result)
    
    # Replace placeholders with actual bold tags
    for placeholder, replacement in placeholders.items():
        result = result.replace(placeholder, replacement)
    
    return result


def parse_domain(domain_data: Any) -> Optional[dict]:
    """Parse domain data into a standardized dict. Returns None if invalid."""
    if is_none_value(domain_data):
        return None
    
    if not isinstance(domain_data, dict):
        return None
    
    return {
        "title": domain_data.get("ui_label") or domain_data.get("description") or "Unknown",
        "id": domain_data.get("@id", ""),
        "aliases": format_aliases(domain_data.get("alias")),
        "validation_key": domain_data.get("validation_key", ""),
    }


def parse_coupled_with(coupled_data: Any) -> list:
    """Parse coupled_with data into a list of domain dicts."""
    if is_none_value(coupled_data):
        return []
    
    if isinstance(coupled_data, dict):
        parsed = parse_domain(coupled_data)
        return [parsed] if parsed else []
    
    if isinstance(coupled_data, list):
        result = []
        for item in coupled_data:
            if isinstance(item, str):
                continue
            parsed = parse_domain(item)
            if parsed:
                result.append(parsed)
        return result
    
    if isinstance(coupled_data, str):
        return []
    
    return []


def parse_code_base(code_base: Any) -> dict:
    """Parse code_base into a structured dict."""
    if is_none_value(code_base):
        return {"value": None, "is_private": False, "is_url": False}
    
    if not isinstance(code_base, str):
        return {"value": str(code_base), "is_private": False, "is_url": False}
    
    is_private = code_base.lower() == "private"
    is_url = code_base.startswith("http://") or code_base.startswith("https://")
    
    return {
        "value": code_base,
        "is_private": is_private,
        "is_url": is_url,
    }


def parse_references(references_data: Any) -> list:
    """Parse references into a list."""
    if isinstance(references_data, str):
        return [references_data] if references_data and not is_none_value(references_data) else []
    elif isinstance(references_data, list):
        return [r for r in references_data if r and not is_none_value(r)]
    return []


def create_jinja_env(template_dir: Optional[Path] = None) -> Environment:
    """
    Create and configure Jinja2 environment.
    
    Args:
        template_dir: Path to templates directory. Defaults to helpers/templates.
    
    Returns:
        Configured Jinja2 Environment
    """
    if template_dir is None:
        template_dir = TEMPLATE_DIR
    
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    
    # Add shared globals
    env.globals["ICONS"] = ICONS
    
    return env


def create_section_macro(css_prefix: str = "component"):
    """
    Create a section macro function for collapsible sections.
    
    Args:
        css_prefix: CSS class prefix (e.g., 'component' or 'model')
    
    Returns:
        Section macro function
    """
    def section_macro(title, icon, expanded=False, *, caller):
        """Section macro - caller is passed by Jinja2's {% call %} block."""
        expanded_class = "expanded" if expanded else ""
        return f'''<section class="{css_prefix}-section {expanded_class}">
                <div class="{css_prefix}-section-header" onclick="toggleSection(this)">
                    <div class="{css_prefix}-section-title-wrapper">
                        <div class="{css_prefix}-section-icon">{icon}</div>
                        <h2 class="{css_prefix}-section-title">{title}</h2>
                    </div>
                    <div class="{css_prefix}-section-toggle">{ICONS["chevron"]}</div>
                </div>
                <div class="{css_prefix}-section-content">
                    <div class="{css_prefix}-section-body">
                        <div class="{css_prefix}-section-divider"></div>
                        {caller()}
                    </div>
                </div>
            </section>'''
    return section_macro


def create_domain_card_macro(css_prefix: str = "component"):
    """
    Create a domain card macro function.
    
    Args:
        css_prefix: CSS class prefix (e.g., 'component' or 'model')
    
    Returns:
        Domain card macro function
    """
    def domain_card_macro(title, card_type, domain_id, description, aliases):
        aliases_html = "\n".join(
            f'<span class="{css_prefix}-meta-tag">{escape_html(str(alias))}</span>' 
            for alias in aliases if alias
        )
        return f'''<div class="{css_prefix}-domain-card">
                        <div class="{css_prefix}-domain-card-header">
                            <span class="{css_prefix}-domain-card-title">{escape_html(str(title))}</span>
                            <span class="{css_prefix}-domain-card-type">{escape_html(str(card_type))}</span>
                        </div>
                        <div class="{css_prefix}-domain-card-id">@id: {escape_html(str(domain_id))}</div>
                        <p class="{css_prefix}-domain-card-description">{escape_html(str(description))}</p>
                        <div class="{css_prefix}-domain-card-meta">
                            {aliases_html}
                        </div>
                    </div>'''
    return domain_card_macro
