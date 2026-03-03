"""Helper utilities for model component page generation."""

import html
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Icons for sections
ICONS = {
    "description": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>',
    "domain": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>',
    "grid": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>',
    "coupling": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>',
    "tech": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg>',
    "reference": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>',
    "chevron": '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" /></svg>',
}

# Keywords to highlight in descriptions
HIGHLIGHT_KEYWORDS = [
    "CNRM", "NEMO", "ORCA", "SURFEX", "ARPEGE", "GELATO", "TACTIC",
    "atmosphere", "ocean", "sea ice", "land surface", "ice sheet",
    "tripolar", "Arakawa", "EVP", "rheology",
    "thermodynamic", "dynamic", "coupled", "embedded",
]


def is_none_value(value) -> bool:
    """Check if a value represents 'none' or is empty."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.lower() in ("none", "", "null")
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""
    return html.escape(str(text))


def create_jinja_env(template_dir: Path) -> Environment:
    """Create a Jinja2 environment with the template directory."""
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
    )
    return env


def create_section_macro(component_type: str):
    """Create a section macro for the given component type."""
    def section(title, icon_name, count=None, expanded=True):
        return {
            "title": title,
            "icon": ICONS.get(icon_name, ""),
            "count": count,
            "expanded": expanded,
        }
    return section


def create_domain_card_macro(component_type: str):
    """Create a domain card macro for the given component type."""
    def domain_card(domain, card_type="Component"):
        return {
            "domain": domain,
            "type": card_type,
        }
    return domain_card
