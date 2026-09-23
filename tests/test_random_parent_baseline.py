from __future__ import annotations

import pytest

from ml.evaluation.random_parent_baseline import uniform_parent_baseline
from ml.taxonomy import Taxonomy, TaxonomyClass


def taxonomy() -> Taxonomy:
    return Taxonomy(
        version="test",
        checksum="checksum",
        classes=(
            TaxonomyClass("first", "First", (), ("a", "b"), True),
            TaxonomyClass("second", "Second", (), ("c", "d", "e", "f"), True),
            TaxonomyClass("plain", "Plain", (), (), True),
        ),
    )


def test_uniform_parent_baseline_uses_true_event_counts_and_excludes_plain_classes() -> None:
    baseline = uniform_parent_baseline(["first", "first", "first", "second", "plain"], taxonomy())

    assert baseline.included_events == 4
    assert baseline.excluded_events == 1
    assert baseline.value == pytest.approx((3 * 2 + 4) / (4 * 28))


def test_uniform_parent_baseline_rejects_unknown_event_classes() -> None:
    with pytest.raises(ValueError, match="Unknown DataSED"):
        uniform_parent_baseline(["unknown"], taxonomy())
