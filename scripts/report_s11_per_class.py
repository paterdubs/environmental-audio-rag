"""Báo cáo per-class frame-AP/F1 trên dev cho S11 (không đọc test)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score, f1_score

from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]


def _load(run: Path) -> tuple[list[str], dict[str, dict[str, float | int]]]:
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete") or manifest.get("git", {}).get("dirty") is not False:
        raise ValueError(f"run chưa complete hoặc tree bẩn: {run}")
    class_ids = [str(value) for value in manifest["class_ids"]]
    path = run / "predictions" / "dev.npz"
    if not path.is_file():
        raise ValueError(f"thiếu predictions/dev.npz: {path}")
    data = np.load(path)
    required = {"logits", "targets", "mask"}
    if not required.issubset(data.files):
        raise ValueError(f"artifact dev thiếu trường {sorted(required - set(data.files))}: {path}")
    logits = np.asarray(data["logits"], dtype=np.float32)
    targets = np.asarray(data["targets"], dtype=np.uint8)
    mask = np.asarray(data["mask"], dtype=bool)
    if logits.shape != targets.shape or logits.shape[:2] != mask.shape:
        raise ValueError(f"shape dev không khớp: {path}")
    result: dict[str, dict[str, float | int]] = {}
    probabilities = 1.0 / (1.0 + np.exp(-np.clip(logits, -80.0, 80.0)))
    for index, class_id in enumerate(class_ids):
        valid = mask.reshape(-1)
        y = targets[:, :, index].reshape(-1)[valid]
        p = probabilities[:, :, index].reshape(-1)[valid]
        result[class_id] = {
            "n_pos_frames": int(y.sum()),
            "average_precision": float(average_precision_score(y, p)) if y.any() else float("nan"),
            "f1_at_0_5": float(f1_score(y, p >= 0.5, zero_division=0)),
        }
    return class_ids, result


def _parse_candidate(value: str) -> tuple[str, Path]:
    label, separator, raw = value.partition("=")
    if not separator or not label or not raw:
        raise ValueError(f"candidate phải có dạng nhãn=run: {value!r}")
    return label, Path(raw)


def build_report(candidates: list[tuple[str, Path]]) -> dict[str, object]:
    rows: dict[str, dict[str, dict[str, float | int]]] = {}
    class_ids: list[str] | None = None
    for label, run in candidates:
        ids, metrics = _load(run)
        if class_ids is None:
            class_ids = ids
        elif ids != class_ids:
            raise ValueError("class_ids giữa các run không giống nhau")
        rows[label] = metrics
    assert class_ids is not None
    reference = next(iter(rows.values()))
    rare = sorted(class_ids, key=lambda cid: (int(reference[cid]["n_pos_frames"]), cid))[:5]
    return {"candidates": rows, "class_ids": class_ids, "rare_by_dev_positive_frames": rare}


def render(payload: dict[str, object]) -> str:
    rows = payload["candidates"]
    labels = list(rows)
    lines = [
        "# S11 per-class dev",
        "",
        "> Chỉ dùng `predictions/dev.npz`; không mở test. AP/F1 là frame-level ở ngưỡng 0.5. "
        "‘Hiếm’ được xác định minh bạch là 5 lớp có ít positive frame nhất "
        "trong ứng viên đầu tiên.",
        "",
        "| Lớp | n positive dev | " + " | ".join(f"{label} AP / F1" for label in labels) + " |",
        "|---|---:|" + "---:|" * len(labels),
    ]
    class_ids = payload["class_ids"]
    rare = set(payload["rare_by_dev_positive_frames"])
    for class_id in class_ids:
        marker = " **(hiếm)**" if class_id in rare else ""
        first = rows[labels[0]][class_id]
        cells = [
            f"{rows[label][class_id]['average_precision']:.6f} / "
            f"{rows[label][class_id]['f1_at_0_5']:.6f}"
            for label in labels
        ]
        lines.append(
            f"| `{class_id}`{marker} | {int(first['n_pos_frames'])} | "
            + " | ".join(cells)
            + " |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="append", required=True, help="nhãn=đường_dẫn_run")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "docs" / "measurements")
    args = parser.parse_args()
    candidates = [_parse_candidate(value) for value in args.candidate]
    payload = build_report(candidates)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    stem = args.out_dir / f"s11_per_class_{stamp}"
    payload["generated_by"] = "scripts.report_s11_per_class"
    payload["git"] = git_state(ROOT)
    stem.with_suffix(".json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    stem.with_suffix(".md").write_text(render(payload), encoding="utf-8")
    print(render(payload))


if __name__ == "__main__":
    main()
