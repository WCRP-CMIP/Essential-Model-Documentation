"""
Handler for Model (source_id) registration (Stage 4)

Produces one file:
  model/{source_id}.json  — the complete CMIP source_id record

Schema field names (from esgvoc):
  model_components   — list of component_config IDs
  coupled_components — list of coupling groups
  references         — list of DOI strings
"""

import os
import re
import json
from cmipld.utils.similarity import ReportBuilder
from cmipld.utils import crs as _crs

kind = __file__.split('/')[-1].replace('.py', '')

FIELD_MAP = {
    'model_name':           None,           # handled explicitly → validation_key + ui_label
    'model_family':         'family',
    'release_year':         'release_year',
    'reference_dois':       'references',
    'calendar_s_':          'calendar',
    'calendar(s)':          'calendar',
    'component_configs':    'model_components',
    'component_config_ids': 'model_components',
}

LIST_FIELDS = {
    'dynamic_components', 'prescribed_components', 'omitted_components',
    'calendar', 'calendar_s_', 'calendar(s)',
    'component_config_ids', 'component_configs', 'model_components',
}

IGNORE = {
    'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators',
    'model_name', 'model_family', 'name',
    'references', 'reference_dois',
    'embedded_components',
    'coupling_group_1', 'coupling_group_2', 'coupling_group_3',
    'coupling_group_4', 'coupling_group_5',
}


def _parse_list(value, lowercase=False) -> list:
    if isinstance(value, list):
        items = [str(v).strip() for v in value if str(v).strip()]
    else:
        delim = '\n' if '\n' in str(value) else ','
        items = [v.strip() for v in str(value).split(delim) if v.strip()]
    return [i.lower() for i in items] if lowercase else items


def _parse_refs(value) -> list:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [v.strip() for v in re.split(r'[,\s]+', str(value)) if v.strip()]


def _parse_embedded(raw) -> list:
    def _clean(s: str) -> str:
        return re.sub(r'\s*-\s*$', '', s.strip()).strip().lower()

    if isinstance(raw, list):
        result = []
        for item in raw:
            if isinstance(item, list) and len(item) >= 2:
                result.append([_clean(str(item[0])), _clean(str(item[1]))])
            elif isinstance(item, str):
                if ' - ' in item:
                    parts = item.split(' - ', 1)
                    result.append([_clean(parts[0]), _clean(parts[1])])
                else:
                    for sep in ('=', '>', ':'):
                        if sep in item:
                            parts = item.split(sep, 1)
                            result.append([_clean(parts[0]), _clean(parts[1])])
                            break
        return result

    if not raw:
        return []

    result = []
    for line in re.split(r'[,\n]+', str(raw)):
        line = line.strip()
        if not line:
            continue
        if ' - ' in line:
            parts = line.split(' - ', 1)
            result.append([_clean(parts[0]), _clean(parts[1])])
        else:
            for sep in ('=', '>', ':'):
                if sep in line:
                    parts = line.split(sep, 1)
                    result.append([_clean(parts[0]), _clean(parts[1])])
                    break
    return result


