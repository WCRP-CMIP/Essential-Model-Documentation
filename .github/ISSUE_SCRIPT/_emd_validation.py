"""
Validate a record built by an issue handler against the pydantic models in
`.github/EMD_tests`, and render the outcome as a markdown block for the PR body.

The same models back the scheduled `emd-validate` workflow, so a submission is
checked against exactly the rules the repository is held to — before the record
is merged rather than after.

Usage from a handler's `update()`:

    from _emd_validation import validation_block

    block = validation_block(folder, data)
    data['_validation_report'] = '\\n\\n'.join(p for p in (block, existing) if p)

A model raising rejects the record (rendered as CAUTION). A model calling
`warn()` lets it through with a note for the reviewer (rendered as NOTE).
Folders with no model in EMD_tests return '' and change nothing.
"""

from __future__ import annotations

import importlib
import os
import re
import sys
import warnings

# Closes every list of errors (on the issue) and of warnings (on the PR).
GUIDANCE = 'If you are unsure, consult the guidance and specification from https://emd.wcrp-cmip.org.'

TESTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'EMD_tests'
)

# The EMD_tests modules import each other by bare name (`from base import ...`),
# so the folder itself has to be importable.
if os.path.isdir(TESTS_DIR) and TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)


def _emd_warning():
    """The warning class EMD_tests uses for 'loads, but look at it'."""
    try:
        from base import EMDWarning
        return EMDWarning
    except Exception:
        return None


def _model_for(folder: str):
    """The pydantic model for a repository folder, or None if there isn't one."""
    if not os.path.isfile(os.path.join(TESTS_DIR, f'{folder}.py')):
        return None
    try:
        return getattr(importlib.import_module(folder), 'model', None)
    except Exception as e:
        print(f"\033[93m  Could not load EMD_tests model '{folder}': {e}\033[0m", flush=True)
        return None


def validate(folder: str, data: dict, pending: dict | None = None, records: dict | None = None):
    """Validate one record.

    Returns (errors, warnings) as lists of strings, or None when the folder has
    no model. Handler-internal keys (leading '_') are dropped first — they are
    scaffolding, not part of the record that gets written. `pending` maps each
    folder to the ids this submission is creating, so siblings may link to each other;
    `records` holds those records by id, so a model can read a sibling's fields.
    """
    model = _model_for(folder)
    if model is None:
        return None

    try:
        from pydantic import ValidationError
    except ImportError:
        return None

    record = {k: v for k, v in data.items() if not k.startswith('_')}
    EMDWarning = _emd_warning()

    errors: list[str] = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        try:
            model.model_validate(record, context={'pending': pending or {}, 'records': records or {}})
        except ValidationError as exc:
            for e in exc.errors():
                where = '.'.join(str(p) for p in e['loc'])
                message = e['msg'].removeprefix('Value error, ')
                errors.append(f'`{where}`: {message}' if where else message)
        except Exception as exc:
            errors.append(f'{type(exc).__name__}: {exc}')

    notes = [
        str(w.message)
        for w in caught
        if EMDWarning is not None and issubclass(w.category, EMDWarning)
    ]
    return errors, notes


def validation_block(folder: str, data: dict, heading: str = 'Record validation') -> str:
    """The reviewer's view for the PR body: warnings only. '' when the folder has no model.

    Errors never get this far — `attach_errors()` in `run()` has already stopped the issue —
    so anything this model still has to say is advice for the reviewer.
    """
    result = validate(folder, data)
    if result is None:
        return ''
    _, notes = result

    source = f'`.github/EMD_tests/{folder}.py`'
    lines = [f'#### {heading}', '']
    if notes:
        lines += ['> [!NOTE]', '> Valid, but worth a reviewer check:', '>']
        lines += [f'> - {n}' for n in notes]
        lines += ['>', f'> {GUIDANCE}']
    else:
        lines += ['> [!TIP]', f'> Validates cleanly against {source}.']
    return '\n'.join(lines)


def print_summary(folder: str, data: dict) -> None:
    """Colour summary in the action log, mirroring the handlers' other output."""
    result = validate(folder, data)
    if result is None:
        return
    _, notes = result
    for n in notes:
        print(f"\033[93m  ⚠ {folder}: {n}\033[0m", flush=True)
    if not notes:
        print(f"\033[92m  ✓ {folder}: validates against EMD_tests\033[0m", flush=True)


