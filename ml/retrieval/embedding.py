"""BGE-M3 dense embeddings for retrieval (ADR-0004, ADR-0027).

Vectors are L2-normalised so cosine similarity is a dot product and matches pgvector's
``vector_cosine_ops``. The model lives in ``artifacts/hf`` (git-ignored); the exact
Hugging Face revision is recorded so an index can be tied to the weights that built it.
`sentence-transformers` is imported lazily — importing this module stays cheap.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np

MODEL_NAME = "BAAI/bge-m3"
DIMENSION = 1024
CACHE_DIR = Path(__file__).resolve().parents[2] / "artifacts" / "hf"
DOCUMENT_VERSION = "doc-v1-template-en-vi"


class Embedder:
    def __init__(self, device: str | None = None, cache_dir: Path = CACHE_DIR):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(MODEL_NAME, cache_folder=str(cache_dir), device=device)
        self.revision = _revision(cache_dir)

    @property
    def version(self) -> str:
        return f"{MODEL_NAME}@{self.revision[:12]}+{DOCUMENT_VERSION}"

    def encode(self, texts: Sequence[str], batch_size: int = 16) -> np.ndarray:
        vectors = self.model.encode(list(texts), batch_size=batch_size,
                                    normalize_embeddings=True, convert_to_numpy=True)
        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.ndim != 2 or vectors.shape[1] != DIMENSION:
            raise ValueError(f"expected (n, {DIMENSION}) embeddings, got {vectors.shape}")
        return vectors


def _revision(cache_dir: Path) -> str:
    """Commit hash that ``main`` resolved to when the model was cached.

    A second snapshot may exist holding only ``model.safetensors`` — transformers fetches
    that conversion of the same weights from a pull-request ref — so the repo revision is
    read from ``refs/main``, not guessed from the snapshot list.
    """
    ref = cache_dir / "models--BAAI--bge-m3" / "refs" / "main"
    if not ref.exists():
        raise RuntimeError(f"BGE-M3 is not cached under {cache_dir}")
    return ref.read_text(encoding="utf-8").strip()
