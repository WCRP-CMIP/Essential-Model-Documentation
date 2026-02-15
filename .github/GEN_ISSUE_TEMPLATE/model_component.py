# Model Component Template Data
import cmipld
from cmipld.utils.ldparse import graph_entry, name_entry
from cmipld.generate.template_utils import get_repo_info
from urllib.parse import urlencode

# Get component families (only those marked as 'component' type)
component_family = name_entry(
    [i for i in cmipld.get('emd:model_family/_graph.json', 2).get('contents', []) 
     if i.get('family_type') == 'component'],
    value='ui_label',
    key='validation_key'
)

# Get existing model components for prefill links
def get_prefill_links():
    repo_url, _, _ = get_repo_info()
    if not repo_url:
        repo_url = "https://github.com/WCRP-CMIP/Essential-Model-Documentation"
    
    components = cmipld.get('emd:model_component/_graph.json', 2).get('contents', [])
    
    links = []
    for comp in components:
        if not isinstance(comp, dict):
            continue
        
        name = comp.get('name', comp.get('validation_key', 'Unknown'))
        val_key = comp.get('validation_key', comp.get('@id', ''))
        comp_type = comp.get('component', '')
        
        # Build prefill params
        params = {
            'template': 'model_component.yml',
            'title': f'[EMD] Component: {name}',
            'issue_kind': '"Modify"',
        }
        
        # Add available fields
        if name:
            params['name'] = name
        if comp.get('description'):
            params['description'] = comp.get('description')
        if comp.get('code_base'):
            params['code_base'] = comp.get('code_base')
        
        url = f"{repo_url}/issues/new?" + urlencode(params) + f"&_={hash(name) % 100000}"
        
        label = f"{name} ({comp_type})" if comp_type else name
        links.append(f'<li><a href="{url}">{label}</a></li>')
    
    if not links:
        return "<p><em>No pre-registered components found.</em></p>"
    
    return "<ul>\n" + "\n".join(sorted(links)) + "\n</ul>"

DATA = {
    'component_type': graph_entry('constants:scientific_domain/_graph.json'),
    'component_family': component_family,
    'horizontal_grid': graph_entry('emd:horizontal_computational_grid/_graph.json'),
    'vertical_grid': graph_entry('emd:vertical_computational_grid/_graph.json'),
    'issue_kind': ['New', 'Modify'],
    'prefill_links': get_prefill_links()
}
