# Using the EMD in your work

The EMD is published as ordinary JSON files, so you can use it in three ways, from clicking around to scripting your own analysis. Pick whichever suits you; they all read the same data.

---

## Browse it

For a quick look, no code needed:

- [**Model viewer**](../Model_viewer/): everything about one model — its components, grids, coupling, references, and any data it has published to ESGF.
- [**Grid viewer**](../Grid_viewer/): find, filter and compare the horizontal grids.
- [**Model participation**](../Model_participation/): which institutions take part in which model and component families, and what they have published.

---

## Read the files directly

Every record is a JSON file at a predictable address, with no installation and no account:

```
https://wcrp-cmip.github.io/Essential-Model-Documentation/<folder>/<id>.json
```

=== "curl"

    ```bash
    curl https://wcrp-cmip.github.io/Essential-Model-Documentation/model/ukesm1-3-ll.json
    ```

=== "Python"

    ```python
    import requests

    base = "https://wcrp-cmip.github.io/Essential-Model-Documentation/"
    model = requests.get(base + "model/ukesm1-3-ll.json").json()
    print(model["validation_key"], model["family"], model["model_components"][:2])

    # every model in the EMD
    index = requests.get(base + "model/_graph.json").json()
    ids = [entry["@id"] for entry in index["contents"]]
    ```

=== "JavaScript"

    ```js
    const base = "https://wcrp-cmip.github.io/Essential-Model-Documentation/";
    const model = await (await fetch(base + "model/ukesm1-3-ll.json")).json();
    console.log(model.validation_key, model.family, model.model_components.slice(0, 2));
    ```

### How the records fit together

A record never repeats another record's content. It points to it by id, so `"family": "ukesm1"` means the file `model_family/ukesm1.json`. To get the full picture of a model, follow the links:

| Folder | What a record describes | Links to |
|---|---|---|
| `model` | One model (its `source_id`): realms, coupling, release year | `family`, `model_components` |
| `model_family` | A family of models or of components | institutions |
| `component_config` | A component version on a specific grid | `model_component`, `horizontal_computational_grid`, `vertical_computational_grid` |
| `model_component` | A versioned piece of model software | `family` |
| `horizontal_computational_grid` | The complete horizontal domain a component runs on | `horizontal_subgrids` |
| `horizontal_subgrid` | Where variable types sit within a grid | `horizontal_grid_cell` |
| `horizontal_grid_cell` | Grid geometry: type, resolution, extent | |
| `vertical_computational_grid` | The vertical layering | |

Each folder also has a `_graph.json` listing everything in it.

!!! note "Good to know"
    - A model's `validation_key` is its `source_id` in capitals (`UKESM1-3-LL`); the file name and id are lower case (`ukesm1-3-ll`).
    - Institutions are managed by ESGVOC, not by the EMD, so they live in a separate registry, the [WCRP universe](https://github.com/WCRP-CMIP/WCRP-universe).
    - A few links point to records that are not published yet. Write your code so that a missing record does not stop it.

---

## Python: the CMIP-LD library

[**CMIP-LD**](https://github.com/WCRP-CMIP/CMIP-LD) (`cmipld`) is the Python library for the CMIP linked-data registries, the EMD included. Its advantage over reading the files yourself is that it follows the links for you. Ask for a model, and you get back the family, the institutions, every component configuration, and their grids already filled in.

**Install** (you need Python 3.8+ and [Node.js](https://nodejs.org/), because the library runs a small local helper to process the linked data):

```bash
pip install "git+https://github.com/WCRP-CMIP/CMIP-LD.git"
```

**Use**:

```python
import cmipld

# one model, with everything it links to filled in
model = cmipld.get("emd:model/ukesm1-3-ll")
print(model["ui_label"], "| released", model["release_year"])
print("family:", model["family"]["@id"], "| lead institution:", model["family"]["primary_institution"]["@id"])
for c in model["model_components"]:
    print(c["model_component"]["component"], c["horizontal_computational_grid"]["arrangement"],
          c["vertical_computational_grid"]["n_z"], "levels")

# every model in the EMD
ids = [e["@id"] for e in cmipld.get("emd:model/graph")["contents"]]
```

The `emd:` prefix points at the EMD. The same call works for the other CMIP registries (for example `universal:` and `cmip7:`). See the [CMIP-LD README](https://github.com/WCRP-CMIP/CMIP-LD#readme) for the full list. The library also works alongside [esgvoc](https://github.com/ESGF/esgf-vocab), the ESGF vocabulary API.

!!! tip "Version"
    Install from GitHub as shown above. The release on PyPI (0.0.6, July 2025) is older than the version this page was written against.

---

<!-- Observable notebook: add a section here with the link once the notebook page is published. -->

## Questions

Email [emd@wcrp-cmip.org](mailto:emd@wcrp-cmip.org), or open an issue on the [GitHub repository](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues).
