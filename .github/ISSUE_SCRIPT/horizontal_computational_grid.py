"""
Handler for Horizontal Computational Grid registration (Stage 2a)

Produces N+1 files per submission:
  horizontal_subgrid/{cell}-{vtype}.json               — one per slot (content-addressed, e.g. g100-mass)
  horizontal_computational_grid/tempgrid_{author}-{timestamp}.json — temporary comp grid file

Subgrid IDs remain content-addressed for deduplication.
The comp grid file gets a tempgrid_ prefix and is renamed to h### on PR merge
by tempgrid-rename.yml, which scans existing h### files on src-data.
"""

import os
import time

from cmipld.utils.id_generation import generate_id_from_issue
from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')

IGNORE = {'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators',
          'arrangement', 'additional_information', 'description'}


def _slot_fields(parsed_issue: dict, issue_body: str = '') -> list[dict]:
    """
    Extract subgrid slots by walking the raw issue body.

    The form repeats identical ### headers for each slot, which parse_issue_body
    collapses to a single key (last value wins). We must parse the raw body to
    recover all occurrences in order.
    """
    slots = []

    if issue_body:
        # Walk raw body — pair each 'Grid Cells' header with the next 'Variable Types'
        CELL_HEADER  = 'grid cells'
        VTYPE_HEADER = 'variable types'
        PLACEHOLDER  = {'not specified', 'none', '_no response_', ''}

        lines       = issue_body.split('\n')
        current_key = None
        current_val = []
        sections    = []   # [(normalised_header, value_str), ...]

        for line in lines:
            if line.startswith('### '):
                if current_key is not None:
                    sections.append((current_key, ' '.join(current_val).strip()))
                current_key = line[4:].strip().lower()
                current_val = []
            elif current_key is not None:
                current_val.append(line.strip())
        if current_key is not None:
            sections.append((current_key, ' '.join(current_val).strip()))

        # Pair consecutive cell/vtype headers
        n = 0
        i = 0
        while i < len(sections):
            key, val = sections[i]
            if CELL_HEADER in key:
                cell = val.strip()
                vtypes = ''
                # Look ahead for the immediately following variable types header
                if i + 1 < len(sections) and VTYPE_HEADER in sections[i + 1][0]:
                    vtypes = sections[i + 1][1].strip()
                    i += 1  # consume the vtype section too
                if cell and cell.lower() not in PLACEHOLDER:
                    n += 1
                    vtype_list = [v.strip() for v in vtypes.split(',') if v.strip()] if vtypes else []
                    slots.append({'cell': cell, 'variable_types': vtype_list, 'n': n})
            i += 1
        return slots

    # Fallback: numbered keys from parsed_issue (works if field_ids are numbered)
    for n in range(1, 5):
        cell = (
            parsed_issue.get(f'horizontal_grid_cells_{n}') or
            parsed_issue.get(f'grid_cells_(select_or_define_horizontal_grid_cells_for_this_subgrid)_{n}') or
            ''
        ).strip()
        vtypes = (
            parsed_issue.get(f'cell_variable_type_{n}') or
            parsed_issue.get(f'variable_types_(variable_types_at_this_cell_location)_{n}') or
            ''
        ).strip()
        if cell and cell.lower() not in ('not specified', 'none', ''):
            vtype_list = [v.strip() for v in vtypes.split(',') if v.strip()] if vtypes else []
            slots.append({'cell': cell, 'variable_types': vtype_list, 'n': n})
    return slots


