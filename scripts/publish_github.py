#!/usr/bin/env python3
"""Stage, commit, and push the current branch with a timestamp message."""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=capture_output,
    )


def main() -> int:
    status = run("git", "status", "--short", capture_output=True)
    if status.returncode != 0:
        print("Could not read git status.", file=sys.stderr)
        return status.returncode
    if not status.stdout.strip():
        print("No changes to commit.")
        return 0

    branch = run("git", "branch", "--show-current", capture_output=True)
    if branch.returncode != 0 or not branch.stdout.strip():
        print("Could not determine the current branch.", file=sys.stderr)
        return branch.returncode or 1

    message = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for command in (
        ("git", "add", "-A"),
        ("git", "commit", "-m", message),
        ("git", "push", "origin", branch.stdout.strip()),
    ):
        result = run(*command)
        if result.returncode != 0:
            return result.returncode

    print(f"Pushed to origin/{branch.stdout.strip()} with commit message: {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
