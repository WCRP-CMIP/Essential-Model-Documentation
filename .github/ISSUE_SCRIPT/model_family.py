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

# Fields whose values are @type:@id links — must be lowercased
LINKED_FIELDS = {'collaborative_institutions', 'scientific_domains', 'primary_institution'}

# Fields to drop entirely from the final JSON
IGNORE = {'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators',
          'family_type', 'family_name', 'name'}

# Bare (non-@) keys that JSONValidator may inject — must not appear in output
BAD_KEYS = {'id', 'type', 'context'}


def _clean_id(s: str) -> str:
    return s.strip().replace(' ', '-')

def _parse_list(value) -> list:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    s = str(value)
    # Split on newlines or commas first; fall back to whitespace (e.g. space-separated URLs)
    if '\n' in s:
        parts = s.split('\n')
    elif ',' in s:
        parts = s.split(',')
    else:
        import re
        parts = re.split(r'\s+(?=https?://)', s)
    return [v.strip() for v in parts if v.strip()]


def run(parsed_issue, issue, dry_run=False):
    family_name = parsed_issue.get('family_name') or parsed_issue.get('name') or ''
    if not family_name:
        return None  # fall back to generic handler

    atid           = _clean_id(family_name)
    family_type    = (parsed_issue.get('family_type') or '').strip().lower() or 'model'

    # @type based on family_type
    if family_type == 'component':
        wcrp_type   = 'wcrp:model_family'
        esgvoc_type = 'esgvoc:ModelFamily'
    else:
        wcrp_type   = 'wcrp:model_family'
        esgvoc_type = 'esgvoc:ModelFamily'

    data = {
        "@context":       "_context",
        "@id":            atid,
        "@type":          ["emd", wcrp_type, esgvoc_type],
        "validation_key": atid,
        "ui_label":       family_name.strip(),
        "family_type":    family_type,
    }

    for k, v in parsed_issue.items():
        if k in IGNORE or not v:
            continue
        if isinstance(v, str) and v.lower() in ('_no response_', 'none', 'not specified', ''):
            continue
        if k in LIST_FIELDS:
            items = _parse_list(v)
            data[k] = [i.lower() for i in items] if k in LINKED_FIELDS else items
        elif k in LINKED_FIELDS:
            data[k] = v.strip().lower()
        else:
            data[k] = v.strip() if isinstance(v, str) else v

    # Normalise website
    if data.get('website') and not str(data['website']).startswith(('http://', 'https://')):
        data['website'] = f"https://{data['website']}"

    # 'Year Established' → 'established' as int
    year_val = data.pop('year_established', None) or data.pop('established', None)
    if year_val:
        try:
            year = int(year_val)
            data['established'] = year if 1900 <= year <= 2100 else None
        except (ValueError, TypeError):
            data['established'] = None

    # 'Reference DOIs' → 'references' as list
    refs = data.pop('reference_dois', None) or data.pop('references', None)
    if refs:
        data['references'] = _parse_list(refs)

    # Strip bad bare keys
    for key in BAD_KEYS:
        data.pop(key, None)

    # Ensure all spec fields present — assign '' if not set
    ALL_KEYS = [
        'validation_key', 'ui_label', 'family_type',
        'description', 'website', 'established', 'references',
        'primary_institution', 'collaborative_institutions', 'scientific_domains',
    ]
    for k in ALL_KEYS:
        if k not in data:
            data[k] = ''

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []
    file_path    = os.path.join(kind, f"{atid}.json")

    return {
        file_path:       data,
        '_author':       issue.get('author'),
        '_contributors': contributors,
        '_make_pull':    True,
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue

        # Re-strip bad keys in case JSONValidator re-introduced them
        for key in BAD_KEYS | {'name'}:
            data.pop(key, None)

        print(f"\033[92m  Generating review report for {file_path} …\033[0m", flush=True)
        try:
            data['_validation_report'] = ReportBuilder(
                folder_url=f"emd:{kind}", kind=kind, item=data, link_threshold=80.0
            ).build()
        except Exception as e:
            print(f"\033[91m  ⚠ Report generation failed: {e}\033[0m", flush=True)
            data['_validation_report'] = ''
