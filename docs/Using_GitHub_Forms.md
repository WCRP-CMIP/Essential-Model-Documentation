# Using GitHub Forms

EMD submissions are made through structured GitHub issue forms. This page explains how to open a form, fill in each field type, and submit.

You will need a free GitHub account — [create one here](https://github.com/signup) if you do not already have one.

---

## Opening a form

Go to the [submission form chooser](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new/choose) and click the form for the stage you are completing.

![The GitHub issue template chooser showing all available EMD submission forms](assets/github/form.png)

Each form opens as a structured GitHub issue. The title is pre-filled — do not edit it.

---

## Field types

!!! note
    The examples below are representative illustrations. The exact appearance may vary slightly depending on your browser, operating system, and GitHub's current interface.



### Text fields

A single-line box for short answers such as a name, version, or year. Click it and type.

<div style="background:#ffffff;border:1px solid #d0d7de;border-radius:6px;padding:16px 20px;margin:12px 0 20px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;">
  <p style="font-size:14px;font-weight:600;color:#1f2328;margin:0 0 6px;">Model Name <span style="color:#cf222e;">*</span></p>
  <input type="text" placeholder="e.g. CNRM-ESM2-1" readonly style="width:100%;box-sizing:border-box;padding:5px 12px;font-size:14px;border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;color:#6e7781;height:32px;"/>
</div>

1. Click inside the box
2. Type your answer
3. Move to the next field — answers are held automatically, there is no save button

---

### Text areas

A larger box for longer answers such as a model description or list of reference DOIs. The box expands as you type.

<div style="background:#ffffff;border:1px solid #d0d7de;border-radius:6px;padding:16px 20px;margin:12px 0 20px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;">
  <p style="font-size:14px;font-weight:600;color:#1f2328;margin:0 0 6px;">Description <span style="color:#cf222e;">*</span></p>
  <textarea readonly placeholder="1. Dynamic components (briefly)&#10;2. Prescribed components and their treatment&#10;3. Omitted components" style="width:100%;box-sizing:border-box;padding:8px 12px;font-size:14px;border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;color:#6e7781;min-height:80px;resize:vertical;font-family:inherit;"></textarea>
</div>

1. Click inside the box
2. Type your answer — press **Enter** for a new line
3. The box grows as you type

---

### Dropdowns

A box with a small arrow on the right. Click it to open a list and select one option.

<div style="background:#ffffff;border:1px solid #d0d7de;border-radius:6px;padding:16px 20px;margin:12px 0 20px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;">
  <p style="font-size:14px;font-weight:600;color:#1f2328;margin:0 0 6px;">Model Family</p>
  <div style="position:relative;display:inline-block;width:100%;">
    <select style="width:100%;padding:5px 32px 5px 12px;font-size:14px;border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;color:#1f2328;height:32px;appearance:none;font-family:inherit;">
      <option>Not specified</option>
      <option>ACCESS</option>
      <option>CESM</option>
      <option>CNRM-CM</option>
      <option>HadGEM3</option>
    </select>
    <span style="position:absolute;right:10px;top:50%;transform:translateY(-50%);pointer-events:none;color:#57606a;font-size:12px;">▾</span>
  </div>
</div>

1. Click the box — a list drops down
2. Click the option you want
3. The box updates to show your selection

---

### Multi-select dropdowns

Some dropdowns allow more than one selection — labelled **Select multiple** in the form. When you open one, a panel with a checkbox next to each option appears.

<div style="background:#ffffff;border:1px solid #d0d7de;border-radius:6px;padding:16px 20px;margin:12px 0 20px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;">
  <p style="font-size:14px;font-weight:600;color:#1f2328;margin:0 0 4px;">Dynamic Components <span style="color:#cf222e;">*</span></p>
  <p style="font-size:12px;color:#57606a;margin:0 0 8px;">Select multiple</p>
  <div style="border:1px solid #d0d7de;border-radius:6px;overflow:hidden;width:240px;">
    <div style="background:#f6f8fa;border-bottom:1px solid #d0d7de;padding:4px 8px;font-size:12px;font-weight:600;color:#57606a;">Options</div>
    <div style="padding:4px 0;">
      <label style="display:flex;align-items:center;gap:8px;padding:4px 12px;font-size:14px;color:#1f2328;cursor:pointer;"><input type="checkbox" checked readonly style="accent-color:#0969da;"> Atmosphere</label>
      <label style="display:flex;align-items:center;gap:8px;padding:4px 12px;font-size:14px;color:#1f2328;cursor:pointer;"><input type="checkbox" readonly style="accent-color:#0969da;"> Aerosol</label>
      <label style="display:flex;align-items:center;gap:8px;padding:4px 12px;font-size:14px;color:#1f2328;cursor:pointer;"><input type="checkbox" checked readonly style="accent-color:#0969da;"> Ocean</label>
      <label style="display:flex;align-items:center;gap:8px;padding:4px 12px;font-size:14px;color:#1f2328;cursor:pointer;"><input type="checkbox" readonly style="accent-color:#0969da;"> Land Ice</label>
      <label style="display:flex;align-items:center;gap:8px;padding:4px 12px;font-size:14px;color:#1f2328;cursor:pointer;"><input type="checkbox" checked readonly style="accent-color:#0969da;"> Sea Ice</label>
    </div>
  </div>
</div>

1. Click the dropdown button to open the panel
2. Click each option you want — a checkmark appears next to it
3. Click the same option again to deselect it
4. Click anywhere outside the panel to close it

The closed button updates to show how many items are selected.

---

### Collapsible guidance

Many fields include a **▶ Detailed Guidance** section. Click it to expand examples and formatting rules for that field. Read these before filling in your answer — they contain the acceptance criteria reviewers use.

<div style="background:#ffffff;border:1px solid #d0d7de;border-radius:6px;padding:16px 20px;margin:12px 0 20px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;">
  <p style="font-size:14px;font-weight:600;color:#1f2328;margin:0 0 6px;">Model Name <span style="color:#cf222e;">*</span></p>
  <details style="margin-bottom:8px;font-size:13px;color:#57606a;">
    <summary style="cursor:pointer;color:#0969da;">Detailed Guidance</summary>
    <div style="margin-top:8px;padding-left:12px;border-left:3px solid #d0d7de;">
      <p style="margin:4px 0;"><strong>Model name (source_id)</strong></p>
      <p style="margin:4px 0;">Full identifier including family and version. For CMIP, this becomes the official <strong>source_id</strong>.</p>
      <p style="margin:4px 0;"><strong>Examples:</strong> CNRM-ESM2-1, HadGEM3-GC31-LL, CESM2, ACCESS-ESM1-5</p>
    </div>
  </details>
  <input type="text" placeholder="e.g. CNRM-ESM2-1" readonly style="width:100%;box-sizing:border-box;padding:5px 12px;font-size:14px;border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;color:#6e7781;height:32px;"/>
</div>

---

## Required fields

Fields marked with a red **\*** must be filled in before you can submit. If you try to submit with one empty, the form scrolls to it and highlights the box in red.

<div style="background:#ffffff;border:1px solid #d0d7de;border-radius:6px;padding:16px 20px;margin:12px 0 20px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;">
  <p style="font-size:14px;font-weight:600;color:#1f2328;margin:0 0 6px;">Release Year <span style="color:#cf222e;">*</span></p>
  <input type="text" readonly style="width:100%;box-sizing:border-box;padding:5px 12px;font-size:14px;border:1px solid #cf222e;border-radius:6px;background:#fff;color:#1f2328;height:32px;"/>
  <p style="font-size:12px;color:#cf222e;margin:4px 0 0;">This field is required.</p>
</div>

---

## Submitting

When all required fields are complete, scroll to the bottom and click **Submit new issue**.

<div style="background:#ffffff;border:1px solid #d0d7de;border-radius:6px;padding:16px 20px;margin:12px 0 20px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;text-align:right;">
  <button style="background:#1f883d;color:#fff;border:1px solid rgba(31,136,61,0.4);border-radius:6px;padding:5px 16px;font-size:14px;font-weight:500;cursor:pointer;">Submit new issue</button>
</div>

GitHub creates an issue from your answers. Automated validation runs within a couple of minutes — see [What to Expect on Submission](What_to_expect_on_submission/) for a full walkthrough of what happens next.

![A submitted form shown as a GitHub issue](assets/github/issue.png)

!!! note
    You can edit the issue body after submission at any time. Every edit re-triggers the validation workflow automatically — there is no need to close and reopen the issue.
