"""Tổng hợp test annotated của các ứng viên S13 sau khi lựa chọn đã khóa."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument(
        "--candidate", action="append", required=True, help="nhãn=đường/run có evaluation"
    )
    parser.add_argument("--evaluation-name", default="evaluation_cv_annotated.json")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def load_results(
    selection_path: Path, specs: list[str], evaluation_name: str
) -> tuple[dict, list[dict]]:
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    selected = selection.get("selected")
    if not selected or selection.get("provisional") is not False:
        raise ValueError("selection S13 chưa được khóa")
    cv_rank = {item["label"]: item["rank"] for item in selection["ranking"]}
    results = []
    for spec in specs:
        label, separator, raw_path = spec.partition("=")
        if not separator or label not in cv_rank:
            raise ValueError(f"ứng viên không hợp lệ: {spec}")
        run = Path(raw_path)
        payload = json.loads((run / evaluation_name).read_text(encoding="utf-8"))
        if payload.get("split") != "test" or payload.get("eval_set") != "annotated":
            raise ValueError(f"{label}: evaluation không phải test annotated")
        ci = payload["event_based_f1_bootstrap"]
        results.append(
            {
                "label": label,
                "cv_rank": cv_rank[label],
                "run": run.name,
                "postproc_family": payload.get("postproc_family", "theta"),
                "macro": float(payload["event_based_f1_macro"]["f_measure"]),
                "micro": float(payload["event_based_f1"]["f_measure"]),
                "micro_ci_lower": float(ci["lower"]),
                "micro_ci_upper": float(ci["upper"]),
                "n_recordings": int(payload["n_recordings"]),
                "psds_1": float(payload["psds"]["psds_1"]),
                "psds_2": float(payload["psds"]["psds_2"]),
            }
        )
    if {item["label"] for item in results} != set(cv_rank):
        raise ValueError("danh sách test không phủ đúng mọi ứng viên trong selection")
    return selection, sorted(results, key=lambda item: item["cv_rank"])


def render(selection: dict, results: list[dict]) -> str:
    selected = selection["selected"]
    best_test = max(results, key=lambda item: item["micro"])["label"]
    lines = [
        "# S13 — kết quả test `annotated` sau khi khóa lựa chọn",
        "",
        f"> Hệ thống đã khóa bằng CV dev: `{selected}`. Test micro cao nhất: `{best_test}`. "
        "Không chọn lại sau khi xem test.",
        "",
        "| Hạng CV | Ứng viên | Run test | Hậu xử lý | Macro F1 | "
        "Micro F1 [CI 95%] | PSDS-1 | PSDS-2 |",
        "|---:|---|---|---|---:|---:|---:|---:|",
    ]
    for item in results:
        lines.append(
            f"| {item['cv_rank']} | {item['label']} | `{item['run']}` | "
            f"{item['postproc_family']} | {item['macro']:.4f} | {item['micro']:.4f} "
            f"[{item['micro_ci_lower']:.4f}, {item['micro_ci_upper']:.4f}] | "
            f"{item['psds_1']:.4f} | {item['psds_2']:.4f} |"
        )
    lines += [
        "",
        f"Mọi CI bootstrap theo recording; n={results[0]['n_recordings']}. "
        "Thứ tự bảng giữ nguyên hạng CV dev, không xếp lại theo test.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    selection, results = load_results(args.selection, args.candidate, args.evaluation_name)
    payload = {
        "selection": str(args.selection),
        "selected": selection["selected"],
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    report = render(selection, results)
    args.output.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
