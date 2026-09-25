"""Sổ test (nghiệm thu W7: "test chạy một lần, mọi cấu hình đã chạy đều được báo cáo").

    .venv/Scripts/python.exe -m scripts.report_test_ledger

Liệt kê **mọi** lần đánh giá SED trên test có trong `ml/runs/*/evaluation*.json` — kể cả run
dirty, run thăm dò, ablation — cùng cấu hình (nhánh, seed, trần pos_weight, file hậu xử lý)
và số đo; rồi mọi measurement khác chạm test theo thành phần. Chỉ đọc artifact, không tính
lại. Mục đích: không cấu hình nào được chạy trên test mà vắng mặt trong báo cáo.
"""

from __future__ import annotations

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
            "psds_2": psds[1]}


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
    lines += ["", "## Thành phần khác chạm test", ""]
    for component, files in result["other"].items():
        listed = ", ".join(f"`{f}`" for f in files) if files else "—"
        lines.append(f"- **{component}** ({len(files)}): {listed}")
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    evaluations = sorted(RUNS.glob("*/evaluation*.json"))
    result = {"git": git_state(ROOT), "sed": [sed_row(e) for e in evaluations],
              "other": other_artifacts()}
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    out = MEASUREMENTS / f"test_ledger_{stamp}.md"
    out.with_suffix(".json").write_text(json.dumps(result, indent=1, ensure_ascii=False),
                                        encoding="utf-8")
    out.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
