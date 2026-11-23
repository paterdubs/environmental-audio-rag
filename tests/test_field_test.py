import csv

import pytest

from scripts import field_test as ft


def _events():
    return [{"event_id": 1, "class_id": "horn", "onset_s": 1.0, "offset_s": 3.5, "score": 0.91},
            {"event_id": 2, "class_id": "voices", "onset_s": 4.0, "offset_s": 6.0, "score": 0.5}]


def _rated(rows, judgements, missed=0):
    out, it = [], iter(judgements)
    for r in rows:
        r = dict(r)
        if r["loai_dong"] == "phat_hien":
            r["danh_gia"] = next(it)
        else:
            r["so_bo_sot"] = str(missed)
        out.append(r)
    return out


def test_sheet_has_one_row_per_event_plus_a_missed_row_per_clip():
    rows = ft.sheet_rows("clip_01", _events())
    assert [r["loai_dong"] for r in rows] == ["phat_hien", "phat_hien", "bo_sot"]
    assert rows[0]["onset_s"] == "1.00" and rows[0]["danh_gia"] == ""


def test_summary_counts_precision_missed_and_agreement():
    rows = ft.sheet_rows("clip_01", _events()) + ft.sheet_rows("clip_02", _events()[:1])
    a = _rated(rows, ["dung", "sai", "dung"], missed=1)
    b = _rated(rows, ["dung", "dung", "dung"], missed=2)
    result = ft.summarise(a, b)
    assert result["rater_a"]["precision"] == pytest.approx(2 / 3)
    assert result["rater_b"]["missed"] == 4
    assert result["agreement"]["n"] == 3 and result["agreement"]["agree"] == 2
    assert result["agreement"]["both_correct"] == 2


def test_kappa_is_one_for_identical_and_zero_for_chance_level():
    assert ft.cohen_kappa([("dung", "dung"), ("sai", "sai")]) == pytest.approx(1.0)
    assert ft.cohen_kappa([("dung", "dung"), ("dung", "sai"), ("sai", "dung"),
                           ("sai", "sai")]) == pytest.approx(0.0)
    assert ft.cohen_kappa([]) is None
    assert ft.cohen_kappa([("dung", "dung"), ("dung", "dung")]) is None


def test_unrated_and_uncertain_rows_are_excluded_from_precision_and_agreement():
    rows = ft.sheet_rows("clip_01", _events())
    a = _rated(rows, ["dung", "khong_ro"])
    b = _rated(rows, ["dung", ""])
    result = ft.summarise(a, b)
    assert result["rater_a"]["precision"] == 1.0 and result["rater_a"]["khong_ro"] == 1
    assert result["rater_b"]["unrated"] == 1
    assert result["agreement"]["n"] == 1


def test_read_sheet_rejects_unknown_judgement_and_accepts_excel_cp1252(tmp_path):
    rows = _rated(ft.sheet_rows("clip_01", _events()), ["dung", "sai"])
    path = tmp_path / "a.csv"
    ft.write_sheet(path, rows)
    assert ft.read_sheet(path)[0]["danh_gia"] == "dung"
    text = path.read_text(encoding="utf-8-sig").replace("sai", "SAI ")
    path.write_bytes(text.encode("cp1252"))
    assert ft.read_sheet(path)[1]["danh_gia"] == "sai"
    bad = tmp_path / "b.csv"
    with bad.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ft.COLUMNS)
        writer.writeheader()
        writer.writerow({**rows[0], "danh_gia": "co"})
    with pytest.raises(ValueError):
        ft.read_sheet(bad)


def test_prepare_clips_anonymises_names_and_keeps_accepted_formats(tmp_path):
    source, work = tmp_path / "in", tmp_path / "work"
    source.mkdir()
    work.mkdir()
    (source / "dam cuoi nha ban.wav").write_bytes(b"RIFF")
    (source / "z.mp3").write_bytes(b"ID3")
    names = [(cid, p.name) for cid, p in ft.prepare_clips(source, work)]
    assert names == [("clip_01", "clip_01.wav"), ("clip_02", "clip_02.mp3")]


def test_prepare_clips_refuses_an_empty_folder(tmp_path):
    with pytest.raises(SystemExit):
        ft.prepare_clips(tmp_path, tmp_path)
