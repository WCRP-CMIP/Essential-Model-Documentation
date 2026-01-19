# Solution: Search HTML Files in MkDocs

## The Problem
MkDocs' built-in search plugin ONLY indexes `.md` files. It cannot index `.html` files.

## Solutions

### Option 1: Use an External Search Service

Use Algolia DocSearch or similar:

1. **Algolia DocSearch** (Free for open source)
   - Crawls your deployed site
   - Indexes ALL HTML pages
   - Better search than built-in
   - Setup: https://docsearch.algolia.com/

2. **Add to mkdocs.yml**:
```yaml
extra:
  search:
    provider: algolia
    api_key: YOUR_API_KEY
    index_name: YOUR_INDEX_NAME
```

### Option 2: Generate Parallel .md Files for Search

Keep your `.html` files AND generate `.md` stubs for search:

**Modify your generator scripts to create BOTH:**

```python
# In generate_models.py
def process_model(env, template, filename, pbar=None):
    # Generate HTML file
    html_path = OUTPUT_DIR / filename.replace(".json", ".html")
    # ... generate HTML ...
    
    # ALSO generate a .md stub for search
    md_path = OUTPUT_DIR / filename.replace(".json", ".md")
    with open(md_path, 'w') as f:
        f.write(f"""---
title: {model_name}
---

# {model_name}

{description}

[View full details]({filename.replace('.json', '.html')})
""")
```

This way:
- `.html` files are your full pages
- `.md` files are searchable stubs that link to HTML
- Search finds the `.md` files
- Users click and go to the HTML pages

### Option 3: Client-Side Search Library

Use a JavaScript search library that indexes at runtime:

**Install lunr.js or similar**:

Add to your HTML templates:
```html
<script src="https://unpkg.com/lunr/lunr.js"></script>
<script>
// Build search index from your HTML pages
var idx = lunr(function () {
  this.ref('id')
  this.field('title')
  this.field('content')
  
  // Add your pages
  documents.forEach(function (doc) {
    this.add(doc)
  }, this)
})
</script>
```

### Option 4: Accept HTML Files Won't Be Searchable

Keep HTML files, but:
- Only markdown files are searchable
- HTML files are browseable via navigation
- Users can still access them, just not via search

## Recommendation

**For your use case**, I recommend **Option 2** (parallel .md files):

- Keep generating HTML files as-is
- ALSO generate simple .md stubs
- .md stubs contain basic info and link to full HTML
- Search works on .md files
- Users click through to HTML pages

Want me to implement Option 2 in your generator scripts?
