"""Đo độ nhất quán chú giải bằng các recording byte-identical của DataSED.

    .venv/Scripts/python.exe -m scripts.report_annotation_consistency

DataSED chứa các cặp recording **giống nhau từng byte** nhưng mang hai
`recording_id` khác nhau, và mỗi bản được chú giải riêng. Đó là một phép đo
agreement có sẵn: cùng một âm thanh, hai lần gán nhãn độc lập.

Con số này đặt **trần thực tế** cho mọi metric event-based. Nếu chính ground
truth bất đồng 12 giây trên một biên, thì collar 0.2 s của
[evaluation_protocol §3](../docs/evaluation_protocol.md) chặt hơn độ chính xác
của nhãn, và "lỗi" của model ở mức đó không phân biệt được với nhiễu nhãn.

Cỡ mẫu rất nhỏ (8 cặp). Đây là **tín hiệu cảnh báo**, không phải một nghiên cứu
agreement đầy đủ, và phải được báo cáo đúng như vậy.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data" / "manifests"
MEASUREMENTS = ROOT / "docs" / "measurements"
COLLAR_S = 0.2


def identical_pairs(recordings: pd.DataFrame) -> list[tuple[str, str]]:
    grouped = recordings.groupby("content_sha256")["recording_id"].apply(list)
    return [tuple(sorted(members)[:2]) for members in grouped if len(members) > 1]


def compare(events: pd.DataFrame, left: str, right: str) -> dict:
    """So hai chú giải của cùng một audio."""
    first = events[events["recording_id"] == left]
    second = events[events["recording_id"] == right]
    classes_first = sorted(first["class_id"])
    classes_second = sorted(second["class_id"])

    result = {
        "left": left,
        "right": right,
        "events_left": len(first),
        "events_right": len(second),
        "same_event_count": len(first) == len(second),
        "same_class_multiset": classes_first == classes_second,
        "classes_only_left": sorted(set(classes_first) - set(classes_second)),
        "classes_only_right": sorted(set(classes_second) - set(classes_first)),
    }
    if result["same_event_count"] and result["same_class_multiset"] and len(first):
        ordered_left = first.sort_values(["class_id", "onset_s"])
        ordered_right = second.sort_values(["class_id", "onset_s"])
        onset = (ordered_left["onset_s"].values - ordered_right["onset_s"].values)
        offset = (ordered_left["offset_s"].values - ordered_right["offset_s"].values)
        deltas = [abs(float(value)) for value in [*onset, *offset]]
        result.update(
            {
                "max_boundary_delta_s": max(deltas),
                "mean_boundary_delta_s": sum(deltas) / len(deltas),
                "boundaries_within_collar": sum(1 for value in deltas if value <= COLLAR_S),
                "boundaries_total": len(deltas),
            }
        )
    return result


def build_report(results: list[dict], collar: float) -> str:
    comparable = [item for item in results if "max_boundary_delta_s" in item]
    within = sum(item["boundaries_within_collar"] for item in comparable)
    total = sum(item["boundaries_total"] for item in comparable)
    class_disagreements = [item for item in results if not item["same_class_multiset"]]

    lines = [
        "# Độ nhất quán chú giải — đo trên recording byte-identical",
        "",
        f"**Sinh tự động** `scripts.report_annotation_consistency` — "
        f"{datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "## Phương pháp",
        "",
        "DataSED chứa các cặp recording giống nhau **từng byte** nhưng mang hai "
        "`recording_id`, và mỗi bản được chú giải riêng. So hai chú giải đó cho ra "
        "một phép đo agreement mà không tốn công gán nhãn nào.",
        "",
        f"> ⚠️ **Cỡ mẫu {len(results)} cặp.** Đây là tín hiệu cảnh báo, không phải một "
        "nghiên cứu agreement. Không dùng con số này làm ước lượng điểm cho bất kỳ "
        "đại lượng nào.",
        "",
        "## Tổng hợp",
        "",
        "| | |",
        "|---|---:|",
        f"| Cặp byte-identical | {len(results)} |",
        f"| Cặp **bất đồng về lớp hoặc số event** | **{len(class_disagreements)}** |",
        f"| Cặp so được biên | {len(comparable)} |",
        f"| Biên nằm trong collar {collar} s | {within} / {total} |",
        "",
    ]
    if comparable:
        worst = max(comparable, key=lambda item: item["max_boundary_delta_s"])
        lines += [
            f"Lệch biên lớn nhất: **{worst['max_boundary_delta_s']:.2f} s** "
            f"(`{worst['left']}` vs `{worst['right']}`).",
            "",
        ]

    lines += [
        "## Chi tiết từng cặp",
        "",
        "| Cặp | Event | Cùng lớp | Lệch biên lớn nhất | Biên trong collar |",
        "|---|---|---|---:|---:|",
    ]
    for item in results:
        counts = f"{item['events_left']} / {item['events_right']}"
        same = "✅" if item["same_class_multiset"] else "❌"
        if "max_boundary_delta_s" in item:
            delta = f"{item['max_boundary_delta_s']:.2f} s"
            collar_cell = f"{item['boundaries_within_collar']}/{item['boundaries_total']}"
        else:
            delta = collar_cell = "—"
        lines.append(
            f"| `{item['left']}` / `{item['right']}` | {counts} | {same} "
            f"| {delta} | {collar_cell} |"
        )

    if class_disagreements:
        lines += ["", "## Bất đồng về lớp", ""]
        for item in class_disagreements:
            lines += [
                f"### `{item['left']}` vs `{item['right']}`",
                "",
                f"- Chỉ có ở `{item['left']}`: "
                f"{', '.join(f'`{value}`' for value in item['classes_only_left']) or '—'}",
                f"- Chỉ có ở `{item['right']}`: "
                f"{', '.join(f'`{value}`' for value in item['classes_only_right']) or '—'}",
                "",
            ]

    lines += [
        "## Hệ quả",
        "",
        f"1. **Collar {collar} s chặt hơn độ chính xác của nhãn.** Chỉ {within}/{total} "
        "biên của hai lần gán nhãn trên **cùng một audio** nằm trong khoảng đó. Sai số "
        "của model ở mức này không phân biệt được với nhiễu nhãn.",
        "2. **Bất đồng về lớp là bằng chứng trực tiếp cho cặp dễ nhầm**, lấy từ chính "
        "ground truth chứ không từ ma trận nhầm của model. Nó nên đi vào "
        "[taxonomy.md §8](../taxonomy.md) như một nguồn độc lập.",
        "3. Khi báo event-based F1 và PSDS, phải nêu con số này trong phần Hạn chế. "
        "Một cải thiện nhỏ hơn mức bất đồng của chính nhãn thì không tuyên bố được.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    recordings = pd.read_csv(MANIFESTS / "datased_recordings.csv")
    events = pd.read_csv(ROOT / "data" / "annotations" / "datased_polyphonic_events.csv")

    pairs = identical_pairs(recordings)
    if not pairs:
        print("Không có cặp byte-identical nào: không đo được agreement theo cách này.")
        return
    results = [compare(events, left, right) for left, right in pairs]

    MEASUREMENTS.mkdir(parents=True, exist_ok=True)
    destination = (
        MEASUREMENTS / f"annotation_consistency_{datetime.now(UTC).strftime('%Y%m%d')}.md"
    )
    destination.write_text(build_report(results, COLLAR_S) + "\n", encoding="utf-8")
    disagreeing = sum(1 for item in results if not item["same_class_multiset"])
    print(f"{len(pairs)} cặp byte-identical; {disagreeing} cặp bất đồng lớp/số event")
    print(f"wrote {destination}")


if __name__ == "__main__":
    main()
