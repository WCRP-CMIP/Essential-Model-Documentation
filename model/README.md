# Model

Top-level model description (EMD v1.0 Section 2). The following properties provide a top-level description of the model as a whole.

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:model` |
| **Entries** | 1 |
| **Validation** | ✓ Validated |
| **Pydantic Model** | [`Model`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/model.py) |
| **JSON-LD** | [`emd:model`](https://emd.mipcvs.dev/model) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/model) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-02-22 |

---

## Schema

The JSON structure and validation for this vocabulary is defined using the [`Model`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/model.py) Pydantic model in [esgvoc](https://github.com/ESGF/esgf-vocab). This ensures data consistency and provides automatic validation of all entries. *Click field name for description.*

### Required Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [name](#name) | `str` | min_length=1 | - |
| [calendar](#calendar) | `List[str | Calendar]` | min_length=1 | [`calendar`](../calendar/) |
| [dynamic_components](#dynamic_components) | `List[str | ComponentType]` | min_length=1 | [`ComponentType`](../componenttype/), [`component`](../component/) |
| [family](#family) | `str` | min_length=1 | - |
| [model_components](#model_components) | `List[str | EMDModelComponent]` | - | - |
| [references](#references) | `List[str | Reference]` | min_length=1 | - |
| [release_year](#release_year) | `int` | min=1900, max=2100 | - |

### Optional Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [description](#description) | `str` | min_length=1 | - |
| [omitted_components](#omitted_components) | `List[str | ComponentType]` | - | [`ComponentType`](../componenttype/), [`component`](../component/) |
| [prescribed_components](#prescribed_components) | `List[str | ComponentType]` | - | [`ComponentType`](../componenttype/), [`component`](../component/) |

### Field Descriptions

<a id="description"></a>
#### Description

A scientific overview of the top-level model. The description should include a brief mention of all the components listed in the 7.1 component CV, whether dynamically simulated, prescribed, or omitted.

<details markdown="1" id="description-validate_non_empty_strings" open>
<summary><strong>Validation:</strong> validate_non_empty_strings <a href="https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/model.py">[source]</a></summary>

Validate that string fields are not empty.

```python
def validate_non_empty_strings(cls, v):
        """Validate that string fields are not empty."""
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Field cannot be empty")
            return v.strip()
        return v
```

</details>

<a id="name"></a>
#### Name

The name of the top-level model. For CMIP7, this name will be registered as the model's source_id.

<details markdown="1" id="name-validate_non_empty_strings" open>
<summary><strong>Validation:</strong> validate_non_empty_strings <a href="https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/model.py">[source]</a></summary>

Validate that string fields are not empty.

```python
def validate_non_empty_strings(cls, v):
        """Validate that string fields are not empty."""
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Field cannot be empty")
            return v.strip()
        return v
```

</details>

<a id="calendar"></a>
#### Calendar

The calendar, or calendars, that define which dates are permitted in the top-level model. Taken from 7.2 calendar CV.

<details markdown="1" id="calendar-validate_calendar_list" open>
<summary><strong>Validation:</strong> validate_calendar_list <a href="https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/model.py">[source]</a></summary>

Validate calendar list contains valid strings or Calendar objects.

```python
def validate_calendar_list(cls, v):
        """Validate calendar list contains valid strings or Calendar objects."""
        if not v:
            raise ValueError("At least one calendar must be specified")
        # Filter out empty strings, keep Calendar objects
        cleaned = []
        for item in v:
            if isinstance(item, str):
                if item.strip():
                    cleaned.append(item.strip())
            else:
                cleaned.append(item)
        if not cleaned:
            raise ValueError("Calendar list cannot be empty")
        return cleaned
