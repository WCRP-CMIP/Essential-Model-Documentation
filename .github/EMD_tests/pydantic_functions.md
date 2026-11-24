# EMD validation checks

_Generated from `.github/EMD_tests` by `document.py`. Regenerate it; do not edit by hand._

Every record submitted through an issue is checked against the model for its folder.
**Errors** stop the issue becoming a pull request; the submitter is told what to fix on the issue.
**Warnings** let the pull request be made and are listed on it for the reviewer.

## Contents

- [Field types](#field-types)
- [Checks on every record](#checks-on-every-record)
- [component_config](#component_config)
- [horizontal_computational_grid](#horizontal_computational_grid)
- [horizontal_grid_cell](#horizontal_grid_cell)
- [horizontal_subgrid](#horizontal_subgrid)
- [model](#model)
- [model_component](#model_component)
- [model_family](#model_family)
- [vertical_computational_grid](#vertical_computational_grid)

## Field types

The types used in the field tables below.

| Type | Rule |
|---|---|
| `link to <folder>` | A value that must name an entry of `folder`, e.g. Link("grid_type") or Link("model_family"). |
| `links to <folder>` | A list of Link(folder), each value once. A single value is read as a list of one. |
| `References` | A reference is a URL (error), and a DOI unless the paper is still in preparation (warning). |
| `Positive` | a number > 0 |
| `PositiveInt` | a whole number > 0 |
| `Latitude` | a number ≥ -90 and ≤ 90 |
| `Longitude` | a number ≥ 0 and < 360 |

## Checks on every record

Every record has these fields and checks, whatever its folder.

### Fields

| Field | Required | Type | Allowed values |
|---|---|---|---|
| `@id` | yes | str | matches `^[a-z0-9-]+(_[a-z0-9-]+)*$` |
| `@type` | yes | list[str] | — |
| `@context` | yes | Literal["_context"] | — |
| `validation_key` | yes | str | — |
| `ui_label` | no | str | — |
| `description` | no | str | — |

### Checks

| Check | Severity | What it checks |
|---|---|---|
| `empty_means_not_given` | Tidies input | An empty string means "not given", so it is dropped before validation. |
| `property_names_are_snake_case` | Error | Property names use lower case and "_" only (the JSON-LD names starting with @ aside). |
| `validation_key_matches_id` | Error | validation_key is @id, in any case, with '-' and '_' treated alike. |
| `type_names_emd_and_its_folder` | Error | @type holds "emd" and names the record's folder. |
| `file_name_matches_id` | Error | The file name, without .json, is @id. Checked when the record is read by load(). |
| `id_is_not_a_submission_placeholder` | Error | A record kept in the repository has its real id, not the one its issue was given. |

---

## component_config

One component configuration. Its id is {realm}_{model_component}_{horizontal grid}_{vertical grid}.

### Fields

| Field | Required | Type | Allowed values |
|---|---|---|---|
| `model_component` | yes | link to model_component | any of the 152 entries of `model_component/` |
| `horizontal_computational_grid` | no | link to horizontal_computational_grid | any of the 78 entries of `horizontal_computational_grid/` |
| `vertical_computational_grid` | no | link to vertical_computational_grid | any of the 88 entries of `vertical_computational_grid/` |

### Checks

| Check | Severity | What it checks |
|---|---|---|
| `both_grids_named` | Warning | Both grids are named; a component without one uses no-horizontal or no-vertical. |
| `id_names_its_component_and_grids` | Warning | The id ends with _{model_component}_{horizontal grid}_{vertical grid}. |
| `used_by_a_model` | Warning | Every configuration should belong to a model's model_components (EMD 2). |

---

## horizontal_computational_grid

One horizontal computational grid. Required: arrangement and horizontal_subgrids, except on no-horizontal.

### Fields

| Field | Required | Type | Allowed values |
|---|---|---|---|
| `arrangement` | no | link to arrangement | `arakawa-a` · `arakawa-b` · `arakawa-c` · `arakawa-d` · `arakawa-e` |
| `horizontal_subgrids` | no | links to horizontal_subgrid | any of the 157 entries of `horizontal_subgrid/` |

### Checks

| Check | Severity | What it checks |
|---|---|---|
| `arrangement_and_subgrids_given` | Error | Both are required (EMD Appendix B 4.1.1). no-horizontal stands for "no grid" and has neither. |
| `used_by_a_component_config` | Warning | A grid no component is integrated on is usually a leftover from an earlier submission. |

---

## horizontal_grid_cell

One horizontal grid cell description. Required: grid_type and region (EMD Appendix B 4.1.3).

### Fields

| Field | Required | Type | Allowed values |
|---|---|---|---|
| `grid_type` | yes | link to grid_type | `basin-by-latitude` · `cubed-sphere` · `cubic-octahedral-spectral-reduced-gaussian` · `discrete-lines` · `discrete-points` · `displaced-pole` · `hierarchical-discrete-global-grid` · `icosahedral` · `icosahedral-geodesic` · `icosahedral-geodesic-dual` · `linear-spectral-gaussian` · `plane-projection` · `quadratic-spectral-gaussian` · `reduced-gaussian` · `regular-gaussian` · `regular-latitude-longitude` · `rotated-pole` · `spectral-gaussian` · `spectral-reduced-gaussian` · `stretched` · `tripolar` · `unstructured` · `unstructured-polygonal` · `unstructured-quadrilateral` · `unstructured-triangular` · `yin-yang` |
| `region` | yes | links to region, at least one | `30s-90s` · `antarctica` · `arctic` · `global` · `greenland` · `limited-area` · `northern-hemisphere` · `southern-hemisphere` · `tropics` |
| `grid_mapping` | no | link to grid_mapping | `albers-conical-equal-area` · `azimuthal-equidistant` · `geostationary` · `healpix` · `lambert-azimuthal-equal-area` · `lambert-conformal-conic` · `lambert-cylindrical-equal-area` · `latitude-longitude` · `mercator` · `orthographic` · `polar-stereographic` · `rotated-latitude-longitude` · `sinusoidal` · `stereographic` · `transverse-mercator` · `vertical-perspective` |
| `temporal_refinement` | no | link to temporal_refinement | `adaptive` · `dynamically-stretched` · `static` |
| `units` | no | link to units | `degree` · `k` · `km` · `meter` · `pa` |
| `truncation_method` | no | link to truncation_method | `rhomboidal` · `triangular` |
| `truncation_number` | no | PositiveInt | — |
| `x_resolution` | no | Positive | — |
| `y_resolution` | no | Positive | — |
| `southernmost_latitude` | no | Latitude | — |
| `westernmost_longitude` | no | Longitude | — |
| `n_cells` | no | PositiveInt | — |

### Checks

| Check | Severity | What it checks |
|---|---|---|
| `units_given_with_resolution` | Error | A resolution needs its units (EMD 4.1.3). |
| `edges_set_together` | Error | The southern and western edges are given together (EMD Appendix B 4.1.3). |
| `truncation_set_together` | Error | The truncation method and number are given together (EMD Appendix B 4.1.3). |
| `spectral_grid_has_truncation` | Warning | A spectral grid type should give its truncation number. |
| `resolution_matches_truncation` | Warning | On a spectral grid that names its convention, the resolution is within 35 % of what N gives. |
| `n_cells_given_unless_adaptive` | Warning | n_cells is given when the cell count is fixed, and left out when it is adaptive (EMD 4.1.3). |
| `n_cells_matches_resolution` | Warning | On a regular grid, n_cells is within 10 times of (360/dx) * (180/dy) * area of the regions. |
| `southern_edge_on_pole_or_half_cell` | Warning | On a regular latitude-longitude grid near the pole, the edge is -90 or -90 + dy/2. |
| `grid_mapping_suits_grid_type` | Warning | A plane-projection grid uses a projected mapping; a regular latitude-longitude grid does not (EMD 7.6, 7.7). |
| `used_by_a_subgrid` | Warning | Grid cells may describe an output grid on their own (EMD 4.1.3), so an unused one is only odd. |

---

## horizontal_subgrid

One subgrid. Required: cell_variable_type and horizontal_grid_cell (EMD Appendix B 4.1.2).

### Fields

| Field | Required | Type | Allowed values |
|---|---|---|---|
| `cell_variable_type` | yes | links to cell_variable_type, at least one | `divergence` · `mass` · `u-velocity` · `v-velocity` · `velocity` · `vorticity` · `x-velocity` · `y-velocity` |
| `horizontal_grid_cell` | yes | link to horizontal_grid_cell | any of the 195 entries of `horizontal_grid_cell/` |

### Checks

| Check | Severity | What it checks |
|---|---|---|
| `accept_plural_spelling` | Tidies input | EMD 4.1.2 writes horizontal_grid_cells; this folder's _context writes horizontal_grid_cell. Read either. |
| `velocity_or_x_y_velocity` | Error | velocity is not listed with x-velocity or y-velocity (EMD Appendix B 4.1.2). |
| `axes_named_x_and_y` | Warning | EMD 7.4 names the velocity axes x and y, not u and v. |
| `id_lists_the_variable_types` | Warning | The id is {cell}_{type}_{type}...; the types in it are the ones listed in cell_variable_type. |
| `belongs_to_a_computational_grid` | Error | A subgrid is part of a horizontal computational grid and cannot stand alone (EMD Appendix A). |

---

## model

One model. Required: name, description, release_year, calendar, references, dynamic_components and model_components (EMD Appendix B 2).

### Fields

| Field | Required | Type | Allowed values |
|---|---|---|---|
| `name` | yes | str | — |
| `description` | yes | str | — |
| `release_year` | yes | int | — |
| `calendar` | yes | links to calendar, at least one | `360-day` · `365-day` · `366-day` · `julian` · `none` · `proleptic-gregorian` · `standard` · `tai` · `utc` |
| `references` | yes | References, at least one | — |
| `family` | no | link to model_family | any of the 74 entries of `model_family/` |
| `dynamic_components` | yes | links to scientific_domain, at least one | `aerosol` · `atmosphere` · `atmospheric-chemistry` · `land-ice` · `land-surface` · `ocean` · `ocean-biogeochemistry` · `sea-ice` |
| `prescribed_components` | no | links to scientific_domain | `aerosol` · `atmosphere` · `atmospheric-chemistry` · `land-ice` · `land-surface` · `ocean` · `ocean-biogeochemistry` · `sea-ice` |
| `omitted_components` | no | links to scientific_domain | `aerosol` · `atmosphere` · `atmospheric-chemistry` · `land-ice` · `land-surface` · `ocean` · `ocean-biogeochemistry` · `sea-ice` |
| `embedded_components` | no | list[Pair] | — |
| `coupled_components` | no | list[Pair] | — |
| `model_components` | yes | links to component_config, at least one | any of the 178 entries of `component_config/` |
| `crs` | no | str | — |

### Checks

| Check | Severity | What it checks |
|---|---|---|
| `dynamic_not_also_omitted` | Error | A component cannot be simulated and also absent (EMD 2). |
| `pairs_name_two_dynamic_components` | Error | Each embedded or coupled pair names two different dynamic components (EMD Appendix B 2). |
| `one_host_each` | Error | An embedded component has one host (EMD 3.1). |
| `no_embedding_cycle` | Error | A component cannot be embedded, directly or indirectly, in itself. |
| `embedded_components_do_not_couple` | Error | An embedded component cannot be coupled with any other component (EMD 3.1). |
| `hosts_coupled_into_one_group` | Error | With more than one superior host, the couplings join them all into one group (EMD 3.1). |
| `family_given` | Warning | family is given; a model with no family uses no-family. |
| `prescribed_not_in_another_list` | Warning | A prescribed component is not also dynamic or omitted (reviewer checklist). |
| `embedding_is_usual` | Warning | Each (embedded, host) pair is one of the usual patterns (reviewer checklist). |
| `release_year_plausible` | Warning | release_year is from 1990 to this year (reviewer checklist). |
| `crs_agrees_with_lists` | Warning | crs names each dynamic component once, each prescribed one once with "^", and the same pairs. |
| `description_mentions_each_component` | Warning | The description mentions every dynamic, prescribed and omitted component (EMD 2). |

---

## model_component

One model component. Required: component, description, references, and a name or ui_label.

### Fields

| Field | Required | Type | Allowed values |
|---|---|---|---|
| `component` | yes | link to scientific_domain | `aerosol` · `atmosphere` · `atmospheric-chemistry` · `land-ice` · `land-surface` · `ocean` · `ocean-biogeochemistry` · `sea-ice` |
| `description` | yes | str | — |
| `references` | yes | References, at least one | — |
| `family` | no | link to model_family | any of the 74 entries of `model_family/` |
| `name` | no | str | — |
| `code_base` | no | str | — |

### Checks

| Check | Severity | What it checks |
|---|---|---|
| `has_a_name` | Error | name is required (EMD Appendix B 3). The repository usually holds it in ui_label, so either counts. |
| `family_given` | Warning | family is given; a component with no family uses no-family. |
| `name_has_hyphenated_version` | Warning | The name holds a version written with hyphens, not dots (reviewer checklist). |
| `description_is_specific` | Warning | The description says what the component simulates, not only where it is used. |
| `code_base_is_a_fixed_url` | Warning | code_base is a URL, or private/none. A repository URL names a commit, tag or release (EMD 3). |
| `used_by_a_component_config` | Warning | A component reaches a model through a component_config; without one it is documented but unused. |

---

## model_family

One model family. Nothing is required by the specification; gaps are warnings.

### Fields

| Field | Required | Type | Allowed values |
|---|---|---|---|
| `primary_institution` | no | str | — |
| `collaborative_institutions` | no | TextList | — |
| `scientific_domains` | no | links to scientific_domain | `aerosol` · `atmosphere` · `atmospheric-chemistry` · `land-ice` · `land-surface` · `ocean` · `ocean-biogeochemistry` · `sea-ice` |
| `references` | no | References | — |
| `family_type` | no | str | — |
| `established` | no | Any | — |
| `representative_member` | no | Any | — |

### Checks

| Check | Severity | What it checks |
|---|---|---|
| `institution_given_once` | Warning | A primary institution is given, and it is not also listed as a collaborator. |
| `references_and_description_given` | Warning | A family cites at least one reference and has a description. |

---

## vertical_computational_grid

One vertical grid. Thicknesses are in metres. A value left out must be explained in description.

### Fields

| Field | Required | Type | Allowed values |
|---|---|---|---|
| `vertical_coordinate` | no | link to vertical_coordinate | `air-potential-temperature` · `air-pressure` · `atmosphere-hybrid-height-coordinate` · `atmosphere-hybrid-sigma-pressure-coordinate` · `atmosphere-ln-pressure-coordinate` · `atmosphere-sigma-coordinate` · `atmosphere-sleve-coordinate` · `depth` · `geopotential-height` · `height` · `land-ice-sigma-coordinate` · `ocean-double-sigma-coordinate` · `ocean-hybrid-pressure-isopycnic-coordinate` · `ocean-hybrid-z-star-isopycnic-coordinate` · `ocean-s-coordinate` · `ocean-s-coordinate-g1` · `ocean-s-coordinate-g2` · `ocean-sigma-coordinate` · `ocean-sigma-z-coordinate` · `sea-water-potential-temperature` · `sea-water-pressure` · `z-star` |
| `n_z` | no | PositiveInt | — |
| `n_z_range` | no | list[PositiveInt] | — |
| `top_layer_thickness` | no | Positive | — |
| `bottom_layer_thickness` | no | Positive | — |
| `total_thickness` | no | Positive | — |

### Checks

| Check | Severity | What it checks |
|---|---|---|
| `n_z_or_n_z_range` | Error | A fixed level count or a range, not both (EMD Appendix B 4.2). |
| `range_runs_low_to_high` | Error | n_z_range is [minimum, maximum]. |
| `description_explains_what_is_left_out` | Error | When a property is left out, description must be set to explain it (EMD Appendix B 4.2). |
| `top_layer_within_column` | Error | The top layer cannot be thicker than the whole column. |
| `bottom_layer_is_not_whole_column` | Warning | A bottom layer as thick as the whole column is usually a copy-paste error. |
| `top_and_bottom_fit_in_column` | Warning | The top and bottom layers together fit inside the column. |
| `used_by_a_component_config` | Warning | A grid no component is integrated on is usually a leftover from an earlier submission. |
