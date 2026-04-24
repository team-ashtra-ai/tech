#!/usr/bin/env python3
"""Create WebP siblings for large raster assets when Pillow is installed."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "src/assets"
try:
    from PIL import Image
except Exception:
    print("Pillow not installed; skipping image optimization.")
    raise SystemExit(0)

count = 0
for path in ASSETS.rglob("*"):
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        continue
    target = path.with_suffix(".webp")
    if target.exists():
        continue
    with Image.open(path) as image:
        image.thumbnail((1600, 1600))
        image.save(target, "WEBP", quality=82, method=6)
        count += 1
print(f"Optimized {count} images")
