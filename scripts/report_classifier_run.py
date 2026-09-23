"""D1 — báo cáo một run của `scripts.train_classifier` từ manifest/metrics đã lưu.

    .venv/Scripts/python.exe -m scripts.report_classifier_run ml/runs/<run_id>

In lại đúng số đã ghi trong `manifest.json`/`metrics.json`/`history.json` —
không tính toán lại, không làm tròn khác đi. Sinh
`docs/measurements/classifier_datasec_<run_id>.md`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(run_dir: Path, name: str) -> dict:
    import json

    path = run_dir / name
    if not path.exists():
        raise SystemExit(f"Thiếu {path}. Run chưa hoàn tất hoặc sai đường dẫn.")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    run_dir = args.run_dir
    manifest = load(run_dir, "manifest.json")
    metrics = load(run_dir, "metrics.json")
    history = load(run_dir, "logs/history.json")["epochs"]

    if not manifest.get("complete"):
        raise SystemExit(f"{run_dir} chưa hoàn tất (complete=false) — không báo cáo run dở dang.")

    checkpoint_path = manifest["config"].get("checkpoint_path")
    is_pretrained = checkpoint_path is not None
    branch_note = (
        "Nạp checkpoint AudioSet — đây là bước giữa của **nhánh C** (ADR-0002)."
        if is_pretrained
        else "⚠️ **KHÔNG nạp checkpoint AudioSet** — encoder khởi tạo ngẫu nhiên. "
        "Đây KHÔNG PHẢI nhánh C như ADR-0002 định nghĩa, chỉ là CNN14-scratch."
    )

    best_epoch = max(history, key=lambda item: item["validation"]["coarse_macro_f1"])
    test = metrics.get("test")

    lines = [
        f"# Run huấn luyện DataSEC — `{run_dir.name}`",
        "",
        f"> Sinh bởi `scripts.report_classifier_run {run_dir}`. Không sửa số bằng tay.",
        "",
        f"- {branch_note}",
        f"- Checkpoint: `{checkpoint_path or '(không có — scratch)'}`",
        f"- Checkpoint SHA-256: `{manifest['config'].get('checkpoint_sha256') or '(n/a)'}`",
        f"- Tỷ lệ tham số transplant: "
        f"`{manifest['config'].get('checkpoint_parameter_fraction') or '(n/a)'}`",
        f"- Split SHA-256: `{manifest['split_sha256']}`",
        f"- Taxonomy SHA-256: `{manifest['taxonomy_sha256']}`",
        f"- Seed: `{manifest['config']['seed']}`",
        f"- Git dirty lúc chạy: `{manifest['git']['dirty']}`"
        + (
            " — ⚠️ số dưới đây là thăm dò, không phải số khoá cuối. Chạy lại trên "
            "tree sạch sau khi commit để có số chính thức."
            if manifest["git"]["dirty"]
            else ""
        ),
        "- Số item: " + ", ".join(f"{k}={v}" for k, v in manifest["dataset_items"].items()),
        f"- Best checkpoint: epoch {best_epoch['epoch']}/{len(history)} "
        f"(validation coarse_macro_f1 = {best_epoch['validation']['coarse_macro_f1']:.4f})",
        "",
        "## Test (chạy một lần, sau khi khoá best checkpoint)",
        "",
    ]
    if test:
        lines += [
            "| Metric | Giá trị |",
            "|---|---:|",
            f"| coarse macro-F1 | {test['coarse_macro_f1']:.4f} |",
            f"| subclass macro-F1 (tất cả node) | {test['subclass_macro_f1_all']:.4f} |",
            f"| subclass macro-F1 (n≥10, {len(manifest['supported_subclass_ids'])} node) | "
            f"{test['subclass_macro_f1_supported']:.4f} |",
            f"| parent-consistency rate | {test['parent_consistency_rate']:.4f} |",
            f"| loss | {test['loss']:.4f} |",
            f"| số item / có subclass | {test['items']} / {test['items_with_subclass']} |",
        ]
    else:
        lines.append("_Không có — chạy với `--evaluate-test` để có số này._")

    lines += [
        "",
        "## Diễn giải",
        "",
        "`subclass macro-F1 (n≥10)` là số diễn giải được (ADR-0006 §3) — 5 node "
        f"đạt ngưỡng này trên test: `{manifest['supported_subclass_ids']}` (chỉ số "
        "trong không gian 28 subclass). Số `(tất cả node)` có nhiễu từ các lớp "
        "n_test nhỏ, chỉ báo cáo kèm theo, không thay thế.",
        "",
        "`parent-consistency rate` đo tỷ lệ subclass dự đoán rơi đúng gia đình "
        "coarse dự đoán — so với baseline random $k_c/28$ đã đặc tả ở "
        "[ADR-0006 §7](../decisions/ADR-0006-danh-gia-subclass.md) khi có số đó.",
    ]

    destination = ROOT / "docs" / "measurements" / f"{run_dir.name}.md"
    destination.write_text("\n".join(lines), encoding="utf-8")
    print(f"report: {destination}")


if __name__ == "__main__":
    main()
