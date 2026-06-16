# Frequently Asked Questions

!!! question ""
    For anything not covered here, email [emd@wcrp-cmip.org](mailto:emd@wcrp-cmip.org)

---

## Models & Grids

**Do I need to register separate models for different horizontal resolutions?**  
Yes. High- and low-resolution versions of the same model are registered as two separate models. This isn't double the work — you only need to define the new grid. If that grid is already registered, you can reference it and skip many of the initial steps.

**Do I register the computational grid or the output grid?**  
Both, if they differ. The computational grid is what the model runs on internally. If output is regridded (e.g. to 0.5°), that output grid also needs a label.

**Do I need to register vertical grids?**  
Only horizontal grids are required for output files. If there is no vertical grid (e.g. sea ice with only lat/long), you can register a "no vertical grid" or omit it entirely.

**Can grids be shared across model families?**  
Yes. Grids are reusable — even ones you didn't create. The same applies to model components. A similarity checker is available to help identify existing grids.

**How do I describe a staggered grid?**
If you have an Arakawa-B grid you will need to register two grids and if you have an Arakawa-C grid you will need to register three grids. The stagger locations of these grids is captured when you provide the lat-lon location of the western-most of the southern-most grid cells for each grid.

---

## Registration Process

**How do I edit an issue description?**  
Follow the steps in this [interactive guide](https://scribehow.com/embed-preview/Edit_an_Issues_Description_Field_on_GitHub__BFQ9OA50Q9-RbQvQ3r_GEQ?as=slides&size=flexible).

**When should I use "Modify" vs "Create" on the form?**  
Use "Create" for new entries. To modify an existing entry, email [emd@wcrp-cmip.org](mailto:emd@wcrp-cmip.org). Additive changes (e.g. extra papers, additional information) are generally welcome.

**My affiliation isn't listed — what do I do?**  
Register it using [this form](https://github.com/WCRP-CMIP/WCRP-constants/issues/new?template=organisation.yml). If urgent, complete the registration using the known acronym and submit — it will be held until the affiliation is approved but won't be lost.

**Can a registration issue be shared with colleagues?**  
Yes. Use the **Additional Collaborators** field in the issue form — they will receive notifications and can contribute.

**Does grid registration need to be completed in one go?**  
Ideally yes, but future edits are possible. Note that grids require more rigorous review than other fields, so they take the longest to process.

---

## Timelines & Review

**Is there a deadline for EMD submission?**  
There is no fixed date, but EMD registration must be completed **before any data is submitted to ESGF**. Plan around your own publication timeline.

**How do I know when action is required during review?**  
You will receive a GitHub notification. The [Progress Tracker](Progress_Tracker.html) is the easiest place to check — entries needing action are flagged with a flashing red **"Changes Requested"** label.

**Should I reply in the pull request or the issue?**  
Always reply in the **pull request**. Replies in the issue will eventually be picked up, but the PR is the primary place for review conversation.

---

## Preparation & Spreadsheets

**Are there spreadsheets I can use for preparation?**  
Spreadsheet templates are available below to help collate information internally before entering it into GitHub. Use these at your own risk — GitHub forms are always the main entry point for the EMD.

| Form | Spreadsheet |
|---|---|
| Model Family | [model_family.xlsx](assets/EMD_Form_Spreadsheets/model_family.xlsx) |
| Model | [model.xlsx](assets/EMD_Form_Spreadsheets/model.xlsx) |
| Model Component | [model_component.xlsx](assets/EMD_Form_Spreadsheets/model_component.xlsx) |
| Horizontal Computational Grid | [horizontal_computational_grid.xlsx](assets/EMD_Form_Spreadsheets/horizontal_computational_grid.xlsx) |
| Horizontal Grid Cell | [horizontal_grid_cell.xlsx](assets/EMD_Form_Spreadsheets/horizontal_grid_cell.xlsx) |
| Vertical Computational Grid | [vertical_computational_grid.xlsx](assets/EMD_Form_Spreadsheets/vertical_computational_grid.xlsx) |

---

## Further Help

- Full field definitions: [EMD Specification (Zenodo)](https://zenodo.org/records/17853724)
- Progress Tracker: [Progress Tracker](Progress_Tracker.html)
- Contact: [emd@wcrp-cmip.org](mailto:emd@wcrp-cmip.org)
