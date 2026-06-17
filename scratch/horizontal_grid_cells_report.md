# 📋 Submission Report: `g107-submitted`

**Kind:** `horizontal_grid_cell`  
**Type:** `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells, wcrp:horizontal_grid_cells, esgvoc:HorizontalGridCells`  
**Folder:** `emd:horizontal_grid_cells`  
**Generated:** 2026-02-28 15:04 UTC


---

## 🔗 Link Similarity Analysis

**Item:** `g107`  
**External links found:** 8  
**Folder items compared:** 7

### Links in submitted item

- `esgvoc:HorizontalGridCells`
- `https://constants.mipcvs.dev/grid_mapping/latitude-longitude`
- `https://constants.mipcvs.dev/grid_type/regular-latitude-longitude`
- `https://constants.mipcvs.dev/region/global`
- `https://constants.mipcvs.dev/temporal_refinement/static`
- `https://constants.mipcvs.dev/units/degree`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells`
- `wcrp:horizontal_grid_cells`

### Link fields

- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/grid_mapping`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/grid_type`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/region`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/temporal_refinement`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/units`

### Similarity to existing folder items

| Folder item | Link overlap |
|-------------|-------------|
| `g100` | 77.8% ███████░░░ |
| `g104` | 77.8% ███████░░░ |
| `g101` | 54.5% █████░░░░░ |
| `g102` | 50.0% █████░░░░░ |
| `g106` | 50.0% █████░░░░░ |
| `g105` | 50.0% █████░░░░░ |
| `g103` | 14.3% █░░░░░░░░░ |

---

## 🧩 Pydantic Model Validation

### Model-declared fields (pre-validated)

These fields are defined in the esgvoc schema and are automatically validated when present.

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `description` | optional | `Optional` | A description of the grid. A description is only required if there is information that is not covered by any of the other properties. Omit when not required. |
| `drs_name` | ✅ required | `str` |  |
| `grid_mapping` | optional | `Union` | The name of the coordinate reference system of the horizontal coordinates. Taken from 7.7 grid_mapping CV. E.g. 'latitude_longitude', 'lambert_conformal_conic'. Can be None or empty for certain grid types (e.g., tripolar grids). |
| `grid_type` | ✅ required | `str | esgvoc.api.data_descriptors.EMD_models.grid_type.GridType` | The horizontal grid type, i.e. the method of distributing grid cells over the region. Taken from 7.6 grid_type CV. E.g. 'regular_latitude_longitude', 'tripolar' |
| `horizontal_units` | optional | `Optional` | 
The physical units of the x_resolution and y_resolution property values.

If x_resolution and y_resolution are None, set this to None.
 |
| `id` | ✅ required | `str` |  |
| `n_cells` | optional | `Optional` | 
The total number of cells in the horizontal grid.

If the total number of grid cells is not constant, set to None.
 |
| `region` | ✅ required | `esgvoc.api.data_descriptors.region.Region | str` | The geographical region, or regions, over which the component is simulated. A region is a contiguous part of the Earth's surface, and may include areas for which no calculations are made (such as ocean areas for a land surface component). Taken from 7.5 region CV. E.g. 'global', 'antarctica', 'greenland', 'limited_area' |
| `resolution_range_km` | optional | `Optional` | 
The minimum and maximum resolution (in km) of cells of the horizontal grid.

Should be calculated according to the algorithm implemented by
https://github.com/PCMDI/nominal_resolution/blob/master/lib/api.py
You need to take the min and max of the array that is returned
when using the returnMaxDistance of the mean_resolution function.
 |
| `southernmost_latitude` | optional | `Optional` | 
The southernmost grid cell latitude, in degrees north.

Cells for which no calculations are made are included.
The southernmost latitude may be shared by multiple cells.

If the southernmost latitude is not known (e.g. the grid is adaptive), use None.
 |
| `spatial_refinement` | optional | `Optional` | The grid spatial refinement, indicating how the distribution of grid cells varies with space. NEW in EMD v1.0. Omit when not applicable. |
| `temporal_refinement` | ✅ required | `str | esgvoc.api.data_descriptors.EMD_models.temporal_refinement.TemporalRefinement` | The grid temporal refinement, indicating how the distribution of grid cells varies with time. Taken from 7.8 temporal_refinement CV. E.g. 'static' |
| `truncation_method` | optional | `Union` | The method for truncating the spherical harmonic representation of a spectral model when reporting on this grid. If the grid is not used for reporting spherical harmonic representations, set to None. |
| `truncation_number` | optional | `Optional` | The zonal (east-west) wave number at which a spectral model is truncated when reporting on this grid. If the grid is not used for reporting spectral models, set to None. |
| `type` | ✅ required | `str` |  |
| `westernmost_longitude` | optional | `Optional` | 
The westernmost grid cell longitude, in degrees east, of the southernmost grid cell(s).

Cells for which no calculations are made are included.
The westernmost longitude is the smallest longitude value of the cells
that share the latitude given by the southernmost_latitude.

