#!/usr/bin/env python3
"""
generate_similarity.py
======================
For every configured record type, generate:

  docs/EMD_Repository/{stem}.md           — MkDocs page (appears in site nav)
  docs/EMD_Repository/{stem}_data.json    — raw data snapshot

Each .md page embeds an integrated visualisation:
  1. "View a specific <X>" dropdown + summary stats (count, file sizes,
     last-updated timestamp)
  2. Dendrogram (UPGMA on spectrally-ordered similarity, orthogonal branches)
     fused left-to-right with the adjacency/similarity matrix — one SVG.
     The matrix grows to occupy up to 3/4 of the container width.
  3. Horizontal key-schema tree (2 levels deep, includes linked-object sub-keys).
     The synthetic root is suppressed; nodes carry type badges (value/link/list).

Dendrogram leaf order == spectral order of the similarity matrix; every leaf
is pinned to the y-centre of its matrix row.  Branches are orthogonal
(right-angle elbow paths: M px,py V cy H cx).

Dependencies: numpy>=1.24.0, cmipld (via helpers.data_loader)
"""

import json
import sys
from datetime import datetime, timezone
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

def _format_size(num_bytes):
    """Format a byte count as a human-readable string (KB / MB)."""
    if num_bytes is None:
        return "—"
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes / (1024 * 1024):.2f} MB"


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

        return {"name": "", "children": children} if children else None

    # Use the first item as the schema template
    if not items:
        return {"name": "", "children": []}
    result = _node(items[0], max_depth)
    return result or {"name": "", "children": []}


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

