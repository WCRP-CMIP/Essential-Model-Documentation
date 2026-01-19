# Making Generated Files Searchable

## The Problem

Your scripts currently generate `.html` files:
- `/docs/model/cnrm-esm2-1e.html`
- `/docs/model_component/tactic.html`
- etc.

**MkDocs search only indexes `.md` (Markdown) files, not HTML files.**

## Solution: Change File Extension to .md

### Option 1: Quick Fix - Change Extension Only

In your generation scripts, change the output extension from `.html` to `.md`:

**In `generate_models.py`:**
```python
# Find this line (around line 33):
OUTPUT_DIR = SCRIPT_DIR.parent / "model"

# And where files are saved (look for something like):
output_file = OUTPUT_DIR / f"{model_id}.html"  # OLD

# Change to:
output_file = OUTPUT_DIR / f"{model_id}.md"  # NEW
```

**Do the same in:**
- `generate_model_components.py`
- `generate_model_families.py`

### Option 2: Wrap HTML in Markdown (Better)

If your templates generate HTML, wrap it in Markdown like this:

**Change output format:**
```python
# Instead of writing pure HTML:
with open(output_file, 'w') as f:
    f.write(html_content)

# Write as Markdown with HTML block:
with open(output_file, 'w') as f:
    f.write(f"""---
title: {title}
---

{html_content}
""")
```

This way:
1. File has `.md` extension
2. MkDocs indexes the content
3. HTML still renders properly (MkDocs Material supports HTML in Markdown)

### Option 3: Convert Templates to Markdown (Best)

Convert your Jinja2 templates from HTML to Markdown format:

**Instead of:**
```html
<h1>{{ title }}</h1>
<p>{{ description }}</p>
```

**Use:**
```markdown
# {{ title }}

{{ description }}
```

## Implementation Steps

### 1. Update generate_models.py

Find where the output file is created and change extension:

```python
# Look for something like:
output_path = OUTPUT_DIR / f"{slug}.html"

# Change to:
output_path = OUTPUT_DIR / f"{slug}.md"
```

### 2. Update generate_model_components.py

Same change:
```python
output_path = OUTPUT_DIR / f"{slug}.md"  # Changed from .html
```

### 3. Update generate_model_families.py

Same change:
```python
output_path = OUTPUT_DIR / f"{slug}.md"  # Changed from .html
```

### 4. Update Navigation Generation

In `generate_nav.py`, the code already handles both `.md` and `.html`:

```python
if item.suffix in ('.md', '.html'):  # Already supports both
```

So navigation will work with `.md` files automatically.

### 5. Rebuild

```bash
cd src/mkdocs
mkdocs build
```

## Why This Works

1. **MkDocs search** → Indexes `.md` files during build
2. **Your .md files contain HTML** → MkDocs Material renders HTML in Markdown
3. **Search works** → Because files are `.md`, they're indexed
4. **Display works** → Because HTML is valid in Markdown

## Quick Test

After making changes:

```bash
cd src/mkdocs
mkdocs serve
```

1. Search for a model name
2. It should appear in results now!

## If You Need Help

Let me know which script you want me to update, and I can make the specific changes for you!
