# Templates

Jinja2 templates generate the HTML pages from JSON-LD data.

## Template Files

| Template | Purpose |
|----------|---------|
| `model.html.j2` | Climate model pages |
| `model_component.html.j2` | Model component pages |
| `model_family.html.j2` | Model family pages |

All templates are in `docs/scripts/helpers/templates/`.

## Base Structure

Every template follows this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ name | e }} | Page Type</title>
    <link rel="stylesheet" href="../stylesheets/page-type.css">
</head>
<body class="emd-page">
    <div class="emd-container">
        <header class="emd-header">
            <!-- Breadcrumb, badge, title, subtitle, meta -->
        </header>

        <main>
            <!-- Collapsible sections -->
        </main>

        <footer class="emd-footer">
            <!-- Attribution and generation date -->
        </footer>
    </div>
    <script>
        // Section toggle + copy protection
    </script>
</body>
</html>
```

## Common Components

### Header

```html
<header class="emd-header">
    <nav class="emd-breadcrumb">
        <a href="../">← Back to Documentation</a>
        <span>|</span>
        <a href="https://emd.mipcvs.dev/" target="_blank">EMD Registry</a>
        <span>→</span>
        <span>{{ name | e }}</span>
    </nav>
    
    <div class="emd-badge">Page Type</div>
    <h1 class="emd-title">{{ name | e }}</h1>
    <p class="emd-subtitle">{{ description | e }}</p>
    
    <div class="emd-header-meta">
        <div class="emd-meta-item">
            <span class="emd-meta-label">Label</span>
            <span class="emd-meta-value">{{ value | e }}</span>
        </div>
    </div>
</header>
```

### Collapsible Section

```html
<section class="emd-section expanded">
    <div class="emd-section-header" onclick="toggleSection(this)">
        <div class="emd-section-title-wrapper">
            <div class="emd-section-icon">{{ icons.name | safe }}</div>
            <h2 class="emd-section-title">
                Section Title 
                <span class="emd-section-count">({{ items | length }})</span>
            </h2>
        </div>
        <div class="emd-section-toggle">{{ icons.chevron | safe }}</div>
    </div>
    <div class="emd-section-content">
        <div class="emd-section-body">
            <div class="emd-section-divider"></div>
            <!-- Section content -->
        </div>
    </div>
</section>
```

### Domain Card

```html
<div class="emd-domain-card">
    <div class="emd-domain-card-header">
        <span class="emd-domain-card-title">{{ item.name | e }}</span>
        <span class="emd-domain-card-type">Type</span>
    </div>
    <div class="emd-domain-card-id">@id: {{ item.id | e }}</div>
    <p class="emd-domain-card-description">{{ item.description | e }}</p>
    {% if item.aliases %}
    <div class="emd-domain-card-meta">
        {% for alias in item.aliases %}
        <span class="emd-meta-tag">{{ alias | e }}</span>
        {% endfor %}
    </div>
    {% endif %}
</div>
```

### Grid Card (with stats)

```html
<div class="emd-grid-card">
    <div class="emd-grid-card-header">
        <div class="emd-grid-card-icon">{{ icons.grid | safe }}</div>
        <div class="emd-grid-card-title">
            <span class="emd-grid-card-label">Grid Type</span>
            <span class="emd-grid-card-id">{{ grid.id | e }}</span>
        </div>
    </div>
    <p class="emd-grid-card-desc">{{ grid.description | e }}</p>
    <div class="emd-grid-card-stats">
        <div class="emd-grid-card-stat">
            <span class="emd-grid-card-stat-label">Metric</span>
            <span class="emd-grid-card-stat-value accent">{{ value }}</span>
        </div>
    </div>
</div>
```

### Footer

```html
<footer class="emd-footer">
    <p class="emd-footer-text">
        Data sourced from 
        <a href="https://emd.mipcvs.dev/" class="emd-footer-link">EMD Registry</a> · 
        Part of the <a href="https://wcrp-cmip.org/" class="emd-footer-link">WCRP CMIP</a> initiative · 
        Generated {{ generated_date }}
    </p>
</footer>
```

## JavaScript

### Section Toggle

```javascript
function toggleSection(header) { 
    header.parentElement.classList.toggle('expanded'); 
}
```

### Copy Protection

Embeds JSON-LD source when copying:

```javascript
const sourceData = {{ raw_json | safe }};
document.addEventListener("copy", function(e) {
    e.preventDefault();
    const jsonString = JSON.stringify(sourceData, null, 2);
    const copyText = "// JSON-LD Source Data for {{ name | e }}\n" +
                     "// From: {{ context_url | e }}\n" +
                     "// Generated: {{ generated_date }}\n\n" + 
                     jsonString;
    e.clipboardData.setData("text/plain", copyText);
});
```

## Jinja2 Syntax

### Escaping

```html
{{ variable | e }}        <!-- HTML escape -->
{{ variable | safe }}     <!-- No escape (for icons, highlighted text) -->
```

### Conditionals

```html
{% if condition %}
    <!-- content -->
{% elif other_condition %}
    <!-- other content -->
{% else %}
    <!-- fallback -->
{% endif %}
```

### Loops

```html
{% for item in items %}
<div>{{ item.name | e }}</div>
{% endfor %}
```

### Variables

```html
{% set count = items | length %}
{% set has_data = value and value != 'none' %}
```

### Filters

```html
{{ text | replace('-', ' ') | title }}    <!-- Transform text -->
{{ number | format(',') }}                 <!-- Format numbers -->
{{ url | replace('https://', '') }}        <!-- Clean URLs -->
```

## Icons

Available icons from `icons` dict:

```html
{{ icons.description | safe }}  <!-- Document -->
{{ icons.domain | safe }}       <!-- Globe -->
{{ icons.grid | safe }}         <!-- Grid -->
{{ icons.coupling | safe }}     <!-- Link -->
{{ icons.tech | safe }}         <!-- Code -->
{{ icons.reference | safe }}    <!-- Book -->
{{ icons.chevron | safe }}      <!-- Arrow -->
```

## Creating New Templates

1. Copy an existing template as base
2. Update the CSS link and body class
3. Modify sections for your data structure
4. Update the generator to provide required context
5. Test with `mkdocs serve`
