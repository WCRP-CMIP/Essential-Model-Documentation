# EMD Reviewer Checklist — Common Mistakes by File Type

Each section below lists the physical and scientific mistakes that reviewers most frequently catch. Use these as an initial checklist when reviewing submissions.

For full field constraints, valid ranges, and CV rules, open the EMD specification from the navigational menu. 

---

## `horizontal_grid_cell`

Grid cells describe the horizontal discretisation of a model component. They look simple but carry subtle consistency requirements that trip up submitters regularly.

### Grid type vs. domain mismatch

The `grid_type` must match the component's physical domain. Reviewers have flagged:

- `tripolar` applied to atmosphere or land components — tripolar grids are used exclusively in ocean and sea-ice models.
- `reduced_gaussian` or `spectral_gaussian` applied to an ocean component — these are atmosphere-only grid types.
- `regular_latitude_longitude` is valid for any domain.

### Resolution inconsistent with grid type

The resolution fields must be consistent with how that grid type is defined. The spacing formula differs by type:

- **Linear reduced Gaussian (TL):** Δx ≈ 180° / N (e.g. TL319 ≈ 0.56°)
- **Cubic octahedral (TCo):** Δx ≈ 10,000 km / N (e.g. TCo319 ≈ 31–36 km — both conventions are acceptable)
- If the grid type is ambiguous, ask the submitter to confirm the truncation number and resolution are consistent rather than asserting they are wrong.

Note that `horizontal_units: km` on a `regular_latitude_longitude` grid is valid — a companion degree-resolution entry may exist separately. Do not flag this.

### Cell count doesn't match resolution

`n_cells` must be consistent with the stated resolution and region at order-of-magnitude level:

- Global 1° grid → ~65,000 cells
- Global 0.25° grid → ~1,000,000 cells
- Global 0.1° grid → ~6,000,000 cells

A cell count that is off by an order of magnitude from what the resolution implies is almost always a transcription error.

### Duplicate of an existing grid cell

Submitters sometimes resubmit a corrected grid cell as a new entry rather than editing the original issue. Check whether an equivalent grid cell (same resolution, type, and domain) already exists.

### Blank descriptions are fine

An empty or blank `description` on a grid cell is the correct default. Never flag it.

---

## `horizontal_computational_grid`

Computational grids link grid cells to subgrids (mass, velocity-x, velocity-y). The most common mistake is structural.

### Subgrid variables combined into one entry

For staggered grids (e.g. Arakawa-C), mass and velocity variables must be registered as **separate** horizontal grid cells, each with their own subgrid entry. Submitters frequently combine them into a single form entry.

If the grid staggering is Arakawa-C, the submission should contain separate grid cell registrations for mass, x-velocity, and y-velocity — each potentially at different grid point locations.

### Orphaned grid cells

A grid cell may be defined in the submission but not actually referenced by any subgrid in the computational grid. This usually indicates a copy-paste error from a spreadsheet or a leftover from an earlier version of the submission.

### Units missing or wrong

The `horizontal_units` field is sometimes left blank or set incorrectly. Common case: degrees intended but field left empty, or "degree" missing when it should be present.

### No scientific concerns on structure

Do not flag data types, array vs. string representations, field formats, or schema structure. Raise scientific concerns only.

---

## `vertical_computational_grid`

### Top and bottom layer thickness swapped

This is the single most common mistake on vertical grid submissions. "Bottom" means the layer closest to the centre of the Earth (deepest soil layer, deepest ocean layer), and "top" means closest to the surface or top of atmosphere. Submitters regularly reverse these.

Check: is `bottom_layer_thickness` > `top_layer_thickness` for an ocean grid? That would be unusual — ocean grids typically have thin layers near the surface and thicker layers at depth.

### Bottom layer thickness equal to total thickness

A copy-paste error where `bottom_layer_thickness` is accidentally set to the same value as `total_thickness`. These should almost never be equal.

### Missing thickness and metadata fields

The fields `bottom_layer_thickness`, `top_layer_thickness`, `total_thickness`, and `description` are frequently left blank. Submitters should provide values as appropriate — see EMD specification §4.2.1 for guidance.

### Vertical coordinate inappropriate for domain

The `vertical_coordinate` must make physical sense for the component type:

- **Atmosphere:** `atmosphere_hybrid_sigma_pressure_coordinate`, `atmosphere_hybrid_height_coordinate`
- **Ocean:** `ocean_sigma_z_coordinate`, `ocean_s_coordinate`, `depth`, `z*`, `z-star` (both valid forms of the z-star rescaled height coordinate)
- **Soil / land surface:** `depth`
- **Sea ice / land ice:** `height`, `land_ice_sigma_coordinate`

