# Alternative Documentation Versioning Solutions

## Option 1: Manual Directory Structure (Simplest)

### How It Works

Manually build to different directories for each version:

```bash
# Version 1.0
mkdocs build --site-dir /path/to/site/v1.0/

# Version 1.1
mkdocs build --site-dir /path/to/site/v1.1/

# Latest (symlink or copy)
mkdocs build --site-dir /path/to/site/latest/
```

### Directory Structure
```
your-site/
├── index.html (redirects to latest/)
├── latest/ → symlink to v1.1/
├── v1.0/
│   ├── index.html
│   └── ...
└── v1.1/
    ├── index.html
    └── ...
```

### Pros/Cons
✅ Simple, no dependencies  
✅ Full control  
❌ Manual process  
❌ No built-in version selector

---

## Option 2: Git Tags + Build Script

Use git tags to mark versions:

### Setup

```bash
#!/bin/bash
# build-versions.sh

VERSIONS=("1.0.0" "1.1.0" "1.2.0")
OUTPUT_DIR="/path/to/site"

for VERSION in "${VERSIONS[@]}"; do
    echo "Building version $VERSION..."
    
    # Checkout tag
    git checkout "v$VERSION"
    
    # Build to version directory
    cd src/mkdocs
    mkdocs build --site-dir "$OUTPUT_DIR/$VERSION"
    cd ../..
done

# Build latest from main branch
git checkout main
cd src/mkdocs
mkdocs build --site-dir "$OUTPUT_DIR/latest"

echo "All versions built!"
```

### Pros/Cons
✅ Uses git for version control  
✅ Automated with script  
❌ Must rebuild all versions  
❌ No version selector UI

---

## Option 3: mkdocs-versioning Plugin

Third-party plugin for versioning.

### Installation

```bash
pip install mkdocs-versioning
```

### Configuration

```yaml
# mkdocs.yml
plugins:
  - versioning:
      version: 1.0
      previous:
        - version: 0.9
          name: Version 0.9
```

### Pros/Cons
✅ Built-in version selector  
✅ Config-based  
⚠️ Less maintained than mike  
❌ Limited features

---

## Option 4: Docusaurus (Different Framework)

If you're open to changing frameworks, Docusaurus has built-in versioning:

```bash
npm install @docusaurus/core
docusaurus docs:version 1.0
```

### Pros/Cons
✅ Professional versioning system  
✅ Modern UI  
❌ Complete rewrite needed  
❌ Node.js instead of Python

---

## Option 5: Custom Version Selector

Keep your current setup, add a custom version dropdown manually.

### Implementation

**1. Create versions.json:**
```json
{
  "versions": [
    {"label": "1.1.0", "path": "/v1.1/"},
    {"label": "1.0.0", "path": "/v1.0/"}
  ],
  "latest": "1.1.0"
}
```

**2. Add to header template:**

In `overrides/partials/header.html`:

```html
<div class="version-selector">
  <select onchange="window.location.href=this.value">
    <option value="/v1.1/">v1.1.0 (latest)</option>
    <option value="/v1.0/">v1.0.0</option>
  </select>
</div>
```

**3. Build to directories:**
```bash
mkdocs build --site-dir site/v1.1/
mkdocs build --site-dir site/v1.0/
```

### Pros/Cons
✅ Custom solution  
✅ Flexible  
❌ Manual maintenance  
❌ More work

---

## Option 6: GitHub Releases + Actions

Use GitHub Actions to build on release:

### .github/workflows/docs.yml

```yaml
name: Build Docs

on:
  release:
    types: [published]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        
      - name: Install dependencies
        run: pip install -r src/mkdocs/requirements.txt
        
      - name: Build docs
        run: |
          VERSION=${{ github.event.release.tag_name }}
          cd src/mkdocs
          mkdocs build --site-dir ../../site/$VERSION
          
      - name: Deploy
        # Deploy to your server
```

### Pros/Cons
✅ Automatic on release  
✅ CI/CD integration  
❌ Requires GitHub Actions  
❌ Still need version selector

---

## Option 7: netlify.toml Redirects

If hosting on Netlify, use branch-based versioning:

```toml
# netlify.toml
[build]
  command = "cd src/mkdocs && mkdocs build"
  publish = "src/mkdocs/site"

# Version redirects
[[redirects]]
  from = "/v1.0/*"
  to = "https://v1-0--yoursite.netlify.app/:splat"
  status = 200

[[redirects]]
  from = "/latest/*"
  to = "/:splat"
  status = 200
```

### Pros/Cons
✅ Platform-specific solution  
✅ Easy with Netlify  
❌ Only works on Netlify  
❌ Requires multiple deployments

---

## Recommendation for Your Setup

Given your **docs branch → production** workflow, I recommend:

### Hybrid Approach: Tags + Build Script

**Workflow:**

1. **Tag versions in git:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Build script in production:**
   ```bash
   #!/bin/bash
   # production-build-versions.sh
   
   # Get all version tags
   VERSIONS=$(git tag -l "v*" | sort -V)
   
   for VERSION in $VERSIONS; do
       git checkout $VERSION
       cd src/mkdocs
       mkdocs build --site-dir /var/www/site/${VERSION#v}/
       cd ../..
   done
   
   # Build latest from docs branch
   git checkout docs
   cd src/mkdocs
   mkdocs build --site-dir /var/www/site/latest/
   ```

3. **Add simple version selector** to your header template

**Benefits for you:**
- ✅ Works with your current workflow
- ✅ No extra tools (just git)
- ✅ Production builds as needed
- ✅ Simple version dropdown

Would you like me to implement this approach?
