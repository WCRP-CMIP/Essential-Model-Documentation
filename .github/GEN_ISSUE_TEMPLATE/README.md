# EMD Issue Template Generator

This folder contains CSV and Python files that are used to generate GitHub issue templates for Essential Model Documentation (EMD) registrations.

## Structure

Each template consists of two files:

```
GEN_ISSUE_TEMPLATE/
├── template_name.csv    # Field definitions
├── template_name.py     # Configuration and CV data
└── ...
```

## Templates

| Template | Purpose |
|----------|---------|
| `model.csv/.py` | Top-level model registration |
| `model_component.csv/.py` | Model component registration |
| `model_family.csv/.py` | Model family registration |
| `horizontal_computational_grid.csv/.py` | Horizontal computational grid |
| `horizontal_subgrid.csv/.py` | Horizontal subgrid |
| `horizontal_grid_cells.csv/.py` | Horizontal grid cells |
| `vertical_computational_grid.csv/.py` | Vertical computational grid |
| `reference.csv/.py` | Reference/citation |
| `general_issue.csv/.py` | General issues and questions |

## Generation

Templates are generated using the `cmipld` package:

```bash
# Generate all templates
template_update
```

Or via GitHub Actions workflow when this folder is updated.

## CSV Field Structure

| Column | Description |
|--------|-------------|
| `field_order` | Order of fields (1, 2, 3...) |
| `field_type` | `dropdown`, `input`, `textarea`, `multi-select`, `markdown` |
| `field_id` | Unique identifier |
| `label` | Display label |
| `description` | Help text (supports `\n` for line breaks) |
| `data_source` | Data source from Python file |
| `required` | `true` or `false` |
| `placeholder` | Placeholder text |
| `options_type` | `dict_keys`, `list`, `dict_multiple`, `list_with_na` |
| `default_value` | Default selection |
