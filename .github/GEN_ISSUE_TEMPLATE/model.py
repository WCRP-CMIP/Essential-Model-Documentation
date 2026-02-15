# Model Template Data
from cmipld.utils.ldparse import graph_entry

# Get scientific domains for embedded pairings
domains = graph_entry('constants:scientific_domain/_graph.json')

# Generate all pairings: a -> b where a != b
embedded_pairs = []
for a in domains:
    for b in domains:
        if a != b:
            embedded_pairs.append(f"{a} -> {b}")
            
model_family = name_entry(
    [i for i in cmipld.get('emd:model_family/_graph.json', 2).get('contents', []) 
     if i.get('family_type') == 'model'],
    value='ui_label',
    key='validation_key'
)

DATA = {
    'component': graph_entry('constants:scientific_domain/_graph.json'),
    'calendar': graph_entry('constants:calendar/_graph.json'),
    'model_family': model_family,
    'embedded_pairs': sorted(embedded_pairs),
    'issue_kind': ['New', 'Modify']
}