<link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;600;700&display=swap" rel="stylesheet">

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
/* ── accessible font toggle ── */
.emd-font-btn {
  padding: 5px 12px; border-radius: 20px; border: 1.5px solid #ccc;
  background: #fff; font-size: 11px; cursor: pointer;
  font-family: 'Source Code Pro', monospace; color: #888;
  transition: all .2s; white-space: nowrap;
}
.emd-font-btn:hover { border-color: #2065a0; color: #1a4a80; }
.emd-font-btn.active { background: #e8f0ff; border-color: #2065a0;
  color: #1a4a80; font-family: inherit; font-weight: 600; }
/* Accessible mode: also switch the UI controls (the SVGs are already on the
   accessible/sans-serif font by default via the JS `FONT` constant). */
.emd-viz.accessible { font-family: inherit; }
.emd-viz.accessible #emd-entry-select,
.emd-viz.accessible .emd-stats,
.emd-viz.accessible .emd-stats-grid,
.emd-viz.accessible .emd-stat-label,
.emd-viz.accessible .emd-stat-value,
.emd-viz.accessible .emd-section-label,
.emd-viz.accessible .emd-fbtn,
.emd-viz.accessible #emd-go-btn { font-family: inherit !important; }
/* ── stats grid ── */
.emd-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin: 10px 0 18px;
  padding: 14px 16px;
  background: #f7f8fa;
  border-left: 3px solid #0d1035;
  border-radius: 4px;
}
.emd-stat-item { display: flex; flex-direction: column; gap: 3px; }
.emd-stat-label {
  font-family: 'Source Code Pro', monospace;
  color: #888; font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.06em;
}
.emd-stat-value {
  font-family: 'Source Code Pro', monospace;
  color: #0d1035; font-weight: 600; font-size: 13px;
}
</style>

<div class="emd-viz">

<!-- Status / stats box pinned to the top of the page -->
<div class="emd-stats-grid">
  <div class="emd-stat-item">
    <span class="emd-stat-label">Total Records</span>
    <span class="emd-stat-value">__N__</span>
  </div>
  <div class="emd-stat-item">
    <span class="emd-stat-label">Endpoint</span>
    <span class="emd-stat-value">__ENDPOINT__</span>
  </div>
  <div class="emd-stat-item">
    <span class="emd-stat-label">Raw Data</span>
    <span class="emd-stat-value">__RAW_SIZE__</span>
  </div>
  <div class="emd-stat-item">
    <span class="emd-stat-label">Processed Data</span>
    <span class="emd-stat-value">__DATA_SIZE__</span>
  </div>
  <div class="emd-stat-item">
    <span class="emd-stat-label">Last Updated</span>
    <span class="emd-stat-value">__LAST_UPDATED__</span>
  </div>
</div>

<div class="emd-section">
<span class="emd-section-label">View a specific __SINGULAR__</span>
<div class="emd-selector-row">
  <select id="emd-entry-select">
    <option value="">Select an entry\u2026</option>
__OPTIONS__
  </select>
  <button id="emd-go-btn" onclick="emdGotoEntry()">Open \u2192</button>
  <button class="emd-font-btn" id="emd-font-toggle" onclick="emdToggleFont()" title="Switch to the page's default font for improved readability">Accessible font</button>
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

var FONT    = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
var FONT_MONO = "'Source Code Pro', monospace";
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

/* ── accessible font toggle ──────────────────────────────────────────── */
window.emdToggleFont = function () {
  var viz = document.querySelector('.emd-viz');
  var btn = document.getElementById('emd-font-toggle');
  viz.classList.toggle('accessible');
  btn.classList.toggle('active');
};

/* ── layout constants ──────────────────────────────────────────────────── */
/* Matrix grows to occupy up to 3/4 of the available container/SVG width. */
var containerEl = document.querySelector('.emd-viz');
var containerW  = (containerEl && containerEl.clientWidth) || window.innerWidth * 0.85;
var availMatW   = containerW * 0.75;
var cellSize    = Math.min(80, Math.floor(availMatW / n));
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

/* ── key schema horizontal tree ────────────────────────────────────────
   Cleaner left-to-right layout (replaces the previous radial graph).
   The root node ("record") is suppressed — its children represent the
   schema's top-level keys directly. Type-colour-coded nodes with
   compact badges show whether each key is a scalar, link, or list. */
(function () {
  var schemaData = EMD_SCHEMA || {};
  var topLevel   = (schemaData.children || []);
  if (!topLevel.length) {
    d3.select('#emd-key-graph').append('div')
      .style('color', '#888').style('font-size', '12px')
      .style('font-family', FONT).style('padding', '20px 0')
      .text('No schema fields available for this record type.');
    return;
  }

  /* Wrap the real children under a synthetic root so d3.tree() works,
     but we will *never* render the synthetic root. */
  var hierData = {name: '', children: topLevel};
  var rootH    = d3.hierarchy(hierData);

  /* Count leaves to size the SVG height. */
  var leaves = rootH.leaves().length;
  var rowH   = 24;
  var topPad = 18, botPad = 70;
  var h      = Math.max(280, leaves * rowH + topPad + botPad);

  /* Width: use container, fall back to viewport. Reserve room for labels. */
  var contW = (containerEl && containerEl.clientWidth) || window.innerWidth - 48;
  var w     = Math.min(contW, 820);

  var leftPad = 16;
  var labelReserve = 220;  /* horizontal space reserved for labels on the right */

  var svg2 = d3.select('#emd-key-graph').append('svg')
    .attr('width', w).attr('height', h)
    .style('overflow', 'visible');

  var tree = d3.tree()
    .size([h - topPad - botPad, w - leftPad - labelReserve])
    .separation(function (a, b) { return a.parent === b.parent ? 1 : 1.3; });
  tree(rootH);

  var g2 = svg2.append('g')
    .attr('transform', 'translate(' + leftPad + ',' + topPad + ')');

  var typeColor = { scalar: NAVY, link: RED, links: RED, list: MUSTARD };
  var typeLabel = { scalar: 'value', link: 'link',  links: 'links', list: 'list' };

  /* Links — but skip the edges from the synthetic root, draw a short
     vertical anchor line on the left instead. */
  g2.selectAll('.emd-klink')
    .data(rootH.links().filter(function (d) { return d.source.depth > 0; }))
    .join('path')
    .attr('class','emd-klink')
    .attr('fill','none').attr('stroke', NAVY).attr('stroke-width', 1.1).attr('opacity', 0.28)
    .attr('d', d3.linkHorizontal()
      .x(function (d) { return d.y; })
      .y(function (d) { return d.x; }));

  /* Anchor line + ticks from a virtual rail to each depth-1 node. */
  var depth1 = rootH.descendants().filter(function (d) { return d.depth === 1; });
  if (depth1.length > 1) {
    var railX = depth1[0].y - 18;
    var yMin  = d3.min(depth1, function (d) { return d.x; });
    var yMax  = d3.max(depth1, function (d) { return d.x; });
    g2.append('line')
      .attr('x1', railX).attr('x2', railX)
      .attr('y1', yMin).attr('y2', yMax)
      .attr('stroke', NAVY).attr('stroke-width', 1.5).attr('opacity', 0.35);
    depth1.forEach(function (d) {
      g2.append('line')
        .attr('x1', railX).attr('x2', d.y)
        .attr('y1', d.x).attr('y2', d.x)
        .attr('stroke', NAVY).attr('stroke-width', 1.1).attr('opacity', 0.28);
    });
  }

  /* Nodes — skip the synthetic root. */
  var nodes = rootH.descendants().filter(function (d) { return d.depth > 0; });

  var knode = g2.selectAll('.emd-knode')
    .data(nodes).join('g')
    .attr('class','emd-knode')
    .attr('transform', function (d) { return 'translate(' + d.y + ',' + d.x + ')'; });

  knode.append('circle')
    .attr('r', function (d) { return d.depth === 1 ? 5 : 3.5; })
    .attr('fill', function (d) { return typeColor[d.data.type] || NAVY; })
    .attr('stroke', WHITE).attr('stroke-width', 1.5);

  /* Field name label */
  knode.append('text')
    .attr('x', 10).attr('dy', '0.32em')
    .attr('font-family', FONT)
    .attr('font-size', function (d) { return d.depth === 1 ? 11 : 10; })
    .attr('font-weight', function (d) { return d.depth === 1 ? 600 : 400; })
    .attr('fill', NAVY)
    .text(function (d) { return d.data.name; });

  /* Type badge to the right of the label */
  knode.each(function (d) {
    if (!d.data.type) return;
    var label = typeLabel[d.data.type] || d.data.type;
    var nameLen = (d.data.name || '').length;
    var bx = 10 + nameLen * (d.depth === 1 ? 6.4 : 5.8) + 8;
    var bw = label.length * 5.5 + 10;
    var sel = d3.select(this);
    sel.append('rect')
      .attr('x', bx).attr('y', -7)
      .attr('width', bw).attr('height', 14).attr('rx', 7)
      .attr('fill', typeColor[d.data.type] || NAVY).attr('opacity', 0.12);
    sel.append('text')
      .attr('x', bx + bw / 2).attr('y', 0).attr('dy', '0.32em')
      .attr('text-anchor', 'middle')
      .attr('font-family', FONT).attr('font-size', 8)
      .attr('font-weight', 600)
      .attr('fill', typeColor[d.data.type] || NAVY)
      .text(label);
  });

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

# ──────────────────────────────────────────────────────────────────────────────
# Dynamic view-page template.  One of these is generated per record type
# (e.g. view_horizontal_grid_cells.md). It reads ?id=<entry_id> from the URL,
# fetches the sibling {stem}_raw.json (already recursively populated to
# depth=2 by this script), and renders the matching entry as a clean card
# layout — scalars in a property table, linked records as tag-style buttons
# that link onward to their own view pages.
#
# The page is hidden from navigation (set to -1 in nav_order.json).
# ──────────────────────────────────────────────────────────────────────────────

_VIEW_TEMPLATE = """\
---
title: View __SINGULAR__
hide:
  - navigation
  - toc
search:
  exclude: true
---

# __SINGULAR__ Viewer

<style>
.emd-view { width: 100%; font-family: inherit; }
.emd-view-loading,
.emd-view-error {
  padding: 28px; text-align: center; color: #666;
  border: 1px dashed #ccc; border-radius: 6px; margin: 18px 0;
}
.emd-view-error { color: #a40e4c; border-color: #f3c4d2; background: #fff7fa; }
.emd-view-back {
  display: inline-block; margin-bottom: 16px;
  font-size: 12px; color: #1a4a80; text-decoration: none;
  font-family: 'Source Code Pro', monospace;
}
.emd-view-back:hover { text-decoration: underline; }
.emd-view-header { margin-bottom: 22px; padding-bottom: 18px; border-bottom: 1px solid #e4e6ec; }
.emd-view-badge {
  display: inline-block; padding: 3px 10px; border-radius: 999px;
  background: #e8f0ff; color: #1a4a80; font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.08em;
  font-family: 'Source Code Pro', monospace; margin-bottom: 10px;
}
.emd-view-title { font-size: 1.6rem; font-weight: 700; color: #0d1035; margin: 0 0 6px; }
.emd-view-id    { font-family: 'Source Code Pro', monospace; font-size: 12px; color: #888; }
.emd-view-desc  { color: #444; line-height: 1.65; margin: 12px 0 0; font-size: 0.95rem; }

.emd-view-stat-row {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px; margin: 18px 0;
}
.emd-view-stat {
  background: #f7f8fa; border-left: 3px solid #0d1035;
  border-radius: 4px; padding: 10px 14px;
}
.emd-view-stat-label {
  font-family: 'Source Code Pro', monospace; color: #888;
  font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em;
  margin-bottom: 3px;
}
.emd-view-stat-value {
  font-family: 'Source Code Pro', monospace; color: #0d1035;
  font-weight: 600; font-size: 14px;
}

.emd-view-section { margin: 26px 0; }
.emd-view-section-title {
  font-family: 'Source Code Pro', monospace;
  font-size: 11px; font-weight: 700; color: #0d1035;
  text-transform: uppercase; letter-spacing: 0.09em;
  margin-bottom: 10px;
}

.emd-view-prop-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.emd-view-prop-table tr { border-bottom: 1px solid #eef0f4; }
.emd-view-prop-table tr:last-child { border-bottom: none; }
.emd-view-prop-table td { padding: 9px 12px; vertical-align: top; }
.emd-view-prop-table td:first-child {
  font-family: 'Source Code Pro', monospace;
  font-weight: 600; color: #555; font-size: 0.78rem;
  text-transform: uppercase; letter-spacing: 0.04em;
  width: 32%; white-space: nowrap;
}
.emd-view-prop-table td:last-child { color: #222; word-break: break-word; }
.emd-view-prop-table code {
  font-family: 'Source Code Pro', monospace; font-size: 0.85em;
  background: #f3f4f8; padding: 1px 5px; border-radius: 3px;
}

.emd-view-tag {
  display: inline-block; padding: 3px 10px; margin: 2px 4px 2px 0;
  border-radius: 14px; font-size: 11px;
  background: #f3f4f8; color: #333; border: 1px solid #e4e6ec;
}
.emd-view-tag.link { background: #fff0f4; color: #a40e4c; border-color: #f3c4d2; }
.emd-view-tag a { color: inherit; text-decoration: none; }
.emd-view-tag a:hover { text-decoration: underline; }
.emd-view-list-item { margin-bottom: 4px; }
.emd-view-link-card {
  display: inline-block; padding: 8px 12px; margin: 4px 6px 4px 0;
  border: 1px solid #e4e6ec; border-radius: 6px;
  background: #fafbfd; text-decoration: none; color: #0d1035;
  font-size: 0.85rem; min-width: 120px;
}
.emd-view-link-card:hover { background: #e8f0ff; border-color: #1a4a80; }
.emd-view-link-card-id { font-family: 'Source Code Pro', monospace; color: #888; font-size: 10px; display: block; }
.emd-view-link-card-name { color: #0d1035; font-weight: 600; }

.emd-view-json-toggle {
  margin: 28px 0 8px;
  border: 1px solid #e4e6ec; border-radius: 6px; padding: 10px 14px;
  background: #fafbfd; font-size: 0.85rem; cursor: pointer;
}
.emd-view-json-toggle summary {
  font-family: 'Source Code Pro', monospace;
  font-weight: 600; color: #555; outline: none;
}
.emd-view-json-toggle pre {
  margin: 10px 0 0; padding: 12px; background: #0d1035; color: #d4d9ff;
  border-radius: 4px; overflow-x: auto; font-size: 0.78rem; line-height: 1.5;
}

/* ───────────────────────────────────────────────────────────────
   Rich "cells" — based on the deactivated jinja templates.
   These are the per-record-type boxes populated by the JS renderers.
   ─────────────────────────────────────────────────────────────── */

/* "What is this?" plain-language callout */
.emd-view-callout {
  background: #f0f5ff; border-left: 4px solid #1a4a80;
  padding: 14px 18px; margin: 18px 0; border-radius: 4px;
  font-size: 0.95rem; line-height: 1.65; color: #2a2e3e;
}
.emd-view-callout strong { color: #1a4a80; }

/* Hero stat tiles (big numbers across the top) */
.emd-view-hero-stats {
  display: flex; flex-wrap: wrap; gap: 12px; margin: 18px 0;
}
.emd-view-hero-stat {
  flex: 1 1 130px; background: #fff; border: 1px solid #e4e6ec;
  border-radius: 6px; padding: 14px 16px; text-align: center;
  min-width: 130px;
}
.emd-view-hero-stat-value {
  font-family: 'Source Code Pro', monospace;
  font-size: 1.5rem; font-weight: 800; color: #1a4a80;
  line-height: 1.1; margin-bottom: 4px;
}
.emd-view-hero-stat-value.small { font-size: 0.95rem; padding-top: 4px; }
.emd-view-hero-stat-label {
  font-family: 'Source Code Pro', monospace;
  font-size: 10px; font-weight: 700; color: #888;
  text-transform: uppercase; letter-spacing: 0.07em;
}

/* Section box (replaces the bare h2 + table) */
.emd-view-box {
  margin: 22px 0; border: 1px solid #e4e6ec; border-radius: 8px;
  background: #fff; overflow: hidden;
}
.emd-view-box-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; cursor: pointer;
  background: linear-gradient(180deg, #fafbfd 0%, #f3f4f8 100%);
  border-bottom: 1px solid #e4e6ec;
  user-select: none; transition: background 0.15s;
}
.emd-view-box-header:hover { background: #f0f3fa; }
.emd-view-box-title {
  font-family: 'Source Code Pro', monospace;
  font-size: 12px; font-weight: 700; color: #0d1035;
  text-transform: uppercase; letter-spacing: 0.07em;
  display: flex; align-items: center; gap: 10px;
}
.emd-view-box-title .emd-view-box-icon {
  width: 18px; height: 18px; opacity: 0.7;
}
.emd-view-box-count {
  font-weight: 400; color: #888; font-size: 11px; margin-left: 6px;
}
.emd-view-box-chevron {
  color: #888; transition: transform 0.2s; font-size: 11px;
}
.emd-view-box.collapsed .emd-view-box-chevron { transform: rotate(-90deg); }
.emd-view-box.collapsed .emd-view-box-body { display: none; }
.emd-view-box-body { padding: 16px; }

/* Domain pill (colored badge for component domains) */
.emd-view-domain-pill {
  display: inline-flex; align-items: center;
  padding: 4px 12px; border-radius: 999px;
  font-family: 'Source Code Pro', monospace;
  font-size: 11px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.05em;
  margin-bottom: 10px;
  border: 1.5px solid #1a4a80; color: #1a4a80; background: #e8f0ff;
}
.emd-view-domain-pill.atmosphere       { border-color:#3490dc; color:#3490dc; background:#eaf4fd; }
.emd-view-domain-pill.ocean            { border-color:#1565c0; color:#1565c0; background:#e3f2fd; }
.emd-view-domain-pill.land-surface     { border-color:#7b6f43; color:#7b6f43; background:#f5efe0; }
.emd-view-domain-pill.sea-ice          { border-color:#0288d1; color:#0288d1; background:#e1f5fe; }
.emd-view-domain-pill.land-ice         { border-color:#5e35b1; color:#5e35b1; background:#ede7f6; }
.emd-view-domain-pill.aerosol          { border-color:#d84315; color:#d84315; background:#fbe9e7; }
.emd-view-domain-pill.atmospheric-chemistry  { border-color:#558b2f; color:#558b2f; background:#f1f8e9; }
.emd-view-domain-pill.ocean-biogeochemistry  { border-color:#00695c; color:#00695c; background:#e0f2f1; }

/* References list (clickable DOI/URL items) */
.emd-view-references { display: flex; flex-direction: column; gap: 8px; }
.emd-view-reference {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border: 1px solid #e4e6ec; border-radius: 6px;
  background: #fafbfd; text-decoration: none; color: #1a4a80;
  font-size: 0.85rem; transition: all 0.15s;
}
.emd-view-reference:hover { background: #f0f5ff; border-color: #1a4a80; }
.emd-view-reference-text { flex: 1; font-family: 'Source Code Pro', monospace; word-break: break-all; }
.emd-view-reference-arrow { color: #888; font-size: 1rem; }

/* Tag rows (lists of CV values) */
.emd-view-tag-row { display: flex; flex-wrap: wrap; gap: 6px; }
.emd-view-tag-row .emd-view-tag-pill {
  display: inline-block; padding: 4px 11px; border-radius: 999px;
  font-size: 11px; border: 1px solid #d6d9e0; color: #555;
  background: #fafbfd;
}
.emd-view-tag-row .emd-view-tag-pill.primary {
  border-color: #1a4a80; color: #1a4a80; background: #e8f0ff;
}

/* Code-base / source-repo display (mixed-content row) */
.emd-view-code-base {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 12px; border-radius: 6px;
  background: #f3f4f8; font-family: 'Source Code Pro', monospace;
  font-size: 0.82rem; color: #444;
}
.emd-view-code-base.private { background: #fff2e8; color: #b54708; }
.emd-view-code-base.public a { color: #1a4a80; text-decoration: none; }
.emd-view-code-base.public a:hover { text-decoration: underline; }

/* Sub-label / explainer text inside a box */
.emd-view-explainer {
  margin-top: 10px; font-size: 0.85rem; color: #666; line-height: 1.6;
}

/* Tech details — small grid for @id, validation_key, types */
.emd-view-tech-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}
.emd-view-tech-item {
  background: #fafbfd; border: 1px solid #eef0f4;
  border-radius: 4px; padding: 10px 12px;
}
.emd-view-tech-label {
  font-family: 'Source Code Pro', monospace;
  font-size: 10px; font-weight: 700; color: #888;
  text-transform: uppercase; letter-spacing: 0.06em;
  margin-bottom: 4px;
}
.emd-view-tech-value {
  font-family: 'Source Code Pro', monospace;
  font-size: 0.82rem; color: #222; word-break: break-all;
}
.emd-view-tech-value a { color: #1a4a80; text-decoration: none; }
.emd-view-tech-value a:hover { text-decoration: underline; }
.emd-view-type-badges { display: flex; flex-wrap: wrap; gap: 4px; }
.emd-view-type-badge {
  font-family: 'Source Code Pro', monospace;
  font-size: 10px; padding: 2px 7px; border-radius: 4px;
  background: #e8f0ff; color: #1a4a80; font-weight: 600;
}

/* Linked-record cards (used in family links, component configs) */
.emd-view-record-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
}
</style>

<!-- JSON-LD recursive expansion library (graceful no-op if unavailable) -->
<script src="https://cdn.jsdelivr.net/npm/jsonld-recursive@1/lib/ldr-core.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jsonld-recursive@1/lib/ldr-browser.js"></script>

<div class="emd-view">
  <a class="emd-view-back" href="../__STEM__/">\u2190 Back to all __TITLE_PLURAL__</a>
  <div id="emd-view-content">
    <div class="emd-view-loading">Loading entry\u2026</div>
  </div>
</div>

<script>
(function () {
  'use strict';

  var STEM       = "__STEM__";
  var SINGULAR   = "__SINGULAR__";
  var BADGE_TEXT = SINGULAR;
  var STAT_KEYS  = __STAT_KEYS__;       /* JSON list */
  var LINK_TYPES = __LINK_TYPES__;      /* JSON map: field name -> view-page stem */

  var params  = new URLSearchParams(window.location.search);
  var entryId = (params.get('id') || '').trim();
  var contentEl = document.getElementById('emd-view-content');

  if (!entryId) {
    contentEl.innerHTML =
      '<div class="emd-view-error">No entry ID specified.<br>' +
      'Add <code>?id=&lt;identifier&gt;</code> to the URL.</div>';
    return;
  }

  /* JSON sits next to the summary page at ../<stem>_raw.json.
     Build & log the absolute URL so any 404 is trivially diagnosable. */
  var jsonRelUrl = '../' + STEM + '_raw.json';
  var jsonAbsUrl = new URL(jsonRelUrl, window.location.href).href;

  console.group('[EMD view] ' + STEM);
  console.log('Stem        :', STEM);
  console.log('Singular    :', SINGULAR);
  console.log('Entry ID    :', entryId);
  console.log('Page URL    :', window.location.href);
  console.log('Fetching    :', jsonRelUrl);
  console.log('Resolved to :', jsonAbsUrl);
  console.groupEnd();

  /* CMIP7-experiments-style fetch:
     1. Plain fetch() first for guaranteed baseline.
     2. If jsonld-recursive loaded, upgrade to JsonLdExpand.compact(URL, {depth:2}).
     3. Graceful fallback on any failure.
     4. Normalise: accept array | {contents:[...]} | {@graph:[...]}. */
  (async function loadData() {
    try {
      console.log('[EMD view] Fetching raw:', jsonAbsUrl);
      var r = await fetch(jsonAbsUrl);
      if (!r.ok) {
        throw new Error('HTTP ' + r.status + ' ' + r.statusText + ' \u2014 ' + jsonAbsUrl);
      }
      var raw = await r.json();
      console.log('[EMD view] Raw JSON:', raw);

      var res = raw;
      if (window.JsonLdExpand) {
        try {
          console.log('[EMD view] Compacting via JsonLdExpand (depth=2)...');
          res = await JsonLdExpand.compact(jsonAbsUrl, { depth: 2 });
          console.log('[EMD view] Compacted result:', res);
        } catch (e) {
          console.warn('[EMD view] JsonLdExpand failed, falling back to raw:', e);
          res = raw;
        }
      } else {
        console.log('[EMD view] JsonLdExpand library not loaded \u2014 using raw JSON.');
      }

      var items;
      if (Array.isArray(res))                  items = res;
      else if (Array.isArray(res.contents))    items = res.contents;
      else if (Array.isArray(res['@graph']))   items = res['@graph'];
      else                                     items = [];

      console.log('[EMD view] Loaded', items.length, 'items from', STEM + '_raw.json');

      var entry = findEntry(items, entryId);
      if (!entry) {
        console.warn('[EMD view] Entry not found:', entryId,
                     '\u2014 available ids:', items.map(function (it) { return bestId(it); }));
        contentEl.innerHTML =
          '<div class="emd-view-error">' +
            'No entry with id <code>' + escapeHtml(entryId) + '</code> in ' +
            '<code>' + escapeHtml(STEM) + '_raw.json</code>.<br>' +
            '<small>Available ids logged to browser console.</small>' +
          '</div>';
        return;
      }
      console.log('[EMD view] Rendering entry:', bestLabel(entry));
      renderEntry(entry);
    } catch (err) {
      console.error('[EMD view] Fetch failed:', err);
      contentEl.innerHTML =
        '<div class="emd-view-error">' +
          '<strong>Failed to load entry data.</strong><br>' +
          '<small>URL: <code>' + escapeHtml(jsonAbsUrl) + '</code></small><br>' +
          '<small>Error: ' + escapeHtml(err.message) + '</small>' +
        '</div>';
    }
  }());

  /* ── helpers ─────────────────────────────────────────────── */

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function lastSeg(s) {
    if (!s) return '';
    s = String(s);
    var idx = Math.max(s.lastIndexOf('/'), s.lastIndexOf(':'));
    return idx >= 0 ? s.slice(idx + 1) : s;
  }

  function findEntry(items, id) {
    if (!Array.isArray(items)) return null;
    var lower = id.toLowerCase();
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      if (!it || typeof it !== 'object') continue;
      var candidates = [
        it.validation_key,
        it.ui_label,
        it['@id'],
        lastSeg(it['@id']),
        it.name
      ].map(function (x) { return x == null ? '' : String(x).toLowerCase(); });
      if (candidates.indexOf(lower) >= 0) return it;
    }
    return null;
  }

  function bestLabel(entry) {
    if (!entry || typeof entry !== 'object') return String(entry || '');
    return entry.name || entry.ui_label || entry.validation_key ||
           lastSeg(entry['@id']) || '(unnamed)';
  }

  function bestId(entry) {
    if (!entry || typeof entry !== 'object') return String(entry || '');
    return entry.validation_key || lastSeg(entry['@id']) || '';
  }

  function isNoneVal(v) {
    if (v === null || v === undefined) return true;
    if (typeof v === 'string') {
      var s = v.trim().toLowerCase();
      return s === '' || s === 'none' || s === 'null' || s === 'n/a' || s === './';
    }
    if (Array.isArray(v)) return v.length === 0;
    return false;
  }

  function formatKey(k) {
    return String(k).replace(/[_-]/g, ' ')
      .replace(/\\b\\w/g, function (c) { return c.toUpperCase(); });
  }

  function viewUrlFor(field, id) {
    var targetStem = LINK_TYPES[field];
    if (!targetStem) return null;
    return '../view_' + targetStem.toLowerCase() + '/?id=' + encodeURIComponent(id);
  }

  /* ── value renderer ─────────────────────────────────────────── */

  function renderValue(field, value) {
    if (isNoneVal(value)) return '<span style="color:#aaa">\u2014</span>';

    /* Linked-object renderer */
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      if ('@value' in value) return escapeHtml(String(value['@value']));
      var label = bestLabel(value);
      var id    = bestId(value);
      var href  = viewUrlFor(field, id);
      if (href) {
        return '<a class="emd-view-link-card" href="' + href + '">' +
          '<span class="emd-view-link-card-name">' + escapeHtml(label) + '</span>' +
          '<span class="emd-view-link-card-id">' + escapeHtml(id) + '</span>' +
        '</a>';
      }
      return '<span class="emd-view-tag link">' + escapeHtml(label) +
        (id && id !== label ? ' <code>(' + escapeHtml(id) + ')</code>' : '') + '</span>';
    }

    /* Array — render each item */
    if (Array.isArray(value)) {
      if (!value.length) return '<span style="color:#aaa">\u2014</span>';
      return value.map(function (v) {
        return '<div class="emd-view-list-item">' + renderValue(field, v) + '</div>';
      }).join('');
    }

    /* URLs become clickable links */
    var s = String(value);
    if (/^https?:\\/\\//i.test(s)) {
      return '<a href="' + escapeHtml(s) + '" target="_blank" rel="noopener">' +
             escapeHtml(s) + '</a>';
    }

    /* Bare string that names a sibling record — also link it. */
    var href = viewUrlFor(field, s);
    if (href) {
      return '<a class="emd-view-tag link" href="' + href + '">' + escapeHtml(s) + '</a>';
    }

    /* Numbers shown in code style for visual contrast */
    if (typeof value === 'number') {
      return '<code>' + escapeHtml(s) + '</code>';
    }
    return escapeHtml(s);
  }

  /* ── reusable building-block cells ────────────────────────────────────
     These produce the rich boxes you see in the deactivated jinja
     templates: hero stats, plain-language callouts, collapsible sections,
     property tables, tag rows, reference lists, code-base displays,
     domain pills, and tech-details grids. */

  function box(title, bodyHtml, opts) {
    opts = opts || {};
    if (!bodyHtml) return '';
    var count = (opts.count != null)
      ? ' <span class="emd-view-box-count">(' + escapeHtml(String(opts.count)) + ')</span>'
      : '';
    var cls = 'emd-view-box' + (opts.collapsed ? ' collapsed' : '');
    return '<section class="' + cls + '">' +
      '<div class="emd-view-box-header" onclick="this.parentElement.classList.toggle(\\'collapsed\\')">' +
        '<div class="emd-view-box-title">' + escapeHtml(title) + count + '</div>' +
        '<div class="emd-view-box-chevron">\u25be</div>' +
      '</div>' +
      '<div class="emd-view-box-body">' + bodyHtml + '</div>' +
    '</section>';
  }

  function heroStat(label, value, opts) {
    opts = opts || {};
    var vCls = 'emd-view-hero-stat-value' + (opts.small ? ' small' : '');
    return '<div class="emd-view-hero-stat">' +
      '<div class="' + vCls + '">' + escapeHtml(String(value)) + '</div>' +
      '<div class="emd-view-hero-stat-label">' + escapeHtml(label) + '</div>' +
    '</div>';
  }

  function heroStatRow(stats) {
    if (!stats || !stats.length) return '';
    return '<div class="emd-view-hero-stats">' +
      stats.map(function (s) { return heroStat(s.label, s.value, s); }).join('') +
    '</div>';
  }

  function propRow(label, valueHtml) {
    if (valueHtml == null || valueHtml === '') return '';
    return '<tr><td>' + escapeHtml(label) + '</td><td>' + valueHtml + '</td></tr>';
  }

  function propTable(rows) {
    var inner = rows.filter(function (r) { return r; }).join('');
    if (!inner) return '';
    return '<table class="emd-view-prop-table">' + inner + '</table>';
  }

  function callout(html) {
    return '<div class="emd-view-callout">' + html + '</div>';
  }

  function tagRow(items, opts) {
    if (!items) return '';
    var list = Array.isArray(items) ? items : [items];
    list = list.filter(function (t) { return !isNoneVal(t); });
    if (!list.length) return '';
    opts = opts || {};
    var pillCls = 'emd-view-tag-pill' + (opts.primary ? ' primary' : '');
    return '<div class="emd-view-tag-row">' +
      list.map(function (t) {
        var name = (typeof t === 'object' && t) ? bestLabel(t) : String(t);
        var id   = (typeof t === 'object' && t) ? bestId(t)    : name;
        var href = opts.viewField ? viewUrlFor(opts.viewField, id) : null;
        var inner = href
          ? '<a href="' + escapeHtml(href) + '" style="color:inherit;text-decoration:none">' + escapeHtml(name) + '</a>'
          : escapeHtml(name);
        return '<span class="' + pillCls + '">' + inner + '</span>';
      }).join('') +
    '</div>';
  }

  function referenceList(refs) {
    var list = Array.isArray(refs) ? refs : (refs ? [refs] : []);
    list = list.filter(function (r) { return !isNoneVal(r); });
    if (!list.length) {
      return '<p style="color:#666;font-size:0.9rem;margin:0">No references available.</p>';
    }
    return '<div class="emd-view-references">' +
      list.map(function (r) {
        var s = String(r);
        return '<a class="emd-view-reference" href="' + escapeHtml(s) +
          '" target="_blank" rel="noopener">' +
          '<span class="emd-view-reference-text">' + escapeHtml(s) + '</span>' +
          '<span class="emd-view-reference-arrow">\u2192</span>' +
        '</a>';
      }).join('') +
    '</div>';
  }

  function codeBaseBox(codeBase) {
    if (isNoneVal(codeBase)) return '<span style="color:#aaa">\u2014</span>';
    var s = String(codeBase).trim();
    if (s.toLowerCase() === 'private') {
      return '<span class="emd-view-code-base private">\ud83d\udd12 Private</span>';
    }
    if (/^https?:\\/\\//i.test(s)) {
      var display = s.replace(/^https?:\\/\\//i, '');
      return '<span class="emd-view-code-base public">\ud83d\udcc2 ' +
        '<a href="' + escapeHtml(s) + '" target="_blank" rel="noopener">' +
        escapeHtml(display) + '</a></span>';
    }
    return '<span class="emd-view-code-base">' + escapeHtml(s) + '</span>';
  }

  function domainPill(domain) {
    if (isNoneVal(domain)) return '';
    var name = bestLabel(domain);
    var id   = bestId(domain) || name;
    var key  = String(id).toLowerCase().replace(/[^a-z0-9-]+/g, '-');
    return '<div class="emd-view-domain-pill ' + escapeHtml(key) + '">' +
      escapeHtml(name) + '</div>';
  }

  function linkRecord(field, value, fallbackLabel) {
    if (isNoneVal(value)) return '<span style="color:#aaa">\u2014</span>';
    var label, id;
    if (typeof value === 'object' && value && !Array.isArray(value)) {
      label = bestLabel(value); id = bestId(value);
    } else {
      id = String(value);
      label = fallbackLabel || formatKey(id.replace(/[-_]/g, ' '));
    }
    var href = viewUrlFor(field, id);
    if (href) {
      return '<a class="emd-view-link-card" href="' + escapeHtml(href) + '">' +
        '<span class="emd-view-link-card-name">' + escapeHtml(label) + '</span>' +
        '<span class="emd-view-link-card-id">' + escapeHtml(id) + '</span>' +
      '</a>';
    }
    return '<span class="emd-view-tag link">' + escapeHtml(label) +
      (id !== label ? ' <code>(' + escapeHtml(id) + ')</code>' : '') + '</span>';
  }

  function recordGrid(field, values) {
    if (isNoneVal(values)) return '';
    var list = Array.isArray(values) ? values : [values];
    list = list.filter(function (v) { return !isNoneVal(v); });
    if (!list.length) return '';
    return '<div class="emd-view-record-grid">' +
      list.map(function (v) { return linkRecord(field, v); }).join('') +
    '</div>';
  }

  function fmtNumber(n) {
    if (typeof n !== 'number') return String(n);
    return n.toLocaleString('en-US');
  }

  function techDetails(entry) {
    var rows = [];
    rows.push(
      '<div class="emd-view-tech-item">' +
        '<div class="emd-view-tech-label">Identifier (@id)</div>' +
        '<div class="emd-view-tech-value">' + escapeHtml(entry['@id'] || '') + '</div>' +
      '</div>');
    rows.push(
      '<div class="emd-view-tech-item">' +
        '<div class="emd-view-tech-label">Validation Key</div>' +
        '<div class="emd-view-tech-value">' + escapeHtml(entry.validation_key || 'N/A') + '</div>' +
      '</div>');
    var types = entry['@type'];
    if (types) {
      var typeList = Array.isArray(types) ? types : [types];
      rows.push(
        '<div class="emd-view-tech-item">' +
          '<div class="emd-view-tech-label">Resource Types</div>' +
          '<div class="emd-view-type-badges">' +
            typeList.map(function (t) {
              return '<span class="emd-view-type-badge">' + escapeHtml(t) + '</span>';
            }).join('') +
          '</div>' +
        '</div>');
    }
    return '<div class="emd-view-tech-grid">' + rows.join('') + '</div>';
  }

  function rawJsonBox(entry) {
    return '<details class="emd-view-json-toggle">' +
      '<summary>View raw JSON</summary>' +
      '<pre>' + escapeHtml(JSON.stringify(entry, null, 2)) + '</pre>' +
    '</details>';
  }

  /* ── header (shared across all renderers) ─────────────────────────── */

  function renderHeader(entry, opts) {
    opts = opts || {};
    var label = bestLabel(entry);
    var validKey = entry.validation_key || bestId(entry) || lastSeg(entry['@id']);
    var desc  = isNoneVal(entry.description) ? '' : entry.description;
    document.title = label + ' \u2014 ' + SINGULAR;

    var html = '<header class="emd-view-header">';
    if (opts.beforeBadge) html += opts.beforeBadge;
    html += '<div class="emd-view-badge">' + escapeHtml(BADGE_TEXT) + '</div>';
    html += '<h1 class="emd-view-title">' + escapeHtml(label) + '</h1>';
    if (validKey) html += '<div class="emd-view-id">id: <code>' + escapeHtml(validKey) + '</code></div>';
    if (desc)     html += '<p class="emd-view-desc">' + escapeHtml(desc) + '</p>';
    html += '</header>';
    return html;
  }

  /* ── leftover-properties helper ───────────────────────────────────────
     Auto-populate a "Other Properties" box with any fields the type-specific
     renderer didn't already display. Keeps the page complete even when new
     fields are added to a schema. */

  function leftoverPropsBox(entry, usedKeys) {
    var hideKeys = { 'validation_key':1, 'ui_label':1, 'description':1, 'name':1 };
    usedKeys.forEach(function (k) { hideKeys[k] = 1; });
    var rows = Object.keys(entry).filter(function (k) {
      return k.charAt(0) !== '@' && !hideKeys[k] && !isNoneVal(entry[k]);
    }).map(function (k) {
      return propRow(formatKey(k), renderValue(k, entry[k]));
    });
    var tbl = propTable(rows);
    return tbl ? box('Other Properties', tbl, {collapsed: true}) : '';
  }

  /* ── per-record-type renderers ────────────────────────────────────── */

  /* Horizontal Grid Cell — Stage 1 */
  function renderGridCell(entry) {
    var used = ['grid_type', 'grid_mapping', 'temporal_refinement', 'n_cells',
                'x_resolution', 'y_resolution', 'units', 'truncation_method',
                'truncation_number', 'southernmost_latitude', 'westernmost_longitude',
                'region', 'alias'];

    var stats = [];
    if (!isNoneVal(entry.n_cells))
      stats.push({label:'Cells', value: fmtNumber(entry.n_cells)});
    if (!isNoneVal(entry.x_resolution) && !isNoneVal(entry.y_resolution))
      stats.push({label:'Resolution', value: entry.x_resolution + '\u00b0 \u00d7 ' + entry.y_resolution + '\u00b0', small:true});
    if (!isNoneVal(entry.truncation_number))
      stats.push({label:'Truncation', value: 'T' + entry.truncation_number});
    if (!isNoneVal(entry.grid_type))
      stats.push({label:'Grid Type', value: bestLabel(entry.grid_type), small:true});
    if (!isNoneVal(entry.temporal_refinement))
      stats.push({label:'Temporal', value: bestLabel(entry.temporal_refinement), small:true});

    var key = entry.validation_key || bestId(entry);
    var co  = '<strong>What is this?</strong> Grid cell <strong>' + escapeHtml(key) + '</strong>';
    if (!isNoneVal(entry.grid_type))    co += ' uses a <strong>' + escapeHtml(bestLabel(entry.grid_type)) + '</strong> grid';
    if (!isNoneVal(entry.grid_mapping)) co += ' with <strong>' + escapeHtml(bestLabel(entry.grid_mapping)) + '</strong> mapping';
    if (!isNoneVal(entry.n_cells))      co += ', containing <strong>' + escapeHtml(fmtNumber(entry.n_cells)) + '</strong> cells';
    co += '.';
    if (!isNoneVal(entry.x_resolution) && !isNoneVal(entry.y_resolution))
      co += ' Resolution: <strong>' + entry.x_resolution + '\u00b0 \u00d7 ' + entry.y_resolution + '\u00b0</strong>.';
    if (!isNoneVal(entry.temporal_refinement))
      co += ' The grid is <strong>' + escapeHtml(bestLabel(entry.temporal_refinement)) + '</strong> in time.';

    var truncStr = null;
    if (!isNoneVal(entry.truncation_method) || !isNoneVal(entry.truncation_number)) {
      truncStr = (entry.truncation_method ? escapeHtml(bestLabel(entry.truncation_method)) + ' ' : '') +
                 (entry.truncation_number ? 'T' + escapeHtml(String(entry.truncation_number)) : '');
    }

    var props = propTable([
      propRow('Grid Type',           !isNoneVal(entry.grid_type)           ? escapeHtml(bestLabel(entry.grid_type)) : null),
      propRow('Grid Mapping',        !isNoneVal(entry.grid_mapping)        ? escapeHtml(bestLabel(entry.grid_mapping)) : null),
      propRow('Temporal Refinement', !isNoneVal(entry.temporal_refinement) ? escapeHtml(bestLabel(entry.temporal_refinement)) : null),
      propRow('Number of Cells',     !isNoneVal(entry.n_cells)             ? fmtNumber(entry.n_cells) : null),
      propRow('Resolution (x \u00d7 y)',
        (!isNoneVal(entry.x_resolution) && !isNoneVal(entry.y_resolution))
          ? entry.x_resolution + '\u00b0 \u00d7 ' + entry.y_resolution + '\u00b0' +
            (!isNoneVal(entry.units) ? ' (' + escapeHtml(bestLabel(entry.units)) + ')' : '')
          : null),
      propRow('Southernmost Latitude', !isNoneVal(entry.southernmost_latitude) ? escapeHtml(String(entry.southernmost_latitude)) + '\u00b0' : null),
      propRow('Westernmost Longitude', !isNoneVal(entry.westernmost_longitude) ? escapeHtml(String(entry.westernmost_longitude)) + '\u00b0' : null),
      propRow('Truncation', truncStr),
      propRow('Alias',  !isNoneVal(entry.alias)  ? escapeHtml(String(entry.alias))  : null),
    ]);

    var regions = !isNoneVal(entry.region)
      ? '<div class="emd-view-explainer" style="margin-top:14px"><strong>Region:</strong> ' +
          tagRow(entry.region, {primary:true}) +
        '</div>'
      : '';

    var html = renderHeader(entry);
    html += heroStatRow(stats);
    html += callout(co);
    html += box('Grid Properties', props + regions);
    html += leftoverPropsBox(entry, used);
    html += box('Technical Details', techDetails(entry), {collapsed: true});
    html += rawJsonBox(entry);
    return html;
  }

  /* Horizontal Computational Grid — Stage 2a */
  function renderHorizontalGrid(entry) {
    var used = ['arrangement', 'horizontal_subgrids'];
    var stats = [];
    if (!isNoneVal(entry.arrangement))
      stats.push({label:'Arrangement', value: bestLabel(entry.arrangement), small:true});
    if (Array.isArray(entry.horizontal_subgrids))
      stats.push({label:'Subgrids', value: entry.horizontal_subgrids.length});

    var key = entry.validation_key || bestId(entry);
    var co  = '<strong>What is this?</strong> Horizontal computational grid <strong>' +
              escapeHtml(key) + '</strong>';
    if (!isNoneVal(entry.arrangement)) co += ' uses an <strong>' + escapeHtml(bestLabel(entry.arrangement)) + '</strong> staggering arrangement';
    co += '.';

    var subgridsHtml = !isNoneVal(entry.horizontal_subgrids)
      ? recordGrid('horizontal_subgrids', entry.horizontal_subgrids)
      : '';

    var html = renderHeader(entry);
    html += heroStatRow(stats);
    html += callout(co);
    if (subgridsHtml) html += box('Horizontal Subgrids', subgridsHtml,
      {count: Array.isArray(entry.horizontal_subgrids) ? entry.horizontal_subgrids.length : 1});
    html += leftoverPropsBox(entry, used);
    html += box('Technical Details', techDetails(entry), {collapsed: true});
    html += rawJsonBox(entry);
    return html;
  }

  /* Vertical Computational Grid — Stage 2b */
  function renderVerticalGrid(entry) {
    var used = ['vertical_coordinate', 'n_z', 'total_thickness',
                'top_layer_thickness', 'bottom_layer_thickness'];
    var stats = [];
    if (!isNoneVal(entry.n_z))             stats.push({label:'Levels', value: fmtNumber(entry.n_z)});
    if (!isNoneVal(entry.total_thickness)) stats.push({label:'Total Thickness', value: entry.total_thickness, small:true});
    if (!isNoneVal(entry.vertical_coordinate))
      stats.push({label:'Coordinate', value: bestLabel(entry.vertical_coordinate), small:true});

    var co = '<strong>What is this?</strong> Vertical grid <strong>' +
             escapeHtml(entry.validation_key || bestId(entry)) + '</strong>';
    if (!isNoneVal(entry.vertical_coordinate))
      co += ' uses <strong>' + escapeHtml(bestLabel(entry.vertical_coordinate)) + '</strong> as its coordinate system';
    if (!isNoneVal(entry.n_z))
      co += ' with <strong>' + fmtNumber(entry.n_z) + '</strong> levels';
    co += '.';

    var props = propTable([
      propRow('Vertical Coordinate', !isNoneVal(entry.vertical_coordinate) ? escapeHtml(bestLabel(entry.vertical_coordinate)) : null),
      propRow('Number of Levels',    !isNoneVal(entry.n_z)                 ? fmtNumber(entry.n_z) : null),
      propRow('Top Layer Thickness',    !isNoneVal(entry.top_layer_thickness)    ? escapeHtml(String(entry.top_layer_thickness))    : null),
      propRow('Bottom Layer Thickness', !isNoneVal(entry.bottom_layer_thickness) ? escapeHtml(String(entry.bottom_layer_thickness)) : null),
      propRow('Total Thickness',        !isNoneVal(entry.total_thickness)        ? escapeHtml(String(entry.total_thickness))        : null),
    ]);

    var html = renderHeader(entry);
    html += heroStatRow(stats);
    html += callout(co);
    if (props) html += box('Vertical Profile', props);
    html += leftoverPropsBox(entry, used);
    html += box('Technical Details', techDetails(entry), {collapsed: true});
    html += rawJsonBox(entry);
    return html;
  }

  /* Component / ESM Family */
  function renderFamily(entry) {
    var used = ['primary_institution', 'collaborative_institutions',
                'scientific_domains', 'shared_code_base', 'source_code_repository',
                'programming_languages', 'license', 'established', 'evolution',
                'representative_member', 'family_type', 'website', 'references'];

    var stats = [];
    if (!isNoneVal(entry.primary_institution))
      stats.push({label:'Institution', value: bestLabel(entry.primary_institution), small:true});
    if (!isNoneVal(entry.established))
      stats.push({label:'Established', value: entry.established});
    if (!isNoneVal(entry.license))
      stats.push({label:'License', value: bestLabel(entry.license), small:true});

    var familyType = !isNoneVal(entry.family_type) ? entry.family_type : '';
    var typeLabel  = familyType === 'model' ? 'ESM Family' : 'Component Family';

    var co = '<strong>What is this?</strong> <strong>' + escapeHtml(bestLabel(entry)) +
             '</strong> is a <strong>' + escapeHtml(typeLabel) + '</strong>';
    if (!isNoneVal(entry.primary_institution))
      co += ' developed by <strong>' + escapeHtml(bestLabel(entry.primary_institution)) + '</strong>';
    co += '.';
    if (!isNoneVal(entry.scientific_domains)) {
      var domList = Array.isArray(entry.scientific_domains) ? entry.scientific_domains : [entry.scientific_domains];
      var domNames = domList.map(function (d) { return bestLabel(d); }).join(', ');
      co += ' It covers the <strong>' + escapeHtml(domNames) + '</strong> domain' +
            (domList.length > 1 ? 's' : '') + '.';
    }

    /* Institutions box */
    var instHtml = '';
    if (!isNoneVal(entry.primary_institution)) {
      instHtml += '<div class="emd-view-explainer" style="margin:0 0 8px"><strong>Primary:</strong></div>';
      instHtml += linkRecord('primary_institution', entry.primary_institution);
    }
    if (!isNoneVal(entry.collaborative_institutions)) {
      instHtml += '<div class="emd-view-explainer" style="margin:14px 0 8px"><strong>Collaborators:</strong></div>';
      instHtml += recordGrid('collaborative_institutions', entry.collaborative_institutions);
    }

    /* Scientific domains box */
    var domainsHtml = !isNoneVal(entry.scientific_domains)
      ? tagRow(entry.scientific_domains, {primary: true})
      : '';

    /* Code & development box */
    var devRows = propTable([
      propRow('Shared Code Base', !isNoneVal(entry.shared_code_base) ? escapeHtml(String(entry.shared_code_base)) : null),
      propRow('Source Repository', !isNoneVal(entry.source_code_repository) ? codeBaseBox(entry.source_code_repository) : null),
      propRow('Programming Languages', !isNoneVal(entry.programming_languages) ? tagRow(entry.programming_languages) : null),
      propRow('License',          !isNoneVal(entry.license)     ? escapeHtml(bestLabel(entry.license)) : null),
      propRow('Established',      !isNoneVal(entry.established) ? escapeHtml(String(entry.established)) : null),
      propRow('Website',          !isNoneVal(entry.website)     ? renderValue('website', entry.website) : null),
      propRow('Representative Member', !isNoneVal(entry.representative_member) ? linkRecord('representative_member', entry.representative_member) : null),
      propRow('Evolution',        !isNoneVal(entry.evolution)   ? escapeHtml(String(entry.evolution)) : null),
    ]);

    var html = renderHeader(entry);
    html += heroStatRow(stats);
    html += callout(co);
    if (instHtml)    html += box('Institutions', instHtml);
    if (domainsHtml) html += box('Scientific Domains', domainsHtml);
    if (devRows)     html += box('Code & Development', devRows);
    if (!isNoneVal(entry.references)) {
      var refCount = Array.isArray(entry.references) ? entry.references.length : 1;
      html += box('References', referenceList(entry.references), {count: refCount});
    }
    html += leftoverPropsBox(entry, used);
    html += box('Technical Details', techDetails(entry), {collapsed: true});
    html += rawJsonBox(entry);
    return html;
  }

  /* Model Component — Stage 3 */
  function renderModelComponent(entry) {
    var used = ['family', 'component', 'code_base', 'references', 'name'];

    var stats = [];
    if (!isNoneVal(entry.component))
      stats.push({label:'Domain', value: bestLabel(entry.component), small:true});
    if (!isNoneVal(entry.family))
      stats.push({label:'Family', value: bestLabel(entry.family), small:true});
    if (!isNoneVal(entry.code_base)) {
      var cb = String(entry.code_base).toLowerCase();
      stats.push({label:'Code Base', value: cb === 'private' ? '🔒 Private' : '📂 Public', small:true});
    }

    var co = '<strong>What is this?</strong> <strong>' + escapeHtml(bestLabel(entry)) +
             '</strong> is a <strong>model component</strong> that simulates the';
    co += !isNoneVal(entry.component)
      ? ' <strong>' + escapeHtml(bestLabel(entry.component)) + '</strong>'
      : ' physical';
    co += ' processes within an Earth system model.';
    if (!isNoneVal(entry.family))
      co += ' It belongs to the <strong>' + escapeHtml(bestLabel(entry.family)) + '</strong> family.';
    if (!isNoneVal(entry.code_base)) {
      co += String(entry.code_base).toLowerCase() === 'private'
        ? ' The source code is kept private.'
        : ' The source code is publicly available.';
    }

    var html = renderHeader(entry, {
      beforeBadge: !isNoneVal(entry.component) ? domainPill(entry.component) : ''
    });
    html += heroStatRow(stats);
    html += callout(co);

    /* Scientific Domain box (if applicable) */
    if (!isNoneVal(entry.component)) {
      html += box('Scientific Domain',
        '<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">' +
          domainPill(entry.component) +
          '<span class="emd-view-explainer" style="margin:0">' +
            'This component operates in the ' + escapeHtml(bestLabel(entry.component)) + ' realm.' +
          '</span>' +
        '</div>');
    }

    /* Family link box */
    if (!isNoneVal(entry.family)) {
      html += box('Component Family', linkRecord('family', entry.family));
    }

    /* Code base box */
    if (!isNoneVal(entry.code_base)) {
      html += box('Code Base', codeBaseBox(entry.code_base));
    }

    /* References */
    if (!isNoneVal(entry.references)) {
      var refCount = Array.isArray(entry.references) ? entry.references.length : 1;
      html += box('References', referenceList(entry.references), {count: refCount});
    } else {
      html += box('References', referenceList([]), {count: 0, collapsed: true});
    }

    html += leftoverPropsBox(entry, used);
    html += box('Technical Details', techDetails(entry), {collapsed: true});
    html += rawJsonBox(entry);
    return html;
  }

  /* Model (source_id) — Stage 4 */
  function renderModel(entry) {
    var used = ['family', 'release_year', 'calendar', 'name', 'component_configs',
                'dynamic_components', 'prescribed_components', 'omitted_components',
                'embedded_components', 'coupling_groups', 'references'];

    var stats = [];
    if (!isNoneVal(entry.release_year))
      stats.push({label:'Released', value: entry.release_year});
    if (!isNoneVal(entry.calendar))
      stats.push({label:'Calendar', value: bestLabel(entry.calendar), small:true});
    if (!isNoneVal(entry.family))
      stats.push({label:'ESM Family', value: bestLabel(entry.family), small:true});
    if (Array.isArray(entry.component_configs))
      stats.push({label:'Components', value: entry.component_configs.length});

    var co = '<strong>What is this?</strong> <strong>' + escapeHtml(bestLabel(entry)) +
             '</strong> is a registered CMIP <code>source_id</code>';
    if (!isNoneVal(entry.family))
      co += ' belonging to the <strong>' + escapeHtml(bestLabel(entry.family)) + '</strong> family';
    co += '.';
    if (Array.isArray(entry.component_configs)) {
      co += ' It assembles <strong>' + entry.component_configs.length +
            '</strong> component configurations into a coupled system.';
    }
    if (!isNoneVal(entry.release_year))
      co += ' Released in <strong>' + escapeHtml(String(entry.release_year)) + '</strong>.';

    var html = renderHeader(entry);
    html += heroStatRow(stats);
    html += callout(co);

    if (!isNoneVal(entry.family))
      html += box('ESM Family', linkRecord('family', entry.family));

    /* Active vs prescribed vs omitted realms */
    var realmsHtml = '';
    if (!isNoneVal(entry.dynamic_components)) {
      realmsHtml += '<div class="emd-view-explainer" style="margin:0 0 6px"><strong>Dynamic (interactive):</strong></div>' +
        tagRow(entry.dynamic_components, {primary: true});
    }
    if (!isNoneVal(entry.prescribed_components)) {
      realmsHtml += '<div class="emd-view-explainer" style="margin:14px 0 6px"><strong>Prescribed:</strong></div>' +
        tagRow(entry.prescribed_components);
    }
    if (!isNoneVal(entry.omitted_components)) {
      realmsHtml += '<div class="emd-view-explainer" style="margin:14px 0 6px"><strong>Omitted:</strong></div>' +
        tagRow(entry.omitted_components);
    }
    if (realmsHtml) html += box('Realms', realmsHtml);

    /* Component configurations */
    if (!isNoneVal(entry.component_configs)) {
      var cfgCount = Array.isArray(entry.component_configs) ? entry.component_configs.length : 1;
      html += box('Component Configurations',
        recordGrid('component_configs', entry.component_configs), {count: cfgCount});
    }

    /* Embedded components + coupling */
    if (!isNoneVal(entry.embedded_components))
      html += box('Embedded Components',
        renderValue('embedded_components', entry.embedded_components));
    if (!isNoneVal(entry.coupling_groups))
      html += box('Coupling Groups',
        renderValue('coupling_groups', entry.coupling_groups));

    /* Calendar */
    if (!isNoneVal(entry.calendar))
      html += box('Calendar', escapeHtml(bestLabel(entry.calendar)));

    /* References */
    if (!isNoneVal(entry.references)) {
      var refCount = Array.isArray(entry.references) ? entry.references.length : 1;
      html += box('References', referenceList(entry.references), {count: refCount});
    }

    html += leftoverPropsBox(entry, used);
    html += box('Technical Details', techDetails(entry), {collapsed: true});
    html += rawJsonBox(entry);
    return html;
  }

  /* Generic fallback — used when no type-specific renderer applies */
  function renderGeneric(entry) {
    var stats = [];
    STAT_KEYS.forEach(function (k) {
      if (k in entry && !isNoneVal(entry[k])) {
        stats.push({label: formatKey(k), value: bestLabel(entry[k]) || String(entry[k])});
      }
    });

    var html = renderHeader(entry);
    if (stats.length) html += heroStatRow(stats);

    var skip = { 'validation_key':1, 'ui_label':1, 'description':1, 'name':1 };
    var keys = Object.keys(entry).filter(function (k) {
      return k.charAt(0) !== '@' && !skip[k] && STAT_KEYS.indexOf(k) < 0;
    });
    if (keys.length) {
      var rows = keys.map(function (k) {
        return propRow(formatKey(k), renderValue(k, entry[k]));
      });
      html += box('Properties', propTable(rows));
    }
    html += box('Technical Details', techDetails(entry), {collapsed: true});
    html += rawJsonBox(entry);
    return html;
  }

  /* ── dispatch ─────────────────────────────────────────────────────── */

  var RENDERERS = {
    'Horizontal_Grid_Cells':           renderGridCell,
    'Horizontal_Computational_Grids':  renderHorizontalGrid,
    'Vertical_Computational_Grids':    renderVerticalGrid,
    'Component_Families':              renderFamily,
    'Earth_System_Model_Families':     renderFamily,
    'Model_Components':                renderModelComponent,
    'Models':                          renderModel
  };

  function renderEntry(entry) {
    var renderer = RENDERERS[STEM] || renderGeneric;
    contentEl.innerHTML = renderer(entry);
  }
}());
</script>
"""


# Map of common cross-reference fields → the stem of the type they link to.
# Used by the view page to turn linked ids into clickable view-page URLs.
LINK_FIELD_TO_STEM = {
    # component / ESM families share the model_family folder
    "family":                        "model_family",
    "horizontal_grid_cell":          "horizontal_grid_cells",
    "horizontal_subgrid":            "horizontal_subgrid",
    "horizontal_computational_grid": "horizontal_computational_grids",
    "vertical_computational_grid":   "vertical_computational_grids",
    "model_component":               "model_components",
    "component":                     "model_components",
    # approximate: no dedicated view-page for component_config yet
    "component_configs":             "horizontal_computational_grids",
    "horizontal_subgrids":           "horizontal_subgrid",
    "esm_family":                    "earth_system_model_families",
}


# Numeric / "headline" fields per stem — surfaced as stat tiles at the top
# of the entry's view page.
STAT_KEYS_BY_STEM = {
    "Horizontal_Grid_Cells": [
        "grid_type", "n_cells", "x_resolution", "y_resolution",
        "region", "units",
    ],
    "Horizontal_Computational_Grids": [
        "arrangement",
    ],
    "Vertical_Computational_Grids": [
        "vertical_coordinate", "n_z", "total_thickness",
        "top_layer_thickness", "bottom_layer_thickness",
    ],
    "Component_Families": [
        "primary_institution", "established", "license",
    ],
    "Earth_System_Model_Families": [
        "primary_institution", "established", "license",
    ],
    "Model_Components": [
        "component", "family",
    ],
    "Models": [
        "release_year", "family", "calendar",
    ],
}


def _build_view_page(stem, title, singular):
    """Generate a hidden dynamic-view markdown page for a record type.

    Raises ``RuntimeError`` if the template is empty or substitution produces
    an empty result \u2014 prevents the script from silently writing 0-byte
    view pages, which was the bug that caused "view pages not loading content".
    """
    title_plural = title  # e.g. "Horizontal Grid Cells"
    stat_keys = STAT_KEYS_BY_STEM.get(stem, [])
    link_types_clean = dict(LINK_FIELD_TO_STEM)

    if not _VIEW_TEMPLATE or len(_VIEW_TEMPLATE) < 100:
        raise RuntimeError(
            f"_VIEW_TEMPLATE is empty or truncated ({len(_VIEW_TEMPLATE)} chars). "
            f"View page for {stem} would be 0 bytes \u2014 refusing to write."
        )

    out = (
        _VIEW_TEMPLATE
        .replace("__STEM__",         stem)
        .replace("__SINGULAR__",     singular)
        .replace("__TITLE_PLURAL__", title_plural)
        .replace("__STAT_KEYS__",    json.dumps(stat_keys, separators=(",", ":")))
        .replace("__LINK_TYPES__",   json.dumps(link_types_clean, separators=(",", ":")))
    )
    if not out.strip():
        raise RuntimeError(
            f"View page for {stem} rendered as empty string \u2014 refusing to write.")
    return out


def _build_page(stem, items, ordered_labels, ordered_ids, ordered_tags,
                link_ordered, text_ordered, cluster_labels, method_str, repo_subdir,
                raw_size_str="—", data_size_str="—", last_updated_str="—"):

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

    # All entry links go to the dynamic per-stem view page with ?id=<entry_id>.
    # The view page is `view_{stem.lower()}` (a hidden MkDocs page that uses JS
    # to load the recursively-populated raw JSON and render it). Doing this
    # means we no longer need to generate one static directory per record id.
    view_path = "view_" + stem.lower()
    entries = [
        {"label": ordered_labels[i],
         "url":   "../" + view_path + "/?id=" + ordered_ids[i]}
        for i in range(n)
    ]

    meta = [{"label": ordered_labels[i], "tags": ordered_tags[i]} for i in range(n)]

    options_html = "\n".join(
        '    <option value="../' + view_path + "/?id=" + eid + '">' + label + '</option>'
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
        .replace("__RAW_SIZE__", raw_size_str)
        .replace("__DATA_SIZE__", data_size_str)
        .replace("__LAST_UPDATED__", last_updated_str)
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

        # ── Always write the dynamic view page, even if <2 items or the matrix
        #    step later fails. This ensures /EMD_Repository/view_<stem>/?id=<id>
        #    is *always* a routable URL with rendering capability.
        view_md_path = OUT_DIR / f"view_{stem.lower()}.md"
        try:
            view_md = _build_view_page(
                stem=stem,
                title=stem.replace("_", " "),
                singular=SINGULAR_NAMES.get(stem, stem.replace("_", " ").rstrip("s")),
            )
            view_md_path.write_text(view_md, encoding="utf-8")
            print(f"  \u2705 View page written ({view_md_path.name}, "
                  f"{view_md_path.stat().st_size // 1024} KB)", flush=True)
        except Exception as ve:
            print(f"  \u26a0 View page write failed for {stem}: {ve}", flush=True)

        if len(items) < 2:
            print(f"  \u23ed  Skipped similarity \u2014 need \u2265 2 items "
                  f"(got {len(items)})", flush=True)
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

            # ── Build the group-level dendrogram tree (matches _build_page) ──
            combined_sim = (link_ordered + text_ordered) / 2
            np.fill_diagonal(combined_sim, 0.0)
            dist = 1.0 - np.clip(combined_sim, 0, 1)
            unique_groups = sorted(set(cluster_labels.tolist()))
            kgroups = len(unique_groups)
            group_rows = {g: [i for i, c in enumerate(cluster_labels) if c == g]
                          for g in unique_groups}
            if kgroups >= 2:
                gdist = np.zeros((kgroups, kgroups))
                for ai, gi in enumerate(unique_groups):
                    for aj, gj in enumerate(unique_groups):
                        if ai == aj:
                            continue
                        ri, rj = group_rows[gi], group_rows[gj]
                        gdist[ai, aj] = dist[np.ix_(ri, rj)].mean()
                group_labels = [ordered_labels[group_rows[g][0]] for g in unique_groups]
                tree_for_json = _average_linkage_tree(group_labels, gdist)
            else:
                tree_for_json = {"name": ordered_labels[0], "leaf": True,
                                 "spectral_index": 0, "value": 0.0}

            # Write data JSON FIRST so we can include its size in the markdown.
            data_payload = _build_data_json(
                stem, items, ordered_labels, ordered_ids,
                link_ordered, text_ordered, method_str_display,
                tree_for_json, schema,
            )
            data_path.write_text(
                json.dumps(data_payload, indent=2), encoding="utf-8")
            data_size = data_path.stat().st_size
            print(f"  \u2705 JSON written ({data_size // 1024} KB)", flush=True)

            # File-size stats for the page header.
            raw_size       = raw_path.stat().st_size
            last_updated   = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            raw_size_str   = _format_size(raw_size)
            data_size_str  = _format_size(data_size)

            # Write .md page with stats info embedded.
            md_content = _build_page(
                stem, items,
                ordered_labels, ordered_ids, ordered_tags,
                link_ordered, text_ordered, cluster_labels, method_str_display,
                repo_subdir,
                raw_size_str=raw_size_str,
                data_size_str=data_size_str,
                last_updated_str=last_updated,
            )
            md_path.write_text(md_content, encoding="utf-8")
            print(f"  \u2705 MD written  ({md_path.stat().st_size // 1024} KB)", flush=True)

            # (View page already written above \u2014 don't duplicate the write.)
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
