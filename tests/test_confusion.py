from ml.evaluation.confusion import substitutions, unordered


def ev(label, onset, offset):
    return {"event_label": label, "onset": onset, "offset": offset}


def test_missed_reference_overlapped_by_false_positive_is_a_substitution() -> None:
    counts, seconds = substitutions({"r": [ev("horn", 0, 4)]}, {"r": [ev("sirens", 1, 3)]})
    assert counts == {("horn", "sirens"): 1}
    assert seconds[("horn", "sirens")] == 2.0


def test_polyphony_is_not_counted_as_confusion() -> None:
    # birds is real and detected; voices is detected too: nothing is substituted.
    reference = {"r": [ev("voices", 0, 10), ev("birds", 2, 5)]}
    estimate = {"r": [ev("voices", 0, 9), ev("birds", 2, 4)]}
    assert substitutions(reference, estimate)[0] == {}


def test_detected_reference_or_true_positive_estimate_is_excluded() -> None:
    # horn is detected, so the extra sirens estimate is an insertion, not a substitution.
    reference = {"r": [ev("horn", 0, 4)]}
    estimate = {"r": [ev("horn", 0, 4), ev("sirens", 1, 3)]}
    assert substitutions(reference, estimate)[0] == {}
    # sirens estimate is backed by a real sirens event: missed horn is a deletion only.
    reference = {"r": [ev("horn", 0, 4), ev("sirens", 1, 3)]}
    assert substitutions(reference, {"r": [ev("sirens", 1, 3)]})[0] == {}


def test_touching_events_do_not_overlap_and_pairs_fold() -> None:
    assert substitutions({"r": [ev("a", 0, 2)]}, {"r": [ev("b", 2, 4)]})[0] == {}
    assert unordered({("b", "a"): 2, ("a", "b"): 1}) == {("a", "b"): 3}


def test_hypothesis_pairs_read_only_the_acoustic_table() -> None:
    from pathlib import Path

    from ml.taxonomy import load_taxonomy
    from scripts.report_confusable_pairs import hypothesis_pairs

    taxonomy = load_taxonomy(Path(__file__).parents[1] / "ml/configs/taxonomy.yaml")
    pairs = hypothesis_pairs(taxonomy.class_ids)
    assert len(pairs) == 15  # §8.1 measured table uses the same row format
    assert ("chicken_coop", "jet_aircrafts") not in pairs
