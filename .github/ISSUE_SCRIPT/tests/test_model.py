#!/usr/bin/env python3
"""
Tests for model.py issue handler.

Verifies run() produces correct output given simulated parsed issue data,
checking the naming conventions established for this repository:

  - @id and filenames are always lowercase
  - validation_key preserves original casing (dots → dashes, strip invalid chars)
  - ui_label preserves original submission text
  - family references are lowercase
  - component lists normalise free-text to CV slugs
  - All required keys present with correct default types

Run:
  cd .github/ISSUE_SCRIPT
  python3 -m pytest tests/test_model.py -v
"""

import sys
import os
import pytest

# ─── Bootstrap: make handler importable without cmipld ─────
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

try:
    import cmipld  # noqa: F401
except ImportError:
    import types
    cmipld = types.ModuleType('cmipld')
    sys.modules['cmipld'] = cmipld
    utils = types.ModuleType('cmipld.utils')
    sys.modules['cmipld.utils'] = utils
    cmipld.utils = utils
    crs_mod = types.ModuleType('cmipld.utils.crs')
    crs_mod.validate = lambda *a, **kw: []
    crs_mod.build = lambda *a, **kw: 'A(O)O'
    crs_mod.parse = lambda *a, **kw: {'embeddings': [], 'coupling_pairs': []}
    crs_mod.to_name = lambda x: x
    sys.modules['cmipld.utils.crs'] = crs_mod
    utils.crs = crs_mod

import model as model_handler


# ─── Helpers ───────────────────────────────────────────────

def _run(parsed, meta=None):
    meta = meta or {'author': 'test-user', 'number': 1, 'created_at': '2025-01-01T00:00:00Z'}
    result = model_handler.run(parsed, meta)
    if result is None:
        return None, None
    path = next(p for p in result if not p.startswith('_'))
    return path, result[path]


def _base_issue(**overrides):
    issue = {
        'model_name': 'TEST-Model-1.0',
        'model_family': 'test-family',
        'release_year': '2025',
        'reference_dois': 'https://doi.org/10.1234/test',
        'dynamic_components': 'atmosphere, ocean',
        'prescribed_components': 'aerosol',
        'omitted_components': 'land-ice',
        'component_configs': 'atmosphere_test-atm_h100_v100, ocean_test-ocean_h101_v101',
        'coupling_group_1': 'atmosphere, ocean',
        'embedded_components': '',
        'calendar_s_': 'standard',
        'description': 'A test model.',
    }
    issue.update(overrides)
    return issue


# ─── @id and filename ─────────────────────────────────────

class TestIdAndFilename:

    def test_id_is_lowercase(self):
        _, data = _run(_base_issue(model_name='ACCESS-ESM1-6'))
        assert data['@id'] == 'access-esm1-6'

    def test_filename_is_lowercase(self):
        path, _ = _run(_base_issue(model_name='ACCESS-ESM1-6'))
        assert os.path.basename(path) == 'access-esm1-6.json'

    def test_filename_matches_id(self):
        path, data = _run(_base_issue())
        assert path == os.path.join('model', f"{data['@id']}.json")

    def test_dots_become_dashes_in_id(self):
        _, data = _run(_base_issue(model_name='CAS-FGOALS-g3.5'))
        assert '.' not in data['@id']

    def test_id_contains_only_valid_chars(self):
        _, data = _run(_base_issue(model_name='Model (v2.0) [test]'))
        for ch in '()[] ':
            assert ch not in data['@id']


# ─── validation_key and ui_label ───────────────────────────

class TestValidationKeyAndLabel:

    def test_validation_key_preserves_casing(self):
        _, data = _run(_base_issue(model_name='ACCESS-ESM1-6'))
        assert data['validation_key'] == 'ACCESS-ESM1-6'

    def test_validation_key_dots_to_dashes(self):
        _, data = _run(_base_issue(model_name='ICON-XPP-1.1'))
        assert data['validation_key'] == 'ICON-XPP-1-1'

    def test_ui_label_preserves_original(self):
        _, data = _run(_base_issue(model_name='ICON-XPP-1.1'))
        assert data['ui_label'] == 'ICON-XPP-1.1'

    def test_validation_key_never_lowercased(self):
        _, data = _run(_base_issue(model_name='UKESM1-3-LL'))
        assert data['validation_key'] == 'UKESM1-3-LL'


# ─── @type ─────────────────────────────────────────────────

class TestType:

    def test_type_includes_emd(self):
        _, data = _run(_base_issue())
        assert 'emd' in data['@type']

    def test_type_entries(self):
        _, data = _run(_base_issue())
        assert set(data['@type']) == {'emd', 'wcrp:model', 'esgvoc:Model'}


# ─── Linked references ────────────────────────────────────

class TestLinkedReferences:

    def test_family_is_lowercase(self):
        _, data = _run(_base_issue(model_family='ACCESS-ESM'))
        assert data['family'] == 'access-esm'

    def test_family_not_specified_becomes_empty(self):
        _, data = _run(_base_issue(model_family='Not specified'))
        assert data.get('family', '') == ''

    def test_dynamic_components_normalised(self):
        _, data = _run(_base_issue(dynamic_components='atmosphere, Ocean Biogeochemistry, sea ice'))
        assert 'ocean-biogeochemistry' in data['dynamic_components']
        assert 'sea-ice' in data['dynamic_components']
        assert 'atmosphere' in data['dynamic_components']

    def test_references_parsed_as_list(self):
        dois = 'https://doi.org/10.1/a\nhttps://doi.org/10.2/b'
        _, data = _run(_base_issue(reference_dois=dois))
        assert isinstance(data['references'], list)
        assert len(data['references']) == 2


# ─── Required fields and defaults ──────────────────────────

class TestRequiredFields:

    def test_all_scalar_keys_present(self):
        _, data = _run(_base_issue())
        for k in ['validation_key', 'ui_label', 'family', 'description']:
            assert k in data, f"Missing scalar key: {k}"

    def test_all_list_keys_present_and_are_lists(self):
        _, data = _run(_base_issue())
        list_keys = [
            'calendar', 'references',
            'dynamic_components', 'prescribed_components', 'omitted_components',
            'model_components', 'embedded_components', 'coupled_components',
        ]
        for k in list_keys:
            assert k in data, f"Missing list key: {k}"
            assert isinstance(data[k], list), f"{k} should be list, got {type(data[k])}"

    def test_release_year_is_int(self):
        _, data = _run(_base_issue())
        assert isinstance(data['release_year'], int)

    def test_context_is_relative(self):
        _, data = _run(_base_issue())
        assert data['@context'] == '_context'


# ─── Edge cases ────────────────────────────────────────────

class TestEdgeCases:

    def test_empty_name_returns_none(self):
        path, data = _run(_base_issue(model_name=''))
        assert path is None

    def test_whitespace_name_returns_none(self):
        path, data = _run(_base_issue(model_name='   '))
        assert path is None

    def test_coupling_groups_parsed(self):
        _, data = _run(_base_issue(coupling_group_1='atmosphere, ocean'))
        assert isinstance(data['coupled_components'], list)
        assert len(data['coupled_components']) >= 1

    def test_embedded_parsed(self):
        _, data = _run(_base_issue(embedded_components='aerosol -> atmosphere'))
        assert isinstance(data['embedded_components'], list)
        if data['embedded_components']:
            assert len(data['embedded_components'][0]) == 2
