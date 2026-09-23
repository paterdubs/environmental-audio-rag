"""Test cho script sinh measurement của cổng D3.

Script này sinh ra số đi thẳng vào khóa luận, nên nó phải trượt khi artifact
thiếu thay vì im lặng báo 0.
"""

import json

import pytest

from scripts.report_duplicates import (
    alarm_section,
    build_report,
    calibration_section,
    coverage_section,
    decision_section,
    group_stats,
    read_json,
)

AUDIT = {
    "thresholds": {"duplicate_min": 0.95, "review_min": 0.85, "min_overlap_s": 3.0},
    "fingerprint_sha256": "a" * 64,
    "standardizer_sha256": "b" * 64,
    "files": {"datasec": 5048, "datased": 717},
    "pairs_by_tier": {"T1": 24, "T2": 24, "T3": 45191},
    "groups": 30,
    "cross_dataset_groups": 2,
    "review_pairs": 87,
    "review_queue_cross_dataset": 11,
    "split_cohesion_pairs": 1731,
    "unreachable_by_tier3": {"datasec": ["datasec:x.wav"] * 464, "datased": []},
    "alarm": {
        "leaked_files": 0,
        "total_files": 5048,
        "ratio": 0.0,
        "band": "clean",
        "action": "RQ1 hợp lệ như thiết kế",
        "pending_review_groups": 87,
        "notes": ["87 nhóm ở dải review chưa có quyết định người"],
    },
    "cross_dataset_exclusions_pending_split": True,
}

CALIBRATION = {
    "fingerprint_sha256": "a" * 64,
    "standardizer_sha256": "b" * 64,
    "seed": 20260922,
    "positives": {"label": "positives", "count": 24, "p99": 1.0},
    "negatives": {"label": "negatives", "count": 5000, "p99": 0.81},
    "separation": {
        "positive_min": 1.0,
        "negative_max": 0.9205,
        "negative_p999": 0.8692,
        "separated": True,
    },
    "default_thresholds": {"duplicate_min": 0.95, "review_min": 0.85, "min_overlap_s": 3.0},
    "negative_above_review_min": 11,
    "negative_above_duplicate_min": 0,
}


def _rows(*groups: tuple[str, int, bool]) -> list[dict]:
    rows = []
    for group_id, size, cross in groups:
        for index in range(size):
            rows.append(
                {
                    "group_id": group_id,
                    "file_id": f"datased:{group_id}-{index}.wav",
                    "cross_dataset": str(cross).lower(),
                    "needs_review": "false",
                }
            )
    return rows


def test_group_stats_counts_groups_not_rows() -> None:
    stats = group_stats(_rows(("dup-0001", 3, False), ("dup-0002", 2, True)))

    assert stats == {
        "groups": 2,
        "members": 5,
        "sizes": {2: 1, 3: 1},
        "cross": 1,
        "largest": 3,
    }


def test_group_stats_handles_no_groups() -> None:
    stats = group_stats([])
    assert stats["groups"] == 0 and stats["largest"] == 0


def test_read_json_fails_loudly_when_artifact_missing(tmp_path) -> None:
    """Thiếu artifact phải dừng, không được sinh báo cáo toàn số 0."""
    with pytest.raises(SystemExit) as error:
        read_json(tmp_path / "khong-ton-tai.json")

    assert "find_duplicates" in str(error.value)


def test_alarm_section_marks_result_as_inconclusive_before_split() -> None:
    text = "\n".join(alarm_section(AUDIT))

    assert "chưa kết luận được" in text
    assert "0.000%" in text


def test_alarm_section_states_the_band_action() -> None:
    material = {**AUDIT, "alarm": {**AUDIT["alarm"], "band": "material", "ratio": 0.02}}
    assert "chạy lại nhánh C" in "\n".join(alarm_section(material))


def test_alarm_section_escalates_invalidating_band() -> None:
    broken = {**AUDIT, "alarm": {**AUDIT["alarm"], "band": "invalidating", "ratio": 0.08}}
    text = "\n".join(alarm_section(broken))

    assert "không còn diễn giải được" in text


def test_alarm_section_carries_pending_review_note() -> None:
    assert "review chưa có quyết định" in "\n".join(alarm_section(AUDIT))


def test_calibration_section_reports_separation_verdict() -> None:
    text = "\n".join(calibration_section(CALIBRATION))

    assert "**có**" in text
    assert "**0** / 5000" in text  # không negative nào vượt duplicate_min


