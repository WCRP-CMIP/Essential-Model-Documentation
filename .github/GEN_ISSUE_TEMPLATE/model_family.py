# Model Family Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Model Family Registration',
    'description': 'Register a model family for genealogy tracking',
    'title': '[EMD] Model Family:',
    'labels': ['emd-submission', 'family', 'Review'],
    'issue_category': 'model_family'
}

# Hardcoded data
DATA = {
    'family_type': [
        'Earth System Model',
        'Component Family'
    ],
    'component': [
        'aerosol',
        'atmosphere',
        'atmospheric-chemistry',
        'land-surface',
        'land-ice',
        'ocean',
        'ocean-biogeochemistry',
        'sea-ice'
    ],
    'institution': [
        'awi',
        'bas',
        'bcc',
        'bom',
        'cas',
        'cccma',
        'cmcc',
        'cnrm',
        'cnrm-cerfacs',
        'csiro',
        'csiro-arccss',
        'dkrz',
        'dwd',
        'ec-earth-consortium',
        'ecmwf',
        'gfdl',
        'inpe',
        'ipsl',
        'jamstec',
        'lbnl',
        'miroc',
        'mohc',
        'mpi-m',
        'nasa-giss',
        'nasa-gsfc',
        'ncar',
        'ncas',
        'ncc',
        'nerc',
        'niwa',
        'noaa-gfdl',
        'noc',
        'pnnl',
        'ukmo',
        'uob'
    ],
    'issue_kind': ['New', 'Modify']
}


# Mapping from form value to @type value
FAMILY_TYPE_MAPPING = {
    'Earth System Model': 'wcrp:global_model_family',
    'Component Family': 'wcrp:component_model_family'
}


def generate_model_family(issue_data):
    """
    Generate model_family entity from issue data.
    
    Returns:
        dict: The model_family entity
    """
    import re
    
    # Generate ID from name
    family_id = re.sub(r'[^a-z0-9]+', '-', issue_data['name'].lower()).strip('-')
    validation_key = issue_data['name'].replace(' ', '-')
    
    # Determine @type based on family_type selection
    family_type = issue_data.get('family_type', 'Earth System Model')
    type_value = FAMILY_TYPE_MAPPING.get(family_type, 'wcrp:global_model_family')
    
    # Create the entity
    entity = {
        'validation_key': validation_key,
        'ui_label': '',
        'description': issue_data['description'],
        'collaborative_institutions': issue_data.get('collaborative_institutions', []),
        'common_scientific_basis': 'none',
        'computational_requirements': 'none',
        'documentation': 'none',
        'established': issue_data.get('established', 'none') or 'none',
        'evolution': 'none',
        'license': 'none',
        'primary_institution': issue_data['primary_institution'],
        'programming_languages': 'none',
        'references': parse_dois(issue_data.get('reference_dois', '')),
        'representative_member': issue_data.get('representative_member', 'none') or 'none',
        'scientific_domains': issue_data.get('scientific_domains', []),
        'shared_code_base': 'none',
        'software_dependencies': 'none',
        'source_code_repository': 'none',
        'variation_dimensions': 'none',
        'website': issue_data.get('website', 'none') or 'none',
        '@context': '_context',
        '@type': [
            'emd',
            'wcrp:model_family',
            type_value,
            'esgvoc:ModelFamily'
        ],
        '@id': family_id
    }
    
    return entity


def parse_dois(doi_text):
    """Parse DOI URLs from textarea (one per line)."""
    if not doi_text:
        return []
    
    dois = [line.strip() for line in doi_text.split('\n') if line.strip()]
    return dois
