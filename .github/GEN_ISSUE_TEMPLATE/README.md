# EMD Issue Template Generator

This folder contains CSV, Python, and JSON files that generate GitHub issue templates for Essential Model Documentation (EMD) registrations.

## 🎯 Simplified Submission Process

The streamlined process **reduces submission burden by 50-60%** by bundling grid cells with subgrids, and auto-generating component configs.

## Reusable Component Pattern

Each template consists of **three files**:

```
GEN_ISSUE_TEMPLATE/
├── template_name.csv     # Field definitions
├── template_name.py      # Configuration and CV data
└── template_name.json    # Template metadata and field guidance
```

### File Responsibilities

**`.csv` files** - Define form structure:
- Field order, type, and validation
- Labels and placeholders
- Data sources
- Required fields

**`.py` files** - Provide dropdown data:
- Load CVs from CMIP-LD
- Define options lists
- Template configuration
- Data transformations

**`.json` files** - Reusable metadata:
- Template name and description
- Issue labels and categories
- Field-specific guidance (expandable help text)
- Centralized guidance reduces CSV clutter

## Templates Overview

| Template | Creates | Dependencies | Files |
|----------|---------|--------------|-------|
| **grid_cells_and_subgrid** | Grid cells + Subgrids (2-3 entities) | None | .csv, .py, .json |
| **horizontal_computational_grid** | H-Grid (1 entity) | Subgrids | .csv, .py, .json |
| **vertical_computational_grid** | V-Grid (1 entity) | None | .csv, .py, .json |
| **model_component** | Component + Config (2 entities) | Grids | .csv, .py, .json |
| **model_family** | Family (1 entity) | None | .csv, .py, .json |
| **model** | Model (1 entity) | Family, Configs | .csv, .py, .json |
| **general_issue** | Discussion | None | .csv, .py, .json |

## Submission Flow

### Phase 1: Grids (3 issues per config)

```
1. grid_cells_and_subgrid → s100, s101
   ↓
2. horizontal_computational_grid (refs s100, s101) → c100
   ↓ (parallel)
3. vertical_computational_grid → v100
```

### Phase 2: Family (if new)

```
4. model_family → cnrm-cm
```

### Phase 3: Components (1 issue per component)

```
5. model_component (refs c100, v100)
   → Creates: component + component_config
   → Returns: atmosphere_arpege-climat-version-6-3_c100_v100
```

### Phase 4: Model

```
6. model (refs all component_configs + relationships)
   → Creates: model
   → Returns: cnrm-esm2-1e (CMIP7 source_id)
```

## JSON Metadata Structure

Template metadata centralizes reusable information:

```json
{
  "name": "Template Display Name",
  "description": "Short template description",
  "title": "[EMD] Template Title",
  "labels": ["emd-submission", "category", "Review"],
  "issue_category": "template_name",
  "dropdown_title": "Completion Guidance",
  "field_guidance": {
    "field_id_1": "Detailed guidance for field 1...",
    "field_id_2": "Detailed guidance for field 2..."
  }
}
```

### Benefits of JSON Metadata

✅ **Centralized guidance** - Field help in one place
✅ **Reduced CSV clutter** - CSV stays focused on structure
✅ **Reusable** - Same guidance across template versions
✅ **Expandable** - Collapsible dropdowns in GitHub UI
✅ **Maintainable** - Update guidance without touching CSV

## Field Guidance Pattern

Guidance is shown in expandable dropdowns in the GitHub issue form:

**In CSV:**
```csv
field_id,component,Component Type,Select component type,component,true,...
```

**In JSON:**
```json
{
  "field_guidance": {
    "component": "**Component types:**\n- atmosphere: Atmospheric circulation\n- ocean: Ocean circulation\n- ...\n\nDetailed explanations here."
  }
}
```

**Rendered as:**
```
Component Type *
[Dropdown: Select component type]
> Completion Guidance ▼
  Component types:
  - atmosphere: Atmospheric circulation
  - ocean: Ocean circulation
  ...
```

## CSV Field Structure

