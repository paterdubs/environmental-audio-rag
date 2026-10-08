"""Sổ test (nghiệm thu W7: "test chạy một lần, mọi cấu hình đã chạy đều được báo cáo").

    .venv/Scripts/python.exe -m scripts.report_test_ledger

Liệt kê **mọi** lần đánh giá SED trên test có trong `ml/runs/*/evaluation*.json` — kể cả run
dirty, run thăm dò, ablation — cùng cấu hình (nhánh, seed, trần pos_weight, file hậu xử lý)
và số đo; rồi mọi measurement khác chạm test theo thành phần. Chỉ đọc artifact, không tính
lại. Mục đích: không cấu hình nào được chạy trên test mà vắng mặt trong báo cáo.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "ml/runs"
MEASUREMENTS = ROOT / "docs/measurements"
COMPONENTS = {  # measurement file pattern → component (non-SED test artifacts)
    "Caption (RQ2)": r"^caption_(grounding|ngram|per_class|vi_template|lexicon_audit).*test",
    "Caption: lớp gộp / wiring": r"(grouped_class_wording.*test|caption_wiring_test)",
    "Retrieval (RQ3) / câu trả lời": r"^retrieval_(benchmark|answers)_test",
    "Ablation / chẩn đoán SED trên test": r"(threshold_ablation|median_filter|duration_prior|"
                                           r"collar_sensitivity|duration_polyphony|branch_per_class)",
    "Classifier DataSEC": r"^(d4_consistency_selected_test|per_class_metrics_datasec)",
    "Parity phục vụ (so với output đóng băng)": r"^inference_parity",
}


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_details(run: Path, *, runs_dir: Path | None = None,
                seen: frozenset[Path] = frozenset()) -> dict:
    """Metadata of phase-O runs, including inherited rewindow/fold recipes; no predictions."""
    run = run.resolve()
    if run in seen:
        raise ValueError(f"dependency cycle: {run}")
    if not (run / 'manifest.json').exists():
        return {}
    manifest = _read(run / 'manifest.json')
    config = manifest.get('config', {})
    task = manifest.get('task')
    refs = config.get('members', []) or ([config['source_run']] if 'source_run' in config else [])
    children = [run_details((runs_dir or run.parent) / ref, runs_dir=runs_dir,
                            seen=seen | {run}) for ref in refs]
    keys = ('hop_seconds', 'window_weighting', 'cv_fold')
    details = {}
    for key in keys:
        values = [config[key]] if key in config else [c[key] for c in children if key in c]
        flattened = [v for value in values for v in (value if isinstance(value, list) else [value])]
        distinct = list(dict.fromkeys(flattened))
        if distinct:
            details[key] = distinct[0] if len(distinct) == 1 else distinct
    if 'fold_of_member' in config:
        details['cv_fold'] = config['fold_of_member']
    if details or task in ('sed_rewindow', 'sed_oof'):
        return {'task': task, **details}
    return {}


def sed_row(evaluation: Path) -> dict:
    run = evaluation.parent
    manifest = _read(run / "manifest.json")
    config = manifest.get("config", {})
    result = _read(evaluation)
    psds = list(result["psds"].values())
    ensemble = config.get("method") == "mean_probability"
    source = config.get("weight_source", "")
    branch = ("ensemble " + str(config.get("ensemble_label")) if ensemble else
              "A" if source == "scratch" else "B" if source == "audioset" else
              "C" if str(source).startswith("datasec") else "?")
    cap = config.get("pos_weight_cap", "50 (mặc định)") if not ensemble else "—"
    return {"run": run.name, "evaluation": evaluation.name, "branch": branch,
            "seed": config.get("seed", "—"), "pos_weight_cap": "inf" if cap is None else cap,
            "postproc": Path(result.get("postproc", "postproc.json")).name,
            "git_dirty": manifest.get("git", {}).get("dirty"),
            "event_f1": result["event_based_f1"]["f_measure"], "psds_1": psds[0],
            "psds_2": psds[1], **run_details(run)}


def collect_sed(runs_dir: Path) -> list[dict]:
    """Historical evaluation*.json names imply test; explicit dev split is excluded."""
    return [sed_row(path) for path in sorted(runs_dir.glob('*/evaluation*.json'))
            if _read(path).get('split', 'test') == 'test']


def verify_legacy(rows: list[dict], previous: dict) -> dict:
    current = {(r['run'], r['evaluation']): r for r in rows}
    old = previous['sed']
    if any(current.get((r['run'], r['evaluation'])) != r for r in old):
        raise ValueError('dòng sổ test cũ bị đổi hoặc mất')
    return {'previous_rows': len(old), 'unchanged_rows': len(old),
            'added_rows': len(rows) - len(old)}


def other_artifacts() -> dict[str, list[str]]:
    names = sorted(p.name for p in MEASUREMENTS.glob("*.md"))
    return {component: [n for n in names if re.search(pattern, n)]
            for component, pattern in COMPONENTS.items()}


def render(result: dict) -> str:
    rows = result["sed"]
    lines = [
        "# Sổ test — mọi lần đánh giá trên test", "",
        "> Sinh bởi `scripts.report_test_ledger`. Chỉ đọc artifact đã có. Mọi dòng dưới đây "
        "đã chạy trên test; không có cấu hình nào được chọn bằng test (θ, prior, hệ thống, "
        "percentile đều chọn trên dev — ADR-0003, ADR-0024, ADR-0028).", "",
        f"## SED — {len(rows)} lần đánh giá trên test", "",
        "| Run | Đánh giá | Nhánh | Seed | Trần pos_weight | Hậu xử lý | Dirty | Event-F1 | "
        "PSDS-1 | PSDS-2 |", "|---|---|---|---:|---|---|:---:|---:|---:|---:|"]
    for r in rows:
        lines.append(f"| `{r['run']}` | `{r['evaluation']}` | {r['branch']} | {r['seed']} "
                     f"| {r['pos_weight_cap']} | `{r['postproc']}` "
                     f"| {'có' if r['git_dirty'] else 'không'} | {r['event_f1']:.4f} "
                     f"| {r['psds_1']:.4f} | {r['psds_2']:.4f} |")
    new_rows = [r for r in rows if 'task' in r]
    if new_rows:
        # Bảng phụ giữ nguyên byte các dòng lịch sử trong bảng metric phía trên.
        lines += ['', '## Công thức giai đoạn O', '',
                  '| Run | Đánh giá | Task | Hop (s) | Gộp cửa sổ | Fold |',
                  '|---|---|---|---|---|---|']
        for r in new_rows:
            lines.append(f"| `{r['run']}` | `{r['evaluation']}` | {r['task']} | "
                         f"{r.get('hop_seconds', '—')} | {r.get('window_weighting', '—')} | "
                         f"{r.get('cv_fold', '—')} |")
    lines += ["", "## Thành phần khác chạm test", ""]
    for component, files in result["other"].items():
        listed = ", ".join(f"`{f}`" for f in files) if files else "—"
        lines.append(f"- **{component}** ({len(files)}): {listed}")
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs-dir', type=Path, default=RUNS)
    parser.add_argument('--out-dir', type=Path, default=MEASUREMENTS)
    parser.add_argument('--compare-ledger', type=Path)
    args = parser.parse_args()
    result = {"git": git_state(ROOT), "sed": collect_sed(args.runs_dir),
              "other": other_artifacts()}
    if args.compare_ledger:
        result['legacy_audit'] = verify_legacy(result['sed'], _read(args.compare_ledger))
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    out = args.out_dir / f"test_ledger_{stamp}.md"
    if out.exists() or out.with_suffix('.json').exists():
        raise FileExistsError(out)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(result, indent=1, ensure_ascii=False),
                                        encoding="utf-8")
    out.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
