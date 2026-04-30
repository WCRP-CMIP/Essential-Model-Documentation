#!/usr/bin/env python3
"""
generate_similarity.py
======================
For every configured record type, generate:

  docs/EMD_Repository/{stem}.md           — MkDocs page (appears in site nav)
  docs/EMD_Repository/{stem}_data.json    — raw data snapshot

Each .md page embeds an integrated visualisation:
  1. "View a specific <X>" dropdown + summary stats
  2. Dendrogram (UPGMA on spectrally-ordered similarity, orthogonal branches)
     fused left-to-right with the adjacency/similarity matrix — one SVG
  3. Radial key-schema graph (2 levels deep, includes linked-object sub-keys)

Dendrogram leaf order == spectral order of the similarity matrix; every leaf
is pinned to the y-centre of its matrix row.  Branches are orthogonal
(right-angle elbow paths: M px,py V cy H cx).

Dependencies: numpy>=1.24.0, cmipld (via helpers.data_loader)
"""

import json
import sys
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
DOCS_DIR   = SCRIPT_DIR.parent
REPO_ROOT  = DOCS_DIR.parent
OUT_DIR    = DOCS_DIR / "EMD_Repository"   # pages live alongside entry pages

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

for candidate in [
    REPO_ROOT.parent / "CMIP-LD",
    Path.home() / "WIPwork" / "CMIP-LD",
]:
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
        break

# ── imports ───────────────────────────────────────────────────────────────────
try:
    from helpers.data_loader import init_loader, fetch_data
except ImportError as e:
    print(f"  \u26a0 generate_similarity: cannot import data_loader ({e}) \u2014 skipping.", flush=True)
    raise SystemExit(0)

try:
    import numpy as np
except ImportError:
    print("  \u26a0 generate_similarity: numpy not installed \u2014 skipping.", flush=True)
    raise SystemExit(0)

try:
    from cmipld.utils.similarity.folder_similarity import (_get_label, _get_tags)
    from cmipld.utils.similarity import (
        extract_links, strip_text_fields, compute_field_similarity,
    )
    from cmipld.utils.similarity.link_analyzer import _jaccard
except ImportError as e:
    print(f"  \u26a0 generate_similarity: cannot import cmipld similarity ({e}) \u2014 skipping.", flush=True)
    raise SystemExit(0)


# ── configuration ──────────────────────────────────────────────────────────────

ENDPOINT_OVERRIDES = {
    "Component_Families":             "model_family",
    "Earth_System_Model_Families":    "model_family",
    "Models":                         "model",
    "Model_Components":               "model_component",
    "Horizontal_Computational_Grids": "horizontal_computational_grid",
    "Vertical_Computational_Grids":   "vertical_computational_grid",
    "Horizontal_Grid_Cells":          "horizontal_grid_cell",
}

PRE_FILTER = {
    "Component_Families":          ("family_type", "component"),
    "Earth_System_Model_Families": ("family_type", "model"),
}

FILTER_FIELD = {
    "Component_Families":          "scientific_domains",
    "Earth_System_Model_Families": "scientific_domains",
    "Model_Components":            "component",
    "Horizontal_Grid_Cells":       "grid_type",
}

REPO_DIR_MAP = {
    "Component_Families":             "Component_Families",
    "Earth_System_Model_Families":    "Earth_System_Model_Families",
    "Models":                         "Models",
    "Model_Components":               "Model_Components",
    "Horizontal_Computational_Grids": "Horizontal_Computational_Grids",
    "Vertical_Computational_Grids":   "Vertical_Computational_Grids",
    "Horizontal_Grid_Cells":          "Horizontal_Grid_Cells",
}

# Submission stage order — controls page order in nav and run order
STAGE_ORDER = [
    "Horizontal_Grid_Cells",           # Stage 1
    "Horizontal_Computational_Grids",  # Stage 2a
    "Vertical_Computational_Grids",    # Stage 2b
    "Component_Families",              # Optional
    "Earth_System_Model_Families",     # Optional
    "Model_Components",                # Stage 3
    "Models",                          # Stage 4
]

SINGULAR_NAMES = {
    "Component_Families":             "Component Family",
    "Earth_System_Model_Families":    "ESM Family",
    "Models":                         "Model",
    "Model_Components":               "Model Component",
    "Horizontal_Computational_Grids": "Horizontal Grid",
    "Vertical_Computational_Grids":   "Vertical Grid",
    "Horizontal_Grid_Cells":          "Grid Cell",
}

DESCRIPTIONS = {
    "Horizontal_Grid_Cells":          "**Stage 1.** Grid cells define the fundamental 2D horizontal geometry — the shape, resolution, and extent of a single tile. A regular 1° atmosphere grid and a tripolar ocean grid are each their own record. Every grid cell is assigned a `g###` ID used in Stage 2.",
    "Horizontal_Computational_Grids": "**Stage 2a.** Horizontal computational grids assemble grid cells into the complete domain a component actually runs on, including the Arakawa staggering arrangement. Each record receives an `h###` ID used in Stage 3.",
    "Vertical_Computational_Grids":   "**Stage 2b.** Vertical grids are registered separately from horizontal grids because they vary independently of the horizontal layout. Each record captures coordinate type, level count, and vertical extent, and receives a `v###` ID used in Stage 3.",
    "Component_Families":             "**Optional.** Component families capture scientific lineage by grouping versions of a single-domain code base (e.g. NEMO, ARPEGE-Climat, SURFEX). A family ID can be referenced by model components at Stage 3.",
    "Earth_System_Model_Families":    "**Optional.** ESM families group coupled model configurations across generations (e.g. HadGEM3, CNRM-CM, CESM). A family ID is referenced by the final model record at Stage 4.",
    "Model_Components":               "**Stage 3.** Model components are specific versioned instances of model software — an atmosphere, ocean, sea-ice, or land-surface code at a specific version — bound to horizontal and vertical grids. Each produces a component config ID used in Stage 4.",
    "Models":                         "**Stage 4.** Model records assemble the complete coupled system: every component configuration, active/prescribed realms, coupling relationships, and the ESM family. This creates the official CMIP `source_id`.",
}


# ── helpers ────────────────────────────────────────────────────────────────────

def _get_id(item):
    vk = item.get("validation_key") or item.get("ui_label")
    if vk and str(vk).strip():
        return str(vk).strip()
    raw = item.get("@id", "")
    return raw.split("/")[-1].split(":")[-1] or "unknown"


def _extract_key_schema(items, max_depth=2):
    """
    Build a key-schema tree up to max_depth levels.
    At depth 1: top-level keys of the record.
    At depth 2: sub-keys of any linked / inline objects.
    Returns a D3-hierarchy-compatible dict.
    """
    def _node(obj, depth):
        if depth == 0 or not isinstance(obj, dict):
            return None
        children = []
        seen = set()
        for k, v in obj.items():
            if k.startswith("@"):
                continue
            name = k.split("/")[-1]
            if name in seen:
                continue
            seen.add(name)

            if isinstance(v, list) and v:
                first = v[0]
                if isinstance(first, dict) and "@value" not in first:
                    # list of linked objects — recurse
                    sub = _node(first, depth - 1)
                    if sub and sub.get("children"):
                        children.append({"name": name, "type": "links",
                                         "children": sub["children"]})
                    else:
                        children.append({"name": name, "type": "links"})
                else:
                    children.append({"name": name, "type": "list"})

            elif isinstance(v, dict):
                if "@value" in v:
                    children.append({"name": name, "type": "scalar"})
                else:
                    # inline or linked object — recurse
                    sub = _node(v, depth - 1)
                    if sub and sub.get("children"):
                        children.append({"name": name, "type": "link",
                                         "children": sub["children"]})
                    else:
                        children.append({"name": name, "type": "link"})
            else:
                children.append({"name": name, "type": "scalar"})

        return {"name": "record", "children": children} if children else None

    # Use the first item as the schema template
    if not items:
        return {"name": "record", "children": []}
    result = _node(items[0], max_depth)
    return result or {"name": "record", "children": []}


