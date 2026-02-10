# Model Component

![Generated](https://img.shields.io/badge/Generated-2026_01_30-708090) ![Type](https://img.shields.io/badge/Type-emd%3Amodel_component-blue) ![Pydantic](https://img.shields.io/badge/Pydantic-✓-green) ![Files](https://img.shields.io/badge/Files-12-lightgrey)

Model component Examples: "AOGCM", "AER", "BGC" These terms are intended to help with identifying required components for experiments or filtering models based on having common components. For example, an aerosol scheme or a circulation model or a biogeochemistry component. However, model component is only an approximate term, there is no precise definition of whether any given model has or does not have a given component.

---

## Quick Reference

| Property | Value |
|----------|-------|
| **Type URI** | `emd:model_component` |
| **Prefix** | `emd` |
| **Pydantic Model** | [`ModelComponent`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/model_component.py) |
| **JSON-LD** | [`emd:model_component`](https://emd.mipcvs.dev/model_component) |
| **Repository** | [![View Source](https://img.shields.io/badge/GitHub-View_Source-blue?logo=github)](https://github.com/wcrp-cmip/Essential-Model-Documentation//tree/src-data/model_component) |
| **Contribute** | [![Submit New / Edit Existing](https://img.shields.io/badge/Submit_New-Edit_Existing-grey?labelColor=orange&logo=github)](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |

---

## Schema

The JSON structure and validation for this vocabulary is defined using the [`ModelComponent`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/model_component.py) Pydantic model in [esgvoc](https://github.com/ESGF/esgf-vocab). This ensures data consistency and provides automatic validation of all entries. *Click field name for description.*

### Optional Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [description](#description) | `str` | - | - |

### Field Descriptions

<a id="description"></a>
#### Description

_No description available._

---

## Usage

<details open>
<summary><strong>Online</strong></summary>

| Resource | Link |
|----------|------|
| **Direct JSON** | [arpege-climat-version-6-3.json](https://github.com/wcrp-cmip/Essential-Model-Documentation//tree/src-data/model_component/arpege-climat-version-6-3.json) |
| **Interactive Viewer** | [Open Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Amodel_component/arpege-climat-version-6-3) |
| **Full URL** | [https://emd.mipcvs.dev/model_component/arpege-climat-version-6-3.json](https://emd.mipcvs.dev/model_component/arpege-climat-version-6-3.json) |

</details>

<details>
<summary><strong>cmipld</strong></summary>

```python
import cmipld

# Fetch and resolve a single record
data = cmipld.get("emd:model_component/arpege-climat-version-6-3")
print(data)
```

</details>

<details>
<summary><strong>esgvoc</strong></summary>

```python
from esgvoc.api import search

# Search for terms in this vocabulary
results = search.find("model_component", term="arpege-climat-version-6-3")
print(results)
```

</details>

<details>
<summary><strong>HTTP</strong></summary>

```python
import requests

url = "https://emd.mipcvs.dev/model_component/arpege-climat-version-6-3.json"
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
ldr compact https://emd.mipcvs.dev/model_component/arpege-climat-version-6-3.json
```

</details>
