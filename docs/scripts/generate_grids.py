#!/usr/bin/env python3
"""Generate computational grid HTML pages from JSON-LD metadata."""

import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from jinja2 import Environment, BaseLoader
except ImportError:
    print("Error: jinja2 not installed")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable

from helpers import ICONS, is_none_value, escape_html
from helpers.data_loader import init_loader, list_entries, fetch_entry

OUTPUT_DIR_H = SCRIPT_DIR.parent / "1_Explore_The_EMD" / "Horizontal_Computational_Grids"
OUTPUT_DIR_V = SCRIPT_DIR.parent / "1_Explore_The_EMD" / "Vertical_Computational_Grids"

# Old directories to clean up
OLD_DIRS = [
    SCRIPT_DIR.parent / "horizontal_computational_grid",
    SCRIPT_DIR.parent / "vertical_computational_grid",
    SCRIPT_DIR.parent / "Horizontal Computational Grid",
    SCRIPT_DIR.parent / "Vertical Computational Grid",
    SCRIPT_DIR.parent / "Horizontal_Computational_Grid",
    SCRIPT_DIR.parent / "Vertical_Computational_Grid",
]


def safe_filename(name):
    """Convert a display name to a safe filename."""
    if not name:
        return "unknown"
    name = str(name)
    name = name.replace('/', '-').replace('\\', '-').replace(':', '-')
    name = name.replace('<', '').replace('>', '').replace('"', '')
    name = name.replace('|', '-').replace('?', '').replace('*', '')
    return name.strip()


def get_display_name(data):
    """Get display name: ui_label (if non-empty) or validation_key."""
    ui_label = data.get("ui_label", "")
    if ui_label and isinstance(ui_label, str) and ui_label.strip():
        return ui_label.strip()
    
    validation_key = data.get("validation_key", "")
    if validation_key and isinstance(validation_key, str) and validation_key.strip():
        return validation_key.strip()
    
    return data.get("@id", "unknown")


# Inline template for grid pages
GRID_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ name | e }} | {{ grid_type }} Grid</title>
    <link rel="stylesheet" href="../stylesheets/emd-page.css">
