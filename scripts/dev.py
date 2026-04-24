#!/usr/bin/env python3
"""Local dev workflow for the Rotata static site.

Runs an initial build, serves `dist/`, and rebuilds automatically whenever
source files change so edits are visible on a local browser refresh.
"""
from __future__ import annotations

import http.server
import socketserver
import subprocess
import sys
import threading
import time
from functools import partial
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
# Watch only source inputs. `public/`, `schema/` and `dist/` are generated
# during builds, so watching them creates a rebuild loop.
WATCH_DIRS = [ROOT / "src", ROOT / "scripts"]
WATCH_EXTENSIONS = {".py", ".json", ".html", ".css", ".js", ".md", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".avif", ".ico", ".mp4"}


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def file_state() -> dict[str, float]:
    state: dict[str, float] = {}
    for base in WATCH_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in WATCH_EXTENSIONS:
                continue
            state[str(path)] = path.stat().st_mtime
    return state


def run_build() -> bool:
    print("[dev] building site...", flush=True)
    result = subprocess.run(
        ["python3", "scripts/build_site.py"],
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        print("[dev] build failed", flush=True)
        return False

    subprocess.run(["python3", "scripts/generate_sitemap.py"], cwd=ROOT, check=False)
    subprocess.run(["python3", "scripts/generate_schema.py"], cwd=ROOT, check=False)
    print("[dev] build complete", flush=True)
    return True


def serve(port: int) -> None:
    # Keep the process cwd at the repo root. Builds replace `dist/`, and a
    # process cwd inside a removed directory causes empty HTTP responses.
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / "dist"))
    for candidate in range(port, port + 10):
        try:
            with ReusableTCPServer(("127.0.0.1", candidate), handler) as httpd:
                print(f"[dev] preview server running at http://127.0.0.1:{candidate}", flush=True)
                httpd.serve_forever()
        except OSError as error:
            if error.errno != 98 or candidate == port + 9:
                raise
            print(f"[dev] port {candidate} in use, trying {candidate + 1}", flush=True)


def watch(interval: float) -> None:
    previous = file_state()
    while True:
        time.sleep(interval)
        current = file_state()
        if current != previous:
            print("[dev] change detected, rebuilding...", flush=True)
            run_build()
            previous = current


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    if not run_build():
        return 1

    server = threading.Thread(target=serve, args=(port,), daemon=True)
    server.start()
    watch(1.0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