# ── average-linkage dendrogram ─────────────────────────────────────────────────

def _upgma_for_ordering(n, dist_matrix):
    """
    Builds a minimal UPGMA tree whose leaves carry their *original* index
    (0..n-1).  Used only to derive the matrix row order via DFS traversal.
    The DFS order of this tree = the order in which rows/columns appear in
    the final matrix, guaranteeing zero crossings in the dendrogram.
    """
    d = dist_matrix.astype(float).copy()
    np.fill_diagonal(d, np.inf)
    nodes  = [{"oi": i, "leaf": True} for i in range(n)]
    sizes  = [1] * n
    active = list(range(n))
    while len(active) > 1:
        best = np.inf; ai = 0; aj = 1
        for ii in range(len(active)):
            for jj in range(ii + 1, len(active)):
                v = d[active[ii], active[jj]]
                if v < best: best = v; ai = ii; aj = jj
        ci, cj = active[ai], active[aj]
        si, sj = sizes[ci], sizes[cj]
        new_node = {"leaf": False, "children": [nodes[ci], nodes[cj]]}
        new_idx  = len(nodes)
        nodes.append(new_node)
        sizes.append(si + sj)
        old   = len(d)
        new_d = np.full((old + 1, old + 1), np.inf)
        new_d[:old, :old] = d
        for k in active:
            if k in (ci, cj): continue
            nd = (si * d[ci, k] + sj * d[cj, k]) / (si + sj)
            new_d[new_idx, k] = nd
            new_d[k, new_idx] = nd
        d = new_d
        active.remove(ci); active.remove(cj); active.append(new_idx)
    return nodes[active[0]]


def _mcl_clusters(text_matrix, inflation=2.0, iterations=60):
    """
    Markov Clustering Algorithm (MCL) on the text/embedding similarity matrix.

    The text matrix is used (not the combined) because the link matrix for
    most record types has uniformly high values that prevent MCL from finding
    meaningful structure. The text/embedding matrix captures the numerical
    and semantic differences that actually distinguish items.

    Pruning threshold is set adaptively at the 50th percentile of non-zero
    off-diagonal values so the graph sparsity scales with the data.

    inflation controls granularity: higher → more, smaller clusters.
    The default 2.0 is the standard starting value.

    Returns an int array of length n with cluster IDs.
    """
    n = len(text_matrix)
    if n < 2:
        return np.zeros(n, dtype=int)

    # Adaptive pruning: keep only the top half of non-zero similarities
    M    = text_matrix.astype(float).copy()
    np.fill_diagonal(M, 0)
    nonzero = M[M > 0]
    prune   = float(np.percentile(nonzero, 50)) if len(nonzero) else 0.05
    prune   = max(0.05, prune)
    M[M < prune] = 0

    np.fill_diagonal(M, 1.0)  # self-loops keep every node reachable
    col = M.sum(axis=0, keepdims=True); col[col == 0] = 1; M /= col

    for _ in range(iterations):
        prev = M.copy()
        M    = M @ M                          # expand
        np.power(M, inflation, out=M)         # inflate
        col  = M.sum(axis=0, keepdims=True); col[col == 0] = 1; M /= col
        M[M < 1e-5] = 0                       # prune noise
        if np.max(np.abs(M - prev)) < 1e-4:
            break

    # Extract clusters from converged matrix.
    # Attractor nodes have M[i,i] > 0; members are nodes j with M[i,j] > 0.
    labels     = np.full(n, -1, dtype=int)
    cluster_id = 0
    for i in range(n):
        if M[i, i] > 0:
            for m in np.where(M[i, :] > 0)[0]:
                if labels[m] < 0:
                    labels[m] = cluster_id
            cluster_id += 1

    # Catch any unassigned nodes (rare) as singletons
    for i in range(n):
        if labels[i] < 0:
            labels[i] = cluster_id
            cluster_id += 1

    return labels


def _spectral_order_and_clusters(sim_matrix, n_clusters=None):
    """
    Graph-based clustering: threshold the similarity matrix at the 75th
    percentile of off-diagonal values, then find connected components.

    Items whose strongest similarity to any other item is below the
    threshold become singletons naturally — no item is forced into a group.

    Within each multi-item component the Fiedler vector (second eigenvector
    of the component's Laplacian) is used to give a smooth linear ordering.
    Components are then sorted largest-first so the dominant groups appear
    at the top-left of the matrix.

    Returns (order, cluster_labels) where:
      order          — permutation of 0..n-1 giving the final matrix row order
      cluster_labels — cluster ID for each item *in the returned order*
    """
    n = len(sim_matrix)
    if n < 2:
        return np.arange(n), np.zeros(n, dtype=int)

    # ── 1. Adaptive threshold: keep only the top 25% of similarities ──
    W = np.clip(sim_matrix, 0, 1).copy()
    np.fill_diagonal(W, 0)
    off = W[W > 0]
    threshold = float(np.percentile(off, 85)) if len(off) else 0.5

    adj = W > threshold

    # ── 2. Connected components (BFS) ────────────────────────────
    raw_labels = np.full(n, -1, dtype=int)
    cid = 0
    for start in range(n):
        if raw_labels[start] >= 0:
            continue
        stack = [start]
        while stack:
            node = stack.pop()
            if raw_labels[node] >= 0:
                continue
            raw_labels[node] = cid
            stack.extend(int(nb) for nb in np.where(adj[node] & (raw_labels < 0))[0])
        cid += 1

    # ── 3. Order within each component using Fiedler vector ─────────
    component_orders = []
    for c in range(cid):
        idx = np.where(raw_labels == c)[0]
        if len(idx) < 3:
            component_orders.append(idx.tolist())
            continue
        sub = W[np.ix_(idx, idx)]
        deg = sub.sum(axis=1)
        deg[deg == 0] = 1
        d = 1.0 / np.sqrt(deg)
        L = np.eye(len(idx)) - (d[:, None] * sub * d[None, :])
        _, evec = np.linalg.eigh(L)
        fiedler = evec[:, 1]          # second eigenvector = smoothest ordering
        local_order = np.argsort(fiedler)
        component_orders.append(idx[local_order].tolist())

    # ── 4. Sort components largest-first ────────────────────────────
    component_orders.sort(key=len, reverse=True)

    order = []
    cluster_labels = []
    new_cid = 0
    for comp in component_orders:
        order.extend(comp)
        cluster_labels.extend([new_cid] * len(comp))
        new_cid += 1

    return np.array(order, dtype=int), np.array(cluster_labels, dtype=int)
def _leaf_order(node):
    if node.get("leaf"):
        return [node["oi"]]
    result = []
    for child in node.get("children", []):
        result.extend(_leaf_order(child))
    return result


