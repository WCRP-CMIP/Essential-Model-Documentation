# Generator Scripts

The generator scripts fetch data from the EMD Registry and create styled HTML pages.

## Scripts Overview

| Script | Output Directory | Registry Endpoint |
|--------|-----------------|-------------------|
| `generate_models.py` | `docs/model/` | `/model/` |
| `generate_model_components.py` | `docs/model_component/` | `/model_component/` |
| `generate_model_families.py` | `docs/model_family/` | `/model_family/` |

## Common Structure

All generators follow the same pattern:

```python
#!/usr/bin/env python3
import cmipld
from jinja2 import Environment, FileSystemLoader
from helpers import ICONS, HIGHLIGHT_KEYWORDS, escape_html
from helpers.utils import parse_references, highlight_keywords

# Configuration
BASE_URL = "https://emd.mipcvs.dev/model_component"
TEMPLATE_DIR = SCRIPT_DIR / "helpers" / "templates"
OUTPUT_DIR = SCRIPT_DIR.parent / "model_component"

# Items to generate
ITEMS = ["item1.json", "item2.json"]

def prepare_template_context(data):
    """Transform raw JSON-LD to template variables."""
    return {
        "id": data.get("@id"),
        "name": data.get("name"),
        "icons": ICONS,
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
        # ... more fields
    }

def main():
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("template.html.j2")
    
    for filename in ITEMS:
        data = cmipld.get(f"{BASE_URL}/{filename}")
        context = prepare_template_context(data)
        html = template.render(**context)
        (OUTPUT_DIR / filename.replace(".json", ".html")).write_text(html)
    
    cmipld.client.close()

if __name__ == "__main__":
    main()
```

## Adding New Items

To add a new model component, edit `generate_model_components.py`:

```python
MODEL_COMPONENTS = [
    "arpege-climat-version-6-3.json",
    "nemo-version-3-6.json",
    "gelato-version-6.json",
    "surfex-version-8-0.json",
    "your-new-component.json",  # Add here
]
```

## Parsing Functions

### parse_domain(data)

Handles domain data in various formats:

```python
# String input
parse_domain("atmosphere")
# Returns: {"id": "atmosphere", "name": "Atmosphere", ...}

# Dict input
parse_domain({"@id": "atmos", "ui_label": "Atmosphere"})
# Returns: {"id": "atmos", "name": "Atmosphere", ...}

# None handling
parse_domain("none")  # Returns None
parse_domain(None)    # Returns None
```

### parse_institution(data)

Extracts institution details including location:

```python
parse_institution({
    "@id": "cnrm",
    "labels": "Centre National...",
    "location": {"name": "Toulouse", "country_name": "France"}
})
# Returns: {
#   "id": "cnrm",
#   "name": "Centre National...",
#   "location": {"name": "Toulouse", "country": "France"}
# }
```

### highlight_keywords(text, extra_keywords)

Wraps keywords in `<strong>` tags:

```python
highlight_keywords(
    "The NEMO ocean model uses tripolar grids",
    ["NEMO"]
)
# Returns: "The <strong>NEMO</strong> <strong>ocean</strong> <strong>model</strong>..."
```

## Template Context

Each generator creates a context dict with:

| Field | Description |
|-------|-------------|
| `id` | Resource identifier (@id) |
| `name` | Display name |
| `description` | Raw description text |
| `description_highlighted` | Description with keyword highlighting |
| `validation_key` | EMD validation key |
| `context_url` | JSON-LD context URL |
| `types` | List of @type values |
| `icons` | Dict of SVG icon strings |
| `raw_json` | Stringified JSON for copy feature |
| `generated_date` | Timestamp string |

Plus type-specific fields like `horizontal_grid`, `institution`, etc.

## Error Handling

Scripts handle errors gracefully:

```python
try:
    data = cmipld.get(url)
    if not data:
        print(f"Warning: No data for {filename}")
        return False
    # ... process
    return True
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
    return False
```

The pre_build hook captures output and continues even if individual items fail.

## Dependencies

Required packages (in `requirements.txt`):

```
cmipld>=0.1.0
jinja2>=3.0.0
```

The `cmipld` package provides the registry client:

```python
import cmipld

# Fetch JSON-LD with dereferencing
data = cmipld.get("https://emd.mipcvs.dev/model/cnrm-esm2-1e.json")

# Always close when done
cmipld.client.close()
```
