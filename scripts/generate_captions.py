"""W5 chuẩn bị trước — verify caption+grounding thật trên dự đoán SED đã đóng băng.

    .venv/Scripts/python.exe -m scripts.generate_captions ml/runs/<sed_run_id>

`ml/captioning`/`ml/evaluation/grounding.py` (G1-G3) chỉ có test fixture cô lập,
mỗi fixture đúng 1 event — chưa từng chạy trên timeline nhiều event/lớp lặp lại
sinh ra từ post-processing thật. Dựng lại `estimate` đúng cách `evaluate_run.py`
làm (`process_recordings` + `postproc.json` đã đóng băng, KHÔNG train lại, KHÔNG
sửa gì), canonicalize từng recording, sinh caption bằng `TemplateCaptioner`, rồi
chạy `evaluate_grounding` — báo cáo bất kỳ recording nào không đạt hallucination=0/
omission=0/coverage=1/forbidden=0 (kỳ vọng bằng constructon với captioner ràng
buộc, nên lệch là dấu hiệu bug thật, không phải kết quả nghiên cứu).

Tiện thể chạy luôn `ml/retrieval/document_builder.py` (W6 6.3) trên cùng
timeline thật — fixture của nó cũng chỉ có 2 event, chưa từng thấy recording
tới hàng chục event đồng thời.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ml.captioning.lexicon import CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.captioning.timeline import canonicalize_timeline
from ml.evaluation.grounding import evaluate_grounding
from ml.evaluation.predictions import load_predictions
from ml.postprocessing import process_recordings, stack_predictions_by_recording
from ml.postprocessing.calibration import validate_postproc_artifact
from ml.retrieval.document_builder import build_document
from ml.taxonomy import load_taxonomy
from scripts.report_threshold_ablation import priors_from_postproc

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--split", choices=("dev", "test"), default="test")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    manifest = json.loads((args.run_dir / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete"):
        raise SystemExit(f"{args.run_dir} chưa hoàn tất — không sinh caption trên run dở dang")

    postproc = json.loads((args.run_dir / "postproc.json").read_text(encoding="utf-8"))
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    validate_postproc_artifact(postproc, taxonomy=taxonomy)
    class_ids = taxonomy.polyphonic_class_ids

    artifact = load_predictions(
        args.run_dir / "predictions" / f"{args.split}.npz", expected_class_ids=class_ids
    )
    if artifact.split != args.split:
        raise SystemExit(f"predictions split={artifact.split!r}, cần {args.split!r}")

    probabilities = stack_predictions_by_recording(artifact)
    priors = priors_from_postproc(postproc, class_ids)
    thresholds = {
        class_id: float(postproc["per_class"][class_id]["theta"]) for class_id in class_ids
    }
    frame_rate = 1.0 / artifact.frame_hop_s

    estimate = process_recordings(
        probabilities, class_ids=class_ids, thresholds=thresholds, priors=priors,
        frame_rate=frame_rate,
    )

    lexicon = CaptionLexicon.from_taxonomy(taxonomy)
    captioner = TemplateCaptioner(lexicon)
    model_version = str(manifest.get("config", {}).get("encoder_type", "sed-unknown"))

    per_recording: list[dict[str, object]] = []
    anomalies: list[dict[str, object]] = []
    document_failures: list[dict[str, object]] = []
    polyphony_values: list[int] = []
    for recording_id in sorted(probabilities):
        duration_s = probabilities[recording_id].shape[0] / frame_rate
        events = estimate.get(recording_id, [])
        timeline = canonicalize_timeline(
            f"datased:{recording_id}", duration_s, events, taxonomy,
            model_version=model_version,
        )
        caption = captioner.caption(timeline)
        metrics = evaluate_grounding(timeline, caption, lexicon)
        record = {
            "recording_id": recording_id,
            "n_events": len(timeline["events"]),
            "text": caption["text"],
            "metrics": metrics.as_dict(),
        }
        per_recording.append(record)
        if (
            metrics.hallucination_rate != 0
            or metrics.omission_rate != 0
            or metrics.evidence_coverage != 1.0
            or metrics.forbidden_term_rate != 0
            or metrics.temporal_order_accuracy != 1.0
        ):
            anomalies.append(record)

        try:
            document = build_document(caption["text"], timeline)
        except Exception as exc:  # noqa: BLE001 -- wiring smoke test, report don't crash
            document_failures.append({"recording_id": recording_id, "error": repr(exc)})
        else:
            polyphony_values.append(int(document["max_polyphony"]))

    n_recordings = len(per_recording)
    n_with_events = sum(1 for r in per_recording if r["n_events"] > 0)
    total_events = sum(r["n_events"] for r in per_recording)
    max_events = max((r["n_events"] for r in per_recording), default=0)
    max_polyphony_observed = max(polyphony_values, default=0)

    result = {
        "run": str(args.run_dir),
        "split": args.split,
        "n_recordings": n_recordings,
        "n_recordings_with_events": n_with_events,
        "total_events": total_events,
        "max_events_single_recording": max_events,
        "n_anomalies": len(anomalies),
        "anomalies": anomalies,
        "n_document_builder_failures": len(document_failures),
        "document_builder_failures": document_failures,
        "max_polyphony_observed": max_polyphony_observed,
    }

    destination = args.output or (
        ROOT / "docs" / "measurements" / f"{args.run_dir.name}_caption_wiring_{args.split}.md"
    )
    sample = [r for r in per_recording if r["n_events"] > 1][:3] or per_recording[:3]
    lines = [
        f"# Verify wiring caption + grounding — `{args.run_dir.name}` ({args.split})",
        "",
        f"> Sinh bởi `scripts.generate_captions {args.run_dir} --split {args.split}`. "
        "Kiểm wiring end-to-end trên dự đoán thật đã đóng băng — không phải kết quả "
        "nghiên cứu W5 (chưa có nhánh unconstrained/constrained đối chứng).",
        "",
        "## Tổng quan",
        "",
        "| | |",
        "|---|---:|",
        f"| Recording | {n_recordings} |",
        f"| Recording có ≥1 event | {n_with_events} |",
        f"| Tổng event | {total_events} |",
        f"| Event nhiều nhất trong 1 recording | {max_events} |",
        f"| Recording lệch bất biến G1-G3 (kỳ vọng 0) | {len(anomalies)} |",
        f"| `document_builder` lỗi (kỳ vọng 0) | {len(document_failures)} |",
        f"| Polyphony lớn nhất quan sát được | {max_polyphony_observed} |",
        "",
    ]
    if anomalies:
        lines.append(
            "⚠️ **Có recording lệch bất biến** — xem `.json` để tra chi tiết, đây là bug thật."
        )
    else:
        lines.append(
            "Không có recording nào lệch bất biến hallucination=0/omission=0/coverage=1/"
            "forbidden=0/temporal_order=1 — pipeline canonicalize→caption→grounding chạy "
            "đúng trên dự đoán thật, kể cả recording nhiều event."
        )
    if document_failures:
        lines.append(
            "⚠️ **`ml/retrieval/document_builder.py` lỗi trên dữ liệu thật** — xem `.json`."
        )
    else:
        lines.append(
            "`document_builder` (W6 6.3) chạy không lỗi trên mọi recording, kể cả polyphony "
            f"tới {max_polyphony_observed} — fixture cũ chỉ có 2 event/1 mức polyphony."
        )
    lines += ["", "## Ví dụ (ưu tiên recording nhiều event)", ""]
    for record in sample:
        lines.append(f"- `{record['recording_id']}` ({record['n_events']} event): {record['text']}")
    destination.write_text("\n".join(lines), encoding="utf-8")
    destination.with_suffix(".json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({"report": str(destination), "n_anomalies": len(anomalies)}, indent=2))


if __name__ == "__main__":
    main()
