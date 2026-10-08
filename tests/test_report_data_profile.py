import pandas as pd
import pytest

from scripts.report_data_profile import SOURCES, build_profile, grid_coverage, summary


@pytest.fixture
def profile_root(tmp_path):
    tables = {
        "recordings": pd.DataFrame({"recording_id": ["a", "b", "c"],
                                    "duration_s": [20.1, 0.5, 1.0],
                                    "content_sha256": ["same", "same", "different"]}),
        "splits": pd.DataFrame({"recording_id": ["a", "b", "c"],
                                "split": ["train", "train", "validation"]}),
        "poly": pd.DataFrame({"recording_id": ["a", "a", "a"],
                              "class_id": ["bells"] * 3,
                              "onset_s": [0.0, 0.1, 0.5], "offset_s": [0.2, 0.3, 0.9]}),
        "mono": pd.DataFrame({"recording_id": ["a", "a", "b", "c"],
                              "class_id": ["bells", "bells", "wind", "bells"],
                              "onset_s": [0.0, 0.0, 0.0, 0.0],
                              "offset_s": [0.2, 0.21, 0.5, 1.0]}),
        "clips": pd.DataFrame({"relative_path": ["DATASEC/Bells/one.wav"],
                               "duration_s": [2.0]}),
    }
    for key, value in tables.items():
        out = tmp_path / SOURCES[key]
        out.parent.mkdir(parents=True, exist_ok=True)
        value.to_csv(out, index=False)
    taxonomy = tmp_path / SOURCES["taxonomy"]
    taxonomy.parent.mkdir(parents=True)
    taxonomy.write_text("version: 1\nclasses:\n  - id: bells\n    source_label: Bells\n"
                        "  - id: wind\n    source_label: Wind\n    polyphonic: false\n")
    return tmp_path


def test_profile_missing_gt_windows_gaps_and_exact_matches(profile_root):
    result = build_profile(profile_root)
    assert result["train_windows"]["total"] == 4  # 20.1 s => 3, 0.5 s => 1
    assert result["missing_poly_gt"]["train"]["recording_ids"] == ["b"]
    assert result["missing_poly_gt"]["train"]["mono_by_class"] == {"wind": 1}
    assert result["missing_poly_gt"]["validation"]["count"] == 1
    assert result["mono_vs_poly"]["mono_exact_matches"] == 1
    assert result["mono_vs_poly"]["mono_21class_events"] == 3
    assert result["same_class_gaps"]["count"] == 2
    assert result["same_class_gaps"]["overlapping"] == 1
    assert result["same_class_gaps"]["under_1s"] == 2
    assert result["identical_pairs"] == [{"left": "a", "right": "b",
                                          "left_split": "train", "right_split": "train"}]
    assert result["datasec_by_class"][0]["quantiles"]["0.5"] == 2.0
    assert len(result["sources"]) == 6


def test_grid_counts_events_half_open_and_clips_end():
    recordings = pd.DataFrame({"recording_id": ["a", "b"], "duration_s": [0.35, 0.1]})
    events = pd.DataFrame({"recording_id": ["a"] * 3, "onset_s": [0, 0, 0.1],
                           "offset_s": [0.2, 0.2, 0.3]})
    result = grid_coverage(recordings, events)
    assert result["points"] == 5
    assert result["counts"] == [2, 1, 1, 1]
    assert sum(result["fractions"]) == pytest.approx(1)


def test_empty_summary_does_not_invent_zero():
    assert summary([])["quantiles"]["0.5"] is None
