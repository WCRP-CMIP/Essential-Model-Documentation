# New Issue Processing Workflow

This document describes how the EMD issue submission and processing system works, from user submission through data file creation.

## Overview

The system converts GitHub issue submissions into validated JSON-LD data files through a multi-stage pipeline:

1. **Template** - User fills out a GitHub issue form
2. **Parse** - Issue body is parsed and cleaned
3. **Handler** - Handler script processes the data
4. **Validate** - JSON-LD structure is validated and sorted
5. **File** - Data is written to repository as `.json`

## Components

### 1. Issue Templates (`../GEN_ISSUE_TEMPLATE/`)

Each stage has a CSV template that defines:
- **fields** - Input fields (dropdowns, text, multi-select, etc.)
- **labels** - User-facing labels with descriptions
- **data sources** - Where to fetch dropdown options
- **required** - Whether field is mandatory
- **default_value** - For certain dropdowns (list_with_na)

**Grid-related templates:**
- `horizontal_grid_cells.csv` (Stage 1)
- `horizontal_computational_grid.csv` (Stage 2a)
- `vertical_computational_grid.csv` (Stage 2b)

These are compiled into YAML by `template_generate`.

### 2. Issue Handler Scripts (`./`)

Each issue type has a Python handler script that:
- **Processes** issue data
- **Generates** @id if needed
- **Validates** fields
- **Enriches** data with computed properties

**Handler files:**
- `horizontal_grid_cells.py`
- `horizontal_computational_grid.py`
- `vertical_computational_grid.py`
- `model_component.py`
- `model_family.py`
- `model.py`

### 3. ID Generator (`id_generator.py`)

**For grid scripts only** - Generates unique @id from:
- **author** - GitHub username of issue submitter
- **created_at** - ISO 8601 timestamp of issue creation
- **epoch** - Seconds since epoch (Unix time)

**Format:** `author-epoch` (e.g., `daniel-ellis-1740511845`)

Used when issue doesn't provide a validation_key/label/acronym.

### 4. Processing Script (`../../../cmipld/generate/new_issue.py`)

