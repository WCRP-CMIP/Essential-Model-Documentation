# HTML Search Solution - Using Hooks

## What I Created

A **post-build hook** that adds HTML files to the MkDocs search index. No plugin installation needed!

## How to Use

### 1. Install BeautifulSoup4

```bash
pip install beautifulsoup4
```

### 2. Build Your Site

```bash
cd src/mkdocs
mkdocs build
```

You'll see:
```
✓ HTML Search: Indexed 47 HTML files
```

### 3. Test

```bash
mkdocs serve
```

Search for your models - they'll appear!

## How It Works

1. **Pre-build hook** runs your generator scripts → creates HTML files
2. **MkDocs builds site** → creates `search_index.json` (indexes .md files)
3. **Post-build hook** runs → finds HTML files, parses them, adds to search index
4. **Material Search** uses the enhanced index → HTML files are searchable!

## Files Created

- `src/mkdocs/hooks/post_build.py` - The hook that does everything

Already configured in `mkdocs.yml`:

```yaml
hooks:
  - hooks/pre_build.py     # Generates HTML files
  - hooks/generate_nav.py  # Creates navigation
  - hooks/post_build.py    # Indexes HTML files for search ← NEW
```

## What It Does

- Scans these directories: `model/`, `model_component/`, `model_family/`, `bidk/`
- Parses each `.html` file with BeautifulSoup
- Extracts title (from `<h1>`, `<title>`, or `.emd-title`)
- Extracts text content (first 1000 characters)
- Adds to `site/search/search_index.json`

## Benefits

✅ No plugin installation  
✅ Just a simple hook  
✅ Works with Material Search  
✅ HTML files stay as-is  
✅ Automatic on every build

## That's It!

Just install beautifulsoup4 and build. Your HTML files will be searchable!

```bash
pip install beautifulsoup4
cd src/mkdocs
mkdocs build
```

Done! 🎉
