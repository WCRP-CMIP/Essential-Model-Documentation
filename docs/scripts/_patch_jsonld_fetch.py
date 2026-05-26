#!/usr/bin/env python3
"""
_patch_jsonld_fetch.py — VERIFIER (changes already applied directly)

The JsonLdExpand integration was applied directly to generate_similarity.py.
This script no longer patches anything; it just verifies the expected
markers are present, so you know the file is in the right state.
"""
import ast
from pathlib import Path

SRC = Path(__file__).resolve().parent / "generate_similarity.py"
text = SRC.read_text(encoding="utf-8")

checks = [
    ("CDN: ldr-core.js",    "jsonld-recursive@1/lib/ldr-core.js"),
    ("CDN: ldr-browser.js", "jsonld-recursive@1/lib/ldr-browser.js"),
    ("loadData IIFE",       "(async function loadData() {"),
    ("JsonLdExpand call",   "JsonLdExpand.compact(jsonAbsUrl, { depth: 2 })"),
    ("contents extraction", "Array.isArray(res.contents)"),
    ("@graph extraction",   "Array.isArray(res['@graph'])"),
]

print(f"Checking {SRC}")
print("=" * 60)
all_ok = True
for label, needle in checks:
    ok = needle in text
    all_ok = all_ok and ok
    print(f"  {'\u2705' if ok else '\u274c'} {label}")

try:
    ast.parse(text)
    print("  \u2705 Python syntax OK")
except SyntaxError as e:
    all_ok = False
    print(f"  \u274c Python syntax error: {e}")

print("=" * 60)
if all_ok:
    print("All changes confirmed in place. No patching needed.")
    print("Next: re-run the build to regenerate view_*.md pages.")
else:
    print("Some markers missing \u2014 the file may have been edited.")
