# Grid Cell and Subgrid Template Data
from cmipld.utils.ldparse import graph_entry
from cmipld.generate.template_utils import get_existing_entries_markdown

DATA = {
    'grid_type': graph_entry('constants:grid_type/_graph.json'),
    'grid_mapping': graph_entry('constants:grid_mapping/_graph.json'),
    'region': graph_entry('constants:region/_graph.json'),
    'temporal_refinement': graph_entry('constants:temporal_refinement/_graph.json'),
    'units': graph_entry('constants:units/_graph.json'),
    'truncation_method': graph_entry('constants:truncation_method/_graph.json'),
    'cell_variable_type': graph_entry('constants:cell_variable_type/_graph.json'),
    'subgrid_option': ['Create new subgrid', 'No subgrid (grid cell only)'],
    'issue_kind': ['New', 'Modify'],
    'prefill_links': get_existing_entries_markdown('grid_cell_and_subgrid', issue_kind='New')
}
