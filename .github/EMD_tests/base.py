"""Shared building blocks for every EMD record.

Each record folder has a file of the same name (model_family/ -> model_family.py). That file defines one
pydantic class and assigns it to a variable called `model`, so the folder name is all you need
(with this folder on sys.path):

    importlib.import_module("model_family").model

Everything those classes reuse lives here, in this order:

    1. EMDWarning, warn()   advice: the record still loads, but a reviewer should look
    2. field types          Positive, Latitude, Link("grid_type"), Links("region"), References, ...
    3. small rules          both_or_neither, not_both
    4. EMDRecord            the fields and rules that every record shares
    5. load()               read one file and validate it with the model of its folder

A validator that raises rejects the record. A validator that calls warn() lets it load and flags it.
"""
from __future__ import annotations

import importlib
import json
import re
import sys
import warnings
from functools import lru_cache
from pathlib import Path
from typing import Annotated, ClassVar, Literal

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field, ValidationInfo, model_validator

REPO = Path(__file__).resolve().parents[2]                 # .github/EMD_tests/base.py -> repository root
SENTINELS = {"no-horizontal", "no-vertical", "no-family"}  # records that stand for "this has none"


# =====================================================================  1. warnings
class EMDWarning(UserWarning):
    """The record is valid, but something in it should be looked at by a reviewer."""


def warn(message: str) -> None:
    """Flag something without rejecting the record."""
    warnings.warn(message, EMDWarning, stacklevel=2)


# =====================================================================  2. field types
def unwrap_id(value):
    """A JSON-LD link may be written "x" or {"@id": "x"}. Both mean "x"."""
    return value.get("@id", value) if isinstance(value, dict) else value


def as_list(value):
    """A single value where a list is expected becomes a list of one."""
    return value if isinstance(value, list) else [value]


def no_duplicates(items: list) -> list:
    """Each value appears once."""
    if repeated := sorted({str(x) for x in items if items.count(x) > 1}):
        raise ValueError(f"`{', '.join(repeated)}` appears more than once. Each value should appear only once, "
                         f"e.g. `{', '.join(dict.fromkeys(map(str, items)))}`.")
    return items


@lru_cache(maxsize=None)
def entries(folder: str) -> frozenset[str]:
    """The ids held in a repository folder: the names of its .json files."""
    return frozenset(p.stem for p in (REPO / folder).glob("*.json") if not p.stem.startswith("_"))


@lru_cache(maxsize=None)
def referenced_ids(folder: str, field: str) -> frozenset[str]:
    """Every id named by `field` in the records of `folder`, i.e. who points at what."""
    found = set()
    for path in (REPO / folder).glob("*.json"):
        if path.stem.startswith("_"):
            continue
        try:
            record = json.loads(path.read_text("utf-8"))
        except ValueError:
            continue              # a malformed file is reported by its own folder's run
        value = record.get(field)
        for item in (value if isinstance(value, list) else [value]):
            item = unwrap_id(item)
            if isinstance(item, str):
                found.add(item)
    return frozenset(found)


def used_by(record, info: ValidationInfo, folder: str, field: str) -> bool | None:
    """Is this record named by `field` in any record of `folder`? None when the rule does not apply.

    Only records read from disk by load() are answered. A submission arriving from an issue is
    not in any folder yet — and its parent is often created in the same submission — so an
    orphan rule must not fire on it.
    """
    if (info.context or {}).get("file") is None or record.is_sentinel:
        return None
    return record.id in referenced_ids(folder, field)


def pending(info: ValidationInfo, folder: str) -> frozenset[str]:
    """Ids of `folder` that the same submission is creating.

    An issue often creates linked records together — a computational grid with its subgrids, a
    component with its configuration — so a record may link to a sibling not yet on disk.
    The issue handlers pass these in as context={"pending": {folder: ids}}.
    """
    return frozenset(((info.context or {}).get("pending") or {}).get(folder, ()))


