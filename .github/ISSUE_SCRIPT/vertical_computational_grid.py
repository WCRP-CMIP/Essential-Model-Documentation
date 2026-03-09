"""
Handler for Vertical Computational Grid registration (Stage 2b)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'CMIP-LD'))
from cmipld.utils.id_generation import generate_id_from_issue


VALID_COORDINATES = [
    "atmosphere_hybrid_sigma_pressure_coordinate",
    "atmosphere_hybrid_height_coordinate",
    "atmosphere_ln_pressure_coordinate",
    "atmosphere_sigma_coordinate",
    "atmosphere_sleve_coordinate",
    "ocean_double_sigma_coordinate",
    "ocean_sigma_z_coordinate",
    "ocean_s_coordinate_g1",
    "ocean_s_coordinate_g2",
    "ocean_s_coordinate",
    "ocean_sigma_coordinate",
    "land_ice_sigma_coordinate",
    "sea_water_potential_temperature",
    "sea_water_pressure",
    "air_potential_temperature",
    "air_pressure",
    "geopotential_height",
    "height",
    "depth",
    "z*",
]

NUMERIC_FIELDS = {
    'n_z':                    ('Number of levels',           int),
    'top_layer_thickness':    ('Top layer thickness (m)',    float),
    'bottom_layer_thickness': ('Bottom layer thickness (m)', float),
    'total_thickness':        ('Total thickness (m)',        float),
}

_PLACEHOLDERS = {'not specified', '_no response_', 'none', 'n/a', ''}


def _is_blank(value):
    return not value or str(value).strip().lower() in _PLACEHOLDERS


def _normalise_coordinate(raw):
    """Map raw user input to the canonical CF coordinate name."""
    cleaned = raw.lower().strip().replace(' ', '_').replace('-', '_')
    for canonical in VALID_COORDINATES:
        if cleaned == canonical.lower().replace('-', '_'):
            return canonical
    best, best_len = None, 0
    for canonical in VALID_COORDINATES:
        canon_clean = canonical.lower().replace('-', '_')
        if canon_clean in cleaned or cleaned in canon_clean:
            if len(canon_clean) > best_len:
                best, best_len = canonical, len(canon_clean)
    return best


def _build_auto_description(parsed_issue):
    """
    Construct a terse, structured description from the submitted field values.
    Returns a string like:
      "91-level atmosphere_hybrid_sigma_pressure_coordinate vertical grid
       with top layer 2.0m, bottom layer 25.0m, total extent 80000m."
    """
    parts = []

    n_z = parsed_issue.get('n_z', '').strip()
    coord = parsed_issue.get('vertical_coordinate', '').strip()
    total = parsed_issue.get('total_thickness', '').strip()
    top = parsed_issue.get('top_layer_thickness', '').strip()
    bottom = parsed_issue.get('bottom_layer_thickness', '').strip()

    # Lead: "<n_z>-level <coord> vertical grid"  or fallbacks
    if n_z and not _is_blank(n_z):
        parts.append(f"{n_z}-level")
    if coord and not _is_blank(coord):
        normalised = _normalise_coordinate(coord)
        parts.append(normalised or coord)
    parts.append("vertical grid")

    # Thickness details
    details = []
    if top and not _is_blank(top):
        details.append(f"top layer {top}m")
    if bottom and not _is_blank(bottom):
        details.append(f"bottom layer {bottom}m")
    if total and not _is_blank(total):
        details.append(f"total extent {total}m")

    sentence = " ".join(parts)
    if details:
        sentence += " with " + ", ".join(details) + "."
    else:
        sentence += "."

    return sentence



def run(parsed_issue, issue, dry_run=False):
    """
    Build the initial JSON-LD record for a vertical computational grid.
    Generates @id from author + timestamp, then auto-constructs the description
    from the submitted field values and appends the user's free-text description.
    """
    if parsed_issue.get('validation_key'):
        return None

    author     = issue.get('author')
    created_at = issue.get('created_at')

    if not author or not created_at:
        return None

    id_result = generate_id_from_issue(author, created_at)

    data = {
        "@context": "_context",
        "@id":      id_result['id'],
        "@type":    ["wcrp:vertical_computational_grid"],
        **parsed_issue,
    }

    if id_result.get('epoch'):
        data['_submitted_by']       = id_result['author']
        data['_submitted_at_epoch'] = id_result['epoch']

    # Auto-construct description from field values, then append user text
    auto_desc  = _build_auto_description(parsed_issue)
    user_desc  = parsed_issue.get('description', '').strip()
    data['description'] = auto_desc + (' ' + user_desc if user_desc else '')

    file_path = os.path.join(
        'vertical_computational_grid', f"{id_result['id']}.json"
    )
    return {file_path: data}


def update(data, parsed_issue, issue, dry_run=False):
    """
    Enrich and validate the vertical grid JSON-LD record.
    Normalises coordinate name, validates and casts numeric fields,
    and strips blank placeholders.
    """

    # 1. Ensure @type
    if '@type' not in data:
        data['@type'] = ['wcrp:vertical_computational_grid']

    # 2. Normalise vertical_coordinate
    raw_coord = (
        data.get('vertical_coordinate')
        or parsed_issue.get('vertical_coordinate')
        or ''
    ).strip()

    if raw_coord and not _is_blank(raw_coord):
        normalised = _normalise_coordinate(raw_coord)
        data['vertical_coordinate'] = normalised if normalised else raw_coord
    elif 'vertical_coordinate' in data and _is_blank(data['vertical_coordinate']):
        del data['vertical_coordinate']

    # 3. Validate and cast numeric fields
    for field, (label, cast) in NUMERIC_FIELDS.items():
        raw = (data.get(field) or parsed_issue.get(field) or '')
        if _is_blank(raw):
            data.pop(field, None)
            continue
        try:
            value = cast(str(raw).strip().replace(',', ''))
            if value <= 0:
                print(f"  ⚠ {label} must be > 0 (got {value!r}) — removing", flush=True)
                data.pop(field, None)
            else:
                data[field] = value
        except (ValueError, TypeError):
            print(f"  ⚠ {label} is not a valid number ({raw!r}) — removing", flush=True)
            data.pop(field, None)

    return data
