"""
Scientific domain colour palette.

Maps each EMD scientific domain to a colour from a curated palette.
Used by generator scripts and referenced by scientific_domains.css.

Palette source: #264653, #287271, #2a9d8f, #8ab17d, #e9c46a, #f4a261, #e76f51
Land-ice uses a derived icy blue (#7cadbe) to complete the eight domains.
"""

REALM_COLORS = {
    "ocean":                 "#264653",  # Charcoal Blue
    "ocean-biogeochemistry": "#287271",  # Pine Blue
    "sea-ice":               "#2a9d8f",  # Verdigris
    "land-surface":          "#8ab17d",  # Muted Olive
    "land-ice":              "#7cadbe",  # Ice Blue (derived)
    "aerosol":               "#e9c46a",  # Tuscan Sun
    "atmospheric-chemistry": "#f4a261",  # Sandy Brown
    "atmosphere":            "#e76f51",  # Burnt Peach
}

# Fallback for unknown domains
DEFAULT_COLOR = "#94a3b8"


def get_realm_color(realm_id: str) -> str:
    """Get the hex colour for a scientific domain."""
    if not realm_id:
        return DEFAULT_COLOR
    key = realm_id.lower().replace("_", "-")
    return REALM_COLORS.get(key, DEFAULT_COLOR)
