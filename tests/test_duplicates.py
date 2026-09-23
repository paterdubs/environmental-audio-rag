import pytest

from ml.dataops.duplicates import (
    DuplicateThresholds,
    PairMatch,
    alarm_band,
    assess_alarm,
    build_groups,
    collect_review_pairs,
    cross_dataset_exclusions,
    human_review_queue,
    split_cohesion_pairs,
    within_dataset_exclusions,
)

THRESHOLDS = DuplicateThresholds()


def _match(left: str, right: str, similarity: float, *, tier="T3", overlap_s=10.0) -> PairMatch:
    return PairMatch(
        left_file_id=left,
        right_file_id=right,
        tier=tier,
        similarity=similarity,
        overlap_s=overlap_s,
        verdict=THRESHOLDS.classify(similarity, overlap_s),
    )


# ---------- ngưỡng ----------


def test_classify_follows_data_plan_bands() -> None:
    assert THRESHOLDS.classify(0.96, 10.0) == "duplicate"
    assert THRESHOLDS.classify(0.95, 10.0) == "duplicate"
    assert THRESHOLDS.classify(0.90, 10.0) == "review"
    assert THRESHOLDS.classify(0.85, 10.0) == "review"
    assert THRESHOLDS.classify(0.84, 10.0) == "distinct"


def test_short_overlap_is_distinct_regardless_of_similarity() -> None:
    assert THRESHOLDS.classify(0.99, 2.9) == "distinct"


def test_invalid_thresholds_are_rejected() -> None:
    with pytest.raises(ValueError):
        DuplicateThresholds(duplicate_min=0.8, review_min=0.9).validate()
    with pytest.raises(ValueError):
        DuplicateThresholds(min_overlap_s=0.0).validate()


# ---------- gom nhóm ----------


def test_transitive_matches_form_one_group() -> None:
    groups = build_groups(
        [
            _match("datased:a.wav", "datased:b.wav", 0.99),
            _match("datased:b.wav", "datased:c.wav", 0.97),
        ]
    )

    assert len(groups) == 1
    assert groups[0].members == ("datased:a.wav", "datased:b.wav", "datased:c.wav")
    assert groups[0].min_similarity == pytest.approx(0.97)
    assert not groups[0].cross_dataset


def test_distinct_pairs_do_not_create_groups() -> None:
    assert build_groups([_match("datased:a.wav", "datased:b.wav", 0.10)]) == []


def test_cross_dataset_group_is_flagged() -> None:
    groups = build_groups([_match("datasec:x.wav", "datased:y.wav", 0.98)])

    assert groups[0].cross_dataset
    assert groups[0].datasets == ("datasec", "datased")


def test_review_edge_does_not_form_a_group() -> None:
    """Gom cạnh review là xử lý tự động — DATA_PLAN §7.3 cấm."""
    matches = [_match("datased:a.wav", "datased:b.wav", 0.88)]

    assert build_groups(matches) == []
    assert [m.similarity for m in collect_review_pairs(matches)] == [0.88]


def test_review_edges_do_not_chain_groups_together() -> None:
    """Đo được trên dữ liệu thật: union cả cạnh review tạo một thành phần
    2,310 file nối bằng đúng ngưỡng yếu nhất 0.850 — chaining, không phải nhóm."""
    matches = [
        _match("datased:a.wav", "datased:b.wav", 0.99),
        _match("datased:b.wav", "datased:c.wav", 0.86),
        _match("datased:c.wav", "datased:d.wav", 0.99),
    ]
    groups = build_groups(matches)

    assert len(groups) == 2
    assert {group.members for group in groups} == {
        ("datased:a.wav", "datased:b.wav"),
        ("datased:c.wav", "datased:d.wav"),
    }


def test_review_pairs_are_sorted_by_similarity() -> None:
    matches = [
        _match("datased:a.wav", "datased:b.wav", 0.86),
        _match("datased:c.wav", "datased:d.wav", 0.93),
    ]
    assert [m.similarity for m in collect_review_pairs(matches)] == [0.93, 0.86]


# ---------- luật xử lý §7.5 ----------


def test_within_dataset_keeps_one_representative() -> None:
    groups = build_groups(
        [
            _match("datased:a.wav", "datased:b.wav", 0.99),
            _match("datased:b.wav", "datased:c.wav", 0.99),
        ]
    )
    exclusions = within_dataset_exclusions(groups)

    assert [item.file_id for item in exclusions] == ["datased:b.wav", "datased:c.wav"]
    assert {item.reason_code for item in exclusions} == {"exclude_duplicate"}


def test_review_pairs_never_reach_the_exclusion_rules() -> None:
    groups = build_groups([_match("datased:a.wav", "datased:b.wav", 0.88)])

    assert groups == []
    assert within_dataset_exclusions(groups) == []
    assert cross_dataset_exclusions(groups, datased_split={}) == []


def test_cross_dataset_group_touching_holdout_excludes_pretraining_clips() -> None:
    groups = build_groups(
        [
            _match("datasec:clip1.wav", "datased:S-0001.wav", 0.98),
            _match("datasec:clip2.wav", "datased:S-0001.wav", 0.97),
        ]
    )
    exclusions = cross_dataset_exclusions(
        groups, datased_split={"datased:S-0001.wav": "test"}
    )

    assert sorted(item.file_id for item in exclusions) == [
        "datasec:clip1.wav",
        "datasec:clip2.wav",
    ]
    assert {item.reason_code for item in exclusions} == {"exclude_cross_dataset_leak"}


