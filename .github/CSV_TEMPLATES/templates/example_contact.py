# Example Contact Form Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Simple Contact Form',
    'description': 'A simple example contact form template.',
    'title': '[Example] Contact Form',
    'labels': ['example', 'contact']
}

# Data for this template
DATA = {
    'contact_types': {
        'technical': {'id': 'technical', 'validation-key': 'technical'},
        'scientific': {'id': 'scientific', 'validation-key': 'scientific'},
        'administrative': {'id': 'administrative', 'validation-key': 'administrative'}
    },
    'priority_levels': ['Low', 'Medium', 'High', 'Urgent'],
    # Hardcoded options for contact_method field
    'contact_method_options': ['Email', 'Phone', 'Video Call', 'In Person']
}
