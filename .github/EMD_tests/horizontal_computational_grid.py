"""horizontal_computational_grid/: an arrangement and the subgrids that build it (EMD v1.1 4.1.1)."""
from pydantic import ValidationInfo, model_validator

from base import EMDRecord, Link, Links, used_by, warn


class HorizontalComputationalGrid(EMDRecord):
    """One horizontal computational grid. Required: arrangement and horizontal_subgrids, except on no-horizontal."""

    arrangement: Link("arrangement") | None = None
    horizontal_subgrids: Links("horizontal_subgrid") = []

    # --------------------------------------------------------------- errors: the record is rejected
    @model_validator(mode="after")
    def arrangement_and_subgrids_given(self):
        """Both are required (EMD Appendix B 4.1.1). no-horizontal stands for "no grid" and has neither."""
        if self.is_sentinel:
            return self
        if self.arrangement is None:
            raise ValueError("arrangement is required")
        if not self.horizontal_subgrids:
            raise ValueError("horizontal_subgrids is required")
        return self

    @model_validator(mode="after")
    def used_by_a_component_config(self, info: ValidationInfo):
        """A grid no component is integrated on is usually a leftover from an earlier submission."""
        if used_by(self, info, "component_config", "horizontal_computational_grid") is False:
            warn(f"{self.id}: no component_config uses this grid")
        return self


model = HorizontalComputationalGrid
