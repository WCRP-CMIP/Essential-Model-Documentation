"""
Lightweight name-similarity check for non-grid submissions.

For each proposed file path, scans the same folder on disk and reports any
existing entries whose @id (filename stem) is suspiciously close to the
proposed one. Returns a small markdown table for the PR description, or an
empty string when nothing is similar enough.
"""

from __future__ import annotations

import os
from difflib import SequenceMatcher


# Threshold above which two names are flagged as similar. 0.80 catches typos
# and version drift (e.g. 'nemo-v3-6' vs 'nemo-v3-5') without flooding the
# report with unrelated entries.
_DEFAULT_THRESHOLD = 0.80
_MAX_ROWS = 5


def _similarity(a: str, b: str) -> float:
    """Return a 0..1 similarity ratio between two names (case-insensitive)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_similar_names(
    proposed_id: str,
    folder: str,
    workspace: str = '.',
    threshold: float = _DEFAULT_THRESHOLD,
    max_rows: int = _MAX_ROWS,
) -> list[tuple[str, float]]:
    """Return [(existing_id, similarity), ...] sorted by similarity desc.

    Only entries scoring >= threshold are returned, capped at max_rows.
    Exact matches (proposed_id == existing_id) are skipped — a duplicate ID
    is a different problem handled elsewhere.
    """
    folder_path = os.path.join(workspace, folder)
    if not os.path.isdir(folder_path):
        return []

    proposed_id = (proposed_id or '').strip()
    if not proposed_id:
        return []

    matches: list[tuple[str, float]] = []
    for entry in os.listdir(folder_path):
        if not entry.endswith('.json'):
            continue
        # Skip context / graph files
        if entry.startswith('_') or entry.startswith('.'):
            continue
        existing_id = entry[:-5]  # strip .json
        if existing_id == proposed_id:
            continue
        score = _similarity(proposed_id, existing_id)
        if score >= threshold:
            matches.append((existing_id, score))

    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:max_rows]


def build_similarity_report(
    proposed_id: str,
    folder: str,
    workspace: str = '.',
    threshold: float = _DEFAULT_THRESHOLD,
    max_rows: int = _MAX_ROWS,
) -> str:
    """Build a markdown table of similar existing names, or '' if none."""
    matches = find_similar_names(
        proposed_id, folder, workspace=workspace,
        threshold=threshold, max_rows=max_rows,
    )
    if not matches:
        return ''

    lines = [
        '#### Similar existing names',
        '',
        f'The proposed name `{proposed_id}` is close to {len(matches)} existing '
        f'entr{"y" if len(matches) == 1 else "ies"} in `{folder}/`. '
        'Please confirm this is a new entry and not a duplicate or typo.',
        '',
        '| Existing | Similarity |',
        '|---|---|',
    ]
    for existing_id, score in matches:
        lines.append(f'| `{existing_id}` | {score * 100:.0f}% |')
    return '\n'.join(lines)


def build_details_block(name: str, description: str, references) -> str:
    """Build a "Registration details" markdown block for the PR body.

    Renders name, description (if any), and references (one per line, if any).
    Returns '' when there's nothing to render. Idempotent by construction —
    every handler rerun rebuilds this block from the current issue fields,
    so the PR body always reflects the latest submission.
    """
    lines: list[str] = []

    name_str = (name or '').strip()
    if name_str:
        lines.append(f'**Name:** `{name_str}`')
        lines.append('')

    if description:
        desc = str(description).strip()
        if desc:
            lines.append('### Description')
            lines.append('')
            lines.append(desc)
            lines.append('')

    refs = references or []
    if isinstance(refs, str):
        refs = [r.strip() for r in refs.replace(',', '\n').splitlines() if r.strip()]
    else:
        refs = [str(r).strip() for r in refs if str(r).strip()]

    if refs:
        lines.append('### References')
        lines.append('')
        for r in refs:
            lines.append(f'- {r}')
        lines.append('')

    return '\n'.join(lines).strip()
