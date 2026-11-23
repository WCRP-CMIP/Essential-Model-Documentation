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
import sys
import warnings

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


def validate(folder: str, data: dict):
    """Validate one record.

    Returns (errors, warnings) as lists of strings, or None when the folder has
    no model. Handler-internal keys (leading '_') are dropped first — they are
    scaffolding, not part of the record that gets written.
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
            model.model_validate(record)
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
    """Markdown for the PR body. '' when the folder has no model."""
    result = validate(folder, data)
    if result is None:
        return ''
    errors, notes = result

    source = f'`.github/EMD_tests/{folder}.py`'
    lines = [f'#### {heading}', '']

    if errors:
        lines += [
            '> [!CAUTION]',
            f'> **This record does not validate against {source}.** '
            'Resolve before merging:',
            '>',
        ]
        lines += [f'> - {e}' for e in errors]
        if notes:
            lines.append('')

    if notes:
        lines += ['> [!NOTE]', '> Valid, but worth a reviewer check:', '>']
        lines += [f'> - {n}' for n in notes]

    if not errors and not notes:
        lines += ['> [!TIP]', f'> Validates cleanly against {source}.']

    return '\n'.join(lines)


def print_summary(folder: str, data: dict) -> None:
    """Colour summary in the action log, mirroring the handlers' other output."""
    result = validate(folder, data)
    if result is None:
        return
    errors, notes = result
    for e in errors:
        print(f"\033[91m  ✗ {folder}: {e}\033[0m", flush=True)
    for n in notes:
        print(f"\033[93m  ⚠ {folder}: {n}\033[0m", flush=True)
    if not errors and not notes:
        print(f"\033[92m  ✓ {folder}: validates against EMD_tests\033[0m", flush=True)
