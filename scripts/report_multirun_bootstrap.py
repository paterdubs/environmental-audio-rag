"""Bootstrap CI theo recording cho event-F1 **trung bình nhiều run** (nghiệm thu W4, RQ1).

    .venv/Scripts/python.exe -m scripts.report_multirun_bootstrap \
        --branch B ml/runs/<b1> ml/runs/<b2> ... --branch C ml/runs/<c1> ...

RQ1-v2 (ADR-0031 §2) thêm `--postproc-name postproc_cv.json --evaluation-name evaluation_cv.json`.

Mỗi run: dự đoán test + `postproc.json` đóng băng, đúng đường đi của `scripts.evaluate_run`
(không chọn lại gì; test đã được đánh giá một lần, đây chỉ là khoảng tin cậy). Đếm (Nref, Nsys,
Ntp) của sed_eval theo từng recording, kiểm tổng khớp `evaluation.json` của run, rồi bootstrap
ghép cặp theo recording (`ml.evaluation.multirun`). PSDS không cộng dồn theo recording nên
không có CI ở đây.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from ml.evaluation.coverage import restrict
from ml.evaluation.multirun import micro_f1, paired_branch_bootstrap
from ml.evaluation.predictions import load_predictions
from ml.evaluation.sed_metrics import event_counts_per_recording
from ml.postprocessing import process_recordings, stack_predictions_by_recording
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from scripts.evaluate_run import load_events_by_recording, priors_from_postproc

ROOT = Path(__file__).resolve().parents[1]
TOLERANCE = 1e-12


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch", nargs="+", action="append", required=True,
                        metavar=("NAME", "RUN"), help="tên nhánh rồi các thư mục run")
    parser.add_argument("--n-bootstrap", type=int, default=1000)
    parser.add_argument("--tag", default="clean")
    parser.add_argument("--postproc-name", default="postproc.json",
                        help="file hậu xử lý trong mỗi run, vd postproc_cv.json (RQ1-v2)")
    parser.add_argument("--evaluation-name", default="evaluation.json",
                        help="file đánh giá test dùng để kiểm tổng, vd evaluation_cv.json")
    parser.add_argument(
        "--postproc-from-evaluation",
        action="store_true",
        help="đọc đường hậu xử lý riêng đã ghi trong từng evaluation thay vì một tên chung",
    )
    return parser.parse_args()


def check_pairing(evaluation: dict, postproc_name: str, run_name: str) -> None:
    """The evaluation file must come from the same post-processing file we recount with."""
    recorded = evaluation.get("postproc")
    if recorded is not None and Path(recorded).name != postproc_name:
        raise SystemExit(f"{run_name}: file đánh giá dùng {Path(recorded).name}, "
                         f"không phải {postproc_name} — cặp file lệch")


def run_counts(run: Path, taxonomy, split: str = "test", postproc_name: str = "postproc.json",
               evaluation_name: str = "evaluation.json", *,
               postproc_from_evaluation: bool = False) -> dict[str, tuple[int, int, int]]:
    """Per-recording sed_eval counts with the run's frozen postproc; test is checked against
    the run's evaluation file (dev has no official evaluation to check against)."""
    official = None
    if split == "test":  # fail fast on a mismatched file pair, before the expensive recount
        official = json.loads((run / evaluation_name).read_text(encoding="utf-8"))
    if postproc_from_evaluation:
        if official is None or not official.get("postproc"):
            raise SystemExit(f"{run.name}: evaluation không ghi đường postproc")
        postproc_path = Path(official["postproc"])
    else:
        postproc_path = run / postproc_name
        if official is not None:
            check_pairing(official, postproc_name, run.name)
    postproc = json.loads(postproc_path.read_text(encoding="utf-8"))
    class_ids = taxonomy.polyphonic_class_ids
    artifact = load_predictions(run / "predictions" / f"{split}.npz", expected_class_ids=class_ids)
    if artifact.split != split:
        raise SystemExit(f"{run.name}: predictions split={artifact.split!r}, cần {split!r}")
    eval_set = official.get("eval_set", "all") if official is not None else "all"
    probabilities = restrict(stack_predictions_by_recording(artifact), eval_set)
    estimate = process_recordings(
        probabilities, class_ids=class_ids,
        thresholds={c: postproc["per_class"][c]["theta"] for c in class_ids},
        priors=priors_from_postproc(postproc, class_ids), frame_rate=1.0 / artifact.frame_hop_s)
    reference = load_events_by_recording(set(probabilities))
    counts = event_counts_per_recording(reference, estimate, event_label_list=list(class_ids))
    if official is None:
        return counts
    summed = micro_f1(*(sum(c[i] for c in counts.values()) for i in range(3)))
    if abs(summed - official["event_based_f1"]["f_measure"]) > TOLERANCE:
        raise SystemExit(f"{run.name}: F1 cộng dồn {summed} ≠ {evaluation_name} — dừng")
    return counts


