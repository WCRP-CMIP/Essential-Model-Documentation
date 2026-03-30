"""
Handler for Model (source_id) registration (Stage 4)

Produces one file:
  model/{source_id}.json  — the complete CMIP source_id record

The source_id references component_config IDs from Stage 3 under
'component_configs', and records coupling/embedding topology as a
Canonical Realm String (CRS) via cmipld.utils.crs.
"""

import os
import json
from cmipld.utils.similarity import ReportBuilder
from cmipld.utils import crs as _crs

kind = __file__.split('/')[-1].replace('.py', '')

FIELD_MAP = {
    'model_name':     'name',
    'model_family':   'family',
    'release_year':   'release_year',
    'reference_dois': 'references',
    'calendar_s_':    'calendar',
    'calendar(s)':    'calendar',
}

LIST_FIELDS = {
    'dynamic_components', 'prescribed_components', 'omitted_components',
    'calendar', 'calendar_s_', 'calendar(s)',
    'component_config_ids', 'component_configs',
}

IGNORE = {
    'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators',
    'model_name', 'model_family',
    # handled explicitly below
    'embedded_components',
    'coupling_group_1', 'coupling_group_2', 'coupling_group_3',
    'coupling_group_4', 'coupling_group_5',
}


def _parse_list(value) -> list:
    if isinstance(value, list):
        return [v.strip() for v in value if str(v).strip()]
    delim = '\n' if '\n' in str(value) else ','
    return [v.strip() for v in str(value).split(delim) if v.strip()]


