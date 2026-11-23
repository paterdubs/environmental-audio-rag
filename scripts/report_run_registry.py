"""Sổ đăng ký mọi lần chạy trong `ml/runs/`: loại, trạng thái, cây git, mã băm dữ liệu, ngày.

Chỉ đọc `manifest.json` của từng run; không mở checkpoint hay dự đoán. `ml/runs/` không nằm trong
git, nên đây là số của máy làm việc. Ngày lấy từ mã run (`<task>_<YYYYMMDDTHHMMSSZ>`), tức thời điểm
tạo run; manifest không ghi thời lượng nên không ước lượng giờ GPU.

    .venv/Scripts/python.exe -m scripts.report_run_registry
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "ml" / "runs"
M = ROOT / "docs" / "measurements"
RUN_ID = re.compile(r"^(?P<task>.+?)_(?P<date>\d{8})T\d{6}Z$")
TASK_NAMES = {
    "sed_polyphonic": "Huấn luyện SED", "sed_rewindow": "Suy luận lại theo cửa sổ (OOF, test)",
    "sed_ensemble": "Ensemble SED", "sed_oof": "Gộp dự đoán ngoài mẫu",
    "retrieval_index": "Dựng kho truy hồi", "classifier_datasec": "Huấn luyện bộ phân loại",
    "sed_lbr": "Học LBR", "sed_lbr_oof_events": "Sự kiện LBR ngoài mẫu",
    "pseudo_labels": "Nhãn giả", "sed_filtered": "Lọc dự đoán theo tập", "sed_served": "Hệ phục vụ",
}


def describe(name: str, manifest: dict[str, Any]) -> dict[str, Any]:
    match = RUN_ID.match(name)
    git = manifest.get("git") or {}
    env = manifest.get("environment") or {}
    return {"run": name, "task": manifest.get("task") or (match["task"] if match else name),
            "date": match["date"] if match else None, "complete": bool(manifest.get("complete")),
            "dirty": bool(git.get("dirty")), "split_sha256": manifest.get("split_sha256"),
            "taxonomy_sha256": manifest.get("taxonomy_sha256"), "gpu": env.get("gpu")}


def summarise(runs: list[dict[str, Any]]) -> dict[str, Any]:
    by_task: dict[str, dict[str, Any]] = {}
    groups: dict[str, list[dict]] = defaultdict(list)
    for run in runs:
        groups[run["task"]].append(run)
    for task, items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        by_task[task] = {
            "n": len(items), "complete": sum(r["complete"] for r in items),
            "dirty": sum(r["dirty"] for r in items),
            "split_hashes": len({r["split_sha256"] for r in items if r["split_sha256"]}),
            "taxonomy_hashes": len({r["taxonomy_sha256"] for r in items if r["taxonomy_sha256"]}),
            "first": min((r["date"] for r in items if r["date"]), default=None),
            "last": max((r["date"] for r in items if r["date"]), default=None)}
    per_day: dict[str, Counter] = defaultdict(Counter)
    for run in runs:
        if run["date"]:
            per_day[run["date"]][run["task"]] += 1
    return {"n_runs": len(runs), "by_task": by_task,
            "per_day": {d: dict(c) for d, c in sorted(per_day.items())},
            "gpus": dict(Counter(r["gpu"] for r in runs if r["gpu"]))}


def render(data: dict[str, Any]) -> str:
    lines = [f"# Sổ đăng ký lần chạy ({data['n_runs']} run trong `ml/runs/`)", "",
             "> Sinh bởi `scripts.report_run_registry`; chỉ đọc manifest.", "",
             "| Loại | n | Hoàn tất | Cây bẩn | Số mã băm split | Từ | Đến |",
             "|---|---:|---:|---:|---:|---|---|"]
    for task, s in data["by_task"].items():
        lines.append(f"| {TASK_NAMES.get(task, task)} (`{task}`) | {s['n']} | {s['complete']} | "
                     f"{s['dirty']} | {s['split_hashes']} | {s['first']} | {s['last']} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    runs = [describe(p.name, json.loads((p / "manifest.json").read_text(encoding="utf-8")))
            for p in sorted(RUNS.iterdir()) if (p / "manifest.json").is_file()]
    data = summarise(runs) | {"runs": runs, "git": git_state(ROOT),
                              "created_at": datetime.now(UTC).isoformat()}
    stem = M / f"run_registry_{datetime.now(UTC):%Y%m%d}"
    stem.with_suffix(".json").write_text(json.dumps(data, indent=1, ensure_ascii=False),
                                         encoding="utf-8")
    stem.with_suffix(".md").write_text(render(data), encoding="utf-8")
    print(render(data))


if __name__ == "__main__":
    main()
