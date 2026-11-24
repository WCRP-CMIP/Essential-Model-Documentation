"""vertical_computational_grid/: the levels of one component (EMD v1.1 4.2.1)."""
from pydantic import Field, ValidationInfo, model_validator

from base import EMDRecord, Link, Positive, PositiveInt, not_both, used_by, warn


class VerticalComputationalGrid(EMDRecord):
    """One vertical grid. Thicknesses are in metres. A value left out must be explained in description."""

    vertical_coordinate: Link("vertical_coordinate") | None = None
    n_z: PositiveInt | None = None
    n_z_range: list[PositiveInt] | None = Field(None, min_length=2, max_length=2)   # [minimum, maximum]
    top_layer_thickness: Positive | None = None
    bottom_layer_thickness: Positive | None = None
    total_thickness: Positive | None = None

    # --------------------------------------------------------------- errors: the record is rejected
    @model_validator(mode="after")
    def n_z_or_n_z_range(self):
        """A fixed level count or a range, not both (EMD Appendix B 4.2)."""
        not_both(self, "n_z", "n_z_range")
        return self

    @model_validator(mode="after")
    def range_runs_low_to_high(self):
        """n_z_range is [minimum, maximum]."""
        if self.n_z_range and self.n_z_range[0] > self.n_z_range[1]:
            raise ValueError(f"n_z_range {self.n_z_range} must be [minimum, maximum]")
        return self

    @model_validator(mode="after")
    def description_explains_what_is_left_out(self):
        """When a property is left out, description must be set to explain it (EMD Appendix B 4.2)."""
        if self.is_sentinel or self.description:
            return self
        left_out = [f for f in ("vertical_coordinate", "top_layer_thickness", "bottom_layer_thickness",
                                "total_thickness") if getattr(self, f) is None]
        if self.n_z is None and self.n_z_range is None:
            left_out.append("n_z")
        if left_out:
            raise ValueError(f"description is required to explain what is left out: {left_out}")
        return self

    @model_validator(mode="after")
    def top_layer_within_column(self):
        """The top layer cannot be thicker than the whole column."""
        top, total = self.top_layer_thickness, self.total_thickness
        if top and total and top > total:
            raise ValueError(f"top_layer_thickness {top} m is more than total_thickness {total} m")
        return self

    # --------------------------------------------------------------- warnings: the record loads
    @model_validator(mode="after")
    def bottom_layer_is_not_whole_column(self):
        """A bottom layer as thick as the whole column is usually a copy-paste error."""
        if self.bottom_layer_thickness is not None and self.bottom_layer_thickness == self.total_thickness:
            warn(f"{self.id}: bottom_layer_thickness equals total_thickness ({self.total_thickness:g} m)")
        return self

    @model_validator(mode="after")
    def top_and_bottom_fit_in_column(self):
        """The top and bottom layers together fit inside the column."""
        top, bottom, total = self.top_layer_thickness, self.bottom_layer_thickness, self.total_thickness
        if None not in (top, bottom, total) and top + bottom > total:
            warn(f"{self.id}: top {top:g} m + bottom {bottom:g} m is more than total_thickness {total:g} m")
        return self

    @model_validator(mode="after")
    def used_by_a_component_config(self, info: ValidationInfo):
        """A grid no component is integrated on is usually a leftover from an earlier submission."""
        if used_by(self, info, "component_config", "vertical_computational_grid") is False:
            warn(f"{self.id}: no component_config uses this grid")
        return self


model = VerticalComputationalGrid
