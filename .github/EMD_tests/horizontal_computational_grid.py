"""horizontal_computational_grid/: an arrangement and the subgrids that build it (EMD v1.1 4.1.1)."""
from pydantic import model_validator

from base import EMDRecord, Link, Links


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


model = HorizontalComputationalGrid
