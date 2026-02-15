# Model Component Template Data
from cmipld.utils.ldparse import graph_entry

DATA = {
    'component': graph_entry('constants:model_component_type/_graph.json'),
    'component_family': graph_entry('emd:model_component/_graph.json'),
    'issue_kind': ['New', 'Modify']
}
