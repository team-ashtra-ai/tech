#!/usr/bin/env python3
"""Start the local dev server when needed and open the English concept preview."""
from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
URL = "http://127.0.0.1:8000/en/showcase/databricks/"
TIMEOUT_SECONDS = 30
POLL_SECONDS = 0.5


def is_ready() -> bool:
    try:
        with urllib.request.urlopen(URL, timeout=2) as response:
            return 200 <= response.status < 400
    except (urllib.error.URLError, TimeoutError):
        return False


def start_dev_server() -> subprocess.Popen[str]:
    log_path = ROOT / ".open_preview.log"
    log_file = log_path.open("a", encoding="utf-8")
    process = subprocess.Popen(
        ["python3", "scripts/dev.py", "8000"],
        cwd=ROOT,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    print(f"Started local dev server in background (PID {process.pid}).")
    print(f"Server log: {log_path}")
    return process


def wait_until_ready() -> bool:
    deadline = time.time() + TIMEOUT_SECONDS
    while time.time() < deadline:
        if is_ready():
            return True
        time.sleep(POLL_SECONDS)
    return False


def main() -> int:
    if not is_ready():
        start_dev_server()
        if not wait_until_ready():
            print(f"Preview server did not start at {URL}", file=sys.stderr)
            print("Check `.open_preview.log` for the startup error.", file=sys.stderr)
            return 1

    webbrowser.open(URL)
    print(f"Opened {URL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