def _average_linkage_tree(labels, dist_matrix):
    """
    UPGMA on the *already-row-ordered* distance matrix.
    Because the row order was derived from _upgma_for_ordering + _leaf_order,
    the DFS traversal of this tree is guaranteed to be 0, 1, 2, …, n-1 —
    i.e. perfectly aligned with the matrix rows, zero dendrogram crossings.
    Each leaf carries spectral_index = its position in the final matrix.
    """
    n = len(labels)
    if n < 2:
        return {"name": labels[0] if labels else "?",
                "leaf": True, "spectral_index": 0, "value": 0.0}

    d = dist_matrix.astype(float).copy()
    np.fill_diagonal(d, np.inf)

    nodes = [{"name": labels[i], "leaf": True, "spectral_index": i, "value": 0.0}
             for i in range(n)]
    sizes = [1] * n
    active = list(range(n))

    while len(active) > 1:
        best = np.inf
        ai, aj = 0, 1
        for ii in range(len(active)):
            for jj in range(ii + 1, len(active)):
                v = d[active[ii], active[jj]]
                if v < best:
                    best, ai, aj = v, ii, jj

        ci, cj = active[ai], active[aj]
        si, sj = sizes[ci], sizes[cj]

        new_node = {"name": "", "leaf": False,
                    "children": [nodes[ci], nodes[cj]],
                    "value": float(best)}
        new_idx = len(nodes)
        nodes.append(new_node)
        sizes.append(si + sj)

        old   = len(d)
        new_d = np.full((old + 1, old + 1), np.inf)
        new_d[:old, :old] = d
        for k in active:
            if k in (ci, cj):
                continue
            nd = (si * d[ci, k] + sj * d[cj, k]) / (si + sj)
            new_d[new_idx, k] = nd
            new_d[k, new_idx] = nd
        d = new_d

        active.remove(ci)
        active.remove(cj)
        active.append(new_idx)

    return nodes[active[0]]


# ── similarity computation ─────────────────────────────────────────────────────

def _compute_matrices(items, ids, use_embeddings=True):
    n         = len(items)
    all_links = [extract_links(item) for item in items]
    link_raw  = np.array([
        [_jaccard(all_links[i], all_links[j]) if i != j else 0.0
         for j in range(n)]
        for i in range(n)
    ], dtype=float)

    off        = link_raw[~np.eye(n, dtype=bool)]
    link_degen = (off.size == 0 or float(off.std()) < 1e-6 or float(off.mean()) > 0.98)

    text_items  = [strip_text_fields(item) for item in items]
    text_method = "field-level"

    if use_embeddings:
        try:
            from sentence_transformers import SentenceTransformer  # noqa
            from cmipld.utils.similarity import JSONSimilarityFingerprint
            fp = JSONSimilarityFingerprint(include_keys=False)
            fp.load_from_dict({iid: ti for iid, ti in zip(ids, text_items)})
            fp.embed(show_progress=False)
            fp.compute_similarity()
            text_matrix = np.array(fp.similarity_matrix, dtype=float)
            np.fill_diagonal(text_matrix, 0.0)
            text_method = "embedding (all-MiniLM-L6-v2)"
        except Exception as exc:
            print(f"  \u26a0 Embeddings unavailable ({exc}), using field-level.", flush=True)
            text_matrix = _field_matrix(text_items, n)
    else:
        text_matrix = _field_matrix(text_items, n)

    if link_degen:
        # Links are uninformative — fall back to field-level similarity for
        # the upper triangle so it always differs from the embedding lower triangle.
        link_matrix = _field_matrix(text_items, n)
        link_label  = "field-level (links uninformative)"
    else:
        link_matrix = link_raw
        link_label  = "jaccard"

    return link_matrix, text_matrix, f"{text_method} | link: {link_label}"


def _field_matrix(text_items, n):
    return np.array([
        [compute_field_similarity(text_items[i], text_items[j])[0]
         if i != j else 0.0
         for j in range(n)]
        for i in range(n)
    ], dtype=float)


# ── Markdown + embedded HTML template ─────────────────────────────────────────
#
# Produces a .md file that MkDocs renders inside the site layout.
# The page content is a mix of markdown (title/description) and raw HTML
# blocks (visualisation).  Python-Markdown passes <script> / <style> /
# <div> blocks through unchanged.
#
# JS is wrapped in an IIFE to avoid global namespace pollution.
# All CSS classes use the "emd-" prefix to avoid theme conflicts.
# ──────────────────────────────────────────────────────────────────────────────

