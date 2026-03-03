# Horizontal Subgrid

Horizontal subgrid description (EMD v1.0 Section 4.1.2). A horizontal subgrid describes the grid cells at one of the stagger positions of a horizontal computational grid. Often the locations of mass-related and velocity-related variables differ, so more than one horizontal subgrid will be defined as part of a horizontal computational grid.

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:horizontal_subgrid` |
| **Entries** | 7 |
| **Validation** | ✓ Validated |
| **Pydantic Model** | [`HorizontalSubgrid`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/horizontal_subgrid.py) |
| **JSON-LD** | [`emd:horizontal_subgrid`](https://emd.mipcvs.dev/horizontal_subgrid) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/horizontal_subgrid) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-02-22 |

---

## Schema

The JSON structure and validation for this vocabulary is defined using the [`HorizontalSubgrid`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/horizontal_subgrid.py) Pydantic model in [esgvoc](https://github.com/ESGF/esgf-vocab). This ensures data consistency and provides automatic validation of all entries. *Click field name for description.*

### Required Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [horizontal_grid_cells](#horizontal_grid_cells) | `HorizontalGridCells` | - | [`HorizontalGridCells`](../horizontalgridcells/) |

### Optional Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [description](#description) | `str` | - | - |
| [cell_variable_type](#cell_variable_type) | `List[str | CellVariableType]` | - | [`cell_variable_type`](../cell_variable_type/), [`CellVariableType`](../cellvariabletype/) |

### Field Descriptions

<a id="description"></a>
#### Description

_No description available._

<a id="cell_variable_type"></a>
#### Cell Variable Type

The types of physical variables that are carried at, or representative of conditions at, the cells described by this horizontal subgrid. Taken from 7.4 cell_variable_type CV. Options: 'mass', 'x_velocity', 'y_velocity', 'velocity'. E.g. ['mass'], ['x_velocity'], ['mass', 'x_velocity', 'y_velocity'], ['mass', 'velocity']. Can be an empty list in certain cases.

<a id="horizontal_grid_cells"></a>
#### Horizontal Grid Cells

A description of the characteristics and location of the grid cells of this subgrid.

---

## Usage

**Direct Access:**

- JSON: [`https://emd.mipcvs.dev/horizontal_subgrid/s100.json`](https://emd.mipcvs.dev/horizontal_subgrid/s100.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Ahorizontal_subgrid/s100)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:horizontal_subgrid/s100")
```

**Python (esgvoc):**

```python
from esgvoc.api import search
results = search.find("horizontal_subgrid", term="s100")
```
