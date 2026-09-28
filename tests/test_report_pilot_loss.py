import json
from pathlib import Path

import pytest

from scripts.report_pilot_loss import choose, pilot_row


def _row(gamma: float, values: list[float]) -> dict[str, object]:
    return {
        "run": f"r{gamma}", "focal_gamma": gamma,
        "macro_average_precision": values,
        "encoder_type": "frame_mn", "recipe": "t2b", "seed": 20260922,
        "epochs": 3, "warmup_epochs": 0, "cosine_decay": False,
        "batch_size": 24, "loss": "focal",
    }


def test_choose_uses_epoch_three_and_lower_gamma_on_tie() -> None:
    rows = [_row(0.5, [0.1, 0.2, 0.7]), _row(1.0, [0.2, 0.3, 0.7]), _row(2.0, [0.3, 0.4, 0.6])]
    assert choose(rows)["focal_gamma"] == 0.5


def test_choose_rejects_gamma_outside_preregistered_grid() -> None:
    rows = [_row(0.5, [0.1, 0.2, 0.7]), _row(1.0, [0.2, 0.3, 0.6]), _row(3.0, [0.3, 0.4, 0.5])]
    with pytest.raises(SystemExit, match="đúng lưới"):
        choose(rows)


def test_pilot_row_rejects_dirty_manifest(tmp_path: Path) -> None:
    run = tmp_path / "run"
    (run / "logs").mkdir(parents=True)
    manifest = {"complete": True, "git": {"dirty": True}, "config": {}}
    (run / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(SystemExit, match="tree sạch"):
        pilot_row(run)
