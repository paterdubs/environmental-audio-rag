"""Torch-free provenance helpers shared by training and evaluation scripts."""

from __future__ import annotations

import subprocess
from pathlib import Path


def git_state(root: Path) -> dict:
    def run(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    revision = run("rev-parse", "HEAD")
    if not revision:
        raise RuntimeError(f"Cannot resolve Git revision under {root}")
    return {"revision": revision, "dirty": bool(run("status", "--porcelain"))}
