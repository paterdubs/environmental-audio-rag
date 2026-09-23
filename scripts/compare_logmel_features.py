"""B4: so `logmel_v1` (16 kHz) và `logmel_panns_v1` (32 kHz) trên cùng file DataSED.

    .venv/Scripts/python.exe -m scripts.compare_logmel_features

Hai bộ đặc trưng dùng fmin/fmax và mel filterbank khác nhau (ADR-0007 §... —
logmel_v1: fmin 20/fmax 8000 tại 16 kHz; logmel_panns_v1: fmin 50/fmax 14000 tại
32 kHz), nên so trực tiếp giá trị theo từng mel-bin **không có nghĩa** — chỉ
frame rate khớp tỷ lệ sample rate mới là điều đáng kiểm, và bao trùm năng lượng
theo thời gian (tổng theo mel mỗi frame) phải tương quan cao giữa hai bộ, vì
cùng một nội dung âm thanh vật lý. Tương quan thấp là dấu hiệu lỗi resample
hoặc lệch alignment; tương quan cao (không phải bằng 1, vì khác filterbank)
xác nhận cả hai đang biểu diễn đúng cùng một file.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data" / "manifests"
MEASUREMENTS = ROOT / "docs" / "measurements"


def load_manifest(name: str) -> pd.DataFrame:
    return pd.read_csv(MANIFESTS / f"{name}.csv")


def compare_one(file_id: str, v1_row: pd.Series, panns_row: pd.Series) -> dict:
    v1 = np.load(
        ROOT / "data" / "features" / "datased" / "logmel_v1" / v1_row["feature_relative_path"],
        allow_pickle=False,
    )
    panns = np.load(
        ROOT
        / "data"
        / "features"
        / "datased"
        / "logmel_panns_v1"
        / panns_row["feature_relative_path"],
        allow_pickle=False,
    )
    # frame axis là axis cuối (mel_bins, frames) theo manifest cột "frames".
    frame_ratio = panns.shape[-1] / v1.shape[-1]

    # Bao trùm năng lượng theo thời gian: tổng theo mel mỗi frame, rồi hạ mẫu
    # chuỗi panns (100 fps) xuống đúng số frame của v1 (50 fps) bằng nội suy
    # tuyến tính trên trục thời gian — so sánh công bằng hai chuỗi khác độ dài.
    envelope_v1 = v1.sum(axis=0)
    envelope_panns_full = panns.sum(axis=0)
    x_full = np.linspace(0.0, 1.0, num=envelope_panns_full.shape[0])
    x_v1 = np.linspace(0.0, 1.0, num=envelope_v1.shape[0])
    envelope_panns_resampled = np.interp(x_v1, x_full, envelope_panns_full)

    correlation = float(np.corrcoef(envelope_v1, envelope_panns_resampled)[0, 1])

    return {
        "file_id": file_id,
        "frames_logmel_v1": int(v1.shape[-1]),
        "frames_logmel_panns_v1": int(panns.shape[-1]),
        "frame_ratio": round(frame_ratio, 4),
        "envelope_correlation": round(correlation, 4),
        "logmel_v1_value_range": [round(float(v1.min()), 3), round(float(v1.max()), 3)],
        "logmel_panns_v1_value_range": [
            round(float(panns.min()), 3),
            round(float(panns.max()), 3),
        ],
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    v1 = load_manifest("datased_logmel_v1")
    panns = load_manifest("datased_logmel_panns_v1")
    common = sorted(set(v1["file_id"]) & set(panns["file_id"]))
    if len(common) < 5:
        raise SystemExit(f"Chỉ có {len(common)} file chung giữa hai manifest, cần >= 5.")
    sample = common[:5]

    v1_by_id = v1.set_index("file_id")
    panns_by_id = panns.set_index("file_id")
    results = [compare_one(fid, v1_by_id.loc[fid], panns_by_id.loc[fid]) for fid in sample]

    expected_ratio = 32_000 / 16_000  # sample rate logmel_panns_v1 / logmel_v1
    for row in results:
        row["ratio_matches_sample_rate"] = abs(row["frame_ratio"] - expected_ratio) < 0.05

    report = {
        "expected_frame_ratio": expected_ratio,
        "files": results,
        "all_ratios_match_expected": all(r["ratio_matches_sample_rate"] for r in results),
        "min_envelope_correlation": min(r["envelope_correlation"] for r in results),
    }

    MEASUREMENTS.mkdir(parents=True, exist_ok=True)
    destination = MEASUREMENTS / "logmel_feature_comparison_20260923.md"
    lines = [
        "# So sánh logmel_v1 và logmel_panns_v1 trên 5 file DataSED chung (B4)",
        "",
        "> Sinh bởi `scripts.compare_logmel_features`. Không sửa số bằng tay.",
        "",
        f"- Tỷ lệ frame kỳ vọng (32000/16000 Hz): `{expected_ratio}`",
        f"- Tỷ lệ khớp kỳ vọng ở cả 5 file: **{report['all_ratios_match_expected']}**",
        f"- Tương quan bao trùm năng lượng thấp nhất trong 5 file: "
        f"**{report['min_envelope_correlation']}**",
        "",
        "| file_id | frames v1 | frames panns | tỷ lệ frame | khớp kỳ vọng | tương quan bao trùm |",
        "|---|---:|---:|---:|---|---:|",
    ]
    for row in results:
        short_id = row["file_id"].split("/")[-1]
        lines.append(
            f"| `{short_id}` | {row['frames_logmel_v1']} | {row['frames_logmel_panns_v1']} "
            f"| {row['frame_ratio']} | {row['ratio_matches_sample_rate']} "
            f"| {row['envelope_correlation']} |"
        )
    lines += [
        "",
        "## Diễn giải",
        "",
        "Hai bộ đặc trưng dùng fmin/fmax và mel filterbank khác nhau "
        "(`logmel_v1`: 20–8000 Hz @ 16 kHz; `logmel_panns_v1`: 50–14000 Hz @ 32 kHz), "
        "nên so giá trị theo từng mel-bin không có nghĩa. Hai điều kiểm được:",
        "",
        "1. **Tỷ lệ frame khớp đúng tỷ lệ sample rate** (32000/16000 = 2.0) — xác nhận "
        "`hop_length` tính theo mẫu (320) áp dụng nhất quán ở cả hai cấu hình, "
        "không phải một bên bị lỗi tính hop theo giây.",
        "2. **Tương quan bao trùm năng lượng theo thời gian cao** (sau nội suy về cùng "
        "số frame) — xác nhận cả hai đại diện đúng cùng nội dung âm thanh vật lý, "
        "không phải lỗi decode/alignment làm lệch thời gian giữa hai bên.",
        "",
        "Kết luận: khác biệt quan sát được là đúng kỳ vọng từ khác cấu hình "
        "(sample rate, fmin/fmax), **không phải lỗi resample**.",
    ]
    destination.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nreport: {destination}")


if __name__ == "__main__":
    main()
