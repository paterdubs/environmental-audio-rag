"""Test cho việc đóng băng split và guard chống sinh lại âm thầm."""

import hashlib
import json

import pytest

from scripts.check_leakage import assert_matches_frozen
from scripts.freeze_split import build_record, require_gates_passed, split_paths

PASSING_LEAKAGE = {"passed": True, "dedup_available": True}
PASSING_AUDIT = {
    "cross_dataset_exclusions_pending_split": False,
    "alarm": {"pending_review_groups": 0, "band": "minor", "leaked_files": 11},
    "fingerprint_sha256": "a" * 64,
    "standardizer_sha256": "b" * 64,
}


def _write_gates(tmp_path, leakage: dict, audit: dict) -> None:
    (tmp_path / "datased_leakage_report.json").write_text(
        json.dumps(leakage), encoding="utf-8"
    )
    (tmp_path / "duplicate_audit.json").write_text(json.dumps(audit), encoding="utf-8")


# ---------- guard chống split đổi sau khi freeze ----------


def test_guard_is_silent_when_nothing_is_frozen(tmp_path) -> None:
    path = tmp_path / "split.csv"
    path.write_text("recording_id,split\nS-0001,train\n", encoding="utf-8")

    assert_matches_frozen(path)  # không raise


def test_guard_accepts_the_frozen_split(tmp_path) -> None:
    path = tmp_path / "split.csv"
    path.write_text("recording_id,split\nS-0001,train\n", encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    path.with_suffix(".frozen.json").write_text(
        json.dumps({"split_sha256": digest}), encoding="utf-8"
    )

    assert_matches_frozen(path)


def test_guard_rejects_a_regenerated_split(tmp_path) -> None:
    """Sinh lại split rồi quên chạy lại cổng là cách im lặng nhất để hỏng mọi kết quả."""
    path = tmp_path / "split.csv"
    path.write_text("recording_id,split\nS-0001,train\n", encoding="utf-8")
    path.with_suffix(".frozen.json").write_text(
        json.dumps({"split_sha256": "0" * 64}), encoding="utf-8"
    )

    with pytest.raises(SystemExit, match="đóng băng"):
        assert_matches_frozen(path)


# ---------- điều kiện được phép đóng băng ----------


def test_freeze_requires_d4_to_pass(tmp_path, monkeypatch) -> None:
    import scripts.freeze_split as module

    monkeypatch.setattr(module, "MANIFESTS", tmp_path)
    _write_gates(tmp_path, {**PASSING_LEAKAGE, "passed": False}, PASSING_AUDIT)

    with pytest.raises(SystemExit, match="D4 chưa pass"):
        require_gates_passed("datased")


def test_freeze_rejects_a_vacuous_d4_report(tmp_path, monkeypatch) -> None:
    """Báo cáo D4 sinh khi chưa có D3 thì kiểm 3 và 5 pass rỗng."""
    import scripts.freeze_split as module

    monkeypatch.setattr(module, "MANIFESTS", tmp_path)
    _write_gates(tmp_path, {**PASSING_LEAKAGE, "dedup_available": False}, PASSING_AUDIT)

    with pytest.raises(SystemExit, match="pass rỗng"):
        require_gates_passed("datased")


def test_freeze_requires_cross_dataset_exclusions_applied(tmp_path, monkeypatch) -> None:
    import scripts.freeze_split as module

    monkeypatch.setattr(module, "MANIFESTS", tmp_path)
    audit = {**PASSING_AUDIT, "cross_dataset_exclusions_pending_split": True}
    _write_gates(tmp_path, PASSING_LEAKAGE, audit)

    with pytest.raises(SystemExit, match="apply_cross_exclusions"):
        require_gates_passed("datased")


def test_freeze_refuses_while_humans_still_owe_decisions(tmp_path, monkeypatch) -> None:
    import scripts.freeze_split as module

    monkeypatch.setattr(module, "MANIFESTS", tmp_path)
    audit = {**PASSING_AUDIT, "alarm": {**PASSING_AUDIT["alarm"], "pending_review_groups": 3}}
    _write_gates(tmp_path, PASSING_LEAKAGE, audit)

    with pytest.raises(SystemExit, match="3 cặp chờ người"):
        require_gates_passed("datased")


def test_freeze_passes_when_every_gate_is_clean(tmp_path, monkeypatch) -> None:
    import scripts.freeze_split as module

    monkeypatch.setattr(module, "MANIFESTS", tmp_path)
    _write_gates(tmp_path, PASSING_LEAKAGE, PASSING_AUDIT)

    leakage, audit = require_gates_passed("datased")

    assert leakage["passed"] and audit["alarm"]["band"] == "minor"


def test_freeze_detects_split_changed_after_metadata(tmp_path, monkeypatch) -> None:
    """Metadata ghi một hash, file lại là hash khác — không đóng băng thứ mơ hồ."""
    import scripts.freeze_split as module

    monkeypatch.setattr(module, "MANIFESTS", tmp_path)
    monkeypatch.setattr(module, "SPLITS", tmp_path)
    _write_gates(tmp_path, PASSING_LEAKAGE, PASSING_AUDIT)
    csv_path, metadata_path, _ = split_paths("datased", "polyphonic")
    csv_path.write_text("recording_id,split\nS-0001,train\n", encoding="utf-8")
    metadata_path.write_text(json.dumps({"sha256": "0" * 64}), encoding="utf-8")

    with pytest.raises(SystemExit, match="Sinh lại split"):
        build_record("datased", "polyphonic")


# ---------- loại trừ D3 nghĩa gì với split này (ADR-0010) ----------


def _manifests(tmp_path, *, exclusions: str, inventory: str = "", duplicates: str = "") -> None:
    (tmp_path / "exclusions.csv").write_text(
        "file_id,group_id,reason_code,decided_by\n" + exclusions, encoding="utf-8"
    )
    (tmp_path / "duplicate_groups.csv").write_text(
        "group_id,file_id\n" + duplicates, encoding="utf-8"
    )
    if inventory:
        (tmp_path / "datasec_inventory.csv").write_text(
            "file_id,relative_path,sha256\n" + inventory, encoding="utf-8"
        )


def _split(tmp_path, name: str, header: str, body: str):
    path = tmp_path / name
    path.write_text(header + body, encoding="utf-8")
    return path


CLIP_A = "datasec:DATASEC/Bells/Bells-0001.wav"
CLIP_B = "datasec:DATASEC/Bells/Bells-0002.wav"
INVENTORY = f"{CLIP_A},a,aa\n{CLIP_B},b,bb\n"


def test_pretraining_split_must_not_contain_an_excluded_clip(tmp_path, monkeypatch) -> None:
    """Clip trùng dev/test benchmark mà lọt vào pretraining thì RQ1 mất nghĩa."""
    import scripts.freeze_split as module

    monkeypatch.setattr(module, "MANIFESTS", tmp_path)
    _manifests(
        tmp_path,
        exclusions=f"{CLIP_A},dup-0001,exclude_cross_dataset_leak,human:patphh\n",
        inventory=INVENTORY,
    )
    path = _split(tmp_path, "datasec.csv", "file_id,split,leakage_group\n", f"{CLIP_A},train,g1\n")

    with pytest.raises(SystemExit, match="vẫn nằm trong split"):
        module.require_exclusion_policy("datasec", path)


def test_pretraining_split_passes_when_the_clip_is_absent(tmp_path, monkeypatch) -> None:
    import scripts.freeze_split as module

    monkeypatch.setattr(module, "MANIFESTS", tmp_path)
    _manifests(
        tmp_path,
        exclusions=f"{CLIP_A},dup-0001,exclude_cross_dataset_leak,human:patphh\n",
        inventory=INVENTORY,
    )
    path = _split(tmp_path, "datasec.csv", "file_id,split,leakage_group\n", f"{CLIP_B},train,g2\n")

    summary = module.require_exclusion_policy("datasec", path)

    assert summary == {"corpus": "pretraining", "checked": 1, "must_be_absent": 1, "grouped": 0}


def test_benchmark_keeps_internal_duplicates_instead_of_deleting(tmp_path, monkeypatch) -> None:
    """Xoá trùng nội bộ khỏi benchmark thì benchmark teo lại — luật là buộc cùng split."""
    import scripts.freeze_split as module

    monkeypatch.setattr(module, "MANIFESTS", tmp_path)
    file_a, file_b = "datased:SED_wav/S-0001.wav", "datased:SED_wav/S-0002.wav"
    _manifests(
        tmp_path,
        exclusions=f"{file_b},dup-0001,exclude_duplicate,rule:within_dataset_representative\n",
        duplicates=f"dup-0001,{file_a}\ndup-0001,{file_b}\n",
    )
    (tmp_path / "datased_recordings.csv").write_text(
        f"recording_id,file_id,content_sha256\nS-0001,{file_a},aa\nS-0002,{file_b},aa\n",
        encoding="utf-8",
    )
    path = _split(
        tmp_path,
        "datased.csv",
        "recording_id,split,leakage_group\n",
        "S-0001,train,g1\nS-0002,train,g1\n",
    )

    summary = module.require_exclusion_policy("datased", path)

    assert summary == {"corpus": "benchmark", "checked": 1, "must_be_absent": 0, "grouped": 1}


def test_benchmark_rejects_a_duplicate_group_split_in_two(tmp_path, monkeypatch) -> None:
    import scripts.freeze_split as module

    monkeypatch.setattr(module, "MANIFESTS", tmp_path)
    file_a, file_b = "datased:SED_wav/S-0001.wav", "datased:SED_wav/S-0002.wav"
    _manifests(
        tmp_path,
        exclusions=f"{file_b},dup-0001,exclude_duplicate,rule:within_dataset_representative\n",
        duplicates=f"dup-0001,{file_a}\ndup-0001,{file_b}\n",
    )
    (tmp_path / "datased_recordings.csv").write_text(
        f"recording_id,file_id,content_sha256\nS-0001,{file_a},aa\nS-0002,{file_b},aa\n",
        encoding="utf-8",
    )
    path = _split(
        tmp_path,
        "datased.csv",
        "recording_id,split,leakage_group\n",
        "S-0001,train,g1\nS-0002,test,g2\n",
    )

    with pytest.raises(SystemExit, match="leakage_group"):
        module.require_exclusion_policy("datased", path)


def test_an_empty_split_cannot_be_reported_as_clean(tmp_path, monkeypatch) -> None:
    """Có loại trừ nhưng split phân giải ra rỗng — đó là pass rỗng, không phải sạch."""
    import scripts.freeze_split as module

    monkeypatch.setattr(module, "MANIFESTS", tmp_path)
    _manifests(
        tmp_path,
        exclusions=f"{CLIP_A},dup-0001,exclude_cross_dataset_leak,human:patphh\n",
        inventory=INVENTORY,
    )
    path = _split(tmp_path, "datasec.csv", "file_id,split,leakage_group\n", "")

    with pytest.raises(SystemExit, match="pass rỗng"):
        module.require_exclusion_policy("datasec", path)
