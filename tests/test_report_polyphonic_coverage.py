import pandas as pd

from scripts.report_polyphonic_coverage import uncovered_summary


def test_uncovered_recordings_are_split_and_counted_on_polyphonic_classes_only() -> None:
    recordings = pd.DataFrame({"recording_id": ["S-1", "S-2", "S-3"],
                               "duration_s": [3600.0, 1800.0, 900.0]})
    splits = pd.Series({"S-1": "train", "S-2": "test", "S-3": "test"})
    mono = pd.DataFrame({"recording_id": ["S-2", "S-2", "S-3", "S-1"],
                         "class_id": ["horn", "wind_turbine", "wind_turbine", "horn"]})
    summary = uncovered_summary(recordings, splits, mono, covered={"S-1"}, class_ids=("horn",))
    assert summary["recordings"] == ["S-2", "S-3"]
    assert summary["per_split"]["test"] == {"recordings": ["S-2", "S-3"], "hours": 0.75,
                                            "mono_events_in_polyphonic_classes": 1}
    assert summary["per_split"]["train"]["recordings"] == []
    assert summary["wind_turbine_recordings_equal_uncovered"] is True
