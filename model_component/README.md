# Model Component

One model component. Required: component, description, references, and a name or ui_label.

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:model_component` |
| **Entries** | 152 |
| **Validation** | ✓ Validated |
| **Pydantic Model** | [`ModelComponent`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model_component.py) |
| **JSON-LD** | [`emd:model_component`](https://emd.wcrp-cmip.org/model_component) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/model_component) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-11-23 |

---

## Schema

The JSON structure and validation for this vocabulary is defined using the [`ModelComponent`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model_component.py) pydantic model, kept alongside the data in [`.github/EMD_tests`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests). This ensures data consistency and provides automatic validation of all entries. *Click field name for description.*

### Required Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [description](#description) | `str` | - | - |
| [component](#component) | `str` | - | - |
| [context](#context) | `Literal` | - | - |
| [references](#references) | `List[Annotated]` | min_length=1 | - |
| [validation_key](#validation_key) | `str` | - | - |

### Optional Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [name](#name) | `str | None` | - | - |
| [code_base](#code_base) | `str | None` | - | - |
| [family](#family) | `Optional[Annotated]` | - | - |
| [ui_label](#ui_label) | `str | None` | - | - |

### Field Descriptions

<a id="description"></a>
#### Description

_No description available._

<a id="name"></a>
#### Name

_No description available._

<a id="code_base"></a>
#### Code Base

_No description available._

<a id="component"></a>
#### Component

_No description available._

<a id="context"></a>
#### Context

_No description available._

<a id="family"></a>
#### Family

_No description available._

<a id="references"></a>
#### References

_No description available._

<a id="ui_label"></a>
#### Ui Label

_No description available._

<a id="validation_key"></a>
#### Validation Key

_No description available._

### Other Validations

<details markdown="1" id="other-has_a_name" open>
<summary><strong>has_a_name</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model_component.py">[source]</a></summary>

name is required (EMD Appendix B 3). The repository usually holds it in ui_label, so either counts.

```python
def has_a_name(self):
        """name is required (EMD Appendix B 3). The repository usually holds it in ui_label, so either counts."""
        if not (self.name or self.ui_label):
            raise ValueError("set name or ui_label")
        return self

    # --------------------------------------------------------------- warnings: the record loads
```

</details>

<details markdown="1" id="other-family_given" open>
<summary><strong>family_given</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model_component.py">[source]</a></summary>

family is given; a component with no family uses no-family.

```python
def family_given(self):
        """family is given; a component with no family uses no-family."""
        if self.family is None:
            warn(f"{self.id}: family is empty; use 'no-family' if the component has none")
        return self
```

</details>

<details markdown="1" id="other-name_has_hyphenated_version" open>
<summary><strong>name_has_hyphenated_version</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model_component.py">[source]</a></summary>

The name holds a version written with hyphens, not dots (reviewer checklist).

```python
def name_has_hyphenated_version(self):
        """The name holds a version written with hyphens, not dots (reviewer checklist)."""
        name = self.name or self.id
        if re.search(r"\d+\.\d+", name):
            warn(f"{self.id}: name '{name}' writes its version with dots; use hyphens")
        elif not re.search(r"\d", name):
            warn(f"{self.id}: name '{name}' holds no version")
        return self
```

</details>

<details markdown="1" id="other-description_is_specific" open>
<summary><strong>description_is_specific</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model_component.py">[source]</a></summary>

The description says what the component simulates, not only where it is used.

```python
def description_is_specific(self):
        """The description says what the component simulates, not only where it is used."""
        text = self.description.strip()
        if len(text.split()) == 1 or GENERIC.fullmatch(text):
            warn(f"{self.id}: the description is too generic to say what the component simulates")
        return self
```

</details>

<details markdown="1" id="other-code_base_is_a_fixed_url" open>
<summary><strong>code_base_is_a_fixed_url</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model_component.py">[source]</a></summary>

code_base is a URL, or private/none. A repository URL names a commit, tag or release (EMD 3).

```python
def code_base_is_a_fixed_url(self):
        """code_base is a URL, or private/none. A repository URL names a commit, tag or release (EMD 3)."""
        url = (self.code_base or "").strip()
        if not url or url.lower() in NO_PUBLIC_CODE:
            return self
        if not url.startswith(("http://", "https://")):
            warn(f"{self.id}: code_base '{url}' is not a URL, 'private' or 'none'")
        elif ("github.com" in url or "gitlab" in url) and not PINNED.fullmatch(url):
            warn(f"{self.id}: code_base '{url}' does not name a commit, tag or release")
        return self


model = ModelComponent
```

</details>

---

## Usage

**Direct Access:**

- JSON: [`https://emd.wcrp-cmip.org/model_component/am4-2-aerosol.json`](https://emd.wcrp-cmip.org/model_component/am4-2-aerosol.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Amodel_component/am4-2-aerosol)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:model_component/am4-2-aerosol")
```
