# Model Component

Model component Examples: "AOGCM", "AER", "BGC" These terms are intended to help with identifying required components for experiments or filtering models based on having common components. For example, an aerosol scheme or a circulation model or a biogeochemistry component. However, model component is only an approximate term, there is no precise definition of whether any given model has or does not have a given component.

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:model_component` |
| **Entries** | 10 |
| **Validation** | ✓ Validated |
| **Pydantic Model** | [`ModelComponent`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/model_component.py) |
| **JSON-LD** | [`emd:model_component`](https://emd.mipcvs.dev/model_component) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/model_component) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-02-22 |

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

**Direct Access:**

- JSON: [`https://emd.mipcvs.dev/model_component/arpege-climat-version-6-3.json`](https://emd.mipcvs.dev/model_component/arpege-climat-version-6-3.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Amodel_component/arpege-climat-version-6-3)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:model_component/arpege-climat-version-6-3")
```

**Python (esgvoc):**

```python
from esgvoc.api import search
results = search.find("model_component", term="arpege-climat-version-6-3")
```
