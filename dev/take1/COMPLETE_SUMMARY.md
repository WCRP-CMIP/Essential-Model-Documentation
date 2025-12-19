# EMD Data Files - Complete Summary

## Overview

All EMD data files have been successfully created on your filesystem at:
`/Users/daniel.ellis/WIPwork/Essential-Model-Documentation/data/`

## Directory Structure

```
data/
├── README.md                           # User guide
├── SUMMARY.md                          # Original component summary
├── components/                         # 8 model component files
│   ├── aerosol_TACTIC.json
│   ├── atmosphere_Arpege-Climat_Version_6_3.json
│   ├── atmosphere_HadAM3.json
│   ├── atmospheric-chemistry_REPROBUS-C_v2_0.json
│   ├── land-surface_SURFEX_v8_modeling_platform.json
│   ├── ocean-biogeochemistry_PISCESv2-gas.json
│   ├── ocean_NEMO_Nucleus_for_European_Modelling_of_the_Ocean_version_3_6_OPA.json
│   └── sea-ice_GELATO.json
├── component-types/                    # 8 ComponentType CV terms
│   ├── aerosol.json
│   ├── atmosphere.json
│   ├── atmospheric-chemistry.json
│   ├── land-ice.json
│   ├── land-surface.json
│   ├── ocean-biogeochemistry.json
│   ├── ocean.json
│   └── sea-ice.json
├── calendars/                          # 7 Calendar CV terms
│   ├── 360_day.json
│   ├── 365_day.json
│   ├── 366_day.json
│   ├── julian.json
│   ├── none.json
│   ├── proleptic_gregorian.json
│   └── standard.json
├── temporal-refinements/               # 3 TemporalRefinement CV terms
│   ├── adaptive.json
│   ├── dynamically_stretched.json
│   └── static.json
├── horizontal-grids/                   # 2 HorizontalGrid instances
│   ├── HGRID001.json
│   └── HGRID002.json
└── vertical-grids/                     # 5 VerticalGrid instances
    ├── VGRID001_hybrid_height.json
    ├── VGRID001_hybrid_sigma_pressure.json
    ├── VGRID002.json
    ├── VGRID003.json
    └── VGRID004.json
```

## File Counts

- **Model Components**: 8 files
- **Component Types (CV)**: 8 files
- **Calendars (CV)**: 7 files
- **Temporal Refinements (CV)**: 3 files
- **Horizontal Grids**: 2 files
- **Vertical Grids**: 5 files
- **Documentation**: 3 files (README.md, SUMMARY.md, COMPLETE_SUMMARY.md)

**Total**: 36 JSON files + 3 documentation files

## Data Descriptor Type Mapping

### 1. EMDModelComponent (8 files in components/)

Pydantic model: `EMDModelComponent(PlainTermDataDescriptor)`

Structure:
- component (string, hyphenated)
- name, family, description
- code_base, references
- embedded_in, coupled_with
- native_horizontal_grid, native_vertical_grid

Files follow the full nested structure with grids embedded.

### 2. ComponentType (8 files in component-types/)

Pydantic model: `ComponentType(PlainTermDataDescriptor)`

Structure:
```json
{
  "term": "atmospheric-chemistry",
  "description": "...",
  "ui_label": "Atmospheric Chemistry"
}
```

All component types are hyphenated (e.g., `atmospheric-chemistry`, `land-surface`, `ocean-biogeochemistry`, `sea-ice`).

### 3. Calendar (7 files in calendars/)

Pydantic model: `Calendar(PlainTermDataDescriptor)`

Structure:
```json
{
  "term": "standard",
  "description": "Mixed Gregorian/Julian calendar..."
}
```

Terms: standard, proleptic_gregorian, julian, 360_day, 365_day, 366_day, none

### 4. TemporalRefinement (3 files in temporal-refinements/)

Pydantic model: `TemporalRefinement(DataDescriptor)`

Structure:
```json
{
  "term": "static",
  "description": "Grid is held fixed..."
}
```

Terms: static, dynamically_stretched, adaptive

### 5. HorizontalGrid (2 files in horizontal-grids/)

Pydantic model: `HorizontalGrid(DataDescriptor)`

