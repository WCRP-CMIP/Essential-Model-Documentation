# Issue Templates — Structure and Maintenance

This page explains how the GitHub issue templates (the backbone of the EMD submission process) are structured, generated, edited / corrected. 
It is aimed at developers and maintainers.

---

## Overview

The submission forms at [github.com/…/issues/new/choose](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new/choose) are standard GitHub issue templates stored as YAML files under `.github/ISSUE_TEMPLATE/`. Rather than being edited by hand, they are **generated automatically** by the `template_generate` command from the `cmipld` library. The generator runs on the `main` branch and commits the resulting files back to `.github/ISSUE_TEMPLATE/` and the modification links in `CONTRIBUTING.md`. The generator is triggered by the `issue-templates.yml` workflow — see [Workflows and Automations](Workflows_and_Automations/).

[!warning] The general rule is: **do not edit the generated template files directly** — as they will be overwritten on the next run. 

---

## Branch Layout

| Branch | What it contains |
|---|---|
| `main` | Workflow files, generated `.github/ISSUE_TEMPLATE/*.yml`, `CONTRIBUTING.md` |
| `src-data` | Raw JSON records submitted through the forms |
| `production` | Processed JSON, graph files, built documentation |

The generator reads live controlled vocabulary data from the `production` branch (via the LDR server) to populate dropdowns. This is why newly merged entries appear in forms after the publication action in a merge chain. 

---

## Template File Anatomy (For info)

Each generated template is a standard GitHub issue form YAML file. The overall structure is:

```yaml
name: <human-readable name shown in the template chooser>
description: <subtitle shown under the name>
title: "New <RecordType>: "
labels: ["needs-review", "<record-type-label>"]
body:
  - type: input | dropdown | textarea | checkboxes | markdown
    id: <field_id>
    attributes:
      label: <display label>
      description: <hint text shown under the field>
      placeholder: <greyed-out example text>
      options: [...]        # dropdown only
      value: <default>      # textarea/input default content
    validations:
      required: true | false
```

GitHub renders `body` as a structured form. Each element maps to a field in the issue body, which `new-issue.yml` then parses by `id` to build the JSON record.If these files contain an error (often if no options are provided to a dropdown) the templates will not render, and the issue will not appear in GitHub.

---

## How the Generator Works

`template_generate` (from `cmipld`) does the following for each record type:

1. Reads a schema definition that maps field names to their GitHub form field type and display properties.
2. Queries the live JSONLD-recursive server (serving `production` data) to get the current list of registered entries for any field that references another record type — these become `dropdown` or `checkboxes` options.
3. Renders each field into YAML using the schema + live data.
4. Writes the resulting file to `.github/ISSUE_TEMPLATE/<record_type>.yml`.

`template_update` then re-generates the modification links in `CONTRIBUTING.md` — the pre-filled URLs in the "Modifying or reusing existing entries" section — by serialising each existing registry record back into URL query parameters.

---

## How to Change a Template

### The options in a dropdown are wrong or out of date

This means the live registry data is stale relative to what you expect. Check whether the record that should appear has been merged to `src-data` and published to `production`. If it has, manually trigger the **Update Issue Templates** workflow (`issue-templates.yml`) from the [Actions tab](https://github.com/WCRP-CMIP/Essential-Model-Documentation/actions/workflows/issue-templates.yml) — the dropdown will be updated when the workflow commits.



### A field label or hint text is wrong

All fields are described within the `.github/GEN_ISSUE_TEMPLATE` folder `.csv` file with the relevant issue name. Any dynamic information is computed by the `.py` file, and dropdown descriptions come from the `.json` files. 

### A required field is missing from a template

Again this is a schema change upstream in the `.csv` file. If a field needs to be added as `required: true`.



---

## Post Submission Processing

After submission, the `New Issue` workflow processes the contents using the logic in the `.github/ISSUE_SCIPTS` folder. Here we compare the pre-configured labels assigned to the issue, and find the python script containing the same term and then run it on the parsed input. This workflow is the one which creates any new files and submits a pull request for review. 

---

## Useful Links

- [Template chooser (live)](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new/choose)
- [Generated templates on `main`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/tree/main/.github/ISSUE_TEMPLATE)
- [Issue Templates workflow](https://github.com/WCRP-CMIP/Essential-Model-Documentation/actions/workflows/issue-templates.yml)
- [CMIPLD library](https://github.com/WCRP-CMIP/CMIPLD) — upstream source of template schemas and the `template_generate` command
