# Model

One model. Required: name, description, release_year, calendar, references, dynamic_components and model_components (EMD Appendix B 2).

---

## Quick Reference

| | |
|---|---|
| **Type URI** | `emd:model` |
| **Entries** | 34 |
| **Validation** | ✓ Validated |
| **Pydantic Model** | [`Model`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model.py) |
| **JSON-LD** | [`emd:model`](https://emd.wcrp-cmip.org/model) |
| **Source** | [View on GitHub](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/src-data/model) |
| **Contribute** | [Submit or Edit](https://github.com/wcrp-cmip/Essential-Model-Documentation/tree/main?tab=readme-ov-file#contributing) |
| **Generated** | 2026-11-23 |

---

## Schema

The JSON structure and validation for this vocabulary is defined using the [`Model`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model.py) pydantic model, kept alongside the data in [`.github/EMD_tests`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests). This ensures data consistency and provides automatic validation of all entries. *Click field name for description.*

### Required Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [description](#description) | `str` | - | - |
| [name](#name) | `str` | - | - |
| [calendar](#calendar) | `List[Annotated]` | min_length=1 | - |
| [context](#context) | `Literal` | - | - |
| [dynamic_components](#dynamic_components) | `List[Annotated]` | min_length=1 | - |
| [model_components](#model_components) | `List[Annotated]` | min_length=1 | - |
| [references](#references) | `List[Annotated]` | min_length=1 | - |
| [release_year](#release_year) | `int` | - | - |
| [validation_key](#validation_key) | `str` | - | - |

### Optional Fields

| Field | Type | Constraints | References |
|-------|------|-------------|------------|
| [coupled_components](#coupled_components) | `List[tuple]` | - | - |
| [crs](#crs) | `str | None` | - | - |
| [embedded_components](#embedded_components) | `List[tuple]` | - | - |
| [family](#family) | `Optional[Annotated]` | - | - |
| [omitted_components](#omitted_components) | `List[Annotated]` | - | - |
| [prescribed_components](#prescribed_components) | `List[Annotated]` | - | - |
| [ui_label](#ui_label) | `str | None` | - | - |

### Field Descriptions

<a id="description"></a>
#### Description

_No description available._

<a id="name"></a>
#### Name

_No description available._

<a id="calendar"></a>
#### Calendar

_No description available._

<a id="context"></a>
#### Context

_No description available._

<a id="coupled_components"></a>
#### Coupled Components

_No description available._

<a id="crs"></a>
#### Crs

_No description available._

<a id="dynamic_components"></a>
#### Dynamic Components

_No description available._

<a id="embedded_components"></a>
#### Embedded Components

_No description available._

<a id="family"></a>
#### Family

_No description available._

<a id="model_components"></a>
#### Model Components

_No description available._

<a id="omitted_components"></a>
#### Omitted Components

_No description available._

<a id="prescribed_components"></a>
#### Prescribed Components

_No description available._

<a id="references"></a>
#### References

_No description available._

<a id="release_year"></a>
#### Release Year

_No description available._

<a id="ui_label"></a>
#### Ui Label

_No description available._

<a id="validation_key"></a>
#### Validation Key

_No description available._

### Other Validations

<details markdown="1" id="other-dynamic_not_also_omitted" open>
<summary><strong>dynamic_not_also_omitted</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model.py">[source]</a></summary>

A component cannot be simulated and also absent (EMD 2).

```python
def dynamic_not_also_omitted(self):
        """A component cannot be simulated and also absent (EMD 2)."""
        if both := set(self.dynamic_components) & set(self.omitted_components):
            raise ValueError(f"{sorted(both)} are both dynamic and omitted")
        return self
```

</details>

<details markdown="1" id="other-pairs_name_two_dynamic_components" open>
<summary><strong>pairs_name_two_dynamic_components</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model.py">[source]</a></summary>

Each embedded or coupled pair names two different dynamic components (EMD Appendix B 2).

```python
def pairs_name_two_dynamic_components(self):
        """Each embedded or coupled pair names two different dynamic components (EMD Appendix B 2)."""
        for field in ("embedded_components", "coupled_components"):
            for a, b in getattr(self, field):
                if a == b or not {a, b} <= set(self.dynamic_components):
                    raise ValueError(f"{field} pair ({a}, {b}) must name two different dynamic components")
        return self
```

</details>

<details markdown="1" id="other-one_host_each" open>
<summary><strong>one_host_each</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model.py">[source]</a></summary>

An embedded component has one host (EMD 3.1).

```python
def one_host_each(self):
        """An embedded component has one host (EMD 3.1)."""
        children = [child for child, _ in self.embedded_components]
        if many := sorted({c for c in children if children.count(c) > 1}):
            raise ValueError(f"{many} are embedded in more than one host")
        return self
```

</details>

<details markdown="1" id="other-no_embedding_cycle" open>
<summary><strong>no_embedding_cycle</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model.py">[source]</a></summary>

A component cannot be embedded, directly or indirectly, in itself.

```python
def no_embedding_cycle(self):
        """A component cannot be embedded, directly or indirectly, in itself."""
        if cycle := first_cycle(dict(self.embedded_components)):
            raise ValueError(f"the embedding makes a cycle: {' -> '.join(cycle)}")
        return self
```

</details>

<details markdown="1" id="other-embedded_components_do_not_couple" open>
<summary><strong>embedded_components_do_not_couple</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model.py">[source]</a></summary>

An embedded component cannot be coupled with any other component (EMD 3.1).

```python
def embedded_components_do_not_couple(self):
        """An embedded component cannot be coupled with any other component (EMD 3.1)."""
        embedded = {child for child, _ in self.embedded_components}
        if both := embedded & {x for pair in self.coupled_components for x in pair}:
            raise ValueError(f"{sorted(both)} are embedded and also coupled")
        return self
```

</details>

<details markdown="1" id="other-hosts_coupled_into_one_group" open>
<summary><strong>hosts_coupled_into_one_group</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model.py">[source]</a></summary>

With more than one superior host, the couplings join them all into one group (EMD 3.1).

```python
def hosts_coupled_into_one_group(self):
        """With more than one superior host, the couplings join them all into one group (EMD 3.1)."""
        if len(self.hosts) > 1 and len(groups := connected_groups(self.hosts, self.coupled_components)) > 1:
            raise ValueError(f"the couplings leave separate groups: {[sorted(g) for g in groups]}")
        return self

    # --------------------------------------------------------------- warnings: the record loads
```

</details>

<details markdown="1" id="other-family_given" open>
<summary><strong>family_given</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model.py">[source]</a></summary>

family is given; a model with no family uses no-family.

```python
def family_given(self):
        """family is given; a model with no family uses no-family."""
        if self.family is None:
            warn(f"{self.id}: family is empty; use 'no-family' if the model has none")
        return self
```

</details>

<details markdown="1" id="other-prescribed_not_in_another_list" open>
<summary><strong>prescribed_not_in_another_list</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model.py">[source]</a></summary>

A prescribed component is not also dynamic or omitted (reviewer checklist).

```python
def prescribed_not_in_another_list(self):
        """A prescribed component is not also dynamic or omitted (reviewer checklist)."""
        prescribed = set(self.prescribed_components)
        if both := prescribed & (set(self.dynamic_components) | set(self.omitted_components)):
            warn(f"{self.id}: {sorted(both)} are prescribed and also dynamic or omitted")
        return self
```

</details>

<details markdown="1" id="other-embedding_is_usual" open>
<summary><strong>embedding_is_usual</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model.py">[source]</a></summary>

Each (embedded, host) pair is one of the usual patterns (reviewer checklist).

```python
def embedding_is_usual(self):
        """Each (embedded, host) pair is one of the usual patterns (reviewer checklist)."""
        for child, host in self.embedded_components:
            if (child, host) not in USUAL_EMBEDDING:
                warn(f"{self.id}: {child} embedded in {host} is unusual; check the description explains it")
        return self
```

</details>

<details markdown="1" id="other-release_year_plausible" open>
<summary><strong>release_year_plausible</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model.py">[source]</a></summary>

release_year is from 1990 to this year (reviewer checklist).

```python
def release_year_plausible(self):
        """release_year is from 1990 to this year (reviewer checklist)."""
        if not 1990 <= self.release_year <= datetime.date.today().year:
            warn(f"{self.id}: release_year {self.release_year} is implausible")
        return self
```

</details>

<details markdown="1" id="other-crs_agrees_with_lists" open>
<summary><strong>crs_agrees_with_lists</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model.py">[source]</a></summary>

crs names each dynamic component once, each prescribed one once with "^", and the same pairs.

```python
def crs_agrees_with_lists(self):
        """crs names each dynamic component once, each prescribed one once with "^", and the same pairs."""
        if not self.crs:
            return self
        try:
            marks, embedded, coupled = read_crs(self.crs)
        except ValueError as exc:
            warn(f"{self.id}: crs '{self.crs}' cannot be read: {exc}")
            return self
        code = INITIALS.get
        expected = {code(d): False for d in self.dynamic_components} | {code(d): True for d in self.prescribed_components}
        if marks != expected:
            warn(f"{self.id}: crs '{self.crs}' does not list the same dynamic and prescribed components")
        if embedded != {(code(a), code(b)) for a, b in self.embedded_components}:
            warn(f"{self.id}: crs '{self.crs}' does not show the same embedded_components")
        if coupled != {frozenset((code(a), code(b))) for a, b in self.coupled_components}:
            warn(f"{self.id}: crs '{self.crs}' does not show the same coupled_components")
        return self
```

</details>

<details markdown="1" id="other-description_mentions_each_component" open>
<summary><strong>description_mentions_each_component</strong> <a href="https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/main/.github/EMD_tests/model.py">[source]</a></summary>

The description mentions every dynamic, prescribed and omitted component (EMD 2).

```python
def description_mentions_each_component(self):
        """The description mentions every dynamic, prescribed and omitted component (EMD 2)."""
        text = self.description.lower().replace("-", " ")
        every = {*self.dynamic_components, *self.prescribed_components, *self.omitted_components}
        missing = sorted(d for d in every if not any(w in text for w in KEYWORDS.get(d, [d.replace("-", " ")])))
        if missing:
            warn(f"{self.id}: the description does not mention {missing}")
        if self.prescribed_components and "prescrib" not in text:
            warn(f"{self.id}: the description does not say how the prescribed components are supplied")
        return self


model = Model
```

</details>

---

## Usage

**Direct Access:**

- JSON: [`https://emd.wcrp-cmip.org/model/access-esm1-6.json`](https://emd.wcrp-cmip.org/model/access-esm1-6.json)
- Viewer: [Open in CMIP-LD Viewer](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri=emd%3Amodel/access-esm1-6)

**Python (cmipld):**

```python
import cmipld
data = cmipld.get("emd:model/access-esm1-6")
```
