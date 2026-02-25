# Horizontal Computational Grid Template Data
from cmipld.utils.ldparse import graph_entry

DATA = {
    'arrangement': graph_entry('constants:arrangement/_graph.json'),
    'cell_variable_type': graph_entry('constants:cell_variable_type/_graph.json'),
    'horizontal_grid_cells': graph_entry('emd:horizontal_grid_cells/_graph.json'),
    'subgrids': graph_entry('emd:horizontal_subgrid/_graph.json'),
    'issue_kind': ['New', 'Modify']
}
