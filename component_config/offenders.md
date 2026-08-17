# void.txt
#
# Malformed component_config records that were removed because they could not be
# repaired from the data in the repository. Each was renamed to a hidden
# `.deprecated_*.json.bak` sibling so it no longer resolves; they should be
# `git rm`-ed. Format:  <original filename>  —  <reason>  [committer: <who>]

atmosphere_icon-a-1-1_tempgrid_olafmorgenstern-1781781928_tempgrid_olafmorgenstern-1778154923.json — both horizontal and vertical grids are unresolved tempgrid placeholders (no real h###/v### assigned)  [committer: olafmorgenstern]
land-surface_icon-land-1-1_g142_v122.json — horizontal grid "g142" is not a horizontal_computational_grid (no such grid exists) and model_component "icon-land-1-1" does not exist  [committer: unknown]
atmosphere_openifs-48r1__.json — empty horizontal and vertical grid slots; superseded by atmosphere_openifs-48r1_h107_v113.json  [committer: unknown]
hamocc ocean biogeochemistry_tempgrid_olafmorgenstern-1781782292_v121.json — spaces in id, tempgrid horizontal placeholder; superseded by ocean-biogeochemistry_hamocc_h129_v121.json  [committer: olafmorgenstern]
land-ice-pism-v1-2-line-h124-v135.json — all-hyphen duplicate with mismatched @id; superseded by land-ice_pism-v1-2-line_h124_v135.json  [committer: unknown]
atmospheric-chemistry_co2box-v1-0_no-vertical.json — empty horizontal grid; superseded by atmospheric-chemistry_co2box-v1-0_no-horizontal_no-vertical.json  [committer: unknown]
