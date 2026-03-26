"""
Handler for Horizontal Computational Grid registration (Stage 2a)

Produces N+1 files per submission:
  horizontal_subgrid/{atid}_s{N}.json         — one per NEW slot (s### equivalent)
  horizontal_computational_grid/{atid}.json   — groups all subgrids (h### equivalent)

Before creating a new subgrid, checks the remote src-data _graph.json for an
existing subgrid with identical grid_cells + cell_variable_type. If found,
links to that instead of creating a duplicate.
"""

import os
import json
import time

from cmipld.utils.id_generation import generate_id_from_issue
from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')

SUBGRID_GRAPH = 'emd:horizontal_subgrid/_graph.json'

IGNORE = {'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators',
          'arrangement', 'additional_information', 'description'}

def _fetch_existing_subgrids() -> list[dict]:
    """Fetch all existing horizontal_subgrid entries via cmipld using the emd: prefix."""
    try:
        import cmipld
        graph = cmipld.get(SUBGRID_GRAPH, depth=2)
        if isinstance(graph, list):
            return graph
        for key in graph:
            if 'contents' in key.lower() or 'items' in key.lower():
                val = graph[key]
                return val if isinstance(val, list) else [val]
        return [graph]
    except Exception as e:
        print(f"  ⚠ Could not fetch existing subgrids: {e}", flush=True)
        return []


def _normalise_cells(val) -> list[str]:
    """Return sorted list of short IDs from a cell reference value."""
    if not val:
        return []
    if isinstance(val, str):
        return sorted(v.strip().split('/')[-1] for v in val.split(',') if v.strip())
    if isinstance(val, list):
        items = []
        for v in val:
            if isinstance(v, dict):
                items.append(v.get('@id', '').split('/')[-1])
            else:
                items.append(str(v).split('/')[-1])
        return sorted(items)
    return []


def _normalise_vtypes(val) -> list[str]:
    if not val:
        return []
    if isinstance(val, str):
        return sorted(v.strip() for v in val.split(',') if v.strip())
    if isinstance(val, list):
        items = []
        for v in val:
            if isinstance(v, dict):
                items.append(v.get('@id', '').split('/')[-1])
            else:
                items.append(str(v))
        return sorted(items)
    return []


def _find_matching_subgrid(existing: list[dict], cells: list[str], vtypes: list[str]) -> str | None:
    """Return the short @id of an existing subgrid that matches cells+vtypes, or None."""
    for item in existing:
        ex_cells  = _normalise_cells(
            item.get('horizontal_grid_cells') or item.get('esgvoc:horizontal_grid_cells'))
        ex_vtypes = _normalise_vtypes(
            item.get('cell_variable_type') or item.get('esgvoc:cell_variable_type'))
        if ex_cells == cells and ex_vtypes == vtypes:
            return item.get('@id', '').split('/')[-1]
    return None


def _slot_fields(parsed_issue: dict) -> list[dict]:
    slots = []
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
    author     = issue.get('author') or 'unknown'
    created_at = issue.get('created_at') or ''
    atid       = generate_id_from_issue(author, created_at)['id'] \
                 if created_at else f"{author}_{int(time.time())}"

    arrangement = (parsed_issue.get('arrangement') or '').strip().lower()
    description = parsed_issue.get('additional_information') or parsed_issue.get('description') or ''

    slots        = _slot_fields(parsed_issue)
    existing     = _fetch_existing_subgrids()

    files       = {}
    subgrid_ids = []
    slot_report = []   # for update() summary

    for slot in slots:
        norm_cells  = _normalise_cells(slot['cell'])
        norm_vtypes = _normalise_vtypes(slot['variable_types'])
        match       = _find_matching_subgrid(existing, norm_cells, norm_vtypes)

        if match:
            # Reuse existing subgrid — no new file
            subgrid_ids.append(match)
            slot_report.append({**slot, 'sid': match, 'reused': True})
            print(f"  ✓ Slot {slot['n']}: reusing existing subgrid '{match}'", flush=True)
        else:
            # Create new subgrid
            sid = f"{atid}_s{slot['n']}"
            subgrid_data = {
                "@context":              "_context",
                "@id":                   sid,
                "@type":                 ["wcrp:horizontal_subgrid", "esgvoc:horizontal_subgrid"],
                "validation_key":        sid,
                "horizontal_grid_cells": [slot['cell']],
            }
            if slot['variable_types']:
                subgrid_data['cell_variable_type'] = slot['variable_types']
            files[os.path.join('horizontal_subgrid', f"{sid}.json")] = subgrid_data
            subgrid_ids.append(sid)
            slot_report.append({**slot, 'sid': sid, 'reused': False})
            print(f"  + Slot {slot['n']}: creating new subgrid '{sid}'", flush=True)

    hgrid_data = {
        "@context":            "_context",
        "@id":                 atid,
        "@type":               ["wcrp:horizontal_computational_grid",
                                "esgvoc:horizontal_computational_grid"],
        "validation_key":      atid,
        "horizontal_subgrids": subgrid_ids,
    }
    if arrangement:
        hgrid_data['arrangement'] = arrangement
    if description:
        hgrid_data['description'] = description

    files[os.path.join('horizontal_computational_grid', f"{atid}.json")] = hgrid_data

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    return {
        **files,
        '_author':       issue.get('author'),
        '_contributors': contributors,
        '_make_pull':    True,
        '_atid':         atid,
        '_slot_report':  slot_report,
        '_subgrid_ids':  subgrid_ids,
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    atid        = files_to_write.get('_atid', '')
    slot_report = files_to_write.get('_slot_report', [])
    subgrid_ids = files_to_write.get('_subgrid_ids', [])

    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        print(f"  Generating review report for {file_path} …", flush=True)
        report_kind = (
            'horizontal_subgrid' if 'horizontal_subgrid' in file_path
            else 'horizontal_computational_grid'
        )
        try:
            data['_validation_report'] = ReportBuilder(
                folder_url=f"emd:{report_kind}s", kind=report_kind,
                item=data, link_threshold=80.0,
            ).build()
        except Exception as e:
            print(f"  ⚠ Report generation failed: {e}", flush=True)
            data['_validation_report'] = ''

    if atid:
        print("\n" + "=" * 60, flush=True)
        print("Stage 2a files:", flush=True)
        print("=" * 60, flush=True)
        for s in slot_report:
            vtypes = ', '.join(s['variable_types']) or '(not specified)'
            tag    = '♻ reused' if s['reused'] else '+ new'
            print(f"  [{tag}] horizontal_subgrid/ {s['sid']}.json", flush=True)
            print(f"    ↳ grid cell: {s['cell']}  |  variable types: {vtypes}", flush=True)
        print(f"  [+ new] horizontal_computational_grid/ {atid}.json", flush=True)
        print(f"    ↳ subgrids: {', '.join(subgrid_ids)}", flush=True)
        print("=" * 60, flush=True)
        print(
            f"\n  ✅ Computational Grid ID: '{atid}'\n"
            f"     Use this ID with a v### in Stage 3 (Model Component):\n"
            f"     e.g.  atmosphere_arpege-v6_{atid}_<v###>",
            flush=True,
        )
