#!/usr/bin/env python3
"""Open the local English preview in the default browser."""
from __future__ import annotations

import sys
import time
import urllib.error
import urllib.request
import webbrowser


URL = "http://127.0.0.1:8000/en/"
TIMEOUT_SECONDS = 10
POLL_SECONDS = 0.5


def is_ready() -> bool:
    try:
        with urllib.request.urlopen(URL, timeout=2) as response:
            return 200 <= response.status < 400
    except (urllib.error.URLError, TimeoutError):
        return False


def main() -> int:
    deadline = time.time() + TIMEOUT_SECONDS
    while time.time() < deadline:
        if is_ready():
            webbrowser.open(URL)
            print(f"Opened {URL}")
            return 0
        time.sleep(POLL_SECONDS)

    print(f"Preview server is not responding at {URL}", file=sys.stderr)
    print("Run `npm run dev` first, then run this script again.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
