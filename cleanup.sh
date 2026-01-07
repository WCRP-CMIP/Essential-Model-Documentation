#!/bin/bash
# Cleanup script for EMD data directory
# Run this from the Essential-Model-Documentation directory

cd data

# Remove examples directory (content merged into main files)
rm -rf examples

# Remove EX_ prefixed files (merged into numbered files)
rm -f horizontal-computational-grid/EX_HGRID*.json
rm -f horizontal-grid-cells/EX_HGRID*.json
rm -f horizontal-subgrid/EX_HGRID*.json
rm -f vertical-computational-grid/EX_VGRID*.json
rm -f reference/EX_REF*.json

# Remove old hyphenated component files (replaced by underscore versions per EMD spec)
rm -f model-component/atmospheric-chemistry_REPROBUS-C_v2_0.json
rm -f model-component/land-surface_SURFEX_v8_modeling_platform.json
rm -f model-component/ocean-biogeochemistry_PISCESv2-gas.json
rm -f model-component/sea-ice_GELATO.json

# Remove HadAM3 (incomplete example file)
rm -f model-component/atmosphere_HadAM3.json

echo "Cleanup complete!"
