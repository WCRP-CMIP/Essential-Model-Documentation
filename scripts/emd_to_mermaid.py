#!/usr/bin/env python3
"""
emd_to_mermaid.py — Turn an EMD JSON-LD model into a Mermaid graph diagram.

Uses cmipld.get(link, depth=N) for n-depth recursive @id resolution.

Highlights (per EMD model-level lists):
  * dynamic_components  -> thicker outline on the matching component_config
  * embedded_components -> yellow fill on the matching component_config

Only structural types become graph nodes (model, model_family,
component_config, model_component, h-grid, v-grid, subgrid, grid_cell).
Universal-vocab values (arrangement, realm, vertical_coordinate, grid_type,
cell_variable_type, ...) are rendered inline in the parent's label, never as
nodes of their own.

If a reference comes back as a bare string instead of a resolved object (e.g.
because cmipld's effective resolution depth is exhausted or the cache was
populated at a shallower depth), the walker still emits a stub node so the
chain stays visible — h-grid -> subgrid -> grid_cell is preserved.

Usage:
    python emd_to_mermaid.py emd:model/cnrm-esm2-1e > cnrm.mmd
    python emd_to_mermaid.py model/cnrm-esm2-1e.json --depth 8
"""

import argparse
import re
from collections import defaultdict

import cmipld

_EMD_DEFAULT_URL = "https://wcrp-cmip.github.io/Essential-Model-Documentation/"

# ---------------------------------------------------------------------------
# Structural types (these become graph nodes)
# ---------------------------------------------------------------------------

STYLE = {
    "wcrp:model":                         "fill:#1f4e79,color:#fff,stroke:#0b2a4a,stroke-width:2px",
    "wcrp:model_family":                  "fill:#e8d5ff,color:#3a1b5e,stroke:#5a2e91,stroke-width:2px",
    "wcrp:component_config":              "fill:#ffffff,stroke:#333,stroke-width:1px",
    "wcrp:model_component":               "fill:#f4f4f4,stroke:#666,stroke-width:1px",
    "wcrp:horizontal_computational_grid": "fill:#cce5ff,stroke:#003366,stroke-width:2px",
    "wcrp:vertical_computational_grid":   "fill:#d6eaff,stroke:#003366,stroke-width:1px",
    "wcrp:horizontal_subgrid":            "fill:#ffffff,stroke:#666,stroke-width:1px",
    "wcrp:horizontal_grid_cell":          "fill:#e8f5e8,stroke:#2d6a4f,stroke-width:1px",
}

DYNAMIC_STYLE  = "stroke-width:4px"
EMBEDDED_STYLE = "fill:#fff3a3,stroke:#cc8800,stroke-width:3px"

# Field name -> inferred type, used when a reference is left as a bare string
# (e.g. cmipld depth budget exhausted, or pre-resolution input).
FIELD_TYPE = {
    "component_configs":              "wcrp:component_config",
    "horizontal_computational_grid":  "wcrp:horizontal_computational_grid",
    "vertical_computational_grid":    "wcrp:vertical_computational_grid",
    "horizontal_subgrids":            "wcrp:horizontal_subgrid",
    "horizontal_grid_cell":           "wcrp:horizontal_grid_cell",
    "model_component":                "wcrp:model_component",
    "family":                         "wcrp:model_family",
}

# Walk order: deeper structural paths first, so Mermaid lays the diagram out
# in a sensible top-to-bottom order (h-grid chain before v-grid before component).
KEY_ORDER = [
    "horizontal_computational_grid",
    "horizontal_subgrids",
    "horizontal_grid_cell",
    "vertical_computational_grid",
    "model_component",
    "component_configs",
]

# JSON-LD bookkeeping and prose fields — never traversed, never rendered as
# graph edges.
META_KEYS = {
    "@context", "@type", "@id",
    "validation_key", "ui_label", "description",
    "alias", "references", "release_year",
    "calendar", "crs", "name",
}

# Model-level config that drives styling rather than direct graph edges.
MODEL_META_KEYS = {
    "coupling_groups", "omitted_components", "prescribed_components",
    "dynamic_components", "embedded_components", "family",
}

# Universal-vocab fields — values are folded into the parent label, never
# emitted as standalone nodes (even if resolved into dicts by cmipld).
INLINE_VOCAB_KEYS = {
    "arrangement", "grid_mapping", "grid_type",
    "cell_variable_type", "vertical_coordinate",
    "realm", "units", "region",
    "temporal_refinement", "truncation_method",
}

