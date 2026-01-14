"""
Helpers package for page generation scripts.
"""

from .icons import ICONS
from .keywords import HIGHLIGHT_KEYWORDS
from .utils import (
    is_none_value,
    format_list,
    format_aliases,
    escape_html,
    highlight_keywords,
    parse_domain,
    parse_coupled_with,
    parse_code_base,
    parse_references,
    create_jinja_env,
    create_section_macro,
    create_domain_card_macro,
)

__all__ = [
    # Icons
    "ICONS",
    # Keywords
    "HIGHLIGHT_KEYWORDS",
    # Utility functions
    "is_none_value",
    "format_list",
    "format_aliases",
    "escape_html",
    "highlight_keywords",
    # Parsing functions
    "parse_domain",
    "parse_coupled_with",
    "parse_code_base",
    "parse_references",
    # Jinja2 helpers
    "create_jinja_env",
    "create_section_macro",
    "create_domain_card_macro",
]