</head>
<body class="emd-page">
    <div class="emd-container">
        <header class="emd-header">
            <nav class="emd-breadcrumb">
                <a href="../">← Back to Documentation</a>
                <span>|</span>
                <a href="https://emd.mipcvs.dev/" target="_blank">EMD Registry</a>
                <span>→</span>
                <span>{{ grid_type }} Grids</span>
                <span>→</span>
                <span>{{ name | e }}</span>
            </nav>
            <div class="emd-badge">{{ grid_type }} Grid</div>
            <h1 class="emd-title">{{ name | e }}</h1>
            {% if validation_key %}
            <p class="emd-long-name">{{ validation_key | e }}</p>
            {% endif %}
            <p class="emd-subtitle">{{ description | e }}</p>
        </header>

        <main>
            <!-- Properties -->
            <section class="emd-section expanded">
                <div class="emd-section-header" onclick="toggleSection(this)">
                    <div class="emd-section-title-wrapper">
                        <div class="emd-section-icon">{{ icons.grid | safe }}</div>
                        <h2 class="emd-section-title">Grid Properties</h2>
                    </div>
                    <div class="emd-section-toggle">{{ icons.chevron | safe }}</div>
                </div>
                <div class="emd-section-content">
                    <div class="emd-section-body">
                        <div class="emd-section-divider"></div>
                        <div class="emd-tech-grid">
                            {% for prop in properties %}
                            <div class="emd-tech-item">
                                <div class="emd-tech-label">{{ prop.label | e }}</div>
                                <div class="emd-tech-value">{{ prop.value | e }}</div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </section>

            {% if subgrids %}
            <!-- Subgrids -->
            <section class="emd-section expanded">
                <div class="emd-section-header" onclick="toggleSection(this)">
                    <div class="emd-section-title-wrapper">
                        <div class="emd-section-icon">{{ icons.coupling | safe }}</div>
                        <h2 class="emd-section-title">Subgrids <span class="emd-section-count">({{ subgrids | length }})</span></h2>
                    </div>
                    <div class="emd-section-toggle">{{ icons.chevron | safe }}</div>
                </div>
                <div class="emd-section-content">
                    <div class="emd-section-body">
                        <div class="emd-section-divider"></div>
                        <div class="emd-domains-grid">
                        {% for sg in subgrids %}
                        <div class="emd-domain-card">
                            <div class="emd-domain-card-header">
                                <span class="emd-domain-card-title">{{ sg.name | e }}</span>
                                <span class="emd-domain-card-type">Subgrid</span>
                            </div>
                            <div class="emd-domain-card-id">@id: {{ sg.id | e }}</div>
                            {% if sg.description %}
                            <p class="emd-domain-card-description">{{ sg.description | e }}</p>
                            {% endif %}
                        </div>
                        {% endfor %}
                        </div>
                    </div>
                </div>
            </section>
            {% endif %}

            <!-- Technical Details -->
            <section class="emd-section">
                <div class="emd-section-header" onclick="toggleSection(this)">
                    <div class="emd-section-title-wrapper">
                        <div class="emd-section-icon">{{ icons.tech | safe }}</div>
                        <h2 class="emd-section-title">Technical Details</h2>
                    </div>
                    <div class="emd-section-toggle">{{ icons.chevron | safe }}</div>
                </div>
                <div class="emd-section-content">
                    <div class="emd-section-body">
                        <div class="emd-section-divider"></div>
                        <div class="emd-tech-grid">
                            <div class="emd-tech-item">
                                <div class="emd-tech-label">Resource Identifier (@id)</div>
                                <div class="emd-tech-value">{{ id | e }}</div>
                            </div>
                            <div class="emd-tech-item">
                                <div class="emd-tech-label">Validation Key</div>
                                <div class="emd-tech-value">{{ validation_key | e if validation_key else 'N/A' }}</div>
                            </div>
                            <div class="emd-tech-item">
                                <div class="emd-tech-label">Resource Types (@type)</div>
                                <div class="emd-type-badges">
                                    {% for t in types %}<span class="emd-type-badge">{{ t | e }}</span>{% endfor %}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </main>

        <footer class="emd-footer">
            <p class="emd-footer-text">Data sourced from <a href="https://emd.mipcvs.dev/" class="emd-footer-link" target="_blank">EMD Registry</a> · Part of the <a href="https://wcrp-cmip.org/" class="emd-footer-link" target="_blank">WCRP CMIP</a> initiative · Generated {{ generated_date }}</p>
        </footer>
    </div>
    <script>
    function toggleSection(header) { header.parentElement.classList.toggle('expanded'); }
    </script>
