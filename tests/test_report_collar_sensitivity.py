from __future__ import annotations

from scripts.report_collar_sensitivity import collar_curve


def test_wider_collar_recovers_an_event_with_shifted_onset() -> None:
    """Predicted onset 0.6 s late: missed at the 0.2 s protocol collar, matched at 1.0 s."""
    reference = {"R1": [{"event_label": "a", "onset": 1.0, "offset": 5.0}]}
    estimate = {"R1": [{"event_label": "a", "onset": 1.6, "offset": 5.0}]}

    rows = collar_curve(reference, estimate, ("a",), collars=(0.2, 1.0))

    assert rows[0]["collar_s"] == 0.2 and rows[0]["recall"] == 0.0
    assert rows[1]["collar_s"] == 1.0 and rows[1]["f1"] == 1.0
