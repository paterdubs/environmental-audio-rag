"""ADR-0030 §5 — chọn hệ thống SED cuối **chỉ bằng CV trên dev** (luật ghi trước khi có số v2).

    .venv/Scripts/python.exe -m scripts.select_sed_v2 \\
        --candidate "ensemble C v1=ml/runs/sed_ensemble_C_clean_20260925T045631Z" \\
        --candidate "v2 run đơn=ml/runs/<v2 seed 20260922>" \\
        --candidate "v2 ensemble 3 seed=ml/runs/<ensemble v2>"

Điểm của một ứng viên = CV mean event-F1 (**micro**, như ADR-0024) lớn nhất trong các họ hậu
xử lý đã chạy cho nó: `postproc_cv_selection.json` (họ θ) và `sebb_cv_selection.json` (cSEBB).
Chọn điểm cao nhất; bằng nhau → ít model hơn. Chênh lệch với ứng viên thứ hai nhỏ hơn sd giữa
fold của ứng viên được chọn → ghi "không được gọi là tốt hơn" (như ADR-0024 §3).

Không đọc bất kỳ file test nào. Chạy, **commit kết quả**, rồi mới sinh logit test
(`scripts.dump_predictions`) cho ứng viên được chọn.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Candidate:
    label: str
    run: str
    models: int
    family: str
    config: str
    mean: float
    sd: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidate", action="append", required=True,
                        help="'nhãn=đường/dẫn/run' — lặp lại cho mỗi ứng viên")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "docs" / "measurements")
    return parser.parse_args()


def _read(path: Path) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def best_config(run_dir: Path) -> tuple[str, str, float, float]:
    """(family, config, CV mean, CV sd) of the best post-processing config found for a run."""
    options: list[tuple[str, str, float, float]] = []
    for family, name in (("theta", "postproc_cv_selection.json"),
                         ("csebb", "sebb_cv_selection.json")):
        selection = _read(run_dir / name)
        for config, value in (selection or {}).get("cv", {}).items():
            options.append((family, config, float(value["mean"]), float(value["sd"])))
    if not options:
        raise SystemExit(f"{run_dir}: chưa có CV hậu xử lý nào trên dev")
    return max(options, key=lambda option: option[2])


def model_count(manifest: dict) -> int:
    return len(manifest.get("config", {}).get("members", [])) or 1


def load_candidate(spec: str) -> Candidate:
    label, _, path = spec.partition("=")
    run_dir = Path(path)
    if not label or not run_dir.is_dir():
        raise SystemExit(f"ứng viên không hợp lệ: {spec!r} (cần 'nhãn=đường/dẫn/run')")
    manifest = _read(run_dir / "manifest.json") or {}
    family, config, mean, sd = best_config(run_dir)
    return Candidate(label, run_dir.name, model_count(manifest), family, config, mean, sd)


def select(candidates: list[Candidate]) -> tuple[Candidate, list[Candidate], str]:
    """ADR-0030 §5: highest CV mean; exact tie → fewer models. Returns winner, ranking, note."""
    ranking = sorted(candidates, key=lambda c: (-c.mean, c.models, c.label))
    winner = ranking[0]
    note = ""
    if len(ranking) > 1:
        gap = winner.mean - ranking[1].mean
        if gap <= winner.sd:
            note = (f"Chênh với `{ranking[1].label}` là {gap:+.4f}, **không** lớn hơn sd giữa "
                    f"fold ({winner.sd:.4f}) — không được gọi là tốt hơn ứng viên đó.")
    return winner, ranking, note


def cell(text: str) -> str:
    """Config names like `global|25` inside a markdown table cell: escape the pipe."""
    return "`" + text.replace("|", "\\|") + "`"


def render(winner: Candidate, ranking: list[Candidate], note: str, git: dict) -> str:
    lines = [
        "# Chọn hệ thống SED cuối — chỉ bằng CV trên dev (ADR-0030 §5)", "",
        "> Sinh bởi `scripts.select_sed_v2`. Không đọc test. Event-F1 **micro** (như ADR-0024), "
        "CV 5 fold theo `leakage_group`; điểm = cấu hình hậu xử lý tốt nhất của mỗi ứng viên.",
        f"> git `{git['revision'][:7]}`, dirty={git['dirty']}.", "",
        "| Hạng | Ứng viên | Run | Model | Họ hậu xử lý | Cấu hình | CV mean ± sd |",
        "|---:|---|---|---:|---|---|---:|"]
    lines += [f"| {i} | {c.label}{' ◀ chọn' if c == winner else ''} | `{c.run}` | {c.models} "
              f"| {c.family} | {cell(c.config)} | {c.mean:.4f} ± {c.sd:.4f} |"
              for i, c in enumerate(ranking, 1)]
    if note:
        lines += ["", note]
    lines += ["", "Bước tiếp: commit file này, rồi mới `scripts.dump_predictions --split test` "
              "cho ứng viên được chọn và `scripts.evaluate_run` một lần."]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    candidates = [load_candidate(spec) for spec in args.candidate]
    winner, ranking, note = select(candidates)
    git = git_state(ROOT)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    out = args.out_dir / f"sed_v2_selection_{stamp}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(
        {"winner": winner.__dict__, "ranking": [c.__dict__ for c in ranking], "note": note,
         "git": git, "metric": "event-F1 micro, CV 5 fold dev"}, indent=1, ensure_ascii=False),
        encoding="utf-8")
    out.write_text(render(winner, ranking, note, git), encoding="utf-8")
    print(render(winner, ranking, note, git))


if __name__ == "__main__":
    main()
