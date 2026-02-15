# Model Template Data
from cmipld.utils.ldparse import graph_entry

DATA = {
    'component': graph_entry('constants:model_component_type/_graph.json'),
    'calendar': graph_entry('constants:calendar/_graph.json'),
    'model_family': graph_entry('emd:model_family/_graph.json'),
    'issue_kind': ['New', 'Modify']
}
