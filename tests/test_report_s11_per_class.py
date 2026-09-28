import json
from pathlib import Path

import numpy as np

from scripts.report_s11_per_class import build_report


def _run(tmp_path, name: str, logits: np.ndarray) -> str:
    run = tmp_path / name
    (run / "predictions").mkdir(parents=True)
    (run / "manifest.json").write_text(
        json.dumps({"complete": True, "git": {"dirty": False}, "class_ids": ["a", "b"]}),
        encoding="utf-8",
    )
    targets = np.asarray([[[1, 0], [0, 1], [1, 0]]], dtype=np.uint8)
    mask = np.ones((1, 3), dtype=bool)
    np.savez(run / "predictions" / "dev.npz", logits=logits, targets=targets, mask=mask)
    return str(run)


def test_build_report_marks_least_positive_classes(tmp_path):
    logits = np.asarray([[[4, -4], [-4, 4], [4, -4]]], dtype=np.float32)
    payload = build_report([("x", Path(_run(tmp_path, "x", logits)))])
    assert payload["class_ids"] == ["a", "b"]
    assert payload["rare_by_dev_positive_frames"] == ["b", "a"]
    assert payload["candidates"]["x"]["a"]["n_pos_frames"] == 2