def run(parsed_issue, issue, dry_run=False):
    source_id = (parsed_issue.get('model_name') or parsed_issue.get('name') or '').strip()
    if not source_id:
        return None

    family = (parsed_issue.get('model_family') or parsed_issue.get('family') or '').strip()

    data = {
        "@context":       "_context",
        "@id":            source_id,
        "@type":          ["emd", "wcrp:model", "esgvoc:Model"],
        "validation_key": source_id,
        "ui_label":       source_id,
    }

    if family and family.lower() not in ('not specified', 'none', ''):
        data['family'] = family.lower()

    # References
    refs_raw = parsed_issue.get('reference_dois') or parsed_issue.get('references') or ''
    if refs_raw:
        data['references'] = _parse_refs(refs_raw)

    # Coupling groups
    coupling_groups = []
    for i in range(1, 6):
        raw = parsed_issue.get(f'coupling_group_{i}', '')
        if raw:
            group = _parse_list(raw, lowercase=True)
            if group:
                coupling_groups.append(group)

    # Embedded component pairs
    embedded_pairs = _parse_embedded(parsed_issue.get('embedded_components', ''))

    # Generic remaining fields
    for k, v in parsed_issue.items():
        if not v or k in IGNORE:
            continue
        canonical = FIELD_MAP.get(k, k)
        if canonical is None:
            continue  # explicitly suppressed (e.g. model_name)
        if isinstance(v, str) and v.lower() in ('_no response_', 'none', 'not specified', ''):
            continue
        if canonical in LIST_FIELDS or k in LIST_FIELDS:
            data[canonical] = _parse_list(v, lowercase=True)
        else:
            val = v.strip() if isinstance(v, str) else v
            data[canonical] = val

    # Normalise release_year to int
    if 'release_year' in data:
        try:
            data['release_year'] = int(data['release_year'])
        except (ValueError, TypeError):
            pass

    if embedded_pairs:
        data['embedded_components'] = embedded_pairs
    if coupling_groups:
        data['coupled_components'] = coupling_groups

    # Ensure all spec fields present. Use the right empty default for each
    # field's type — list fields get [], scalar fields get ''. Earlier this
    # loop assigned '' indiscriminately, which crashed downstream code that
    # did `data.get('dynamic_components', []) + ...` (because get() returned
    # the string '' rather than the [] default).
    SCALAR_KEYS = [
        'validation_key', 'ui_label', 'family', 'description', 'release_year',
    ]
    LIST_KEYS = [
        'calendar', 'references',
        'dynamic_components', 'prescribed_components', 'omitted_components',
        'model_components', 'embedded_components', 'coupled_components',
    ]
    for k in SCALAR_KEYS:
        if k not in data:
            data[k] = ''
    for k in LIST_KEYS:
        if k not in data:
            data[k] = []

    # Build and validate CRS
    dynamic = (data.get('dynamic_components', []) +
               data.get('prescribed_components', []))
    crs_errors = _crs.validate(dynamic, embedded_pairs, coupling_groups)
    if crs_errors:
        for e in crs_errors:
            print(f"\033[91m  ⚠ CRS: {e}\033[0m", flush=True)
        data['_crs_errors'] = crs_errors
    else:
        data['crs'] = _crs.build(dynamic, embedded_pairs, coupling_groups)
        print(f"\033[92m  ✓ CRS: {data['crs']}\033[0m", flush=True)

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    return {
        os.path.join('model', f"{source_id}.json"): data,
        '_author':       issue.get('author'),
        '_contributors': contributors,
        '_make_pull':    True,
        '_source_id':    source_id,
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    source_id  = files_to_write.get('_source_id', '')
    model_path = next((p for p in files_to_write if not p.startswith('_')), None)
    model_data = files_to_write.get(model_path, {}) if model_path else {}

    crs_errors = model_data.pop('_crs_errors', [])
    if crs_errors:
        print("\033[91m\n⚠  CRS validation errors:\033[0m", flush=True)
        for e in crs_errors:
            print(f"\033[91m    • {e}\033[0m", flush=True)
        model_data['_crs_note'] = (
            "\n> [!WARNING]\n"
            "> **Coupling/embedding errors** — `crs` field was not generated:\n"
            + "\n".join(f"> - {e}" for e in crs_errors)
        )
    else:
        crs_val = model_data.get('crs', '')
        if crs_val:
            print(f"\033[92m\n  CRS: {crs_val}\033[0m", flush=True)
            try:
                parsed = _crs.parse(crs_val)
                if parsed['embeddings']:
                    print("\033[92m  Embeddings:\033[0m", flush=True)
                    for parent, child in parsed['embeddings']:
                        print(f"\033[92m    {_crs.to_name(child)} → embedded in {_crs.to_name(parent)}\033[0m", flush=True)
                if parsed['coupling_pairs']:
                    print("\033[92m  Couplings:\033[0m", flush=True)
                    for a, b in parsed['coupling_pairs']:
                        print(f"\033[92m    {_crs.to_name(a)} ↔ {_crs.to_name(b)}\033[0m", flush=True)
            except Exception:
                pass

    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        # Strip name if JSONValidator re-injected it
        data.pop('name', None)
        print(f"\033[92m  Generating review report for {file_path} …\033[0m", flush=True)
        try:
            data['_validation_report'] = ReportBuilder(
                folder_url=f"emd:{kind}", kind=kind,
                item=data, link_threshold=80.0,
            ).build()
        except Exception as e:
            print(f"\033[91m  ⚠ Report generation failed: {e}\033[0m", flush=True)
            data['_validation_report'] = ''

    if model_data and source_id:
        clean = {k: v for k, v in model_data.items() if not k.startswith('_')}
        print("\n" + "=" * 60, flush=True)
        print(f"Model record: {source_id}", flush=True)
        print("=" * 60, flush=True)
        print(json.dumps(clean, indent=4), flush=True)
        print("=" * 60, flush=True)

        configs = clean.get('model_components', [])
        if configs:
            print(f"\033[92m\n  Component configs ({len(configs)}):\033[0m", flush=True)
            for c in configs:
                print(f"\033[92m    • {c}\033[0m", flush=True)
        else:
            print("\033[91m\n  ⚠ No model_components linked — add Stage 3 config IDs.\033[0m", flush=True)

        if crs_errors:
            print("\033[91m\n  ⚠ Fix coupling/embedding errors above before merging.\033[0m", flush=True)
