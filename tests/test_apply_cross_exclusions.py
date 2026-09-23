"""Test cho mắt nối D3 → D4."""

import csv

import pytest

from ml.dataops.duplicates import Exclusion
from scripts.apply_cross_exclusions import (
    load_existing,
    load_groups,
    load_split,
    merge_exclusions,
    write_exclusions,
)


def _write_groups(path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "group_id",
                "file_id",
                "datasets",
                "tiers",
                "min_similarity",
                "cross_dataset",
                "needs_review",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def test_load_groups_reassembles_members(tmp_path) -> None:
    path = tmp_path / "duplicate_groups.csv"
    _write_groups(
        path,
        [
            {
                "group_id": "dup-0001",
                "file_id": file_id,
                "datasets": "datasec|datased",
                "tiers": "T3",
                "min_similarity": "0.970000",
                "cross_dataset": "true",
                "needs_review": "false",
            }
            for file_id in ("datased:S-0001", "datasec:Sirens/Sirens-0046.wav")
        ],
    )
    groups = load_groups(path)

    assert len(groups) == 1
    assert groups[0].members == ("datasec:Sirens/Sirens-0046.wav", "datased:S-0001")
    assert groups[0].cross_dataset
    assert groups[0].min_similarity == pytest.approx(0.97)


def test_load_groups_fails_loudly_before_d3(tmp_path) -> None:
    with pytest.raises(SystemExit) as error:
        load_groups(tmp_path / "missing.csv")

    assert "find_duplicates detect" in str(error.value)


def test_load_split_fails_loudly_before_freeze(tmp_path) -> None:
    with pytest.raises(SystemExit) as error:
        load_split(tmp_path / "missing.csv", "datased")

    assert "create_splits" in str(error.value)


def test_load_split_resolves_recording_id_to_file_id(tmp_path, monkeypatch) -> None:
    """Split lưu `S-0233`, cổng D3 lưu đường dẫn đầy đủ. Ghép chuỗi thẳng cho ra
    khoá không khớp gì, và luật loại trừ im lặng trả rỗng."""
    import scripts.apply_cross_exclusions as module

    monkeypatch.setattr(module, "MANIFESTS", tmp_path)
    (tmp_path / "datased_recordings.csv").write_text(
        "recording_id,file_id\nS-0233,datased:SED_wav/S-0233.wav\n", encoding="utf-8"
    )
    split_path = tmp_path / "split.csv"
    split_path.write_text("recording_id,split\nS-0233,validation\n", encoding="utf-8")

    assert module.load_split(split_path, "datased") == {
        "datased:SED_wav/S-0233.wav": "validation"
    }


def test_load_split_uses_file_id_column_when_present(tmp_path) -> None:
    path = tmp_path / "split.csv"
    path.write_text("file_id,split\ndatased:a.wav,test\n", encoding="utf-8")

    assert load_split(path, "datased") == {"datased:a.wav": "test"}


def test_namespace_mismatch_between_groups_and_split_is_fatal() -> None:
    """Khoá sai cho ra '0 clip rò rỉ' — trông giống hệt 'sạch thật'."""
    from ml.dataops.duplicates import DuplicateGroup
    from scripts.apply_cross_exclusions import assert_split_covers_groups

    groups = [
        DuplicateGroup(
            group_id="dup-0001",
            members=("datasec:a.wav", "datased:SED_wav/S-0233.wav"),
            tiers=("T3",),
            min_similarity=1.0,
            cross_dataset=True,
            needs_review=False,
        )
    ]
    with pytest.raises(SystemExit, match="Namespace mismatch"):
        assert_split_covers_groups(groups, {"datased:S-0233": "validation"})

    assert_split_covers_groups(groups, {"datased:SED_wav/S-0233.wav": "validation"})


def test_merge_keeps_human_decisions_intact() -> None:
    """Một quyết định đã có người ký tên thì luật máy không được lật."""
    human = Exclusion(
        file_id="datasec:a.wav",
        group_id="dup-0001",
        reason_code="keep_after_review",
        decided_by="human:patph",
    )
    machine = Exclusion(
        file_id="datasec:a.wav",
        group_id="dup-0001",
        reason_code="exclude_cross_dataset_leak",
        decided_by="rule:cross_dataset_holdout",
    )
    merged, added = merge_exclusions([human], [machine])

    assert merged == [human]
    assert added == 0


def test_merge_adds_new_machine_exclusions() -> None:
    machine = Exclusion(
        file_id="datasec:b.wav",
        group_id="dup-0002",
        reason_code="exclude_cross_dataset_leak",
        decided_by="rule:cross_dataset_holdout",
    )
    merged, added = merge_exclusions([], [machine])

    assert merged == [machine] and added == 1


def test_merge_overwrites_earlier_machine_rows_without_double_counting() -> None:
    first = Exclusion("datasec:c.wav", "dup-0003", "exclude_duplicate", "rule:within")
    second = Exclusion("datasec:c.wav", "dup-0003", "exclude_cross_dataset_leak", "rule:cross")
    merged, added = merge_exclusions([first], [second])

    assert merged == [second]
    assert added == 0  # cùng một file, không phải một loại trừ mới


def test_merge_sorts_by_file_id() -> None:
    rows = [
        Exclusion("datasec:z.wav", "g", "exclude_duplicate", "rule:within"),
        Exclusion("datasec:a.wav", "g", "exclude_duplicate", "rule:within"),
    ]
    merged, _ = merge_exclusions(rows, [])

    assert [item.file_id for item in merged] == ["datasec:a.wav", "datasec:z.wav"]


def test_exclusions_round_trip(tmp_path) -> None:
    path = tmp_path / "exclusions.csv"
    rows = [Exclusion("datasec:a.wav", "dup-0001", "exclude_duplicate", "human:patph")]
    write_exclusions(path, rows)

    assert load_existing(path) == rows


def test_load_existing_returns_empty_when_absent(tmp_path) -> None:
    assert load_existing(tmp_path / "nope.csv") == []
