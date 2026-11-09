"""Phân loại FN của script chẩn đoán LBR trên các ca nhỏ dựng tay."""

from scripts.report_lbr_diagnosis import categorize, match


def ev(onset, offset, label="a"):
    return {"class_id": label, "onset": onset, "offset": offset}


def test_match_uses_primary_criterion():
    assert match([ev(1.0, 5.0)], [ev(1.1, 5.3)]) == ({0}, {0})
    assert match([ev(1.0, 5.0)], [ev(1.5, 5.0)]) == (set(), set())


def test_categories_of_missed_events():
    assert categorize([ev(1, 2)], [], []) == ["miss_nothing"]
    assert categorize([ev(1, 2)], [], [ev(1, 2, "b")]) == ["miss_other_class_overlap"]
    assert categorize([ev(1, 5)], [ev(1, 2), ev(3, 5)], []) == ["fragmented"]
    assert categorize([ev(1, 2), ev(3, 4)], [ev(1, 4)], []) == ["merged", "merged"]
    assert categorize([ev(1, 5)], [ev(0.5, 5)], []) == ["bnd_onset"]
    assert categorize([ev(1, 5)], [ev(1, 7)], []) == ["bnd_offset"]
    assert categorize([ev(1, 5)], [ev(0.5, 7)], []) == ["bnd_both"]
    assert categorize([ev(1, 5)], [ev(1.1, 5.1)], []) == []
