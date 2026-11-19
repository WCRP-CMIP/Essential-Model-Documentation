"""Validate every record in the repository and print a coloured report.

Run the folder from the repository root:

    python .github/EMD_tests

Set ISSUES_ONLY below to True to list only the files with an error or a warning.
"""

if __name__ == "__main__":
    import importlib
    import shutil
    import textwrap
    import warnings
    from pathlib import Path

    from pydantic import ValidationError

    from base import REPO, EMDWarning, load

    ISSUES_ONLY = False   # True: list only the files that have an error or a warning

    RESET, BOLD, DIM = "\033[0m", "\033[1m", "\033[2m"
    RED, GREEN, YELLOW, CYAN = "\033[31m", "\033[32m", "\033[33m", "\033[36m"
    STATUS = {"PASS": GREEN, "WARN": YELLOW, "FAIL": RED}   # WARN: loads, but has warnings
    HERE = Path(__file__).resolve().parent

    def check(path):
        """Validate one file. Returns (errors, warnings), each a list of messages."""
        errors = []
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", EMDWarning)
            try:
                load(path)
            except ValidationError as exc:
                for e in exc.errors():
                    where = ".".join(map(str, e["loc"]))
                    message = e["msg"].removeprefix("Value error, ")
                    errors.append(f"{where}: {message}" if where else message)
            except Exception as exc:   # unreadable JSON and the like
                errors.append(f"{type(exc).__name__}: {exc}")
        notes = [str(w.message).removeprefix(f"{path.stem}: ")
                 for w in caught if issubclass(w.category, EMDWarning)]
        return errors, notes

    # ------------------------------------------------------------ every folder that has a model
    folders = [d for d in sorted(REPO.iterdir())
               if d.is_dir() and (HERE / f"{d.name}.py").exists()
               and hasattr(importlib.import_module(d.name), "model")]
    files = {d.name: sorted(p for p in d.glob("*.json") if not p.stem.startswith("_")) for d in folders}

    # ------------------------------------------------------------ column widths, set again for each folder
    width = shutil.get_terminal_size((160, 40)).columns
    name_w = text_w = 0

    def set_widths(paths):
        """Fit the file column to the longest name, and share the rest between warnings and errors."""
        global name_w, text_w
        name_w = min(40, max([len(p.stem) for p in paths] + [4]))
        text_w = max(24, (width - name_w - 4 - 9) // 2)   # 4 for the status, 9 for three " │ " separators

    def wrap(messages):
        return [line for m in messages for line in textwrap.wrap("• " + m, text_w, subsequent_indent="  ")]

    def print_row(name, status, notes, errors):
        """One file, over as many lines as its longest message list needs."""
        left, right = wrap(notes), wrap(errors)
        for i in range(max(len(left), len(right), 1)):
            n = name[:name_w] if i == 0 else ""
            s = f"{STATUS[status]}{status}{RESET}" if i == 0 else "    "
            w = left[i] if i < len(left) else ""
            e = right[i] if i < len(right) else ""
            print(f"{n:<{name_w}} │ {s} │ {YELLOW}{w:<{text_w}}{RESET} │ {RED}{e}{RESET}")

    def rule(char="─"):
        print(DIM + char * min(width, name_w + text_w * 2 + 13) + RESET)

    # ------------------------------------------------------------ one table per folder
    totals = {}
    for folder, paths in files.items():
        set_widths(paths)
        results = []
        for path in paths:
            errors, notes = check(path)
            status = "FAIL" if errors else "WARN" if notes else "PASS"
            results.append((path.stem, status, notes, errors))
        counts = {s: sum(r[1] == s for r in results) for s in STATUS}
        totals[folder] = counts

        print()
        print(f"{BOLD}{CYAN}{folder}{RESET}  {DIM}{len(paths)} files{RESET}  "
              + "  ".join(f"{STATUS[s]}{counts[s]} {s.lower()}{RESET}" for s in STATUS))
        shown = [r for r in results if r[1] != "PASS"] if ISSUES_ONLY else results
        if not shown:
            print(f"{GREEN}  every file passes with no warnings{RESET}")
            continue
        rule()
        print(f"{BOLD}{'file':<{name_w}} │ {'':4} │ {'warnings':<{text_w}} │ errors{RESET}")
        rule()
        for result in shown:
            print_row(*result)
        rule()

    # ------------------------------------------------------------ summary
    print()
    print(f"{BOLD}{'summary':<32}{'files':>7}" + "".join(f"{s:>7}" for s in STATUS) + RESET)
    rule()
    for folder, counts in totals.items():
        print(f"{folder:<32}{sum(counts.values()):>7}"
              + "".join(f"{STATUS[s]}{counts[s]:>7}{RESET}" for s in STATUS))
    rule()
    grand = {s: sum(c[s] for c in totals.values()) for s in STATUS}
    print(f"{BOLD}{'total':<32}{sum(grand.values()):>7}"
          + "".join(f"{STATUS[s]}{grand[s]:>7}{RESET}" for s in STATUS) + RESET)

    # ------------------------------------------------------------ for GitHub Actions
    # Inside an action, hand the counts to later steps (badge, alert). Locally this does nothing.
    import os
    import sys
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as out:
            out.write(f"files={sum(grand.values())}\nfailed={grand['FAIL']}\nwarned={grand['WARN']}\n")
    sys.exit(1 if grand["FAIL"] else 0)   # a failing file fails the run
