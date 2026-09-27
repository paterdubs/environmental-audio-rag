"""Build the SED model a run was trained with, from its manifest config.

Training (`scripts.train_sed`) and serving (`ml.inference.sed`) both go through here, so a
served member is constructed exactly like the run that produced its numbers. Keys absent
from a manifest mean the v1 architecture of every RQ1 run (ADR-0020); SED v2 runs record
their own (ADR-0030).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ml.models.audio import SoundEventDetector
from ml.models.embedding_sed import EmbeddingSequenceSED
from ml.models.panns import PannsCNN14Encoder

V1_ARCHITECTURE: dict[str, Any] = {
    "time_pooling": [2, 2, 2, 2, 2, 2],
    "rnn_hidden": 128,
    "rnn_layers": 1,
    "upsample": "before_rnn",
}


def sed_architecture(config: Mapping[str, Any]) -> dict[str, Any]:
    return {key: config.get(key, default) for key, default in V1_ARCHITECTURE.items()}


def panns_encoder(config: Mapping[str, Any], **kwargs: Any) -> PannsCNN14Encoder:
    time_pooling = tuple(int(p) for p in sed_architecture(config)["time_pooling"])
    return PannsCNN14Encoder(time_pooling=time_pooling, **kwargs)


def embedding_head(config: Mapping[str, Any], classes: int) -> EmbeddingSequenceSED:
    """Track 2a head (ADR-0032 §2): the frozen encoder is not part of the model."""
    return EmbeddingSequenceSED(
        classes,
        input_size=int(config["embedding_dim"]),
        output_frames=int(config["window_frames"]),
        hidden_size=int(config["rnn_hidden"]),
        rnn_layers=int(config["rnn_layers"]),
    )


def sed_model(config: Mapping[str, Any], classes: int,
              encoder: PannsCNN14Encoder | None = None) -> SoundEventDetector:
    architecture = sed_architecture(config)
    return SoundEventDetector(
        classes=classes,
        encoder=encoder if encoder is not None else panns_encoder(config),
        hidden_size=int(architecture["rnn_hidden"]),
        rnn_layers=int(architecture["rnn_layers"]),
        upsample=str(architecture["upsample"]),
    )
