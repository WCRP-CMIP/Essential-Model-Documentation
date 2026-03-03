# Vertical Computational Grid

Vertical computational grid description (EMD v1.0 Section 4.2). The model component's vertical computational grid is described by a subset of the following properties.

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:vertical_computational_grid` |
| **Entries** | 7 |
| **Validation** | ✓ Validated |
| **Pydantic Model** | [`VerticalComputationalGrid`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/vertical_computational_grid.py) |
| **JSON-LD** | [`emd:vertical_computational_grid`](https://emd.mipcvs.dev/vertical_computational_grid) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/vertical_computational_grid) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-02-22 |

---

## Schema

The JSON structure and validation for this vocabulary is defined using the [`VerticalComputationalGrid`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/vertical_computational_grid.py) Pydantic model in [esgvoc](https://github.com/ESGF/esgf-vocab). This ensures data consistency and provides automatic validation of all entries. *Click field name for description.*

### Required Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [vertical_coordinate](#vertical_coordinate) | `str | Coordinate` | - | [`vertical_coordinate`](../vertical_coordinate/) |

### Optional Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [description](#description) | `Optional[str]` | - | - |
| [bottom_layer_thickness](#bottom_layer_thickness) | `Optional[float]` | - | - |
| [n_z](#n_z) | `Optional[int]` | min=1 | - |
| [n_z_range](#n_z_range) | `Optional[List[int]]` | min_length=2, max_length=2 | - |
| [top_layer_thickness](#top_layer_thickness) | `Optional[float]` | - | - |
| [top_of_model](#top_of_model) | `Optional[float]` | - | - |

### Field Descriptions

<a id="description"></a>
#### Description

A description of the vertical grid. A description is only required if there is information that is not covered by any of the other properties. Omit when not required.

<a id="bottom_layer_thickness"></a>
#### Bottom Layer Thickness

The thickness of the bottom model layer (i.e. the layer closest to the centre of the Earth). The value should be reported as a dimensional (as opposed to parametric) quantity. All measurements are in metres (EMD v1.0).

<a id="n_z"></a>
#### N Z

The number of layers (i.e. grid cells) in the Z direction. Omit when not applicable or not constant. If the number of layers varies in time or across the horizontal grid, then the n_z_range property may be used instead.

<details markdown="1" id="n_z-validate_n_z_exclusivity" open>
<summary><strong>Validation:</strong> validate_n_z_exclusivity <a href="https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/vertical_computational_grid.py">[source]</a></summary>

Validate that n_z and n_z_range are mutually exclusive.

```python
def validate_n_z_exclusivity(cls, v, info):
        """Validate that n_z and n_z_range are mutually exclusive."""
        if v is not None and info.data.get("n_z_range") is not None:
            raise ValueError("n_z and n_z_range cannot both be set")
        return v
```

</details>

<a id="n_z_range"></a>
#### N Z Range

The minimum and maximum number of layers for vertical grids with a time- or space-varying number of layers. Omit if the n_z property has been set.

<details markdown="1" id="n_z_range-validate_n_z_range" open>
<summary><strong>Validation:</strong> validate_n_z_range <a href="https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/vertical_computational_grid.py">[source]</a></summary>

Validate that n_z_range has exactly 2 values and min <= max.

```python
def validate_n_z_range(cls, v):
        """Validate that n_z_range has exactly 2 values and min <= max."""
        if v is not None:
            if len(v) != 2:
                raise ValueError("n_z_range must contain exactly 2 values [min, max]")
            if v[0] > v[1]:
                raise ValueError("n_z_range: minimum must be <= maximum")
            if any(val < 1 for val in v):
                raise ValueError("n_z_range values must be >= 1")
        return v
```

</details>

<a id="top_layer_thickness"></a>
#### Top Layer Thickness

The thickness of the top model layer (i.e. the layer furthest away from the centre of the Earth). The value should be reported as a dimensional (as opposed to parametric) quantity. All measurements are in metres (EMD v1.0).

<a id="top_of_model"></a>
#### Top Of Model

The upper boundary of the top model layer (i.e. the upper boundary of the layer that is furthest away from the centre of the Earth). The value should be relative to the lower boundary of the bottom layer of the model, or an appropriate datum (such as mean sea level). All measurements are in metres (EMD v1.0).

<a id="vertical_coordinate"></a>
#### Vertical Coordinate

The coordinate type of the vertical grid. Taken from 7.11 vertical_coordinate CV. If there is no vertical grid, then the value 'none' must be selected.

<details markdown="1" id="vertical_coordinate-validate_vertical_coordinate" open>
<summary><strong>Validation:</strong> validate_vertical_coordinate <a href="https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/vertical_computational_grid.py">[source]</a></summary>

Validate that vertical_coordinate is not empty if it's a string.

```python
def validate_vertical_coordinate(cls, v):
        """Validate that vertical_coordinate is not empty if it's a string."""
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Vertical coordinate cannot be empty")
            return v.strip()
        return v
```

</details>

---

## Usage

**Direct Access:**

- JSON: [`https://emd.mipcvs.dev/vertical_computational_grid/v100.json`](https://emd.mipcvs.dev/vertical_computational_grid/v100.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Avertical_computational_grid/v100)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:vertical_computational_grid/v100")
```

**Python (esgvoc):**

```python
from esgvoc.api import search
results = search.find("vertical_computational_grid", term="v100")
```
