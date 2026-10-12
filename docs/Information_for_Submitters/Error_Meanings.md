# When Things Go Wrong

Something posted on your submission and you are not sure what it means. This page explains the most common automated messages, what caused them, and exactly what to do next.

---

## Validation Failed

> **Submission validation failed**
> The following errors were found. Please edit the issue to correct them.

This appears when the automated checks found a problem with your submitted data before a pull request was created. The comment lists the specific fields that failed and what was wrong with them.

**What to do:** Edit the original issue body to correct the flagged fields. You do not need to close and reopen — the action re-runs automatically every time you save an edit. Repeat until you see the "Automatic checks passed" comment instead.

The [edit guide](https://scribehow.com/embed-preview/Edit_an_Issues_Description_Field_on_GitHub__BFQ9OA50Q9-RbQvQ3r_GEQ?as=slides&size=flexible) shows how to edit an issue body if you are unfamiliar with the process.

---

## File Already Exists

> **File already exists**
> `horizontal_grid_cell/tempgrid_...json` already exists. Change **Issue Kind** to *Modify* to update it, or close this issue if no changes are needed.

This means the action tried to create a file that is already present on the `src-data` branch. This usually happens if the action runs twice on the same submission, or if you are editing an existing record that was already processed.

**What to do:** If you are correcting a submission that already has a PR open, set the **Issue Kind** field in your issue to *Modify* and save the edit. If you are unsure whether a PR already exists, check [My Issues](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues?q=is%3Aissue+author%3A%40me) — a linked PR will be visible there.

---

## Duplicate Grid Detected

> **Duplicate grid detected**
> This submission is identical to an existing entry (ignoring ID fields). No new entry will be created.
> **Existing ID:** `g109`

The content you submitted exactly matches an entry already in the registry. The issue and PR have been closed automatically and the duplicate file removed.

**What to do:** Use the existing ID shown (`g109` in the example) directly in the next stage of your submission — you do not need to register a new grid. If you believe your grid is genuinely different from the existing one, close this issue and submit again, using the **Description** field to explain precisely how your grid differs. Any structural difference that cannot be expressed through the form fields must be documented there.

---

## No Component Configuration Created

> **Component (only) created. Insufficient computational grids supplied. See below.**
> A horizontal **and** vertical computational grid are both required to generate a `component_config` record.

Your model component was registered, but no component configuration was created because you did not supply both a horizontal grid ID and a vertical grid ID. The PR contains only the `model_component` file.

**What to do:** Once your component PR is merged, use the [Stage 3: Link Existing Component](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=link_existing_component.yml) form to link your component to the grids. Select your component from the dropdown and supply the `h###` and `v###` IDs from Stage 2. The configuration is created and pushed without a separate review step.

---

## Changes Requested

> **Reviewer @username on Pull Request #N ✖ requested changes:**
> ...

A reviewer has read your submission and found something that needs correcting before they can approve it. This comment is copied from their GitHub review to your issue so you see it in the same place you track your submission.

**What to do:** Read the comment carefully — it should specify exactly which field to change and what the correct value should be. Edit the original issue body with the correction. The PR updates automatically. Once you have made the changes, the `changes-made` label is added to your issue and PR so the reviewer knows to look again.

Do not reply on the issue. If you have a question about the requested change, reply on the [pull request](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls) directly, as that is where the reviewer is working.

---

## Automatic Checks Passed — But No PR Link

> **Automatic checks passed**
> **a new PR** will be created for review.

The validation passed but the PR had not yet been found when the comment was posted (this can happen if GitHub takes a moment to index the newly opened PR).

**What to do:** Wait a minute and refresh your issue page. The comment is updated automatically — the PR link will appear. You can also check [My Issues](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues?q=is%3Aissue+author%3A%40me) where the linked PR is shown directly.

---

## The Action Never Ran

If you submitted an issue and nothing happened within five minutes — no comment, no PR — check the following:

1. **Labels** — the issue must have the `emd-submission` label and one of the type labels (e.g. `horizontal_grid_cell`). These are added automatically by the form, but if you submitted a general issue rather than a template form, they may be missing.
2. **Workflow status** — go to the [Actions tab](https://github.com/WCRP-CMIP/Essential-Model-Documentation/actions) of the repository and look for a run triggered by your issue. A red cross means the action ran but failed; click through for the error log.
3. **Form used** — make sure you used a form from the [form chooser](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new/choose) rather than opening a blank issue.

If none of these apply, open a [general issue](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=general_issue.yml) and describe what happened.