def test_cross_dataset_group_inside_train_is_kept() -> None:
    groups = build_groups([_match("datasec:clip1.wav", "datased:S-0002.wav", 0.98)])

    assert cross_dataset_exclusions(groups, datased_split={"datased:S-0002.wav": "train"}) == []


def test_unassigned_benchmark_member_is_not_silently_treated_as_train() -> None:
    """Chạy trước khi freeze split thì không được kết luận 'an toàn'."""
    groups = build_groups([_match("datasec:clip1.wav", "datased:S-0003.wav", 0.98)])

    assert cross_dataset_exclusions(groups, datased_split={}) == []


# ---------- ngưỡng báo động §7.6 ----------


@pytest.mark.parametrize(
    ("leaked", "total", "band"),
    [
        (0, 5_048, "clean"),
        (10, 5_048, "minor"),
        (100, 5_048, "material"),
        (500, 5_048, "invalidating"),
    ],
)
def test_alarm_bands_match_data_plan(leaked: int, total: int, band: str) -> None:
    assert alarm_band(leaked, total)[0] == band


def test_alarm_band_boundaries_are_exclusive_upper() -> None:
    assert alarm_band(50, 5_000)[0] == "material"  # đúng 1.0%
    assert alarm_band(250, 5_000)[0] == "invalidating"  # đúng 5.0%


def test_pending_review_makes_ratio_a_lower_bound() -> None:
    groups = build_groups([_match("datasec:clip1.wav", "datased:S-0001.wav", 0.98)])
    exclusions = cross_dataset_exclusions(groups, datased_split={"datased:S-0001.wav": "test"})

    report = assess_alarm(exclusions, total_pretraining_files=5_048, pending_review_groups=3)

    assert report.leaked_files == 1
    assert report.band == "minor"
    assert report.notes and "CẬN DƯỚI" in report.notes[0]


# ---------- luật file ngắn ----------


def test_pending_review_pairs_are_not_groups() -> None:
    matches = [_match("datasec:x.wav", "datased:y.wav", 0.90)]
    assert build_groups(matches) == []
    assert len(collect_review_pairs(matches)) == 1


def test_short_overlap_needs_a_much_higher_similarity() -> None:
    """Đo được: 95.5% cặp T3 có overlap đúng 1 s và similarity 0.85-0.93. Một
    cửa sổ 1 giây giống nhau là chuyện thường giữa hai bản ghi môi trường bất kỳ."""
    assert THRESHOLDS.classify(0.99, 1.5, required_overlap_s=1.5) == "duplicate"
    assert THRESHOLDS.classify(0.96, 1.5, required_overlap_s=1.5) == "distinct"


def test_short_overlap_has_no_review_band() -> None:
    """Bằng chứng trên 1 giây quá mỏng để đáng một quyết định của người."""
    for similarity in (0.86, 0.90, 0.94, 0.98):
        assert THRESHOLDS.classify(similarity, 1.5, required_overlap_s=1.5) == "distinct"


def test_relaxed_overlap_still_rejects_low_similarity() -> None:
    assert THRESHOLDS.classify(0.50, 1.5, required_overlap_s=1.5) == "distinct"


def test_short_duplicate_min_must_be_at_least_duplicate_min() -> None:
    with pytest.raises(ValueError):
        DuplicateThresholds(short_duplicate_min=0.90).validate()


def test_full_overlap_pairs_keep_automatic_duplicate_verdict() -> None:
    assert THRESHOLDS.classify(0.99, 10.0, required_overlap_s=3.0) == "duplicate"
    assert THRESHOLDS.classify(0.88, 10.0, required_overlap_s=3.0) == "review"


def test_non_positive_required_overlap_is_rejected() -> None:
    with pytest.raises(ValueError):
        THRESHOLDS.classify(0.99, 1.0, required_overlap_s=0.0)


# ---------- tách review theo phạm vi ----------


def test_human_queue_holds_only_cross_dataset_reviews() -> None:
    matches = [
        _match("datasec:a.wav", "datased:S-1.wav", 0.90),
        _match("datased:S-2.wav", "datased:S-3.wav", 0.90),
    ]
    queue = human_review_queue(matches)

    assert [m.left_file_id for m in queue] == ["datasec:a.wav"]


def test_within_dataset_reviews_become_split_cohesion_constraints() -> None:
    """Không xoá gì — chỉ buộc hai recording nghi ngờ nằm cùng split."""
    matches = [
        _match("datased:S-2.wav", "datased:S-3.wav", 0.90),
        _match("datasec:a.wav", "datased:S-1.wav", 0.90),
    ]
    assert split_cohesion_pairs(matches) == [("datased:S-2.wav", "datased:S-3.wav")]


def test_split_cohesion_pairs_are_deduplicated_and_ordered() -> None:
    matches = [
        _match("datased:S-3.wav", "datased:S-2.wav", 0.90),
        _match("datased:S-2.wav", "datased:S-3.wav", 0.91),
    ]
    assert split_cohesion_pairs(matches) == [("datased:S-2.wav", "datased:S-3.wav")]


def test_duplicate_pairs_are_not_split_cohesion_pairs() -> None:
    assert split_cohesion_pairs([_match("datased:a.wav", "datased:b.wav", 0.99)]) == []