def record(info: ValidationInfo, folder: str, record_id: str) -> dict | None:
    """Read another record: one the same submission is creating, else the file on disk. None if neither.

    The issue handlers pass the submission's records in as context={"records": {id: record}}.
    """
    found = ((info.context or {}).get("records") or {}).get(record_id)
    if found is not None:
        return found
    path = REPO / folder / f"{record_id}.json"
    return json.loads(path.read_text("utf-8")) if path.is_file() else None


def Link(folder: str):
    """A value that must name an entry of `folder`, e.g. Link("grid_type") or Link("model_family").

    Controlled vocabularies and other records are both folders of JSON files, so one rule covers both.
    A near miss in spelling ("land_surface" for "land-surface") is suggested in the error.
    """
    def exists(value: str, info: ValidationInfo) -> str:
        if value not in entries(folder) | pending(info, folder):
            guess = re.sub(r"[_\s]+", "-", value.strip().lower())
            example = guess if guess in entries(folder) else min(entries(folder), default="")
            name = folder.replace("_", " ")
            raise ValueError(f"`{value}` is not a recognised {name}. It should be one of the listed {name} values, "
                             f"e.g. `{example}`.")
        return value
    return Annotated[str, BeforeValidator(unwrap_id), AfterValidator(exists)]


def Links(folder: str):
    """A list of Link(folder), each value once. A single value is read as a list of one."""
    return Annotated[list[Link(folder)], BeforeValidator(as_list), AfterValidator(no_duplicates)]


Positive = Annotated[float, Field(gt=0)]
PositiveInt = Annotated[int, Field(gt=0)]
Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=0, lt=360)]
TextList = Annotated[list[str], BeforeValidator(as_list)]

DOI = re.compile(r"https://(?:dx\.)?doi\.org/10\.\d{4,9}/\S+")
UNDER_REVIEW = "https://paper.under.review"


def reference(value: str) -> str:
    """A reference is a URL (error), and a DOI unless the paper is still in preparation (warning).

    Source: EMD v1.1 5. A DOI is written https://doi.org/10.xxxx/...; the legacy
    dx.doi.org host resolves to the same work and is accepted.
    https://paper.under.review stands for a paper in preparation.
    """
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        fix = f"https://doi.org/{value}" if value.startswith("10.") else "https://doi.org/10.1029/2021MS002520"
        raise ValueError(f"Reference `{value}` is not a URL. It should be written as a valid DOI URL, e.g. {fix}")
    if not DOI.fullmatch(value) and value.rstrip("/") != UNDER_REVIEW:
        warn(f"reference '{value}' is not a DOI written https://doi.org/10.xxxx/...")
    return value


References = Annotated[list[Annotated[str, AfterValidator(reference)]],
                       BeforeValidator(as_list), AfterValidator(no_duplicates)]


# =====================================================================  3. small rules
def both_or_neither(record, a: str, b: str) -> None:
    """Error unless `a` and `b` are both set or both left out."""
    if (getattr(record, a) is None) != (getattr(record, b) is None):
        given, missing = (a, b) if getattr(record, a) is not None else (b, a)
        raise ValueError(f"{given} is given without {missing}. They should be given together, or both left out.")


def not_both(record, a: str, b: str) -> None:
    """Error when `a` and `b` are both set."""
    if getattr(record, a) is not None and getattr(record, b) is not None:
        raise ValueError(f"Both {a} and {b} are given. Only one of them should be given, e.g. {a}.")


# =====================================================================  4. the base of every record
ID = r"^[a-z0-9-]+(_[a-z0-9-]+)*$"   # lower case; "_" joins parts, "-" stays inside a part


