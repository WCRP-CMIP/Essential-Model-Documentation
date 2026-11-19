"""model/: a model, its components, and how they embed and couple (EMD v1.1 2 and 3.1)."""
import datetime
import re

from pydantic import Field, model_validator

from base import EMDRecord, Link, Links, References, warn

Domain = Link("scientific_domain")
Pair = tuple[Domain, Domain]

# Short codes used in crs, one per component type.
INITIALS = {"aerosol": "Ae", "atmosphere": "A", "atmospheric-chemistry": "Ac", "land-surface": "L",
            "land-ice": "Li", "ocean": "O", "ocean-biogeochemistry": "Ob", "sea-ice": "Si"}

# The (embedded, host) pairs that are usual (reviewer checklist).
USUAL_EMBEDDING = {("sea-ice", "ocean"), ("ocean-biogeochemistry", "ocean"), ("aerosol", "atmosphere"),
                   ("aerosol", "atmospheric-chemistry"), ("atmospheric-chemistry", "atmosphere"),
                   ("land-surface", "atmosphere")}

# Words that show the description mentions a component.
KEYWORDS = {"aerosol": ["aerosol"], "atmosphere": ["atmosphere", "atmospheric model", "agcm"],
            "atmospheric-chemistry": ["chemistry", "chemical", "ozone", "trace gas"],
            "land-surface": ["land surface", "land model", "land physics", "land component", "terrestrial",
                             "vegetation", "soil"],
            "land-ice": ["land ice", "ice sheet", "ice shelf", "ice shelves", "glacier", "ice cap"],
            "ocean": ["ocean"], "ocean-biogeochemistry": ["biogeochem", "ocean ecosystem", "marine ecosystem",
                                                          "ocean carbon", "marine carbon"],
            "sea-ice": ["sea ice"]}


def first_cycle(child_to_host: dict) -> list | None:
    """The first loop in a child -> host mapping, e.g. ["a", "b", "a"], else None."""
    for start in child_to_host:
        path = [start]
        while path[-1] in child_to_host:
            nxt = child_to_host[path[-1]]
            if nxt in path:
                return path[path.index(nxt):] + [nxt]
            path.append(nxt)
    return None


def connected_groups(nodes, pairs) -> list[set]:
    """Split `nodes` into the groups that `pairs` connect."""
    groups = [{n} for n in nodes]
    for a, b in pairs:
        ga, gb = next((g for g in groups if a in g), None), next((g for g in groups if b in g), None)
        if ga is not None and gb is not None and ga is not gb:
            ga |= gb
            groups.remove(gb)
    return groups


def read_crs(text: str):
    """Read a crs string into ({code: prescribed}, {(embedded, host)}, {frozenset of two coupled codes}).

    EMD v1.1 does not define crs; this grammar is written down from the models in the repository:

        crs    = entry { entry }
        entry  = code [ "^" ] [ "[" member { member } "]" ] [ "(" code { "," code } ")" ]
        member = code [ "[" member { member } "]" ]

    X[Y Z]: Y and Z are embedded in X.  X(Y,Z): X couples with Y and Z.  "^": X is prescribed.
    Raises ValueError when the text does not follow the grammar.
    """
    tokens = re.findall(r"[A-Z][a-z]?|[\[\](),^]", text)
    if "".join(tokens) != re.sub(r"\s", "", text):
        raise ValueError("unknown characters")
    codes, at = set(INITIALS.values()), [0]
    marks, embedded, coupled = {}, set(), set()

    def peek():
        return tokens[at[0]] if at[0] < len(tokens) else None

    def take(token=None):
        got = peek()
        if got is None or (token and got != token) or (not token and got not in codes):
            raise ValueError(f"unexpected '{got}' at token {at[0]}")
        at[0] += 1
        return got

    def entry(host=None):
        code = take()
        if code in marks:
            raise ValueError(f"'{code}' appears twice")
        marks[code] = False
        if host:
            embedded.add((code, host))
        if not host and peek() == "^":
            marks[code] = bool(take("^"))
        if peek() == "[":
            take("[")
            while peek() != "]":
                entry(code)
            take("]")
        if not host and peek() == "(":
            take("(")
            coupled.add(frozenset((code, take())))
            while peek() == ",":
                take(",")
                coupled.add(frozenset((code, take())))
            take(")")

    while peek() is not None:
        entry()
    return marks, embedded, coupled


