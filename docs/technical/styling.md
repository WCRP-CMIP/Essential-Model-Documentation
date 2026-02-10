# Styling System

The CSS architecture uses CSS custom properties and a consistent naming convention.

## File Structure

```
docs/stylesheets/
├── custom.css           # Main theme customizations
├── custom.js            # JavaScript functionality
└── embed.js             # Embed mode support
```

## CSS Variables

All colors and values use CSS custom properties in `:root`:

```css
:root {
    /* Colors */
    --essentialmodeldocumentation-primary: #3b82f6;
    --essentialmodeldocumentation-primary-rgb: 59, 130, 246;
    --essentialmodeldocumentation-primary-light: #dbeafe;
    --essentialmodeldocumentation-primary-dark: #2563eb;
    --essentialmodeldocumentation-accent: #0ea5e9;
    --essentialmodeldocumentation-text: #1e293b;
    --essentialmodeldocumentation-text-secondary: #475569;
    --essentialmodeldocumentation-text-tertiary: #94a3b8;
    --essentialmodeldocumentation-bg: #ffffff;
    --essentialmodeldocumentation-bg-secondary: #f8fafc;
    --essentialmodeldocumentation-bg-tertiary: #f1f5f9;
    --essentialmodeldocumentation-border: #e2e8f0;
    --essentialmodeldocumentation-border-light: #f1f5f9;
}
```

### Dark Mode

Variables automatically adjust for dark mode:

```css
.dark {
    --essentialmodeldocumentation-primary: #60a5fa;
    --essentialmodeldocumentation-primary-rgb: 96, 165, 250;
    --essentialmodeldocumentation-primary-light: rgba(59, 130, 246, 0.15);
    --essentialmodeldocumentation-primary-dark: #93c5fd;
    --essentialmodeldocumentation-text: #f1f5f9;
    --essentialmodeldocumentation-text-secondary: #cbd5e1;
    --essentialmodeldocumentation-text-tertiary: #64748b;
    --essentialmodeldocumentation-bg: #0f172a;
    --essentialmodeldocumentation-bg-secondary: #1e293b;
    --essentialmodeldocumentation-bg-tertiary: #334155;
    --essentialmodeldocumentation-border: #334155;
    --essentialmodeldocumentation-border-light: #1e293b;
}
```

## Class Naming

All custom classes use the `essentialmodeldocumentation-` prefix to avoid conflicts with the theme:

| Prefix | Purpose |
|--------|---------|
| `essentialmodeldocumentation-primary` | Primary color variable |
| `essentialmodeldocumentation-text-*` | Text color variants |
| `essentialmodeldocumentation-bg-*` | Background variants |
| `essentialmodeldocumentation-border-*` | Border variants |

## Typography

### Fonts

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Noto+Sans:wght@400;500;600;700&display=swap');
```

### Text Sizes

| Element | Size |
|---------|------|
| h1 | 2rem |
| h2 | 1.4rem |
| h3 | 1.1rem |
| Body text | 0.95rem |
| Code | 0.8rem |

## Responsive Design

### Tablet (< 900px)

```css
@media (max-width: 900px) {
    .typography {
        max-width: 100%;
        padding: 0 1rem;
    }
}
```

### Mobile (< 768px)

```css
@media (max-width: 768px) {
    article h1 {
        font-size: 1.5rem;
    }
    article h2 {
        font-size: 1.2rem;
    }
}
```

## Customizing

### Adding New Colors

```css
:root {
    --essentialmodeldocumentation-success: #10b981;
    --essentialmodeldocumentation-success-light: #d1fae5;
}

.dark {
    --essentialmodeldocumentation-success-light: #065f46;
}
```

### Overriding Theme Defaults

Use `!important` sparingly to override shadcn defaults:

```css
article a {
    color: var(--essentialmodeldocumentation-primary) !important;
}
```

Use existing variables for consistency throughout your customizations.

## Collapsible Content (Details/Summary)

For collapsible sections, use one of these methods to ensure markdown content is properly rendered:

### Method 1: PyMDownX Details Syntax (Recommended)

Use the `??? note` syntax for admonition-style collapsibles:

```markdown
??? note "Click to expand"
    This content is **markdown** and will be properly rendered.
    
    - Lists work
    - `code` works
    - [Links](https://example.com) work

???+ info "Expanded by default"
    Use `???+` to have the section open by default.
```

### Method 2: HTML with markdown attribute

Add `markdown="1"` to enable markdown processing inside HTML tags:

```html
<details markdown="1">
<summary>Click to expand</summary>

This content is **markdown** and will be properly rendered.

- Lists work
- `code` works
- [Links](https://example.com) work

</details>
```

### Styling

Details/summary elements are styled with:
- Summary text: `--essentialmodeldocumentation-primary-dark` color
- Chevron indicator that rotates on expand
- Light background with subtle border
- Proper spacing for nested content
