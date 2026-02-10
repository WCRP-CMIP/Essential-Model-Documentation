# Horizontal Subgrid

![Generated](https://img.shields.io/badge/Generated-2026_01_30-708090) ![Type](https://img.shields.io/badge/Type-emd%3Ahorizontal_subgrid-blue) ![Pydantic](https://img.shields.io/badge/Pydantic-✓-green) ![Files](https://img.shields.io/badge/Files-7-lightgrey)

Horizontal subgrid description (EMD v1.0 Section 4.1.2). A horizontal subgrid describes the grid cells at one of the stagger positions of a horizontal computational grid. Often the locations of mass-related and velocity-related variables differ, so more than one horizontal subgrid will be defined as part of a horizontal computational grid.

---

## Quick Reference

| Property | Value |
|----------|-------|
| **Type URI** | `emd:horizontal_subgrid` |
| **Prefix** | `emd` |
| **Pydantic Model** | [`HorizontalSubgrid`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/horizontal_subgrid.py) |
| **JSON-LD** | [`emd:horizontal_subgrid`](https://emd.mipcvs.dev/horizontal_subgrid) |
| **Repository** | [![View Source](https://img.shields.io/badge/GitHub-View_Source-blue?logo=github)](https://github.com/wcrp-cmip/Essential-Model-Documentation//tree/src-data/horizontal_subgrid) |
| **Contribute** | [![Submit New / Edit Existing](https://img.shields.io/badge/Submit_New-Edit_Existing-grey?labelColor=orange&logo=github)](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |

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
| [cell_variable_type](#cell_variable_type) | `List[str | CellVariableType]` | - | [`CellVariableType`](../cellvariabletype/), [`cell_variable_type`](../cell_variable_type/) |

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

<details open>
<summary><strong>Online</strong></summary>

| Resource | Link |
|----------|------|
| **Direct JSON** | [s100.json](https://github.com/wcrp-cmip/Essential-Model-Documentation//tree/src-data/horizontal_subgrid/s100.json) |
| **Interactive Viewer** | [Open Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Ahorizontal_subgrid/s100) |
| **Full URL** | [https://emd.mipcvs.dev/horizontal_subgrid/s100.json](https://emd.mipcvs.dev/horizontal_subgrid/s100.json) |

</details>

<details>
<summary><strong>cmipld</strong></summary>

```python
import cmipld

# Fetch and resolve a single record
data = cmipld.get("emd:horizontal_subgrid/s100")
print(data)
```

</details>

<details>
<summary><strong>esgvoc</strong></summary>

```python
from esgvoc.api import search

# Search for terms in this vocabulary
results = search.find("horizontal_subgrid", term="s100")
print(results)
```

</details>

<details>
<summary><strong>HTTP</strong></summary>

```python
import requests

url = "https://emd.mipcvs.dev/horizontal_subgrid/s100.json"
response = requests.get(url)
data = response.json()
print(data)
```

</details>

<details>
<summary><strong>CLI / Node / Web</strong></summary>

```bash
# Install
npm install -g jsonld-recursive

# Compact a JSON-LD document
ldr compact https://emd.mipcvs.dev/horizontal_subgrid/s100.json
```

</details>
