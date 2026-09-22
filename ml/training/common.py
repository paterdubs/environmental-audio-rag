from __future__ import annotations

import hashlib
import json
import os
import random
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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

    return {
        "revision": run("rev-parse", "HEAD") or None,
        "dirty": bool(run("status", "--porcelain")),
    }


def runtime_environment() -> dict:
    return {
        "torch": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "pid": os.getpid(),
    }


def create_run_directory(root: Path, prefix: str) -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run = root / "ml" / "runs" / f"{prefix}_{timestamp}"
    (run / "checkpoints").mkdir(parents=True, exist_ok=False)
    (run / "predictions").mkdir()
    (run / "logs").mkdir()
    return run


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
