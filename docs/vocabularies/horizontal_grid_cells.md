# Horizontal Grid Cells

![Generated](https://img.shields.io/badge/Generated-2026_01_30-708090) ![Type](https://img.shields.io/badge/Type-emd%3Ahorizontal_grid_cells-blue) ![Pydantic](https://img.shields.io/badge/Pydantic-✗-red) ![Files](https://img.shields.io/badge/Files-7-lightgrey)

_No description provided yet._

---

## Quick Reference

| Property | Value |
|----------|-------|
| **Type URI** | `emd:horizontal_grid_cells` |
| **Prefix** | `emd` |
| **Pydantic Model** | _Not yet implemented_ |
| **JSON-LD** | [`emd:horizontal_grid_cells`](https://emd.mipcvs.dev/horizontal_grid_cells) |
| **Repository** | [![View Source](https://img.shields.io/badge/GitHub-View_Source-blue?logo=github)](https://github.com/wcrp-cmip/Essential-Model-Documentation//tree/src-data/horizontal_grid_cells) |
| **Contribute** | [![Submit New / Edit Existing](https://img.shields.io/badge/Submit_New-Edit_Existing-grey?labelColor=orange&logo=github)](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |

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

<details open>
<summary><strong>Online</strong></summary>

| Resource | Link |
|----------|------|
| **Direct JSON** | [g100.json](https://github.com/wcrp-cmip/Essential-Model-Documentation//tree/src-data/horizontal_grid_cells/g100.json) |
| **Interactive Viewer** | [Open Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Ahorizontal_grid_cells/g100) |
| **Full URL** | [https://emd.mipcvs.dev/horizontal_grid_cells/g100.json](https://emd.mipcvs.dev/horizontal_grid_cells/g100.json) |

</details>

<details>
<summary><strong>cmipld</strong></summary>

```python
import cmipld

# Fetch and resolve a single record
data = cmipld.get("emd:horizontal_grid_cells/g100")
print(data)
```

</details>

<details>
<summary><strong>esgvoc</strong></summary>

```python
from esgvoc.api import search

# Search for terms in this vocabulary
results = search.find("horizontal_grid_cells", term="g100")
print(results)
```

</details>

<details>
<summary><strong>HTTP</strong></summary>

```python
import requests

url = "https://emd.mipcvs.dev/horizontal_grid_cells/g100.json"
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
ldr compact https://emd.mipcvs.dev/horizontal_grid_cells/g100.json
```

</details>
