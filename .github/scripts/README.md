# EMD Scripts

Utility scripts for managing Essential Model Documentation (EMD) controlled vocabulary (CV) fields and grid type references.

## Overview

These scripts help ensure that all controlled vocabulary field references use `validation_key` format instead of `ui_label` format, maintaining consistency across the EMD dataset.

## Scripts

### 1. `validate_grid_types.py`

Validates grid type references in horizontal grid cell files and converts them from `ui_label` to `validation_key` format.

**Usage:**

```bash
# Display validation report
python scripts/validate_grid_types.py --report

# Fix files automatically
python scripts/validate_grid_types.py --fix

# Fix and display report
python scripts/validate_grid_types.py --fix --report

# Run from specific directory
python scripts/validate_grid_types.py --root /path/to/EMD --fix
```

**Output:**

- Lists all valid grid types (using validation_key format)
- Lists files that need conversion (ui_label → validation_key)
- Lists any invalid or unrecognized grid types
- Reports errors encountered during processing

**Valid Grid Type Keys:**

- `rotated-pole`
- `unstructured-triangular`
- `cubic-octahedral-spectral-reduced-gaussian`
- `unstructured-polygonal`
- `reduced-gaussian`
- `yin-yang`
- `spectral-gaussian`
- `icosahedral-geodesic-dual`
- `linear-spectral-gaussian`
- `cubed-sphere`
- `spectral-reduced-gaussian`
- `icosahedral-geodesic`
- `hierarchical-discrete-global-grid`
- `unstructured`
- `stretched`
- `regular-latitude-longitude`
- `displaced-pole`
- `icosahedral`
- `tripolar`
- `unstructured-quadrilateral`
- `plane-projection`
- `regular-gaussian`
- `quadratic-spectral-gaussian`

### 2. `scan_cv_fields.py`

Scans all JSON files across EMD directories and reports on controlled vocabulary field usage patterns.

**Usage:**

```bash
# Scan all directories
python scripts/scan_cv_fields.py

# Scan specific field
python scripts/scan_cv_fields.py --field grid_type

# Scan specific folder
python scripts/scan_cv_fields.py --folder horizontal_grid_cell

# Combine options
python scripts/scan_cv_fields.py --folder horizontal_grid_cell --field grid_type

# Run from specific root directory
python scripts/scan_cv_fields.py --root /path/to/EMD
```

**Scanned Folders:**

- horizontal_grid_cell
- horizontal_computational_grid
- horizontal_subgrid
- vertical_computational_grid
- model
- model_component
- model_family

**Tracked CV Fields:**

- `grid_type`
- `grid_mapping`
- `region`
- `temporal_refinement`
- `units`
- `truncation_method`

**Output Format:**

- ✅ validation_key format: Number and examples
- ⚠️ ui_label format: Number and examples
- ❌ invalid format: Number and examples
- ❓ unknown: Number and examples

### 3. `cv_mapper.py`

Python module providing utilities for mapping CV fields between `ui_label` and `validation_key` formats.

**Usage in Code:**

```python
from scripts.cv_mapper import CVMapper

# Initialize mapper
mapper = CVMapper()

# Cache a graph's data
graph_data = [
    {
        'validation_key': 'regular-latitude-longitude',
        'ui_label': 'Regular Latitude-Longitude',
        '@id': 'regular-latitude-longitude'
    },
    # ... more entries
]
mapper.cache_graph('grid_type', graph_data)

# Convert ui_label to validation_key
key = mapper.ui_label_to_validation_key('grid_type', 'Regular Latitude-Longitude')
# Returns: 'regular-latitude-longitude'

# Convert validation_key to ui_label
label = mapper.validation_key_to_ui_label('grid_type', 'regular-latitude-longitude')
# Returns: 'Regular Latitude-Longitude'

# Check if value is already validation_key
is_key = mapper.is_already_validation_key('grid_type', 'regular-latitude-longitude')
# Returns: True

# Get statistics
stats = mapper.get_stats()
```

## Workflow

### Validating Grid Types

1. **Run validation report:**

   ```bash
   python scripts/validate_grid_types.py --report
   ```

2. **Review output** for any files in the "Files Needing Conversion" section

3. **Apply fixes:**

   ```bash
   python scripts/validate_grid_types.py --fix
   ```

4. **Verify changes:**

   ```bash
   python scripts/validate_grid_types.py --report
   ```

### Auditing CV Field Usage

1. **Scan all directories:**

   ```bash
   python scripts/scan_cv_fields.py
   ```

2. **Focus on specific field:**

   ```bash
   python scripts/scan_cv_fields.py --field grid_type
   ```

3. **Review report** and identify any ui_label entries that should be validation_key

4. **Manual fixes** or use `validate_grid_types.py` for grid_type field

## Configuration

All scripts accept a `--root` parameter to specify the EMD project root directory:

```bash
python scripts/validate_grid_types.py --root /path/to/EMD --fix --report
```

If not specified, scripts assume the current working directory is the EMD root.

## Exit Status

Scripts return exit status 0 on success, non-zero on errors.

## Dependencies

- Python 3.7+
- Standard library only (json, os, pathlib, argparse, etc.)

No external dependencies required.

## Common Issues

**Issue:** "Grid cell directory not found"

- **Solution:** Ensure you're running scripts from the EMD root directory, or use `--root` parameter

**Issue:** "No grid cell files found"

- **Solution:** Verify that JSON files exist in `horizontal_grid_cell/` directory

**Issue:** "Unknown grid_type"

- **Solution:** Check the grid type value - it may need to be added to VALID_GRID_TYPES

## Contributing

When adding new CV fields or grid types:

1. Update the `VALID_GRID_TYPES` set in `validate_grid_types.py`
2. Update the `CV_FIELDS` and `VALID_KEYS` in `scan_cv_fields.py`
3. Update `CV_GRAPHS` in `cv_mapper.py` if needed
4. Update this README with new field descriptions

## References

- [WCRP Constants Repository](https://github.com/WCRP-CMIP/WCRP-constants)
- [Grid Type Graph](https://raw.githubusercontent.com/WCRP-CMIP/WCRP-constants/refs/heads/production/grid_type/_graph.json)
