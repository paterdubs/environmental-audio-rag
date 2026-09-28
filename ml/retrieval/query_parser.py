"""Constrained EN/VI question-to-filter parser over llama.cpp HTTP (ADR-0036).

This module is deliberately torch-free so the API process can import it. The generated JSON
Schema derives class and predicate enums from their source-of-truth objects instead of copying
either list into the prompt or code.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Protocol

import yaml
from pydantic import ValidationError

from ml.retrieval.filters import Filters
from ml.retrieval.temporal import PREDICATES

PROMPT_VERSION = "query-filter-prompt-v1.1"
SYSTEM_PROMPT = """You convert an environmental-audio search question into one JSON filter.
Return JSON only. Use only class_id values from the supplied taxonomy and predicates from the
supplied predicate list. Do not answer the question. Preserve temporal direction: a is the event
described before/after/overlapping/within b. Use tolerance_s 0.0 unless the question states one."""
FEW_SHOTS = (
    ("en", "Find recordings with birds.", {"classes_all": ["birds"]}),
    ("vi", "Tìm đoạn có cả tiếng nhạc và tiếng người.",
     {"classes_all": ["music", "voices"]}),
    ("en", "Where are birds heard before a horn?", {"temporal": {
        "predicate": "before", "a": "birds", "b": "horn", "tolerance_s": 0.0}}),
    ("vi", "Tiếng tàu kéo dài hơn 10 giây ở bản nào?",
     {"duration": {"class_id": "train", "min_s": 10.0}}),
)


class QueryParserUnavailable(RuntimeError):
    """llama.cpp could not be reached."""


class QueryParserInvalid(RuntimeError):
    """llama.cpp returned output that violates the locked filter contract."""


class ChatTransport(Protocol):
    def complete(self, body: dict[str, Any]) -> dict[str, Any]: ...


class HttpChatTransport:
    def __init__(self, endpoint: str, timeout_s: float):
        self.url = endpoint.rstrip("/") + "/v1/chat/completions"
        self.timeout_s = timeout_s

    def complete(self, body: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            self.url, json.dumps(body).encode("utf-8"), {"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            message = f"LLM parser không sẵn sàng tại {self.url}: {exc}"
            raise QueryParserUnavailable(message) from exc


@dataclass(frozen=True)
class ParserConfig:
    model_name: str
    endpoint: str
    temperature: float
    seed: int
    max_tokens: int
    enable_thinking: bool
    timeout_s: float

    @classmethod
    def from_yaml(cls, path: Path) -> ParserConfig:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        model, runtime, generation = raw["model"], raw["runtime"], raw["generation"]
        return cls(
            model_name=model["name"],
            endpoint=os.environ.get("EARAG_LLM_ENDPOINT", runtime["endpoint"]).rstrip("/"),
            temperature=0.0,
            seed=20260922,
            max_tokens=min(256, int(generation["max_tokens"])),
            enable_thinking=False,
            timeout_s=float(generation["timeout_s"]),
        )


@dataclass(frozen=True)
class ParsedFilters:
    filters: Filters
    raw: str


def filter_json_schema(class_ids: Sequence[str]) -> dict[str, Any]:
    """Build llama.cpp's constrained schema from Pydantic + taxonomy + predicates."""
    pydantic_schema = Filters.model_json_schema()
    allowed = list(class_ids)
    classes_all = deepcopy(pydantic_schema["properties"]["classes_all"]["anyOf"][0])
    classes_all["items"]["enum"] = allowed
    temporal = deepcopy(pydantic_schema["$defs"]["Temporal"])
    temporal["properties"]["predicate"]["enum"] = list(PREDICATES)
    temporal["properties"]["a"]["enum"] = allowed
    temporal["properties"]["b"]["enum"] = allowed
    temporal["required"].append("tolerance_s")
    duration = deepcopy(pydantic_schema["$defs"]["Duration"])
    duration["properties"]["class_id"]["enum"] = allowed
    # llama.cpp b11158 silently loses nested enum constraints through Pydantic's $refs, so
    # inline the two definitions. Bounds and object contracts still originate in Filters.
    variants = []
    for name, shape in (("classes_all", classes_all), ("temporal", temporal),
                        ("duration", duration)):
        variants.append({"type": "object", "additionalProperties": False,
                         "properties": {name: shape}, "required": [name]})
    return {"title": "Filters", "oneOf": variants}


def _messages(question: str, language: str, labels: Mapping[str, Mapping[str, str]]
              ) -> list[dict[str, str]]:
    taxonomy = [{"class_id": class_id, "en": names["en"], "vi": names["vi"]}
                for class_id, names in labels.items()]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for shot_language, shot_question, shot_filter in FEW_SHOTS:
        messages += [
            {"role": "user", "content": f"language={shot_language}\nquestion={shot_question}"},
            {"role": "assistant", "content": json.dumps(shot_filter, ensure_ascii=False)},
        ]
    messages.append({"role": "user", "content": (
        f"taxonomy={json.dumps(taxonomy, ensure_ascii=False)}\n"
        f"predicates={json.dumps(list(PREDICATES))}\n"
        f"language={language}\nquestion={question}")})
    return messages


class QueryParser:
    def __init__(self, transport: ChatTransport, config: ParserConfig,
                 labels: Mapping[str, Mapping[str, str]]):
        self.transport = transport
        self.config = config
        self.labels = dict(labels)
        self.class_ids = tuple(labels)

    @classmethod
    def from_config(cls, config_path: Path, labels: Mapping[str, Mapping[str, str]],
                    transport_factory: Callable[[str, float], ChatTransport] = HttpChatTransport,
                    ) -> QueryParser:
        config = ParserConfig.from_yaml(config_path)
        return cls(transport_factory(config.endpoint, config.timeout_s), config, labels)

    def request_body(self, question: str, language: Literal["en", "vi"]) -> dict[str, Any]:
        schema = filter_json_schema(self.class_ids)
        return {
            "messages": _messages(question, language, self.labels),
            "temperature": self.config.temperature,
            "seed": self.config.seed,
            "max_tokens": self.config.max_tokens,
            "chat_template_kwargs": {"enable_thinking": self.config.enable_thinking},
            # llama.cpp b11158 reads the constrained schema from its top-level json_schema
            # extension. Its OpenAI-style nested json_schema object is silently ignored.
            "response_format": {"type": "json_object"},
            "json_schema": schema,
        }

    def parse(self, question: str, language: Literal["en", "vi"]) -> ParsedFilters:
        response = self.transport.complete(self.request_body(question, language))
        try:
            raw = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise QueryParserInvalid(f"phản hồi LLM sai cấu trúc: {response!r:.300}") from exc
        if not isinstance(raw, str) or not raw.strip():
            raise QueryParserInvalid("LLM parser trả nội dung rỗng")
        try:
            filters = Filters.model_validate_json(raw)
        except (ValidationError, ValueError) as exc:
            raise QueryParserInvalid(f"filter JSON không hợp lệ: {exc}") from exc
        unknown = sorted(filters.class_ids() - set(self.class_ids))
        if unknown:
            raise QueryParserInvalid(f"lớp ngoài 21 lớp SED: {unknown}")
        return ParsedFilters(filters, raw)
