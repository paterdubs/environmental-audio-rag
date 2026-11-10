"""Lưới PSDS ghi trước của LBR (ADR-0047): cố định, và đường cong tính được trên run đóng băng."""

import numpy as np
import pandas as pd
from test_lbr_test_section import CLASSES, FR, frozen_run

from scripts import lbr_test_section
from scripts.evaluate_run import to_reference_frame
from scripts.report_lbr_psds_grid import PSDS_GRID_LOG, psds_curve


def test_pre_registered_grid_is_fixed_log_spaced_and_covers_the_low_scores():
    grid = np.array(PSDS_GRID_LOG)
    assert len(grid) == 48
    assert grid[0] == 1e-5 and abs(grid[-1] - 0.99) < 1e-12
    assert np.all(np.diff(grid) > 0)
    assert np.allclose(np.diff(np.log(grid)), np.diff(np.log(grid))[0])  # cách đều theo log


def test_curve_reports_points_and_boxes_below_the_lowest_threshold(tmp_path):
    probabilities, reference = frozen_run(tmp_path)
    lbr = lbr_test_section.estimate(tmp_path, probabilities, class_ids=CLASSES, frame_rate=FR)
    recordings = sorted(probabilities)
    reference = {r: [{**e, "event_label": e["class_id"]} for e in events]
                 for r, events in reference.items()}
    metadata = pd.DataFrame({"filename": recordings, "duration": [
        probabilities[r].shape[0] / FR for r in recordings]})
    curve = psds_curve(lbr["boxes"], lbr["scores"], PSDS_GRID_LOG, recordings=recordings,
                       ground_truth=to_reference_frame(reference), metadata=metadata)
    assert 0 < curve["n_points"] <= curve["n_grid"] == 48
    assert set(curve["psds"]) == {"psds_1", "psds_2"}
    assert all(0.0 <= v <= 1.0 for v in curve["psds"].values())
    assert curve["boxes_never_included"] == 0  # điểm V1 là điểm box, đều > 1e-5
    assert curve["events_at_lowest_threshold"] >= 1


def _b0_case():
    from ml.postprocessing.events import PostprocessedEvent

    candidates = {"r": [PostprocessedEvent("r", "x", 1.0, 3.0, 0.9),
                        PostprocessedEvent("r", "y", 5.0, 6.0, 0.03),
                        PostprocessedEvent("r", "y", 8.0, 9.0, 1e-6)]}
    ground_truth = pd.DataFrame([{"filename": "r", "event_label": "x", "onset": 1.0, "offset": 3.0},
                                 {"filename": "r", "event_label": "y", "onset": 5.0,
                                  "offset": 6.0}])
    metadata = pd.DataFrame({"filename": ["r"], "duration": [3600.0]})
    return candidates, ground_truth, metadata


def test_b0_curve_counts_boxes_below_each_grid_like_the_lbr_curve():
    from scripts.report_lbr_psds_grid import sebb_curve

    candidates, ground_truth, metadata = _b0_case()
    linear = sebb_curve(candidates, (0.05, 0.5, 0.95), ground_truth=ground_truth,
                        metadata=metadata)
    log = sebb_curve(candidates, PSDS_GRID_LOG, ground_truth=ground_truth, metadata=metadata)
    assert linear["boxes_never_included"] == 2 and log["boxes_never_included"] == 1
    assert linear["events_at_lowest_threshold"] == 1 and log["events_at_lowest_threshold"] == 2
    assert log["psds"]["psds_2"] > linear["psds"]["psds_2"]  # y chỉ vào được trên lưới log


def test_b0_reference_check_passes_only_on_exact_reproduction():
    import pytest

    from scripts.report_lbr_psds_grid import check_reference

    curve = {"psds": {"psds_1": 0.3131178, "psds_2": 0.7309525}}
    ok = check_reference(curve, {"psds": {"psds_1": 0.3131178, "psds_2": 0.7309525}})
    assert ok["match"] is True
    with pytest.raises(SystemExit, match="không tái tạo"):
        check_reference(curve, {"psds": {"psds_1": 0.3489, "psds_2": 0.7309525}})
