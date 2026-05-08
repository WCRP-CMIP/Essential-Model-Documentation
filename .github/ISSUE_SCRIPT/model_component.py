"""
Handler for Model Component registration (Stage 3)

Produces one or two files per submission:
  1. model_component/{name_slug}.json  — the reusable component record (always)
  2. component_config/{config_id}.json — component + grid binding for use in Stage 4
                                         ONLY when both a horizontal AND vertical
                                         computational grid are supplied.

Config ID format: {component_type}_{name_slug}_{h###}_{v###}
e.g.  ocean_nemo-v3-6_h101_v103
"""

import os
import re
from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')

IGNORE = {'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators',
          'component_type', 'component_name', 'component_family',
          'horizontal_grid', 'vertical_grid', 'name'}


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'[^a-z0-9\-\.]', '', s)
    return s.strip('-')


def _parse_list(value: str) -> list:
    delim = '\n' if '\n' in value else ','
    return [v.strip() for v in value.split(delim) if v.strip()]


def run(parsed_issue, issue, dry_run=False):
    component_type = (parsed_issue.get('component_type') or '').strip().lower()
    component_name = (parsed_issue.get('component_name') or '').strip()
    h_grid         = (parsed_issue.get('horizontal_grid') or '').strip().lower()
    v_grid         = (parsed_issue.get('vertical_grid') or '').strip().lower()
    family         = (parsed_issue.get('component_family') or '').strip().lower()
    description    = (parsed_issue.get('description') or '').strip()

    if not component_name:
        return None  # fall back to generic handler

    name_slug = _slugify(component_name)

    _MISSING = {'', 'not specified', 'none'}
    make_config = (h_grid not in _MISSING) and (v_grid not in _MISSING)
    config_id   = f"{component_type}_{name_slug}_{h_grid}_{v_grid}" if make_config else ''

    # ── 1. model_component record ─────────────────────────────────────────────
    component_data = {
        "@context":       "_context",
        "@id":            name_slug,
        "@type":          ["emd", "wcrp:model_component", "esgvoc:ModelComponent"],
        "validation_key": name_slug,
        "ui_label":       component_name,
        "component":      component_type,
    }
    if family and family.lower() not in ('not specified', 'none', ''):
        component_data["family"] = family

    for k, v in parsed_issue.items():
        if k in IGNORE or not v:
            continue
        if isinstance(v, str) and v.lower() in ('_no response_', 'none', 'not specified', ''):
            continue
        if k == 'reference_dois':
            component_data['references'] = _parse_list(v)
        elif k == 'code_repository':
            component_data['code_base'] = v.strip()
        else:
            component_data[k] = v.strip() if isinstance(v, str) else v

    # ── 2. component_config record (only when both grids are provided) ─────────
    if not make_config:
        print(
            '\033[93m  ⚠ No component_config created: '
            'both a horizontal AND vertical computational grid must be supplied.\033[0m',
            flush=True,
        )

    config_data = None
    if make_config:
        config_data = {
            "@context":                      "_context",
            "@id":                           config_id,
            "@type":                         ["emd", "wcrp:component_config", "esgvoc:ComponentConfig"],
            "validation_key":                config_id,
            "ui_label":                      config_id,
            "model_component":               name_slug,
            "horizontal_computational_grid": h_grid,
            "vertical_computational_grid":   v_grid,
        }


        CONFIG_KEYS = [
            'validation_key', 'ui_label', 'model_component',
            'horizontal_computational_grid', 'vertical_computational_grid', 'description',
        ]
        for k in CONFIG_KEYS:
            if k not in config_data:
                config_data[k] = ''

    # Ensure all spec fields present — assign '' if not set
    COMPONENT_KEYS = [
        'validation_key', 'ui_label', 'component', 'family', 'description',
        'references', 'code_base',
    ]
    for k in COMPONENT_KEYS:
        if k not in component_data:
            component_data[k] = ''

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    component_path = os.path.join('model_component', f"{name_slug}.json")

    result = {
        component_path:  component_data,
        '_author':       issue.get('author'),
        '_contributors': contributors,
        '_make_pull':    True,
        '_config_id':    config_id,
    }
    if make_config and config_data is not None:
        config_path = os.path.join('component_config', f"{config_id}.json")
        result[config_path] = config_data

    return result


