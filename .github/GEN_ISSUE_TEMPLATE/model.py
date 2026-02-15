# Model Template Data
import cmipld
from cmipld.utils.ldparse import graph_entry, name_entry
from cmipld.generate.template_utils import get_existing_entries_markdown

# Get scientific domains with ui_labels
domains_data = cmipld.get('constants:scientific_domain/_graph.json', 2).get('contents', [])
domain_labels = [d.get('ui_label', d.get('validation_key')) for d in domains_data if isinstance(d, dict)]

# Generate all pairings using ui_labels: a -> b where a != b
embedded_pairs = []
for a_label in domain_labels:
    for b_label in domain_labels:
        if a_label != b_label:
            embedded_pairs.append(f"{a_label} -> {b_label}")

# Get model families (only those marked as 'model' type)
model_family = name_entry(
    [i for i in cmipld.get('emd:model_family/_graph.json', 2).get('contents', []) 
     if i.get('family_type') == 'model'],
    value='ui_label',
    key='validation_key'
)

# Get component configs for dropdown
component_configs = graph_entry('emd:component_config/_graph.json')

DATA = {
    'component': sorted(domain_labels),
    'calendar': graph_entry('constants:calendar/_graph.json'),
    'model_family': model_family,
    'component_configs': component_configs,
    'embedded_pairs': sorted(embedded_pairs),
    'domains': sorted(domain_labels),
    'issue_kind': ['New', 'Modify'],
    'prefill_links': get_existing_entries_markdown('model', issue_kind='New')
}
