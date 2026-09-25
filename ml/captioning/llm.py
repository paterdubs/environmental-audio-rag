"""LLM captioner for the RQ2 unconstrained (control) branch — ADR-0022.

The model sees only the event timeline (SYSTEM.md §6.1), rendered by
``build_user_prompt``. The constrained branch must reuse the exact same prompt
and generation settings and differ only by a decoding grammar; otherwise the
RQ2 delta mixes the constraint with a prompt or model change.

Unlike ``TemplateCaptioner`` this captioner does NOT call ``assert_safe``:
G1-G3 violations of free generation are the quantity RQ2 measures, so they
must be recorded, not rejected.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import yaml

PROMPT_VERSION = "caption-prompt-v1"
SYSTEM_PROMPT = (
    "You write one short English caption describing an environmental audio recording."
)
USER_TEMPLATE = (
    "Recording duration: {duration:.1f} s.\n"
    "Detected sound events (JSON):\n{events}\n"
    "Write a caption for this recording."
)


@dataclass(frozen=True)
class LLMConfig:
    model_name: str
    model_file: str
    model_sha256: str
    model_local_path: str
    runtime_build: str
    endpoint: str
    temperature: float
    seed: int
    max_tokens: int
    enable_thinking: bool
    timeout_s: float

    @classmethod
    def from_yaml(cls, path: Path) -> LLMConfig:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        model, runtime, gen = raw["model"], raw["runtime"], raw["generation"]
        return cls(
            model_name=model["name"],
            model_file=model["file"],
            model_sha256=model["sha256"],
            model_local_path=model["local_path"],
            runtime_build=runtime["build"],
            endpoint=runtime["endpoint"].rstrip("/"),
            temperature=float(gen["temperature"]),
            seed=int(gen["seed"]),
            max_tokens=int(gen["max_tokens"]),
            enable_thinking=bool(gen["enable_thinking"]),
            timeout_s=float(gen["timeout_s"]),
        )


class ChatTransport(Protocol):
    def complete(self, body: dict[str, Any]) -> dict[str, Any]: ...


class TokenCounter(Protocol):
    def count_tokens(self, text: str) -> int: ...


class HttpChatTransport:
    """OpenAI-compatible ``/v1/chat/completions`` client (llama.cpp server)."""

    def __init__(self, endpoint: str, timeout_s: float):
        self.url = endpoint.rstrip("/") + "/v1/chat/completions"
        self.timeout_s = timeout_s

    def complete(self, body: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            self.url, json.dumps(body).encode("utf-8"), {"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
            return json.load(response)

    def count_tokens(self, text: str) -> int:
        """Tokens the served model's tokenizer uses for `text` (llama.cpp `/tokenize`)."""
        url = self.url.removesuffix("/v1/chat/completions") + "/tokenize"
        request = urllib.request.Request(
            url, json.dumps({"content": text}).encode("utf-8"),
            {"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
            return len(json.load(response)["tokens"])


def build_user_prompt(timeline: dict[str, Any]) -> str:
    """Render the timeline without scores so oracle and end-to-end prompts share a format."""
    events = [
        {
            "class_id": event["class_id"],
            "onset_s": round(float(event["onset_s"]), 2),
            "offset_s": round(float(event["offset_s"]), 2),
        }
        for event in timeline["events"]
    ]
    return USER_TEMPLATE.format(duration=timeline["duration_s"], events=json.dumps(events))


def prompt_sha256() -> str:
    """Hash of the prompt contract; changes whenever the wording changes."""
    payload = json.dumps(
        {"version": PROMPT_VERSION, "system": SYSTEM_PROMPT, "user": USER_TEMPLATE},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_request(
    timeline: dict[str, Any], config: LLMConfig, grammar: str | None = None,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(timeline)},
        ],
        "temperature": config.temperature,
        "seed": config.seed,
        "max_tokens": config.max_tokens if max_tokens is None else max_tokens,
        "chat_template_kwargs": {"enable_thinking": config.enable_thinking},
    }
    if grammar is not None:
        body["grammar"] = grammar
    return body


class UnconstrainedLLMCaptioner:
    grounding_mode = "unconstrained"

    def __init__(self, transport: ChatTransport, config: LLMConfig):
        self.transport = transport
        self.config = config
        self.version = f"{PROMPT_VERSION}+{config.model_name}"

    def caption(self, timeline: dict[str, Any], language: str = "en") -> dict[str, Any]:
        if language != "en":
            raise ValueError("RQ2 benchmark captions are English only (ADR-0004)")
        response = self.transport.complete(build_request(timeline, self.config))
        try:
            choice = response["choices"][0]
            text = choice["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"malformed LLM response: {response!r:.200}") from exc
        if not isinstance(text, str) or not text.strip():
            raise ValueError("LLM returned an empty caption")
        return {
            "recording_id": timeline["recording_id"],
            "language": language,
            "text": text.strip(),
            "captioner_version": self.version,
            "grounding_mode": self.grounding_mode,
            # Free generation cites no event: G2 coverage is 0 by construction.
            "evidence": [],
            "generation": {
                "finish_reason": choice.get("finish_reason"),
                "predicted_tokens": response.get("usage", {}).get("completion_tokens"),
            },
        }
