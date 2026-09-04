# Broken & Inconsistent Links — Full Audit

All `model_components` references in model files checked against existing
`component_config/` files and their linked `model_component/` entries.

---

## ❌ BROKEN REFERENCES (model → component_config)

### 1. `icon-xpp-1-1.json` — two broken refs

```
"icon-land-1-1_h130_v122"    ← MISSING realm prefix
"fesim2_h129_no-vertical"    ← MISSING realm prefix + file does not exist
```

**icon-land-1-1**: model_component has `"component": "land-surface"`.
File `land-surface_icon-land-1-1_h130_v122.json` exists.
→ Fix ref to `"land-surface_icon-land-1-1_h130_v122"`

**fesim2**: model_component has `"component": "sea-ice"`.
But NO component_config file `sea-ice_fesim2_h129_no-vertical.json` exists.
→ Needs a new component_config file created, OR the reference corrected.

---

### 2. `icon-xpp-1-1-ed.json` — one broken ref

```
"fesim2_h129_no-vertical"    ← same issue as above
```

(Note: this model correctly has `"land-surface_icon-land-1-1_h130_v122"`,
unlike icon-xpp-1-1 which is missing the prefix.)

---

### 3. `mri-esm3-4.json` — truncated reference

```
"sea-ice_mricom-5-4-sea-ice_h125"    ← MISSING vertical grid suffix
```

Existing file: `sea-ice_mricom-5-4-sea-ice_h125_no-vertical.json`
→ Fix ref to `"sea-ice_mricom-5-4-sea-ice_h125_no-vertical"`

---

### 4. `kace-2-0-g.json` — two missing component_config files

```
"land-surface_jules-v5-3_h113_v117"   ← file does not exist
"sea-ice_cice5_h142_no-vertical"      ← file does not exist
```

Existing jules-v5-3 config: `land-surface_jules-v5-3_h105_v108.json` (different grids)
Existing cice5 configs: `h109` and `h120` only (not h142)
→ Either wrong grid refs, or these component_config files need to be created.

---

## ⚠️ ORPHAN FILES (component_config not referenced by any model)

### 5. `_hd-hydrological-discharge_h134_no-vertical.json`

- No model lists this in its `model_components` array.
- The `model_component/icon-land-1-1.json` description explicitly states:
  *"river discharge uses the HD hydrological discharge model… This is not
  listed separately, because only one 'land-surface' model component can
  be registered."*
- The model_component `hd-hydrological-discharge.json` has `"component": ""`
  (empty realm).

**Options:**
  a) Delete as orphan (it's embedded in icon-land, never referenced standalone)
  b) Keep and assign realm. If kept, realm = `"land-surface"` based on context,
     making @id = `"land-surface_hd-hydrological-discharge_h134_no-vertical"`

---

### 6. `nemo_v3_6_h120_v107.json` (already flagged)

- Uses underscores throughout.
- `model_component: "nemo_v3_6"` — but actual model_component @id is `"nemo-v3-6"`.
- No model references `"nemo_v3_6_h120_v107"`.
  Models reference either `"ocean_nemo-v3-6_h101_v102"` or `"ocean_nemo3-6_h120_v107"`.
- This is likely an orphan duplicate of `ocean_nemo3-6_h120_v107.json` with wrong naming.

---

## ⚠️ EMPTY REALM in model_component

### 7. `model_component/hd-hydrological-discharge.json`

```json
"component": ""
```

If this model_component is kept, it should have `"component": "land-surface"`.

---

## ✅ VERIFIED CORRECT (all links resolve)

| Model | Status |
|-------|--------|
| access-esm1-6 | ✓ all 6 refs valid |
| awi-esm3-4-2-veg-hr | ✓ all 4 refs valid |
| canesm5-1 | ✓ all 6 refs valid |
| canesm6-0-mr | ✓ all 6 refs valid |
| cas-esm2-1-csm | ✓ all 6 refs valid |
| cnrm-esm2-1e | ✓ all 7 refs valid |
| ec-earth3-esm-1-1 | ✓ all 5 refs valid |
| gfdl-esm4p5 | ✓ all 6 refs valid |
| hadcm3b-esm | ✓ all 6 refs valid |
| mcm-ua-1-0 | ✓ all 4 refs valid |
| ukcm2-0-ll | ✓ all 5 refs valid |
| ukcm2a-0-hh | ✓ all 5 refs valid |
| ukesm1-3-ll | ✓ all 8 refs valid |

---

## Summary of actions needed

| # | File to fix | What | Action |
|---|------------|------|--------|
| 1 | model/icon-xpp-1-1.json | ref `icon-land-1-1_h130_v122` | → `land-surface_icon-land-1-1_h130_v122` |
| 2 | model/icon-xpp-1-1.json | ref `fesim2_h129_no-vertical` | → `sea-ice_fesim2_h129_no-vertical` + create that config file |
| 3 | model/icon-xpp-1-1-ed.json | ref `fesim2_h129_no-vertical` | → same fix as #2 |
| 4 | model/mri-esm3-4.json | ref `sea-ice_mricom-5-4-sea-ice_h125` | → `sea-ice_mricom-5-4-sea-ice_h125_no-vertical` |
| 5 | model/kace-2-0-g.json | ref `land-surface_jules-v5-3_h113_v117` | Create config OR fix grid ref |
| 6 | model/kace-2-0-g.json | ref `sea-ice_cice5_h142_no-vertical` | Create config OR fix grid ref |
| 7 | component_config/_hd-hydro... | orphan file | Delete or assign realm + rename |
| 8 | component_config/nemo_v3_6_h120_v107.json | orphan with wrong naming | Delete (duplicate of nemo3-6 variant) |
| 9 | model_component/hd-hydrological-discharge.json | empty realm | Set `"component": "land-surface"` if keeping |
