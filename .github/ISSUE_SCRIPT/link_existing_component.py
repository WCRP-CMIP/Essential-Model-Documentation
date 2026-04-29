"""
Handler for linking an existing model component to computational grids (Stage 3b).

Unlike model_component.py (which registers a new component AND a config), this
handler assumes the component already exists on src-data and only creates the
component_config record.

Behaviour
---------
1. Derive the config ID: <component>_<h###>_<v###>
   (either grid may be "not specified", in which case it is omitted from the ID)
2. Check whether component_config/<config_id>.json already exists on src-data.
   - EXISTS   → post a comment explaining this, close the issue, return None
                 so new_issue.py skips the PR/push path entirely.
   - NOT FOUND → build the component_config JSON, push it directly to src-data,
                 post a success comment, close the issue.

The file is pushed directly to src-data (no PR) because there is nothing to
review — the component and both grids are already approved entries.
"""

import json
import os
import subprocess

from cmipld.utils.similarity import ReportBuilder

kind = __file__.split('/')[-1].replace('.py', '')   # "link_existing_component"

IGNORE = {'issue_kind', 'issue_category', 'additional_collaborators', 'collaborators'}

_PLACEHOLDER = {'not specified', 'none', '_no response_', ''}

_REPO        = os.environ.get('GITHUB_REPOSITORY', 'WCRP-CMIP/Essential-Model-Documentation')
_BRANCH      = 'src-data'
_BASE_URL    = f'https://github.com/{_REPO}/blob/{_BRANCH}'
_WORKSPACE   = os.environ.get('GITHUB_WORKSPACE', os.getcwd())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(s: str) -> str:
    return (s or '').strip().lower()


def _build_config_id(component: str, h_grid: str, v_grid: str) -> str:
    """Compose the config ID from its three parts, skipping 'not specified'."""
    parts = [component]
    if h_grid not in _PLACEHOLDER:
        parts.append(h_grid)
    if v_grid not in _PLACEHOLDER:
        parts.append(v_grid)
    return '_'.join(parts)


def _file_exists_on_src_data(rel_path: str) -> bool:
    """Return True if rel_path exists on the src-data branch in the workspace."""
    # First try the working tree (if src-data is checked out)
    full = os.path.join(_WORKSPACE, rel_path)
    if os.path.exists(full):
        return True
    # Fall back to asking git
    try:
        result = subprocess.run(
            ['git', 'cat-file', '-e', f'origin/{_BRANCH}:{rel_path}'],
            capture_output=True,
            cwd=_WORKSPACE,
        )
        return result.returncode == 0
    except Exception:
        return False


