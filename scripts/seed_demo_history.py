"""Nạp một corpus lịch sử nhỏ từ TRAIN cho buổi demo local."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

EASY_CLASSES = {
    "sirens_and_alarms", "voices", "birds", "dog_barkings_and_howlings",
    "vehicle_pass_by", "vehicle_idling", "horn", "train", "music",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8088")
    parser.add_argument("--count", type=int, default=20, choices=range(15, 26))
    parser.add_argument("--reset", action="store_true",
                        help="xoá riêng corpus upload trước khi nạp lại")
    return parser.parse_args()


def load_candidates() -> list[dict[str, Any]]:
    split_path = ROOT / "data/splits/datased_polyphonic.csv"
    manifest_path = ROOT / "data/manifests/datased_recordings.csv"
    annotation_path = ROOT / "data/annotations/datased_polyphonic_events.csv"
    splits = {}
    with split_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            splits[row["recording_id"]] = row["split"]
    manifest = {}
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            manifest[row["recording_id"]] = row
    classes: dict[str, set[str]] = {}
    with annotation_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if splits.get(row["recording_id"]) == "train":
                classes.setdefault(row["recording_id"], set()).add(row["class_id"])
    candidates = []
    for recording_id, labels in classes.items():
        row = manifest.get(recording_id)
        if row is None:
            continue
        path = ROOT / "data/raw/datased/extracted" / row["audio_relative_path"]
        if path.is_file():
            candidates.append({"recording_id": recording_id, "classes": sorted(labels),
                               "audio": path, "relative": path.relative_to(ROOT).as_posix()})
    if not candidates:
        raise RuntimeError("không tìm thấy recording TRAIN có annotation và audio")
    return candidates


def choose(candidates: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    remaining = candidates[:]
    covered: set[str] = set()
    while remaining and len(selected) < count:
        def rank(item: dict[str, Any]) -> tuple[int, int, str]:
            labels = set(item["classes"])
            new = len(labels - covered)
            easy = len(labels & EASY_CLASSES)
            return (new * 10 + easy, len(labels), item["recording_id"])
        item = max(remaining, key=rank)
        remaining.remove(item)
        selected.append(item)
        covered.update(item["classes"])
    return selected


def reset_uploads() -> int:
    from ml.retrieval.store import connect

    conn = connect()
    try:
        rows = conn.execute("SELECT recording_id, audio_path FROM recordings "
                            "WHERE source_dataset = 'upload'").fetchall()
        conn.execute("DELETE FROM recordings WHERE source_dataset = 'upload'")
        conn.commit()
    finally:
        conn.close()
    upload_root = (ROOT / "data/uploads").resolve()
    for _, raw_path in rows:
        if not raw_path:
            continue
        path = (ROOT / raw_path).resolve()
        if path.is_relative_to(upload_root) and path.is_file():
            path.unlink()
    return len(rows)


def upload(client: httpx.Client, item: dict[str, Any]) -> dict[str, Any]:
    with item["audio"].open("rb") as handle:
        response = client.post("/api/v1/audio/upload",
                               files={"file": (item["audio"].name, handle, "audio/wav")})
    response.raise_for_status()
    body = response.json()
    if not body.get("success"):
        raise RuntimeError(f"upload {item['recording_id']} thất bại: {body}")
    data = body["data"]
    return {"source_recording_id": item["recording_id"],
            "recording_id": data["recording_id"], "classes": item["classes"],
            "audio_relative_path": item["relative"],
            "duplicate": body.get("meta", {}).get("duplicate", False),
            "events": len(data.get("timeline", {}).get("events", [])),
            "reason": "greedy coverage; ưu tiên lớp dễ nghe, chỉ từ split TRAIN"}


def render(result: dict[str, Any]) -> str:
    lines = ["# Dữ liệu lịch sử demo", "",
             "> Sinh bởi `scripts/seed_demo_history.py`; không dùng validation/test.", "",
             f"- Thời điểm UTC: `{result['timestamp']}`",
             f"- Corpus: `upload`; số recording xử lý: **{len(result['uploads'])}**",
             f"- Số lớp phủ trong annotation TRAIN: **{len(result['covered_classes'])}**",
             f"- Reset trước khi nạp: **{result['reset_count']}**", "",
             "| TRAIN recording | Lớp trong annotation | Event sau phân tích | Kết quả |",
             "|---|---|---:|---|"]
    for item in result["uploads"]:
        status = "trùng SHA, dùng lại" if item["duplicate"] else "đã upload mới"
        lines.append(f"| `{item['source_recording_id']}` | "
                     f"{', '.join(item['classes'])} | {item['events']} | {status} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    reset_count = reset_uploads() if args.reset else 0
    candidates = load_candidates()
    chosen = choose(candidates, args.count)
    with httpx.Client(base_url=args.base_url, timeout=900) as client:
        uploads = [upload(client, item) for item in chosen]
    result = {"timestamp": datetime.now(UTC).isoformat(), "reset_count": reset_count,
              "covered_classes": sorted(set().union(*(set(i["classes"]) for i in chosen))),
              "uploads": uploads}
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    out = ROOT / "docs/measurements" / f"demo_seed_{stamp}.md"
    out.with_suffix(".json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                         encoding="utf-8")
    out.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
