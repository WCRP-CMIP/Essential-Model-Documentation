# Model Family Template Data
from cmipld.utils.ldparse import graph_entry

DATA = {
    'institution': graph_entry('constants:organisation/_graph.json'),
    'component': graph_entry('constants:scientific_domain/_graph.json'),
    'family_type': ['model', 'component'],
    'issue_kind': ['New', 'Modify']
}