</body>
</html>
'''


def parse_list_item(item):
    """Parse a list item (string or object)."""
    if is_none_value(item):
        return None
    if isinstance(item, str):
        return {"id": item, "name": item.replace("-", " ").replace("_", " ").title(), "description": ""}
    if isinstance(item, dict):
        return {
            "id": item.get("@id", ""),
            "name": item.get("ui_label") or item.get("@id", "").replace("-", " ").replace("_", " ").title(),
            "description": item.get("description", "")
        }
    return None


def prepare_horizontal_context(data):
    """Prepare context for horizontal grid template."""
    grid_id = data.get("@id") or data.get("validation_key") or "unknown"
    name = get_display_name(data)
    description = data.get("description") or "No description available."
    
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]
    
    # Build properties list
    properties = []
    
    if data.get("arrangement"):
        properties.append({"label": "Arrangement", "value": data["arrangement"]})
    
    # Parse subgrids
    subgrids = []
    sg_data = data.get("horizontal_subgrids", [])
    if isinstance(sg_data, list):
        for sg in sg_data:
            parsed = parse_list_item(sg)
            if parsed:
                subgrids.append(parsed)
    
    return {
        "id": grid_id,
        "name": name,
        "description": escape_html(description),
        "validation_key": data.get("validation_key", ""),
        "types": types,
        "grid_type": "Horizontal Computational",
        "properties": properties,
        "subgrids": subgrids,
        "icons": ICONS,
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    }


def prepare_vertical_context(data):
    """Prepare context for vertical grid template."""
    grid_id = data.get("@id") or data.get("validation_key") or "unknown"
    name = get_display_name(data)
    description = data.get("description") or "No description available."
    
    types = data.get("@type", [])
    if isinstance(types, str):
        types = [types]
    
    # Build properties list
    properties = []
    
    if data.get("vertical_coordinate"):
        vc = data["vertical_coordinate"]
        if isinstance(vc, dict):
            properties.append({"label": "Vertical Coordinate", "value": vc.get("ui_label") or vc.get("@id", "")})
        else:
            properties.append({"label": "Vertical Coordinate", "value": str(vc)})
    
    if data.get("n_z"):
        properties.append({"label": "Number of Levels (n_z)", "value": str(data["n_z"])})
    
    if data.get("top_layer_thickness"):
        properties.append({"label": "Top Layer Thickness", "value": str(data["top_layer_thickness"])})
    
    if data.get("bottom_layer_thickness"):
        properties.append({"label": "Bottom Layer Thickness", "value": str(data["bottom_layer_thickness"])})
    
    if data.get("total_thickness"):
        properties.append({"label": "Total Thickness", "value": str(data["total_thickness"])})
    
    return {
        "id": grid_id,
        "name": name,
        "description": escape_html(description),
        "validation_key": data.get("validation_key", ""),
        "types": types,
        "grid_type": "Vertical Computational",
        "properties": properties,
        "subgrids": [],
        "icons": ICONS,
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    }


def setup_jinja_env():
    """Setup Jinja2 environment with inline template."""
    env = Environment(loader=BaseLoader(), autoescape=False)
    return env


def process_grid(env, template, endpoint, entry_id, output_dir, prepare_func, pbar=None):
    """Process a single grid entry."""
    if pbar:
        pbar.set_description(f"Processing {entry_id[:25]}")
    
    try:
        data = fetch_entry(endpoint, entry_id)
        if not data:
            if pbar:
                pbar.write(f"  No data for {entry_id}")
            return False
        
        # Get display name for filename
        display_name = get_display_name(data)
        filename = safe_filename(display_name) + ".html"
        output_path = output_dir / filename
        
        if pbar:
            pbar.write(f"  {entry_id} -> {filename}")
        
        context = prepare_func(data)
        html = template.render(**context)
        output_path.write_text(html, encoding="utf-8")
        return True
    except Exception as e:
        if pbar:
            pbar.write(f"  Error {entry_id}: {e}")
        else:
            print(f"  Error {entry_id}: {e}")
        return False


def clear_output_dir(output_dir):
    """Remove all .html files from output directory."""
    if output_dir.exists():
        files = list(output_dir.glob("*.html"))
        for f in files:
            f.unlink()


def remove_old_dirs():
    """Remove old directories."""
    import shutil
    for old_dir in OLD_DIRS:
        if old_dir.exists() and old_dir not in [OUTPUT_DIR_H, OUTPUT_DIR_V]:
            shutil.rmtree(old_dir)
            print(f"  Removed old directory: {old_dir.name}")


def main():
    print("Computational Grid Page Generator")
    print("=" * 40)
    
    # Initialize data loader
    init_loader()
    
    # Remove old directories
    remove_old_dirs()
    
    env = setup_jinja_env()
    template = env.from_string(GRID_TEMPLATE)
    
    total_success = 0
    total_count = 0
    
    # Process horizontal grids
    OUTPUT_DIR_H.mkdir(parents=True, exist_ok=True)
    clear_output_dir(OUTPUT_DIR_H)
    print(f"  Output dir: {OUTPUT_DIR_H.name}")
    
    h_entries = list_entries("horizontal_computational_grid")
    print(f"\nHorizontal Computational Grids: {len(h_entries)}")
    
    if h_entries:
        with tqdm(h_entries, desc="Horizontal grids", unit="file") as pbar:
            for entry_id in pbar:
                if process_grid(env, template, "horizontal_computational_grid", entry_id, 
                               OUTPUT_DIR_H, prepare_horizontal_context, pbar):
                    total_success += 1
                total_count += 1
    
    # Process vertical grids
    OUTPUT_DIR_V.mkdir(parents=True, exist_ok=True)
    clear_output_dir(OUTPUT_DIR_V)
    print(f"  Output dir: {OUTPUT_DIR_V.name}")
    
    v_entries = list_entries("vertical_computational_grid")
    print(f"\nVertical Computational Grids: {len(v_entries)}")
    
    if v_entries:
        with tqdm(v_entries, desc="Vertical grids", unit="file") as pbar:
            for entry_id in pbar:
                if process_grid(env, template, "vertical_computational_grid", entry_id,
                               OUTPUT_DIR_V, prepare_vertical_context, pbar):
                    total_success += 1
                total_count += 1
    
    print(f"\nDone: {total_success}/{total_count} grids generated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
else:
    main()
