"""Measure event-based performance by reference duration and onset polyphony."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import event_based_f1
from ml.postprocessing import process_recordings, stack_predictions_by_recording
from ml.postprocessing.calibration import validate_postproc_artifact
from ml.taxonomy import load_taxonomy
from scripts.evaluate_run import load_events_by_recording, priors_from_postproc

ROOT = Path(__file__).resolve().parents[1]
DURATION_BINS = ("<1s", "1-3s", "3-10s", ">10s")
POLYPHONY_BINS = ("1", "2", ">=3")


def duration_bin(duration: float) -> str:
    if duration < 1.0:
        return "<1s"
    if duration < 3.0:
        return "1-3s"
    if duration <= 10.0:
        return "3-10s"
    return ">10s"


def onset_polyphony(event: dict[str, object], recording_events: list[dict[str, object]]) -> int:
    onset = float(event["onset"])
    return sum(
        float(other["onset"]) <= onset < float(other["offset"])
        for other in recording_events
    )


def polyphony_bin(count: int) -> str:
    if count == 1:
        return "1"
    if count == 2:
        return "2"
    return ">=3"


def score_subset(
    reference: dict[str, list[dict[str, object]]],
    estimate: dict[str, list[dict[str, object]]],
    selected: set[tuple[str, int]],
    class_ids: tuple[str, ...],
) -> dict[str, float | int]:
    subset: dict[str, list[dict[str, object]]] = {}
    for recording_id, events in reference.items():
        kept = [event for index, event in enumerate(events) if (recording_id, index) in selected]
        if kept:
            subset[recording_id] = kept
    if not subset:
        return {"n_reference": 0, "recall": float("nan"), "f1": float("nan")}
    filtered_estimate = {recording_id: estimate.get(recording_id, []) for recording_id in subset}
    result = event_based_f1(subset, filtered_estimate, event_label_list=list(class_ids))
    f_measure = result["f_measure"]
    return {
        "n_reference": sum(len(events) for events in subset.values()),
        "recall": float(f_measure["recall"]),
        "f1": float(f_measure["f_measure"]),
    }


def analyse_run(run_dir: Path) -> dict[str, object]:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete"):
        raise SystemExit(f"{run_dir} chưa hoàn tất")
    postproc = json.loads((run_dir / "postproc.json").read_text(encoding="utf-8"))
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    validate_postproc_artifact(postproc, taxonomy=taxonomy)
    class_ids = taxonomy.polyphonic_class_ids
    artifact = load_predictions(
        run_dir / "predictions" / "test.npz", expected_class_ids=class_ids
    )
    probabilities = stack_predictions_by_recording(artifact)
    reference = load_events_by_recording(set(probabilities))
    priors = priors_from_postproc(postproc, class_ids)
    thresholds = {class_id: postproc["per_class"][class_id]["theta"] for class_id in class_ids}
    estimate = process_recordings(
        probabilities,
        class_ids=class_ids,
        thresholds=thresholds,
        priors=priors,
        frame_rate=1.0 / artifact.frame_hop_s,
    )

    duration_groups: dict[str, set[tuple[str, int]]] = {name: set() for name in DURATION_BINS}
    polyphony_groups: dict[str, set[tuple[str, int]]] = {name: set() for name in POLYPHONY_BINS}
    for recording_id, events in reference.items():
        for index, event in enumerate(events):
            duration = float(event["offset"]) - float(event["onset"])
            duration_groups[duration_bin(duration)].add((recording_id, index))
            count = onset_polyphony(event, events)
            polyphony_groups[polyphony_bin(count)].add((recording_id, index))

    return {
        "run_id": run_dir.name,
        "n_reference_total": sum(len(events) for events in reference.values()),
        "duration": {
            name: score_subset(reference, estimate, selected, class_ids)
            for name, selected in duration_groups.items()
        },
        "polyphony": {
            name: score_subset(reference, estimate, selected, class_ids)
            for name, selected in polyphony_groups.items()
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_b", type=Path)
    parser.add_argument("run_c", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def fmt(value: float) -> str:
    return "N/A" if math.isnan(value) else f"{value:.6f}"


def main() -> None:
    args = parse_args()
    result = {"B": analyse_run(args.run_b), "C": analyse_run(args.run_c)}
    lines = [
        "# K5 — event performance by duration and onset polyphony",
        "",
        "> Reference events are binned; estimates are retained for the same recordings.",
        "> Recall and F1 are event-based metrics; test predictions are read once.",
    ]
    for dimension, labels in (("duration", DURATION_BINS), ("polyphony", POLYPHONY_BINS)):
        lines += [
            "",
            f"## {dimension}",
            "",
            "| Bin | B n | B recall | B F1 | C n | C recall | C F1 |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        for label in labels:
            b = result["B"][dimension][label]
            c = result["C"][dimension][label]
            lines.append(
                f"| {label} | {b['n_reference']} | {fmt(b['recall'])} | {fmt(b['f1'])} | "
                f"{c['n_reference']} | {fmt(c['recall'])} | {fmt(c['f1'])} |"
            )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    args.output.with_suffix(".json").write_text(
        json.dumps(result, indent=2, allow_nan=True), encoding="utf-8"
    )
    print(json.dumps({"report": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
