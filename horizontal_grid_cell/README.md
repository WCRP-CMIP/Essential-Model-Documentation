# Horizontal Grid Cell

One horizontal grid cell description. Required: grid_type and region (EMD Appendix B 4.1.3).

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:horizontal_grid_cell` |
| **Entries** | 194 |
| **Validation** | ✓ Validated |
| **Pydantic Model** | [`HorizontalGridCell`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_grid_cell.py) |
| **JSON-LD** | [`emd:horizontal_grid_cell`](https://emd.wcrp-cmip.org/horizontal_grid_cell) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/horizontal_grid_cell) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-11-23 |

---

## Schema

The JSON structure and validation for this vocabulary is defined using the [`HorizontalGridCell`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_grid_cell.py) pydantic model, kept alongside the data in [`.github/EMD_tests`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests). This ensures data consistency and provides automatic validation of all entries. *Click field name for description.*

### Required Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [context](#context) | `Literal` | - | - |
| [grid_type](#grid_type) | `str` | - | - |
| [region](#region) | `List[Annotated]` | min_length=1 | - |
| [validation_key](#validation_key) | `str` | - | - |

### Optional Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [description](#description) | `str | None` | - | - |
| [grid_mapping](#grid_mapping) | `Optional[Annotated]` | - | - |
| [n_cells](#n_cells) | `Optional[Annotated]` | - | - |
| [southernmost_latitude](#southernmost_latitude) | `Optional[Annotated]` | - | - |
| [temporal_refinement](#temporal_refinement) | `Optional[Annotated]` | - | - |
| [truncation_method](#truncation_method) | `Optional[Annotated]` | - | - |
| [truncation_number](#truncation_number) | `Optional[Annotated]` | - | - |
| [ui_label](#ui_label) | `str | None` | - | - |
| [units](#units) | `Optional[Annotated]` | - | - |
| [westernmost_longitude](#westernmost_longitude) | `Optional[Annotated]` | - | - |
| [x_resolution](#x_resolution) | `Optional[Annotated]` | - | - |
| [y_resolution](#y_resolution) | `Optional[Annotated]` | - | - |

### Field Descriptions

<a id="description"></a>
#### Description

_No description available._

<a id="context"></a>
#### Context

_No description available._

<a id="grid_mapping"></a>
#### Grid Mapping

_No description available._

<a id="grid_type"></a>
#### Grid Type

_No description available._

<a id="n_cells"></a>
#### N Cells

_No description available._

<a id="region"></a>
#### Region

_No description available._

<a id="southernmost_latitude"></a>
#### Southernmost Latitude

_No description available._

<a id="temporal_refinement"></a>
#### Temporal Refinement

_No description available._

<a id="truncation_method"></a>
#### Truncation Method

_No description available._

<a id="truncation_number"></a>
#### Truncation Number

_No description available._

<a id="ui_label"></a>
#### Ui Label

_No description available._

<a id="units"></a>
#### Units

_No description available._

<a id="validation_key"></a>
#### Validation Key

_No description available._

<a id="westernmost_longitude"></a>
#### Westernmost Longitude

_No description available._

<a id="x_resolution"></a>
#### X Resolution

_No description available._

<a id="y_resolution"></a>
#### Y Resolution

_No description available._

### Other Validations

<details markdown="1" id="other-units_given_with_resolution" open>
<summary><strong>units_given_with_resolution</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_grid_cell.py">[source]</a></summary>

A resolution needs its units (EMD 4.1.3).

```python
def units_given_with_resolution(self):
        """A resolution needs its units (EMD 4.1.3)."""
        if (self.x_resolution or self.y_resolution) and not self.units:
            raise ValueError("set units when x_resolution or y_resolution is set")
        return self
```

</details>

<details markdown="1" id="other-edges_set_together" open>
<summary><strong>edges_set_together</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_grid_cell.py">[source]</a></summary>

The southern and western edges are given together (EMD Appendix B 4.1.3).

```python
def edges_set_together(self):
        """The southern and western edges are given together (EMD Appendix B 4.1.3)."""
        both_or_neither(self, "southernmost_latitude", "westernmost_longitude")
        return self
```

</details>

<details markdown="1" id="other-truncation_set_together" open>
<summary><strong>truncation_set_together</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_grid_cell.py">[source]</a></summary>

The truncation method and number are given together (EMD Appendix B 4.1.3).

```python
def truncation_set_together(self):
        """The truncation method and number are given together (EMD Appendix B 4.1.3)."""
        both_or_neither(self, "truncation_method", "truncation_number")
        return self

    # --------------------------------------------------------------- warnings: the record loads
```

</details>

<details markdown="1" id="other-spectral_grid_has_truncation" open>
<summary><strong>spectral_grid_has_truncation</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_grid_cell.py">[source]</a></summary>

A spectral grid type should give its truncation number.

```python
def spectral_grid_has_truncation(self):
        """A spectral grid type should give its truncation number."""
        if self.grid_type in SPECTRAL and not self.truncation_number:
            warn(f"{self.id}: grid_type '{self.grid_type}' is spectral, but no truncation_number is given")
        return self
