# Extract the data

The EMD is JSON-LD: each record links to other records by id. These libraries fetch a record and expand its links for you, to as many levels as you ask for.

## Python

[**CMIP-LD**](https://github.com/WCRP-CMIP/CMIP-LD) (`cmipld`) needs Python 3.8+ and [Node.js](https://nodejs.org/), because it runs a small local helper to process the linked data.

```bash
pip install "git+https://github.com/WCRP-CMIP/CMIP-LD.git"
```

```python
import cmipld

model = cmipld.get("emd:model/ukesm1-3-ll")                          # one model, links expanded
ids = [e["@id"] for e in cmipld.get("emd:model/graph")["contents"]]  # every model id
```

The first call can take a while, because the library fetches one level of links at a time. Later calls are answered from its cache.

## JavaScript

[**jsonld-recursive**](https://www.npmjs.com/package/jsonld-recursive) runs in the browser. Add its two script tags, then call `compact`:

```html
<script src="https://cdn.jsdelivr.net/npm/jsonld-recursive@1.1.2/lib/ldr-core.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jsonld-recursive@1.1.2/lib/ldr-browser.js"></script>

<script type="module">
  await JsonLdExpand.init();

  const base = "https://wcrp-cmip.github.io/Essential-Model-Documentation/";
  const contents = (await JsonLdExpand.compact(base + "model/_graph.json", { depth: 1 })).contents;   // every model
  const model = await JsonLdExpand.compact(base + "model/ukesm1-3-ll.json", { depth: 3 });            // one model, links expanded
</script>
```

`depth` is how many levels of links to follow. Each level fetches more files, so start small.

## Try it in a notebook

[**Reading the EMD in your own work**](https://observablehq.com/@wolfiex/reading-the-emd-in-your-own-work) is an interactive Observable notebook. Pick a folder, list its entries, then expand any item and follow its links to the depth you choose.
