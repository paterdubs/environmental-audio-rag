"""Chẩn đoán: event-based F1 của dự đoán ĐÃ ĐÓNG BĂNG dưới các collar nới rộng.

    .venv/Scripts/python.exe -m scripts.report_collar_sensitivity ml/runs/<run> [...]

Không phải số chính thức và không tuning gì: θ/postproc giữ nguyên, chỉ đổi
dung sai khi chấm (collar onset 0.2 s là protocol, evaluation_protocol §3.2).
Mục đích: tách hai nguồn lỗi. Nếu F1 tăng mạnh khi nới collar, điểm nghẽn là
định vị thời gian (CNN14 ~1.28 s/khối, ADR-0014); phần còn thấp ở collar rộng
là lỗi nhận dạng loại âm thanh.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import event_based_f1
from ml.postprocessing import process_recordings, stack_predictions_by_recording
from ml.postprocessing.calibration import validate_postproc_artifact
from ml.taxonomy import load_taxonomy
from scripts.evaluate_run import load_events_by_recording, priors_from_postproc

ROOT = Path(__file__).resolve().parents[1]
COLLARS = (0.2, 0.5, 1.0, 2.0)
PROTOCOL_COLLAR = 0.2


def collar_curve(
    reference: dict[str, list[dict[str, object]]],
    estimate: dict[str, list[dict[str, object]]],
    class_ids: tuple[str, ...],
    collars: tuple[float, ...] = COLLARS,
) -> list[dict[str, float]]:
    rows = []
    for collar in collars:
        result = event_based_f1(
            reference, estimate, event_label_list=list(class_ids),
            t_collar=collar, percentage_of_length=0.2,
        )["f_measure"]
        rows.append({
            "collar_s": collar,
            "f1": float(result["f_measure"]),
            "precision": float(result["precision"]),
            "recall": float(result["recall"]),
        })
    return rows


def analyse_run(run_dir: Path) -> list[dict[str, float]]:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete"):
        raise SystemExit(f"{run_dir} chưa hoàn tất")
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    postproc = json.loads((run_dir / "postproc.json").read_text(encoding="utf-8"))
    validate_postproc_artifact(postproc, taxonomy=taxonomy)
    class_ids = taxonomy.polyphonic_class_ids
    artifact = load_predictions(run_dir / "predictions" / "test.npz", expected_class_ids=class_ids)
    if artifact.split != "test":
        raise SystemExit(f"predictions split={artifact.split!r}, cần 'test'")
    probabilities = stack_predictions_by_recording(artifact)
    estimate = process_recordings(
        probabilities, class_ids=class_ids,
        thresholds={c: float(postproc["per_class"][c]["theta"]) for c in class_ids},
        priors=priors_from_postproc(postproc, class_ids),
        frame_rate=1.0 / artifact.frame_hop_s,
    )
    return collar_curve(load_events_by_recording(set(probabilities)), estimate, class_ids)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dirs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    results = {run_dir.name: analyse_run(run_dir) for run_dir in args.run_dirs}
    destination = args.output or (
        ROOT / "docs" / "measurements"
        / f"collar_sensitivity_{datetime.now(UTC).strftime('%Y%m%d')}.md"
    )
    header = " | ".join(f"collar {c:g} s" for c in COLLARS)
    lines = [
        "# Chẩn đoán độ nhạy collar — event-based F1",
        "",
        "> Sinh bởi `scripts.report_collar_sensitivity`. **Chẩn đoán, không phải số chính "
        f"thức**: protocol dùng collar {PROTOCOL_COLLAR:g} s; postproc/θ giữ nguyên, không "
        "tuning. Collar thời điểm kết thúc giữ `max(collar, 20% độ dài)`.",
        "",
        f"| Run | {header} |",
        "|---|" + "---:|" * len(COLLARS),
    ]
    for run_name, rows in results.items():
        cells = " | ".join(f"{row['f1']:.4f}" for row in rows)
        lines.append(f"| `{run_name}` | {cells} |")
    lines += ["", "Precision / recall chi tiết trong file `.json` đi kèm."]
    destination.write_text("\n".join(lines), encoding="utf-8")
    destination.with_suffix(".json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({"report": str(destination)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
