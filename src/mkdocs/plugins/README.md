# HTML Search Plugin for MkDocs

A custom MkDocs plugin that extends the built-in search to index HTML files.

## How It Works

1. **After build completes**, the plugin runs
2. **Scans specified directories** for HTML files
3. **Parses HTML content** using BeautifulSoup
4. **Extracts title and text** from each HTML file
5. **Adds entries to `search_index.json`** (the file Material Search uses)
6. **Search bar works normally** - users can now find HTML pages!

## Installation

### 1. Install Dependencies

```bash
cd src/mkdocs
pip install -r requirements.txt
```

This installs `beautifulsoup4` which the plugin needs.

### 2. Install the Plugin

The plugin is located in `src/mkdocs/plugins/` and is automatically loaded by MkDocs when configured in `mkdocs.yml`.

### 3. Configuration

Already configured in `mkdocs.yml`:

```yaml
plugins:
  - search:  # Standard search (indexes .md files)
      lang: en
  - html_search:  # Custom plugin (indexes .html files)
      html_dirs:
        - model
        - model_component
        - model_family
        - bidk
      max_text_length: 1000
```

## Usage

Just build your site normally:

```bash
cd src/mkdocs
mkdocs build
```

Or serve locally:

```bash
mkdocs serve
```

The plugin automatically:
- Finds HTML files in configured directories
- Parses them
- Adds them to the search index
- You'll see: `✓ HTML Search: Indexed X HTML files`

## Search Behavior

**Before plugin:**
- Search only finds `.md` (Markdown) files
- HTML files not searchable

**After plugin:**
- Search finds both `.md` AND `.html` files
- Material Search UI works exactly the same
- HTML pages appear in search results
- Clicking results takes users to HTML pages

## Configuration Options

### `html_dirs`
List of directories (relative to docs/) containing HTML files to index.

```yaml
html_dirs:
  - model
  - model_component
  - model_family
```

### `max_text_length`
Maximum characters of text to extract from each HTML file (default: 1000).

```yaml
max_text_length: 1500
```

## How It Extracts Content

The plugin extracts:

1. **Title** (in priority order):
   - First `<h1>` tag
   - `<title>` tag
   - Element with class `emd-title`
   - Filename as fallback

2. **Text content**:
   - All visible text from HTML
   - Scripts and styles removed
   - Whitespace normalized
   - Truncated to `max_text_length`

## Technical Details

- **Hook**: `on_post_build` - runs after MkDocs build completes
- **File modified**: `site/search/search_index.json`
- **Format**: Standard MkDocs search index format
- **Compatible with**: MkDocs Material search UI

## Troubleshooting

### Plugin not running?

Check:
1. Is `beautifulsoup4` installed? `pip install beautifulsoup4`
2. Is plugin in `mkdocs.yml` under `plugins:` section?
3. Does `html_search.py` exist in `src/mkdocs/plugins/`?

### HTML files not appearing in search?

Check:
1. Are HTML files in directories listed in `html_dirs`?
2. Look for plugin output: `✓ HTML Search: Indexed X HTML files`
3. Check `site/search/search_index.json` - should contain your HTML pages

### Search results missing content?

Increase `max_text_length`:

```yaml
- html_search:
    max_text_length: 2000
```

## Example Output

```
Building MkDocs...
...
✓ HTML Search: Indexed 47 HTML files
```

Your HTML files are now searchable!
