import pytest

from ml.evaluation.multirun import micro_f1, paired_branch_bootstrap
from ml.evaluation.sed_metrics import event_based_f1, event_counts_per_recording


def ev(label, onset, offset):
    return {"event_label": label, "onset": onset, "offset": offset}


REFERENCE = {"a": [ev("horn", 0, 2), ev("birds", 5, 9)], "b": [ev("horn", 1, 3)], "c": []}
ESTIMATE = {"a": [ev("horn", 0.1, 2.1), ev("train", 5, 9)], "b": [], "c": [ev("birds", 0, 1)]}


def test_summed_counts_reproduce_sed_eval_micro_f1() -> None:
    pytest.importorskip("sed_eval")
    labels = ["horn", "birds", "train"]
    counts = event_counts_per_recording(REFERENCE, ESTIMATE, event_label_list=labels)
    totals = [sum(c[i] for c in counts.values()) for i in range(3)]
    full = event_based_f1(REFERENCE, ESTIMATE, event_label_list=labels)
    assert set(counts) == {"a", "b", "c"}
    assert micro_f1(*totals) == pytest.approx(full["f_measure"]["f_measure"])


def test_paired_bootstrap_means_and_difference() -> None:
    better = {f"r{i}": (4, 4, 3) for i in range(20)}
    worse = {f"r{i}": (4, 4, 1) for i in range(20)}
    result = paired_branch_bootstrap({"b1": worse, "b2": worse, "c1": better},
                                     {"B": ["b1", "b2"], "C": ["c1"]}, n_bootstrap=200)
    assert result["branches"]["B"]["estimate"] == pytest.approx(0.25)
    assert result["branches"]["C"]["estimate"] == pytest.approx(0.75)
    diff = result["differences"]["C-B"]
    assert diff["estimate"] == pytest.approx(0.5) and diff["lower"] == pytest.approx(0.5)


def test_runs_on_different_recordings_are_rejected() -> None:
    with pytest.raises(ValueError):
        paired_branch_bootstrap({"b": {"r1": (1, 1, 1), "r2": (1, 1, 0)}, "c": {"r1": (1, 1, 1)}},
                                {"B": ["b"], "C": ["c"]}, n_bootstrap=10)


def test_a4_verdict_and_cap_follow_adr_0028() -> None:
    from scripts.report_pos_weight_ablation import MARGIN, cap_of, verdict

    assert verdict(0.10 + MARGIN + 1e-6, 0.10) == "tốt hơn"
    assert verdict(0.10 - MARGIN - 1e-6, 0.10) == "kém hơn"
    assert verdict(0.10 + MARGIN / 2, 0.10) == "không phân biệt được"
    assert cap_of({"config": {}}) == 50.0  # runs before the flag used the default cap
    assert cap_of({"config": {"pos_weight_cap": None}}) == float("inf")
    assert cap_of({"config": {"pos_weight_cap": 10.0}}) == 10.0
