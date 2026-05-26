# Link Existing Component Template Data
from cmipld.utils.ldparse import graph_entry

DATA = {
    'model_component':               graph_entry('emd:model_component/_graph.json'),
    'horizontal_computational_grid': graph_entry('emd:horizontal_computational_grid/_graph.json'),
    'vertical_computational_grid':   graph_entry('emd:vertical_computational_grid/_graph.json'),
}
