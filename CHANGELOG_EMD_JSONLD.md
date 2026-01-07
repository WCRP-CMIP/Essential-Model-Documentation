# EMD JSON-LD Updates Summary

## Changes Made

### 1. Context Files Updated (`_context`)

All context files updated to use `https://emd.mipcvs.dev/` as base URL instead of relative `../` paths.

**Files updated:**
- `model/_context`
- `model-component/_context`
- `reference/_context`
- `horizontal-computational-grid/_context`
- `horizontal-subgrid/_context`
- `horizontal-grid-cells/_context`
- `vertical-computational-grid/_context`

### 2. Missing Properties Added

#### `n_z_range` (Section 4.2.1)
Added to `vertical-computational-grid/_context`:
```json
"n_z_range": {
  "@container": "@list",
  "@type": "http://www.w3.org/2001/XMLSchema#integer"
}
```

#### `truncation_number` (Section 4.1.3)
Added to `horizontal-grid-cells/_context`:
```json
"truncation_number": {
  "@type": "http://www.w3.org/2001/XMLSchema#integer"
}
```

### 3. Array Support Added

Updated contexts to support arrays where the spec allows multiple values:

- `cell_variable_type` in `horizontal-subgrid/_context`: Added `@container: @set`
- `region` in `horizontal-grid-cells/_context`: Added `@container: @set`

### 4. Naming Conventions Fixed

Component types now use **underscores** per EMD Spec Section 7.1:
- `atmospheric_chemistry` (not `atmospheric-chemistry`)
- `land_surface` (not `land-surface`)
- `ocean_biogeochemistry` (not `ocean-biogeochemistry`)
- `sea_ice` (not `sea-ice`)
- `land_ice` (not `land-ice`)

### 5. Example Files Merged

Content from `data/examples/` merged into main data directories:

| Example | Now Located At |
|---------|----------------|
| CLM4 Land Surface | `model-component/land_surface_CLM4.json` |
| BISICLES Land Ice | `model-component/land_ice_BISICLES-UKESM-ISMIP6-1.0.json` |
| CLM4 Grid | `HGRID004.json`, `HGRID004_subgrid_0.json`, `HGRID004_cells_0.json` |
| BISICLES Grid | `HGRID003.json`, `HGRID003_subgrid_0.json`, `HGRID003_cells_0.json` |
| CLM4 Vertical | `VGRID006.json` |
| BISICLES Vertical | `VGRID005.json` |
| CLM4 Reference | `REF013.json` |
| BISICLES Reference | `REF012.json` |

### 6. New Files Created

**References:**
- `reference/REF012.json` - Smith et al. 2021 (BISICLES)
- `reference/REF013.json` - Ke et al. 2012 (CLM4)

**Horizontal Grids:**
- `horizontal-computational-grid/HGRID003.json` - BISICLES Arakawa C
- `horizontal-computational-grid/HGRID004.json` - CLM4 Arakawa A
- `horizontal-subgrid/HGRID003_subgrid_0.json`
- `horizontal-subgrid/HGRID004_subgrid_0.json`
- `horizontal-grid-cells/HGRID003_cells_0.json` - Plane projection/polar stereographic
- `horizontal-grid-cells/HGRID004_cells_0.json` - Regular lat-lon

**Vertical Grids:**
- `vertical-computational-grid/VGRID005.json` - Land ice sigma
- `vertical-computational-grid/VGRID006.json` - Depth (CLM4)

### 7. Data Format Standardization

All JSON files now use consistent format:
- Arrays for multi-value properties (`cell_variable_type`, `region`, `coupled_with`, `references`)
- `null` instead of missing optional properties where appropriate
- Empty arrays `[]` instead of `null` for empty sets

## Files to Delete (Run cleanup.sh)

```bash
# Examples directory
data/examples/

# EX_ prefixed files
data/horizontal-computational-grid/EX_HGRID*.json
data/horizontal-grid-cells/EX_HGRID*.json
data/horizontal-subgrid/EX_HGRID*.json
data/vertical-computational-grid/EX_VGRID*.json
data/reference/EX_REF*.json

# Old hyphenated naming (duplicates)
data/model-component/atmospheric-chemistry_REPROBUS-C_v2_0.json
data/model-component/land-surface_SURFEX_v8_modeling_platform.json
data/model-component/ocean-biogeochemistry_PISCESv2-gas.json
data/model-component/sea-ice_GELATO.json
data/model-component/atmosphere_HadAM3.json
```

## Final Directory Structure

```
data/
├── model/
│   ├── _context
│   └── CNRM-ESM2-1e.json
├── model-component/
│   ├── _context
│   ├── aerosol_TACTIC.json
│   ├── atmosphere_Arpege-Climat_Version_6_3.json
│   ├── atmospheric_chemistry_REPROBUS-C_v2_0.json
│   ├── land_ice_BISICLES-UKESM-ISMIP6-1.0.json
│   ├── land_surface_CLM4.json
│   ├── land_surface_SURFEX_v8_modeling_platform.json
│   ├── ocean_biogeochemistry_PISCESv2-gas.json
│   ├── ocean_NEMO_v3_6.json
│   └── sea_ice_GELATO.json
├── reference/
│   ├── _context
│   └── REF001.json - REF013.json
├── horizontal-computational-grid/
│   ├── _context
│   └── HGRID001.json - HGRID004.json
├── horizontal-subgrid/
│   ├── _context
│   └── HGRID00*_subgrid_*.json
├── horizontal-grid-cells/
│   ├── _context
│   └── HGRID00*_cells_*.json
└── vertical-computational-grid/
    ├── _context
    └── VGRID001_0.json - VGRID006.json
```

## Compliance with EMD 1.0 Specification

✅ All required properties present
✅ Controlled vocabulary values match Section 7
✅ Naming conventions (underscores for components)
✅ Array support for multi-value properties
✅ `n_z_range` property supported
✅ `truncation_number` property supported
✅ Base URLs updated to emd.mipcvs.dev
✅ Example content integrated
