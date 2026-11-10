"""Event cross-fit của một run LBR cho các recording một split (ADR-0047). Chỉ đọc dev.npz OOF.

    .venv/Scripts/python.exe -m scripts.export_lbr_oof_events \\
        --lbr-run ml/runs/sed_lbr_B0_20261109T172809Z --point f1 --split validation

Model LBR cuối đã thấy mọi recording dev, nên caption/RAG trên dev dùng event cross-fit: lặp lại
đúng cross-fit lồng nhau của tầng C (cùng OOF nguồn, fold, biến thể, cấu hình, ngưỡng chọn theo
fold), rồi giữ recording của split. Micro F1 trên toàn bộ OOF được ghi vào manifest để đối chiếu
với measurement tầng C — lệch nghĩa là cross-fit không tái lập được.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn

from ml.dataops.inventory import sha256_file
from ml.postprocessing.lbr_apply import OPERATING_POINTS, load_lbr
from ml.postprocessing.lbr_crossfit import build_data, crossfit_lbr
from ml.postprocessing.lbr_timeline import EVENTS_FILE, OOF_EVENTS_TASK
from ml.provenance import git_state
from scripts.fit_lbr_oof import SHARED, evaluate, load, objectives

ROOT = Path(__file__).resolve().parents[1]
SPLIT_FILE = {"validation": "dev"}  # tên corpus -> file posterior (giống build_retrieval_index)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lbr-run", type=Path, required=True)
    parser.add_argument("--point", choices=OPERATING_POINTS, required=True)
    parser.add_argument("--split", choices=tuple(SPLIT_FILE), default="validation")
    parser.add_argument("--runs-dir", type=Path, default=ROOT / "ml/runs")
    return parser.parse_args()


def split_recordings(split: str) -> set[str]:
    rows = pd.read_csv(ROOT / "data/splits/datased_polyphonic.csv")
    return set(rows.loc[rows["split"] == split, "recording_id"].astype(str))


def crossfit_events(lbr_run: Path, point: str) -> tuple[dict, dict, dict]:
    """(manifest LBR, OOF nguồn, event cross-fit của mọi recording OOF tại ``point``)."""
    manifest = json.loads((lbr_run / "manifest.json").read_text(encoding="utf-8"))
    src = load(ROOT / "ml/runs" / manifest["config"]["source_run"])
    bundle = load_lbr(lbr_run, class_ids=src["class_ids"])
    if src["dev_predictions_sha256"] != manifest["config"]["source_dev_sha256"]:
        raise ValueError("posterior OOF nguồn đã đổi so với lúc fit run LBR")
    data = build_data(src["probabilities"], src["reference"], src["folds"],
                      class_ids=src["class_ids"], frame_rate=src["frame_rate"],
                      params=bundle["sebb_params"], config=bundle["config"])
    result = crossfit_lbr(data, variant=bundle["variant"], objectives=objectives(src),
                          config=bundle["config"])
    return {**manifest, "variant": bundle["variant"],
            "fold_thresholds": {str(k): dict(v) for k, v in result.thresholds.items()}}, \
        src, result.events[point]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    lbr, src, events = crossfit_events(args.lbr_run, args.point)
    oof_micro = evaluate(src, events, src["class_ids"])["micro_f1"]
    keep = split_recordings(args.split)
    selected = {rid: events[rid] for rid in sorted(events) if rid in keep}
    if not selected:
        raise ValueError(f"không recording OOF nào thuộc split {args.split}")
    now = datetime.now(UTC)
    out = args.runs_dir / f"sed_lbr_oofevents_{lbr['run_id']}_{args.point}_{now:%Y%m%dT%H%M%SZ}"
    out.mkdir(parents=True)
    path = out / EVENTS_FILE
    path.write_text(json.dumps(selected, indent=1, default=float), encoding="utf-8")
    manifest = {
        "run_id": out.name, "task": OOF_EVENTS_TASK, "complete": True,
        "command": ["python", "-m", "scripts.export_lbr_oof_events", *sys.argv[1:]],
        "class_ids": list(src["class_ids"]), **{k: lbr[k] for k in SHARED},
        "config": {"lbr_run": lbr["run_id"], "variant": lbr["variant"], "point": args.point,
                   "source_run": src["run"].name,
                   "source_dev_sha256": src["dev_predictions_sha256"],
                   "split": args.split, "predictions_split": SPLIT_FILE[args.split],
                   "recordings": len(selected), "events_sha256": sha256_file(path),
                   "oof_micro_f1_all": oof_micro, "fold_thresholds": lbr["fold_thresholds"]},
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scikit_learn": sklearn.__version__},
        "git": git_state(ROOT),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"run": out.name, "recordings": len(selected),
                      "oof_micro_f1_all": oof_micro}, indent=2))


if __name__ == "__main__":
    main()
