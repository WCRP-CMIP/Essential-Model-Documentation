"""horizontal_grid_cell/: the horizontal discretisation of one set of grid points (EMD v1.1 4.1.3)."""
import math

from pydantic import Field, ValidationInfo, model_validator

from base import EMDRecord, Latitude, Link, Links, Longitude, Positive, PositiveInt, both_or_neither, used_by, warn

KM_PER_DEGREE = 40075 / 360   # 111.32 km

# Spectral grid types whose truncation N sets the spacing, as degrees for a given N.
SPACING_FROM_TRUNCATION = {
    "linear-spectral-gaussian": lambda n: 180 / n,                                    # TL319 -> 0.56 deg
    "quadratic-spectral-gaussian": lambda n: 120 / n,
    "cubic-octahedral-spectral-reduced-gaussian": lambda n: 10000 / n / KM_PER_DEGREE,  # TCo319 -> 31 km
}
SPECTRAL = {*SPACING_FROM_TRUNCATION, "spectral-gaussian", "spectral-reduced-gaussian", "reduced-gaussian"}
REGULAR = {"regular-latitude-longitude", "regular-gaussian"}

# Fraction of the globe that each region covers, to estimate a cell count.
AREA = {"global": 1, "northern-hemisphere": 0.5, "southern-hemisphere": 0.5, "tropics": 0.4,
        "30s-90s": 0.25, "arctic": 0.05, "antarctica": 0.03, "greenland": 0.004}

PROJECTED = {"albers-conical-equal-area", "azimuthal-equidistant", "geostationary", "lambert-azimuthal-equal-area",
             "lambert-conformal-conic", "lambert-cylindrical-equal-area", "mercator", "orthographic",
             "polar-stereographic", "sinusoidal", "stereographic", "transverse-mercator", "vertical-perspective"}


class HorizontalGridCell(EMDRecord):
    """One horizontal grid cell description. Required: grid_type and region (EMD Appendix B 4.1.3)."""

    grid_type: Link("grid_type")
    region: Links("region") = Field(min_length=1)
    grid_mapping: Link("grid_mapping") | None = None
    temporal_refinement: Link("temporal_refinement") | None = None
    units: Link("units") | None = None
    truncation_method: Link("truncation_method") | None = None
    truncation_number: PositiveInt | None = None
    x_resolution: Positive | None = None
    y_resolution: Positive | None = None
    southernmost_latitude: Latitude | None = None
    westernmost_longitude: Longitude | None = None
    n_cells: PositiveInt | None = None

    @property
    def adaptive(self) -> bool:
        return self.temporal_refinement == "adaptive"

    # --------------------------------------------------------------- errors: the record is rejected
    @model_validator(mode="after")
    def units_given_with_resolution(self):
        """A resolution needs its units (EMD 4.1.3)."""
        if (self.x_resolution or self.y_resolution) and not self.units:
            raise ValueError("set units when x_resolution or y_resolution is set")
        return self

    @model_validator(mode="after")
    def edges_set_together(self):
        """The southern and western edges are given together (EMD Appendix B 4.1.3)."""
        both_or_neither(self, "southernmost_latitude", "westernmost_longitude")
        return self

    @model_validator(mode="after")
    def truncation_set_together(self):
        """The truncation method and number are given together (EMD Appendix B 4.1.3)."""
        both_or_neither(self, "truncation_method", "truncation_number")
        return self

    # --------------------------------------------------------------- warnings: the record loads
    @model_validator(mode="after")
    def spectral_grid_has_truncation(self):
        """A spectral grid type should give its truncation number."""
        if self.grid_type in SPECTRAL and not self.truncation_number:
            warn(f"{self.id}: grid_type '{self.grid_type}' is spectral, but no truncation_number is given")
        return self

    @model_validator(mode="after")
    def resolution_matches_truncation(self):
        """On a spectral grid that names its convention, the resolution is within 35 % of what N gives.

        linear: 180/N degrees. quadratic: 120/N degrees. cubic octahedral: 10000/N km.
        """
        spacing, n = SPACING_FROM_TRUNCATION.get(self.grid_type), self.truncation_number
        if not (spacing and n):
            return self
        expected = spacing(n) * (KM_PER_DEGREE if self.units == "km" else 1)
        for field in ("x_resolution", "y_resolution"):
            value = getattr(self, field)
            if value is not None and abs(value - expected) / expected > 0.35:
                warn(f"{self.id}: {field} is {value} {self.units}, but truncation {n} on '{self.grid_type}' "
                     f"gives about {expected:.3g} {self.units}")
        return self

    @model_validator(mode="after")
    def n_cells_given_unless_adaptive(self):
        """n_cells is given when the cell count is fixed, and left out when it is adaptive (EMD 4.1.3)."""
        if self.n_cells is None and not self.adaptive:
            warn(f"{self.id}: n_cells is not given")
        if self.n_cells is not None and self.adaptive:
            warn(f"{self.id}: n_cells is given on an adaptive grid, where the count changes")
        return self

    @model_validator(mode="after")
    def n_cells_matches_resolution(self):
        """On a regular grid, n_cells is within 10 times of (360/dx) * (180/dy) * area of the regions."""
        if not (self.grid_type in REGULAR and self.n_cells and self.x_resolution and self.y_resolution):
            return self
        scale = KM_PER_DEGREE if self.units == "km" else 1
        area = min(1, sum(AREA.get(r, 1) for r in self.region))
        estimate = (360 * scale / self.x_resolution) * (180 * scale / self.y_resolution) * area
        if abs(math.log10(self.n_cells / estimate)) >= 1:
            warn(f"{self.id}: n_cells is {self.n_cells}, but the resolution and region give about {estimate:,.0f}")
        return self

    @model_validator(mode="after")
    def southern_edge_on_pole_or_half_cell(self):
        """On a regular latitude-longitude grid near the pole, the edge is -90 or -90 + dy/2."""
        south, dy = self.southernmost_latitude, self.y_resolution
        if self.grid_type != "regular-latitude-longitude" or south is None or not dy or south > -80:
            return self
        if min(abs(south + 90), abs(south + 90 - dy / 2)) > max(dy / 4, 0.05):
            warn(f"{self.id}: southernmost_latitude {south} is neither -90 nor -90 + dy/2 = {-90 + dy / 2:g}")
        return self

    @model_validator(mode="after")
    def grid_mapping_suits_grid_type(self):
        """A plane-projection grid uses a projected mapping; a regular latitude-longitude grid does not (EMD 7.6, 7.7)."""
        projected = self.grid_mapping in PROJECTED
        if (self.grid_type == "plane-projection" and not projected) or \
                (self.grid_type == "regular-latitude-longitude" and projected):
            warn(f"{self.id}: grid_mapping '{self.grid_mapping}' does not suit grid_type '{self.grid_type}'")
        return self

    @model_validator(mode="after")
    def used_by_a_subgrid(self, info: ValidationInfo):
        """Grid cells may describe an output grid on their own (EMD 4.1.3), so an unused one is only odd."""
        if used_by(self, info, "horizontal_subgrid", "horizontal_grid_cell") is False:
            warn(f"{self.id}: no horizontal_subgrid uses this grid cell")
        return self


model = HorizontalGridCell
