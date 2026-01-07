# Examples Directory

This directory contains the example model components and grids from Section 6 of the EMD 1.0 specification PDF.

## Purpose

These examples demonstrate proper EMD 1.0 structure and are provided for:
- Educational purposes
- Template reference
- Testing and validation

## Examples Included

### 1. Land Surface Component - CLM4
**From Section 6.1 of EMD 1.0 PDF**

- **Component**: `CLM4.json`
- **Family**: CLM (Community Land Model)
- **Description**: Demonstrates a land surface component embedded in atmosphere
- **Grid**: Regular latitude-longitude (Arakawa A)
- **Vertical**: Depth coordinate with variable layers

**Files**:
- `model-component/CLM4.json`
- `horizontal-computational-grid/EX_HGRID001.json`
- `horizontal-subgrid/EX_HGRID001_subgrid_0.json`
- `horizontal-grid-cells/EX_HGRID001_cells_0.json`
- `vertical-computational-grid/EX_VGRID001.json`
- `reference/EX_REF001.json`

### 2. Land Ice Component - BISICLES
**From Section 6.2 of EMD 1.0 PDF**

- **Component**: `BISICLES-UKESM-ISMIP6-1.0.json`
- **Family**: BISICLES
- **Description**: Demonstrates a coupled land ice component with adaptive mesh
- **Grid**: Plane projection with polar stereographic (Arakawa C)
- **Vertical**: Land ice sigma coordinate

**Files**:
- `model-component/BISICLES-UKESM-ISMIP6-1.0.json`
- `horizontal-computational-grid/EX_HGRID002.json`
- `horizontal-subgrid/EX_HGRID002_subgrid_0.json`
- `horizontal-grid-cells/EX_HGRID002_cells_0.json`
- `vertical-computational-grid/EX_VGRID002.json`
- `reference/EX_REF002.json`

## Key Features Demonstrated

### CLM4 Example Shows:
- Embedded component relationship (`embedded_in: "atmosphere"`)
- Regular lat-lon grid structure
- Arakawa A arrangement (mass variables at same location)
- Complex vertical structure description
- Multiple land units and columns

### BISICLES Example Shows:
- Coupled component relationship (`coupled_with: ["atmosphere", "land_surface", "ocean"]`)
- Adaptive mesh refinement (`temporal_refinement: "adaptive"`)
- Plane projection grid type
- Polar stereographic mapping
- Multiple regions (Greenland and Antarctica)
- Expandable vertical layers

## File Naming Convention

Model component files are named by their **component name only**, without the realm/component type prefix:
- ✅ `CLM4.json` (correct)
- ❌ `land_surface_CLM4.json` (old format - do not use)

The `component` field inside the JSON file specifies the component type (e.g., `"component": "land_surface"`).

## File Structure

```
examples/
├── README.md (this file)
├── model-component/
│   ├── CLM4.json
│   └── BISICLES-UKESM-ISMIP6-1.0.json
├── horizontal-computational-grid/
│   ├── EX_HGRID001.json
│   └── EX_HGRID002.json
├── horizontal-subgrid/
│   ├── EX_HGRID001_subgrid_0.json
│   └── EX_HGRID002_subgrid_0.json
├── horizontal-grid-cells/
│   ├── EX_HGRID001_cells_0.json
│   └── EX_HGRID002_cells_0.json
├── vertical-computational-grid/
│   ├── EX_VGRID001.json
│   └── EX_VGRID002.json
└── reference/
    ├── EX_REF001.json
    └── EX_REF002.json
```

## Usage

These examples can be used as:
1. **Templates** for creating new model components
2. **Reference** for understanding EMD 1.0 structure
3. **Test cases** for validation tools
4. **Educational material** for EMD training

## Notes

- All files follow EMD 1.0 specification exactly as presented in the PDF
- File naming uses `EX_` prefix for grid/reference files to distinguish examples from production data
- Model component files use the component name directly (no realm prefix)
- All @id values use lowercase with appropriate character handling
- All relative file references use the `examples/` path prefix
- These are illustrative examples and should not be considered definitive descriptions

## Source

These examples are taken directly from:
**Essential Model Documentation (EMD) Version 1.0**
Date: 2025-12-03
Section 6: Examples (pages 16-17)

## Validation

All example files have been validated against EMD 1.0 requirements:
- ✅ Proper @context, @type, @id structure
- ✅ All required fields present
- ✅ Controlled vocabulary values from Section 7
- ✅ Proper file references with relative paths
- ✅ Complete grid hierarchy (Computational → Subgrid → Cells)
- ✅ Component names without realm prefix in filenames
