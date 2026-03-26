# EMD Issue Template Generator

Templates for Essential Model Documentation (EMD) registration.

## Registration Workflow

```
Stage 1: Grid Registration
├── 1a: Grid Cells & Subgrid     → Creates g### + s###
├── 1b: Horizontal Grid          → Creates c### (needs s###)
└── 1c: Vertical Grid            → Creates v### (parallel to 1b)

Stage 2: Model Family (if new)   → Creates family entry

Stage 3: Model Component         → Creates component + component_config
                                   (needs c###, v###, family)

Stage 4: Model (Source ID)       → Creates model/source_id
                                   (needs component_configs, family)
```

## Template Files

Each template has three files:

| File | Purpose |
|------|---------|
| `.csv` | Form structure (fields, order, types) |
| `.py` | Dropdown options data |
| `.json` | Metadata and collapsible guidance |

## Templates

| Stage | Template | Creates |
|-------|----------|---------|
| 1a | grid_cell_and_subgrid | g### (grid cells) + s### (subgrid) |
| 1b | horizontal_computational_grid | c### (horizontal grid) |
| 1c | vertical_computational_grid | v### (vertical grid) |
| 2 | model_family | Model family entry |
| 3 | model_component | Component + component_config |
| 4 | model | Model (source_id for CMIP7) |
| - | general_issue | Issues and questions |

## Field Definitions (CSV)

| Column | Description |
|--------|-------------|
| field_order | Display order |
| field_type | dropdown, input, textarea, multi-select, markdown |
| field_id | Unique identifier |
| label | Display label |
| description | Brief description (short!) |
| data_source | Key in .py DATA dict |
| required | true/false |
| placeholder | Example value |
| options_type | list, list_with_na |
| default_value | Default selection |

## Design Principles

1. **Short descriptions** - Brief hints only
2. **Examples in placeholders** - Show format
3. **Detailed guidance in JSON** - Collapsible sections
4. **Lean Python files** - Just DATA dict, no logic
5. **No duplication** - Single source of truth
6. **Stage labels** - Clear workflow progression
