"""Average frozen SED predictions of several runs (optimisation step 1).

Members must be window-aligned (same recordings, offsets, masks, targets,
split and class order); anything else means they did not see the same input
and averaging would mix frames. Probabilities are averaged, then mapped back to
logits so the result is an ordinary `PredictionArtifact`.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from ml.evaluation.predictions import PredictionArtifact

EPS = 1e-7


def average_predictions(members: Sequence[PredictionArtifact]) -> PredictionArtifact:
    if len(members) < 2:
        raise ValueError("an ensemble needs at least two members")
    first = members[0]
    for index, other in enumerate(members[1:], start=1):
        for field in ("recording_ids", "frame_offsets_s", "mask", "targets"):
            if not np.array_equal(getattr(first, field), getattr(other, field)):
                raise ValueError(f"member {index} differs from member 0 in {field}")
        for field in ("class_ids", "split", "frame_hop_s", "taxonomy_sha256"):
            if getattr(first, field) != getattr(other, field):
                raise ValueError(f"member {index} differs from member 0 in {field}")
    probabilities = np.mean(
        [1.0 / (1.0 + np.exp(-m.logits.astype(np.float64))) for m in members], axis=0
    )
    probabilities = np.clip(probabilities, EPS, 1.0 - EPS)
    logits = np.log(probabilities / (1.0 - probabilities)).astype(np.float32)
    return PredictionArtifact(
        logits=logits, targets=first.targets, recording_ids=first.recording_ids,
        frame_offsets_s=first.frame_offsets_s, mask=first.mask, class_ids=first.class_ids,
        split=first.split, model_version="sed-ensemble-v1.0", frame_hop_s=first.frame_hop_s,
        taxonomy_sha256=first.taxonomy_sha256,
    )