_LINK_FORM_URL = (
    'https://github.com/WCRP-CMIP/Essential-Model-Documentation'
    '/issues/new?template=link_existing_component.yml'
)


def _post_issue_comment(issue_number, body):
    """Post a comment on the original issue via the gh CLI."""
    import subprocess
    try:
        subprocess.run(
            ['gh', 'issue', 'comment', str(issue_number), '--body', body],
            check=True,
        )
    except Exception as e:
        print(f'\033[91m  ⚠ Could not post issue comment: {e}\033[0m', flush=True)


def update(files_to_write, parsed_issue, issue, dry_run=False):
    config_id   = files_to_write.get('_config_id', '')
    config_path = next((p for p in files_to_write if 'component_config' in p), None)
    config_data = files_to_write.get(config_path, {}) if config_path else {}

    # ── No-config notice ──────────────────────────────────────────────────────
    # When the submitter omitted one or both grids, no component_config was
    # created.  Notify them on both the issue and (via _validation_report) the PR.
    if not config_id:
        component_path = next(
            (p for p in files_to_write if not p.startswith('_') and 'model_component' in p),
            None,
        )
        name_slug = (
            files_to_write.get(component_path, {}).get('@id', '')
            if component_path else ''
        )
        no_config_notice = (
            '> [!WARNING]\n'
            '> ## Component (only) created.\n'
            '> **Insufficient computational grids supplied. See below.**\n'
            '>\n'
            '> A horizontal **and** vertical computational grid are both required to '
            'generate a `component_config` record. '
            'Because one or both were not supplied, only the `model_component` '
            'record has been created in this PR.\n'
            '>\n'
            '> Once your component is merged, use '
            f'**[Stage 3: Link Existing Component]({_LINK_FORM_URL})** '
            'to create the configuration by selecting:\n'
            '>\n'
            f'> - **Model Component:** `{name_slug}`\n'
            '> - **Horizontal Grid:** your `h###` from Stage 2a\n'
            '> - **Vertical Grid:** your `v###` from Stage 2b\n'
            '>\n'
            '> _The config ID will be auto-generated and pushed directly to '
            '`src-data` without a separate review._'
        )

        # Append to the component\'s PR report
        if component_path and component_path in files_to_write:
            existing = files_to_write[component_path].get('_validation_report') or ''
            files_to_write[component_path]['_validation_report'] = (
                (existing + '\n\n' + no_config_notice).strip()
            )

        # Also comment directly on the issue
        issue_number = issue.get('number') or issue.get('issue_number')
        if issue_number and not dry_run:
            _post_issue_comment(issue_number, no_config_notice)

    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        # Strip name if JSONValidator re-injected it
        data.pop('name', None)
        print(f"\033[92m  Generating review report for {file_path} …\033[0m", flush=True)
        report_kind = 'component_config' if 'component_config' in file_path else 'model_component'
        try:
            data['_validation_report'] = ReportBuilder(
                folder_url=f"emd:{report_kind}", kind=report_kind,
                item=data, link_threshold=80.0,
            ).build()
        except Exception as e:
            print(f"\033[91m  ⚠ Report generation failed: {e}\033[0m", flush=True)
            data['_validation_report'] = ''

    if config_id and config_data:
        import json
        clean = {k: v for k, v in config_data.items() if not k.startswith('_')}
        print("\n" + "=" * 60, flush=True)
        print("Component Config file created:", flush=True)
        print("=" * 60, flush=True)
        print(json.dumps(clean, indent=4), flush=True)
        print("=" * 60, flush=True)
        print(
            f"\033[92m✅ Config ID: '{config_id}'\n"
            f"   Use this ID in Stage 4 (Model) under 'component_configs'.\n"
            f"\n   Example:\n"
            f"     \"component_configs\": [\"{config_id}\", ...]\033[0m",
            flush=True,
        )
