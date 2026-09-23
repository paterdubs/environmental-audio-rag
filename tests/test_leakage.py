import pytest

from ml.dataops.leakage import (
    check_class_coverage,
    check_cross_dataset_exclusions_applied,
    check_duplicate_pairs_within_split,
    check_group_integrity,
    check_hash_integrity,
    check_pretraining_exclusions_absent,
    run_all,
)

ASSIGNMENT = {
    "datased:S-0001": "train",
    "datased:S-0002": "train",
    "datased:S-0003": "validation",
    "datased:S-0004": "test",
}


def test_group_integrity_passes_when_group_stays_in_one_split() -> None:
    result = check_group_integrity(
        ASSIGNMENT, {"datased:S-0001": "g1", "datased:S-0002": "g1"}
    )
    assert result.passed and result.violations == []


def test_group_integrity_names_the_offending_group() -> None:
    result = check_group_integrity(
        ASSIGNMENT, {"datased:S-0001": "g1", "datased:S-0003": "g1"}
    )

    assert not result.passed
    assert result.violations == ["group=g1 splits=['train', 'validation']"]


def test_hash_integrity_catches_same_bytes_in_two_splits() -> None:
    result = check_hash_integrity(
        ASSIGNMENT, {"datased:S-0002": "abc", "datased:S-0004": "abc"}
    )

    assert not result.passed
    assert "sha256=abc" in result.violations[0]


def test_duplicate_pairs_within_split_flags_cross_split_group() -> None:
    result = check_duplicate_pairs_within_split(
        ASSIGNMENT, {"dup-0001": ["datased:S-0001", "datased:S-0004"]}
    )
    assert not result.passed


def test_duplicate_pairs_ignores_members_outside_this_dataset() -> None:
    """Thành viên DataSEC không có split của DataSED — đó là việc của kiểm 5."""
    result = check_duplicate_pairs_within_split(
        ASSIGNMENT, {"dup-0001": ["datased:S-0001", "datasec:Bells/Bells-0001.wav"]}
    )
    assert result.passed


def test_class_coverage_reports_every_missing_pair() -> None:
    labels = {
        "datased:S-0001": ["birds"],
        "datased:S-0002": ["birds"],
        "datased:S-0003": ["birds"],
        "datased:S-0004": ["birds"],
    }
    result = check_class_coverage(ASSIGNMENT, labels, expected_classes=["birds", "horn"])

    assert not result.passed
    assert len(result.violations) == 3  # horn vắng ở cả ba split


def test_class_coverage_honours_declared_exceptions() -> None:
    labels = {item: ["birds"] for item in ASSIGNMENT}
    result = check_class_coverage(
        ASSIGNMENT, labels, expected_classes=["birds", "horn"], allowed_empty=["horn"]
    )

    assert result.passed
    assert "horn" in result.note


def test_cross_dataset_exclusion_required_when_group_touches_holdout() -> None:
    groups = {"dup-0001": ["datasec:clip.wav", "datased:S-0004"]}

    failing = check_cross_dataset_exclusions_applied(ASSIGNMENT, groups, excluded=[])
    passing = check_cross_dataset_exclusions_applied(
        ASSIGNMENT, groups, excluded=["datasec:clip.wav"]
    )

    assert not failing.passed
    assert "datasec:clip.wav" in failing.violations[0]
    assert passing.passed


def test_cross_dataset_group_inside_train_needs_no_exclusion() -> None:
    groups = {"dup-0001": ["datasec:clip.wav", "datased:S-0001"]}
    assert check_cross_dataset_exclusions_applied(ASSIGNMENT, groups, excluded=[]).passed


def test_pretraining_exclusion_fails_when_the_clip_is_still_in_the_split() -> None:
    """DataSEC không có dev/test cần bảo vệ — nó là corpus pretraining tự thân."""
    assignment = {"datasec:clip-a.wav": "train", "datasec:clip-b.wav": "validation"}

    result = check_pretraining_exclusions_absent(assignment, excluded=["datasec:clip-a.wav"])

    assert not result.passed
    assert result.violations == ["datasec:clip-a.wav"]


def test_pretraining_exclusion_passes_when_the_clip_is_absent() -> None:
    assignment = {"datasec:clip-b.wav": "validation"}

    result = check_pretraining_exclusions_absent(assignment, excluded=["datasec:clip-a.wav"])

    assert result.passed
    assert result.violations == []


def test_pretraining_exclusion_ignores_split_membership() -> None:
    """Không liên quan tới split nào — chỉ hỏi có mặt hay không."""
    assignment = {"datasec:clip-a.wav": "test"}

    result = check_pretraining_exclusions_absent(assignment, excluded=["datasec:clip-a.wav"])

    assert not result.passed


def test_run_all_requires_exactly_five_checks() -> None:
    with pytest.raises(ValueError):
        run_all([check_group_integrity(ASSIGNMENT, {})])


def test_run_all_fails_when_any_check_fails() -> None:
    results = [
        check_group_integrity(ASSIGNMENT, {"datased:S-0001": "g1", "datased:S-0003": "g1"}),
        check_hash_integrity(ASSIGNMENT, {}),
        check_duplicate_pairs_within_split(ASSIGNMENT, {}),
        check_class_coverage(ASSIGNMENT, {}, expected_classes=[]),
        check_cross_dataset_exclusions_applied(ASSIGNMENT, {}, excluded=[]),
    ]
    report = run_all(results)

    assert report["passed"] is False
    assert report["checks"][0]["violation_count"] == 1
    assert [check["number"] for check in report["checks"]] == [1, 2, 3, 4, 5]


def test_check_leakage_refuses_to_run_before_dedup(tmp_path, monkeypatch) -> None:
    """D4 không được tuyên bố pass khi D3 chưa chạy: kiểm 3 và 5 sẽ pass rỗng."""
    import scripts.check_leakage as module

    monkeypatch.setattr(module, "MANIFESTS", tmp_path)
    with pytest.raises(SystemExit) as error:
        module.build_checks("datased", "polyphonic", [], allow_missing_dedup=False)

    assert "D3" in str(error.value)
