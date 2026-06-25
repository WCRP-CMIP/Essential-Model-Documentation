"""
Handler for the 'modify' issue template.

Reads four fields from the parsed issue: folder, filename, key, value.

Behaviour
---------
1. Append `.json` to filename if missing.
2. Verify the folder + file exist on src-data (error if not).
3. Verify the key exists on the file (error if not). Nested keys with dot
   notation are supported, e.g. `metadata.version`.
4. Try to JSON-parse the value. If it parses (list/number/bool/object/null),
   store it as that type; otherwise store it as a string.
5. Return the modified file dict so new_issue.py opens a PR for review.

Error path: posts a comment on the original issue explaining what went wrong
and returns None so new_issue.py skips the PR creation path.
"""

import json
import os
import subprocess

kind = __file__.split('/')[-1].replace('.py', '')  # "modify"

IGNORE = {'issue_category', 'additional_collaborators', 'collaborators',
          'folder', 'filename', 'key', 'value', 'justification'}

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
    key           = _clean(parsed_issue.get('key'))
    raw_val       = parsed_issue.get('value', '')
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

    if key.lower() in _PLACEHOLDER:
        msg = '## ❌ Cannot modify: field name (key) is required.'
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

    # ── Locate key ────────────────────────────────────────────────────────
    parent, leaf, exists = _walk_to_key(data, key)
    if not exists:
        msg = (
            f'## ❌ Cannot modify: field not found\n\n'
            f'`{rel_path}` has no field `{key}`. '
            f'This form modifies existing fields only; new fields must be '
            f'added via the relevant stage form.'
        )
        if not dry_run and issue_number:
            _post_comment(issue_number, msg)
        return None

    # ── Apply update ──────────────────────────────────────────────────────
    new_value = _parse_value(raw_val)
    old_value = parent[leaf]
    parent[leaf] = new_value

    print(f'\033[92m  ✓ {rel_path}: {key}\033[0m', flush=True)
    print(f'    old: {json.dumps(old_value, ensure_ascii=False)[:200]}', flush=True)
    print(f'    new: {json.dumps(new_value, ensure_ascii=False)[:200]}', flush=True)

    # ── Rename the issue title to a stamped form ──────────────────────────
    # The stamp_named_types job in tempgrid-rename.yml will recognise the
    # leading "| ... |" and skip re-stamping. Branch deletion on merge is
    # handled there.
    new_title = f'| Modify {folder}/{filename.replace(".json", "")} : {key} |'
    if not dry_run and issue_number:
        _retitle_issue(issue_number, new_title)

    # ── Build collaborators list (matches the other handlers' contract) ──
    collab_str = parsed_issue.get('additional_collaborators',
                                  parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    return {
        rel_path:         data,
        '_author':        issue.get('author'),
        '_contributors':  contributors,
        '_make_pull':     True,
        '_justification': justification,
        '_modify_key':    key,
        '_modify_old':    old_value,
        '_modify_new':    new_value,
    }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    """Attach a justification block to the PR description via _validation_report."""
    justification = files_to_write.get('_justification', '') or ''
    mod_key       = files_to_write.get('_modify_key', '') or ''
    mod_old       = files_to_write.get('_modify_old', '')
    mod_new       = files_to_write.get('_modify_new', '')

    # Truncate huge values so the report stays readable
    def _short(v):
        s = json.dumps(v, ensure_ascii=False)
        return s if len(s) <= 400 else s[:400] + '…'

    for file_path, data in files_to_write.items():
        if file_path.startswith('_'):
            continue
        report_lines = ['## Modify request', '']
        if mod_key:
            report_lines += [
                f'**Field:** `{mod_key}`',
                '',
                '| Before | After |',
                '|---|---|',
                f'| `{_short(mod_old)}` | `{_short(mod_new)}` |',
                '',
            ]
        if justification:
            report_lines += ['### Justification', '', justification]
        data['_validation_report'] = '\n'.join(report_lines)
