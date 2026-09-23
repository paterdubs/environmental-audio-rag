import pytest

from scripts.apply_review_decisions import to_exclusions, validate
from scripts.build_review_worksheet import audio_path, build_rows


def _queue_row(similarity: str = "0.90") -> dict:
    return {
        "left_file_id": "datasec:DATASEC/Train/Train-0031.wav",
        "right_file_id": "datased:SED_wav/S-0241.wav",
        "tier": "T3",
        "similarity": similarity,
        "overlap_s": "8.500",
        "verdict": "review",
    }


# ---------- sinh phiếu ----------


def test_worksheet_rows_sort_by_similarity_descending() -> None:
    rows = build_rows([_queue_row("0.86"), _queue_row("0.94"), _queue_row("0.90")])

    assert [row["similarity"] for row in rows] == ["0.94", "0.90", "0.86"]
    assert [row["pair_id"] for row in rows] == ["rev-001", "rev-002", "rev-003"]


def test_worksheet_leaves_decision_columns_empty() -> None:
    row = build_rows([_queue_row()])[0]

    assert row["decision"] == "" and row["decided_by"] == "" and row["note"] == ""


def test_audio_path_resolves_dataset_prefix() -> None:
    path = audio_path("datasec:DATASEC/Train/Train-0031.wav")

    assert path.parts[-4:] == ("extracted", "DATASEC", "Train", "Train-0031.wav")


# ---------- áp quyết định ----------


def _sheet_row(pair_id: str, decision: str = "", decided_by: str = "") -> dict:
    return {
        "pair_id": pair_id,
        "pretraining_file_id": f"datasec:{pair_id}.wav",
        "benchmark_file_id": f"datased:{pair_id}.wav",
        "decision": decision,
        "decided_by": decided_by,
        "note": "",
    }


def test_empty_decisions_are_reported_as_pending_not_silently_skipped() -> None:
    decided, pending = validate(
        [_sheet_row("rev-001"), _sheet_row("rev-002", "duplicate", "patph")]
    )

    assert [row["pair_id"] for row in decided] == ["rev-002"]
    assert pending == ["rev-001"]


def test_unknown_decision_value_is_fatal() -> None:
    with pytest.raises(SystemExit, match="không hợp lệ"):
        validate([_sheet_row("rev-001", "maybe", "patph")])


def test_decision_without_a_name_is_fatal() -> None:
    """Một quyết định không ai ký tên thì không phải quyết định của người."""
    with pytest.raises(SystemExit, match="decided_by"):
        validate([_sheet_row("rev-001", "duplicate")])


def test_decision_values_are_case_insensitive() -> None:
    decided, _ = validate([_sheet_row("rev-001", "  Duplicate  ", "patph")])
    assert decided[0]["decision"] == "duplicate"


def test_duplicate_decision_excludes_the_pretraining_clip() -> None:
    exclusions = to_exclusions(validate([_sheet_row("rev-001", "duplicate", "patph")])[0])

    assert [item.file_id for item in exclusions] == ["datasec:rev-001.wav"]
    assert exclusions[0].reason_code == "exclude_cross_dataset_leak"


def test_unsure_is_treated_conservatively_as_exclusion() -> None:
    """Loại nhầm một clip rẻ hơn nhiều so với giữ lại một rò rỉ."""
    exclusions = to_exclusions(validate([_sheet_row("rev-001", "unsure", "patph")])[0])

    assert len(exclusions) == 1
    assert exclusions[0].reason_code == "exclude_cross_dataset_unsure"


def test_distinct_decision_excludes_nothing() -> None:
    assert to_exclusions(validate([_sheet_row("rev-001", "distinct", "patph")])[0]) == []


def test_human_prefix_is_added_once() -> None:
    plain = to_exclusions(validate([_sheet_row("rev-001", "duplicate", "patph")])[0])
    prefixed = to_exclusions(validate([_sheet_row("rev-002", "duplicate", "human:patph")])[0])

    assert plain[0].decided_by == "human:patph"
    assert prefixed[0].decided_by == "human:patph"
