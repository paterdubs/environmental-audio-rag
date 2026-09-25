"""Tối ưu SED bước 1 — gộp dự đoán đã đóng băng của nhiều run thành một run ensemble.

    .venv/Scripts/python.exe -m scripts.build_ensemble --label B_clean ml/runs/<r1> ml/runs/<r2> ...
    .venv/Scripts/python.exe -m scripts.sweep_threshold ml/runs/sed_ensemble_B_clean_<ts>
    .venv/Scripts/python.exe -m scripts.evaluate_run ml/runs/sed_ensemble_B_clean_<ts>

Không train lại. Ghi `predictions/{dev,test}.npz` (trung bình xác suất), `manifest.json`
(liệt kê thành viên, SHA-256 dự đoán của từng thành viên, git) và `metrics.json` tối
thiểu mà `sweep_threshold` cần. θ vẫn quét trên dev, test đánh giá một lần.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from ml.evaluation.ensemble import average_predictions
from ml.evaluation.predictions import load_predictions, save_predictions
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
SHARED = ("split_sha256", "data_manifest_sha256", "taxonomy_sha256")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("members", nargs="+", type=Path)
    parser.add_argument("--label", required=True)
    return parser.parse_args()


def ensemble_manifest(
    run_id: str, label: str, members: list[Path], manifests: list[dict],
    class_ids: tuple[str, ...], *, command: list[str], git: dict,
) -> dict:
    """Run manifest valid against `contracts/run_manifest.schema.json` (v1 fields).

    Not `manifest_version` 2: v2 requires training-only fields (seeds, checkpoint
    selection, wall clock) that an average of frozen predictions does not have.
    """
    return {
        "run_id": run_id, "task": "sed_ensemble", "command": command, "complete": True,
        "class_ids": list(class_ids), **{key: manifests[0][key] for key in SHARED},
        "config": {
            "ensemble_label": label, "method": "mean_probability",
            "members": [m.name for m in members],
            "members_git_dirty": [bool(x.get("git", {}).get("dirty")) for x in manifests],
        },
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "git": git,
    }


def main() -> None:
    args = parse_args()
    class_ids = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml").polyphonic_class_ids
    manifests = [json.loads((m / "manifest.json").read_text(encoding="utf-8"))
                 for m in args.members]
    for member, manifest in zip(args.members, manifests, strict=True):
        if not manifest.get("complete"):
            raise SystemExit(f"{member} chưa hoàn tất")
        for key in SHARED:
            if manifest.get(key) != manifests[0].get(key):
                raise SystemExit(f"{member}: {key} khác thành viên đầu — không cùng dữ liệu")

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "ml" / "runs" / f"sed_ensemble_{args.label}_{stamp}"
    digests: dict[str, str] = {}
    for split in ("dev", "test"):
        members = [load_predictions(m / "predictions" / f"{split}.npz",
                                    expected_class_ids=class_ids) for m in args.members]
        digests[split] = save_predictions(out / "predictions" / f"{split}.npz",
                                          average_predictions(members),
                                          expected_class_ids=class_ids)
    manifest = ensemble_manifest(
        out.name, args.label, args.members, manifests, class_ids,
        command=["python", "-m", "scripts.build_ensemble", *sys.argv[1:]], git=git_state(ROOT),
    )
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    metrics = {"dev_predictions_sha256": digests["dev"], "test_predictions_sha256": digests["test"]}
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps({"run_dir": str(out), **metrics}, indent=2))


if __name__ == "__main__":
    main()
