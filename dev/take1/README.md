# EMD Component JSON Files

This directory contains JSON files generated from the CNRM model EMD spreadsheet data.

## Generated Files

The following component JSON files have been created in the `components/` subdirectory:

1. **aerosol_TACTIC.json** - TACTIC aerosol scheme
2. **atmosphere_Arpege-Climat_Version_6_3.json** - ARPEGE-Climat v6.3
3. **atmosphere_HadAM3.json** - HadAM atmosphere component
4. **atmospheric-chemistry_REPROBUS-C_v2_0.json** - REPROBUS chemistry (hyphenated)
5. **land-surface_SURFEX_v8_modeling_platform.json** - SURFEX land surface (hyphenated)
6. **ocean-biogeochemistry_PISCESv2-gas.json** - PISCES biogeochemistry (hyphenated)
7. **ocean_NEMO_Nucleus_for_European_Modelling_of_the_Ocean_version_3_6_OPA.json** - NEMO ocean
8. **sea-ice_GELATO.json** - GELATO sea ice (hyphenated)

## Component Type Hyphenation

**Important:** All component types use hyphens instead of underscores to match realm naming conventions:

- `sea-ice` (not `sea_ice`)
- `land-surface` (not `land_surface`)
- `atmospheric-chemistry` (not `atmospheric_chemistry`)
- `ocean-biogeochemistry` (not `ocean_biogeochemistry`)

This applies to:
- The `component` field
- The `embedded_in` field
- Values in the `coupled_with` list

## Structure

Each JSON file follows the EMDModelComponent Pydantic model structure with:

- **component**: Component type (from controlled vocabulary, hyphenated)
- **name**: Component name
- **family**: Component family name  
- **description**: Scientific overview
- **code_base**: Source code location (URL or "private")
- **references**: List of citation objects with doi and citation text
- **embedded_in**: Host component (if embedded, hyphenated) 
- **coupled_with**: List of coupled components (if coupled, hyphenated)
- **native_horizontal_grid**: Horizontal grid specification
  - arrangement: Grid staggering type
  - horizontal_subgrids: List of subgrid specifications
    - cell_variable_type: Variable types at this location
    - horizontal_grid_cells: Grid cell properties
- **native_vertical_grid**: Vertical grid specification
  - vertical_coordinate: Coordinate type
  - n_z: Number of vertical layers (optional)
  - Other thickness/depth properties (optional)

## Known Issues

**Key Issues:**
1. ⚠️ **Truncated descriptions** - Source data has "..." placeholders
2. ⚠️ **Placeholder DOIs** - Some code_base URLs are not real
3. ⚠️ **Missing cell_variable_type** - Some grid subgrids lack this field in source data
4. ⚠️ **Multiple vertical grid entries** - Some VGRIDs have duplicate entries with different coordinate systems

## Validation

To validate these files against the Pydantic model:

```python
from esgvoc.api.data_descriptors.emd_model_component import EMDModelComponent
import json

with open('components/atmosphere_HadAM3.json') as f:
    data = json.load(f)
    component = EMDModelComponent(**data)
```

## Source

- **Generated from:** `recovered_EMD_Model_v0_993_CNRM.xlsx`
- **Date:** December 17, 2025
- **Modification:** Component types hyphenated to match realm conventions
