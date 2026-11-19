"""model_family/: the institutions and references that related models share (EMD v1.1 2 and 3)."""
from typing import Any

from pydantic import model_validator

from base import EMDRecord, Links, References, TextList, warn


class ModelFamily(EMDRecord):
    """One model family. Nothing is required by the specification; gaps are warnings."""

    primary_institution: str | None = None
    collaborative_institutions: TextList = []
    scientific_domains: Links("scientific_domain") = []
    references: References = []
    family_type: str | None = None
    established: Any = None            # the repository holds both years and "none" here
    representative_member: Any = None

    # --------------------------------------------------------------- warnings: the record loads
    @model_validator(mode="after")
    def institution_given_once(self):
        """A primary institution is given, and it is not also listed as a collaborator."""
        if self.is_sentinel:
            return self
        if not self.primary_institution:
            warn(f"{self.id}: primary_institution is empty")
        elif self.primary_institution in self.collaborative_institutions:
            warn(f"{self.id}: '{self.primary_institution}' is both primary and collaborative institution")
        return self

    @model_validator(mode="after")
    def references_and_description_given(self):
        """A family cites at least one reference and has a description."""
        if self.is_sentinel:
            return self
        if not self.references:
            warn(f"{self.id}: references is empty")
        if not self.description:
            warn(f"{self.id}: description is empty")
        return self


model = ModelFamily
