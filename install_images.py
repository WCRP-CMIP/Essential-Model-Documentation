#!/usr/bin/env python3
"""Decode base64-encoded images from a payload file into the assets folder.

Usage: python3 install_images.py <payload_file>

Payload format (one image per line):
    <filename>:<base64-data>
"""
import base64, os, sys

DEST = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "docs", "assets", "home-cards"
)
os.makedirs(DEST, exist_ok=True)

if len(sys.argv) != 2:
    print("Usage: python3 install_images.py <payload_file>")
    sys.exit(1)

payload = sys.argv[1]
count = 0
with open(payload, "r") as f:
    for line in f:
        line = line.strip()
        if not line or ":" not in line:
            continue
        name, b64 = line.split(":", 1)
        out = os.path.join(DEST, name)
        with open(out, "wb") as w:
            w.write(base64.b64decode(b64))
        print(f"wrote {out} ({os.path.getsize(out)} bytes)")
        count += 1

print(f"\ndone: {count} image(s) installed to {DEST}")
