# Styling System

The CSS architecture uses a shared base with page-specific extensions.

## File Structure

```
docs/stylesheets/
├── shared-page.css      # Common styles (imported by others)
├── model-page.css       # Model-specific additions
├── component-page.css   # Component-specific additions
└── extra.css            # MkDocs theme overrides
```

## Import Pattern

Each page-specific CSS imports the shared base:

```css
/* component-page.css */
@import url('shared-page.css');

/* Component-only styles below */
.emd-subgrids-section { ... }
```

## CSS Variables

All colors and values use CSS custom properties in `:root`:

```css
:root {
    /* Colors */
    --page-bg: #ffffff;
    --page-bg-secondary: #f8fafc;
    --page-bg-tertiary: #f1f5f9;
    --page-text: #1e293b;
    --page-text-secondary: #64748b;
    --page-text-tertiary: #94a3b8;
    --page-border: #e2e8f0;
    --page-border-light: #f1f5f9;
    --page-primary: #3b82f6;
    --page-primary-light: #dbeafe;
    --page-accent: #0ea5e9;
    --page-accent-light: #e0f2fe;
    --page-purple: #8b5cf6;
    --page-purple-light: #ede9fe;
    
    /* Typography */
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
    
    /* Shadows & Radii */
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
    --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1);
    --radius-sm: 6px;
    --radius-md: 8px;
    --radius-lg: 12px;
}
```

### Dark Mode

Variables automatically adjust for dark mode:

```css
@media (prefers-color-scheme: dark) {
    :root {
        --page-bg: #0f172a;
        --page-bg-secondary: #1e293b;
        --page-text: #f1f5f9;
        /* ... */
    }
}
```

## Class Naming

All classes use the `emd-` prefix to avoid conflicts:

| Prefix | Purpose |
|--------|---------|
| `emd-container` | Page wrapper |
| `emd-header` | Header section |
| `emd-section` | Collapsible section |
| `emd-domain-card` | Info card |
| `emd-grid-card` | Stats card |
| `emd-tech-*` | Technical details |
| `emd-reference-*` | Reference links |
| `emd-footer` | Page footer |

## Shared Components

### Container

```css
.emd-container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
}
```

### Collapsible Sections

```css
.emd-section {
    background: var(--page-bg);
    border: 1px solid var(--page-border);
    border-radius: var(--radius-lg);
    margin-bottom: 1rem;
    overflow: hidden;
}

.emd-section-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.4s ease;
}

.emd-section.expanded .emd-section-content {
    max-height: 5000px;
}
```

### Domain Cards

```css
.emd-domain-card {
    background: var(--page-bg-secondary);
    border: 1px solid var(--page-border);
    border-radius: var(--radius-md);
    padding: 1.25rem;
    border-left: 3px solid var(--page-accent);
    transition: all 0.2s;
}

.emd-domain-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}
```

### Grid Layout

```css
.emd-domain-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
}

.emd-grids-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}
```

### Stats Boxes

```css
.emd-grid-card-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.emd-grid-card-stat {
    min-width: 100px;
    flex: 1 1 calc(50% - 0.25rem);
    padding: 0.6rem 0.75rem;
    background: var(--page-bg);
    border: 1px solid var(--page-border-light);
    border-radius: var(--radius-sm);
}

.emd-grid-card-stat-value.accent {
    color: var(--page-accent);
    font-weight: 600;
}
```

## Page-Specific Styles

### Component Page: Subgrids

```css
/* component-page.css */
.emd-subgrids-section {
    margin-top: 1.25rem;
    padding-top: 1rem;
    border-top: 1px dashed var(--page-border);
}

.emd-subgrid-card {
    background: var(--page-bg);
    border: 1px solid var(--page-border);
    border-radius: var(--radius-sm);
    padding: 0.75rem;
    border-left: 3px solid var(--page-purple);
}
```

### Model Page: Institution

```css
/* model-page.css */
.emd-long-name {
    font-size: 1.1rem;
    color: var(--page-text-secondary);
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.emd-institution-card {
    border-left: 3px solid var(--page-primary);
}
```

## Responsive Design

### Tablet (< 900px)

```css
@media (max-width: 900px) {
    .emd-grids-row {
        grid-template-columns: 1fr;
    }
}
```

### Mobile (< 768px)

```css
@media (max-width: 768px) {
    .emd-container { 
        padding: 1.5rem 1rem 3rem; 
    }
    .emd-title { 
        font-size: 2rem; 
    }
    .emd-domain-grid { 
        grid-template-columns: 1fr; 
    }
    .emd-grid-card-stats { 
        flex-direction: column; 
    }
    .emd-grid-card-stat { 
        flex: 1 1 100%; 
    }
}
```

## Typography

### Fonts

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

body.emd-page {
    font-family: var(--font-sans);
    font-size: 15px;
    line-height: 1.6;
}

.emd-meta-value,
.emd-tech-value,
.emd-domain-card-id {
    font-family: var(--font-mono);
}
```

### Text Sizes

| Element | Size |
|---------|------|
| Title | 2.5rem |
| Section title | 1rem |
| Body text | 0.95rem |
| Labels | 0.65rem |
| Monospace | 0.85rem |

## Customizing

### Adding New Colors

```css
:root {
    --page-success: #10b981;
    --page-success-light: #d1fae5;
}

@media (prefers-color-scheme: dark) {
    :root {
        --page-success-light: #065f46;
    }
}
```

### Creating New Components

Follow the naming convention:

```css
.emd-newcomponent {
    /* Base styles */
}

.emd-newcomponent-header {
    /* Header styles */
}

.emd-newcomponent-content {
    /* Content styles */
}
```

Use existing variables for consistency:

```css
.emd-newcomponent {
    background: var(--page-bg-secondary);
    border: 1px solid var(--page-border);
    border-radius: var(--radius-md);
    padding: 1.25rem;
}
```