def submission_records(files_to_write: dict) -> dict:
    """{id: record} for every record this submission creates, including inline subgrids."""
    found: dict = {}
    for file_path, data in files_to_write.items():
        if str(file_path).startswith('_') or not isinstance(data, dict):
            continue
        found[data.get('@id')] = data
        for sub in data.get('horizontal_subgrids') or []:
            if isinstance(sub, dict) and sub.get('@id'):
                found[sub['@id']] = sub
    return found


def submission_ids(files_to_write: dict) -> dict:
    """{folder: ids} for every record this submission creates, including subgrids a
    computational grid carries inline."""
    found: dict = {}
    for file_path, data in files_to_write.items():
        if str(file_path).startswith('_') or not isinstance(data, dict):
            continue
        found.setdefault(os.path.dirname(file_path), set()).add(data.get('@id'))
        for sub in data.get('horizontal_subgrids') or []:
            if isinstance(sub, dict) and sub.get('@id'):
                found.setdefault('horizontal_subgrid', set()).add(sub['@id'])
    return found


def attach_errors(files_to_write: dict) -> dict:
    """Put each record's validation errors on `_errors`, so a bad submission never reaches a PR.

    `new_issue.py` STEP 1b folds `_errors` into the run's validation errors, which are posted
    as a comment on the issue and stop the run before any branch or PR is made — the same
    path the schema checks use. Call this from a handler's `run()`, on what it is about to
    return, because STEP 1b reads the files before `update()` is reached.

    Warnings are deliberately left out: they belong on the PR, and `validation_block()` in
    `update()` puts them there.
    """
    siblings = submission_ids(files_to_write)
    records = submission_records(files_to_write)
    last = None
    for file_path, data in files_to_write.items():
        if str(file_path).startswith('_') or not isinstance(data, dict):
            continue
        folder = os.path.dirname(file_path)
        # The record itself: EMD_tests uses the record's own field names. (_pydantic_data renames
        # fields for the old esgvoc schema, e.g. units -> horizontal_units, and must not be used.)
        result = validate(folder, data, siblings, records)
        if result is None:
            continue
        errors, _ = result
        if errors:
            existing = list(data.get('_errors') or [])
            data['_errors'] = existing + [f'{e}  _(`.github/EMD_tests/{folder}.py`)_' for e in errors]
            print(f"\033[91m  ✗ {file_path}: {len(errors)} schema error(s)\033[0m", flush=True)
            last = data

    # One closing line after all of them. new_issue.py writes each error as a "- " bullet, so a
    # blank line before it ends the list and the line reads as its own paragraph.
    if last is not None:
        last['_errors'][-1] += f'\n\n{GUIDANCE}'
    return files_to_write


def collapse(report: str) -> str:
    """Fold a review report into collapsed items, one per section, keeping its introduction open.

    Sections are cut at the report's top heading level (### for the ReportBuilder report,
    #### for the name-similarity report), never inside a code block. A report with no
    headings is returned unchanged. The record validation block is not passed through
    here: it stays open at the top of the PR so the reviewer reads it first.
    """
    if not report:
        return report

    def heading_level(line: str) -> int:
        match = re.match(r'(#{2,6}) \S', line)
        return len(match.group(1)) if match else 0

    lines = report.splitlines()
    in_code, levels = False, []
    for line in lines:
        if line.lstrip().startswith('```'):
            in_code = not in_code
        elif not in_code and heading_level(line):
            levels.append(heading_level(line))
    if not levels:
        return report
    top = min(levels)

    intro, sections, in_code = [], [], False
    for line in lines:
        if line.lstrip().startswith('```'):
            in_code = not in_code
        if not in_code and heading_level(line) == top:
            sections.append([line.lstrip('#').strip()])
            continue
        (sections[-1] if sections else intro).append(line)

    out = ['\n'.join(intro).rstrip()] if any(l.strip() for l in intro) else []
    for title, *body in sections:
        opening = '<details open>' if any(s in title for s in OPEN_SECTIONS) else '<details>'
        out.append('\n'.join([
            opening, f'<summary><strong>{title}</strong></summary>', '',
            '\n'.join(body).strip(), '', '</details>',
        ]))
    folded = '\n\n'.join(out)

    # Inside a section the reviewer has chosen to open, these should already be showing.
    for title in OPEN_INSIDE:
        folded = folded.replace(f'<details><summary>{title}', f'<details open><summary>{title}')
    return folded


# Report sections shown open; the rest start collapsed.
OPEN_SECTIONS = (
    'Similarity to existing entries',
)

# Blocks within a report section that are shown open once that section is expanded.
OPEN_INSIDE = (
    'Fields included in comparison',
)
