# Component Config

One component configuration. Its id is {realm}_{model_component}_{horizontal grid}_{vertical grid}.

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:component_config` |
| **Entries** | 176 |
| **Validation** | ✓ Validated |
| **Pydantic Model** | [`ComponentConfig`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/component_config.py) |
| **JSON-LD** | [`emd:component_config`](https://emd.wcrp-cmip.org/component_config) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/component_config) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-11-23 |

---

## Schema

The JSON structure and validation for this vocabulary is defined using the [`ComponentConfig`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/component_config.py) pydantic model, kept alongside the data in [`.github/EMD_tests`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests). This ensures data consistency and provides automatic validation of all entries. *Click field name for description.*

### Required Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [context](#context) | `Literal` | - | - |
| [model_component](#model_component) | `str` | - | - |
| [validation_key](#validation_key) | `str` | - | - |

### Optional Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [description](#description) | `str | None` | - | - |
| [horizontal_computational_grid](#horizontal_computational_grid) | `Optional[Annotated]` | - | - |
| [ui_label](#ui_label) | `str | None` | - | - |
| [vertical_computational_grid](#vertical_computational_grid) | `Optional[Annotated]` | - | - |

### Field Descriptions

<a id="description"></a>
#### Description

_No description available._

<a id="context"></a>
#### Context

_No description available._

<a id="horizontal_computational_grid"></a>
#### Horizontal Computational Grid

_No description available._

<a id="model_component"></a>
#### Model Component

_No description available._

<a id="ui_label"></a>
#### Ui Label

_No description available._

<a id="validation_key"></a>
#### Validation Key

_No description available._

<a id="vertical_computational_grid"></a>
#### Vertical Computational Grid

_No description available._

### Other Validations

<details markdown="1" id="other-both_grids_named" open>
<summary><strong>both_grids_named</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/component_config.py">[source]</a></summary>

Both grids are named; a component without one uses no-horizontal or no-vertical.

```python
def both_grids_named(self):
        """Both grids are named; a component without one uses no-horizontal or no-vertical."""
        for field in ("horizontal_computational_grid", "vertical_computational_grid"):
            if getattr(self, field) is None:
                warn(f"{self.id}: {field} is empty; use the no-horizontal or no-vertical entry")
        return self
```

</details>

<details markdown="1" id="other-id_names_its_component_and_grids" open>
<summary><strong>id_names_its_component_and_grids</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/component_config.py">[source]</a></summary>

The id ends with _{model_component}_{horizontal grid}_{vertical grid}.

```python
def id_names_its_component_and_grids(self):
        """The id ends with _{model_component}_{horizontal grid}_{vertical grid}."""
        parts = [self.model_component, self.horizontal_computational_grid, self.vertical_computational_grid]
        if None not in parts and not self.id.endswith("_" + "_".join(parts)):
            warn(f"{self.id}: the id should end with '_{'_'.join(parts)}'")
        return self


model = ComponentConfig
```

</details>

---

## Usage

**Direct Access:**

- JSON: [`https://emd.wcrp-cmip.org/component_config/aerosol_am4-2-aerosol_h169_v172.json`](https://emd.wcrp-cmip.org/component_config/aerosol_am4-2-aerosol_h169_v172.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Acomponent_config/aerosol_am4-2-aerosol_h169_v172)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:component_config/aerosol_am4-2-aerosol_h169_v172")
```
