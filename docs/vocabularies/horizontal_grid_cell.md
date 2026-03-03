# Horizontal Grid Cells

_No description provided yet._

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:horizontal_grid_cells` |
| **Entries** | 7 |
| **Validation** | ✗ Not yet |
| **Pydantic Model** | _Not yet implemented_ |
| **JSON-LD** | [`emd:horizontal_grid_cells`](https://emd.mipcvs.dev/horizontal_grid_cells) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/horizontal_grid_cells) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-02-22 |

---

## Schema

*No Pydantic model available. Fields extracted from JSON files.*

| Field | Type |
|-------|------|
| `description` | _unknown_ |
| `grid_mapping` | _unknown_ |
| `grid_type` | _unknown_ |
| `n_cells` | _unknown_ |
| `region` | _unknown_ |
| `southernmost_latitude` | _unknown_ |
| `temporal_refinement` | _unknown_ |
| `truncation_method` | _unknown_ |
| `truncation_number` | _unknown_ |
| `ui_label` | _unknown_ |
| `units` | _unknown_ |
| `validation_key` | _unknown_ |
| `westernmost_longitude` | _unknown_ |
| `x_resolution` | _unknown_ |
| `y_resolution` | _unknown_ |

---

## Usage

**Direct Access:**

- JSON: [`https://emd.mipcvs.dev/horizontal_grid_cells/g100.json`](https://emd.mipcvs.dev/horizontal_grid_cells/g100.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Ahorizontal_grid_cells/g100)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:horizontal_grid_cells/g100")
```

**Python (esgvoc):**

```python
from esgvoc.api import search
results = search.find("horizontal_grid_cells", term="g100")
```
