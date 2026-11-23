# Horizontal Computational Grid

One horizontal computational grid. Required: arrangement and horizontal_subgrids, except on no-horizontal.

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:horizontal_computational_grid` |
| **Entries** | 75 |
| **Validation** | ✓ Validated |
| **Pydantic Model** | [`HorizontalComputationalGrid`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_computational_grid.py) |
| **JSON-LD** | [`emd:horizontal_computational_grid`](https://emd.wcrp-cmip.org/horizontal_computational_grid) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/horizontal_computational_grid) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-11-23 |

---

## Schema

The JSON structure and validation for this vocabulary is defined using the [`HorizontalComputationalGrid`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_computational_grid.py) pydantic model, kept alongside the data in [`.github/EMD_tests`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests). This ensures data consistency and provides automatic validation of all entries. *Click field name for description.*

### Required Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [context](#context) | `Literal` | - | - |
| [validation_key](#validation_key) | `str` | - | - |

### Optional Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [description](#description) | `str | None` | - | - |
| [arrangement](#arrangement) | `Optional[Annotated]` | - | - |
| [horizontal_subgrids](#horizontal_subgrids) | `List[Annotated]` | - | - |
| [ui_label](#ui_label) | `str | None` | - | - |

### Field Descriptions

<a id="description"></a>
#### Description

_No description available._

<a id="arrangement"></a>
#### Arrangement

_No description available._

<a id="context"></a>
#### Context

_No description available._

<a id="horizontal_subgrids"></a>
#### Horizontal Subgrids

_No description available._

<a id="ui_label"></a>
#### Ui Label

_No description available._

<a id="validation_key"></a>
#### Validation Key

_No description available._

### Other Validations

<details markdown="1" id="other-arrangement_and_subgrids_given" open>
<summary><strong>arrangement_and_subgrids_given</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/horizontal_computational_grid.py">[source]</a></summary>

Both are required (EMD Appendix B 4.1.1). no-horizontal stands for "no grid" and has neither.

```python
def arrangement_and_subgrids_given(self):
        """Both are required (EMD Appendix B 4.1.1). no-horizontal stands for "no grid" and has neither."""
        if self.is_sentinel:
            return self
        if self.arrangement is None:
            raise ValueError("arrangement is required")
        if not self.horizontal_subgrids:
            raise ValueError("horizontal_subgrids is required")
        return self


model = HorizontalComputationalGrid
```

</details>

---

## Usage

**Direct Access:**

- JSON: [`https://emd.wcrp-cmip.org/horizontal_computational_grid/h100.json`](https://emd.wcrp-cmip.org/horizontal_computational_grid/h100.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Ahorizontal_computational_grid/h100)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:horizontal_computational_grid/h100")
```
