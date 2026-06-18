# Link Existing Component Template Data
from cmipld.utils.ldparse import graph_entry

DATA = {
    'model_component':               graph_entry('emd:model_component/_graph.json'),
    'horizontal_computational_grid': [entry for entry in graph_entry('emd:horizontal_computational_grid/_graph.json') if 'tempgrid' not in entry.lower()],
    'vertical_computational_grid':   [entry for entry in graph_entry('emd:vertical_computational_grid/_graph.json') if 'tempgrid' not in entry.lower()],
}