def _push_file_to_src_data(rel_path: str, data: dict) -> bool:
    """
    Write data as JSON to rel_path on the src-data branch and push.
    Returns True on success.
    """
    full = os.path.join(_WORKSPACE, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)

    with open(full, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        f.write('\n')

    try:
        subprocess.run(['git', 'add', rel_path], check=True, cwd=_WORKSPACE)
        subprocess.run(
            ['git', 'commit', '-m', f'Add component_config: {os.path.basename(rel_path)}'],
            check=True, cwd=_WORKSPACE,
        )
        subprocess.run(
            ['git', 'push', 'origin', _BRANCH],
            check=True, cwd=_WORKSPACE,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f'\033[91m  ✗ git push failed: {e}\033[0m', flush=True)
        return False


def _post_comment(issue_number: str | int, body: str):
    try:
        subprocess.run(
            ['gh', 'issue', 'comment', str(issue_number), '--body', body],
            check=True, cwd=_WORKSPACE,
        )
    except Exception as e:
        print(f'\033[91m  ⚠ Could not post comment: {e}\033[0m', flush=True)


def _close_issue(issue_number: str | int):
    try:
        subprocess.run(
            ['gh', 'issue', 'close', str(issue_number)],
            check=True, cwd=_WORKSPACE,
        )
    except Exception as e:
        print(f'\033[91m  ⚠ Could not close issue: {e}\033[0m', flush=True)


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def run(parsed_issue, issue, dry_run=False):
    component = _clean(parsed_issue.get('model_component') or '')
    h_grid    = _clean(parsed_issue.get('horizontal_computational_grid') or '')
    v_grid    = _clean(parsed_issue.get('vertical_computational_grid') or '')

    if not component or component in _PLACEHOLDER:
        print('\033[91m  ✗ No model_component selected — cannot proceed.\033[0m', flush=True)
        return None

    config_id   = _build_config_id(component, h_grid, v_grid)
    config_path = os.path.join('component_config', f'{config_id}.json')
    issue_num   = issue.get('number') or issue.get('issue_number')

    print(f'  Config ID : {config_id}', flush=True)
    print(f'  File path : {config_path}', flush=True)

    # ── Check for duplicate ────────────────────────────────────────────────
    if _file_exists_on_src_data(config_path):
        existing_url = f'{_BASE_URL}/component_config/{config_id}.json'
        msg = (
            f'## ⚠️ Component configuration already exists\n\n'
            f'A `component_config` record with ID **`{config_id}`** already exists on '
            f'`{_BRANCH}`:\n\n'
            f'> [{config_path}]({existing_url})\n\n'
            f'No new file has been created. '
            f'You can use **`{config_id}`** directly in Stage 4 (Model).\n\n'
            f'_This issue has been closed automatically._'
        )
        print(f'\033[93m  ⚠ Duplicate detected — closing issue.\033[0m', flush=True)
        if not dry_run and issue_num:
            _post_comment(issue_num, msg)
            _close_issue(issue_num)
        return None   # signal to new_issue.py: nothing further to do

    # ── Build the config record ────────────────────────────────────────────
    config_data = {
        '@context':                      '_context',
        '@id':                           config_id,
        '@type':                         ['emd', 'wcrp:component_config', 'esgvoc:ComponentConfig'],
        'validation_key':                config_id,
        'ui_label':                      config_id,
        'model_component':               component,
        'horizontal_computational_grid': h_grid if h_grid not in _PLACEHOLDER else '',
        'vertical_computational_grid':   v_grid if v_grid not in _PLACEHOLDER else '',
        'description':                   '',
    }

    collab_str   = parsed_issue.get('additional_collaborators',
                                    parsed_issue.get('collaborators', ''))
    contributors = [c.strip() for c in collab_str.split(',') if c.strip()] \
                   if collab_str else []

    # ── Push directly to src-data ──────────────────────────────────────────
    if not dry_run:
        ok = _push_file_to_src_data(config_path, config_data)
        if ok:
            file_url = f'{_BASE_URL}/component_config/{config_id}.json'
            msg = (
                f'## ✅ Component configuration created\n\n'
                f'A new `component_config` record has been pushed to `{_BRANCH}`:\n\n'
                f'| Field | Value |\n'
                f'|---|---|\n'
                f'| Config ID | `{config_id}` |\n'
                f'| Model component | `{component}` |\n'
                f'| Horizontal grid | `{h_grid or "—"}` |\n'
                f'| Vertical grid | `{v_grid or "—"}` |\n'
                f'| File | [{config_path}]({file_url}) |\n\n'
                f'Use **`{config_id}`** in Stage 4 (Model) under `component_configs`.\n\n'
                f'_This issue has been closed automatically._'
            )
            _post_comment(issue_num, msg)
            _close_issue(issue_num)
            print(f'\033[92m  ✅ Pushed {config_path} to {_BRANCH}\033[0m', flush=True)
        else:
            print(f'\033[91m  ✗ Push failed — issue left open.\033[0m', flush=True)
        return None   # no PR needed; we handled everything directly
    else:
        # dry_run: return the data so callers can inspect it
        return {
            config_path:     config_data,
            '_author':       issue.get('author'),
            '_contributors': contributors,
            '_make_pull':    False,
            '_config_id':    config_id,
        }


def update(files_to_write, parsed_issue, issue, dry_run=False):
    """
    update() is called after the PR/push path. For this handler run() either
    returns None (handled inline) or, in dry_run, returns the dict. Either
    way there is nothing extra to do here.
    """
    config_id = files_to_write.get('_config_id', '') if files_to_write else ''
    if config_id:
        print(f'\033[92m  Config ID: {config_id}\033[0m', flush=True)