class Model(EMDRecord):
    """One model. Required: name, description, release_year, calendar, references, dynamic_components and
    model_components (EMD Appendix B 2)."""

    name: str
    description: str
    release_year: int
    calendar: Links("calendar") = Field(min_length=1)
    references: References = Field(min_length=1)
    family: Link("model_family") | None = None
    dynamic_components: Links("scientific_domain") = Field(min_length=1)
    prescribed_components: Links("scientific_domain") = []
    omitted_components: Links("scientific_domain") = []
    embedded_components: list[Pair] = []    # (embedded, host)
    coupled_components: list[Pair] = []
    model_components: Links("component_config") = Field(min_length=1)
    crs: str | None = None

    @property
    def hosts(self) -> list[str]:
        """The superior hosts: dynamic components that are not embedded in another."""
        embedded = {child for child, _ in self.embedded_components}
        return [d for d in self.dynamic_components if d not in embedded]

    # --------------------------------------------------------------- errors: the record is rejected
    @model_validator(mode="after")
    def dynamic_not_also_omitted(self):
        """A component cannot be simulated and also absent (EMD 2)."""
        if both := set(self.dynamic_components) & set(self.omitted_components):
            raise ValueError(f"{sorted(both)} are both dynamic and omitted")
        return self

    @model_validator(mode="after")
    def pairs_name_two_dynamic_components(self):
        """Each embedded or coupled pair names two different dynamic components (EMD Appendix B 2)."""
        for field in ("embedded_components", "coupled_components"):
            for a, b in getattr(self, field):
                if a == b or not {a, b} <= set(self.dynamic_components):
                    raise ValueError(f"{field} pair ({a}, {b}) must name two different dynamic components")
        return self

    @model_validator(mode="after")
    def one_host_each(self):
        """An embedded component has one host (EMD 3.1)."""
        children = [child for child, _ in self.embedded_components]
        if many := sorted({c for c in children if children.count(c) > 1}):
            raise ValueError(f"{many} are embedded in more than one host")
        return self

    @model_validator(mode="after")
    def no_embedding_cycle(self):
        """A component cannot be embedded, directly or indirectly, in itself."""
        if cycle := first_cycle(dict(self.embedded_components)):
            raise ValueError(f"the embedding makes a cycle: {' -> '.join(cycle)}")
        return self

    @model_validator(mode="after")
    def embedded_components_do_not_couple(self):
        """An embedded component cannot be coupled with any other component (EMD 3.1)."""
        embedded = {child for child, _ in self.embedded_components}
        if both := embedded & {x for pair in self.coupled_components for x in pair}:
            raise ValueError(f"{sorted(both)} are embedded and also coupled")
        return self

    @model_validator(mode="after")
    def hosts_coupled_into_one_group(self):
        """With more than one superior host, the couplings join them all into one group (EMD 3.1)."""
        if len(self.hosts) > 1 and len(groups := connected_groups(self.hosts, self.coupled_components)) > 1:
            raise ValueError(f"the couplings leave separate groups: {[sorted(g) for g in groups]}")
        return self

    # --------------------------------------------------------------- warnings: the record loads
    @model_validator(mode="after")
    def family_given(self):
        """family is given; a model with no family uses no-family."""
        if self.family is None:
            warn(f"{self.id}: family is empty; use 'no-family' if the model has none")
        return self

    @model_validator(mode="after")
    def prescribed_not_in_another_list(self):
        """A prescribed component is not also dynamic or omitted (reviewer checklist)."""
        prescribed = set(self.prescribed_components)
        if both := prescribed & (set(self.dynamic_components) | set(self.omitted_components)):
            warn(f"{self.id}: {sorted(both)} are prescribed and also dynamic or omitted")
        return self

    @model_validator(mode="after")
    def embedding_is_usual(self):
        """Each (embedded, host) pair is one of the usual patterns (reviewer checklist)."""
        for child, host in self.embedded_components:
            if (child, host) not in USUAL_EMBEDDING:
                warn(f"{self.id}: {child} embedded in {host} is unusual; check the description explains it")
        return self

    @model_validator(mode="after")
    def release_year_plausible(self):
        """release_year is from 1990 to this year (reviewer checklist)."""
        if not 1990 <= self.release_year <= datetime.date.today().year:
            warn(f"{self.id}: release_year {self.release_year} is implausible")
        return self

    @model_validator(mode="after")
    def crs_agrees_with_lists(self):
        """crs names each dynamic component once, each prescribed one once with "^", and the same pairs."""
        if not self.crs:
            return self
        try:
            marks, embedded, coupled = read_crs(self.crs)
        except ValueError as exc:
            warn(f"{self.id}: crs '{self.crs}' cannot be read: {exc}")
            return self
        code = INITIALS.get
        expected = {code(d): False for d in self.dynamic_components} | {code(d): True for d in self.prescribed_components}
        if marks != expected:
            warn(f"{self.id}: crs '{self.crs}' does not list the same dynamic and prescribed components")
        if embedded != {(code(a), code(b)) for a, b in self.embedded_components}:
            warn(f"{self.id}: crs '{self.crs}' does not show the same embedded_components")
        if coupled != {frozenset((code(a), code(b))) for a, b in self.coupled_components}:
            warn(f"{self.id}: crs '{self.crs}' does not show the same coupled_components")
        return self

    @model_validator(mode="after")
    def description_mentions_each_component(self):
        """The description mentions every dynamic, prescribed and omitted component (EMD 2)."""
        text = self.description.lower().replace("-", " ")
        every = {*self.dynamic_components, *self.prescribed_components, *self.omitted_components}
        missing = sorted(d for d in every if not any(w in text for w in KEYWORDS.get(d, [d.replace("-", " ")])))
        if missing:
            warn(f"{self.id}: the description does not mention {missing}")
        if self.prescribed_components and "prescrib" not in text:
            warn(f"{self.id}: the description does not say how the prescribed components are supplied")
        return self


model = Model
