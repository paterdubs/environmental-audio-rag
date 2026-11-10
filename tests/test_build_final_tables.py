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
