"""component_config/: a component and the grids it runs on (EMD v1.1 3)."""
from pydantic import model_validator

from base import EMDRecord, Link, warn


class ComponentConfig(EMDRecord):
    """One component configuration. Its id is {realm}_{model_component}_{horizontal grid}_{vertical grid}."""

    model_component: Link("model_component")
    horizontal_computational_grid: Link("horizontal_computational_grid") | None = None
    vertical_computational_grid: Link("vertical_computational_grid") | None = None

    # --------------------------------------------------------------- warnings: the record loads
    @model_validator(mode="after")
    def both_grids_named(self):
        """Both grids are named; a component without one uses no-horizontal or no-vertical."""
        for field in ("horizontal_computational_grid", "vertical_computational_grid"):
            if getattr(self, field) is None:
                warn(f"{self.id}: {field} is empty; use the no-horizontal or no-vertical entry")
        return self

    @model_validator(mode="after")
    def id_names_its_component_and_grids(self):
        """The id ends with _{model_component}_{horizontal grid}_{vertical grid}."""
        parts = [self.model_component, self.horizontal_computational_grid, self.vertical_computational_grid]
        if None not in parts and not self.id.endswith("_" + "_".join(parts)):
            warn(f"{self.id}: the id should end with '_{'_'.join(parts)}'")
        return self


model = ComponentConfig
