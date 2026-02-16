"""
EMD Data Summary Configuration.

Configures the generate_summaries.py script to produce
summary pages for all EMD data types.

Uses branch-aware data loading:
- docs branch: fetch from remote
- production: mount local files with cmipld.map_current()
"""

import sys
from pathlib import Path

# Add helpers to path
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.data_loader import init_loader, fetch_data

# Initialize the loader (mounts local files on production)
init_loader()


# =============================================================================
# DATA FETCHING
# =============================================================================

def fetch_data_for_endpoint(endpoint):
    """Fetch data from EMD - uses branch-aware loading."""
    return fetch_data(endpoint, depth=2)


# =============================================================================
# DATA TYPE CONFIGURATIONS - COMPREHENSIVE COLUMNS
# =============================================================================

DATA_TYPES = {
    "horizontal_grid_cells": {
        "title": "Grid Cells",
        "endpoint": "horizontal_grid_cells",
        "columns": [
            "id", "description", "grid_type", "grid_mapping", "region", 
            "n_cells", "x_resolution", "y_resolution", "units",
            "southernmost_latitude", "westernmost_longitude",
            "truncation_method", "truncation_number", "temporal_refinement"
        ],
        "description": "Fundamental grid cell definitions (Stage 1)."
    },
    "horizontal_subgrid": {
        "title": "Horizontal Subgrids", 
        "endpoint": "horizontal_subgrid",
        "columns": [
            "id", "description", "horizontal_grid_cells", "cell_variable_type"
        ],
        "description": "Subgrid definitions linking cells to variable types (Stage 1)."
    },
    "horizontal_computational_grid": {
        "title": "Horizontal Computational Grids",
        "endpoint": "horizontal_computational_grid",
        "columns": [
            "id", "description", "arrangement", "horizontal_subgrids"
        ],
        "description": "Computational grid configurations (Stage 2a)."
    },
    "vertical_computational_grid": {
        "title": "Vertical Computational Grids",
        "endpoint": "vertical_computational_grid", 
        "columns": [
            "id", "description", "vertical_coordinate", "n_z",
            "top_layer_thickness", "bottom_layer_thickness", "total_thickness"
        ],
        "description": "Vertical grid configurations (Stage 2b)."
    },
    "component_family": {
        "title": "Component Families",
        "endpoint": "model_family",
        "filter": {"family_type": "component"},
        "columns": [
            "id", "description", "primary_institution", "collaborative_institutions",
            "scientific_domains", "shared_code_base", "source_code_repository",
            "programming_languages", "license", "established", "references"
        ],
        "description": "Families of related model components sharing common code."
    },
    "source_family": {
        "title": "Model Families (Earth System)",
        "endpoint": "model_family",
        "filter": {"family_type": "model"},
        "columns": [
            "id", "description", "primary_institution", "collaborative_institutions",
            "scientific_domains", "representative_member", "shared_code_base", 
            "source_code_repository", "programming_languages", "license",
            "established", "evolution", "website", "references"
        ],
        "description": "Families of related Earth System models."
    },
    "model_component": {
        "title": "Model Components",
        "endpoint": "model_component",
        "columns": [
            "id", "name", "description", "component", "family", 
            "code_base", "references"
        ],
        "description": "Registered model components (Stage 3 input)."
    },
    "component_config": {
        "title": "Component Configurations",
        "endpoint": "component_config",
        "columns": [
            "id", "ui_label", "description", "model_component", 
            "horizontal_computational_grid", "vertical_computational_grid"
        ],
        "description": "Component-grid configurations (Stage 3 output)."
    },
    "model": {
        "title": "Models (source_id)",
        "endpoint": "model",
        "columns": [
            "id", "name", "description", "family", "release_year",
            "dynamic_components", "prescribed_components", "omitted_components",
            "component_configs", "embedded_components", "coupling_groups",
            "calendar", "references"
        ],
        "description": "Registered CMIP models (Stage 4 output)."
    }
}


# =============================================================================
# INDEX PAGE CONFIGURATION
# =============================================================================

STAGES = [
    ("Stage 1: Grid Foundations", ["horizontal_grid_cells", "horizontal_subgrid"]),
    ("Stage 2: Computational Grids", ["horizontal_computational_grid", "vertical_computational_grid"]),
    ("Model/Component Families", ["component_family", "source_family"]),
    ("Stage 3: Model Components", ["model_component", "component_config"]),
    ("Stage 4: Models", ["model"]),
]


# =============================================================================
# OUTPUT CONFIGURATION
# =============================================================================

OUTPUT_DIR = "data-summaries"
EXPORT_JSON = True
