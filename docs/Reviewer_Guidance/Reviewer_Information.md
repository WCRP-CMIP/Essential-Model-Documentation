# Reviewer Information

!!! warning "Reviewers only"
    The following information is for the EMD review team. Some features described may not be accessible to those outside the team. If you are interested in helping with the review process, [sign up here](https://airtable.com/apphXCUgASIeT6jCz/pag2oVCHWXFCkJQ3A/form).

---

## Quick Links

### For Submitters

| Link | Description |
|------|-------------|
| [New submission](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new/choose) | Open the form chooser to start a new grid, component, family, or model submission |
| [Track my submissions](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues?q=is%3Aissue%20author%3A%40me) | All issues you have opened, including their current review status |
| [How to edit an issue and rerun actions](https://scribehow.com/embed-preview/Edit_an_Issues_Description_Field_on_GitHub__BFQ9OA50Q9-RbQvQ3r_GEQ?as=slides&size=flexible) | Step-by-step guide for making corrections after submission |

### For Reviewers

| Link | Description |
|------|-------------|
| [All open PRs — oldest first](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls?q=is%3Apr+is%3Aopen+sort%3Acreated-asc) | The full PR queue sorted by age — **review in this order** |
| [How to submit a review on GitHub](https://scribehow.com/embed-preview/Reviewing_a_Pull_Reqiest__lI5FFHj-Rz2dcvD9-JEe5g?as=slides&size=flexible) | Step-by-step walkthrough of the review and merge process |
| [PRs needing a first review](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls?q=is%3Apr+is%3Aopen+review%3Anone) | Open PRs that have not yet received any reviewer engagement |
| [Approved PRs awaiting merge](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls?q=is%3Apr+is%3Aopen+review%3Aapproved) | PRs that have passed review and are ready for a sanity check and merge |
| [PRs with changes requested](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls?q=is%3Aopen+is%3Apr+label%3Achanges-requested) | Submissions awaiting corrections from the submitter |
| [PRs approved after changes](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls?q=is%3Aopen+is%3Apr+label%3Achanges-requested+label%3Aapproved) | Submitter made changes and a reviewer has since approved — ready to merge |
| [PRs with reviewer comments](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls?q=is%3Aopen+is%3Apr+label%3Areviewer-comment) | Reviewer has left feedback without blocking or approving — may need a decision |
| [PRs where changes have been made](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls?q=is%3Apr+is%3Aopen+label%3Achanges-made) | Submitter has responded — needs re-review |
| [PRs assigned to me](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls?q=is%3Apr+is%3Aopen+user-review-requested%3A%40me) | PRs where you have been explicitly requested as a reviewer |
| [Reviewer project board](https://github.com/orgs/WCRP-CMIP/projects/8?pane=info) | Kanban view of all active submissions, organised by stage and review status |
| [EMD specification](https://zenodo.org/records/17853724) | The authoritative reference for all field definitions and controlled vocabularies |

### Labels

| Label | Set by | Meaning |
|-------|--------|---------|
| `needs-review` | Automatic on submission | PR is in the review queue. Removed automatically on approval. **Do not add or remove manually.** |
| `approved` | Automatic on reviewer approval | PR has passed review |
| `changes-requested` | Automatic when reviewer requests changes | Submitter must edit their issue |
| `changes-made` | Automatic when submitter edits issue (if `changes-requested` present) | Submitter has responded — re-review needed |
| `reviewer-comment` | Automatic when reviewer leaves a comment review | Reviewer has left feedback without blocking or approving |
| `needs checking` | Manual | Escalating to another reviewer; conditional approval requiring a second opinion |
| `priority` / `urgent` | Manual | To be defined on a case-by-case basis |

---

## Review Procedure

Reviewing oldest first is a requirement — it ensures submitters are not left waiting indefinitely.

1. Open the [oldest-first PR queue](https://github.com/WCRP-CMIP/Essential-Model-Documentation/pulls?q=is%3Apr+is%3Aopen+sort%3Acreated-asc).
2. Read the automated summary report posted as a comment, then examine the JSON diff.
3. Submit your review using GitHub's **Review changes** panel — see [Review Options](Review_Options/) for guidance on when to approve, request changes, or comment.
4. Your review body is automatically copied to the linked issue so the submitter is notified.
5. On approval, a second reviewer or maintainer performs a sanity check and merges.

!!! note
    All review comments must go through the GitHub **Review** panel on the pull request. Comments left directly on the Conversation tab or on the issue are not formal reviews and do not trigger the label and notification workflow.

---

## General Rules

**IDs and naming**

- IDs must not contain underscores or spaces.
- Any periods `.` must be replaced with hyphens `-`. This applies to source IDs, model family names, and component version strings.
- Confirm this for every identifier in the submitted record.

**Links and references**

- All links must point to permanent locations: version control platforms (GitHub, GitLab, Bitbucket) or DOIs.
- If a submitter needs a DOI for an otherwise unpublished resource, [Zenodo](https://zenodo.org/) can mint one for free.

**Grid descriptions**

- A description field on a grid record should only exist to document a difference between two otherwise identical parameter sets that cannot be captured by any structured field.
- Do not accept descriptions that simply restate the grid type or parameters already present in other fields.

---

## Reading an EMD Report

Every pull request includes an automated summary report as a comment. Read it before examining the raw diff.

**Check the overall structure.** Ensure all required sections are present and populated. Compare against the latest [EMD specification](https://zenodo.org/records/17853724).

**Review validation outputs.** Errors indicate mandatory issues that must be fixed before merging. Warnings highlight potential inconsistencies — use your judgement on whether they need addressing.

**Inspect identifiers and references.** Confirm IDs follow the naming rules above. Ensure any referenced entities (grids, component configs, families) already exist in the registry and are correctly linked.

**Assess the semantic content.** Check that descriptions are meaningful and not duplicated unnecessarily.

**Follow all links.** Verify that references resolve and point to stable, permanent resources. A link to a personal Dropbox or an unversioned URL should be flagged.

---

## Grid Similarity

Duplicate or near-duplicate grid submissions are common. Before approving any grid record:

- Check whether a similar or identical grid already exists. The automated duplicate-detection comment is a starting point, but apply your own judgement.
- Minor differences in naming or description do not justify a new record. A new entry is warranted only when there are structural differences (resolution, topology, cell count, indexing) or when the physical interpretation differs in a way no existing field can capture.
- If unsure, tag the PR with `needs checking` and request input from a domain expert.

---

## Requesting Changes

When requesting changes, provide clear and pasteable guidance so the submitter knows exactly what to do. Always include what needs to change, in which field, and what the correct value should be. See [Review Comments](Review_Comments/) for templates and examples.

Leave change requests via the **Request changes** review option — not as free-form issue comments. When the submitter edits their issue in response, a `changes-made` label is added automatically so you know to look again.

---

## Project Board

The [project board](https://github.com/orgs/WCRP-CMIP/projects/8?pane=info) provides a consolidated view of all active submissions organised by stage and review status. Columns are managed via issue labels. On approval, the automated action removes `needs-review` and the PR moves to the Done column.

---

## Command Line Helper

A helper script is available on the `main` branch for reviewers who prefer the terminal:

```bash
git checkout main && .github/pr_issue_map.sh
```

Filter flags: `--approved`, `--needs-review`, `--json`.

---

## Using Copilot

Copilot may be added as a reviewer **only after you have completed your own manual review**. It must not be used as a primary reviewer.

Appropriate uses: sanity checking your conclusions, flagging weaknesses you may have missed, suggesting grammar improvements in description fields.

When working with Copilot suggestions: never use "Fix all", manually review each suggestion, resolve irrelevant conversations, and do not ask Copilot to review subgrid records (these are auto-generated).
