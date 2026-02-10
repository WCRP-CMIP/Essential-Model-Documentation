# MkDocs Build System

This documentation site uses MkDocs with Material theme and a custom build pipeline for generating dynamic pages from the EMD Registry.

## Overview

The build system has three main stages:

1. **Pre-build Generation** - Python scripts fetch JSON-LD data and generate HTML pages
2. **Navigation Generation** - Automatic navigation built from directory structure
3. **MkDocs Build** - Standard MkDocs compilation and static site generation

## Directory Structure

```
Essential-Model-Documentation/
├── docs/                          # Documentation source
│   ├── model/                     # Generated model pages
│   ├── model_component/           # Generated component pages
│   ├── model_family/              # Generated family pages
│   ├── scripts/                   # Generation scripts
│   │   ├── helpers/               # Shared utilities
│   │   │   ├── __init__.py        # Icons, keywords, utilities
│   │   │   ├── utils.py           # Parsing functions
│   │   │   └── templates/         # Jinja2 templates
│   │   ├── generate_models.py
│   │   ├── generate_model_components.py
│   │   └── generate_model_families.py
│   ├── stylesheets/               # CSS styles
│   │   ├── shared-page.css        # Common styles (emd-* classes)
│   │   ├── model-page.css         # Model-specific styles
│   │   └── component-page.css     # Component-specific styles
│   └── SUMMARY.md                 # Auto-generated navigation
│
└── src/mkdocs/
    ├── mkdocs.yml                 # MkDocs configuration
    ├── hooks/
    │   ├── pre_build.py           # Runs generators before build
    │   └── generate_nav.py        # Creates SUMMARY.md
    └── overrides/                 # Theme customizations
```

## Build Pipeline

### Stage 1: Pre-build Hook

The `pre_build.py` hook runs before MkDocs starts building. It executes all `generate_*.py` scripts in `docs/scripts/` as subprocesses:

```python
def on_pre_build(config):
    # Find all generate_*.py scripts
    scripts = sorted(scripts_dir.glob("generate_*.py"))
    
    # Execute each and wait for completion
    for script_path in scripts:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            timeout=120
        )
```

This ensures generated HTML files exist before MkDocs copies them to the output directory.

### Stage 2: Generator Scripts

Each generator script:

1. Fetches JSON-LD data from the EMD Registry via `cmipld`
2. Parses and transforms the data
3. Renders HTML using Jinja2 templates
4. Writes files to the appropriate `docs/` subdirectory

Example flow for model components:

```python
# Fetch from registry
data = cmipld.get("https://emd.mipcvs.dev/model_component/nemo-version-3-6.json")

# Prepare template context
context = prepare_template_context(data)

# Render and write
html = template.render(**context)
output_path.write_text(html)
```

### Stage 3: Navigation Generation

The `generate_nav.py` hook creates `SUMMARY.md` by scanning the docs directory:

- Discovers all `.md` and `.html` files
- Builds hierarchical navigation from folder structure
- Adds custom links from `links.yml`
- Generates proper titles from filenames

### Stage 4: MkDocs Build

Standard MkDocs compilation with Material theme features:

- Search indexing
- Dark/light mode toggle
- Code syntax highlighting
- Responsive navigation

## Configuration

### mkdocs.yml

Key settings:

```yaml
plugins:
  - search
  - literate-nav:
      nav_file: SUMMARY.md

hooks:
  - hooks/pre_build.py      # Runs first - generates pages
  - hooks/generate_nav.py   # Runs second - builds navigation
```

### Adding New Generated Pages

1. Create a generator script in `docs/scripts/generate_*.py`
2. Create a Jinja2 template in `docs/scripts/helpers/templates/`
3. Create output directory in `docs/`
4. The pre_build hook will automatically pick it up

## Styling System

The CSS uses a shared base with page-specific extensions:

### shared-page.css

Common styles with `emd-` prefix:

- `.emd-container` - Page wrapper
- `.emd-header` - Header section
- `.emd-section` - Collapsible sections
- `.emd-domain-card` - Info cards
- `.emd-tech-grid` - Technical details grid

### Page-specific CSS

Each page type imports shared and adds specifics:

```css
/* component-page.css */
@import url('shared-page.css');

.emd-subgrids-section { /* component-only */ }
```

## Templates

Templates use Jinja2 with these conventions:

- `{{ variable | e }}` - HTML escaped output
- `{{ variable | safe }}` - Raw HTML (for icons, highlighted text)
- `{% if condition %}` - Conditional blocks
- `{{ icons.name | safe }}` - SVG icon injection

### Available Icons

Defined in `helpers/__init__.py`:

- `description` - Document icon
- `domain` - Globe icon
- `grid` - Grid icon
- `coupling` - Link icon
- `tech` - Code icon
- `reference` - Book icon
- `chevron` - Collapse/expand arrow

## Running Locally

```bash
cd src/mkdocs
pip install -r requirements.txt
mkdocs serve
```

The pre_build hook runs on each reload, regenerating pages from the registry.

## Troubleshooting

### Pages not appearing in navigation

- Check that files are in `docs/` before `generate_nav.py` runs
- Verify the pre_build hook completed successfully
- Check for errors in script output

### Styles not loading

- Ensure CSS imports use correct relative paths
- Check that `shared-page.css` exists
- Verify `body.emd-page` class is set

### Generator script errors

- Scripts have 120 second timeout
- Check `cmipld` is installed
- Verify network access to emd.mipcvs.dev
