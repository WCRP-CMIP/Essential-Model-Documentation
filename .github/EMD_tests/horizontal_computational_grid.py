"""horizontal_computational_grid/: an arrangement and the subgrids that build it (EMD v1.1 4.1.1)."""
from pydantic import ValidationInfo, model_validator

from base import EMDRecord, Link, Links, as_list, record, unwrap_id, used_by, warn

# EMD 4.1.1: a grid built from more than one subgrid is "staggered", and every arrangement but
# Arakawa A puts velocity somewhere other than mass (EMD 7.3). So those need two subgrids or more.
MIN_SUBGRIDS = {"arakawa-a": 1, "arakawa-b": 2, "arakawa-c": 2, "arakawa-d": 2, "arakawa-e": 2}

# cell_variable_type values that carry velocity (EMD 7.4: x_velocity, y_velocity, velocity).
VELOCITY = {"velocity", "x-velocity", "y-velocity", "u-velocity", "v-velocity"}


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
            raise ValueError("No arrangement is selected. An arrangement should be selected, e.g. `arakawa-c`.")
        if not self.horizontal_subgrids:
            raise ValueError("No grid cell slots are filled in. At least slot 1 should be filled in, e.g. `g010` with `mass`.")
        return self

    @model_validator(mode="after")
    def enough_subgrids_for_the_arrangement(self):
        """Arakawa B, C, D and E put velocity apart from mass, so they need at least two subgrids (EMD 4.1.1, 7.3)."""
        need = MIN_SUBGRIDS.get(self.arrangement or "", 1)
        given = len(self.horizontal_subgrids)
        if not self.is_sentinel and given < need:
            raise ValueError(f"`{self.arrangement}` has only {given} grid cell slot{'s' if given != 1 else ''}. "
                             f"It should have at least {need}: one for mass and one or more for velocity, "
                             f"e.g. add slot 2 `x-velocity` and slot 3 `y-velocity`.")
        return self

    # --------------------------------------------------------------- warnings: a reviewer should look
    @model_validator(mode="after")
    def unstaggered_grid_has_one_subgrid(self):
        """Arakawa A holds mass and velocity at the same points, so one subgrid is expected (EMD 7.3)."""
        if self.arrangement == "arakawa-a" and len(self.horizontal_subgrids) > 1:
            warn(f"{self.id}: arakawa-a holds mass and velocity at the same points, "
                 f"but {len(self.horizontal_subgrids)} subgrids are given")
        return self

    @model_validator(mode="before")
    @classmethod
    def subgrids_carry_mass_and_velocity(cls, data, info: ValidationInfo):
        """Between them the subgrids carry mass, and velocity on a staggered grid (EMD 4.1.2, 7.3).

        Read before the subgrids are reduced to ids, so one written inline or created by the same
        submission counts as well as one on disk. Skipped when a subgrid cannot be read.
        """
        if not isinstance(data, dict):
            return data
        types = set()
        for subgrid in as_list(data.get("horizontal_subgrids") or []):
            found = subgrid if isinstance(subgrid, dict) else record(info, "horizontal_subgrid", unwrap_id(subgrid))
            if found is None:
                return data
            types |= set(as_list(found.get("cell_variable_type") or []))
        if not types:
            return data
        name, arrangement = data.get("@id"), unwrap_id(data.get("arrangement"))
        if "mass" not in types:
            warn(f"{name}: no subgrid carries mass")
        if arrangement in MIN_SUBGRIDS and arrangement != "arakawa-a" and not types & VELOCITY:
            warn(f"{name}: {arrangement} needs velocity on a subgrid, but none carries it")
        return data

    @model_validator(mode="after")
    def used_by_a_component_config(self, info: ValidationInfo):
        """A grid no component is integrated on is usually a leftover from an earlier submission."""
        if used_by(self, info, "component_config", "horizontal_computational_grid") is False:
            warn(f"{self.id}: no component_config uses this grid")
        return self


model = HorizontalComputationalGrid
