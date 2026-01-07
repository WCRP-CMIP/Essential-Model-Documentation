#!/bin/bash
# Cleanup script for duplicate files
# Run from Essential-Model-Documentation directory

echo "=== Removing duplicate files ==="

# Model component duplicates (lowercase hyphenated versions)
cd data/model_component
rm -f arpege-climat-version-6-3.json
rm -f nemo-v3-6.json
rm -f reprobus-c-v2-0.json
rm -f surfex-v8-modeling-platform.json
echo "Removed model_component duplicates"
cd ../..

# Reference duplicates
cd data/reference
rm -f REF_BISICLES.json
rm -f REF_CLM4.json
rm -f ref-bisicles.json
rm -f ref-clm4.json
echo "Removed reference duplicates"
cd ../..

echo "=== Done ==="
echo ""
echo "Current directory structure:"
echo "  data/"
echo "    horizontal_computational_grid/  HG100-HG105"
echo "    horizontal_grid_cells/          HGC100-HGC104"
echo "    horizontal_subgrid/             HSG100-HSG106"
echo "    vertical_computational_grid/    VG100-VG106"
echo "    model/                          CNRM-ESM2-1e"
echo "    model_component/                10 components"
echo "    model_family/                   22 families"
echo "    reference/                      REF001-REF015"
