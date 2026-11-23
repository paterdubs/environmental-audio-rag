"""Field test định tính: clip tự thu đi qua demo đang chạy, hai người nghe chấm độc lập.

Không có nhãn chuẩn cho clip tự thu, nên không tính event-F1. Hai người nghe từng sự kiện hệ thống
phát hiện và chấm đúng/sai, rồi ghi số sự kiện nghe thấy mà hệ thống bỏ sót. Kết quả là độ chính
xác theo người nghe, mức đồng thuận giữa hai người (Cohen kappa) và số sự kiện bị bỏ sót.

Hai bước (clip KHÔNG bao giờ được commit: có thể chứa giọng nói, chỉ commit phiếu và kết quả):

    .venv/Scripts/python.exe -m scripts.field_test run --clips <thư mục clip>
    # hai người điền cột `danh_gia` (dung | sai | khong_ro) và dòng `bo_sot` ở phiếu A và phiếu B
    .venv/Scripts/python.exe -m scripts.field_test summarise --sheet-a <A.csv> --sheet-b <B.csv>
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from ml.dataops.textio import read_csv_rows
from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "measurements"
ALLOWED = (".wav", ".flac", ".ogg", ".mp3")
JUDGEMENTS = ("dung", "sai", "khong_ro")
COLUMNS = ["clip", "loai_dong", "event_id", "class_id", "onset_s", "offset_s", "score",
           "danh_gia", "so_bo_sot", "ghi_chu"]
GUIDE = ("Chấm `danh_gia` cho từng dòng phat_hien: dung = nghe thấy đúng loại âm thanh đó trong "
         "khoảng onset–offset; sai = không có hoặc là âm thanh khác; khong_ro = không chắc. "
         "Dòng bo_sot: điền `so_bo_sot` (số sự kiện nghe thấy mà hệ thống không phát hiện) và "
         "`ghi_chu`. Hai người điền độc lập, không trao đổi trước khi nộp.")


def prepare_clips(source: Path, workdir: Path) -> list[tuple[str, Path]]:
    """Đặt tên ẩn danh clip_NN; đổi sang WAV khi định dạng gốc (m4a, aac...) không được nhận."""
    files = sorted(p for p in source.iterdir() if p.is_file())
    if not files:
        raise SystemExit(f"Không có clip nào trong {source}")
    prepared = []
    for index, path in enumerate(files, 1):
        clip_id = f"clip_{index:02d}"
        if path.suffix.lower() in ALLOWED:
            target = workdir / f"{clip_id}{path.suffix.lower()}"
            shutil.copyfile(path, target)
        else:
            target = workdir / f"{clip_id}.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-ac", "1",
                            str(target)], check=True)
        prepared.append((clip_id, target))
    return prepared


def analyse(client: httpx.Client, path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        response = client.post("/api/v1/audio/upload", files={"file": (path.name, handle)})
    body = response.json()
    if not body.get("success"):
        raise RuntimeError(f"{path.name}: {body.get('error')}")
    recording_id = body["data"]["recording_id"]
    timeline = client.get(f"/api/v1/recordings/{recording_id}/timeline").json()["data"]
    captions = client.get(f"/api/v1/recordings/{recording_id}/caption").json()["data"]
    return {"recording_id": recording_id, "duration_s": timeline["duration_s"],
            "events": timeline["events"], "captions": captions,
            "duplicate": bool(body.get("meta", {}).get("duplicate"))}


def sheet_rows(clip_id: str, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [{"clip": clip_id, "loai_dong": "phat_hien", "event_id": e["event_id"],
             "class_id": e["class_id"], "onset_s": f"{e['onset_s']:.2f}",
             "offset_s": f"{e['offset_s']:.2f}", "score": f"{e['score']:.3f}",
             "danh_gia": "", "so_bo_sot": "", "ghi_chu": ""} for e in events]
    rows.append({"clip": clip_id, "loai_dong": "bo_sot", "event_id": "", "class_id": "",
                 "onset_s": "", "offset_s": "", "score": "", "danh_gia": "", "so_bo_sot": "",
                 "ghi_chu": ""})
    return rows


def write_sheet(path: Path, rows: list[dict[str, Any]]) -> None:
    import csv

    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def cohen_kappa(pairs: list[tuple[str, str]]) -> float | None:
    """Kappa của hai người chấm trên các dòng cả hai đều chấm dung/sai; None nếu không xác định."""
    n = len(pairs)
    if n == 0:
        return None
    observed = sum(a == b for a, b in pairs) / n
    labels = {label for pair in pairs for label in pair}
    expected = sum((sum(a == k for a, _ in pairs) / n) * (sum(b == k for _, b in pairs) / n)
                   for k in labels)
    if expected == 1.0:
        return None
    return (observed - expected) / (1.0 - expected)


def read_sheet(path: Path) -> list[dict[str, str]]:
    rows, _ = read_csv_rows(path)
    for row in rows:
        row["danh_gia"] = (row.get("danh_gia") or "").strip().lower()
        bad = row["danh_gia"] not in ("", *JUDGEMENTS)
        if bad and row["loai_dong"] == "phat_hien":
            raise ValueError(f"{path.name}: danh_gia không hợp lệ ở {row['clip']} "
                             f"{row['event_id']}: {row['danh_gia']!r} (dung | sai | khong_ro)")
    return rows


def rater_stats(rows: list[dict[str, str]]) -> dict[str, Any]:
    detected = [r for r in rows if r["loai_dong"] == "phat_hien"]
    counts = {j: sum(r["danh_gia"] == j for r in detected) for j in JUDGEMENTS}
    unrated = sum(not r["danh_gia"] for r in detected)
    decided = counts["dung"] + counts["sai"]
    missed = sum(int(r["so_bo_sot"] or 0) for r in rows if r["loai_dong"] == "bo_sot")
    return {"events": len(detected), "unrated": unrated, **counts,
            "precision": counts["dung"] / decided if decided else None, "missed": missed}


def summarise(rows_a: list[dict[str, str]], rows_b: list[dict[str, str]]) -> dict[str, Any]:
    key = lambda r: (r["clip"], r["event_id"])  # noqa: E731
    b_by_key = {key(r): r for r in rows_b if r["loai_dong"] == "phat_hien"}
    both, per_class = [], defaultdict(lambda: [0, 0])
    for r in rows_a:
        if r["loai_dong"] != "phat_hien":
            continue
        other = b_by_key.get(key(r))
        if other and r["danh_gia"] in ("dung", "sai") and other["danh_gia"] in ("dung", "sai"):
            both.append((r["danh_gia"], other["danh_gia"]))
            per_class[r["class_id"]][0] += r["danh_gia"] == "dung" and other["danh_gia"] == "dung"
            per_class[r["class_id"]][1] += 1
    agree = sum(a == b for a, b in both)
    return {"rater_a": rater_stats(rows_a), "rater_b": rater_stats(rows_b),
            "agreement": {"n": len(both), "agree": agree,
                          "rate": agree / len(both) if both else None,
                          "kappa": cohen_kappa(both),
                          "both_correct": sum(a == b == "dung" for a, b in both)},
            "per_class_both_correct": {k: {"both_correct": v[0], "n": v[1]}
                                       for k, v in sorted(per_class.items())}}


def render(result: dict[str, Any]) -> str:
    def pct(value: float | None) -> str:
        return "—" if value is None else f"{value:.3f}"

    a, b, g = result["rater_a"], result["rater_b"], result["agreement"]
    lines = ["# Field test trên clip tự thu", "",
             "> Sinh bởi `scripts.field_test summarise`; chấm tay, không có nhãn chuẩn.", "",
             "| Người nghe | Sự kiện | Đúng | Sai | Không rõ | Chưa chấm | Độ chính xác | Bỏ sót |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name, s in (("A", a), ("B", b)):
        lines.append(f"| {name} | {s['events']} | {s['dung']} | {s['sai']} | {s['khong_ro']} | "
                     f"{s['unrated']} | {pct(s['precision'])} | {s['missed']} |")
    lines += ["", f"Đồng thuận trên {g['n']} sự kiện cả hai cùng chấm đúng/sai: {g['agree']} "
              f"({pct(g['rate'])}), kappa {pct(g['kappa'])}; cả hai cùng chấm đúng: "
              f"{g['both_correct']}.", "", "| Lớp | Cả hai chấm đúng | Số sự kiện |",
              "|---|---:|---:|"]
    for name, v in result["per_class_both_correct"].items():
        lines.append(f"| {name} | {v['both_correct']} | {v['n']} |")
    return "\n".join(lines) + "\n"


def cmd_run(args: argparse.Namespace) -> None:
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    folder = OUT / f"field_test_{stamp}"
    folder.mkdir(parents=True, exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory() as tmp, httpx.Client(base_url=args.base_url,
                                                            timeout=900) as client:
        status = client.get("/api/v1/models/status").json()["data"]
        for clip_id, path in prepare_clips(args.clips, Path(tmp)):
            results.append({"clip": clip_id, **analyse(client, path)})
            print(f"{clip_id}: {len(results[-1]['events'])} sự kiện")
    rows = [row for r in results for row in sheet_rows(r["clip"], r["events"])]
    for name in ("A", "B"):
        write_sheet(folder / f"phieu_cham_{name}.csv", rows)
    (folder / "ket_qua_he_thong.json").write_text(json.dumps(
        {"status": {k: status.get(k) for k in ("served_run", "official", "lbr_run",
                                               "operating_point")},
         "clips": results, "guide": GUIDE, "git": git_state(ROOT),
         "created_at": datetime.now(UTC).isoformat()}, indent=1, ensure_ascii=False),
        encoding="utf-8")
    print(f"Đã ghi {folder} (2 phiếu chấm + kết quả hệ thống). {GUIDE}")


def cmd_summarise(args: argparse.Namespace) -> None:
    result = summarise(read_sheet(args.sheet_a), read_sheet(args.sheet_b))
    result["git"] = git_state(ROOT)
    result["created_at"] = datetime.now(UTC).isoformat()
    stem = OUT / f"field_test_{datetime.now(UTC):%Y%m%d}_summary"
    stem.with_suffix(".json").write_text(json.dumps(result, indent=1, ensure_ascii=False),
                                         encoding="utf-8")
    stem.with_suffix(".md").write_text(render(result), encoding="utf-8")
    print(render(result))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--clips", type=Path, required=True)
    run.add_argument("--base-url", default="http://localhost:8088")
    run.set_defaults(func=cmd_run)
    summary = sub.add_parser("summarise")
    summary.add_argument("--sheet-a", type=Path, required=True)
    summary.add_argument("--sheet-b", type=Path, required=True)
    summary.set_defaults(func=cmd_summarise)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
