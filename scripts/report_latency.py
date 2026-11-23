"""Đo độ trễ xử lý của demo đang chạy: tải lên TRAIN nhiều độ dài, truy vấn lặp lại.

Chỉ upload bản ghi thuộc split TRAIN (không chạm dev/test, không chấm metric). Ghi trung vị và p95
của thời gian tải lên + phân tích, hệ số thời gian thực (RTF = thời gian xử lý / độ dài âm thanh) và
độ trễ truy vấn. Thời gian khởi động và RAM đỉnh đo riêng (xem `--container`).

    .venv/Scripts/python.exe -m scripts.report_latency --count 12 --label lbrv3
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]
QUERY_REPEATS = 5


def train_recordings() -> list[dict[str, Any]]:
    with (ROOT / "data/splits/datased_polyphonic.csv").open(encoding="utf-8") as handle:
        train = {r["recording_id"] for r in csv.DictReader(handle) if r["split"] == "train"}
    with (ROOT / "data/manifests/datased_recordings.csv").open(encoding="utf-8") as handle:
        rows = [r for r in csv.DictReader(handle) if r["recording_id"] in train]
    return sorted(({"id": r["recording_id"], "duration_s": float(r["duration_s"]),
                    "path": ROOT / "data/raw/datased/extracted" / r["audio_relative_path"]}
                   for r in rows), key=lambda r: r["duration_s"])


def spread(rows: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    """Chọn `count` bản ghi rải đều theo độ dài (tất định, không ngẫu nhiên)."""
    if count >= len(rows):
        return rows
    step = (len(rows) - 1) / (count - 1)
    return [rows[round(i * step)] for i in range(count)]


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round(q * (len(ordered) - 1))))
    return ordered[index]


def summarise(values: list[float]) -> dict[str, float]:
    return {"n": len(values), "median": statistics.median(values), "p95": percentile(values, 0.95),
            "max": max(values)}


def container_memory(name: str) -> str | None:
    result = subprocess.run(["docker", "stats", "--no-stream", "--format", "{{.MemUsage}}", name],
                            capture_output=True, text=True, encoding="utf-8", check=False)
    return result.stdout.strip() or None


def measure(base_url: str, rows: list[dict[str, Any]], container: str | None) -> dict[str, Any]:
    uploads: list[dict[str, Any]] = []
    queries: list[float] = []
    with httpx.Client(base_url=base_url, timeout=900) as client:
        status = client.get("/api/v1/models/status").json()["data"]
        for row in rows:
            started = time.perf_counter()
            with row["path"].open("rb") as handle:
                response = client.post("/api/v1/audio/upload",
                                       files={"file": (row["path"].name, handle, "audio/wav")})
            elapsed = time.perf_counter() - started
            body = response.json()
            if not body.get("success") or body.get("meta", {}).get("duplicate"):
                uploads.append({"id": row["id"], "duration_s": row["duration_s"], "skipped": True})
                continue
            uploads.append({"id": row["id"], "duration_s": row["duration_s"],
                            "elapsed_s": elapsed, "rtf": elapsed / row["duration_s"],
                            "memory": container_memory(container) if container else None})
        body = {"question": "Bản ghi nào có tiếng xe?", "corpus": "upload", "mode": "hybrid",
                "language": "vi", "k": 5, "filters": {"classes_all": ["vehicle_pass_by"]}}
        for _ in range(QUERY_REPEATS):
            started = time.perf_counter()
            client.post("/api/v1/retrieval/query", json=body).raise_for_status()
            queries.append(time.perf_counter() - started)
    done = [u for u in uploads if not u.get("skipped")]
    if not done:
        raise RuntimeError("không có lần upload nào mới (mọi bản ghi đã có trong kho); dùng "
                           "demo_up.ps1 -ResetHistory rồi chạy lại")
    return {"status": {k: status.get(k) for k in ("served_run", "official", "device", "lbr_run",
                                                  "operating_point")},
            "uploads": uploads, "elapsed_s": summarise([u["elapsed_s"] for u in done]),
            "rtf": summarise([u["rtf"] for u in done]), "query_s": summarise(queries),
            "audio_duration_s": {"min": min(u["duration_s"] for u in done),
                                 "max": max(u["duration_s"] for u in done)}}


def render(result: dict[str, Any], label: str) -> str:
    e, r, q = result["elapsed_s"], result["rtf"], result["query_s"]
    st = result["status"]
    lines = [f"# Độ trễ demo `{label}` (bản ghi TRAIN)", "",
             "> Sinh bởi `scripts.report_latency`; chỉ upload TRAIN, không chấm metric.", "",
             f"Hệ phục vụ: `{st['served_run']}`, thiết bị `{st['device']}`, "
             f"LBR `{st['lbr_run']}` điểm `{st['operating_point']}`.", "",
             "| Đại lượng | n | Trung vị | p95 | Lớn nhất |", "|---|---:|---:|---:|---:|",
             f"| Tải lên + phân tích (s) | {e['n']} | {e['median']:.2f} | {e['p95']:.2f} | "
             f"{e['max']:.2f} |",
             f"| RTF (thời gian xử lý / độ dài âm thanh) | {r['n']} | {r['median']:.3f} | "
             f"{r['p95']:.3f} | {r['max']:.3f} |",
             f"| Truy vấn kết hợp (s) | {q['n']} | {q['median']:.3f} | {q['p95']:.3f} | "
             f"{q['max']:.3f} |", "",
             f"Độ dài âm thanh {result['audio_duration_s']['min']:.1f} đến "
             f"{result['audio_duration_s']['max']:.1f} s.", "",
             "| Bản ghi | Độ dài (s) | Xử lý (s) | RTF | Bộ nhớ container |",
             "|---|---:|---:|---:|---|"]
    for u in result["uploads"]:
        if u.get("skipped"):
            lines.append(f"| {u['id']} | {u['duration_s']:.1f} | bỏ qua (đã có) | — | — |")
        else:
            lines.append(f"| {u['id']} | {u['duration_s']:.1f} | {u['elapsed_s']:.2f} | "
                         f"{u['rtf']:.3f} | {u['memory'] or '—'} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8088")
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--label", default="lbrv3")
    parser.add_argument("--container", help="tên container suy luận để lấy RAM (docker stats)")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    result = measure(args.base_url, spread(train_recordings(), args.count), args.container)
    result |= {"label": args.label, "git": git_state(ROOT),
               "created_at": datetime.now(UTC).isoformat()}
    out = ROOT / "docs/measurements" / f"latency_{args.label}_{datetime.now(UTC):%Y%m%d}"
    out.with_suffix(".json").write_text(json.dumps(result, indent=1, ensure_ascii=False),
                                        encoding="utf-8")
    out.with_suffix(".md").write_text(render(result, args.label), encoding="utf-8")
    print(render(result, args.label))


if __name__ == "__main__":
    main()
