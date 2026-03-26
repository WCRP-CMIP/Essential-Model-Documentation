"""
Handler for Horizontal Computational Grid registration (Stage 2a)

Produces N+1 files per submission:
  horizontal_subgrid/{atid}_s{N}.json         — one per filled slot (s### equivalent)
  horizontal_computational_grid/{atid}.json   — groups all subgrids (h### equivalent)

Each slot links an existing grid cell (g###) with its cell_variable_type(s).
The arrangement (Arakawa type) is set on the computational grid.
"""

import os
import time

from cmipld.utils.id_generation import generate_id_from_issue
from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')

IGNORE = {'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators',
          'arrangement', 'additional_information', 'horizontal_subgrids',
          'description'}

# Parsed label → canonical key for slot fields
# "Grid Cells (select...)" → horizontal_grid_cells_1 etc. (spaces → _, lowercased)
# "Variable Types (variable types...)" → variable_types__variable_types_at_this_cell_location__1
# The actual parsed key depends on how parse_issue_body handles the label.
# CSV field_ids are: horizontal_grid_cells_1, cell_variable_type_1 etc.
# but labels are long strings. We match by checking for the slot number suffix.


def _slot_fields(parsed_issue: dict) -> list[dict]:
    """Extract per-slot {grid_cell, variable_types} from parsed issue."""
    slots = []
    for n in range(1, 5):
        # Try both field_id form and parsed-label form
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

    slots = _slot_fields(parsed_issue)

    # If no inline slots, check for pre-existing s### references
    existing_subgrids = []
    raw_subgrids = parsed_issue.get('horizontal_subgrids') or parsed_issue.get('subgrid_ids') or ''
    if raw_subgrids:
        existing_subgrids = [s.strip() for s in raw_subgrids.split(',') if s.strip()]

    files = {}

    # ── One horizontal_subgrid per inline slot ────────────────────────────────
    subgrid_ids = list(existing_subgrids)  # start with any pre-existing ones
    for slot in slots:
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

    # ── horizontal_computational_grid ─────────────────────────────────────────
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
        '_slots':        slots,
        '_subgrid_ids':  subgrid_ids,
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    atid        = files_to_write.get('_atid', '')
    slots       = files_to_write.get('_slots', [])
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
        print(f"Stage 2a files created:", flush=True)
        print("=" * 60, flush=True)
        for slot in slots:
            sid = f"{atid}_s{slot['n']}"
            vtypes = ', '.join(slot['variable_types']) or '(not specified)'
            print(f"  horizontal_subgrid/            {sid}.json", flush=True)
            print(f"    ↳ grid cell: {slot['cell']}  |  variable types: {vtypes}", flush=True)
        print(f"  horizontal_computational_grid/ {atid}.json", flush=True)
        print(f"    ↳ subgrids: {', '.join(subgrid_ids)}", flush=True)
        print("=" * 60, flush=True)
        print(
            f"\n  ✅ Computational Grid ID: '{atid}'\n"
            f"     Use this ID together with a v### (vertical grid) in\n"
            f"     Stage 3 (Model Component) to form a component config ID:\n"
            f"     e.g.  atmosphere_arpege-v6_<{atid}>_<v###>",
            flush=True,
        )
