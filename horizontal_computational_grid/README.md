# Horizontal Computational Grid

Horizontal computational grid description (EMD v1.0 Section 4.1.1). A model component's horizontal computational grid is composed of one or more horizontal subgrids, on which different sets of variables are calculated. When the computational grid relies on more than one subgrid, it is referred to as a "staggered" grid. For most staggered grids, the velocity-related variables are calculated on a subgrid offset from the mass-related variables (e.g. pressure, temperature, water vapour and other mass constituents).

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:horizontal_computational_grid` |
| **Entries** | 4 |
| **Validation** | ✓ Validated |
| **Pydantic Model** | [`HorizontalComputationalGrid`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/horizontal_computational_grid.py) |
| **JSON-LD** | [`emd:horizontal_computational_grid`](https://emd.mipcvs.dev/horizontal_computational_grid) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/horizontal_computational_grid) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-02-22 |

---

## Schema

The JSON structure and validation for this vocabulary is defined using the [`HorizontalComputationalGrid`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/horizontal_computational_grid.py) Pydantic model in [esgvoc](https://github.com/ESGF/esgf-vocab). This ensures data consistency and provides automatic validation of all entries. *Click field name for description.*

### Required Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [arrangement](#arrangement) | `str | Arrangement` | - | [`arrangement`](../arrangement/) |
| [horizontal_subgrids](#horizontal_subgrids) | `List[HorizontalSubgrid]` | min_length=1 | [`HorizontalSubgrid`](../horizontalsubgrid/) |

### Optional Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [description](#description) | `str` | - | - |

### Field Descriptions

<a id="description"></a>
#### Description

_No description available._

<a id="arrangement"></a>
#### Arrangement

A characterisation of the grid staggering defining the relative positions of computed mass-related and velocity-related variables. Taken from 7.3 arrangement CV. Options: 'arakawa_a', 'arakawa_b', 'arakawa_c', 'arakawa_d', 'arakawa_e'. E.g. 'arakawa_c'

<a id="horizontal_subgrids"></a>
#### Horizontal Subgrids

All of the subgrids, of which there must be at least one, used to construct the horizontal computational grid. Each subgrid is associated with one or more variable types (mass-related, velocity-related, etc.), consistent with the arrangement property.

<details markdown="1" id="horizontal_subgrids-validate_at_least_one_subgrid" open>
<summary><strong>Validation:</strong> validate_at_least_one_subgrid <a href="https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/horizontal_computational_grid.py">[source]</a></summary>

Validate that there is at least one horizontal subgrid.

```python
def validate_at_least_one_subgrid(cls, v):
        """Validate that there is at least one horizontal subgrid."""
        if not v or len(v) < 1:
            raise ValueError("At least one horizontal subgrid must be provided")
        return v
```

</details>

---

## Usage

**Direct Access:**

- JSON: [`https://emd.mipcvs.dev/horizontal_computational_grid/h100.json`](https://emd.mipcvs.dev/horizontal_computational_grid/h100.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Ahorizontal_computational_grid/h100)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:horizontal_computational_grid/h100")
```

**Python (esgvoc):**

```python
from esgvoc.api import search
results = search.find("horizontal_computational_grid", term="h100")
```
