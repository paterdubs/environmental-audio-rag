"""Chạy kịch bản truy vấn demo thật qua API và ghi bằng chứng."""

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
from ml.provenance import git_state  # noqa: E402

VI = {
    "bells": "chuông", "birds": "chim", "cat_fights_and_moans": "mèo kêu hoặc đánh nhau",
    "chicken_coop": "gà trong chuồng", "cicadas_and_crickets": "côn trùng như ve sầu hoặc dế",
    "dog_barkings_and_howlings": "chó", "horn": "còi xe",
    "jet_aircrafts": "máy bay phản lực", "music": "nhạc",
    "propeller_aircrafts": "máy bay cánh quạt hoặc trực thăng",
    "sirens_and_alarms": "còi hú", "train": "tàu hỏa", "vehicle_pass_by": "xe chạy qua",
    "vehicle_idling": "động cơ xe chạy không tải", "voices": "người nói",
    "workshop": "máy móc của xưởng hoặc công trình",
}
EN = {"bells": "bells", "birds": "birds", "cat_fights_and_moans": "cat fights",
      "dog_barkings_and_howlings": "dog barks", "horn": "horn",
      "sirens_and_alarms": "sirens", "train": "train", "vehicle_pass_by": "vehicle pass-by",
      "vehicle_idling": "vehicle idling", "voices": "voices"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8088")
    return parser.parse_args()


def api(client: httpx.Client, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    body = response.json()
    if not body.get("success"):
        raise RuntimeError(f"API thất bại ở {path}: {body}")
    return body


def train_audio_ids() -> list[tuple[str, Path]]:
    with (ROOT / "data/splits/datased_polyphonic.csv").open(encoding="utf-8") as handle:
        train = {r["recording_id"] for r in csv.DictReader(handle) if r["split"] == "train"}
    labels: dict[str, set[str]] = {}
    with (ROOT / "data/annotations/datased_polyphonic_events.csv").open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["recording_id"] in train:
                labels.setdefault(row["recording_id"], set()).add(row["class_id"])
    with (ROOT / "data/manifests/datased_recordings.csv").open(encoding="utf-8") as handle:
        rows = [(r["recording_id"], ROOT / "data/raw/datased/extracted" / r["audio_relative_path"])
                for r in csv.DictReader(handle) if r["recording_id"] in train]
    return sorted(rows, key=lambda item: (-len(labels.get(item[0], set())), item[0]))


def upload_new(client: httpx.Client) -> tuple[str, dict[str, Any]]:
    existing = api(client, "GET", "/api/v1/recordings", params={"corpus": "upload", "limit": 100})
    known = {r["sha256"] for r in existing["data"]}
    import hashlib
    for source_id, path in train_audio_ids():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in known:
            continue
        with path.open("rb") as handle:
            body = api(client, "POST", "/api/v1/audio/upload",
                       files={"file": (path.name, handle, "audio/wav")})
        data = body["data"]
        events = data.get("timeline", {}).get("events", [])
        if len({event["class_id"] for event in events}) >= 2:
            return source_id, data
        known.add(digest)
    raise RuntimeError("không tìm thấy WAV TRAIN mới có ít nhất hai lớp dự đoán")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    with httpx.Client(base_url=args.base_url, timeout=900) as client:
        source_id, uploaded = upload_new(client)
        rid = uploaded["recording_id"]
        timeline = api(client, "GET", f"/api/v1/recordings/{rid}/timeline")["data"]
        classes = list(dict.fromkeys(e["class_id"] for e in timeline["events"]))
        if not classes:
            raise RuntimeError("recording demo không có event để dựng câu hỏi")
        a = classes[0]
        if len(classes) < 2:
            raise RuntimeError(
                "kịch bản cần ít nhất hai lớp dự đoán để minh hoạ hai lớp và trước/sau")
        b = classes[1]
        duration = max(1.0, (timeline["events"][0]["offset_s"] -
                             timeline["events"][0]["onset_s"]) / 2)
        questions = [
            ("vi", f"Bản ghi nào có tiếng {VI.get(a, a.replace('_', ' '))}?"),
            ("en", f"Which recordings contain both {EN.get(a, a.replace('_', ' '))} and "
                    f"{EN.get(b, b.replace('_', ' '))}?"),
            ("vi", f"Có tiếng {VI.get(a, a.replace('_', ' '))} trước tiếng "
                   f"{VI.get(b, b.replace('_', ' '))} không?"),
            ("en", f"Which recordings have {EN.get(a, a.replace('_', ' '))} lasting longer "
                    f"than {duration:g} seconds?"),
            ("vi", f"Bản ghi nào có tiếng {VI.get(b, b.replace('_', ' '))}?"),
        ]
        results = []
        for language, question in questions:
            parsed = api(client, "POST", "/api/v1/retrieval/parse",
                         json={"question": question, "language": language})
            answer = api(client, "POST", "/api/v1/retrieval/query",
                         json={"question": question, "corpus": "upload", "mode": "hybrid",
                               "language": language, "k": 5})
            results.append({"language": language, "question": question,
                            "parsed": parsed["data"], "answer": answer["data"]})
    result = {"source_recording_id": source_id, "recording_id": rid,
              "event_classes": classes, "questions": results,
              "grounding_artifact": "docs/measurements/caption_grounding_"
              "sed_ensemble_s13_f2_20260929T045053Z_test_annotated.json",
              "git": git_state(ROOT)}
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    out = ROOT / "docs/measurements" / f"demo_script_{stamp}.md"
    out.with_suffix(".json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                         encoding="utf-8")
    lines = ["# Kịch bản demo — lượt chạy thật", "",
             f"- Upload mới: `{source_id}` → `{rid}` (TRAIN).", "",
             "| # | Ngôn ngữ | Câu hỏi | Bộ lọc parse | Số evidence |", "|---:|---|---|---|---:|"]
    for index, item in enumerate(results, 1):
        data = item["answer"]
        lines.append(f"| {index} | {item['language']} | {item['question']} | "
                     f"`{json.dumps(item['parsed']['filters'], ensure_ascii=False)}` | "
                     f"{len(data.get('evidence', []))} |")
    lines += ["", "Grounding minh hoạ lấy từ artifact W5 f2 đã có, không chạy lại chấm test:",
              f"`{result['grounding_artifact']}`.", ""]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
