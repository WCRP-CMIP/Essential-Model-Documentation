#!/usr/bin/env python3
"""Generate model genealogy radial tree page."""

import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from jinja2 import Environment, FileSystemLoader
from helpers.data_loader import init_loader, fetch_data
from helpers.realm_colors import get_realm_color

TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"
OUTPUT_DIR   = SCRIPT_DIR.parent / "EMD_Repository"
OUTPUT_FILE  = OUTPUT_DIR / "genealogy.html"

DEPTH = 8


def _label(obj) -> str:
    """Best short label for a dict-or-string node."""
    if isinstance(obj, str):
        return obj.split("/")[-1].split(":")[-1]
    if isinstance(obj, dict):
        return (
            obj.get("ui_label") or
            obj.get("validation_key") or
            str(obj.get("@id", "unknown")).split("/")[-1]
        )
    return "unknown"


def build_tree(graph: list) -> dict:
    """
    Build nested hierarchy for D3:
      root -> realm -> model family -> model -> component config -> grid
    """
    root = {"name": "EMD Models", "depth": 0, "children": {}}

    for model in graph:
        model_name = model.get("name") or _label(model)

        raw_family = model.get("family", [])
        families = raw_family if isinstance(raw_family, list) else [raw_family]

        def types_str(f):
            t = f.get("@type", [])
            return " ".join(t if isinstance(t, list) else [str(t)])

        realms = [
            _label(f) for f in families
            if isinstance(f, dict) and "scientific_domain" in types_str(f)
        ] or ["unknown"]

        model_families = [
            _label(f) for f in families
            if isinstance(f, dict) and "model_family" in types_str(f)
        ] or ["ungrouped"]

        for realm in realms:
            r_node = root["children"].setdefault(
                realm, {"name": realm, "depth": 1,
                        "color": get_realm_color(realm), "children": {}}
            )
            for mf in model_families:
                mf_node = r_node["children"].setdefault(
                    mf, {"name": mf, "depth": 2, "children": {}}
                )
                m_node = mf_node["children"].setdefault(
                    model_name, {"name": model_name, "depth": 3, "children": {}}
                )
                for cfg in model.get("component_configs", []):
                    cfg_id = _label(cfg)
                    h = _label(cfg.get("horizontal_computational_grid", "?"))
                    v = _label(cfg.get("vertical_computational_grid", "?"))
                    grid_key = f"{h} / {v}"
                    cfg_node = m_node["children"].setdefault(
                        cfg_id,
                        {"name": cfg_id, "depth": 4,
                         "meta": {"h_grid": h, "v_grid": v}, "children": {}}
                    )
                    cfg_node["children"].setdefault(
                        grid_key, {"name": grid_key, "depth": 5, "children": {}}
                    )

    def _to_list(node):
        kids = list(node.pop("children").values())
        if kids:
            node["children"] = [_to_list(c) for c in kids]
        return node

    return _to_list(root)


def main():
    print("Genealogy Page Generator")
    print("=" * 40)

    init_loader()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("  Fetching model graph ...")
    graph = fetch_data("model", depth=DEPTH)
    print(f"  -> {len(graph)} models")

    if not graph:
        print("No models found - skipping genealogy page")
        return 0

    tree = build_tree(graph)

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)
    template = env.get_template("genealogy.html.j2")

    html = template.render(
        name="Model Genealogy",
        tree_json=json.dumps(tree, indent=2),
        depth="../../",
        generated_date=datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    )
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"  + Written -> {OUTPUT_FILE.relative_to(SCRIPT_DIR.parent.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
else:
    main()
