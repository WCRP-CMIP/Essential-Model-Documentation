# Issue Template Guidelines

## Template Structure Overview

Each template consists of three files:
- **`.csv`** — Field definitions and structure
- **`.py`** — Dropdown data sources
- **`.json`** — Metadata and detailed guidance

---

## Title

Format: `[EMD] {Form Name}:`

Example: `[EMD] Model Component:`

---

## Header Section

The first markdown block should include:

1. **Brief description** — What this form is and what it creates
2. **Prerequisites** — What IDs/forms must be completed first
3. **Workflow diagram [if relevant]** — Mermaid flowchart with current stage highlighted 
4. **Result** — What ID format the user will receive

> **Info box:** Remind users to read the guidance (collapsible arrows ▶) before filling in the form, as incorrect entries will be rejected. For modifications to existing entries, link to the relevant `.ov` file.

---

## Field Definitions

### Field ID
- Use lowercase with underscores
- Match JSON output field names where possible
- Example: `horizontal_computational_grid`

### Label
- User-friendly, title case
- Brief but descriptive
- Example: `Horizontal Grid ID`

### Description
- Single sentence/line explaining what to enter
- No examples (these go in placeholder)
- No detailed guidance (this goes in collapsible)
- Example: `Grid ID from Stage 2a. Leave blank if none.`

### Placeholder
- Concrete examples of valid input
- Show expected format/structure
- For textareas: one example per line in a list of what to include in an enumerated format. Users will likely follow this as a template. This is the "what to include section"
- Example: `c101` or `https://doi.org/10.1234/example`

### Collapsible Guidance (in `.json`)
- Full description with context about where it is useful
- Bullet points for options/choices
- References or links if relevant
- "What to include" for textareas
- When to leave blank

---

## Field Types

| Type | Use Case |
|------|----------|
| `input` | Single-line text (IDs, names, URLs, years) |
| `textarea` | Multi-line text (descriptions, DOI lists) |
| `dropdown` | Single selection from list |
| `multi-select` | Multiple selections from list |
| `markdown` | Headers, dividers, instructions |

---

## Field Order Convention

1. Workflow diagram + header description
2. Core required fields (name, type, description)
3. Related optional fields grouped logically
4. Divider (`---`)
5. Issue handling metadata

---

## Issue Handling Section

### Metadata Header
```
---
```

### Pre-submission Information
Above the `Issue Kind` field, but under the Issue handling header, include:
- What happens after submission (e.g., "Creates two entities: component + config")
- What ID(s) the user will receive
- Next steps (e.g., "Use this ID in Stage 4")
- Link to where updates will appear

### Issue Kind
Final field, always required:
- `New` — Create new entry
- `Modify` — Update existing entry

---

## Data Sources (`.py` file)

- Keep minimal — only dropdown options, no complex processing code if avoidable
- No processing functions
- Use descriptive key names matching `data_source` in CSV
- Example:
```python
DATA = {
    'component': ['atmosphere', 'ocean', ...],
    'issue_kind': ['New', 'Modify']
}
```

---

## Guidance (`.json` file)

```json
{
  "name": "Form Display Name",
  "description": "One-line description for template picker",
  "title": "[EMD] Form Name:",
  "labels": ["emd-submission", "category", "Review"],
  "field_guidance": {
    "field_id": "**Bold heading**\n\nDetailed explanation...\n\n- Bullet points\n- For options"
  }
}
```

---

## Checklist

- [ ] Title follows `[EMD] Name:` format
- [ ] Header has: description, prerequisites, diagram (if relevant), result
- [ ] Info box about reading guidance + link to existing files
- [ ] Field IDs match output JSON fields
- [ ] Labels are user-friendly title case
- [ ] Descriptions are single-line, no examples
- [ ] Placeholders show concrete examples (enumerated for textareas)
- [ ] Collapsible guidance is comprehensive with context
- [ ] Fields grouped logically
- [ ] Issue Handling section with next steps above Issue Kind
- [ ] All `data_source` values exist in `.py`
- [ ] `.json` has guidance for all non-trivial fields
