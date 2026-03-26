"""
Handler for Model Family registration (Supporting stage)

Handles both:
  - Earth System / coupled model families  (family_type = "model")
  - Single-domain component families       (family_type = "component")
"""

import os
from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')

# Fields that come in as comma- or newline-separated strings → lists
LIST_FIELDS = {'collaborative_institutions', 'scientific_domains', 'reference_dois'}

# Fields to drop from the final JSON
IGNORE = {'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators',
          'family_type', 'name'}


def _clean_id(s: str) -> str:
    return s.strip().lower().replace(' ', '-')


def _parse_list(value: str) -> list:
    """Split comma- or newline-separated string into a cleaned list."""
    delim = '\n' if '\n' in value else ','
    return [v.strip() for v in value.split(delim) if v.strip()]


def run(parsed_issue, issue, dry_run=False):
    family_name = parsed_issue.get('family_name') or parsed_issue.get('name') or ''
    if not family_name:
        return None  # fall back to generic handler

    atid         = _clean_id(family_name)
    family_type  = (parsed_issue.get('family_type') or '').strip().lower()

    # Set @type based on family_type dropdown value
    if family_type == 'component':
        wcrp_type  = 'wcrp:component_family'
        esgvoc_type = 'esgvoc:component_family'
    else:
        # "model" or anything else → coupled ESM family
        wcrp_type  = 'wcrp:model_family'
        esgvoc_type = 'esgvoc:model_family'

    # Build data from remaining parsed fields
    data = {
        "@context":       "_context",
        "@id":            atid,
        "@type":          [wcrp_type, esgvoc_type],
        "validation_key": atid,
        "family_type":    family_type or 'model',
        "name":           family_name.strip(),
    }

    for k, v in parsed_issue.items():
        if k in IGNORE or not v:
            continue
        if k in LIST_FIELDS:
            data[k] = _parse_list(v)
        else:
            data[k] = v.strip() if isinstance(v, str) else v

    # Normalise website: ensure https:// prefix
    if 'website' in data and data['website']:
        url = data['website']
        if not url.startswith(('http://', 'https://')):
            data['website'] = f"https://{url}"

    # Normalise established: keep only if a plausible year
    if 'established' in data:
        try:
            year = int(data['established'])
            data['established'] = year if 1900 <= year <= 2100 else None
        except (ValueError, TypeError):
            data['established'] = None

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []
    file_path    = os.path.join(kind, f"{atid}.json")

    return {file_path: data, '_author': issue.get('author'),
            '_contributors': contributors, '_make_pull': True}


def update(files_to_write, parsed_issue, issue, dry_run=False):
    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        print(f"  Generating review report for {file_path} …", flush=True)
        try:
            data['_validation_report'] = ReportBuilder(
                folder_url=f"emd:{kind}s", kind=kind, item=data, link_threshold=80.0
            ).build()
        except Exception as e:
            print(f"  ⚠ Report generation failed: {e}", flush=True)
            data['_validation_report'] = ''