# Numeric / scalar literals — keep in labels, don't traverse.
SCALAR_FIELDS = {
    "n_cells", "n_z", "n_z_range",
    "x_resolution", "y_resolution",
    "westernmost_longitude", "southernmost_latitude",
    "truncation_number",
    "bottom_layer_thickness", "top_layer_thickness", "total_thickness",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def short_id(node_id):
    if not isinstance(node_id, str):
        return str(node_id)
    return node_id.rsplit("/", 1)[-1].split(":")[-1]


def mid(node_id):
    return re.sub(r"[^A-Za-z0-9_]", "_", str(node_id))


def primary_type(node):
    t = node.get("@type", [])
    if isinstance(t, str):
        t = [t]
    for x in t:
        if isinstance(x, str) and x.startswith("wcrp:"):
            return x
    return t[0] if t else None


def _vocab_name(value):
    """Extract a short name from a vocab value — string, dict, or list."""
    if isinstance(value, str):
        return short_id(value)
    if isinstance(value, dict):
        return short_id(value.get("@id") or value.get("validation_key") or "")
    if isinstance(value, list):
        names = [_vocab_name(v) for v in value]
        return ", ".join(n for n in names if n)
    return ""


def _name_of(item):
    """Realm-name normalisation for dynamic_components / embedded_components."""
    if isinstance(item, str):
        return short_id(item)
    if isinstance(item, dict):
        return short_id(item.get("@id") or item.get("validation_key") or "")
    return None


def realm_of(node):
    """Realm of a component_config from its validation_key/@id prefix."""
    vk = node.get("validation_key") or short_id(node.get("@id", ""))
    return vk.split("_", 1)[0] if vk else None


def make_label(node):
    """Compact node label — id plus at most one or two summary lines."""
    nid = short_id(node.get("@id", "?"))
    t = primary_type(node)
    lines = [f"<b>{nid}</b>"]

    if t == "wcrp:horizontal_grid_cell":
        gt = _vocab_name(node.get("grid_type"))
        if gt:
            lines.append(gt)
        nc = node.get("n_cells")
        if isinstance(nc, int):
            lines.append(f"{nc:,} cells")
    elif t == "wcrp:horizontal_computational_grid":
        arr = _vocab_name(node.get("arrangement"))
        if arr:
            lines.append(arr)
    elif t == "wcrp:vertical_computational_grid":
        if node.get("n_z"):
            lines.append(f"{node['n_z']} levels")
        vc = _vocab_name(node.get("vertical_coordinate"))
        if vc:
            lines.append(vc)
    elif t == "wcrp:horizontal_subgrid":
        cvt = _vocab_name(node.get("cell_variable_type"))
        if cvt:
            lines.append(cvt)
    elif t == "wcrp:model_component":
        realm = _vocab_name(node.get("realm"))
        if realm:
            lines.append(f"({realm})")
    # wcrp:component_config: realm is already in @id (realm_code_h_v), nothing to add

    return "<br/>".join(s for s in lines if s)


def _sorted_keys(d):
    pri = {k: i for i, k in enumerate(KEY_ORDER)}
    return sorted(d.keys(), key=lambda k: (pri.get(k, 999), k))


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

class Builder:
    def __init__(self, model, family_link=True, edge_labels=False, max_depth=50):
        self.model = model
        self.family_link = family_link
        self.edge_labels = edge_labels
        self.max_depth = max_depth
        self.nodes = {}
        self.edges = []
        self.classes = defaultdict(set)

        self.dyn = {
            name
            for item in (model.get("dynamic_components") or [])
            for name in [_name_of(item)] if name
        }
        self.emb_children = {}
        for pair in (model.get("embedded_components") or []):
            if isinstance(pair, list) and len(pair) == 2:
                p = _name_of(pair[0])
                c = _name_of(pair[1])
                if p and c:
                    self.emb_children[c] = p

    def walk(self, node, parent_id=None, edge_label=None, depth=0):
        if depth > self.max_depth:
            return

        # Lists: walk each item with the same edge label.
        if isinstance(node, list):
            for item in node:
                self.walk(item, parent_id, edge_label, depth + 1)
            return

        # Bare string reference: emit a stub node if we can infer the type
        # from the edge label. Lets us keep the chain visible when cmipld
        # leaves leaves unresolved.
        if isinstance(node, str):
            if not parent_id or edge_label not in FIELD_TYPE:
                return
            inferred = FIELD_TYPE[edge_label]
            nid = node
            if nid not in self.nodes:
                self.nodes[nid] = {"@id": nid, "@type": [inferred]}
                if inferred in STYLE:
                    self.classes[inferred].add(nid)
            if parent_id != nid:
                self.edges.append((parent_id, nid, edge_label))
            return

        if not isinstance(node, dict) or "@id" not in node:
            return

        # Only structural types make it into the graph as nodes.
        t = primary_type(node)
        if t not in STYLE:
            return

        nid = node["@id"]
        if nid not in self.nodes:
            self.nodes[nid] = node
            self._classify(node, nid)
        if parent_id and parent_id != nid:
            self.edges.append((parent_id, nid, edge_label))

        for key in _sorted_keys(node):
            if key in META_KEYS or key in MODEL_META_KEYS:
                continue
            if key in SCALAR_FIELDS or key in INLINE_VOCAB_KEYS:
                continue
            self.walk(node[key], parent_id=nid, edge_label=key, depth=depth + 1)

    def _classify(self, node, nid):
        t = primary_type(node)
        if t in STYLE:
            self.classes[t].add(nid)
        if t == "wcrp:component_config":
            r = realm_of(node)
            if r in self.dyn:
                self.classes["__dynamic__"].add(nid)
            if r in self.emb_children:
                self.classes["__embedded__"].add(nid)

    def emit(self):
        lines = ["graph TD"]

        # Family node
        family = self.model.get("family")
        family_id = None
        if family:
            if isinstance(family, dict):
                family_id = family.get("@id")
                if family_id:
                    self.nodes.setdefault(family_id, family)
            else:
                family_id = family
                self.nodes.setdefault(
                    family_id, {"@id": family, "@type": ["wcrp:model_family"]}
                )
            if family_id:
                self.classes["wcrp:model_family"].add(family_id)

        for nid, node in self.nodes.items():
            lines.append(f'    {mid(nid)}["{make_label(node)}"]')

        if self.family_link and family_id and self.model.get("@id"):
            lines += [
                '    subgraph FAM[" "]',
                "        direction BT",
                f"        {mid(self.model['@id'])} -.->|family| {mid(family_id)}",
                "    end",
            ]

        for src, dst, lbl in self.edges:
            if self.edge_labels and lbl:
                lines.append(f"    {mid(src)} -->|{lbl}| {mid(dst)}")
            else:
                lines.append(f"    {mid(src)} --> {mid(dst)}")

        for cls in self.classes:
            if cls == "__dynamic__":
                lines.append(f"    classDef dynamic {DYNAMIC_STYLE}")
            elif cls == "__embedded__":
                lines.append(f"    classDef embedded {EMBEDDED_STYLE}")
            elif cls in STYLE:
                lines.append(f"    classDef {_cname(cls)} {STYLE[cls]}")

        order = [c for c in self.classes if c not in ("__dynamic__", "__embedded__")]
        if "__dynamic__" in self.classes:
            order.append("__dynamic__")
        if "__embedded__" in self.classes:
            order.append("__embedded__")
        for cls in order:
            cn = ("dynamic" if cls == "__dynamic__"
                  else "embedded" if cls == "__embedded__"
                  else _cname(cls))
            for nid in self.classes[cls]:
                lines.append(f"    class {mid(nid)} {cn}")

        return "\n".join(lines)


def _cname(cls):
    return cls.replace("wcrp:", "").replace(":", "_").replace("-", "_")


# ---------------------------------------------------------------------------
# Prefix registration
# ---------------------------------------------------------------------------

def register_prefix(prefix, url):
    if not url.endswith("/"):
        url += "/"
    cmipld.mapping[prefix] = url
    cmipld.locations.mapping[prefix] = url
    cmipld.locations.matches = re.compile(
        f"({'|'.join([p + ':' for p in cmipld.locations.mapping.keys()])})"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="EMD JSON-LD model -> Mermaid graph (via cmipld.get).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("link",
                    help="Prefixed URI, full URL, or local path (e.g. emd:model/cnrm-esm2-1e).")
    ap.add_argument("--depth", type=int, default=6,
                    help="Depth passed to cmipld.get (default 6).")
    ap.add_argument("--prefix", action="append", default=[],
                    help="Add a prefix mapping, e.g. emd=https://.... Repeatable.")
    ap.add_argument("--no-family-link", action="store_true",
                    help="Suppress the model->family upward edge.")
    ap.add_argument("--edge-labels", action="store_true",
                    help="Annotate edges with the JSON-LD field name.")
    args = ap.parse_args()

    if "emd" not in cmipld.mapping:
        register_prefix("emd", _EMD_DEFAULT_URL)
    for spec in args.prefix:
        if "=" not in spec:
            ap.error(f"--prefix expects p=URL, got: {spec!r}")
        p, u = spec.split("=", 1)
        register_prefix(p.strip(), u.strip())

    model = cmipld.get(args.link, depth=args.depth)

    builder = Builder(
        model,
        family_link=not args.no_family_link,
        edge_labels=args.edge_labels,
    )
    builder.walk(model)
    print(builder.emit())


if __name__ == "__main__":
    main()
