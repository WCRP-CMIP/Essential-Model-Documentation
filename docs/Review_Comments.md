# Writing Review Comments

This page covers how to write clear, consistent review comments on EMD pull requests. GitHub renders markdown in PR reviews, comments, and issue bodies — but its syntax differs from the MkDocs syntax used in this documentation site.

---

## GitHub vs MkDocs Admonitions

The EMD documentation site uses MkDocs Material admonitions (`!!! warning`). Pull request review comments use **GitHub's alert syntax** instead. These are two different systems — do not mix them.

| Context | Correct syntax |
|---|---|
| This documentation site (`.md` files in `docs/`) | `!!! warning` / `!!! note` |
| GitHub PR reviews, issue comments, PR bodies | `> [!WARNING]` / `> [!NOTE]` |

---

## GitHub Alert Syntax

GitHub supports five alert types. Each is a blockquote with a type keyword on the first line:

```markdown
> [!NOTE]
> Useful information the reader should notice.

> [!TIP]
> Helpful advice or a suggested improvement.

> [!WARNING]
> Something that needs attention or correction.

> [!IMPORTANT]
> Critical information required for a correct submission.

> [!CAUTION]
> A logical error or contradiction that must be resolved before merging.
```

These render as coloured callout boxes in the GitHub UI. Plain blockquotes (`>`) without the keyword render as standard indented quotes and carry no visual weight — use the typed form for review comments.

---

## Review Comment Structure

EMD reviews follow a four-section structure. Use only the sections that apply — omit empty ones entirely.

```markdown
**EMD Review:**

### Changes
Minor corrections where the fix is unambiguous.

> [!TIP]
> **[Component] name:** "Noo changes" → "No changes". Typo.

### Warnings
Values that are physically implausible or internally inconsistent.

> [!WARNING]
> **[Grid] n_z:** 500 levels for an ocean component — typical range is 25–75. Verify this is not a transcription error.

### Concerns
Things that look unusual but could be intentional. No action required if deliberate.

> [!NOTE]
> **[Grid] description:** Description restates the grid type already captured in `grid_type`. Consider leaving blank.

### Errors
Logical contradictions that make the submission invalid and must be resolved before merging.

> [!CAUTION]
> **[Model] dynamic_components / omitted_components:** "aerosol" appears in both lists. A realm cannot be both active and omitted — one entry must be removed.
```

If you find nothing to flag, write:

```markdown
**EMD Review:** No issues found.
```

---

## Alert Type Reference

| Type | Use for |
|---|---|
| `[!TIP]` | **Changes** — unambiguous corrections, typos, clear fixes |
| `[!WARNING]` | **Warnings** — implausible values, inconsistencies requiring submitter confirmation |
| `[!NOTE]` | **Concerns** — unusual but possibly intentional; raised for awareness |
| `[!IMPORTANT]` | **Rules** — flagging a broken convention (ID format, link permanence) |
| `[!CAUTION]` | **Errors** — logical contradictions that block merging |

---

## Formatting Individual Comments

Each comment should identify the category and field clearly so the submitter knows exactly what to address.

**Pattern:**

```markdown
> [!WARNING]
> **[Category] field_name:** what is wrong and why. Suggested correction if applicable.
```

**Category** is the record type in square brackets — `[Grid]`, `[Component]`, `[Model]`, `[Family]`.

**Examples:**

```markdown
> [!TIP]
> **[Grid] grid_type:** "regular_latitide_longitude" → "regular_latitude_longitude". Typo.

> [!WARNING]
> **[Grid] x_resolution:** Stated as 1.4° for a T127 spectral grid, consistent. But `y_resolution`
> is 2.8° — double the expected meridional spacing. Verify this is intentional.

> [!NOTE]
> **[Component] description:** "Used in CNRM-ESM2-1e for CMIP7." This describes where the component
> is used, not what it does. Consider leaving blank or replacing with a technical description.

> [!CAUTION]
> **[Model] prescribed_components / dynamic_components:** "ocean" appears in both. A realm must be
> either active or prescribed, not both — remove it from one list.
```

---

## Requesting Edits from Submitters

When changes are needed, leave the request on the **original issue**, not the PR. The submitter edits the issue body and the action re-runs automatically, updating the PR.

Make it easy to action — include exactly what to change, in which field, and what the corrected value should be:

```markdown
Please update the **original issue** (not this PR) with the following correction:

- Field: `x_resolution`
- Current value: `"1.4 km"`
- Corrected value: `"1.40"` (units are set separately in the `units` field)

After editing the issue body, the pull request will update automatically within a few minutes.
```

Link to the [edit guide](https://scribehow.com/embed-preview/Edit_an_Issues_Description_Field_on_GitHub__BFQ9OA50Q9-RbQvQ3r_GEQ?as=slides&size=flexible) if the submitter may be unfamiliar with the process.

---

## Other Useful Markdown

**Inline code** — use backticks to reference field names, values, and IDs:

```markdown
The `n_cells` value of `55296` is consistent with a global 1.25° × 0.9° grid.
```

**Quoting the submission** — quote the relevant line from the diff to anchor your comment:

```markdown
> "description": "This is the grid used in our model."

This description references the model rather than the grid itself.
Leave blank or replace with a description of the grid's physical structure.
```

**Linking to a specific line in the diff** — in the PR Files tab, click a line number to highlight it, then copy the URL. Paste this into your comment to pin it to the exact field being discussed. This is especially useful when requesting changes to a specific value in a long JSON file.
