#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
failures = []
for html_file in DIST.rglob("*.html"):
    html = html_file.read_text(encoding="utf-8")
    for href in re.findall(r'href="([^"]+)"', html):
        if href.startswith(("#", "mailto:", "tel:", "http")):
            continue
        path = urlparse(href).path
        target = DIST / path.strip("/")
        if path.endswith("/"):
            target = target / "index.html"
        elif not target.suffix:
            target = target / "index.html"
        if not target.exists():
            failures.append(f"{html_file.relative_to(DIST)} -> {href}")
if failures:
    print("Broken internal links:")
    print("\n".join(failures))
    sys.exit(1)
print("Internal links OK")