_MD_TEMPLATE = """\
# __TITLE__

__DESCRIPTION__

---

!!! info "Generated files"
    This page is auto-generated during the build from live registry data. Three files are produced for each record type:

    - **`__STEM__.md`** — this page, embedded in the MkDocs site layout
    - **`__STEM___data.json`** — processed similarity matrices, dendrogram tree, and key schema
    - **`__STEM___raw.json`** — raw JSON-LD records as fetched from the cmipld registry (depth 2)

---

<link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;600;700&family=Pacifico&display=swap" rel="stylesheet">

<style>
.emd-viz { font-family: 'Source Code Pro', monospace; width: 100%; }
.emd-section { margin-bottom: 2.5rem; }
.emd-section-label {
  font-size: 11px; font-weight: 700; color: #0d1035;
  text-transform: uppercase; letter-spacing: 0.09em;
  margin-bottom: 12px; display: block;
}
.emd-selector-row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
#emd-entry-select {
  flex: 1; min-width: 240px; padding: 8px 12px;
  border: 1.5px solid #ccc; border-radius: 6px;
  font-family: 'Source Code Pro', monospace; font-size: 12px;
  color: #0d1035; background: #fff; cursor: pointer;
}
#emd-entry-select:focus { outline: none; border-color: #0d1035; }
#emd-go-btn {
  padding: 8px 18px; border: 1.5px solid #0d1035; border-radius: 6px;
  background: #0d1035; color: #fff;
  font-family: 'Source Code Pro', monospace; font-size: 12px;
  font-weight: 600; cursor: pointer; transition: background .15s;
}
#emd-go-btn:hover { background: #1a2080; }
.emd-stats {
  margin-top: 10px; font-size: 11px; color: #888;
  display: flex; gap: 20px; flex-wrap: wrap;
}
.emd-stats b { color: #0d1035; }
.emd-filter-bar { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.emd-fbtn {
  padding: 4px 11px; border-radius: 20px; border: 1.5px solid #ccc;
  background: #fff; cursor: pointer; font-family: 'Source Code Pro', monospace;
  font-size: 11px; color: #555; transition: all .15s;
}
.emd-fbtn:hover  { border-color: #0d1035; color: #0d1035; }
.emd-fbtn.active { background: #0d1035; border-color: #0d1035; color: #fff; font-weight: 600; }
.emd-tip {
  position: fixed; background: #0d1035; color: #fff;
  padding: 10px 14px; border-radius: 8px; font-size: 12px;
  font-family: 'Source Code Pro', monospace; pointer-events: none;
  opacity: 0; transition: opacity .12s; line-height: 1.9;
  box-shadow: 0 6px 24px rgba(0,0,0,.25); max-width: 280px; z-index: 999;
}
.emd-tip-link { color: #e8607e; font-weight: 600; }
.emd-tip-text { color: #f5c842; font-weight: 600; }
.emd-tip-head { font-weight: 700; font-size: 13px;
  border-bottom: 1px solid rgba(255,255,255,.2); padding-bottom: 5px; margin-bottom: 5px; }
/* ── font toggle ── */
.emd-font-btn {
  padding: 5px 12px; border-radius: 20px; border: 1.5px solid #ccc;
  background: #fff; font-size: 11px; cursor: pointer;
  font-family: 'Source Code Pro', monospace; color: #888;
  transition: all .2s; white-space: nowrap;
}
.emd-font-btn:hover { border-color: #a060c0; color: #602080; }
.emd-font-btn.active { background: #f3e8ff; border-color: #a060c0;
  color: #602080; font-family: 'Pacifico', cursive; }
.emd-viz.pretty svg text { font-family: 'Pacifico', cursive !important; }
.emd-viz.pretty #emd-entry-select,
.emd-viz.pretty .emd-stats,
.emd-viz.pretty .emd-section-label { font-family: 'Pacifico', cursive !important; }
</style>

<div class="emd-viz">

<div class="emd-section">
<span class="emd-section-label">View a specific __SINGULAR__</span>
<div class="emd-selector-row">
  <select id="emd-entry-select">
    <option value="">Select an entry\u2026</option>
__OPTIONS__
  </select>
  <button id="emd-go-btn" onclick="emdGotoEntry()">Open \u2192</button>
  <button class="emd-font-btn" id="emd-font-toggle" onclick="emdToggleFont()">✨ Pretty font</button>
</div>
<div class="emd-stats">
  <span><b>__N__</b> registered entries</span>
  <span>Endpoint: <b>__ENDPOINT__</b></span>
</div>
</div>

<div class="emd-section">
<span class="emd-section-label">Similarity &amp; Hierarchical Clustering</span>
<div class="emd-filter-bar" id="emd-filter-bar"></div>
<div id="emd-combined-chart" style="overflow-x:auto; display:flex; justify-content:center;"></div>
<div class="emd-tip" id="emd-tip"></div>
</div>

<div class="emd-section">
<span class="emd-section-label">Record Key Schema</span>
<div id="emd-key-graph"></div>
</div>

</div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
(function () {
'use strict';

/* ── injected data ─────────────────────────────────────────────────────── */
var EMD_DATA    = __DATA__;
var EMD_ENTRIES = __ENTRIES__;
var EMD_SCHEMA  = __SCHEMA__;

var ids         = EMD_DATA.ids;
var link        = EMD_DATA.link;
var text        = EMD_DATA.text;
var method      = EMD_DATA.method;
var meta        = EMD_DATA.meta;
var tree        = EMD_DATA.tree;
var clusters    = EMD_DATA.clusters || ids.map(function() { return 0; });
var group_spans = EMD_DATA.group_spans || [];  /* [[start_row, end_row], ...] per group */
var n           = ids.length;

/* Cluster colour palette — 20 distinct monotone colours */
var CLUSTER_COLORS = [
  '#1565c0','#b71c1c','#1b5e20','#4a148c','#e65100',
  '#006064','#3e2723','#37474f','#880e4f','#33691e',
  '#0d47a1','#bf360c','#1a237e','#01579b','#004d40',
  '#f57f17','#4e342e','#263238','#6a1b9a','#827717'
];
function clusterColor(k) {
  return CLUSTER_COLORS[k % CLUSTER_COLORS.length];
}

var FONT    = "'Source Code Pro', monospace";
var RED     = '#a40e4c';
var MUSTARD = '#f2b30d';
var NAVY    = '#0d1035';
var WHITE   = '#ffffff';

/* ── entry selector ────────────────────────────────────────────────────── */
window.emdGotoEntry = function () {
  var v = document.getElementById('emd-entry-select').value;
  if (v) window.location.href = v;
};

/* ── filter buttons ────────────────────────────────────────────────────── */
var allTags = Array.from(new Set(meta.flatMap(function (m) { return m.tags || []; }))).sort();
var activeFilter = null;

function itemVisible(i) {
  return !activeFilter || (meta[i].tags || []).indexOf(activeFilter) >= 0;
}

var matG, dendG;   // assigned below; needed by applyFilter

function applyFilter() {
  if (!matG) return;
  matG.selectAll('.emd-cell').attr('opacity', function (d) {
    if (d.i === d.j) return itemVisible(d.i) ? 1 : 0.08;
    return (itemVisible(d.i) && itemVisible(d.j)) ? 1 : 0.06;
  });
  matG.selectAll('.emd-val').attr('opacity', function (d) {
    return (itemVisible(d.i) && itemVisible(d.j)) ? 1 : 0;
  });
  matG.selectAll('.emd-diag').attr('opacity', function (d, i) { return itemVisible(i) ? 1 : 0.1; });
  matG.selectAll('.emd-xlabel').attr('opacity', function (d, i) { return itemVisible(i) ? 1 : 0.1; });
  matG.selectAll('.emd-ylabel').attr('opacity', function (d, i) { return itemVisible(i) ? 1 : 0.1; });
}

if (allTags.length > 0) {
  var bar = document.getElementById('emd-filter-bar');
  var allBtn = document.createElement('button');
  allBtn.className = 'emd-fbtn active'; allBtn.textContent = 'All';
  allBtn.onclick = function () {
    activeFilter = null;
    document.querySelectorAll('.emd-fbtn').forEach(function (b) { b.classList.remove('active'); });
    allBtn.classList.add('active'); applyFilter();
  };
  bar.appendChild(allBtn);
  allTags.forEach(function (tag) {
    var btn = document.createElement('button');
    btn.className = 'emd-fbtn';
    btn.textContent = tag.replace(/[-_]/g, ' ');
    btn.onclick = function () {
      activeFilter = tag;
      document.querySelectorAll('.emd-fbtn').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active'); applyFilter();
    };
    bar.appendChild(btn);
  });
}

/* ── font toggle ──────────────────────────────────────────────────────── */
window.emdToggleFont = function () {
  var viz = document.querySelector('.emd-viz');
  var btn = document.getElementById('emd-font-toggle');
  viz.classList.toggle('pretty');
  btn.classList.toggle('active');
};

/* ── layout constants ──────────────────────────────────────────────────── */
var cellSize = Math.min(60, Math.floor(Math.min(window.innerWidth * 0.65, 440) / n));
var gap      = Math.max(2, Math.round(cellSize * 0.055));
var inner    = cellSize - gap;
var rad      = Math.round(inner * 0.14);
var lblFs    = Math.max(8, Math.round(cellSize * 0.145));
var maxLLen  = Math.max.apply(null, meta.map(function (m) { return Math.min(m.label.length, 50); }));
var XLBL_H   = Math.ceil(maxLLen * lblFs * 0.62) + 12;
var YLBL_W   = Math.ceil(maxLLen * lblFs * 0.62) + 16;
var LEG_H    = 62;
var DEND_W   = Math.max(30, Math.round(n * cellSize * 0.09));  /* compact right-side dendrogram */
var matW     = n * cellSize;
var margin   = { top: 30, right: DEND_W + 8, bottom: XLBL_H + LEG_H + 16, left: YLBL_W };
var totalW   = matW + margin.left + margin.right;
var totalH   = matW + margin.top + margin.bottom;

/* ── root SVG ──────────────────────────────────────────────────────────── */
var svg = d3.select('#emd-combined-chart').append('svg')
  .attr('width', totalW).attr('height', totalH);

var defs = svg.append('defs');
[['emd-leg-red', RED], ['emd-leg-mustard', MUSTARD]].forEach(function (pair) {
  var gr = defs.append('linearGradient').attr('id', pair[0]).attr('x1','0%').attr('x2','100%');
  gr.append('stop').attr('offset','0%').attr('stop-color', WHITE);
  gr.append('stop').attr('offset','100%').attr('stop-color', pair[1]);
});

/* Clip the dendrogram to its column */
defs.append('clipPath').attr('id','emd-dend-clip')
  .append('rect').attr('x', 0).attr('y', 0).attr('width', DEND_W).attr('height', matW);

/* Matrix is at left; dendrogram is to the RIGHT of the matrix */
matG = svg.append('g')
  .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

dendG = svg.append('g')
  .attr('transform', 'translate(' + (margin.left + matW) + ',' + margin.top + ')')
  .attr('clip-path', 'url(#emd-dend-clip)');

/* ── colour helpers ────────────────────────────────────────────────────── */
function hexToRgb(h) {
  return [parseInt(h.slice(1,3),16)/255, parseInt(h.slice(3,5),16)/255, parseInt(h.slice(5,7),16)/255];
}
function blend(hex, a) {
  var c = hexToRgb(hex);
  return 'rgb(' + Math.round((1-a+c[0]*a)*255) + ',' +
                  Math.round((1-a+c[1]*a)*255) + ',' +
                  Math.round((1-a+c[2]*a)*255) + ')';
}

/* ── method subtitle ───────────────────────────────────────────────────── */
svg.append('text')
  .attr('x', margin.left + matW / 2).attr('y', margin.top - 12)
  .attr('text-anchor','middle').attr('font-family', FONT).attr('font-size', 9).attr('fill','#aaa')
  .text(n + ' items  \xb7  UPGMA leaf order  \xb7  ' + method);

/* ── similarity matrix ─────────────────────────────────────────────────── */
var cellData = [];
for (var i = 0; i < n; i++) for (var j = 0; j < n; j++) cellData.push({i: i, j: j});

var tip = d3.select('#emd-tip');

/* Show cluster boxes only while the mouse is over the matrix */
d3.select('#emd-combined-chart')
  .on('mouseenter.cluster', function () {
    matG.selectAll('.emd-cluster-box').attr('opacity', 0.8);
  })
  .on('mouseleave.cluster', function () {
    matG.selectAll('.emd-cluster-box').attr('opacity', 0);
  });

/* ── cluster background fills (drawn before cells so they sit behind) ──── */
(function () {
  var runs = [];
  var start = 0;
  for (var i = 1; i <= n; i++) {
    if (i === n || clusters[i] !== clusters[start]) {
      runs.push({ k: clusters[start], start: start, end: i - 1 });
      start = i;
    }
  }
  var clusterSize = {};
  clusters.forEach(function (c) { clusterSize[c] = (clusterSize[c] || 0) + 1; });

  runs.forEach(function (r) {
    if (clusterSize[r.k] < 2) return;
    var x  = r.start * cellSize;
    var sz = (r.end - r.start + 1) * cellSize;
    matG.append('rect')
      .attr('class', 'emd-cluster-box')
      .attr('x', x).attr('y', x)
      .attr('width', sz).attr('height', sz)
      .attr('fill', 'none')
      .attr('stroke', clusterColor(r.k))
      .attr('stroke-width', 2)
      .attr('rx', rad + 1)
      .attr('pointer-events', 'none')
      .attr('opacity', 0);
  });
}());

matG.selectAll('.emd-cell').data(cellData).join('rect')
  .attr('class','emd-cell')
  .attr('x', function (d) { return d.j * cellSize + gap / 2; })
  .attr('y', function (d) { return d.i * cellSize + gap / 2; })
  .attr('width', inner).attr('height', inner).attr('rx', rad)
  .attr('fill', function (d) {
    if (d.i === d.j) return NAVY;
    return d.i < d.j ? blend(RED, link[d.i][d.j]) : blend(MUSTARD, text[d.i][d.j]);
  })
  .style('cursor', function (d) { return d.i === d.j ? 'default' : 'pointer'; })
  .on('mouseover', function (event, d) {
    if (d.i === d.j) return;
    var li = Math.min(d.i, d.j), lj = Math.max(d.i, d.j);
    tip.style('opacity', 1).html(
      '<div class="emd-tip-head">' + meta[d.i].label + ' \u2194 ' + meta[d.j].label + '</div>' +
      '<span class="emd-tip-link">\u25b2 Link similarity</span>&nbsp;' + (link[li][lj]*100).toFixed(1) + '%<br>' +
      '<span class="emd-tip-text">\u25bc Embeddings</span>&nbsp;' + (text[lj][li]*100).toFixed(1) + '%'
    );
    d3.select(this).attr('stroke', NAVY).attr('stroke-width', 2);
    matG.selectAll('.emd-cell').filter(function (e) { return e.i !== d.i && e.j !== d.j; })
      .attr('opacity', function (e) { return (itemVisible(e.i) && itemVisible(e.j)) ? 0.35 : 0.04; });
  })
  .on('mousemove', function (ev) {
    tip.style('left', (ev.clientX + 14) + 'px').style('top', (ev.clientY - 10) + 'px');
  })
  .on('mouseout', function () {
    tip.style('opacity', 0); d3.select(this).attr('stroke', 'none'); applyFilter();
  });

var maxDiagFs = Math.max(9, Math.round(cellSize * 0.18));
function diagText(label) {
  for (var fs = maxDiagFs; fs >= 6; fs--) {
    var mc = Math.floor(inner / (0.58 * fs));
    if (label.length <= mc) return {fs: fs, t: label};
  }
  var mc2 = Math.floor(inner / (0.58 * 6));
  return {fs: 6, t: label.slice(0, Math.max(1, mc2 - 1)) + '\u2026'};
}

matG.selectAll('.emd-val').data(cellData.filter(function (d) { return d.i !== d.j; })).join('text')
  .attr('class','emd-val')
  .attr('x', function (d) { return d.j * cellSize + cellSize / 2; })
  .attr('y', function (d) { return d.i * cellSize + cellSize / 2; })
  .attr('dy','0.35em').attr('text-anchor','middle')
  .attr('font-family', FONT).attr('font-size', Math.max(8, Math.round(cellSize * 0.16)))
  .attr('font-weight', 600).attr('pointer-events','none')
  .attr('fill', function (d) {
    var v = d.i < d.j ? link[d.i][d.j] : text[d.i][d.j];
    if (v < 0.08) return 'none';
    var c = hexToRgb(d.i < d.j ? RED : MUSTARD);
    return (0.299*(1-v+c[0]*v) + 0.587*(1-v+c[1]*v) + 0.114*(1-v+c[2]*v)) < 0.55 ? WHITE : NAVY;
  })
  .text(function (d) {
    var v = d.i < d.j ? link[d.i][d.j] : text[d.i][d.j];
    return v >= 0.08 ? Math.round(v * 100) + '%' : '';
  });

/* ── cluster legend ────────────────────────────────────────────────────── */
(function () {
  var clusterSize = {};
  clusters.forEach(function (c) { clusterSize[c] = (clusterSize[c] || 0) + 1; });
  var shownClusters = Object.keys(clusterSize)
    .map(Number)
    .filter(function (k) { return clusterSize[k] >= 2; })
    .sort(function (a, b) { return a - b; });
  var legY2 = matW + XLBL_H + LEG_H + 28;
  var legFs2 = Math.max(9, Math.round(cellSize * 0.14));
  var dot = legFs2 + 2;
  var lx = 0;
  shownClusters.forEach(function (k, idx) {
    matG.append('rect')
      .attr('x', lx).attr('y', legY2)
      .attr('width', dot).attr('height', dot)
      .attr('rx', 2)
      .attr('fill', clusterColor(k));
    matG.append('text')
      .attr('x', lx + dot + 4).attr('y', legY2 + dot - 2)
      .attr('font-family', FONT).attr('font-size', legFs2)
      .attr('fill', NAVY)
      .text('Group ' + (idx + 1));
    lx += dot + 70;
  });
}());

matG.selectAll('.emd-diag').data(meta).join('text')
  .attr('class','emd-diag')
  .attr('x', function (d, i) { return i * cellSize + cellSize / 2; })
  .attr('y', function (d, i) { return i * cellSize + cellSize / 2; })
  .attr('dy','0.35em').attr('text-anchor','middle')
  .attr('font-family', FONT).attr('font-size', function (d) { return diagText(d.label).fs; })
  .attr('font-weight', 700).attr('fill', WHITE).attr('pointer-events','none')
  .text(function (d) { return diagText(d.label).t; });

var pivotY = matW + 4;
matG.selectAll('.emd-xlabel').data(meta).join('text')
  .attr('class','emd-xlabel')
  .attr('transform', function (d, i) {
    return 'translate(' + (i * cellSize + cellSize / 2) + ',' + pivotY + ') rotate(-90)';
  })
  .attr('text-anchor','end').attr('dy','0.35em')
  .attr('font-family', FONT).attr('font-size', lblFs).attr('font-weight', 600).attr('fill', NAVY)
  .text(function (d) { return d.label.length > 50 ? d.label.slice(0,50) + '\u2026' : d.label; });

matG.selectAll('.emd-ylabel').data(meta).join('text')
  .attr('class','emd-ylabel').attr('x', -6)
  .attr('y', function (d, i) { return i * cellSize + cellSize / 2; })
  .attr('text-anchor','end').attr('dominant-baseline','middle')
  .attr('font-family', FONT).attr('font-size', lblFs).attr('font-weight', 600).attr('fill', NAVY)
  .text(function (d) { return d.label.length > 50 ? d.label.slice(0,50) + '\u2026' : d.label; });

matG.append('line')
  .attr('x1',0).attr('y1',0).attr('x2',matW).attr('y2',matW)
  .attr('stroke', NAVY).attr('stroke-width', 1.5).attr('stroke-dasharray','5,4').attr('opacity',0.22);

/* ── upper / lower triangle corner labels ──────────────────────────────── */
/* These make explicit that the two triangles show different metrics. */
var triFs = Math.max(8, Math.round(cellSize * 0.13));
var pad   = Math.max(6, Math.round(cellSize * 0.18));
/* Upper-right: link / field-level label (from method string) */
var upperLabel = (method.indexOf('field-level') >= 0 && method.indexOf('jaccard') < 0)
  ? 'field similarity' : 'link similarity';
matG.append('text')
  .attr('x', matW - pad).attr('y', pad + triFs)
  .attr('text-anchor','end').attr('font-family', FONT)
  .attr('font-size', triFs).attr('font-weight', 700).attr('fill', RED).attr('opacity', 0.75)
  .text(upperLabel);
/* Lower-left: text / embedding label */
matG.append('text')
  .attr('x', pad).attr('y', matW - pad)
  .attr('text-anchor','start').attr('font-family', FONT)
  .attr('font-size', triFs).attr('font-weight', 700).attr('fill', MUSTARD).attr('opacity', 0.75)
  .text('embeddings');

/* ── legend ────────────────────────────────────────────────────────────── */
var legY  = matW + XLBL_H + 16;
var barW  = Math.floor(matW * 0.43);
var barH  = 13;
var legFs = Math.max(9, Math.round(cellSize * 0.16));

matG.append('text').attr('x',0).attr('y',legY-8)
  .attr('font-family',FONT).attr('font-size',legFs).attr('font-weight',700).attr('fill',RED)
  .text('\u25b2  link similarity (upper)');
matG.append('rect').attr('x',0).attr('y',legY).attr('width',barW).attr('height',barH)
  .attr('rx',3).attr('fill','url(#emd-leg-red)');
matG.append('text').attr('x',0).attr('y',legY+barH+9)
  .attr('font-size',legFs-1).attr('fill','#bbb').attr('font-family',FONT).text('0%');
matG.append('text').attr('x',barW).attr('y',legY+barH+9).attr('text-anchor','end')
  .attr('font-size',legFs-1).attr('fill','#bbb').attr('font-family',FONT).text('100%');

var mustX = matW - barW;
matG.append('text').attr('x',mustX).attr('y',legY-8)
  .attr('font-family',FONT).attr('font-size',legFs).attr('font-weight',700).attr('fill','#c49000')
  .text('\u25bc  embeddings (lower)');
matG.append('rect').attr('x',mustX).attr('y',legY).attr('width',barW).attr('height',barH)
  .attr('rx',3).attr('fill','url(#emd-leg-mustard)');
matG.append('text').attr('x',mustX).attr('y',legY+barH+9)
  .attr('font-size',legFs-1).attr('fill','#bbb').attr('font-family',FONT).text('0%');
matG.append('text').attr('x',mustX+barW).attr('y',legY+barH+9).attr('text-anchor','end')
  .attr('font-size',legFs-1).attr('fill','#bbb').attr('font-family',FONT).text('100%');

/* ── dendrogram (orthogonal, spectral-ordered leaves) ──────────────────── */
(function () {
  var root = d3.hierarchy(tree);

  /* max merge distance for x-scaling */
  var maxDist = 0;
  root.each(function (d) { if (d.data.value > maxDist) maxDist = d.data.value; });
  if (maxDist < 1e-9) maxDist = 1;

  /* 1. y-positions: each leaf represents a GROUP, not an individual item.
        Pin each leaf to the vertical centre of its group's matrix block.
        spectral_index in the group-level tree = group index (0-based, in
        the order groups appear as rows in the matrix).
        Falls back to uniform spacing if group_spans is not populated. */
  function assignY(node) {
    if (!node.children) {
      var gi  = node.spectral_index || 0;
      var span = group_spans[gi];
      if (span) {
        /* centre of the group block */
        node.dendY = (span[0] + span[1]) / 2 * cellSize + cellSize / 2;
      } else {
        node.dendY = gi * cellSize + cellSize / 2;
      }
    } else {
      node.children.forEach(assignY);
      node.dendY = (node.children[0].dendY + node.children[node.children.length-1].dendY) / 2;
    }
  }
  assignY(root);

  /* 2. x-positions for RIGHT-SIDE dendrogram:
        Leaf x = 2  (touching matrix right edge = left edge of dendG)
        Root x = DEND_W-2  (rightmost — furthest from matrix)
        Internal nodes: scaled by merge distance — larger distance → further right */
  function assignX(node) {
    if (!node.children) {
      node.dendX = 2;
    } else {
      /* distance 0 → x=2 (at matrix), distance=maxDist → x=DEND_W-2 (far right) */
      node.dendX = node.data.value / maxDist * (DEND_W - 4) + 2;
      node.children.forEach(assignX);
    }
  }
  assignX(root);

  /* 3. Collect parent→child pairs */
  var links = [];
  root.each(function (d) {
    if (d.children) d.children.forEach(function (c) { links.push({src: d, tgt: c}); });
  });

  /* Annotate each node with the majority cluster of its leaf subtree.
     Used to colour branches: a branch is the cluster colour when all
     leaves below share the same cluster AND that cluster is not a singleton.
     Grey when mixed or all singletons. */
  var clusterSizeD = {};
  clusters.forEach(function (c) { clusterSizeD[c] = (clusterSizeD[c] || 0) + 1; });

  root.each(function (d) {
    var leaves = d.leaves();
    var clusterSet = {};
    leaves.forEach(function (l) {
      var ci = clusters[l.data.spectral_index || 0];
      clusterSet[ci] = (clusterSet[ci] || 0) + 1;
    });
    var keys = Object.keys(clusterSet);
    var singleCluster = (keys.length === 1) ? parseInt(keys[0]) : -1;
    /* Only assign a clique colour if the cluster has more than 1 item total */
    d._clique = (singleCluster >= 0 && clusterSizeD[singleCluster] >= 2)
      ? singleCluster : -1;
  });

  /* 4. Orthogonal elbow paths: M px,py V cy H cx
        Parent (further right) → vertical to child’s y → horizontal left to child.
        Coloured by cluster when the entire subtree belongs to one cluster. */
  dendG.selectAll('.emd-dend-branch')
    .data(links.filter(function (d) { return d.tgt._clique >= 0; })).join('path')
    .attr('class','emd-dend-branch')
    .attr('fill','none')
    .attr('stroke', function (d) {
      var k = d.tgt._clique;
      return k >= 0 ? clusterColor(k) : '#888';
    })
    .attr('stroke-width', function (d) { return d.tgt._clique >= 0 ? 1.8 : 0.9; })
    .attr('opacity', function (d) { return d.tgt._clique >= 0 ? 0.6 : 0.25; })
    .attr('d', function (d) {
      return 'M ' + d.src.dendX + ',' + d.src.dendY +
             ' V ' + d.tgt.dendY +
             ' H ' + d.tgt.dendX;
    });

  /* 5. No dashed connectors needed: leaves are already pinned to the
        centre of their group block in the matrix. */

  /* No leaf labels — rows are already labelled by the matrix y-axis */

  /* 6. Internal node dots — only within-cluster nodes */
  root.each(function (d) {
    if (!d.children || d._clique < 0) return;
    dendG.append('circle')
      .attr('cx', d.dendX).attr('cy', d.dendY).attr('r', 1.8)
      .attr('fill', WHITE).attr('stroke', NAVY).attr('stroke-width', 1).attr('opacity', 0.65);
  });
}());

/* ── key schema radial graph ───────────────────────────────────────────── */
(function () {
  var w  = Math.min(window.innerWidth - 48, 720);
  var h  = Math.max(360, Math.round(w * 0.6));
  var cx = w / 2, cy = h / 2;
  var R  = Math.min(cx, cy) - 90;

  var root = d3.hierarchy(EMD_SCHEMA).sum(function () { return 1; });

  var treeLayout = d3.tree()
    .size([2 * Math.PI, R])
    .separation(function (a, b) { return (a.parent === b.parent ? 1 : 1.5) / a.depth; });
  treeLayout(root);

  var svg2 = d3.select('#emd-key-graph').append('svg').attr('width', w).attr('height', h);
  var g2   = svg2.append('g').attr('transform', 'translate(' + cx + ',' + cy + ')');

  /* Radial curved links */
  g2.selectAll('.emd-klink')
    .data(root.links()).join('path')
    .attr('class','emd-klink')
    .attr('fill','none').attr('stroke', NAVY).attr('stroke-width', 1.1).attr('opacity', 0.3)
    .attr('d', d3.linkRadial().angle(function (d) { return d.x; }).radius(function (d) { return d.y; }));

  var typeColor = { scalar: NAVY, link: RED, links: RED, list: MUSTARD };

  var knode = g2.selectAll('.emd-knode')
    .data(root.descendants()).join('g')
    .attr('class','emd-knode')
    .attr('transform', function (d) {
      return 'rotate(' + (d.x * 180 / Math.PI - 90) + ') translate(' + d.y + ',0)';
    });

  knode.append('circle')
    .attr('r', function (d) { return d.depth === 0 ? 6 : (d.depth === 1 ? 4 : 3); })
    .attr('fill', function (d) { return d.depth === 0 ? NAVY : (typeColor[d.data.type] || NAVY); })
    .attr('stroke', WHITE).attr('stroke-width', 1);

  knode.append('text')
    .attr('dy','0.31em')
    .attr('x', function (d) { return d.x < Math.PI === !d.children ? 8 : -8; })
    .attr('text-anchor', function (d) { return d.x < Math.PI === !d.children ? 'start' : 'end'; })
    .attr('transform', function (d) { return d.x >= Math.PI ? 'rotate(180)' : null; })
    .attr('font-family', FONT)
    .attr('font-size', function (d) { return d.depth === 0 ? 11 : (d.depth === 1 ? 9 : 8); })
    .attr('font-weight', function (d) { return d.depth <= 1 ? 600 : 400; })
    .attr('fill', function (d) { return d.depth === 0 ? NAVY : (typeColor[d.data.type] || '#555'); })
    .text(function (d) { return d.data.name; });

  /* Legend */
  var legItems = [
    {label: 'Scalar field',       col: NAVY},
    {label: 'Linked record',      col: RED},
    {label: 'List / multi-value', col: MUSTARD},
  ];
  var legG = svg2.append('g').attr('transform', 'translate(12,' + (h - 58) + ')');
  legItems.forEach(function (item, idx) {
    legG.append('circle').attr('cx',6).attr('cy', idx*17+6).attr('r',4).attr('fill', item.col);
    legG.append('text').attr('x',16).attr('y', idx*17+10)
      .attr('font-family',FONT).attr('font-size',9).attr('fill','#666').text(item.label);
  });
}());

}());
</script>
"""


