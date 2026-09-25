"""Everything the inference service loads once: served SED, captioners, BGE-M3 (ADR-0029)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np
import torch

from ml.inference.pipeline import Analyzer
from ml.inference.sed import ServedSed
from ml.retrieval.embedding import Embedder
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[2]
SERVED_ENSEMBLE = ROOT / "ml/runs/sed_ensemble_C_clean_20260925T045631Z"
SERVED_POSTPROC = "postproc_cv.json"


class Engine:
    def __init__(self, device: str | None = None) -> None:
        name = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
        self.sed = ServedSed(SERVED_ENSEMBLE, SERVED_POSTPROC, self.taxonomy, torch.device(name))
        self.analyzer = Analyzer(self.sed, self.taxonomy)
        self.embedder = Embedder(device=name)
        self.device = name

    def analyze(self, recording_id: str, path: Path) -> dict[str, Any]:
        analysis = self.analyzer.analyze(recording_id, path)
        vector = self.embedder.encode([analysis["document"]["text"]])[0]
        return {**analysis, "embedding": vector.tolist(),
                "embedding_version": self.embedder.version}

    def embed(self, texts: Sequence[str]) -> np.ndarray:
        return self.embedder.encode(texts)

    def info(self) -> dict[str, Any]:
        return {"model_version": self.sed.model_version, "members": self.sed.member_ids,
                "postproc": SERVED_POSTPROC, "threshold_mode": self.sed.postproc["threshold_mode"],
                "taxonomy_version": self.taxonomy.version,
                "taxonomy_sha256": self.taxonomy.checksum,
                "embedding_version": self.embedder.version, "device": self.device}
