# Vertical Computational Grid

One vertical grid. Thicknesses are in metres. A value left out must be explained in description.

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:vertical_computational_grid` |
| **Entries** | 87 |
| **Validation** | ✓ Validated |
| **Pydantic Model** | [`VerticalComputationalGrid`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/vertical_computational_grid.py) |
| **JSON-LD** | [`emd:vertical_computational_grid`](https://emd.wcrp-cmip.org/vertical_computational_grid) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/vertical_computational_grid) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-11-23 |

---

## Schema

The JSON structure and validation for this vocabulary is defined using the [`VerticalComputationalGrid`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/vertical_computational_grid.py) pydantic model, kept alongside the data in [`.github/EMD_tests`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests). This ensures data consistency and provides automatic validation of all entries. *Click field name for description.*

### Required Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [context](#context) | `Literal` | - | - |
| [validation_key](#validation_key) | `str` | - | - |

### Optional Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [description](#description) | `str | None` | - | - |
| [bottom_layer_thickness](#bottom_layer_thickness) | `Optional[Annotated]` | - | - |
| [n_z](#n_z) | `Optional[Annotated]` | - | - |
| [n_z_range](#n_z_range) | `list[Annotated[int, FieldInfo(annotation=NoneType, required=True, metadata=[Gt(gt=0)])]] | None` | min_length=2, max_length=2 | - |
| [top_layer_thickness](#top_layer_thickness) | `Optional[Annotated]` | - | - |
| [total_thickness](#total_thickness) | `Optional[Annotated]` | - | - |
| [ui_label](#ui_label) | `str | None` | - | - |
| [vertical_coordinate](#vertical_coordinate) | `Optional[Annotated]` | - | - |

### Field Descriptions

<a id="description"></a>
#### Description

_No description available._

<a id="bottom_layer_thickness"></a>
#### Bottom Layer Thickness

_No description available._

<a id="context"></a>
#### Context

_No description available._

<a id="n_z"></a>
#### N Z

_No description available._

<a id="n_z_range"></a>
#### N Z Range

_No description available._

<a id="top_layer_thickness"></a>
#### Top Layer Thickness

_No description available._

<a id="total_thickness"></a>
#### Total Thickness

_No description available._

<a id="ui_label"></a>
#### Ui Label

_No description available._

<a id="validation_key"></a>
#### Validation Key

_No description available._

<a id="vertical_coordinate"></a>
#### Vertical Coordinate

_No description available._

### Other Validations

<details markdown="1" id="other-n_z_or_n_z_range" open>
<summary><strong>n_z_or_n_z_range</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/vertical_computational_grid.py">[source]</a></summary>

A fixed level count or a range, not both (EMD Appendix B 4.2).

```python
def n_z_or_n_z_range(self):
        """A fixed level count or a range, not both (EMD Appendix B 4.2)."""
        not_both(self, "n_z", "n_z_range")
        return self
```

</details>

<details markdown="1" id="other-range_runs_low_to_high" open>
<summary><strong>range_runs_low_to_high</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/vertical_computational_grid.py">[source]</a></summary>

n_z_range is [minimum, maximum].

```python
def range_runs_low_to_high(self):
        """n_z_range is [minimum, maximum]."""
        if self.n_z_range and self.n_z_range[0] > self.n_z_range[1]:
            raise ValueError(f"n_z_range {self.n_z_range} must be [minimum, maximum]")
        return self
```

</details>

<details markdown="1" id="other-description_explains_what_is_left_out" open>
<summary><strong>description_explains_what_is_left_out</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/vertical_computational_grid.py">[source]</a></summary>

When a property is left out, description must be set to explain it (EMD Appendix B 4.2).

```python
def description_explains_what_is_left_out(self):
        """When a property is left out, description must be set to explain it (EMD Appendix B 4.2)."""
        if self.is_sentinel or self.description:
            return self
        left_out = [f for f in ("vertical_coordinate", "top_layer_thickness", "bottom_layer_thickness",
                                "total_thickness") if getattr(self, f) is None]
        if self.n_z is None and self.n_z_range is None:
            left_out.append("n_z")
        if left_out:
            raise ValueError(f"description is required to explain what is left out: {left_out}")
        return self
```

</details>

<details markdown="1" id="other-top_layer_within_column" open>
<summary><strong>top_layer_within_column</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/vertical_computational_grid.py">[source]</a></summary>

The top layer cannot be thicker than the whole column.

```python
def top_layer_within_column(self):
        """The top layer cannot be thicker than the whole column."""
        top, total = self.top_layer_thickness, self.total_thickness
        if top and total and top > total:
            raise ValueError(f"top_layer_thickness {top} m is more than total_thickness {total} m")
        return self

    # --------------------------------------------------------------- warnings: the record loads
```

</details>

<details markdown="1" id="other-bottom_layer_is_not_whole_column" open>
<summary><strong>bottom_layer_is_not_whole_column</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/vertical_computational_grid.py">[source]</a></summary>

A bottom layer as thick as the whole column is usually a copy-paste error.

```python
def bottom_layer_is_not_whole_column(self):
        """A bottom layer as thick as the whole column is usually a copy-paste error."""
        if self.bottom_layer_thickness is not None and self.bottom_layer_thickness == self.total_thickness:
            warn(f"{self.id}: bottom_layer_thickness equals total_thickness ({self.total_thickness:g} m)")
        return self
```

</details>

<details markdown="1" id="other-top_and_bottom_fit_in_column" open>
<summary><strong>top_and_bottom_fit_in_column</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/vertical_computational_grid.py">[source]</a></summary>

The top and bottom layers together fit inside the column.

```python
def top_and_bottom_fit_in_column(self):
        """The top and bottom layers together fit inside the column."""
        top, bottom, total = self.top_layer_thickness, self.bottom_layer_thickness, self.total_thickness
        if None not in (top, bottom, total) and top + bottom > total:
            warn(f"{self.id}: top {top:g} m + bottom {bottom:g} m is more than total_thickness {total:g} m")
        return self


model = VerticalComputationalGrid
```

</details>

---

## Usage

**Direct Access:**

- JSON: [`https://emd.wcrp-cmip.org/vertical_computational_grid/no-vertical.json`](https://emd.wcrp-cmip.org/vertical_computational_grid/no-vertical.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Avertical_computational_grid/no-vertical)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:vertical_computational_grid/no-vertical")
```
