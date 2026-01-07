#!/bin/bash
# Cleanup script - run from Essential-Model-Documentation directory

echo "=== Cleaning up old files ==="

# Model components with realm prefix
cd data/model-component
rm -f aerosol_* atmosphere_* atmospheric-chemistry_* atmospheric_chemistry_* land-surface_* land_surface_* land_ice_* ocean-biogeochemistry_* ocean_biogeochemistry_* ocean_* sea-ice_* sea_ice_* 2>/dev/null
cd ../..

# Horizontal computational grids
cd data/horizontal-computational-grid
rm -f HGRID*.json EX_HGRID*.json 2>/dev/null
cd ../..

# Horizontal subgrids
cd data/horizontal-subgrid
rm -f HGRID*_subgrid_*.json EX_HGRID*_subgrid_*.json 2>/dev/null
cd ../..

# Horizontal grid cells
cd data/horizontal-grid-cells
rm -f HGRID*_cells_*.json EX_HGRID*_cells_*.json 2>/dev/null
cd ../..

# Vertical computational grids
cd data/vertical-computational-grid
rm -f VGRID*.json EX_VGRID*.json 2>/dev/null
cd ../..

# Examples cleanup
cd data/examples/model-component 2>/dev/null && rm -f land_ice_* land_surface_* 2>/dev/null && cd ../../..
cd data/examples/horizontal-computational-grid 2>/dev/null && rm -f EX_HGRID*.json 2>/dev/null && cd ../../..
cd data/examples/horizontal-subgrid 2>/dev/null && rm -f EX_HGRID*_subgrid_*.json 2>/dev/null && cd ../../..
cd data/examples/horizontal-grid-cells 2>/dev/null && rm -f EX_HGRID*_cells_*.json 2>/dev/null && cd ../../..
cd data/examples/vertical-computational-grid 2>/dev/null && rm -f EX_VGRID*.json 2>/dev/null && cd ../../..

echo "=== Done ==="
echo ""
echo "New naming conventions:"
echo "  - Model components: component name only (e.g., TACTIC.json)"
echo "  - Horizontal grids: HG###.json (starting at 100)"
echo "  - Horizontal subgrids: HSG###.json (starting at 100)"
echo "  - Horizontal grid cells: HGC###.json (starting at 100)"
echo "  - Vertical grids: VG###.json (starting at 100)"
echo "  - Families: lowercase (e.g., hadcm2.json)"
