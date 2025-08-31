# EMD property requirements (2025-08-29)

For each section, the following are given:

<property name> <MANDATORY|OPTIONAL> <source> <notes>

where

<property name> is the per-section name of each property (e.g. family, prescribed_components, etc.)

<MANDATORY|OPTIONAL> indicates if the providing a property value is mandatory or optional.

<source> indicates the type of values expected (e.g. string, integer, CV). Other compound types (such as <Reference>) may also be indicated.

<notes>, if present on optional properties, indicates at least some (not necessarily all) cases where the property does/doesn't need to be provided.

## 2. Top-level model

- name MANDATORY string
- family MANDATORY string
- dynamic_components MANDATORY CV
- prescribed_components MANDATORY CV
- omitted_components MANDATORY CV
- description MANDATORY string
- calendar MANDATORY CV
- release_year MANDATORY integer
- references MANDATORY <Reference>
 
## 3. Model components
 
- component MANDATORY CV
- name MANDATORY string
- family MANDATORY string
- description MANDATORY string
- references MANDATORY <Reference>
- code_base MANDATORY string
- embedded_in OPTIONAL CV
- coupled_with OPTIONAL CV 
- native_horizontal_grid MANDATORY <Horizontal grid>
- native_vertical_grid MANDATORY <Vertical grid>
 
## 4.1. Horizontal grid
 
- grid MANDATORY CV
- description OPTIONAL string
- grid_mapping MANDATORY CV
- region MANDATORY CV
- temporal_refinement MANDATORY CV
- arrangement MANDATORY CV
- resolution_x OPTIONAL float
- resolution_y OPTIONAL float
- horizontal_units OPTIONAL CV NOTE: Required if any of resolution_x, resolution_y are set
- n_cells MANDATORY integer
- n_sides OPTIONAL integer
- n_vertices OPTIONAL integer
- truncation_method OPTIONAL CV
- truncation_number OPTIONAL integer
- resolution_range_km MANDATORY [float,float]
- mean_resolution_km MANDATORY float
- nominal_resolution MANDATORY CV

## 4.2. Vertical grid

- coordinate MANDATORY CV
- description OPTIONAL string
- n_z OPTIONAL integer NOTE: Must be omitted if n_z_range is set
- n_z_range OPTIONAL [integer,integer] NOTE: Must be omitted if n_z is set
- bottom_layer_thickness OPTIONAL float
- top_layer_thickness OPTIONAL float
- top_of_model OPTIONAL float
- vertical_units OPTIONAL CV NOTE: Required if any of bottom_layer_thickness, top_layer_thickness, top_of_model are set

## 5. References

- citation MANDATORY string
- doi MANDATORY string