Structure:
```json
{
  "grid": "regular_latitude_longitude",
  "grid_mapping": "latitude_longitude",
  "region": "global",
  "temporal_refinement": "static",
  "arrangement": "arakawa_c",
  "resolution_x": 1.25,
  "resolution_y": 0.9,
  "horizontal_units": "degree",
  "n_cells": 55296,
  "mean_resolution_km": 139.5,
  "nominal_resolution": "100 km"
}
```

Instances:
- **HGRID001**: Regular lat-lon grid (1.25° x 0.9°, 55,296 cells)
- **HGRID002**: Tripolar ocean grid (105,704 cells, eORCA1L75)

### 6. VerticalGrid (5 files in vertical-grids/)

Pydantic model: `VerticalGrid(DataDescriptor)`

Structure:
```json
{
  "coordinate": "atmosphere_hybrid_height_coordinate",
  "n_z": 85,
  "bottom_layer_thickness": 100.0,
  "top_layer_thickness": 10.0,
  "top_of_model": 84763.34,
  "vertical_units": "m"
}
```

Instances:
- **VGRID001_hybrid_height**: Atmosphere (85 layers, hybrid height)
- **VGRID001_hybrid_sigma_pressure**: Atmosphere (91 layers, hybrid sigma-pressure)
- **VGRID002**: Land surface (14 soil layers)
- **VGRID003**: Ocean (75 layers, sigma-z coordinate)
- **VGRID004**: Sea ice (10 layers, height)

## Hyphenation Consistency

All component type references use **hyphens** consistently:
- ✓ `atmospheric-chemistry` (not `atmospheric_chemistry`)
- ✓ `land-surface` (not `land_surface`)
- ✓ `ocean-biogeochemistry` (not `ocean_biogeochemistry`)
- ✓ `sea-ice` (not `sea_ice`)

This applies across:
- Component type CV terms (`component-types/*.json`)
- Model component `component` field
- Model component `embedded_in` field
- Model component `coupled_with` field values

## Source Data

All files generated from:
- **Spreadsheet**: `recovered_EMD_Model_v0_993_CNRM.xlsx`
- **Date**: December 17, 2025
- **Model**: CNRM Earth System Model data

## Pydantic Model Compliance

All JSON files are structured to match their respective Pydantic models:

| JSON Directory | Pydantic Model | Base Class |
|----------------|----------------|------------|
| `components/` | EMDModelComponent | PlainTermDataDescriptor |
| `component-types/` | ComponentType | PlainTermDataDescriptor |
| `calendars/` | Calendar | PlainTermDataDescriptor |
| `temporal-refinements/` | TemporalRefinement | DataDescriptor |
| `horizontal-grids/` | HorizontalGrid | DataDescriptor |
| `vertical-grids/` | VerticalGrid | DataDescriptor |

## Usage Examples

### Load a Component Type

```python
from esgvoc.api.data_descriptors.data_descriptor import PlainTermDataDescriptor
import json

with open('data/component-types/atmospheric-chemistry.json') as f:
    data = json.load(f)
    # Use with ComponentType class
```

### Load a Horizontal Grid

```python
from esgvoc.api.data_descriptors.horizontal_grid import HorizontalGrid
import json

with open('data/horizontal-grids/HGRID001.json') as f:
    data = json.load(f)
    hgrid = HorizontalGrid(**data)
```

### Load a Model Component

```python
from esgvoc.api.data_descriptors.emd_model_component import EMDModelComponent
import json

with open('data/components/atmosphere_HadAM3.json') as f:
    data = json.load(f)
    component = EMDModelComponent(**data)
```

## Next Steps

1. **Validate** all JSON files against their Pydantic models
2. **Complete** truncated descriptions in component files
3. **Replace** placeholder DOIs with actual values
4. **Create** Model (top-level) JSON files if needed
5. **Create** Source JSON files if needed
6. **Add** more CV terms from the spreadsheet as needed

## Files Written to Filesystem

✅ All files written directly to your macOS filesystem at:
`/Users/daniel.ellis/WIPwork/Essential-Model-Documentation/data/`

No files were created in Docker containers - all files are on your local filesystem.