Main orchestrator that:
1. Fetches issue from GitHub using `gh CLI`
2. Parses issue body (### Header sections)
3. Cleans placeholder values
4. Determines issue type from labels
5. Loads handler script
6. Calls `run()` to create initial data
7. Validates and writes to temp file
8. Calls `update()` to enrich data
9. Creates PR to src-data branch

## Processing Flow

### Step 1: Fetch Issue

```python
# From GitHub using gh CLI
gh issue view 42 --json 'title,body,author,labels,number,createdAt'
```

**Returns:**
- `body` - Full issue body markdown
- `author` - GitHub username
- `created_at` - ISO 8601 timestamp (e.g., "2025-02-26T15:30:45Z")
- `labels` - Array of label objects
- `number` - Issue number
- `title` - Issue title

### Step 2: Parse Issue Body

Issue body is formatted as:

```markdown
### Grid Type
Gaussian

### X Resolution
0.5

### Collaborators
user1,user2
```

Parsed into dict:
```python
{
  'grid_type': 'Gaussian',
  'x_resolution': '0.5',
  'collaborators': 'user1,user2',
  ...
}
```

**Key transformations:**
- `### ` header prefix removed
- Spaces/dashes in headers → underscores + lowercase
- Values stripped of whitespace
- Placeholder values replaced with empty strings:
  - "Not specified"
  - "_No response_"
  - "none"

### Step 3: Determine Issue Type & Find Handler

Script cycles through all non-ignored labels to find a matching handler:

```python
# Issue labels: ['horizontal_grid_cells', 'review', 'alpha']
# Ignored: {'review', 'alpha', ...}
# Relevant: ['horizontal_grid_cells']

# Cycle through labels in order:
# Check: .github/ISSUE_SCRIPT/horizontal_grid_cells.py?
# ✓ Found! Use this handler
```

**Label Matching Strategy:**
1. Parse labels and filter out ignored ones (review, alpha, keep-open, etc.)
2. For each remaining label (in order):
   - Check if `.github/ISSUE_SCRIPT/{label}.py` exists
   - If found → use that handler and stop
3. If no handler found for any label:
   - Use first label with generic handler (generic `build_data_from_issue()`)

**Example scenarios:**
- Labels: `['grid_cells', 'review']` 
  - Check `grid_cells.py` ✓ found → use grid_cells handler
- Labels: `['model', 'alpha', 'custom']`
  - Check `model.py` ✓ found → use model handler (skip alpha/custom)
- Labels: `['unknown', 'other']`
  - Check `unknown.py` ✗ not found
  - Check `other.py` ✗ not found
  - Use generic handler with issue_type='unknown'

**Output folder determination:**

Data is written to: `{output_folder}/{data_id}.json`

Where `output_folder` is determined by:
```python
FOLDER_MAPPING = {
    'institution': 'organisation',  # Special case mapping
}

folder = FOLDER_MAPPING.get(issue_type, issue_type)
# Default: use issue_type as folder name if not in mapping
```

**Examples:**
- issue_type='horizontal_grid_cells' → folder='horizontal_grid_cells/'
- issue_type='institution' → folder='organisation/' (mapped)
- issue_type='model' → folder='model/'

### Step 4: Handler `run()` - Initial Data Creation

Called **before** validation. Returns either:

**Option A: Return initial data**
```python
def run(parsed_issue, issue, dry_run=False):
    # For grid scripts: generate @id from author + timestamp
    id_result = generate_id_from_issue(issue.get('author'), issue.get('created_at'))
    
    return {
        "@context": "_context",
        "@id": id_result['id'],
        "@type": ["wcrp:horizontal_grid_cells"],
        "_submitted_by": id_result['author'],
        "_submitted_at_epoch": id_result['epoch'],
    }
```

**Option B: Return None** (uses generic handler)
```python
def run(parsed_issue, issue, dry_run=False):
    return None  # → Generic handler builds from parsed_issue
```

### Step 5: Generic Handler (if needed)

If `run()` returned `None`:

```python
def build_data_from_issue(parsed_issue, issue_type, labels):
    # Look for validation_key, consortium_name, acronym, label
    validation_key = parsed_issue.get('validation_key') or ...
    
    data_id = clean_id(validation_key)
    
    return {
        "@context": "_context",
        "@id": data_id,
        "@type": build_type_array(labels, issue_type),
        # ... copy relevant fields from parsed_issue
    }
```

**Field mapping:**
- `ui_label` ← `full_name`, `long_label`, etc.
- `description` ← description
- `url` ← webpage, website, etc.

Fields are filtered to exclude:
- Empty values
- Placeholder strings
- Known control fields (issue_kind, validation_key, etc.)

### Step 6: Validation

Data is written to temp file and validated by `JSONValidator`:
- Checks JSON-LD structure
- Sorts fields
- Ensures @context, @id, @type present

### Step 7: Handler `update()` - Enrichment

Called **after** validation. Takes validated data and enriches it:

```python
def update(data, parsed_issue, issue, dry_run=False):
    # Validate grid parameters
    if 'x_resolution' in data:
        try:
            x_res = float(data.get('x_resolution', 0))
            if x_res > 0:
                data['resolution_valid'] = True
        except ValueError:
            pass
    
    # Parse comma-separated lists
    if 'subgrids' in data:
        data['subgrids'] = [s.strip() for s in data['subgrids'].split(',')]
    
    return data
```

Common enrichments:
- Parse lists from comma-separated strings
- Validate numeric fields
- Normalize enum values
- Add computed/derived fields

### Step 8: File Output & Folder Mapping

Data is written to a folder based on the issue type:

**Folder determination:**
```python
FOLDER_MAPPING = {
    'institution': 'organisation',  # Exception: institution → organisation
}

folder = FOLDER_MAPPING.get(issue_type, issue_type)
# If not in mapping, use issue_type as folder name
```

**Final file path:**
```
{output_folder}/{data_id}.json
```

**Examples:**
- issue_type='horizontal_grid_cells', data_id='daniel-ellis-1740511845'
  - Path: `horizontal_grid_cells/daniel-ellis-1740511845.json`
  
- issue_type='model_family', data_id='hadgem3'
  - Path: `model_family/hadgem3.json`
  
- issue_type='institution', data_id='uk-met-office'
  - Path: `organisation/uk-met-office.json` (mapped from 'institution')

### Step 9: PR Creation

A pull request is created with:
- **Target branch:** `src-data`
- **Title:** Formatted from issue type and data_id
- **Commit message:** With author co-author metadata
- **Linked to:** Original issue number

## ID Generation (Grid Scripts Only)

### When Used

When issue lacks:
- `validation_key`
- `consortium_name`
- `acronym`
- `label`

Grid handlers call `id_generator.generate_id_from_issue()` to create unique @id.

### Format

```
{github_username}-{unix_epoch_seconds}
```

Examples:
- `daniel-ellis-1740511845` - submitted Feb 26, 2025, 3:30 PM UTC
- `alice-smith-1707129600` - submitted Feb 5, 2025, 4:00 PM UTC

### Implementation

```python
from .id_generator import generate_id_from_issue

id_result = generate_id_from_issue(
    author='daniel-ellis',
    created_at='2025-02-26T15:30:45Z'
)

# Returns:
{
    'author': 'daniel-ellis',
    'epoch': 1740511845,
    'id': 'daniel-ellis-1740511845'
}
```

## Dry Run Testing

Test issue processing without making changes:

```bash
cd /Users/daniel.ellis/WIPwork/CMIP-LD
python -m cmipld.generate.new_issue --issue 42 --dry-run
```

Output shows:
- Parsed issue content
- Generated data
- Proposed file location
- What would be committed
- No actual files written

## Placeholder Value Cleaning

The following values are treated as empty and replaced with `""`:

- `"Not specified"` (case-insensitive)
- `"_No response_"` (case-insensitive)
- `"none"` (case-insensitive)
- Already empty strings

Cleaned during `parse_issue_body()` in `new_issue.py`.

## Error Handling

### Missing Validation Key (and no author/timestamp)

```
❌ Error: No validation key or ID found
```

Solution: Provide `validation_key` or let grid handler generate from author+timestamp.

### File Already Exists (for "new" issues)

```
⚠️ File Already Exists

The file {path} already exists in the repository.

Options:
1. Change issue type to "Modify"
2. Close this issue
3. Use a different identifier
```

### Not on src-data Branch

```
❌ Error: Must be on 'src-data' branch to write files.
Current branch: {branch}
Please checkout src-data branch first.
```

## File Structure

```
.github/
├── GEN_ISSUE_TEMPLATE/          # Template sources (CSV)
│   ├── horizontal_grid_cells.csv
│   ├── horizontal_computational_grid.csv
│   ├── vertical_computational_grid.csv
│   └── ...
├── ISSUE_TEMPLATE/              # Compiled templates (YAML)
│   ├── horizontal_grid_cells.yml
│   └── ...
├── ISSUE_SCRIPT/                # Handler scripts (Python)
│   ├── id_generator.py          # Generates @id for grids
│   ├── horizontal_grid_cells.py
│   ├── horizontal_computational_grid.py
│   ├── vertical_computational_grid.py
│   └── ...
└── workflows/
    └── new-issue.yml            # GitHub Actions workflow
```

## Adding New Stages

To add a new EMD stage:

1. **Create template** `GEN_ISSUE_TEMPLATE/{name}.csv`
   - Define fields, labels, data sources
   
2. **Create handler** `ISSUE_SCRIPT/{name}.py`
   - Implement `run()` and/or `update()`
   - Import `id_generator` if generating @id
   
3. **Run template_generate** to compile CSV → YAML
   
4. **Test with dry-run**
   ```bash
   python -m cmipld.generate.new_issue --issue {num} --dry-run
   ```

## See Also

- `README.md` - Overview of EMD templates
- `GUIDELINES.md` - Detailed completion guidance
- `WORKFLOW.md` - Stage workflow diagrams
- `id_generator.py` - @id generation from author+timestamp
