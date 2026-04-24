#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
data = json.loads((SRC / "data/site.json").read_text(encoding="utf-8"))
og_dir = SRC / "assets/og"
og_dir.mkdir(parents=True, exist_ok=True)
for key, page in data["pages"].items():
    title = page["translations"]["en"]["h1"]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630"><rect width="1200" height="630" fill="#08151D"/><circle cx="980" cy="150" r="180" fill="#136888" opacity=".28"/><circle cx="880" cy="480" r="160" fill="#E7304D" opacity=".18"/><text x="72" y="190" fill="#9BE1E5" font-family="Space Grotesk, sans-serif" font-size="30" font-weight="700">ROTATA</text><text x="72" y="300" fill="#F5F1E8" font-family="Space Grotesk, sans-serif" font-size="66" font-weight="700">{title[:70]}</text><text x="72" y="390" fill="#A7B6BB" font-family="Manrope, sans-serif" font-size="28">B2B growth systems</text></svg>'''
    (og_dir / f"{key}.svg").write_text(svg, encoding="utf-8")
print("Generated OG SVG templates")
