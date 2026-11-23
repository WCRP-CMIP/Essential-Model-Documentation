# Model Family

One model family. Nothing is required by the specification; gaps are warnings.

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:model_family` |
| **Entries** | 74 |
| **Validation** | ✓ Validated |
| **Pydantic Model** | [`ModelFamily`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model_family.py) |
| **JSON-LD** | [`emd:model_family`](https://emd.wcrp-cmip.org/model_family) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/model_family) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-11-23 |

---

## Schema

The JSON structure and validation for this vocabulary is defined using the [`ModelFamily`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model_family.py) pydantic model, kept alongside the data in [`.github/EMD_tests`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests). This ensures data consistency and provides automatic validation of all entries. *Click field name for description.*

### Required Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [context](#context) | `Literal` | - | - |
| [validation_key](#validation_key) | `str` | - | - |

### Optional Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [description](#description) | `str | None` | - | - |
| [collaborative_institutions](#collaborative_institutions) | `List[str]` | - | - |
| [established](#established) | `Any` | - | - |
| [family_type](#family_type) | `str | None` | - | - |
| [primary_institution](#primary_institution) | `str | None` | - | - |
| [references](#references) | `List[Annotated]` | - | - |
| [representative_member](#representative_member) | `Any` | - | - |
| [scientific_domains](#scientific_domains) | `List[Annotated]` | - | - |
| [ui_label](#ui_label) | `str | None` | - | - |

### Field Descriptions

<a id="description"></a>
#### Description

_No description available._

<a id="collaborative_institutions"></a>
#### Collaborative Institutions

_No description available._

<a id="context"></a>
#### Context

_No description available._

<a id="established"></a>
#### Established

_No description available._

<a id="family_type"></a>
#### Family Type

_No description available._

<a id="primary_institution"></a>
#### Primary Institution

_No description available._

<a id="references"></a>
#### References

_No description available._

<a id="representative_member"></a>
#### Representative Member

_No description available._

<a id="scientific_domains"></a>
#### Scientific Domains

_No description available._

<a id="ui_label"></a>
#### Ui Label

_No description available._

<a id="validation_key"></a>
#### Validation Key

_No description available._

### Other Validations

<details markdown="1" id="other-institution_given_once" open>
<summary><strong>institution_given_once</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model_family.py">[source]</a></summary>

A primary institution is given, and it is not also listed as a collaborator.

```python
def institution_given_once(self):
        """A primary institution is given, and it is not also listed as a collaborator."""
        if self.is_sentinel:
            return self
        if not self.primary_institution:
            warn(f"{self.id}: primary_institution is empty")
        elif self.primary_institution in self.collaborative_institutions:
            warn(f"{self.id}: '{self.primary_institution}' is both primary and collaborative institution")
        return self
```

</details>

<details markdown="1" id="other-references_and_description_given" open>
<summary><strong>references_and_description_given</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model_family.py">[source]</a></summary>

A family cites at least one reference and has a description.

```python
def references_and_description_given(self):
        """A family cites at least one reference and has a description."""
        if self.is_sentinel:
            return self
        if not self.references:
            warn(f"{self.id}: references is empty")
        if not self.description:
            warn(f"{self.id}: description is empty")
        return self


model = ModelFamily
```

</details>

---

## Usage

**Direct Access:**

- JSON: [`https://emd.wcrp-cmip.org/model_family/access-esm.json`](https://emd.wcrp-cmip.org/model_family/access-esm.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Amodel_family/access-esm)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:model_family/access-esm")
```
