"""Everything the inference service loads once: served SED, captioners, BGE-M3 (ADR-0029)."""

from __future__ import annotations

import os
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
DEFAULT_SERVED_RUN = Path("ml/runs/sed_ensemble_t2b_20260927T200914Z")
DEFAULT_SERVED_POSTPROC = "sebb_cv_selection_annotated.json"
SERVED_ENSEMBLE = ROOT / DEFAULT_SERVED_RUN
SERVED_POSTPROC = DEFAULT_SERVED_POSTPROC


def served_settings() -> tuple[Path, str, bool]:
    """Resolve the frozen S13 winner, with an explicit local override for diagnostics."""
    relative = Path(os.environ.get("EARAG_SERVED_RUN", str(DEFAULT_SERVED_RUN)))
    if relative.is_absolute():
        raise ValueError("EARAG_SERVED_RUN must be relative to the repository root")
    run_dir = (ROOT / relative).resolve()
    try:
        run_dir.relative_to(ROOT.resolve())
    except ValueError:
        raise ValueError("EARAG_SERVED_RUN must stay inside the repository") from None
    postproc = os.environ.get("EARAG_SERVED_POSTPROC", DEFAULT_SERVED_POSTPROC)
    if Path(postproc).name != postproc:
        raise ValueError("EARAG_SERVED_POSTPROC must be a file name inside the served run")
    official = (run_dir == SERVED_ENSEMBLE.resolve()
                and postproc == DEFAULT_SERVED_POSTPROC)
    return run_dir, postproc, official


class Engine:
    def __init__(self, device: str | None = None) -> None:
        name = device or ("cuda" if torch.cuda.is_available() else "cpu")
        run_dir, postproc, official = served_settings()
        self.taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
        self.sed = ServedSed(run_dir, postproc, self.taxonomy, torch.device(name))
        self.analyzer = Analyzer(self.sed, self.taxonomy)
        self.embedder = Embedder(device=name)
        self.device = name
        self.served_run = run_dir.relative_to(ROOT).as_posix()
        self.served_postproc = postproc
        self.official = official

    def analyze(self, recording_id: str, path: Path) -> dict[str, Any]:
        analysis = self.analyzer.analyze(recording_id, path)
        vector = self.embedder.encode([analysis["document"]["text"]])[0]
        return {**analysis, "embedding": vector.tolist(),
                "embedding_version": self.embedder.version}

    def embed(self, texts: Sequence[str]) -> np.ndarray:
        return self.embedder.encode(texts)

    def info(self) -> dict[str, Any]:
        return {"model_version": self.sed.model_version, "members": self.sed.member_ids,
                "served_run": self.served_run, "official": self.official,
                "postproc": self.served_postproc,
                "threshold_mode": (self.sed.postproc.get("threshold_mode")
                                   if self.sed.postproc_family == "theta" else "csebb"),
                "taxonomy_version": self.taxonomy.version,
                "taxonomy_sha256": self.taxonomy.checksum,
                "embedding_version": self.embedder.version, "device": self.device}
