"""
Handler for the 'modify' issue template.

Reads from the parsed issue: folder, filename, and then either a single
`key` + `value` pair or a `changes` JSON object holding several of them.

Behaviour
---------
1. Append `.json` to filename if missing.
2. Verify the folder + file exist on src-data (error if not).
3. Collect the requested updates. Either `key` + `value`, or `changes` as a
   JSON object of field -> new value. Supplying both is an error rather than
   a guess about which one wins.
4. Verify every key exists on the file (error if not). Nested keys with dot
   notation are supported, e.g. `metadata.version`.
5. Try to JSON-parse each value. If it parses (list/number/bool/object/null),
   store it as that type; otherwise store it as a string.
6. Return the modified file dict so new_issue.py opens a PR for review.

Multi-field updates are validated as a unit and applied as a unit: if any one
key is missing or blocked, nothing is written. A single logical correction that
spans several fields therefore lands in one commit, so src-data never compiles
a half-applied state to production.

Error path: posts a comment on the original issue explaining what went wrong
and returns None so new_issue.py skips the PR creation path.
"""

import json
import os
import subprocess

kind = __file__.split('/')[-1].replace('.py', '')  # "modify"

IGNORE = {'issue_category', 'additional_collaborators', 'collaborators',
          'folder', 'filename', 'key', 'value', 'changes', 'justification'}

_PLACEHOLDER = {'', 'not specified', 'none', '_no response_'}

_VALID_FOLDERS = {
    'component_config',
    'horizontal_computational_grid',
    'horizontal_grid_cell',
    'horizontal_subgrid',
    'model',
    'model_component',
    'model_family',
    'vertical_computational_grid',
}

_WORKSPACE = os.environ.get('GITHUB_WORKSPACE', os.getcwd())

# @id and @type are derived fields — direct edits would break linking.
_BLOCKED_KEYS = {'@id', '@type', '@context'}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(s: str) -> str:
    return (s or '').strip()


def _parse_value(raw: str):
    """Try to JSON-parse `raw`; fall back to the original string if it fails."""
    raw = (raw or '').strip()
    if not raw:
        return ''
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return raw


def _walk_to_key(data: dict, dotted_key: str):
    """Walk `data` along a dotted key path.

    Returns (parent_dict, leaf_key, exists). parent_dict is the dict that
    directly contains leaf_key. exists is True only if every intermediate
    path segment AND the leaf already exist on `data`.
    """
    parts = dotted_key.split('.')
    cur = data
    for part in parts[:-1]:
        if not isinstance(cur, dict) or part not in cur:
            return None, parts[-1], False
        cur = cur[part]
    if not isinstance(cur, dict):
        return None, parts[-1], False
    leaf = parts[-1]
    return cur, leaf, (leaf in cur)


def _post_comment(issue_number, body: str):
    """Best-effort gh comment; never raises."""
    try:
        subprocess.run(
            ['gh', 'issue', 'comment', str(issue_number), '--body', body],
            check=True, cwd=_WORKSPACE,
        )
    except Exception as e:
        print(f'\033[91m  ⚠ Could not post comment: {e}\033[0m', flush=True)


