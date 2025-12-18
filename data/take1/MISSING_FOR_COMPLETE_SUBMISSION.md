# Missing Components for Complete EMD Submission

## What You Have ✅

### 1. Model Components (8 files) ✅
- All 8 dynamic components documented
- Each has name, family, description, code_base, references
- Grids (horizontal and vertical) properly linked
- Embedded/coupled relationships defined

### 2. Component Type CVs (8 files) ✅
- All component types from CV defined
- With descriptions and UI labels
- Properly hyphenated

### 3. Supporting CVs ✅
- Calendars (7 files)
- Temporal Refinements (3 files)
- Horizontal Grids (2 instances: HGRID001, HGRID002)
- Vertical Grids (5 instances: VGRID001-004)

## What You're Missing ❌

### 1. **Top-Level Model** ❌ (CRITICAL)

According to the `Model` Pydantic class and the spreadsheet "Top-Level Model" sheet, you need:

**File to create**: `data/models/CNRM-ESM2-1e.json`

**Required fields from spreadsheet**:
```json
{
  "term": "CNRM-ESM2-1e",
  "name": "CNRM-ESM2-1e",
  "family": "CNRM-CM, CNRM-ESM",
  "dynamic_components": [
    "aerosol",
    "atmosphere",
    "atmospheric-chemistry",
    "land-surface",
    "ocean",
    "ocean-biogeochemistry",
    "sea-ice"
  ],
  "prescribed_components": [],
  "omitted_components": ["land-ice"],
  "description": "CNRM-ESM2-1e is the CNRM Earth System model version 2 designed for CMIP6...",
  "calendar": ["standard"],
  "release_year": 2018,
  "references": [
    {
      "citation": "...",
      "doi": "https://doi.org/..."
    }
  ],
  "model_components": [
    // References to the 8 component JSON files or inline component data
  ]
}
```

**Note**: `dynamic_components` should use **hyphenated** names to match your component-types.

### 2. **Top-Level Model References** ❌

The Top-Level Model needs its own set of references that describe the model as a whole (not component-specific).

From the References sheet, you need to identify which references apply to the overall model vs. individual components.

### 3. **Additional CV Terms** ⚠️ (Optional but recommended)

You may want to create JSON files for other CV terms used in your data:

#### Grid-related CVs:
- **Grid Types** (from CV_Grid sheet): 
  - regular_latitude_longitude
  - linear_spectral_gaussian
  - tripolar
  - (and all others from the CV)

- **Grid Mappings** (from CV_GridMapping sheet):
  - latitude_longitude
  - polar_stereographic
  - etc.

- **Regions** (from CV_Region sheet):
  - global
  - antarctica
  - greenland
  - etc.

- **Arrangements** (from CV_Arrangement sheet):
  - arakawa_a, arakawa_b, arakawa_c, etc.

- **Cell Variable Types** (from CV_CellVariableType sheet):
  - mass
  - velocity_x, velocity_y
  - velocity

- **Horizontal Units** (from CV_HorizontalUnits sheet):
  - km
  - degree

- **Truncation Methods** (from CV_TruncationMethod sheet):
  - triangular
  - rhomboidal

- **Vertical Coordinates** (from CV_Coordinate sheet):
  - atmosphere_hybrid_height_coordinate
  - atmosphere_hybrid_sigma_pressure_coordinate
  - ocean_sigma_z_coordinate
  - depth
  - height
  - (and all others)

- **Vertical Units** (from CV_VerticalUnits sheet):
  - m
  - Pa
  - hPa

### 4. **Source** ⚠️ (If needed for CMIP registration)

According to the `Source` Pydantic class, if you're registering this for CMIP7, you may need:

**File to create**: `data/sources/CNRM-ESM2-1e.json`

```json
{
  "term": "CNRM-ESM2-1e",
  "label": "CNRM-ESM2-1e",
  "label_extended": "Centre National de Recherches Météorologiques Earth System Model 2.1e",
  "activity_participation": ["CMIP", "ScenarioMIP", ...],
  "cohort": ["2024"],
  "organisation_id": ["CNRM"],
  "license": {
    "name": "CC BY 4.0",
    "url": "https://creativecommons.org/licenses/by/4.0/"
  },
  "model_component": {
    // Reference to model or inline data
  },
  "release_year": 2018
}
```

## Priority Actions

### CRITICAL - Must Have:

1. **Create Top-Level Model JSON** ✅ `data/models/CNRM-ESM2-1e.json`
   - Use data from "Top-Level Model" sheet
   - Hyphenate all component names
   - Link to or embed the 8 component files

2. **Add Top-Level Model References**
   - Extract from References sheet which ones apply to the whole model

### IMPORTANT - Should Have:

3. **Complete Component Descriptions**
   - Replace "..." placeholders in component descriptions
   - Add full scientific text

4. **Fix Placeholder DOIs**
   - Replace `https://doi.org/10.5281/zenodo.xxx` with real DOIs or "private"

### RECOMMENDED - Nice to Have:

5. **Create Complete CV Term Libraries**
   - All grid type CVs
   - All coordinate CVs
   - All unit CVs
   - Makes the data more reusable and complete

6. **Create Source JSON** (if for CMIP7 registration)
   - Links the model to CMIP activities and organizations

## Validation Checklist

According to the spreadsheet's validation section, you need:

- ✅ Required Top-Level Fields
- ✅ Dynamic Components Documented
- ✅ Component Grids Defined
- ✅ Horizontal Grids Exist
- ✅ Vertical Grids Exist
- ✅ References Provided
- ✅ Component References Linked
- ✅ Grid Resolution Data
- ⚠️ Embedded/Coupled Exclusivity (manual check needed)
- ✅ Grid Units Consistency

## EMD Submission Requirements (from PDF)

According to the EMD PDF specification, a complete submission includes:

### Section 2: Top-Level Model (MISSING)
- [x] name
- [x] family
- [x] dynamic_components
- [x] prescribed_components
- [x] omitted_components
- [x] description
- [x] calendar
- [x] release_year
- [x] references

### Section 3: Model Components (HAVE)
- [x] 8 components documented
- [x] Each with grids
- [x] Each with references

### Section 4: Grids (HAVE)
- [x] Horizontal grids
- [x] Vertical grids

### Section 5: References (HAVE)
- [x] Component references
- [ ] Top-level model references (need to verify which ones)

## Summary

**You have**: 
- ✅ All 8 model components fully documented
- ✅ All component-type CV terms
- ✅ Supporting CVs (calendars, temporal refinements)
- ✅ Grid instances (horizontal and vertical)

**You're missing**:
- ❌ **Top-Level Model JSON** (CRITICAL - this is the main entry point)
- ❌ Verification that top-level model references are identified
- ⚠️ Complete CV term libraries (recommended but not strictly required)
- ⚠️ Source JSON (if needed for CMIP7 registration)

**Next step**: Create the Top-Level Model JSON file, which ties everything together!
