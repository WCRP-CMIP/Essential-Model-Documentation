# Horizontal Computational Grid Template Data
from cmipld.utils.ldparse import graph_entry

DATA = {
    'arrangement': graph_entry('constants:arrangement/_graph.json'),
    'grid_type': graph_entry('constants:grid_type/_graph.json'),
    'grid_mapping': graph_entry('constants:grid_mapping/_graph.json'),
    'subgrids': graph_entry('emd:horizontal_subgrid/_graph.json'),
    'issue_kind': ['New', 'Modify']
}
