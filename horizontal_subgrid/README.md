# Horizontal Subgrid

One subgrid. Required: cell_variable_type and horizontal_grid_cell (EMD Appendix B 4.1.2).

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:horizontal_subgrid` |
| **Entries** | 152 |
| **Validation** | ✓ Validated |
| **Pydantic Model** | [`HorizontalSubgrid`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_subgrid.py) |
| **JSON-LD** | [`emd:horizontal_subgrid`](https://emd.wcrp-cmip.org/horizontal_subgrid) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/horizontal_subgrid) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-11-23 |

---

## Schema

The JSON structure and validation for this vocabulary is defined using the [`HorizontalSubgrid`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_subgrid.py) pydantic model, kept alongside the data in [`.github/EMD_tests`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests). This ensures data consistency and provides automatic validation of all entries. *Click field name for description.*

### Required Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [cell_variable_type](#cell_variable_type) | `List[Annotated]` | min_length=1 | - |
| [context](#context) | `Literal` | - | - |
| [horizontal_grid_cell](#horizontal_grid_cell) | `str` | - | - |
| [validation_key](#validation_key) | `str` | - | - |

### Optional Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [description](#description) | `str | None` | - | - |
| [ui_label](#ui_label) | `str | None` | - | - |

### Field Descriptions

<a id="description"></a>
#### Description

_No description available._

<a id="cell_variable_type"></a>
#### Cell Variable Type

_No description available._

<a id="context"></a>
#### Context

_No description available._

<a id="horizontal_grid_cell"></a>
#### Horizontal Grid Cell

_No description available._

<a id="ui_label"></a>
#### Ui Label

_No description available._

<a id="validation_key"></a>
#### Validation Key

_No description available._

### Other Validations

<details markdown="1" id="other-accept_plural_spelling" open>
<summary><strong>accept_plural_spelling</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_subgrid.py">[source]</a></summary>

EMD 4.1.2 writes horizontal_grid_cells; this folder's _context writes horizontal_grid_cell. Read either.

```python
def accept_plural_spelling(cls, data):
        """EMD 4.1.2 writes horizontal_grid_cells; this folder's _context writes horizontal_grid_cell. Read either."""
        if isinstance(data, dict) and "horizontal_grid_cells" in data:
            data = dict(data)
            data.setdefault("horizontal_grid_cell", data.pop("horizontal_grid_cells"))
        return data
```

</details>

<details markdown="1" id="other-velocity_or_x_y_velocity" open>
<summary><strong>velocity_or_x_y_velocity</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_subgrid.py">[source]</a></summary>

velocity is not listed with x-velocity or y-velocity (EMD Appendix B 4.1.2).

```python
def velocity_or_x_y_velocity(self):
        """velocity is not listed with x-velocity or y-velocity (EMD Appendix B 4.1.2)."""
        types = set(self.cell_variable_type)
        if "velocity" in types and types & {"x-velocity", "y-velocity"}:
            raise ValueError("list velocity, or x-velocity and y-velocity, not both")
        return self

    # --------------------------------------------------------------- warnings: the record loads
```

</details>

<details markdown="1" id="other-axes_named_x_and_y" open>
<summary><strong>axes_named_x_and_y</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_subgrid.py">[source]</a></summary>

EMD 7.4 names the velocity axes x and y, not u and v.

```python
def axes_named_x_and_y(self):
        """EMD 7.4 names the velocity axes x and y, not u and v."""
        for name in {"u-velocity", "v-velocity"} & set(self.cell_variable_type):
            warn(f"{self.id}: use '{name.replace('u-', 'x-').replace('v-', 'y-')}' instead of '{name}'")
        return self
```

</details>

<details markdown="1" id="other-id_lists_the_variable_types" open>
<summary><strong>id_lists_the_variable_types</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_subgrid.py">[source]</a></summary>

The id is {cell}_{type}_{type}...; the types in it are the ones listed in cell_variable_type.

```python
def id_lists_the_variable_types(self):
        """The id is {cell}_{type}_{type}...; the types in it are the ones listed in cell_variable_type."""
        in_id = set(self.id.split("_")[1:])
        if in_id and in_id != set(self.cell_variable_type):
            warn(f"{self.id}: the id names {sorted(in_id)}, but cell_variable_type is {sorted(self.cell_variable_type)}")
        return self


model = HorizontalSubgrid
```

</details>

---

## Usage

**Direct Access:**

- JSON: [`https://emd.wcrp-cmip.org/horizontal_subgrid/g100_mass.json`](https://emd.wcrp-cmip.org/horizontal_subgrid/g100_mass.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Ahorizontal_subgrid/g100_mass)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:horizontal_subgrid/g100_mass")
```
