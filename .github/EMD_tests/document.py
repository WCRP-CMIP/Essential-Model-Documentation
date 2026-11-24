"""Write CHECKS.md: every EMD_tests model, its fields, the values they accept, and its checks.

    python .github/EMD_tests/document.py             # writes .github/EMD_tests/CHECKS.md
    python .github/EMD_tests/document.py other.md    # writes other.md

Everything is read from the models themselves, so regenerate the file rather than edit it.
"""
from __future__ import annotations

import importlib
import inspect
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import base  # noqa: E402  (needs HERE on sys.path)

LIST_LIMIT = 30   # list a vocabulary's values in full when it has at most this many
FIELD = re.compile(r"^    (\w+): (.+?)(?:\s+=\s+(.+?))?\s*(?:#.*)?$")
LINK = re.compile(r'\b(Links?)\("([\w-]+)"\)')
BOUND = {"Gt": ">", "Ge": "≥", "Lt": "<", "Le": "≤"}


def cell(text: str) -> str:
    """Safe inside a markdown table cell."""
    return " ".join(str(text).split()).replace("|", "\\|")


def summary(obj) -> str:
    """First paragraph of a docstring, on one line."""
    return " ".join(inspect.cleandoc(inspect.getdoc(obj) or "").split("\n\n")[0].split())


def severity(func) -> str:
    """Error when the validator can raise, Warning when it can warn, both when it can do either.

    Shared helpers from base.py that the validator calls (both_or_neither, used_by, ...) are
    read too, since that is where many rules actually raise.
    """
    source = inspect.getsource(func)
    source += "".join(text for name, text in HELPERS.items() if f"{name}(" in source)
    kinds = [name for name, marker in (("Error", "raise "), ("Warning", "warn(")) if marker in source]
    return " + ".join(kinds) or "Tidies input"


HELPERS = {name: inspect.getsource(obj) for name, obj in vars(base).items()
           if inspect.isfunction(obj) and obj.__module__ == base.__name__}


def checks(cls) -> list[tuple[str, str, str]]:
    """(name, severity, description) for each validator a class defines itself, in source order."""
    found = []
    decorators = cls.__pydantic_decorators__
    for group in (decorators.model_validators, decorators.field_validators):
        for name, dec in group.items():
            func = getattr(dec.func, "__func__", dec.func)
            if func.__qualname__.split(".")[0] != cls.__name__:
                continue                       # inherited: listed under its own class
            line = inspect.getsourcelines(func)[1]
            found.append((line, name, severity(func), summary(func)))
    return [(name, sev, text) for _, name, sev, text in sorted(found)]


def allowed(folder: str) -> str:
    """The values a link to `folder` may take."""
    values = sorted(base.entries(folder))
    if not values:
        return f"entries of `{folder}/`"
    if len(values) > LIST_LIMIT:
        return f"any of the {len(values)} entries of `{folder}/`"
    return " · ".join(f"`{v}`" for v in values)


def fields(cls) -> list[tuple[str, str, str, str]]:
    """(field, required, type, allowed values) for each field a class declares, in source order."""
    rows = []
    for line in inspect.getsource(cls).splitlines():
        match = FIELD.match(line)
        if not match or "ClassVar" in line:
            continue
        name, annotation, default = match.group(1), match.group(2), match.group(3) or ""
        info = cls.model_fields.get(name)
        if info is None:
            continue
        shown = info.alias or name
        links = LINK.findall(annotation)
        kind = LINK.sub(lambda m: ("links to " if m[1] == "Links" else "link to ") + m[2], annotation)
        kind = kind.replace(" | None", "").replace("Field(", "").strip()
        if "min_length=1" in default or "min_length=1" in annotation:
            kind += ", at least one"
        pattern = next((m.pattern for m in info.metadata if getattr(m, "pattern", None)), None)
        values = " ".join(allowed(folder) for _, folder in links) or (f"matches `{pattern}`" if pattern else "—")
        rows.append((f"`{shown}`", "yes" if info.is_required() else "no", cell(kind), values))
    return rows


def bounds(annotated) -> str:
    """The numeric limits of a constrained type, e.g. Latitude -> '≥ -90 and ≤ 90'."""
    parts = []
    for info in getattr(annotated, "__metadata__", ()):
        for limit in getattr(info, "metadata", ()):
            name = type(limit).__name__          # Gt, Ge, Lt, Le — each holds its value as .gt, .ge, ...
            if name in BOUND:
                parts.append(f"{BOUND[name]} {getattr(limit, name.lower())}")
    number = "a whole number" if getattr(annotated, "__origin__", None) is int else "a number"
    return f"{number} " + " and ".join(parts)


def table(header: tuple, rows: list) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    return out + ["| " + " | ".join(row) + " |" for row in rows]


def models() -> dict:
    """{folder: model class} for every model file in this directory."""
    found = {}
    for path in sorted(HERE.glob("*.py")):
        if path.stem in {"base", "__init__", "__main__", Path(__file__).stem}:
            continue
        model = getattr(importlib.import_module(path.stem), "model", None)
        if model is not None:
            found[path.stem] = model
    return found


def document() -> str:
    found = models()
    md = [
        "# EMD validation checks", "",
        "_Generated from `.github/EMD_tests` by `document.py`. Regenerate it; do not edit by hand._", "",
        "Every record submitted through an issue is checked against the model for its folder.",
        "**Errors** stop the issue becoming a pull request; the submitter is told what to fix on the issue.",
        "**Warnings** let the pull request be made and are listed on it for the reviewer.", "",
        "## Contents", "",
        "- [Field types](#field-types)",
        "- [Checks on every record](#checks-on-every-record)",
        *[f"- [{folder}](#{folder})" for folder in found], "",
    ]

    md += ["## Field types", "", "The types used in the field tables below.", ""]
    md += table(("Type", "Rule"), [
        ("`link to <folder>`", cell(summary(base.Link))),
        ("`links to <folder>`", cell(summary(base.Links))),
        ("`References`", cell(summary(base.reference))),
        *[(f"`{name}`", bounds(getattr(base, name)))
          for name in ("Positive", "PositiveInt", "Latitude", "Longitude")],
    ])

    md += ["", "## Checks on every record", "", "Every record has these fields and checks, whatever its folder.", "", "### Fields", ""]
    md += table(("Field", "Required", "Type", "Allowed values"), fields(base.EMDRecord))
    md += ["", "### Checks", ""]
    md += table(("Check", "Severity", "What it checks"),
                [(f"`{n}`", s, cell(t)) for n, s, t in checks(base.EMDRecord)])

    for folder, model in found.items():
        md += ["", "---", "", f"## {folder}", "", summary(model), "", "### Fields", ""]
        rows = fields(model)
        md += table(("Field", "Required", "Type", "Allowed values"), rows) if rows else ["_No fields beyond those on every record._"]
        md += ["", "### Checks", ""]
        rows = [(f"`{n}`", s, cell(t)) for n, s, t in checks(model)]
        md += table(("Check", "Severity", "What it checks"), rows) if rows else ["_Only the checks on every record._"]
    return "\n".join(md) + "\n"


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "pydantic_functions.md"
    out.write_text(document(), encoding="utf-8")
    print(f"wrote {out}")