def test_calibration_section_says_not_separated_when_it_is_not() -> None:
    failing = {
        **CALIBRATION,
        "separation": {**CALIBRATION["separation"], "separated": False},
    }
    assert "**KHÔNG**" in "\n".join(calibration_section(failing))


def test_coverage_section_computes_tier3_reach() -> None:
    text = "\n".join(coverage_section(AUDIT))

    assert "| `datasec` | 5048 | 464 | 90.8% |" in text
    assert "| `datased` | 717 | 0 | 100.0% |" in text


def test_build_report_contains_every_required_section() -> None:
    report = build_report(AUDIT, CALIBRATION, group_stats(_rows(("dup-0001", 2, True))))

    for heading in (
        "## Cấu hình đã dùng",
        "## Cặp khớp theo tầng",
        "## Nhóm trùng lặp",
        "## Cặp ở dải review",
        "## Ngưỡng báo động",
        "## Hiệu chuẩn ngưỡng T3",
        "## Độ phủ của cổng",
    ):
        assert heading in report


def test_build_report_records_both_checksums() -> None:
    report = build_report(AUDIT, CALIBRATION, group_stats([]))

    assert "aaaaaaaaaaaaaaaa" in report  # fingerprint
    assert "bbbbbbbbbbbbbbbb" in report  # standardizer


def test_build_report_is_valid_when_nothing_was_found() -> None:
    empty = {
        **AUDIT,
        "groups": 0,
        "cross_dataset_groups": 0,
        "review_pairs": 0,
        "review_queue_cross_dataset": 0,
        "split_cohesion_pairs": 0,
        "pairs_by_tier": {},
    }
    report = build_report(empty, CALIBRATION, group_stats([]))

    assert "(không có nhóm)" in report
    assert "| T1 | 0 |" in report


def test_report_json_round_trips(tmp_path) -> None:
    path = tmp_path / "audit.json"
    path.write_text(json.dumps(AUDIT, ensure_ascii=False), encoding="utf-8")

    assert read_json(path)["groups"] == 30


# ---------- nhật ký quyết định ----------


def _sheet(pair_id: str, decision: str, note: str = "", similarity: str = "0.90") -> dict:
    return {
        "pair_id": pair_id,
        "similarity": similarity,
        "overlap_s": "8.5",
        "pretraining_file_id": "datasec:DATASEC/Train/Train-0031.wav",
        "benchmark_file_id": "datased:SED_wav/S-0241.wav",
        "decision": decision,
        "decided_by": "patphh",
        "note": note,
    }


def test_decision_section_prompts_when_worksheet_absent() -> None:
    text = "\n".join(decision_section([], AUDIT))

    assert "build_review_worksheet" in text


def test_decision_section_counts_each_verdict() -> None:
    rows = [_sheet("rev-001", "duplicate"), _sheet("rev-002", "distinct")]
    text = "\n".join(decision_section(rows, {**AUDIT, "review_queue_cross_dataset": 2}))

    assert "| `duplicate` | 1 |" in text
    assert "| `distinct` | 1 |" in text
    assert "Người duyệt: patphh" in text


def test_decision_section_flags_unfinished_review() -> None:
    rows = [_sheet("rev-001", "duplicate"), _sheet("rev-002", "")]
    text = "\n".join(decision_section(rows, {**AUDIT, "review_queue_cross_dataset": 2}))

    assert "Còn **1** cặp chưa có quyết định" in text


def test_decision_log_carries_the_note_verbatim() -> None:
    """Ghi chú giải thích vì sao một cặp 0.89 là cùng nguồn còn 0.91 thì không."""
    rows = [_sheet("rev-001", "distinct", "audio thứ hai là trực thăng")]
    text = "\n".join(decision_section(rows, {**AUDIT, "review_queue_cross_dataset": 1}))

    assert "audio thứ hai là trực thăng" in text


def test_decision_log_sorts_by_similarity_descending() -> None:
    rows = [
        _sheet("rev-002", "distinct", similarity="0.86"),
        _sheet("rev-001", "duplicate", similarity="0.94"),
    ]
    text = "\n".join(decision_section(rows, {**AUDIT, "review_queue_cross_dataset": 2}))

    assert text.index("rev-001") < text.index("rev-002")


def test_empty_note_renders_as_dash() -> None:
    rows = [_sheet("rev-001", "duplicate", "")]
    text = "\n".join(decision_section(rows, {**AUDIT, "review_queue_cross_dataset": 1}))

    assert "| `duplicate` | — |" in text
