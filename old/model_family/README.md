# Model Family

![Generated](https://img.shields.io/badge/Generated-2026_01_30-708090) ![Type](https://img.shields.io/badge/Type-emd%3Amodel_family-blue) ![Pydantic](https://img.shields.io/badge/Pydantic-✗-red) ![Files](https://img.shields.io/badge/Files-32-lightgrey)

_No description provided yet._

---

## Quick Reference

| Property | Value |
|----------|-------|
| **Type URI** | `emd:model_family` |
| **Prefix** | `emd` |
| **Pydantic Model** | _Not yet implemented_ |
| **JSON-LD** | [`emd:model_family`](https://emd.mipcvs.dev/model_family) |
| **Repository** | [![View Source](https://img.shields.io/badge/GitHub-View_Source-blue?logo=github)](https://github.com/wcrp-cmip/Essential-Model-Documentation//tree/src-data/model_family) |
| **Contribute** | [![Submit New / Edit Existing](https://img.shields.io/badge/Submit_New-Edit_Existing-grey?labelColor=orange&logo=github)](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |

---

## Schema

*No Pydantic model available. Fields extracted from JSON files.*

| Field | Type |
|-------|------|
| `description` | _unknown_ |
| `collaborative_institutions` | _unknown_ |
| `common_scientific_basis` | _unknown_ |
| `computational_requirements` | _unknown_ |
| `documentation` | _unknown_ |
| `established` | _unknown_ |
| `evolution` | _unknown_ |
| `license` | _unknown_ |
| `primary_institution` | _unknown_ |
| `programming_languages` | _unknown_ |
| `references` | _unknown_ |
| `representative_member` | _unknown_ |
| `scientific_domains` | _unknown_ |
| `shared_code_base` | _unknown_ |
| `software_dependencies` | _unknown_ |
| `source_code_repository` | _unknown_ |
| `ui_label` | _unknown_ |
| `validation_key` | _unknown_ |
| `variation_dimensions` | _unknown_ |
| `website` | _unknown_ |

---

## Usage

<details open>
<summary><strong>Online</strong></summary>

| Resource | Link |
|----------|------|
| **Direct JSON** | [access.json](https://github.com/wcrp-cmip/Essential-Model-Documentation//tree/src-data/model_family/access.json) |
| **Interactive Viewer** | [Open Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Amodel_family/access) |
| **Full URL** | [https://emd.mipcvs.dev/model_family/access.json](https://emd.mipcvs.dev/model_family/access.json) |

</details>

<details>
<summary><strong>cmipld</strong></summary>

```python
import cmipld

# Fetch and resolve a single record
data = cmipld.get("emd:model_family/access")
print(data)
```

</details>

<details>
<summary><strong>esgvoc</strong></summary>

```python
from esgvoc.api import search

# Search for terms in this vocabulary
results = search.find("model_family", term="access")
print(results)
```

</details>

<details>
<summary><strong>HTTP</strong></summary>

```python
import requests

url = "https://emd.mipcvs.dev/model_family/access.json"
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
ldr compact https://emd.mipcvs.dev/model_family/access.json
```

</details>
