from __future__ import annotations

import pytest

from scripts.report_multirun_bootstrap import check_pairing


def test_pairing_accepts_matching_or_unrecorded_postproc() -> None:
    check_pairing({"postproc": "D:/repo/ml/runs/r/postproc_cv.json"}, "postproc_cv.json", "r")
    check_pairing({}, "postproc.json", "r")  # older evaluations do not record the file


def test_pairing_rejects_evaluation_from_another_postproc() -> None:
    with pytest.raises(SystemExit, match="cặp file lệch"):
        check_pairing({"postproc": "ml/runs/r/postproc.json"}, "postproc_cv.json", "r")
