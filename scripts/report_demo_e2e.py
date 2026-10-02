"""Chạy và ghi bằng chứng demo upload TRAIN → timeline/caption → RAG."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

# Allow the documented direct-file invocation to import repository packages.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.provenance import git_state  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recording-id", required=True,
                        help="Recording DataSED thuộc split train, ví dụ S-0016")
    parser.add_argument("--base-url", default="http://localhost:8088")
    return parser.parse_args(argv)


def train_audio(recording_id: str) -> Path:
    with (ROOT / "data/splits/datased_polyphonic.csv").open(encoding="utf-8") as handle:
        split = {r["recording_id"]: r["split"] for r in csv.DictReader(handle)}
    if split.get(recording_id) != "train":
        raise ValueError(f"{recording_id} không thuộc split train")
    with (ROOT / "data/manifests/datased_recordings.csv").open(encoding="utf-8") as handle:
        rows = {r["recording_id"]: r for r in csv.DictReader(handle)}
    path = ROOT / "data/raw/datased/extracted" / rows[recording_id]["audio_relative_path"]
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def request_json(client: httpx.Client, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    body = response.json()
    if not body.get("success"):
        raise RuntimeError(f"API thất bại ở {path}: {body.get('error')}")
    return body


def run(recording_id: str, base_url: str) -> dict[str, Any]:
    audio = train_audio(recording_id)
    with httpx.Client(base_url=base_url, timeout=900) as client:
        status = request_json(client, "GET", "/api/v1/models/status")["data"]
        started = time.perf_counter()
        with audio.open("rb") as handle:
            uploaded = request_json(client, "POST", "/api/v1/audio/upload",
                                    files={"file": (audio.name, handle, "audio/wav")})
        upload_s = time.perf_counter() - started
        if uploaded.get("meta", {}).get("duplicate"):
            raise RuntimeError(f"{recording_id} đã có trong event store; chọn TRAIN recording khác")
        rid = uploaded["data"]["recording_id"]
        timeline = request_json(client, "GET", f"/api/v1/recordings/{rid}/timeline")["data"]
        captions = request_json(client, "GET", f"/api/v1/recordings/{rid}/caption")["data"]
        events = timeline["events"]
        if not events:
            raise RuntimeError("timeline không có event để kiểm truy vấn RAG")
        query_class = events[0]["class_id"]
        query = {"question": f"Bản ghi nào có lớp {query_class}?", "corpus": "upload",
                 "mode": "hybrid", "language": "vi", "k": 5,
                 "filters": {"classes_all": [query_class]}}
        started = time.perf_counter()
        rag = request_json(client, "POST", "/api/v1/retrieval/query", json=query)
        rag_s = time.perf_counter() - started
    evidence = rag["data"]["evidence"]
    return {
        "source_recording_id": recording_id, "source_split": "train",
        "audio_relative_path": audio.relative_to(ROOT).as_posix(),
        "recording_id": rid, "served_run": status["served_run"],
        "model_version": timeline["model_versions"], "official": status["official"],
        "postproc": status["postproc"], "device": status["device"],
        "upload_elapsed_s": upload_s, "events": len(events),
        "caption_languages": sorted(c["language"] for c in captions),
        "captions_with_evidence": sum(bool(c["evidence"]) for c in captions),
        "rag_mode": "hybrid", "rag_query_class": query_class, "rag_elapsed_s": rag_s,
        "rag_evidence": len(evidence),
        "rag_contains_uploaded_recording": any(e["recording_id"] == rid for e in evidence),
        "git": git_state(ROOT),
    }


def render(result: dict[str, Any]) -> str:
    return "\n".join([
        "# Demo SED f2 đầu-cuối", "",
        "> Sinh bởi `scripts.report_demo_e2e`; chỉ upload WAV thuộc TRAIN, không chấm metric.", "",
        "| Kiểm tra | Kết quả |", "|---|---|",
        f"| Nguồn | `{result['source_recording_id']}` (`{result['source_split']}`) |",
        f"| Hệ thống | `{result['served_run']}`; official=`{str(result['official']).lower()}`; "
        f"`{result['device']}` |",
        f"| Upload + phân tích | {result['upload_elapsed_s']:.3f} s; "
        f"{result['events']} event |",
        f"| Caption | {', '.join(result['caption_languages'])}; "
        f"{result['captions_with_evidence']} caption có evidence |",
        f"| RAG `{result['rag_mode']}` | {result['rag_elapsed_s']:.3f} s; "
        f"{result['rag_evidence']} evidence; chứa recording vừa upload: "
        f"{str(result['rag_contains_uploaded_recording']).lower()} |",
    ]) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    result = run(args.recording_id, args.base_url)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    out = ROOT / "docs/measurements" / f"demo_f2_e2e_{stamp}.md"
    out.with_suffix(".json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    out.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
