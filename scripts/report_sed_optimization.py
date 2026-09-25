"""Tối ưu SED — áp luật chọn hệ thống ADR-0024 §3 và sinh measurement.

    .venv/Scripts/python.exe -m scripts.report_sed_optimization ml/runs/<cand1> ... --dev-only
    .venv/Scripts/python.exe -m scripts.report_sed_optimization ml/runs/<cand1> ...

Mỗi ứng viên (ensemble hoặc run đơn) phải đã có `postproc_cv_selection.json`
(`scripts.select_postproc_cv`). `--dev-only` ghi CV + lựa chọn mà không mở file test —
commit bản này **trước** khi chạy `scripts.evaluate_run --tag cv`, để git chứng minh lựa
chọn có trước test. Bản đầy đủ đòi thêm `evaluation_cv.json` của mọi ứng viên.

Thứ tự trong code phản ánh giao thức: `select_system` chỉ nhận số **dev** (CV mean của
cấu hình đã chọn, số model) và chạy **trước** khi đọc bất kỳ file test nào; kết quả test
đọc sau, chỉ để báo — **mọi** ứng viên đều được in, ứng viên được chọn chỉ được đánh dấu.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_ORDER = ("per_class|50", "per_class|25", "global|50", "global|25")
DEFAULT_CONFIG = "per_class|50"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidates", nargs="+", type=Path)
    parser.add_argument("--dev-only", action="store_true",
                        help="chỉ ghi CV + lựa chọn, không mở file test (commit trước test)")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def _read(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"thiếu {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_label(manifest: dict, run_id: str) -> tuple[str, int]:
    """Human label and number of models behind the predictions."""
    config = manifest.get("config", {})
    if manifest.get("task") == "sed_ensemble":
        return f"ensemble {config['ensemble_label']}", len(config["members"])
    source = str(config.get("weight_source", ""))
    branch = {"audioset": "B", "datasec": "C", "scratch": "A"}.get(source.split(":")[0], "?")
    return f"run đơn {branch} `{run_id.rsplit('_', 1)[-1]}`", 1


def load_dev(run_dir: Path) -> dict:
    """Everything the selection rule may see: dev CV only, no test file is opened."""
    manifest = _read(run_dir / "manifest.json")
    selection = _read(run_dir / "postproc_cv_selection.json")
    selected = selection["selected"]
    key = f"{selected['threshold_mode']}|{selected['g_max_percentile']:g}"
    label, n_models = candidate_label(manifest, run_dir.name)
    return {
        "run_id": run_dir.name, "label": label, "n_models": n_models,
        "git_dirty": bool(manifest.get("git", {}).get("dirty")),
        "selected_config": key, "cv": selection["cv"],
        "score": selection["cv"][key]["mean"], "score_sd": selection["cv"][key]["sd"],
    }


def select_system(candidates: list[dict]) -> dict:
    """ADR-0024 §3: highest dev CV mean; exact tie -> fewer models.

    Also reports whether the margin to the runner-up exceeds the winner's fold sd;
    if not, the winner may not be called "better" (§3, last bullet).
    """
    ranked = sorted(candidates, key=lambda c: (-c["score"], c["n_models"]))
    winner = ranked[0]
    margin = winner["score"] - ranked[1]["score"] if len(ranked) > 1 else None
    return {
        "run_id": winner["run_id"], "label": winner["label"], "score": winner["score"],
        "fold_sd": winner["score_sd"],
        "runner_up": ranked[1]["run_id"] if len(ranked) > 1 else None,
        "margin": margin,
        "margin_exceeds_fold_sd": margin is not None and margin > winner["score_sd"],
    }


def _metrics(evaluation: dict) -> dict:
    ci = evaluation["event_based_f1_bootstrap"]
    return {
        "event_f1": evaluation["event_based_f1"]["f_measure"],
        "ci": [ci["lower"], ci["upper"]],
        "psds_1": evaluation["psds"]["psds_1"], "psds_2": evaluation["psds"]["psds_2"],
    }


def load_test(run_dir: Path) -> dict:
    """Read after selection. Refuses a cv evaluation that did not use postproc_cv.json."""
    tuned = _read(run_dir / "evaluation_cv.json")
    if Path(tuned["postproc"]).name != "postproc_cv.json":
        raise SystemExit(f"{run_dir}/evaluation_cv.json không dùng postproc_cv.json")
    return {"default": _metrics(_read(run_dir / "evaluation.json")), "cv": _metrics(tuned)}


def _fmt(m: dict) -> str:
    return (f"{m['event_f1']:.4f} [{m['ci'][0]:.4f}, {m['ci'][1]:.4f}] | "
            f"{m['psds_1']:.4f} | {m['psds_2']:.4f}")


def render(candidates: list[dict], choice: dict, command: str) -> list[str]:
    lines = render_dev(candidates, choice, command)
    lines += [
        "", "## 3. Test — mỗi cấu hình chạy một lần, báo tất cả", "",
        "| Ứng viên | hậu xử lý | event-F1 [95% CI] | PSDS-1 | PSDS-2 |",
        "|---|---|---:|---:|---:|",
    ]
    for c in candidates:
        mark = " ◀ chọn" if c["run_id"] == choice["run_id"] else ""
        lines.append(f"| {c['label']}{mark} | mặc định `{DEFAULT_CONFIG}` | "
                     f"{_fmt(c['test']['default'])} |")
        lines.append(f"| {c['label']}{mark} | CV `{c['selected_config']}` | "
                     f"{_fmt(c['test']['cv'])} |")
    if any(c["git_dirty"] for c in candidates):
        lines += ["", "⚠️ Có ứng viên với `git.dirty=true` (xem JSON)."]
    return lines


def render_dev(candidates: list[dict], choice: dict, command: str) -> list[str]:
    """Sections 1–2: dev CV and the choice — needs no test file."""
    lines = [
        "# Tối ưu SED — chọn hậu xử lý và hệ thống trên dev (ADR-0024)", "",
        f"> Sinh bởi `{command}`. Không tính lại metric: đọc `postproc_cv_selection.json`, "
        "`evaluation.json`, `evaluation_cv.json` của từng ứng viên.", "",
        "Luật chọn (ADR-0024 §2–§3, ghi trước khi có số): trong mỗi ứng viên chọn cấu hình "
        "có CV mean lớn nhất (không hơn hẳn mặc định thì giữ `per_class|50`); giữa các "
        "ứng viên chọn CV mean lớn nhất, hoà thì ít model hơn. Test chỉ để báo.", "",
        "## 1. CV 5 fold trên dev (event-F1, mean ± sd giữa fold)", "",
        "| Ứng viên | model | " + " | ".join(f"`{k}`" for k in CONFIG_ORDER) + " | chọn |",
        "|---|---:|" + "---:|" * len(CONFIG_ORDER) + "---|",
    ]
    for c in candidates:
        cells = [f"{c['cv'][k]['mean']:.4f} ± {c['cv'][k]['sd']:.4f}" for k in CONFIG_ORDER]
        lines.append(f"| {c['label']} | {c['n_models']} | " + " | ".join(cells)
                     + f" | `{c['selected_config']}` |")
    verdict = ("lớn hơn" if choice["margin_exceeds_fold_sd"] else
               "**không** lớn hơn — không được gọi là tốt hơn ứng viên xếp sau")
    lines += [
        "", "## 2. Hệ thống được chọn (chỉ bằng dev)", "",
        f"**{choice['label']}** (`{choice['run_id']}`), CV mean {choice['score']:.4f} "
        f"± {choice['fold_sd']:.4f}.",
    ]
    if choice["margin"] is not None:
        lines.append(f"Cách ứng viên xếp thứ hai `{choice['runner_up']}` "
                     f"{choice['margin']:+.4f} — {verdict} sd giữa fold.")
    return lines


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    candidates = [load_dev(run_dir) for run_dir in args.candidates]
    choice = select_system(candidates)  # quyết định xong trước khi mở file test
    command = "scripts.report_sed_optimization " + " ".join(p.name for p in args.candidates)
    suffix = "_dev" if args.dev_only else ""
    destination = args.output or (
        ROOT / "docs" / "measurements"
        / f"sed_optimization_{datetime.now(UTC).strftime('%Y%m%d')}{suffix}.md"
    )
    if args.dev_only:
        lines = render_dev(candidates, choice, command + " --dev-only")
    else:
        for run_dir, candidate in zip(args.candidates, candidates, strict=True):
            candidate["test"] = load_test(run_dir)
        lines = render(candidates, choice, command)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    destination.with_suffix(".json").write_text(
        json.dumps({"selected": choice, "candidates": candidates}, indent=2,
                   ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"report": str(destination), "selected": choice["run_id"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