### Level count outside plausible range

`n_z` should fall within typical ranges for the domain:

- Atmosphere: 19–137 levels (flag if < 10 or > 200)
- Ocean: 25–75 levels (flag if < 10 or > 100)
- Soil: 4–20 layers
- Sea ice: 1–10 layers

### Total thickness outside plausible range

- Atmosphere: 30,000–85,000 m
- Ocean: 3,000–7,000 m
- Soil: 1–20 m
- Sea ice: 1–10 m

### Blank descriptions are fine

As with grid cells, an empty `description` on a vertical grid is intentional and correct.

---

## `model_component`

Model component submissions are the most error-prone form type. They touch two files — the component definition and its configuration — and reviewers check both.

### Description missing or describing the wrong component

A blank or one-word description is flagged. The description should summarise what the component does scientifically — not just say "used in model X." Descriptions that clearly describe a different component type (e.g. an ocean description on an atmosphere component) should be flagged for rewriting.

Descriptions will be used in broad communications such as the Copernicus Climate Change Service, so they should be written for a general scientific audience, not just as internal technical notes.

### References not submitted as DOIs

Literature references must use DOI format (`https://doi.org/...`), not bare URLs or PDF links. Submitters sometimes provide a direct link to a journal page or PDF instead.

### Version strings use dots instead of hyphens

EMD requires hyphen-separated version strings: `v1-1-3` not `v1.1.3`. Dot-separated versions should be flagged with a suggestion to use hyphens.

### Broken or unresolvable reference links

Check that reference URLs actually resolve. Broken links are common — especially for preprints or institutional repositories that have moved.

---

## `component_config`

### Horizontal grid reference doesn't match the component domain

The horizontal grid linked in the configuration must be scientifically appropriate for the component type. An ocean component config should not point to an atmosphere-only grid type, and vice versa.

### Vertical grid reference doesn't match the component type

- `ocean_biogeochemistry` should share the ocean's vertical grid, not have its own atmospheric vertical grid.
- `land_surface` should reference a soil-depth vertical grid, not an atmospheric one.

### Grid references point to unmerged or temporary entries

The configuration sometimes references grids that haven't been approved yet (still in `tempgrid_*` form). While these are renamed on merge, check that the referenced grid actually exists as a submitted entry.

---

## `model_family`

### Institution identifiers don't match the CMIP7 CVs

The `primary_institution` and `collaborative_institutions` fields must match valid entries in the [CMIP7 Controlled Vocabularies](https://github.com/WCRP-CMIP/CMIP7-CVs/tree/main/institution). Submitters often use informal abbreviations that don't correspond to any registered institution.

### References scoped to individual components

Model family references should describe the model **as a whole**, not individual components. Reviewers flag submissions that include papers about a specific ocean or atmosphere component — these belong on the component entry, not the family.

### Missing collaborative institutions

If the model family is developed across multiple institutions, the `collaborative_institutions` field should list them. There is a separate field for this — submitters sometimes try to list everything under `primary_institution`.

---

## `model`

### Realm listed in both dynamic and omitted components

A realm cannot appear in both `dynamic_components` and `omitted_components`. This is a logical contradiction that must be resolved.

### Realm listed in both dynamic and prescribed components

Similarly, a realm should not appear in both `dynamic_components` and `prescribed_components` without explanation.

### Embedded component coupling errors

Coupling topology is the hardest part of the model form to get right. Common mistakes:

- Listing both directions of an embedding (e.g. `aerosol-atmosphere` and `atmosphere-aerosol`) when only one direction is correct.
- An embedded realm also appearing in a coupling group — an embedded component should not also be separately coupled.
- Land ice listed as embedded without explanation — land ice is typically dynamic, not embedded.

### Model description too technical for downstream use

The model `description` will appear in climate service communications (e.g. Copernicus). A purely technical description is insufficient — it should give a high-level overview accessible to non-specialists.

### Release year implausible

Flag `release_year` if before 1990 or in the future.

---

## General — all file types

### What not to flag

- `@id`, `@type`, `@context`, `validation_key`, `ui_label` — these are auto-generated infrastructure fields.
- `tempgrid_*` values — temporary identifiers, renamed on merge.
- Empty `description` on grid files — intentional and correct.
- Filenames, JSON structure, field formats — syntax is out of scope; focus on science.


