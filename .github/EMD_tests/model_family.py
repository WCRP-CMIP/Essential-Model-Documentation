"""model_family/: the institutions and references that related models share (EMD v1.1 2 and 3)."""
import json
import ssl
import urllib.request
from functools import lru_cache
from typing import Any

from pydantic import ValidationInfo, field_validator, model_validator

from base import EMDRecord, Links, References, TextList, warn

# The model family form offers institutions from these two esgvoc lists
# (see .github/GEN_ISSUE_TEMPLATE/model_family.py), so the same lists decide what is recognised.
ESGVOC = "https://esgvoc.ipsl.fr/api/v1/universe/data_descriptors/"


def _tls() -> ssl.SSLContext:
    """certifi's certificates where installed: some Python builds (macOS) ship without a CA bundle."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


@lru_cache(maxsize=None)
def known_institutions() -> frozenset[str]:
    """Every esgvoc organisation and institution id. Empty when esgvoc cannot be reached."""
    found = set()
    for kind in ("organisation", "institution"):
        try:
            with urllib.request.urlopen(f"{ESGVOC}{kind}/terms", timeout=30, context=_tls()) as reply:
                found |= {term["id"] for term in json.load(reply) if term.get("id")}
        except Exception:
            return frozenset()        # unreachable: skip the check rather than reject every family
    return frozenset(found)


class ModelFamily(EMDRecord):
    """One model family. Required: primary_institution, except on no-family."""

    primary_institution: str | None = None
    collaborative_institutions: TextList = []
    scientific_domains: Links("scientific_domain") = []
    references: References = []
    family_type: str | None = None
    established: Any = None            # the repository holds both years and "none" here
    representative_member: Any = None

    # --------------------------------------------------------------- errors: the record is rejected
    @model_validator(mode="after")
    def primary_institution_given(self):
        """A family names its primary institution. no-family stands for "no family" and has none."""
        if not self.is_sentinel and not self.primary_institution:
            raise ValueError("No primary institution is given. A primary institution should be selected, e.g. `ipsl`.")
        return self

    @field_validator("primary_institution", "collaborative_institutions")
    @classmethod
    def institutions_are_recognised(cls, value, info: ValidationInfo):
        """Every institution is an esgvoc organisation or institution, as offered on the form.

        A field check, so it is reported alongside the other field errors rather than after them.
        """
        names = [v for v in (value if isinstance(value, list) else [value]) if v]
        if not names:
            return value
        known = known_institutions()
        if not known:
            warn(f"{info.data.get('id', 'model_family')}: institutions were not checked, "
                 f"because esgvoc could not be reached")
            return value
        unknown = [n for n in names if n not in known]
        if unknown:
            guess = unknown[0].strip().lower().replace(" ", "-").replace("_", "-")
            example = guess if guess in known else "ipsl"
            raise ValueError(f"`{', '.join(unknown)}` {'are' if len(unknown) > 1 else 'is'} not a recognised "
                             f"institution. It should be one of the institutions listed on the form, e.g. `{example}`.")
        return value

    # --------------------------------------------------------------- warnings: the record loads
    @model_validator(mode="after")
    def primary_not_also_collaborative(self):
        """The primary institution is not also listed as a collaborator."""
        if self.primary_institution and self.primary_institution in self.collaborative_institutions:
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