def _parse_embedded(raw) -> list:
    """
    Parse embedded_components field into [[parent, child], ...] pairs.

    Accepts any of:
      "atmosphere=aerosol, atmosphere=atmospheric-chemistry"
      "atmosphere>aerosol\natmosphere>atmospheric-chemistry"
      [["atmosphere","aerosol"], ...]
    """
    if isinstance(raw, list):
        result = []
        for item in raw:
            if isinstance(item, list) and len(item) >= 2:
                result.append([item[0].strip(), item[1].strip()])
            elif isinstance(item, str) and ('=' in item or '>' in item or ':' in item):
                sep = '=' if '=' in item else ('>' if '>' in item else ':')
                parts = item.split(sep, 1)
                result.append([parts[0].strip(), parts[1].strip()])
        return result

    if not raw:
        return []

    lines = str(raw).replace('\n', ',').split(',')
    result = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        for sep in ('=', '>', ':'):
            if sep in line:
                parts = line.split(sep, 1)
                result.append([parts[0].strip(), parts[1].strip()])
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
        "@type":          ["wcrp:model", "esgvoc:model"],
        "validation_key": source_id,
        "name":           source_id,
    }

    if family and family.lower() not in ('not specified', 'none', ''):
        data['family'] = family

    # ── Coupling groups ───────────────────────────────────────────────────────
    coupling_groups = []
    for i in range(1, 6):
        raw = parsed_issue.get(f'coupling_group_{i}', '')
        if raw:
            group = _parse_list(raw)
            if group:
                coupling_groups.append(group)

    # ── Embedding pairs ───────────────────────────────────────────────────────
    embedded_raw = parsed_issue.get('embedded_components', '')
    embedded_pairs = _parse_embedded(embedded_raw)

    # ── Remaining scalar / list fields ────────────────────────────────────────
    for k, v in parsed_issue.items():
        if not v or k in IGNORE:
            continue
        canonical = FIELD_MAP.get(k, k)
        if canonical in LIST_FIELDS or k in LIST_FIELDS:
            data[canonical] = _parse_list(v)
        else:
            val = v.strip() if isinstance(v, str) else v
            if val and str(val).lower() not in ('_no response_', 'none', 'not specified'):
                data[canonical] = val

    # Rename component_config_ids → component_configs
    if 'component_config_ids' in data:
        data['component_configs'] = data.pop('component_config_ids')

    # Normalise release_year to int
    if 'release_year' in data:
        try:
            data['release_year'] = int(data['release_year'])
        except (ValueError, TypeError):
            pass

    # ── Store structured coupling/embedding fields ────────────────────────────
    if embedded_pairs:
        data['embedded_components'] = embedded_pairs
    if coupling_groups:
        data['coupling_groups'] = coupling_groups

    # ── Build and validate CRS ────────────────────────────────────────────────
    dynamic = (data.get('dynamic_components', []) +
               data.get('prescribed_components', []))

    crs_errors = _crs.validate(dynamic, embedded_pairs, coupling_groups)
    if crs_errors:
        for e in crs_errors:
            print(f"  ⚠ CRS validation: {e}", flush=True)
        data['_crs_errors'] = crs_errors
    else:
        data['crs'] = _crs.build(dynamic, embedded_pairs, coupling_groups)
        print(f"  ✓ CRS: {data['crs']}", flush=True)

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []
    file_path    = os.path.join('model', f"{source_id}.json")

    return {
        file_path:       data,
        '_author':       issue.get('author'),
        '_contributors': contributors,
        '_make_pull':    True,
        '_source_id':    source_id,
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    source_id  = files_to_write.get('_source_id', '')
    model_path = next((p for p in files_to_write if not p.startswith('_')), None)
    model_data = files_to_write.get(model_path, {}) if model_path else {}

    # Report any CRS errors prominently before generating the review report
    crs_errors = model_data.pop('_crs_errors', [])
    if crs_errors:
        print("\n⚠  CRS validation errors — coupling/embedding structure is invalid:", flush=True)
        for e in crs_errors:
            print(f"    • {e}", flush=True)
        crs_note = (
            "\n> [!WARNING]\n"
            "> **Coupling/embedding errors** — `crs` field was not generated:\n"
            + "\n".join(f"> - {e}" for e in crs_errors)
        )
        model_data['_crs_note'] = crs_note
    else:
        crs_val = model_data.get('crs', '')
        if crs_val:
            print(f"\n  CRS: {crs_val}", flush=True)
            # Show human-readable expansion of the CRS
            try:
                parsed = _crs.parse(crs_val)
                if parsed['embeddings']:
                    print("  Embeddings:", flush=True)
                    for parent, child in parsed['embeddings']:
                        print(f"    {_crs.to_name(child)} → embedded in {_crs.to_name(parent)}", flush=True)
                if parsed['coupling_pairs']:
                    print("  Couplings:", flush=True)
                    for a, b in parsed['coupling_pairs']:
                        print(f"    {_crs.to_name(a)} ↔ {_crs.to_name(b)}", flush=True)
            except Exception:
                pass

    # Generate similarity/review report
    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        print(f"  Generating review report for {file_path} …", flush=True)
        try:
            data['_validation_report'] = ReportBuilder(
                folder_url=f"emd:{kind}", kind=kind,
                item=data, link_threshold=80.0,
            ).build()
        except Exception as e:
            print(f"  ⚠ Report generation failed: {e}", flush=True)
            data['_validation_report'] = ''

    # Print the completed model record
    if model_data and source_id:
        clean = {k: v for k, v in model_data.items() if not k.startswith('_')}

        print("\n" + "=" * 60, flush=True)
        print(f"Model record: {source_id}", flush=True)
        print("=" * 60, flush=True)
        print(json.dumps(clean, indent=4), flush=True)
        print("=" * 60, flush=True)

        configs = clean.get('component_configs', [])
        crs_val = clean.get('crs', '')

        print(f"\n  ✅ source_id: '{source_id}'", flush=True)
        if crs_val:
            print(f"  CRS fingerprint: {crs_val}", flush=True)
        if configs:
            print(f"\n  Component configs ({len(configs)}):", flush=True)
            for c in configs:
                print(f"    • {c}", flush=True)
        else:
            print(
                "\n  ⚠ No component_configs linked.\n"
                "    Add Stage 3 config IDs to complete registration.",
                flush=True,
            )

        if crs_errors:
            print(
                "\n  ⚠ Fix the coupling/embedding errors above before merging.\n"
                "    The 'crs' field will be generated automatically once resolved.",
                flush=True,
            )

