"""Pilot lr choice (ADR-0032 §8): pre-registered rule and its guards."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.report_pilot_lr import choose, pilot_row


def _run(tmp_path: Path, name: str, lr: float, curve: list[float], **config) -> Path:
    run = tmp_path / name
    (run / "logs").mkdir(parents=True)
    base = {"learning_rate": lr, "recipe": "t2a", "encoder_type": "beats", "seed": 0,
            "epochs": len(curve), "warmup_epochs": 0, "cosine_decay": False, "batch_size": 24}
    base.update(config)
    (run / "manifest.json").write_text(json.dumps(
        {"complete": True, "git": {"dirty": False}, "config": base}), encoding="utf-8")
    (run / "logs" / "history.json").write_text(json.dumps(
        {"epochs": [{"validation": {"macro_average_precision": ap}} for ap in curve]}),
        encoding="utf-8")
    return run


def test_highest_ap_at_the_last_epoch_wins_not_the_best_epoch(tmp_path: Path) -> None:
    rows = [pilot_row(_run(tmp_path, "a", 3e-4, [0.60, 0.66, 0.70])),
            pilot_row(_run(tmp_path, "b", 1e-3, [0.69, 0.74, 0.71])),
            pilot_row(_run(tmp_path, "c", 3e-3, [0.72, 0.69, 0.68]))]
    assert choose(rows)["learning_rate"] == 1e-3


def test_pilots_must_differ_only_in_learning_rate(tmp_path: Path) -> None:
    rows = [pilot_row(_run(tmp_path, "a", 3e-4, [0.6, 0.7, 0.7])),
            pilot_row(_run(tmp_path, "b", 1e-3, [0.6, 0.7, 0.7], seed=1))]
    with pytest.raises(SystemExit, match="seed"):
        choose(rows)
    with pytest.raises(SystemExit, match="constant learning rate"):
        pilot_row(_run(tmp_path, "c", 1e-3, [0.6], cosine_decay=True))