# ── page builder ───────────────────────────────────────────────────────────────

def _build_page(stem, items, ordered_labels, ordered_ids, ordered_tags,
                link_ordered, text_ordered, cluster_labels, method_str, repo_subdir):

    n = len(ordered_ids)

    # ── Group-level dendrogram ────────────────────────────────────────────────────
    # Build one UPGMA leaf per group, not per item.
    # Inter-group distance = average pairwise distance of their members.
    # group_spans[g] = [start_row, end_row] of group g in the matrix.
    combined_sim = (link_ordered + text_ordered) / 2
    np.fill_diagonal(combined_sim, 0.0)
    dist = 1.0 - np.clip(combined_sim, 0, 1)

    unique_groups = sorted(set(cluster_labels.tolist()))
    k = len(unique_groups)

    # Map group id -> list of item row indices
    group_rows = {g: [i for i, c in enumerate(cluster_labels) if c == g]
                  for g in unique_groups}
    # Row spans [start, end] for the JS
    group_spans = [[min(rows), max(rows)] for g in unique_groups
                   for rows in [group_rows[g]]]

    if k >= 2:
        # k×k average-linkage distance matrix between groups
        gdist = np.zeros((k, k))
        for ai, gi in enumerate(unique_groups):
            for aj, gj in enumerate(unique_groups):
                if ai == aj:
                    continue
                ri, rj = group_rows[gi], group_rows[gj]
                gdist[ai, aj] = dist[np.ix_(ri, rj)].mean()

        # Labels for group nodes: use first member’s label as representative
        group_labels = [ordered_labels[group_rows[g][0]] for g in unique_groups]
        tree = _average_linkage_tree(group_labels, gdist)
    else:
        # Single group — trivial tree
        tree = {"name": ordered_labels[0], "leaf": True,
                "spectral_index": 0, "value": 0.0}

    # Key schema (2 levels deep)
    schema = _extract_key_schema(items, max_depth=2)

    singular = SINGULAR_NAMES.get(stem, stem.replace("_", " ").rstrip("s"))

    # Entry URLs: page is at /EMD_Repository/{stem}/ so siblings are at ../{stem}/{id}/
    # Actually page IS in EMD_Repository so entries are at {id}/ relative
    entries = [
        {"label": ordered_labels[i], "url": "../" + repo_subdir + "/" + ordered_ids[i] + "/"}
        for i in range(n)
    ]

    meta = [{"label": ordered_labels[i], "tags": ordered_tags[i]} for i in range(n)]

    options_html = "\n".join(
        '    <option value="../' + repo_subdir + "/" + eid + '/">' + label + '</option>'
        for eid, label in zip(ordered_ids, ordered_labels)
    )

    payload = json.dumps({
        "ids":         ordered_ids,
        "link":        link_ordered.tolist(),
        "text":        text_ordered.tolist(),
        "method":      method_str,
        "folder":      stem.replace("_", " "),
        "meta":        meta,
        "tree":        tree,
        "clusters":    cluster_labels.tolist(),
        "group_spans": group_spans,
    }, separators=(",", ":"))

    title       = stem.replace("_", " ")
    description = DESCRIPTIONS.get(stem, "")

    return (
        _MD_TEMPLATE
        .replace("__TITLE__",    title)
        .replace("__DESCRIPTION__", description)
        .replace("__STEM__",     stem)
        .replace("__SINGULAR__", singular)
        .replace("__N__",        str(n))
        .replace("__ENDPOINT__", ENDPOINT_OVERRIDES.get(stem, stem))
        .replace("__OPTIONS__",  options_html)
        .replace("__DATA__",     payload)
        .replace("__ENTRIES__",  json.dumps(entries, separators=(",", ":")))
        .replace("__SCHEMA__",   json.dumps(schema,  separators=(",", ":")))
    )


