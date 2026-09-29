"""Audio file → timeline → template captions (EN, VI) → retrieval document (ADR-0029 §2–§3).

Mirrors the measured path step by step: `extract_logmel` with the members' feature config,
features rounded to float16 exactly as the stored `.npy` files, `ServedSed` for events, the
same `canonicalize_timeline` / `TemplateCaptioner` / `build_document` as the W5/W6 index.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import librosa
import numpy as np
import soundfile

from ml.captioning.lexicon import VI_LEXICON_CONFIG, CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.captioning.timeline import canonicalize_timeline
from ml.features.logmel import extract_logmel, load_logmel_config
from ml.inference.sed import ServedSed
from ml.retrieval.document_builder import build_document
from ml.taxonomy import Taxonomy


@dataclass(frozen=True)
class AudioInfo:
    duration_s: float
    sample_rate: int
    channels: int


def audio_info(path: Path) -> AudioInfo:
    info = soundfile.info(str(path))
    return AudioInfo(float(info.duration), int(info.samplerate), int(info.channels))


def served_feature(path: Path, feature_set: str) -> np.ndarray:
    """Log-mel as training saw it: extracted, then stored/loaded through float16."""
    feature = extract_logmel(path, load_logmel_config(feature_set))
    return feature.astype(np.float16).astype(np.float32)


def served_waveform(path: Path) -> np.ndarray:
    """Match the Track-2 cache: librosa 16 kHz mono, then deterministic PCM16 quantisation."""
    waveform, _ = librosa.load(path, sr=16_000, mono=True)
    return np.clip(np.round(waveform * 32768.0), -32768, 32767).astype(np.int16)


class Analyzer:
    def __init__(self, sed: ServedSed, taxonomy: Taxonomy) -> None:
        self.sed = sed
        self.taxonomy = taxonomy
        self.captioners = {
            "en": TemplateCaptioner(CaptionLexicon.from_taxonomy(taxonomy)),
            "vi": TemplateCaptioner(CaptionLexicon.from_taxonomy(taxonomy,
                                                                  config=VI_LEXICON_CONFIG)),
        }

    def timeline(self, recording_id: str, signal: np.ndarray, *, total_frames: int | None = None
                 ) -> dict[str, Any]:
        probabilities = self.sed.probabilities(signal, total_frames=total_frames)
        duration = probabilities.shape[0] / self.sed.config.frame_rate
        return canonicalize_timeline(recording_id, duration, self.sed.events(probabilities),
                                     self.taxonomy, model_version=self.sed.model_version)

    def analyze(self, recording_id: str, path: Path) -> dict[str, Any]:
        feature = served_feature(path, self.sed.config.feature_set)
        signal = (served_waveform(path) if self.sed.config.input_kind == "waveform_16k"
                  else feature)
        timeline = self.timeline(recording_id, signal, total_frames=feature.shape[1])
        captions = {lang: c.caption(timeline, language=lang)
                    for lang, c in self.captioners.items()}
        document = build_document(captions["en"]["text"] + "\n" + captions["vi"]["text"],
                                  timeline)
        return {"timeline": timeline, "captions": captions, "document": document}