def _retitle_issue(issue_number, title: str):
    """Best-effort gh issue title update."""
    try:
        subprocess.run(
            ['gh', 'issue', 'edit', str(issue_number), '--title', title],
            check=True, cwd=_WORKSPACE,
        )
    except Exception as e:
        print(f'\033[91m  ⚠ Could not rename issue: {e}\033[0m', flush=True)


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def run(parsed_issue, issue, dry_run=False):
    folder        = _clean(parsed_issue.get('folder'))
    filename      = _clean(parsed_issue.get('filename'))
    # issue form heading "### Field name" parses to 'field_name'; 'key' is legacy
    key           = _clean(parsed_issue.get('field_name') or parsed_issue.get('key', ''))
    # issue form heading "### New value" parses to 'new_value'; 'value' is legacy
    raw_val       = parsed_issue.get('new_value') or parsed_issue.get('value', '')
    # issue form heading "### Changes" parses to 'changes'
    raw_changes   = _clean(parsed_issue.get('changes'))
    justification = _clean(parsed_issue.get('justification'))

    issue_number = issue.get('number') or issue.get('issue_number')

    # ── Validate inputs ───────────────────────────────────────────────────
    if folder.lower() in _PLACEHOLDER or folder not in _VALID_FOLDERS:
        msg = (
            f'## ❌ Cannot modify: invalid folder\n\n'
            f'The folder `{folder or "(empty)"}` is not one of the recognised '
            f'data folders: `{", ".join(sorted(_VALID_FOLDERS))}`.'
        )
        print(f'\033[91m  ✗ {msg.splitlines()[0]}\033[0m', flush=True)
        if not dry_run and issue_number:
            _post_comment(issue_number, msg)
        return None

    if filename.lower() in _PLACEHOLDER:
        msg = '## ❌ Cannot modify: filename is required.'
        if not dry_run and issue_number:
            _post_comment(issue_number, msg)
        return None

    # ── Collect the requested updates ─────────────────────────────────────
    # Either one key + value, or a `changes` object holding several. Both at
    # once is ambiguous, so it is refused rather than resolved by precedence.
    has_single = key.lower() not in _PLACEHOLDER
    has_multi  = raw_changes.lower() not in _PLACEHOLDER

    if has_single and has_multi:
        msg = (
            '## ❌ Cannot modify: conflicting input\n\n'
            'You filled in both **Field name** / **New value** and **Changes**. '
            'Use one or the other: a single field goes in **Field name** and '
            '**New value**, while several fields go in **Changes** as a JSON '
            'object. Clear whichever you did not mean to use.'
        )
        if not dry_run and issue_number:
            _post_comment(issue_number, msg)
        return None

    if not has_single and not has_multi:
        msg = (
            '## ❌ Cannot modify: nothing to change\n\n'
            'Fill in either **Field name** plus **New value** for a single '
            'field, or **Changes** with a JSON object for several.'
        )
        if not dry_run and issue_number:
            _post_comment(issue_number, msg)
        return None

    if has_multi:
        try:
            parsed_changes = json.loads(raw_changes)
        except (json.JSONDecodeError, ValueError) as e:
            msg = (
                '## ❌ Cannot modify: **Changes** is not valid JSON\n\n'
                f'```\n{e}\n```\n\n'
                'It must be a JSON object mapping field names to new values, '
                'for example:\n\n'
                '```json\n{"n_cells": 220509, "units": "degrees"}\n```'
            )
            if not dry_run and issue_number:
                _post_comment(issue_number, msg)
            return None

        if not isinstance(parsed_changes, dict):
            msg = (
                '## ❌ Cannot modify: **Changes** must be a JSON object\n\n'
                f'It parsed as `{type(parsed_changes).__name__}`. Use an object '
                'mapping field names to new values:\n\n'
                '```json\n{"n_cells": 220509, "units": "degrees"}\n```'
            )
            if not dry_run and issue_number:
                _post_comment(issue_number, msg)
            return None

        if not parsed_changes:
            msg = ('## ❌ Cannot modify: **Changes** is an empty object.\n\n'
                   'List at least one field and its new value.')
            if not dry_run and issue_number:
                _post_comment(issue_number, msg)
            return None

        # Values here are already real JSON types, so they bypass _parse_value.
        updates = [(_clean(k), v, False) for k, v in parsed_changes.items()]
    else:
        # A single value arrives as raw form text and still needs parsing.
        updates = [(key, raw_val, True)]

    # ── Protect structural JSON-LD keys from accidental modification ──
    blocked = [k for k, _, _ in updates if k in _BLOCKED_KEYS]
    if blocked:
        names = ', '.join(f'`{k}`' for k in blocked)
        msg = (
            f'## ❌ Cannot modify {names}\n\n'
            f'{names} {"are" if len(blocked) > 1 else "is"} structural JSON-LD '
            f'{"fields" if len(blocked) > 1 else "field"} derived from the '
            f'filename and cannot be edited directly. '
            f'To change the display name, modify `validation_key` or `ui_label` instead.'
        )
        if not dry_run and issue_number:
            _post_comment(issue_number, msg)
        return None

    empty_keys = [k for k, _, _ in updates if k.lower() in _PLACEHOLDER]
    if empty_keys:
        msg = ('## ❌ Cannot modify: a field name is empty.\n\n'
               'Every entry in **Changes** needs a non-empty field name.')
        if not dry_run and issue_number:
            _post_comment(issue_number, msg)
        return None

    if justification.lower() in _PLACEHOLDER:
        msg = '## ❌ Cannot modify: justification is required.'
        if not dry_run and issue_number:
            _post_comment(issue_number, msg)
        return None

    # ── Resolve file path ────────────────────────────────────────────────
    if not filename.endswith('.json'):
        filename = filename + '.json'
    rel_path = os.path.join(folder, filename)
    full_path = os.path.join(_WORKSPACE, rel_path)

    if not os.path.isdir(os.path.join(_WORKSPACE, folder)):
        msg = (
            f'## ❌ Cannot modify: folder not found\n\n'
            f'The folder `{folder}/` does not exist on `src-data`.'
        )
        if not dry_run and issue_number:
            _post_comment(issue_number, msg)
        return None

    if not os.path.isfile(full_path):
        msg = (
            f'## ❌ Cannot modify: file not found\n\n'
            f'`{rel_path}` does not exist on `src-data`. '
            f'Check the filename (case matters) and try again, '
            f'or use the relevant stage form to create a new entry.'
        )
        if not dry_run and issue_number:
            _post_comment(issue_number, msg)
        return None

    # ── Load file ─────────────────────────────────────────────────────────
    try:
        with open(full_path, encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        msg = (
            f'## ❌ Cannot modify: could not read `{rel_path}`\n\n'
            f'```\n{e}\n```'
        )
        if not dry_run and issue_number:
            _post_comment(issue_number, msg)
        return None

    # ── Resolve every key before touching anything ────────────────────────
    # Resolution is a separate pass from mutation so that a bad key in a
    # multi-field request leaves the file untouched instead of half-updated.
    resolved = []
    missing  = []
    for k, raw, needs_parse in updates:
        parent, leaf, exists = _walk_to_key(data, k)
        if not exists:
            missing.append(k)
            continue
        resolved.append((k, parent, leaf, _parse_value(raw) if needs_parse else raw))

    if missing:
        available = ', '.join(f'`{k}`' for k in sorted(data.keys()))
        names = ', '.join(f'`{k}`' for k in missing)
        msg = (
            f'## ❌ Cannot modify: field not found\n\n'
            f'`{rel_path}` has no {"fields" if len(missing) > 1 else "field"} {names}. '
            f'This form modifies existing fields only; new fields must be '
            f'added via the relevant stage form.\n\n'
            f'**Available fields:** {available}'
        )
        if len(updates) > 1:
            msg += '\n\nNothing was changed. Fix the field name and resubmit.'
        if not dry_run and issue_number:
            _post_comment(issue_number, msg)
        return None

    # ── Apply updates ─────────────────────────────────────────────────────
    applied = []
    for k, parent, leaf, new_value in resolved:
        old_value = parent[leaf]
        parent[leaf] = new_value
        applied.append((k, old_value, new_value))
        print(f'\033[92m  ✓ {rel_path}: {k}\033[0m', flush=True)
        print(f'    old: {json.dumps(old_value, ensure_ascii=False)[:200]}', flush=True)
        print(f'    new: {json.dumps(new_value, ensure_ascii=False)[:200]}', flush=True)

    # ── Rename the issue title to a stamped form ──────────────────────────
    # The stamp_named_types job in tempgrid-rename.yml will recognise the
    # leading "| ... |" and skip re-stamping. Branch deletion on merge is
    # handled there.
    shown = [k for k, _, _ in applied[:3]]
    if len(applied) > 3:
        shown.append(f'+{len(applied) - 3} more')
    new_title = (f'| Modify {folder}/{filename.replace(".json", "")} '
                 f': {", ".join(shown)} |')
    if not dry_run and issue_number:
        _retitle_issue(issue_number, new_title)

    # ── Build collaborators list (matches the other handlers' contract) ──
    collab_str = parsed_issue.get('additional_collaborators',
                                  parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    # `_force_modify` tells new_issue.py that overwriting an existing file is the
    # intent here, not an accident. Without it the writer's "File already exists"
    # guard rejects every submission from this form, since the guard only skips
    # when issue_kind == 'modify' and no handler sets issue_kind.
    return {
        rel_path:         data,
        '_author':        issue.get('author'),
        '_contributors':  contributors,
        '_make_pull':     True,
        '_force_modify':  {rel_path},
        '_justification': justification,
        '_modify_changes': applied,
        # Kept for anything still reading the single-field keys.
        '_modify_key':    applied[0][0] if len(applied) == 1 else '',
        '_modify_old':    applied[0][1] if len(applied) == 1 else '',
        '_modify_new':    applied[0][2] if len(applied) == 1 else '',
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    """Attach a justification block to the PR description via _validation_report."""
    justification = files_to_write.get('_justification', '') or ''
    changes       = files_to_write.get('_modify_changes') or []

    # Fall back to the single-field keys if an older caller set only those.
    if not changes and files_to_write.get('_modify_key'):
        changes = [(files_to_write['_modify_key'],
                    files_to_write.get('_modify_old', ''),
                    files_to_write.get('_modify_new', ''))]

    # Truncate huge values so the report stays readable
    def _short(v):
        s = json.dumps(v, ensure_ascii=False)
        s = s if len(s) <= 400 else s[:400] + '…'
        # Pipes would break out of the markdown table cell
        return s.replace('|', '\\|')

    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        report_lines = ['## Modify request', '']
        if changes:
            plural = 's' if len(changes) > 1 else ''
            report_lines += [
                f'**{len(changes)} field{plural} changed**' if len(changes) > 1
                else f'**Field:** `{changes[0][0]}`',
                '',
                '| Field | Before | After |',
                '|---|---|---|',
            ]
            report_lines += [
                f'| `{k}` | `{_short(old)}` | `{_short(new)}` |'
                for k, old, new in changes
            ]
            report_lines += ['']
            if len(changes) > 1:
                report_lines += [
                    'These were submitted together and applied as a single '
                    'commit, so the entry is never published in a '
                    'part-updated state.',
                    '',
                ]
        if justification:
            report_lines += ['### Justification', '', justification]
        data['_validation_report'] = '\n'.join(report_lines)
