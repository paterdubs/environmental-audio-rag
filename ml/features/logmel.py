from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, ClassVar

import librosa
import numpy as np
import yaml


@dataclass(frozen=True)
class LogMelConfig:
    sample_rate: int = 16_000
    n_fft: int = 1_024
    hop_length: int = 320
    n_mels: int = 64
    fmin: float = 20.0
    fmax: float = 8_000.0
    top_db: float = 80.0

    @property
    def frame_rate(self) -> float:
        return self.sample_rate / self.hop_length

    @property
    def checksum(self) -> str:
        encoded = json.dumps(asdict(self), sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class PannsLogMelConfig(LogMelConfig):
    """Frontend parameters used by the PANNs CNN14 implementation.

    PANNs uses 32 kHz audio, a 1024-sample Hann analysis window, 320-sample
    hop, and 64 mel bins spanning 50--14,000 Hz.  The inherited extraction
    function is deliberately reused so the feature orientation stays
    ``[mel, time]`` across both feature versions.
    """

    sample_rate: int = 32_000
    n_fft: int = 1_024
    hop_length: int = 320
    n_mels: int = 64
    fmin: float = 50.0
    fmax: float = 14_000.0
    top_db: float = 80.0

    name: ClassVar[str] = "logmel_panns_v1"


def load_logmel_config(name: str, config_path: Path | None = None) -> LogMelConfig:
    """Load a named log-mel configuration from the repository YAML file."""

    path = config_path or Path(__file__).parents[1] / "configs" / "features.yaml"
    raw: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    try:
        entry = raw["features"][name]
        params = dict(entry["parameters"])
    except (KeyError, TypeError) as exc:
        raise ValueError(f"Unknown or malformed log-mel configuration: {name}") from exc

    config_type = entry.get("type")
    if config_type == "panns":
        config_class: type[LogMelConfig] = PannsLogMelConfig
    elif config_type == "librosa":
        config_class = LogMelConfig
    else:
        raise ValueError(f"Unsupported log-mel configuration type: {config_type}")
    return config_class(**params)


def waveform_to_logmel(waveform: np.ndarray, config: LogMelConfig) -> np.ndarray:
    if waveform.ndim != 1:
        raise ValueError("Expected mono waveform")
    if waveform.size == 0:
        raise ValueError("Cannot extract features from empty audio")
    mel = librosa.feature.melspectrogram(
        y=waveform.astype(np.float32, copy=False),
        sr=config.sample_rate,
        n_fft=config.n_fft,
        hop_length=config.hop_length,
        n_mels=config.n_mels,
        fmin=config.fmin,
        fmax=config.fmax,
        power=2.0,
    )
    decibels = librosa.power_to_db(mel, ref=np.max, top_db=config.top_db)
    normalized = (decibels + config.top_db) / config.top_db
    return np.clip(normalized, 0.0, 1.0).astype(np.float32)


def extract_logmel(audio_path: Path, config: LogMelConfig) -> np.ndarray:
    waveform, _ = librosa.load(audio_path, sr=config.sample_rate, mono=True)
    return waveform_to_logmel(waveform, config)


def save_feature(feature: np.ndarray, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.save(handle, feature.astype(np.float16, copy=False), allow_pickle=False)
    temporary.replace(destination)
