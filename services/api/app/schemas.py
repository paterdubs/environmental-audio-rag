"""Request models of the API (SYSTEM §4.4). Class ids are checked against the taxonomy in the
route, not here, so the allowed list is never duplicated as constants (SYSTEM §4.2)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ml.retrieval.filters import Duration, Filters, Temporal  # noqa: F401

Corpus = Literal["upload", "validation", "test"]


class QueryRequest(BaseModel):
    """Retrieval needs hard filters: the evidence-bound answer only cites events that satisfy
    them (SYSTEM §7.4). `vector_only` stays a benchmark mode (RQ3), not a user-facing one."""

    question: str = Field(min_length=1, max_length=500)
    filters: Filters | None = None
    mode: Literal["hybrid", "structured_only"] = "hybrid"
    corpus: Corpus = "upload"
    language: Literal["en", "vi"] = "vi"
    k: int = Field(default=10, ge=1, le=50)


class ParseRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    language: Literal["en", "vi"] = "vi"