def _build_data_json(stem, items, ordered_labels, ordered_ids,
                     link_ordered, text_ordered, method_str, tree, schema):
    """Raw data snapshot written alongside the .md page."""
    n = len(ordered_ids)
    return {
        "stem":     stem,
        "singular": SINGULAR_NAMES.get(stem, stem),
        "endpoint": ENDPOINT_OVERRIDES.get(stem, stem),
        "count":    n,
        "method":   method_str,
        "entries":  [
            {"id": ordered_ids[i], "label": ordered_labels[i], "spectral_rank": i}
            for i in range(n)
        ],
        "link_matrix": link_ordered.tolist(),
        "text_matrix": text_ordered.tolist(),
        "dendrogram":  tree,
        "schema":      schema,
    }


# ── main ───────────────────────────────────────────────────────────────────────

def run(use_embeddings=True):
    init_loader()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ok = skipped = failed = 0
    _cache: dict[str, list] = {}

    for stem in STAGE_ORDER:
        endpoint    = ENDPOINT_OVERRIDES[stem]
        repo_subdir = REPO_DIR_MAP.get(stem, stem)
        md_path     = OUT_DIR / f"{stem}.md"
        data_path   = OUT_DIR / f"{stem}_data.json"
        raw_path    = OUT_DIR / f"{stem}_raw.json"

        print(f"\n{'─'*60}", flush=True)
        print(f"  Stem     : {stem}", flush=True)
        print(f"  Endpoint : {endpoint}", flush=True)
        print(f"  MD       : {md_path.relative_to(REPO_ROOT)}", flush=True)
        print(f"  Data     : {data_path.relative_to(REPO_ROOT)}", flush=True)

        if endpoint not in _cache:
            print(f"  Fetching {endpoint}\u2026", flush=True)
            _cache[endpoint] = fetch_data(endpoint, depth=2)

        items = list(_cache[endpoint])
        print(f"  Fetched  : {len(items)} items", flush=True)

        pf = PRE_FILTER.get(stem)
        if pf:
            from cmipld.utils.similarity.folder_similarity import _get_field_value
            items = [it for it in items if _get_field_value(it, pf[0]) == pf[1]]
            print(f"  Filtered : {len(items)} items ({pf[0]}={pf[1]})", flush=True)

        # Write raw cmipld JSON immediately after fetching/filtering
        raw_path.write_text(json.dumps(items, indent=2), encoding="utf-8")
        print(f"  \u2705 Raw JSON ({raw_path.stat().st_size // 1024} KB)", flush=True)

        if len(items) < 2:
            print(f"  \u23ed  Skipped \u2014 need \u2265 2 items (got {len(items)})", flush=True)
            skipped += 1
            continue

        try:
            labels = [_get_label(it) for it in items]
            ids    = [_get_id(it)    for it in items]
            tags   = [_get_tags(it, FILTER_FIELD[stem]) if stem in FILTER_FIELD else []
                      for it in items]

            link_m, text_m, method_str = _compute_matrices(
                items, ids, use_embeddings=use_embeddings)

            # ── Graph-based spectral clustering ────────────────────────────────
            # Threshold the combined similarity at the 75th percentile,
            # find connected components (singletons allowed naturally),
            # order within each component by the Fiedler vector.
            n_items   = len(items)
            combined0 = (link_m + text_m) / 2
            np.fill_diagonal(combined0, 0.0)

            spec_order, cluster_labels = _spectral_order_and_clusters(combined0)

            ordered_labels = [labels[i] for i in spec_order]
            ordered_ids    = [ids[i]    for i in spec_order]
            ordered_tags   = [tags[i]   for i in spec_order]

            link_ordered = link_m[np.ix_(spec_order, spec_order)]
            text_ordered = text_m[np.ix_(spec_order, spec_order)]

            method_str_display = method_str + " | order: spectral graph components"

            schema = _extract_key_schema(items, max_depth=2)

            # Write .md page
            md_content = _build_page(
                stem, items,
                ordered_labels, ordered_ids, ordered_tags,
                link_ordered, text_ordered, cluster_labels, method_str_display,
                repo_subdir,
            )
            md_path.write_text(md_content, encoding="utf-8")
            print(f"  \u2705 MD written  ({md_path.stat().st_size // 1024} KB)", flush=True)

            # Write data JSON
            data_payload = _build_data_json(
                stem, items, ordered_labels, ordered_ids,
                link_ordered, text_ordered, method_str_display, tree, schema,
            )
            data_path.write_text(
                json.dumps(data_payload, indent=2), encoding="utf-8")
            print(f"  \u2705 JSON written ({data_path.stat().st_size // 1024} KB)", flush=True)

            ok += 1

        except ValueError as e:
            print(f"  \u23ed  Skipped \u2014 {e}", flush=True)
            skipped += 1
        except Exception as e:
            import traceback
            print(f"  \u274c Failed  \u2014 {e}", flush=True)
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*60}", flush=True)
    print(f"  Similarity  \u2705 {ok}  \u23ed {skipped}  \u274c {failed}", flush=True)
    print(f"{'='*60}\n", flush=True)
    if failed:
        print(f"  \u26a0 {failed} page(s) failed \u2014 build continues.", flush=True)


run()