def render(result: dict) -> str:
    ci = f"CI {result['confidence']:.0%}"
    lines = [
        "# Event-F1 trung bình nhiều run — bootstrap theo recording (test)", "",
        "> Sinh bởi `scripts.report_multirun_bootstrap`. Mỗi lần bootstrap rút lại recording "
        "test một lần và chấm lại **mọi** run trên cùng mẫu (ghép cặp). Các run giữ nguyên, "
        "không rút lại seed — CI đo độ bất định do mẫu recording, độ lệch giữa seed xem cột "
        f"SD. n = {result['n_recordings']} recording, {result['n_bootstrap']} lần, seed "
        f"{result['seed']}. Hậu xử lý `{result.get('postproc_name', 'postproc.json')}`; F1 cộng "
        f"dồn của từng run khớp `{result.get('evaluation_name', 'evaluation.json')}`.", "",
        f"| Nhánh | n run | Mean event-F1 | {ci} | SD giữa run | Các run (F1) |",
        "|---|---:|---:|---|---:|---|",
    ]
    for name, b in result["branches"].items():
        runs = ", ".join(f"`{r[-7:]}` {result['per_run'][r]:.4f}" for r in b["runs"])
        lines.append(f"| {name} | {len(b['runs'])} | {b['estimate']:.4f} "
                     f"| [{b['lower']:.4f}, {b['upper']:.4f}] | {b['sd']:.4f} | {runs} |")
    lines += ["", f"| Hiệu số | Ước lượng | {ci} |", "|---|---:|---|"]
    for name, d in result["differences"].items():
        lines.append(f"| {name} | {d['estimate']:+.4f} | [{d['lower']:+.4f}, {d['upper']:+.4f}] |")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    git = git_state(ROOT)
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    branches = {group[0]: [Path(p) for p in group[1:]] for group in args.branch}
    counts = {run.name: run_counts(run, taxonomy, postproc_name=args.postproc_name,
                                   evaluation_name=args.evaluation_name,
                                   postproc_from_evaluation=args.postproc_from_evaluation)
              for runs in branches.values() for run in runs}
    per_run = {run: micro_f1(*(sum(c[i] for c in rec.values()) for i in range(3)))
               for run, rec in counts.items()}
    names = {name: [run.name for run in runs] for name, runs in branches.items()}
    result = paired_branch_bootstrap(counts, names, n_bootstrap=args.n_bootstrap)
    for b in result["branches"].values():
        values = [per_run[r] for r in b["runs"]]
        b["sd"] = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
    postproc_label = "từ từng evaluation" if args.postproc_from_evaluation else args.postproc_name
    result.update({"per_run": per_run, "git": git, "postproc_name": postproc_label,
                   "evaluation_name": args.evaluation_name})
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    out = ROOT / "docs/measurements" / f"rq1_multirun_bootstrap_{args.tag}_{stamp}.md"
    out.with_suffix(".json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    out.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
