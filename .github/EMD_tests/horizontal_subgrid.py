"""horizontal_subgrid/: the variables that sit on one grid cell (EMD v1.1 4.1.2)."""
from pydantic import Field, ValidationInfo, model_validator

from base import EMDRecord, Link, Links, used_by, warn


class HorizontalSubgrid(EMDRecord):
    """One subgrid. Required: cell_variable_type and horizontal_grid_cell (EMD Appendix B 4.1.2)."""

    cell_variable_type: Links("cell_variable_type") = Field(min_length=1)
    horizontal_grid_cell: Link("horizontal_grid_cell")

    # --------------------------------------------------------------- errors: the record is rejected
    @model_validator(mode="before")
    @classmethod
    def accept_plural_spelling(cls, data):
        """EMD 4.1.2 writes horizontal_grid_cells; this folder's _context writes horizontal_grid_cell. Read either."""
        if isinstance(data, dict) and "horizontal_grid_cells" in data:
            data = dict(data)
            data.setdefault("horizontal_grid_cell", data.pop("horizontal_grid_cells"))
        return data

    @model_validator(mode="after")
    def velocity_or_x_y_velocity(self):
        """velocity is not listed with x-velocity or y-velocity (EMD Appendix B 4.1.2)."""
        types = set(self.cell_variable_type)
        if "velocity" in types and types & {"x-velocity", "y-velocity"}:
            raise ValueError("list velocity, or x-velocity and y-velocity, not both")
        return self

    # --------------------------------------------------------------- warnings: the record loads
    @model_validator(mode="after")
    def axes_named_x_and_y(self):
        """EMD 7.4 names the velocity axes x and y, not u and v."""
        for name in {"u-velocity", "v-velocity"} & set(self.cell_variable_type):
            warn(f"{self.id}: use '{name.replace('u-', 'x-').replace('v-', 'y-')}' instead of '{name}'")
        return self

    @model_validator(mode="after")
    def id_lists_the_variable_types(self):
        """The id is {cell}_{type}_{type}...; the types in it are the ones listed in cell_variable_type."""
        in_id = set(self.id.split("_")[1:])
        if in_id and in_id != set(self.cell_variable_type):
            warn(f"{self.id}: the id names {sorted(in_id)}, but cell_variable_type is {sorted(self.cell_variable_type)}")
        return self

    @model_validator(mode="after")
    def belongs_to_a_computational_grid(self, info: ValidationInfo):
        """A subgrid is part of a horizontal computational grid and cannot stand alone (EMD Appendix A)."""
        if used_by(self, info, "horizontal_computational_grid", "horizontal_subgrids") is False:
            raise ValueError("no horizontal_computational_grid lists this subgrid")
        return self


model = HorizontalSubgrid