| Column | Description |
|--------|-------------|
| `field_order` | Display order (1, 2, 3...) |
| `field_type` | `dropdown`, `input`, `textarea`, `multi-select`, `markdown` |
| `field_id` | Unique identifier (referenced in .json guidance) |
| `label` | Display label |
| `description` | Brief description (detailed guidance in .json) |
| `data_source` | Data key from .py file |
| `required` | `true` or `false` |
| `placeholder` | Example text |
| `options_type` | `dict_keys`, `list`, `dict_multiple`, `list_with_na` |
| `default_value` | Default selection index |

## Python Data Structure

```python
# template_name.py

import cmipld
from cmipld.utils.ldparse import name_multikey_extract

# Data for dropdowns
DATA = {
    # From controlled vocabularies
    'component': name_multikey_extract(
        cmipld.get('constants:scientific-domain/graph.jsonld'),
        ['id', 'validation_key'], 'validation_key'
    ),
    
    # Hardcoded options
    'arrangement': [
        'arakawa-a',
        'arakawa-b', 
        'arakawa-c',
        'unstaggered'
    ],
    
    # Issue metadata
    'issue_kind': ['New', 'Modify']
}
```

## Configuration File

**_config.json** organizes templates:

```json
{
  "grouping": {
    "Grid Registration": ["grid_cells_and_subgrid", "horizontal_computational_grid", "vertical_computational_grid"],
    "Component Registration": ["model_component"],
    "Model Registration": ["model_family", "model"]
  },
  "template_order": [...],
  "deprecated": ["horizontal_grid_cells", "horizontal_subgrid"]
}
```

## Generation

Templates are generated via:

```bash
# Using cmipld
template_update

# Or via GitHub Actions (automatic on file changes)
```

## Workflow Integration

Templates auto-generate when:
1. Any file in GEN_ISSUE_TEMPLATE/ changes
2. Workflow manually triggered
3. Scheduled cron job runs

Workflow: `.github/workflows/issue-templates.yml`

## Template Files

### Active Templates (7)
✅ grid_cells_and_subgrid (.csv, .py, .json)
✅ horizontal_computational_grid (.csv, .py, .json)
✅ vertical_computational_grid (.csv, .py, .json)
✅ model_component (.csv, .py, .json)
✅ model (.csv, .py, .json)
✅ model_family (.csv, .py, .json)
✅ general_issue (.csv, .py, .json)

### Configuration
✅ _config.json (template grouping and order)

### Deprecated (reference only)
📦 horizontal_grid_cells (.csv, .py)
📦 horizontal_subgrid (.csv, .py)
📦 grid_bundle (.csv) - earlier proposal

## Example: Adding Field Guidance

**Instead of cluttering CSV:**
```csv
field_id,component,Component Type,Select the component type. Options: atmosphere (atmospheric circulation and dynamics), ocean (ocean circulation and thermodynamics), land-surface (soil vegetation snow hydrology), ...[500 more characters],component,true,...
```

**Separate into CSV + JSON:**

**CSV (concise):**
```csv
field_id,component,Component Type,Select component type,component,true,...
```

**JSON (detailed):**
```json
{
  "field_guidance": {
    "component": "**Component types:**\n- **atmosphere**: Atmospheric circulation and dynamics\n- **ocean**: Ocean circulation and thermodynamics\n- **land-surface**: Soil, vegetation, snow, hydrology\n...[detailed explanations]"
  }
}
```

## Benefits

### Maintainability
✅ Update guidance without touching CSV
✅ Share guidance across related fields
✅ Version control friendly

### User Experience
✅ Expandable guidance (doesn't clutter form)
✅ Consistent help format
✅ Rich formatting (markdown supported)

### Development
✅ Separate concerns (structure vs data vs guidance)
✅ Easier testing
✅ Reusable patterns

## Next Steps

1. ✅ CSV templates updated
2. ✅ JSON metadata created
3. [ ] Update Python files (.py) with new logic
4. [ ] Test template generation
5. [ ] Update workflows
6. [ ] Deploy

---

**Last Updated:** February 9, 2026  
**Pattern:** CSV (structure) + PY (data) + JSON (guidance)  
**Status:** Ready for Python implementation