```

</details>

<details markdown="1" id="other-resolution_matches_truncation" open>
<summary><strong>resolution_matches_truncation</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_grid_cell.py">[source]</a></summary>

On a spectral grid that names its convention, the resolution is within 35 % of what N gives.

        linear: 180/N degrees. quadratic: 120/N degrees. cubic octahedral: 10000/N km.

```python
def resolution_matches_truncation(self):
        """On a spectral grid that names its convention, the resolution is within 35 % of what N gives.

        linear: 180/N degrees. quadratic: 120/N degrees. cubic octahedral: 10000/N km.
        """
        spacing, n = SPACING_FROM_TRUNCATION.get(self.grid_type), self.truncation_number
        if not (spacing and n):
            return self
        expected = spacing(n) * (KM_PER_DEGREE if self.units == "km" else 1)
        for field in ("x_resolution", "y_resolution"):
            value = getattr(self, field)
            if value is not None and abs(value - expected) / expected > 0.35:
                warn(f"{self.id}: {field} is {value} {self.units}, but truncation {n} on '{self.grid_type}' "
                     f"gives about {expected:.3g} {self.units}")
        return self
```

</details>

<details markdown="1" id="other-n_cells_given_unless_adaptive" open>
<summary><strong>n_cells_given_unless_adaptive</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_grid_cell.py">[source]</a></summary>

n_cells is given when the cell count is fixed, and left out when it is adaptive (EMD 4.1.3).

```python
def n_cells_given_unless_adaptive(self):
        """n_cells is given when the cell count is fixed, and left out when it is adaptive (EMD 4.1.3)."""
        if self.n_cells is None and not self.adaptive:
            warn(f"{self.id}: n_cells is not given")
        if self.n_cells is not None and self.adaptive:
            warn(f"{self.id}: n_cells is given on an adaptive grid, where the count changes")
        return self
```

</details>

<details markdown="1" id="other-n_cells_matches_resolution" open>
<summary><strong>n_cells_matches_resolution</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_grid_cell.py">[source]</a></summary>

On a regular grid, n_cells is within 10 times of (360/dx) * (180/dy) * area of the regions.

```python
def n_cells_matches_resolution(self):
        """On a regular grid, n_cells is within 10 times of (360/dx) * (180/dy) * area of the regions."""
        if not (self.grid_type in REGULAR and self.n_cells and self.x_resolution and self.y_resolution):
            return self
        scale = KM_PER_DEGREE if self.units == "km" else 1
        area = min(1, sum(AREA.get(r, 1) for r in self.region))
        estimate = (360 * scale / self.x_resolution) * (180 * scale / self.y_resolution) * area
        if abs(math.log10(self.n_cells / estimate)) >= 1:
            warn(f"{self.id}: n_cells is {self.n_cells}, but the resolution and region give about {estimate:,.0f}")
        return self
```

</details>

<details markdown="1" id="other-southern_edge_on_pole_or_half_cell" open>
<summary><strong>southern_edge_on_pole_or_half_cell</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_grid_cell.py">[source]</a></summary>

On a regular latitude-longitude grid near the pole, the edge is -90 or -90 + dy/2.

```python
def southern_edge_on_pole_or_half_cell(self):
        """On a regular latitude-longitude grid near the pole, the edge is -90 or -90 + dy/2."""
        south, dy = self.southernmost_latitude, self.y_resolution
        if self.grid_type != "regular-latitude-longitude" or south is None or not dy or south > -80:
            return self
        if min(abs(south + 90), abs(south + 90 - dy / 2)) > max(dy / 4, 0.05):
            warn(f"{self.id}: southernmost_latitude {south} is neither -90 nor -90 + dy/2 = {-90 + dy / 2:g}")
        return self
```

</details>

<details markdown="1" id="other-grid_mapping_suits_grid_type" open>
<summary><strong>grid_mapping_suits_grid_type</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_grid_cell.py">[source]</a></summary>

A plane-projection grid uses a projected mapping; a regular latitude-longitude grid does not (EMD 7.6, 7.7).

```python
def grid_mapping_suits_grid_type(self):
        """A plane-projection grid uses a projected mapping; a regular latitude-longitude grid does not (EMD 7.6, 7.7)."""
        projected = self.grid_mapping in PROJECTED
        if (self.grid_type == "plane-projection" and not projected) or \
                (self.grid_type == "regular-latitude-longitude" and projected):
            warn(f"{self.id}: grid_mapping '{self.grid_mapping}' does not suit grid_type '{self.grid_type}'")
        return self


model = HorizontalGridCell
```

</details>

---

## Usage

**Direct Access:**

- JSON: [`https://emd.wcrp-cmip.org/horizontal_grid_cell/g010.json`](https://emd.wcrp-cmip.org/horizontal_grid_cell/g010.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Ahorizontal_grid_cell/g010)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:horizontal_grid_cell/g010")
```
