"""model_component/: one part of a model, such as an ocean or a land surface (EMD v1.1 3)."""
import re

from pydantic import Field, ValidationInfo, model_validator

from base import EMDRecord, Link, References, used_by, warn

NO_PUBLIC_CODE = {"private", "none"}                          # accepted instead of a URL
GENERIC = re.compile(r"(used (in|for)\b|the \w+ (model|component)$|see\b|n/?a$|tbd$).*", re.I)
PINNED = re.compile(r".*/(commit|tree|releases/tag)/.*")      # a URL that names a fixed version


class ModelComponent(EMDRecord):
    """One model component. Required: component, description, references, and a name or ui_label."""

    component: Link("scientific_domain")
    description: str
    references: References = Field(min_length=1)
    family: Link("model_family") | None = None
    name: str | None = None
    code_base: str | None = None

    # --------------------------------------------------------------- errors: the record is rejected
    @model_validator(mode="after")
    def has_a_name(self):
        """name is required (EMD Appendix B 3). The repository usually holds it in ui_label, so either counts."""
        if not (self.name or self.ui_label):
            raise ValueError("set name or ui_label")
        return self

    # --------------------------------------------------------------- warnings: the record loads
    @model_validator(mode="after")
    def family_given(self):
        """family is given; a component with no family uses no-family."""
        if self.family is None:
            warn(f"{self.id}: family is empty; use 'no-family' if the component has none")
        return self

    @model_validator(mode="after")
    def name_has_hyphenated_version(self):
        """The name holds a version written with hyphens, not dots (reviewer checklist)."""
        name = self.name or self.id
        if re.search(r"\d+\.\d+", name):
            warn(f"{self.id}: name '{name}' writes its version with dots; use hyphens")
        elif not re.search(r"\d", name):
            warn(f"{self.id}: name '{name}' holds no version")
        return self

    @model_validator(mode="after")
    def description_is_specific(self):
        """The description says what the component simulates, not only where it is used."""
        text = self.description.strip()
        if len(text.split()) == 1 or GENERIC.fullmatch(text):
            warn(f"{self.id}: the description is too generic to say what the component simulates")
        return self

    @model_validator(mode="after")
    def code_base_is_a_fixed_url(self):
        """code_base is a URL, or private/none. A repository URL names a commit, tag or release (EMD 3)."""
        url = (self.code_base or "").strip()
        if not url or url.lower() in NO_PUBLIC_CODE:
            return self
        if not url.startswith(("http://", "https://")):
            warn(f"{self.id}: code_base '{url}' is not a URL, 'private' or 'none'")
        elif ("github.com" in url or "gitlab" in url) and not PINNED.fullmatch(url):
            warn(f"{self.id}: code_base '{url}' does not name a commit, tag or release")
        return self

    @model_validator(mode="after")
    def used_by_a_component_config(self, info: ValidationInfo):
        """A component reaches a model through a component_config; without one it is documented but unused."""
        if used_by(self, info, "component_config", "model_component") is False:
            warn(f"{self.id}: no component_config uses this component")
        return self


model = ModelComponent