def run(parsed_issue, issue, dry_run=False):
    arrangement = (parsed_issue.get('arrangement') or '').strip().lower()
    description = parsed_issue.get('additional_information') or parsed_issue.get('description') or ''

    slots       = _slot_fields(parsed_issue, issue.get('body', ''))
    repo_root   = os.environ.get('GITHUB_WORKSPACE', os.getcwd())

    # Temp ID for the comp grid file — renamed to h### on PR merge
    author     = issue.get('author') or 'unknown'
    created_at = issue.get('created_at') or ''
    temp_id    = f"tempgrid_{generate_id_from_issue(author, created_at)['id']}" \
                 if created_at else f"tempgrid_{author}_{int(time.time())}"

    if not slots:
        print('  ❌ No subgrid slots found — cannot build a computational grid ID.', flush=True)
        return None

    files       = {}
    subgrid_ids = []
    slot_report = []   # for update() summary

    for slot in slots:
        # Lowercase the cell ID and variable types — these are links to other entries
        cell       = slot['cell'].strip().lower()
        vtypes     = [v.strip().lower() for v in slot['variable_types']]
        vtype_slug = '-'.join(sorted(vtypes)) if vtypes else 'untyped'
        sid        = f"{cell}-{vtype_slug}"
        file_path  = os.path.join('horizontal_subgrid', f"{sid}.json")
        reused     = os.path.exists(os.path.join(repo_root, file_path))

        subgrid_data = {
            "@context":              "_context",
            "@id":                   sid,
            "@type":                 ["wcrp:horizontal_subgrid", "esgvoc:horizontal_subgrid"],
            "validation_key":        sid,
            "horizontal_grid_cells": [{"@id": cell}],
        }
        # Update slot so slot_report and subgrid_ids use the normalised values
        slot = {**slot, 'cell': cell, 'variable_types': vtypes}
        if slot['variable_types']:
            subgrid_data['cell_variable_type'] = slot['variable_types']

        files[file_path] = subgrid_data
        subgrid_ids.append(sid)
        slot_report.append({**slot, 'sid': sid, 'reused': reused})
        tag = '♻ matched' if reused else '+ new'
        print(f"  [{tag}] Slot {slot['n']}: subgrid '{sid}'", flush=True)

    # Collect paths of matched subgrids so new_issue.py skips the 'file exists' check
    force_modify = {
        os.path.join('horizontal_subgrid', f"{s['sid']}.json")
        for s in slot_report if s['reused']
    }

    hgrid_data = {
        "@context":            "_context",
        "@id":                 temp_id,
        "@type":               ["wcrp:horizontal_computational_grid",
                                "esgvoc:horizontal_computational_grid"],
        "validation_key":      temp_id,
        "horizontal_subgrids": subgrid_ids,
    }
    if arrangement:
        hgrid_data['arrangement'] = arrangement
    if description:
        hgrid_data['description'] = description

    files[os.path.join('horizontal_computational_grid', f"{temp_id}.json")] = hgrid_data

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    return {
        **files,
        '_author':        issue.get('author'),
        '_contributors':  contributors,
        '_make_pull':     True,
        '_atid':          temp_id,
        '_slot_report':   slot_report,
        '_subgrid_ids':   subgrid_ids,
        '_force_modify':  force_modify,
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    atid        = files_to_write.get('_atid', '')
    slot_report = files_to_write.get('_slot_report', [])
    subgrid_ids = files_to_write.get('_subgrid_ids', [])

    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        report_kind = (
            'horizontal_subgrid' if 'horizontal_subgrid' in file_path
            else 'horizontal_computational_grid'
        )
        # folder names are singular — do not pluralise
        folder_url = f"emd:{report_kind}"
        try:
            report = ReportBuilder(
                folder_url=folder_url, kind=report_kind,
                item=data, link_threshold=80.0,
            ).build()
            data['_validation_report'] = report
            status = '✓' if report else '(empty)'
        except Exception as e:
            print(f"  ⚠ Report generation failed for {file_path}: {e}", flush=True)
            data['_validation_report'] = ''
            status = '⚠ failed'
        print(f"  Report {status}: {file_path}", flush=True)

    if atid:
        import json as _json

        # Print each subgrid file
        print("\n" + "=" * 60, flush=True)
        print("Stage 2a — Subgrid files:", flush=True)
        print("=" * 60, flush=True)
        for s in slot_report:
            tag         = '♻ matched' if s['reused'] else '+ new'
            subgrid_key = os.path.join('horizontal_subgrid', f"{s['sid']}.json")
            subgrid_obj = files_to_write.get(subgrid_key, {})
            clean       = {k: v for k, v in subgrid_obj.items() if not k.startswith('_')}
            print(f"\n  [{tag}] horizontal_subgrid/{s['sid']}.json", flush=True)
            print(_json.dumps(clean, indent=4), flush=True)

        # Print the computational grid file
        hgrid_key = os.path.join('horizontal_computational_grid', f"{atid}.json")
        hgrid_obj = files_to_write.get(hgrid_key, {})
        clean     = {k: v for k, v in hgrid_obj.items() if not k.startswith('_')}
        print("\n" + "=" * 60, flush=True)
        print(f"  [+ new] horizontal_computational_grid/{atid}.json", flush=True)
        print(_json.dumps(clean, indent=4), flush=True)
        print("=" * 60, flush=True)
        print(
            f"\n  ✅ Temporary ID: '{atid}'\n"
            f"     Will be renamed to h### on PR merge.\n"
            f"     Use the final h### with a v### in Stage 3 (Model Component).\n"
            f"     e.g.  atmosphere_arpege-v6_<h###>_<v###>",
            flush=True,
        )
