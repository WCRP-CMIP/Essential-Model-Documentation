# Grid Cell and Subgrid Template Data
from cmipld.utils.ldparse import graph_entry

DATA = {
    'grid_type': graph_entry('emd:grid_type/_graph.json', entry='ui_label'),
    'grid_mapping': graph_entry('emd:grid_mapping/_graph.json', entry='ui_label'),
    'region': graph_entry('emd:region/_graph.json', entry='ui_label'),
    'temporal_refinement': graph_entry('emd:temporal_refinement/_graph.json', entry='ui_label'),
    'units': graph_entry('emd:units/_graph.json', entry='ui_label'),
    'truncation_method': graph_entry('emd:truncation_method/_graph.json', entry='ui_label'),
    'cell_variable_type': graph_entry('emd:cell_variable_type/_graph.json', entry='ui_label'),
    'subgrid_option': ['Create new subgrid', 'No subgrid (grid cell only)'],
}
