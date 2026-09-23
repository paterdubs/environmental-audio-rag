import pytest

from ml.dataops.grouping import build_leakage_groups, group_size_histogram, largest_group

ITEMS = [f"datased:S-000{index}" for index in range(1, 6)]
CONTENT = {item: f"hash-{index}" for index, item in enumerate(ITEMS)}


def test_distinct_content_yields_one_group_each() -> None:
    groups = build_leakage_groups(ITEMS, content_key=CONTENT)

    assert len(set(groups.values())) == len(ITEMS)


def test_identical_content_merges_items() -> None:
    content = {**CONTENT, "datased:S-0002": CONTENT["datased:S-0001"]}
    groups = build_leakage_groups(ITEMS, content_key=content)

    assert groups["datased:S-0001"] == groups["datased:S-0002"]
    assert len(set(groups.values())) == len(ITEMS) - 1


def test_duplicate_group_merges_items() -> None:
    groups = build_leakage_groups(
        ITEMS,
        content_key=CONTENT,
        duplicate_groups={"dup-0001": ["datased:S-0003", "datased:S-0004"]},
    )

    assert groups["datased:S-0003"] == groups["datased:S-0004"]


def test_cohesion_pair_merges_items() -> None:
    groups = build_leakage_groups(
        ITEMS, content_key=CONTENT, cohesion_pairs=[("datased:S-0001", "datased:S-0005")]
    )

    assert groups["datased:S-0001"] == groups["datased:S-0005"]


def test_three_sources_merge_transitively() -> None:
    """Nối bằng ba lý do khác nhau vẫn phải ra một nhóm."""
    content = {**CONTENT, "datased:S-0002": CONTENT["datased:S-0001"]}
    groups = build_leakage_groups(
        content_key=content,
        items=ITEMS,
        duplicate_groups={"dup-0001": ["datased:S-0002", "datased:S-0003"]},
        cohesion_pairs=[("datased:S-0003", "datased:S-0004")],
    )
    merged = {groups[item] for item in ITEMS[:4]}

    assert len(merged) == 1
    assert groups["datased:S-0005"] not in merged


def test_members_outside_the_item_set_are_ignored() -> None:
    """Quan hệ xuyên dataset do luật loại trừ lo, không phải do split."""
    groups = build_leakage_groups(
        ITEMS,
        content_key=CONTENT,
        duplicate_groups={"dup-0001": ["datased:S-0001", "datasec:Sirens/Sirens-0046.wav"]},
        cohesion_pairs=[("datased:S-0002", "datasec:Voices/Voices-0001.wav")],
    )

    assert set(groups) == set(ITEMS)
    assert len(set(groups.values())) == len(ITEMS)


def test_group_key_is_stable_regardless_of_input_order() -> None:
    kwargs = {
        "content_key": CONTENT,
        "duplicate_groups": {"dup-0001": ["datased:S-0004", "datased:S-0002"]},
    }
    first = build_leakage_groups(ITEMS, **kwargs)
    second = build_leakage_groups(list(reversed(ITEMS)), **kwargs)

    assert first == second


def test_missing_content_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="Missing content key"):
        build_leakage_groups(ITEMS, content_key={ITEMS[0]: "hash-0"})


def test_empty_item_set_is_rejected() -> None:
    with pytest.raises(ValueError):
        build_leakage_groups([], content_key={})


def test_histogram_and_largest_group() -> None:
    groups = build_leakage_groups(
        ITEMS,
        content_key=CONTENT,
        cohesion_pairs=[("datased:S-0001", "datased:S-0002"), ("datased:S-0002", "datased:S-0003")],
    )

    assert group_size_histogram(groups) == {1: 2, 3: 1}
    assert largest_group(groups) == 3


def test_namespace_mismatch_is_rejected_not_ignored() -> None:
    """Đã xảy ra thật: split dùng `datased:S-0001`, cổng D3 dùng đường dẫn đầy đủ.
    Luật "bỏ qua thành viên ngoài tập" nuốt trọn ràng buộc và split vẫn chạy."""
    with pytest.raises(ValueError, match="Namespace mismatch"):
        build_leakage_groups(
            ITEMS,
            content_key=CONTENT,
            duplicate_groups={"dup-0001": ["datased:SED_wav/S-0001.wav"]},
        )


def test_namespace_check_allows_partial_overlap() -> None:
    """Một ràng buộc khớp là đủ để chứng minh namespace đúng."""
    groups = build_leakage_groups(
        ITEMS,
        content_key=CONTENT,
        duplicate_groups={"dup-0001": ["datased:S-0001", "datased:S-9999"]},
    )
    assert set(groups) == set(ITEMS)


def test_namespace_check_ignores_other_datasets() -> None:
    groups = build_leakage_groups(
        ITEMS,
        content_key=CONTENT,
        cohesion_pairs=[("datasec:a.wav", "datasec:b.wav")],
    )
    assert len(set(groups.values())) == len(ITEMS)