If the westernmost longitude is not known (e.g. the grid is adaptive), use None.
 |
| `x_resolution` | optional | `Optional` | 
The size of grid cells in the X direction.

Cells for which no calculations are made are included (such as ocean areas
for a land surface component).

The X direction for a grid defined by spherical polar coordinates is longitude.

The value's physical units are given by the horizontal_units property.

Report only when cell sizes are identical or else reasonably uniform (in their given units).
When cells sizes in the X direction are not identical, a representative value should be
provided and this fact noted in the description property.
If the cell sizes vary by more than 25%, set this to None.
 |
| `y_resolution` | optional | `Optional` | 
The size of grid cells in the Y direction.

Cells for which no calculations are made are included (such as ocean areas
for a land surface component).

The Y direction for a grid defined by spherical polar coordinates is latitude.

The value's physical units are given by the horizontal_units property.

Report only when cell sizes are identical or else reasonably uniform (in their given units).
When cells sizes in the Y direction are not identical, a representative value should be
provided and this fact noted in the description property.
If the cell sizes vary by more than 25%, set this to None.
 |

### ❌ Validation Errors

| **Field** | **Error Type** | **Input Value** | **Input Type** | **Message** |
| --- | --- | --- | --- | --- |
| drs_name | string_type | `None` | None | Input should be a valid string |
| region | missing | `None` | None | Field required |
| grid_type | missing | `None` | None | Field required |
| temporal_refinement | missing | `None` | None | Field required |


### Fields that failed validation

- ❌ `drs_name`

### Fields not covered by the Pydantic model

These will be assessed separately via text-similarity analysis.

- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/description`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/grid_mapping`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/grid_type`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/n_cells`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/region`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/southernmost_latitude`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/temporal_refinement`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/ui_label`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/units`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/validation_key`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/westernmost_longitude`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/x_resolution`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/y_resolution`


---

## 📊 Text-Field Similarity Analysis

**Item:** `g107-submitted`  
**Method:** embedding (semantic)  
**Text fields compared:** 8

### Text fields included in comparison

| Field | Value |
|-------|-------|
| `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/description` | {'@value': 'Global regular latitude-longitude grid with 0.5°… |
| `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/n_cells` | {'@value': 259200} |
| `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/southernmost_latitude` | {'@value': -89.75} |
| `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/ui_label` | {'@value': ''} |
| `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/validation_key` | {'@value': 'g107'} |
| `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/westernmost_longitude` | {'@value': 0.0} |
| `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/x_resolution` | {'@value': 0.5} |
| `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/y_resolution` | {'@value': 0.5} |

### Excluded fields

_These fields were excluded from similarity comparison (link-fields, pydantic-validated fields, or custom exclusions):_

- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/grid_mapping`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/grid_type`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/region`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/temporal_refinement`
- `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/units`

### Similarity to existing folder items

| Folder item | Similarity | Bar |
|-------------|-----------|-----|
| `g100` | 97.1% | █████████░ |
| `g104` | 89.9% | ████████░░ |
| `g102` | 54.7% | █████░░░░░ |
| `g101` | 49.6% | ████░░░░░░ |
| `g105` | 46.3% | ████░░░░░░ |
| `g106` | 44.6% | ████░░░░░░ |
| `g103` | 43.3% | ████░░░░░░ |


---

## ✏️ Reviewer Checklist

_Fields validated by Pydantic are pre-ticked.  Please verify all other fields manually._

### Fields for manual review

- [ ] `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/description`: `{'@value': 'Global regular latitude-longitude grid with 0.5° x 0.5° resolution a…`
- [ ] `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/grid_mapping`: `{'@id': 'https://constants.mipcvs.dev/grid_mapping/latitude-longitude'}`
- [ ] `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/grid_type`: `{'@id': 'https://constants.mipcvs.dev/grid_type/regular-latitude-longitude'}`
- [ ] `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/n_cells`: `{'@value': 259200}`
- [ ] `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/region`: `{'@id': 'https://constants.mipcvs.dev/region/global'}`
- [ ] `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/southernmost_latitude`: `{'@value': -89.75}`
- [ ] `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/temporal_refinement`: `{'@id': 'https://constants.mipcvs.dev/temporal_refinement/static'}`
- [ ] `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/ui_label`: `{'@value': ''}`
- [ ] `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/units`: `{'@id': 'https://constants.mipcvs.dev/units/degree'}`
- [ ] `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/validation_key`: `{'@value': 'g107'}`
- [ ] `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/westernmost_longitude`: `{'@value': 0.0}`
- [ ] `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/x_resolution`: `{'@value': 0.5}`
- [ ] `https://emd.mipcvs.dev/docs/contents/HorizontalGridCells/y_resolution`: `{'@value': 0.5}`


---

_Report generated automatically by [cmipld](https://github.com/WCRP-CMIP/CMIP-LD) — `cmipld.utils.similarity.report_builder`_
