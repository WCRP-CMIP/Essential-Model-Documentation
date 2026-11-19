# ⚠️ Do not edit the files in this folder

> [!CAUTION]
> Every file here is **generated automatically** and will be **overwritten**.
> Changes made directly in this folder are lost the next time the templates are regenerated.

## Where to make changes instead

Edit the source files in [`.github/GEN_ISSUE_TEMPLATE/`](../GEN_ISSUE_TEMPLATE/). Each template is built from three files with the same name:

| Edit this file | To change |
|---|---|
| `GEN_ISSUE_TEMPLATE/<template>.csv` | the form: its fields, their order, types, labels and whether they are required |
| `GEN_ISSUE_TEMPLATE/<template>.py` | the options offered in the dropdowns |
| `GEN_ISSUE_TEMPLATE/<template>.json` | the title, metadata and the collapsible guidance text |

For example, to change the model form, edit `model.csv`, `model.py` or `model.json`, never `ISSUE_TEMPLATE/model.yml`.

See [`GEN_ISSUE_TEMPLATE/README.md`](../GEN_ISSUE_TEMPLATE/README.md) and
[`GEN_ISSUE_TEMPLATE/GUIDELINES.md`](../GEN_ISSUE_TEMPLATE/GUIDELINES.md) for how the files fit together.

## How the files here are made

The [Update Issue Templates](../workflows/issue-templates.yml) workflow runs cmipld's `template_generate`, which writes one
`<template>.yml` for each template, plus `config.yml` (the template chooser) and `../issues.md`. It runs:

- on every push to `src-data` that changes `.github/GEN_ISSUE_TEMPLATE/`,
- once a day, on a schedule,
- and on demand, from the workflow's **Run workflow** button.

This README has no front matter, so it does not appear as an issue template in the chooser.
