# Model Component Template Data
import cmipld
from cmipld.utils.ldparse import graph_entry, name_entry

# Get component families (only those marked as 'component' type)
component_family = name_entry(
    [i for i in cmipld.get('emd:model_family/_graph.json', 2).get('contents', []) 
     if i.get('family_type') == 'component'],
    value='ui_label',
    key='validation_key'
)

DATA = {
    'component_type': graph_entry('constants:scientific_domain/_graph.json'),
    'component_family': component_family,
    'horizontal_grid': [entry for entry in graph_entry('emd:horizontal_computational_grid/_graph.json') if 'tempgrid' not in entry.lower()],
    'vertical_grid': [entry for entry in graph_entry('emd:vertical_computational_grid/_graph.json') if 'tempgrid' not in entry.lower()],
    'issue_kind': ['New', 'Modify'],
}
