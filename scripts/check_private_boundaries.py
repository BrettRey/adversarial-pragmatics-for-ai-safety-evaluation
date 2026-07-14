#!/usr/bin/env python3
"""Check that local-only research paths cannot be admitted to Git by default."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTECTED = [
    "private/",
    "benchmark/study-a/_runs/",
]
ALLOWED_NOTICES = {
    "private/README.md",
    "benchmark/study-a/_runs/README.md",
}
SENTINELS = [
    "private/sentinel-private-history.jsonl",
    "benchmark/study-a/_runs/sentinel/evaluator-response.json",
]


def git_lines(*args: str) -> list[str]:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if completed.returncode != 0:
        raise SystemExit(completed.stderr.strip() or "git command failed")
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def main() -> None:
    errors: list[str] = []
    tracked = git_lines("ls-files")
    for path in tracked:
        if any(path.startswith(prefix) for prefix in PROTECTED) and path not in ALLOWED_NOTICES:
            errors.append(f"tracked local-only path: {path}")
    staged = git_lines("diff", "--cached", "--name-only")
    for path in staged:
        if any(path.startswith(prefix) for prefix in PROTECTED) and path not in ALLOWED_NOTICES:
            errors.append(f"staged local-only path: {path}")
    for sentinel in SENTINELS:
        completed = subprocess.run(
            ["git", "check-ignore", "-q", sentinel], cwd=ROOT, check=False
        )
        if completed.returncode != 0:
            errors.append(f"ignore rule missing for local-only sentinel: {sentinel}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    print("ok: private histories, blind Study A runs, and evaluator responses are Git-protected")


if __name__ == "__main__":
    main()
