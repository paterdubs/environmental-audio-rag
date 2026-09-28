"""Shared Pydantic contract for structured retrieval filters (ADR-0036)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Temporal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    predicate: Literal["before", "after", "overlaps", "within"]
    a: str
    b: str
    tolerance_s: float = Field(default=0.0, ge=0.0, le=60.0)


class Duration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    class_id: str
    min_s: float = Field(gt=0.0, le=600.0)


class Filters(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
