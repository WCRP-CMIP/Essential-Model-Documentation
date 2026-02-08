# Reference

![Generated](https://img.shields.io/badge/Generated-2026_01_30-708090) ![Type](https://img.shields.io/badge/Type-emd%3Areference-blue) ![Pydantic](https://img.shields.io/badge/Pydantic-✓-green) ![Files](https://img.shields.io/badge/Files-19-lightgrey)

Academic reference to published work for the top-level model or model components. An academic reference to published work for the top-level model or one of its model components is defined by the following properties: * **Citation** - A human-readable citation for the work. E.g. Smith, R. S., Mathiot, P., Siahaan, A., Lee, V., Cornford, S. L., Gregory, J. M., et al. (2021). Coupling the U.K. Earth System model to dynamic models of the Greenland and Antarctic ice sheets. Journal of Advances in Modeling Earth Systems, 13, e2021MS002520. https://doi.org/10.1029/2021MS002520, 2023 * **DOI** - The persistent identifier (DOI) used to identify the work. A DOI is required for all references. A reference that does not already have a DOI (as could be the case for some technical reports, for instance) must be given one (e.g. with a service like Zenodo). E.g. https://doi.org/10.1029/2021MS002520

---

## Quick Reference

| Property | Value |
|----------|-------|
| **Type URI** | `emd:reference` |
| **Prefix** | `emd` |
| **Pydantic Model** | [`Reference`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/reference.py) |
| **JSON-LD** | [`emd:reference`](https://emd.mipcvs.dev/reference) |
| **Repository** | [![View Source](https://img.shields.io/badge/GitHub-View_Source-blue?logo=github)](https://github.com/wcrp-cmip/Essential-Model-Documentation//tree/src-data/reference) |
| **Contribute** | [![Submit New / Edit Existing](https://img.shields.io/badge/Submit_New-Edit_Existing-grey?labelColor=orange&logo=github)](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |

---

## Schema

The JSON structure and validation for this vocabulary is defined using the [`Reference`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/reference.py) Pydantic model in [esgvoc](https://github.com/ESGF/esgf-vocab). This ensures data consistency and provides automatic validation of all entries. *Click field name for description.*

### Required Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [citation](#citation) | `str` | min_length=1 | - |
| [doi](#doi) | `str` | min_length=1 | - |

### Optional Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [description](#description) | `str` | - | - |

### Field Descriptions

<a id="description"></a>
#### Description

_No description available._

<a id="citation"></a>
#### Citation

A human-readable citation for the work.

<details id="citation-validate_citation" open>
<summary><strong>Validation:</strong> validate_citation <a href="https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/reference.py">[source]</a></summary>

Validate that citation is not empty.

```python
def validate_citation(cls, v):
        """Validate that citation is not empty."""
        if not v.strip():
            raise ValueError("Citation cannot be empty")
        return v.strip()
```

</details>

<a id="doi"></a>
#### Doi

The persistent identifier (DOI) used to identify the work. Must be a valid DOI URL.

<details id="doi-validate_doi" open>
<summary><strong>Validation:</strong> validate_doi <a href="https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/EMD_models/reference.py">[source]</a></summary>

Validate that DOI follows proper format (accepts proxies like doi-org.insu.bib...).

```python
def validate_doi(cls, v):
        """Validate that DOI follows proper format (accepts proxies like doi-org.insu.bib...)."""
        # Remove all whitespace to handle formatting issues
        v = "".join(v.split())

        # Accept both canonical DOIs and proxy URLs
        if not v.startswith("https://doi"):
            raise ValueError(
                'DOI must start with "https://doi" (canonical: https://doi.org/, proxies: https://doi-...)'
            )

        # Ensure there's an actual identifier after the DOI prefix
        if len(v) <= len("https://doi"):
            raise ValueError('DOI must contain identifier after "https://doi"')

        return v
```

</details>

---

## Usage

<details open>
<summary><strong>Online</strong></summary>

| Resource | Link |
|----------|------|
| **Direct JSON** | [ref-bisicles.json](https://github.com/wcrp-cmip/Essential-Model-Documentation//tree/src-data/reference/ref-bisicles.json) |
| **Interactive Viewer** | [Open Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Areference/ref-bisicles) |
| **Full URL** | [https://emd.mipcvs.dev/reference/ref-bisicles.json](https://emd.mipcvs.dev/reference/ref-bisicles.json) |

</details>

<details>
<summary><strong>cmipld</strong></summary>

```python
import cmipld

# Fetch and resolve a single record
data = cmipld.get("emd:reference/ref-bisicles")
print(data)
```

</details>

<details>
<summary><strong>esgvoc</strong></summary>

```python
from esgvoc.api import search

# Search for terms in this vocabulary
results = search.find("reference", term="ref-bisicles")
print(results)
```

</details>

<details>
<summary><strong>HTTP</strong></summary>

```python
import requests

url = "https://emd.mipcvs.dev/reference/ref-bisicles.json"
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
ldr compact https://emd.mipcvs.dev/reference/ref-bisicles.json
```

</details>
