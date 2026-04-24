#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
theme = ROOT / "wordpress-export/rotata-theme"
if not theme.exists():
    raise SystemExit("Run scripts/export_wordpress_theme.py first")
target = ROOT / "wordpress-export/rotata-theme"
archive = shutil.make_archive(str(target), "zip", root_dir=theme.parent, base_dir=theme.name)
print(f"Created {archive}")
