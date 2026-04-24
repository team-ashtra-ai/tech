#!/usr/bin/env python3
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
failures = []
for html_file in DIST.rglob("*.html"):
    html = html_file.read_text(encoding="utf-8")
    h1_count = len(re.findall(r"<h1[\s>]", html, flags=re.I))
    if h1_count != 1:
        failures.append(f"{html_file.relative_to(DIST)} has {h1_count} H1 tags")
    for pattern, label in [(r"<title>[^<]{10,}</title>", "title"), (r'<meta name="description" content="[^"]{40,}"', "description"), (r'rel="canonical"', "canonical"), (r'application/ld\+json', "schema")]:
        if not re.search(pattern, html, flags=re.I):
            failures.append(f"{html_file.relative_to(DIST)} missing {label}")
if failures:
    print("SEO validation failures:")
    print("\n".join(failures))
    sys.exit(1)
print("SEO basics OK")