class EMDRecord(BaseModel):
    """The fields and rules that every record shares. Subclass it in a file named after the folder."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)
    folder: ClassVar[str] = ""   # set from the file name: model_family.py -> "model_family"

    id: str = Field(alias="@id", pattern=ID)
    type: list[str] = Field(alias="@type")
    context: Literal["_context"] = Field(alias="@context")   # unresolved JSON-LD: the folder's own context
    validation_key: str
    ui_label: str | None = None
    description: str | None = None

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)
        cls.folder = Path(sys.modules[cls.__module__].__file__).stem   # works when run as a script too

    @property
    def is_sentinel(self) -> bool:
        """True for no-horizontal, no-vertical and no-family, which stand for "this has none"."""
        return self.id in SENTINELS

    # --------------------------------------------------------------- errors: the record is rejected
    @model_validator(mode="before")
    @classmethod
    def empty_means_not_given(cls, data):
        """An empty string means "not given", so it is dropped before validation."""
        if isinstance(data, dict):
            data = {k: v for k, v in data.items() if not (isinstance(v, str) and not v.strip())}
        return data

    @model_validator(mode="before")
    @classmethod
    def property_names_are_snake_case(cls, data):
        """Property names use lower case and "_" only (the JSON-LD names starting with @ aside)."""
        if isinstance(data, dict):
            bad = sorted(k for k in data if not k.startswith("@") and not re.fullmatch(r"[a-z][a-z0-9_]*", k))
            if bad:
                raise ValueError(f"The property names {bad} are not valid. They should use lower case and '_' only, "
                             f"e.g. `{re.sub(r'[^a-z0-9]+', '_', bad[0].lower()).strip('_')}`.")
        return data

    @model_validator(mode="after")
    def validation_key_matches_id(self):
        """validation_key is @id, in any case, with '-' and '_' treated alike.

        Some vocabularies spell the key with '_' where the id uses '-'
        (arrangement/arakawa-a carries validation_key 'arakawa_a'), so the two
        separators are interchangeable here.
        """
        def same(value: str) -> str:
            return value.lower().replace("_", "-")

        if same(self.validation_key) != same(self.id):
            raise ValueError(f"validation_key `{self.validation_key}` does not match @id `{self.id}`. "
                             f"They should be the same name, e.g. validation_key `{self.id}`.")
        return self

    @model_validator(mode="after")
    def type_names_emd_and_its_folder(self):
        """@type holds "emd" and names the record's folder."""
        if "emd" not in self.type:
            raise ValueError(f"@type {self.type} does not include 'emd'. It should include it, "
                             f"e.g. [\"emd\", \"wcrp:{self.folder}\"].")
        if self.folder and self.folder not in {t.split(":")[-1] for t in self.type}:
            raise ValueError(f"@type {self.type} does not name the folder {self.folder}. It should name it, "
                             f"e.g. [\"emd\", \"wcrp:{self.folder}\"].")
        return self

    @model_validator(mode="after")
    def file_name_matches_id(self, info: ValidationInfo):
        """The file name, without .json, is @id. Checked when the record is read by load()."""
        file = (info.context or {}).get("file")
        if file is not None and file != self.id:
            raise ValueError(f"The file `{file}.json` does not match @id `{self.id}`. It should be renamed, e.g. `{self.id}.json`.")
        return self

    @model_validator(mode="after")
    def id_is_not_a_submission_placeholder(self, info: ValidationInfo):
        """A record kept in the repository has its real id, not the one its issue was given.

        Issue handlers mint a temporary id (tempgrid_<submitter>-<number>) and a later job renames
        the file; one that survives into the repository means that rename did not run. Only files
        on disk are checked, so a submission still carrying its temporary id passes.
        """
        if (info.context or {}).get("file") is None:
            return self
        if "tempgrid" in self.id:
            raise ValueError(f"`{self.id}` is still a temporary submission ID. It should be renamed to its registered ID, e.g. `h175`.")
        return self


# =====================================================================  5. read a file
def load(path) -> EMDRecord:
    """Read one record file and validate it with the `model` in the file named after its folder."""
    path = Path(path)
    module = importlib.import_module(path.parent.name)   # the file named after the folder
    return module.model.model_validate(json.loads(path.read_text("utf-8")), context={"file": path.stem})