```

</details>

<a id="dynamic_components"></a>
#### Dynamic Components

The model components that are dynamically simulated within the top-level model. Taken from 7.1 component CV.

<details markdown="1" id="dynamic_components-validate_component_lists" open>
<summary><strong>Validation:</strong> validate_component_lists <a href="https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/model.py">[source]</a></summary>

Validate component lists contain valid strings or ComponentType objects.

```python
def validate_component_lists(cls, v):
        """Validate component lists contain valid strings or ComponentType objects."""
        if v is None:
            return []
        # Filter out empty strings, keep ComponentType objects
        cleaned = []
        for item in v:
            if isinstance(item, str):
                if item.strip():
                    cleaned.append(item.strip())
            else:
                cleaned.append(item)
        return cleaned
```

</details>

<a id="family"></a>
#### Family

The top-level model's 'family' name. Use 'none' to indicate that there is no such family.

<details markdown="1" id="family-validate_non_empty_strings" open>
<summary><strong>Validation:</strong> validate_non_empty_strings <a href="https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/model.py">[source]</a></summary>

Validate that string fields are not empty.

```python
def validate_non_empty_strings(cls, v):
        """Validate that string fields are not empty."""
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Field cannot be empty")
            return v.strip()
        return v
```

</details>

<a id="model_components"></a>
#### Model Components

The model components that dynamically simulate processes within the model.

<details markdown="1" id="model_components-validate_same_dynamic_components" open>
<summary><strong>Validation:</strong> validate_same_dynamic_components <a href="https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/model.py">[source]</a></summary>

Validate that model_components has the same length as dynamic_components.

```python
def validate_same_dynamic_components(cls, v, info):
        """Validate that model_components has the same length as dynamic_components."""
        if "dynamic_components" in info.data:
            dynamic_components = info.data["dynamic_components"]
            if len(v) != len(dynamic_components):
                raise ValueError(
                    f"Number of model_components ({len(v)}) must equal number of dynamic_components({len(dynamic_components)})"
                )
        return v
```

</details>

<a id="omitted_components"></a>
#### Omitted Components

The components that are wholly omitted from the top-level model. Taken from 7.1 component CV.

<details markdown="1" id="omitted_components-validate_component_lists" open>
<summary><strong>Validation:</strong> validate_component_lists <a href="https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/model.py">[source]</a></summary>

Validate component lists contain valid strings or ComponentType objects.

```python
def validate_component_lists(cls, v):
        """Validate component lists contain valid strings or ComponentType objects."""
        if v is None:
            return []
        # Filter out empty strings, keep ComponentType objects
        cleaned = []
        for item in v:
            if isinstance(item, str):
                if item.strip():
                    cleaned.append(item.strip())
            else:
                cleaned.append(item)
        return cleaned
```

</details>

<a id="prescribed_components"></a>
#### Prescribed Components

The components that are represented in the top-level model with prescribed values. Taken from 7.1 component CV.

<details markdown="1" id="prescribed_components-validate_component_lists" open>
<summary><strong>Validation:</strong> validate_component_lists <a href="https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/model.py">[source]</a></summary>

Validate component lists contain valid strings or ComponentType objects.

```python
def validate_component_lists(cls, v):
        """Validate component lists contain valid strings or ComponentType objects."""
        if v is None:
            return []
        # Filter out empty strings, keep ComponentType objects
        cleaned = []
        for item in v:
            if isinstance(item, str):
                if item.strip():
                    cleaned.append(item.strip())
            else:
                cleaned.append(item)
        return cleaned
```

</details>

<a id="references"></a>
#### References

One or more references to published work for the top-level model as a whole.

<a id="release_year"></a>
#### Release Year

The year in which the top-level model being documented was released, or first used for published simulations.

---

## Usage

**Direct Access:**

- JSON: [`https://emd.mipcvs.dev/model/cnrm-esm2-1e.json`](https://emd.mipcvs.dev/model/cnrm-esm2-1e.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Amodel/cnrm-esm2-1e)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:model/cnrm-esm2-1e")
```

**Python (esgvoc):**

```python
from esgvoc.api import search
results = search.find("model", term="cnrm-esm2-1e")
```
