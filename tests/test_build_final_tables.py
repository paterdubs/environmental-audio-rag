"""Bảng báo cáo cuối phải khớp từng ô với `final_numbers` (không tự tính lại)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import build_final_tables as bft

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "docs" / "measurements" / "final_numbers_20261110.json"

pytestmark = pytest.mark.skipif(not FINAL.is_file(), reason="chưa có final_numbers")


@pytest.fixture(scope="module")
def data() -> dict:
    return json.loads(FINAL.read_text(encoding="utf-8"))


def test_sed_table_has_every_system_and_locked_numbers(data):
    text = bft.build_sed(data, "abcdef0", FINAL)
    for label in bft.SED_ROWS.values():
        assert label in text
    assert "0.2965 [0.2293, 0.3603]" in text
    assert "+0.1159 [+0.0741, +0.1593]" in text
    assert "0.3061 / 0.7452" in text


def test_rq2_table_reports_constrained_v3_omission(data):
    text = bft.build_rq2(data, "abcdef0", FINAL)
    assert "Constrained — bỏ sót | 0.012 [0.002, 0.024] | 0.013" in text
    assert "0.081 [0.051, 0.112]" in text


def test_rq3_and_psds_tables(data):
    rq3 = bft.build_rq3(data, "abcdef0", FINAL)
    assert "0.670 [0.610, 0.729]" in rq3
    psds = bft.build_psds(data, "abcdef0", FINAL)
    assert "Δ PSDS-2 (lưới tuyến tính) | -0.0078" in psds
    assert "H2 — lợi ích quanh điểm vận hành (PSDS-2) | không" in psds


def test_rq1_and_intersection(data):
    assert "-0.0071 [-0.0164, +0.0021]" in bft.build_rq1(data, "abcdef0", FINAL)
    assert "0.8203" in bft.build_intersection(data, "abcdef0", FINAL)


RUN_B0 = ROOT / "ml" / "runs" / "sed_ensemble_B0_final_test_20261014T085016Z"


@pytest.mark.skipif(not RUN_B0.is_dir(), reason="chưa có run B0 final test")
def test_per_class_table_hides_f1_for_small_classes():
    text = bft.build_per_class(RUN_B0, "abcdef0")
    assert "| `cat_fights_and_moans` | 9 | khớp 0/9 | khớp 3/9 | — | — |" in text
    assert "| `workshop` | 69 | 0.4505 | 0.6992 | 0.7963 | 0.6232 |" in text


MODES = ROOT / "docs" / "measurements" / "rq3_modes_20261123.json"


@pytest.mark.skipif(not MODES.is_file(), reason="chưa có rq3_modes")
def test_rq3_modes_tables_report_hybrid_minus_vector_and_groups():
    modes = json.loads(MODES.read_text(encoding="utf-8"))
    paired = bft.build_rq3_paired(modes, "abcdef0", MODES)
    assert "-0.075 [-0.121, -0.028]" in paired  # B0
    assert "+0.040 [+0.004, +0.079]" in paired  # V3 đảo chiều
    groups = bft.build_rq3_groups(modes, "abcdef0", MODES)
    assert "0.126 / 0.426" in groups  # f2, quan hệ thời gian


BACKFILL = ROOT / "docs" / "measurements" / "retrieval_backfill_test_20261124.json"


@pytest.mark.skipif(not BACKFILL.is_file(), reason="chưa có retrieval_backfill")
def test_rq3_backfill_table_reports_locked_hybrid_and_paired_gain():
    text = bft.build_rq3_backfill(json.loads(BACKFILL.read_text(encoding="utf-8")), "abcdef0",
                                  BACKFILL)
    assert "| B0 | 0.458 | 0.383 | 0.500 |" in text
    assert "+0.097 [+0.070, +0.126]" in text  # V3, backfill − vector


CONTEXT = ROOT / "docs" / "measurements" / "lbr_context_20261123.json"


@pytest.mark.skipif(not CONTEXT.is_file(), reason="chưa có lbr_context")
def test_lbr_context_table_has_baselines_ceiling_and_robustness_row():
    context = json.loads(CONTEXT.read_text(encoding="utf-8"))
    text = bft.build_lbr_context(context, "abcdef0", CONTEXT)
    assert "0.3332" in text and "+0.0990 [+0.0761, +0.1200]" in text
    assert "0.4641" in text  # trần ±1 s
    assert "0.3505" in text  # kiểm chuyển sang ensemble 3 seed


CALIBRATION = ROOT / "docs" / "measurements" / "calibration_20261123.json"


@pytest.mark.skipif(not CALIBRATION.is_file(), reason="chưa có calibration")
def test_calibration_table_places_systems_next_to_label_agreement():
    data = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    text = bft.build_calibration(data, "abcdef0", CALIBRATION)
    assert "| B0 | 0.1806 | 0.3889 | 0.7260 |" in text
    assert "0.5785 | 0.7603 | 0.7425" in text


def test_workload_table_formats_counts_from_the_measurement():
    data = {"commits": 400, "first_commit": "2026-09-22", "last_commit": "2026-11-23",
            "python_lines": {"ml": 1000, "scripts": 2000, "tests": 3000, "services": 4},
            "frontend_lines": 1234, "test_functions": 9, "adr": 48, "measurement_reports": 270,
            "runs": {"sed": 103, "classifier": 8}, "json_schemas": 8}
    text = bft.build_workload(data, "abcdef0", ROOT / "docs" / "measurements" / "w.json")
    assert "400 commit" in text and "6.004 dòng" in text and "103 run SED" in text


def test_latency_table_reports_median_and_p95_with_audio_range():
    data = {"elapsed_s": {"n": 10, "median": 3.89, "p95": 11.96, "max": 11.96},
            "rtf": {"n": 10, "median": 0.0721, "p95": 0.2936, "max": 0.2936},
            "query_s": {"n": 5, "median": 0.2215, "p95": 0.3021, "max": 0.3021},
            "audio_duration_s": {"min": 3.36, "max": 179.6}}
    text = bft.build_latency(data, "abcdef0", ROOT / "docs" / "measurements" / "l.json")
    assert "| Tải lên + phân tích (giây) | 10 | 3.89 | 11.96 |" in text
    assert "3.4 đến 179.6" in text and "0.072" in text


def test_run_registry_table_lists_tasks_and_a_total_row():
    data = {"n_runs": 5, "by_task": {
        "sed_polyphonic": {"n": 3, "complete": 2, "dirty": 1, "split_hashes": 1,
                           "first": "20260922", "last": "20261108"},
        "sed_lbr": {"n": 2, "complete": 2, "dirty": 0, "split_hashes": 1,
                    "first": "20261109", "last": "20261110"}}}
    text = bft.build_run_registry(data, "abcdef0", ROOT / "docs" / "measurements" / "r.json")
    assert "| Huấn luyện SED | 3 | 2 | 1 | 1 | 22/09 – 08/11 |" in text
    assert "| Tổng | 5 | 4 | 1 | — | — |" in text
