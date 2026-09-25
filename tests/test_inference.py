from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from ml.inference.pipeline import Analyzer  # noqa: E402
from ml.inference.sed import MemberConfig, ServedSed  # noqa: E402
from ml.taxonomy import load_taxonomy  # noqa: E402

TAXONOMY = load_taxonomy(Path(__file__).parents[1] / "ml/configs/taxonomy.yaml")
CLASSES = TAXONOMY.polyphonic_class_ids


class ConstantModel(torch.nn.Module):
    """Logit `value` for class 0 everywhere, very negative elsewhere; shape [B, T, C]."""

    def __init__(self, value: float) -> None:
        super().__init__()
        self.value = value

    def forward(self, x):
        out = torch.full((x.shape[0], x.shape[-1], len(CLASSES)), -20.0)
        out[..., 0] = self.value
        return out


def served(values, window=100, hop=100) -> ServedSed:
    sed = object.__new__(ServedSed)
    sed.config = MemberConfig(frame_rate=10.0, window_frames=window, hop_frames=hop,
                              feature_set="logmel_panns_v1")
    sed.class_ids, sed.taxonomy_sha256 = CLASSES, TAXONOMY.checksum
    sed.device, sed.model_version = torch.device("cpu"), "sed-test"
    sed.members = [ConstantModel(v) for v in values]
    sed.member_ids = [f"m{i}" for i in range(len(values))]
    sed.postproc = {"per_class": {c: {"theta": 0.5, "median_w": 1, "d_min_s": 0.0,
                                      "g_max_s": 0.0, "n_train_events": 1} for c in CLASSES}}
    return sed


def test_windows_cover_every_frame_with_an_end_aligned_last_window() -> None:
    artifact = served([0.0]).artifacts(np.zeros((64, 250), np.float32))[0]
    assert artifact.frame_offsets_s.tolist() == [0.0, 10.0, 15.0]  # starts 0, 100, 150
    assert artifact.mask.all()


def test_short_recording_is_zero_padded_and_masked() -> None:
    artifact = served([0.0]).artifacts(np.zeros((64, 40), np.float32))[0]
    assert artifact.mask.sum() == 40 and not artifact.mask[0, 40:].any()
    assert served([0.0]).probabilities(np.zeros((64, 40), np.float32)).shape == (40, len(CLASSES))


def test_members_are_averaged_in_probability_space_then_postprocessed() -> None:
    sed = served([4.0, -4.0])  # sigmoid mean = 0.5 → not above θ = 0.5
    probabilities = sed.probabilities(np.zeros((64, 120), np.float32))
    assert np.allclose(probabilities[:, 0], 0.5, atol=1e-6)
    positive = served([4.0, 2.0])
    events = positive.events(positive.probabilities(np.zeros((64, 120), np.float32)))
    spans = [(e["event_label"], e["onset"], e["offset"]) for e in events]
    assert spans == [(CLASSES[0], 0.0, 12.0)]


def test_analyzer_produces_grounded_captions_in_both_languages_and_a_document() -> None:
    analyzer = Analyzer(served([4.0]), TAXONOMY)
    timeline = analyzer.timeline("upload:x", np.zeros((64, 120), np.float32))
    assert timeline["model_version"] == "sed-test" and len(timeline["events"]) == 1
    captions = {lang: c.caption(timeline, language=lang)
                for lang, c in analyzer.captioners.items()}
    assert "12.0" in captions["en"]["text"] and "12,0" in captions["vi"]["text"]
    assert all(c["evidence"] for c in captions.values())
