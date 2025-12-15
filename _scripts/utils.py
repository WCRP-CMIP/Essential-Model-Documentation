"""Shared utilities for EMD CV extraction and esgvoc conversion."""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional


# Section to descriptor mapping for EMD Section 7 CVs
# Based on actual CV names in the EMD document
SECTION_TO_DESCRIPTOR = {
    "7.1": "model_component",           # component CV
    "7.2": "calendar",                   # calendar CV
    "7.3": "horizontal_grid_arrangement", # arrangement CV
    "7.4": "horizontal_grid_cell_variable_type",  # cell_variable_type CV
    "7.5": "grid_region",                # region CV
    "7.6": "horizontal_grid_type",       # grid_type CV
    "7.7": "horizontal_grid_mapping",    # grid_mapping CV
    "7.8": "horizontal_grid_temporal_refinement", # temporal_refinement CV
    "7.9": "horizontal_units",           # horizontal_units CV
    "7.10": "truncation_method",         # truncation_method CV
    "7.11": "coordinate",                # vertical_coordinate CV
}


def normalize_id(name: str) -> str:
    """
    Convert display name to ID format.

    Examples:
        'Regular Latitude Longitude' → 'regular-latitude-longitude'
        'Arakawa A' → 'arakawa-a'

    Args:
        name: Display name to normalize

    Returns:
        Normalized ID (lowercase with hyphens)
    """
    # Remove special characters except spaces and hyphens
    cleaned = re.sub(r'[^a-zA-Z0-9\s\-]', '', name)
    # Convert to lowercase
    cleaned = cleaned.lower()
    # Replace spaces with hyphens
    cleaned = re.sub(r'\s+', '-', cleaned)
    # Remove duplicate hyphens
    cleaned = re.sub(r'-+', '-', cleaned)
    # Strip leading/trailing hyphens
    return cleaned.strip('-')


def generate_drs_name(id_str: str, table_value: Optional[str] = None) -> str:
    """
    Generate DRS name (typically uppercase version of ID).

    Args:
        id_str: The normalized ID string
        table_value: Optional DRS name from table (takes precedence)

    Returns:
        DRS name (uppercase format)
    """
    if table_value and table_value.strip():
        return table_value.strip()
    # Convert ID to uppercase with underscores
    return id_str.replace('-', '_').upper()


def load_json(path: Path) -> Dict[str, Any]:
    """
    Load JSON from file.

    Args:
        path: Path to JSON file

    Returns:
        Parsed JSON data
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(path: Path, data: Dict[str, Any], indent: int = 4) -> None:
    """
    Write JSON to file with proper formatting.

    Args:
        path: Path to write JSON file
        data: Data to serialize
        indent: Indentation level (default: 4)
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
        f.write('\n')  # Add trailing newline


def get_descriptor_from_section(section_num: str) -> Optional[str]:
    """
    Get descriptor name from section number.

    Args:
        section_num: Section number (e.g., "7.1", "7.2")

    Returns:
        Descriptor name or None if not mapped
    """
    return SECTION_TO_DESCRIPTOR.get(section_num)


def create_universe_context(descriptor_name: str) -> Dict[str, Any]:
    """
    Create JSON-LD context for universe descriptor.

    Args:
        descriptor_name: Name of the descriptor

    Returns:
        Context dictionary
    """
    return {
        "@context": {
            "@base": f"https://esgvoc.ipsl.fr/resource/universe/{descriptor_name}/",
            "@vocab": "http://schema.org/",
            "id": "@id",
            "type": "@type",
            "description": {"@id": "https://schema.org/description"},
            "drs_name": {"@id": "acronym"}
        }
    }


def create_project_context(descriptor_name: str) -> Dict[str, Any]:
    """
    Create JSON-LD context for project descriptor.

    Args:
        descriptor_name: Name of the descriptor

    Returns:
        Context dictionary
    """
    return {
        "@context": {
            "id": "@id",
            "type": "@type",
            "@base": f"https://esgvoc.ipsl.fr/resource/universe/{descriptor_name}/",
            descriptor_name: f"https://esgvoc.ipsl.fr/resource/universe/{descriptor_name}"
        }
    }


def create_universe_term(
    term_id: str,
    descriptor_name: str,
    description: str,
    drs_name: str,
    **extra_fields
) -> Dict[str, Any]:
    """
    Create universe term JSON structure.

    Args:
        term_id: Term identifier
        descriptor_name: Descriptor type
        description: Term description
        drs_name: DRS name (uppercase)
        **extra_fields: Additional fields to include

    Returns:
        Term dictionary
    """
    term = {
        "@context": "000_context.jsonld",
        "id": term_id,
        "type": descriptor_name,
        "description": description,
        "drs_name": drs_name
    }
    term.update(extra_fields)
    return term


def create_project_term(term_id: str, descriptor_name: str) -> Dict[str, Any]:
    """
    Create minimal project term JSON structure (reference to universe).

    Args:
        term_id: Term identifier
        descriptor_name: Descriptor type

    Returns:
        Term dictionary
    """
    return {
        "@context": "000_context.jsonld",
        "id": term_id,
        "type": descriptor_name
    }
