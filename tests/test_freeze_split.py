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
