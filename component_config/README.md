# Component Config

_No description provided yet._

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:component_config` |
| **Entries** | 7 |
| **Validation** | ✗ Not yet |
| **Pydantic Model** | _Not yet implemented_ |
| **JSON-LD** | [`emd:component_config`](https://emd.mipcvs.dev/component_config) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/component_config) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-02-22 |

---

## Schema

*No Pydantic model available. Fields extracted from JSON files.*

| Field | Type |
|-------|------|
| `description` | _unknown_ |
| `horizontal_computational_grid` | _unknown_ |
| `model_component` | _unknown_ |
| `ui_label` | _unknown_ |
| `validation_key` | _unknown_ |
| `vertical_computational_grid` | _unknown_ |

---

## Usage

**Direct Access:**

- JSON: [`https://emd.mipcvs.dev/component_config/aerosol-tactic-h100-v100.json`](https://emd.mipcvs.dev/component_config/aerosol-tactic-h100-v100.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Acomponent_config/aerosol-tactic-h100-v100)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:component_config/aerosol-tactic-h100-v100")
```

**Python (esgvoc):**

```python
from esgvoc.api import search
results = search.find("component_config", term="aerosol-tactic-h100-v100")
```
