# Vertical Computational Grid Template Data
#
# vertical_coordinate: dict mapping ui_label → @id (hyphenated)
# The issue template generator uses dict keys as dropdown options (ui_label shown to user).
# The issue script handler maps the selected ui_label back to the @id for storage.

from cmipld.utils.ldparse import graph_entry, name_entry
import cmipld

def _load_vertical_coordinate_map():
    """Return {ui_label: @id} for all vertical_coordinate entries."""
    data = cmipld.get('constants:vertical_coordinate/_graph.json', depth=2)
    entries = data.get('contents', [])
    result = {}
    for entry in entries:
        if isinstance(entry, dict):
            uid = entry.get('ui_label') or entry.get('@id', '')
            atid = entry.get('@id', entry.get('validation_key', ''))
            if uid and atid:
                result[uid] = atid
    return result

DATA = {
    'vertical_coordinate': _load_vertical_coordinate_map(),
    'issue_kind': ['New', 'Modify']
}
