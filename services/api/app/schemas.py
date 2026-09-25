"""Request models of the API (SYSTEM §4.4). Class ids are checked against the taxonomy in the
route, not here, so the allowed list is never duplicated as constants (SYSTEM §4.2)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

Corpus = Literal["upload", "validation", "test"]


class Temporal(BaseModel):
    predicate: Literal["before", "after", "overlaps", "within"]
    a: str
    b: str
    tolerance_s: float = Field(default=0.0, ge=0.0, le=60.0)


class Duration(BaseModel):
    class_id: str
    min_s: float = Field(gt=0.0, le=600.0)


class Filters(BaseModel):
    classes_all: list[str] | None = Field(default=None, min_length=1, max_length=5)
    temporal: Temporal | None = None
    duration: Duration | None = None

    @model_validator(mode="after")
    def at_least_one(self) -> Filters:
        if not (self.classes_all or self.temporal or self.duration):
            raise ValueError("cần ít nhất một bộ lọc: classes_all, temporal hoặc duration")
        return self

    def as_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)

    def class_ids(self) -> set[str]:
        found = set(self.classes_all or [])
        if self.temporal:
            found |= {self.temporal.a, self.temporal.b}
        if self.duration:
            found.add(self.duration.class_id)
        return found


class QueryRequest(BaseModel):
    """Retrieval needs hard filters: the evidence-bound answer only cites events that satisfy
    them (SYSTEM §7.4). `vector_only` stays a benchmark mode (RQ3), not a user-facing one."""

    question: str = Field(min_length=1, max_length=500)
    filters: Filters
    mode: Literal["hybrid", "structured_only"] = "hybrid"
    corpus: Corpus = "upload"
    language: Literal["en", "vi"] = "vi"
    k: int = Field(default=10, ge=1, le=50)
