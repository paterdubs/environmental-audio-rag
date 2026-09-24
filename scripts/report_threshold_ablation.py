"""Ablation A2 -- global θ so với per-class θ (evaluation_protocol.md §2.4).

    .venv/Scripts/python.exe -m scripts.report_threshold_ablation ml/runs/<sed_run_id>

Đọc lại θ đã đóng băng trong `postproc.json` (chế độ per-class, chính thức) và
`threshold_ablation.json` (θ của chế độ global, đã sinh bởi `sweep_threshold.py`) —
**không suy lại priors từ train, không sửa `postproc.json`**. Tính event-based F1
tổng hợp đa lớp **đồng thời** cho cả hai chế độ, trên cả dev và test: H2 chỉ tối ưu
per-class theo từng lớp độc lập (các lớp khác suppress về θ=1.0), nên chưa từng có
điểm F1 tổng hợp thật của chế độ per-class khi mọi lớp cùng hoạt động. So sánh
khoảng cách dev→test của hai chế độ — nếu per-class tụt mạnh hơn global, đó là dấu
hiệu overfit dev (§2.4), phải ghi vào Hạn chế của báo cáo SED cuối cùng, không tự
ý đổi lại `postproc.json` để "sửa".
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import event_based_f1
from ml.postprocessing import DurationPrior, process_recordings, stack_predictions_by_recording
from ml.postprocessing.calibration import validate_postproc_artifact
from ml.taxonomy import Taxonomy, load_taxonomy
from scripts.evaluate_run import load_events_by_recording

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def priors_from_postproc(postproc: dict, class_ids: tuple[str, ...]) -> dict[str, DurationPrior]:
    return {
        class_id: DurationPrior(
            median_w=postproc["per_class"][class_id]["median_w"],
            d_min_s=postproc["per_class"][class_id]["d_min_s"],
            g_max_s=postproc["per_class"][class_id]["g_max_s"],
            n_events=postproc["per_class"][class_id]["n_train_events"],
        )
        for class_id in class_ids
    }


def overall_event_f1(
    probabilities: dict[str, object],
    *,
    class_ids: tuple[str, ...],
    thresholds: dict[str, float],
    priors: dict[str, DurationPrior],
    frame_rate: float,
    reference: dict[str, list[dict[str, object]]],
) -> float:
    events = process_recordings(
        probabilities, class_ids=class_ids, thresholds=thresholds, priors=priors,
        frame_rate=frame_rate,
    )
    result = event_based_f1(reference, events, event_label_list=list(class_ids))
    return float(result["f_measure"]["f_measure"])


def compute_split(
    run_dir: Path,
    filename: str,
    *,
    expected_split: str,
    class_ids: tuple[str, ...],
    priors: dict[str, DurationPrior],
    global_thetas: dict[str, float],
    per_class_thetas: dict[str, float],
) -> dict[str, float]:
    artifact = load_predictions(run_dir / "predictions" / filename, expected_class_ids=class_ids)
    if artifact.split != expected_split:
        raise SystemExit(f"{filename} split={artifact.split!r}, cần '{expected_split}'")
    probabilities = stack_predictions_by_recording(artifact)
    reference = load_events_by_recording(set(probabilities))
    frame_rate = 1.0 / artifact.frame_hop_s
    return {
        "global": overall_event_f1(
            probabilities, class_ids=class_ids, thresholds=global_thetas, priors=priors,
            frame_rate=frame_rate, reference=reference,
        ),
        "per_class": overall_event_f1(
            probabilities, class_ids=class_ids, thresholds=per_class_thetas, priors=priors,
            frame_rate=frame_rate, reference=reference,
        ),
    }


def render_report(run_dir: Path, global_theta: float, results: dict, gaps: dict) -> str:
    lines = [
        f"# Ablation A2 — global θ so với per-class θ — `{run_dir.name}`",
        "",
        f"> Sinh bởi `scripts.report_threshold_ablation {run_dir}`. Không đổi "
        "`postproc.json` đã đóng băng (vẫn là per_class, chính thức); đây là báo cáo "
        "so sánh độc lập, dùng lại đúng priors/θ đã có.",
        "",
        "## Event-based F1 đa lớp đồng thời — dev và test",
        "",
        "| Chế độ | Dev F1 | Test F1 | Dev − Test |",
        "|---|---:|---:|---:|",
        f"| Global (θ={global_theta:.2f}) | {results['dev']['global']:.4f} | "
        f"{results['test']['global']:.4f} | {gaps['global']:+.4f} |",
        f"| Per-class | {results['dev']['per_class']:.4f} | "
        f"{results['test']['per_class']:.4f} | {gaps['per_class']:+.4f} |",
        "",
    ]
    if gaps["per_class"] > gaps["global"] + 1e-9:
        lines.append(
            "**Dấu hiệu overfit dev**: per-class tụt mạnh hơn global từ dev sang test "
            "(evaluation_protocol.md §2.4) — 21 bậc tự do fit trên dev. Ghi vào Hạn chế "
            "của báo cáo SED, không tự ý đổi lại `postproc.json`."
        )
    else:
        lines.append(
            "Không có dấu hiệu overfit dev: khoảng cách dev→test của per-class không "
            "tệ hơn global."
        )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    manifest = json.loads((args.run_dir / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete"):
        raise SystemExit(f"{args.run_dir} chưa hoàn tất — không báo cáo ablation trên run dở dang")

    postproc = json.loads((args.run_dir / "postproc.json").read_text(encoding="utf-8"))
    taxonomy: Taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    validate_postproc_artifact(postproc, taxonomy=taxonomy)
    if postproc["threshold_mode"] != "per_class":
        raise SystemExit(f"{args.run_dir}: postproc.json đóng băng không phải per_class")
    class_ids = taxonomy.polyphonic_class_ids

    ablation = json.loads((args.run_dir / "threshold_ablation.json").read_text(encoding="utf-8"))
    global_theta = float(ablation["global"]["theta"])

    priors = priors_from_postproc(postproc, class_ids)
    per_class_thetas = {
        class_id: float(postproc["per_class"][class_id]["theta"]) for class_id in class_ids
    }
    global_thetas = dict.fromkeys(class_ids, global_theta)

    results = {
        split_name: compute_split(
            args.run_dir, filename, expected_split=split_name, class_ids=class_ids,
            priors=priors, global_thetas=global_thetas, per_class_thetas=per_class_thetas,
        )
        for split_name, filename in (("dev", "dev.npz"), ("test", "test.npz"))
    }
    gaps = {
        mode: results["dev"][mode] - results["test"][mode] for mode in ("global", "per_class")
    }

    output_data = {
        "run": str(args.run_dir),
        "global_theta": global_theta,
        "dev": results["dev"],
        "test": results["test"],
        "dev_minus_test_gap": gaps,
        "per_class_worse_gap_than_global": gaps["per_class"] > gaps["global"] + 1e-9,
    }

    destination = args.output or (
        ROOT / "docs" / "measurements" / f"{args.run_dir.name}_threshold_ablation_A2.md"
    )
    destination.write_text(
        render_report(args.run_dir, global_theta, results, gaps), encoding="utf-8"
    )
    destination.with_suffix(".json").write_text(
        json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({"report": str(destination)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
