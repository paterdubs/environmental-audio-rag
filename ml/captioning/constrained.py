"""Constrained LLM captioner for RQ2 — same model and prompt as the
unconstrained branch, plus an input-dependent GBNF grammar (ADR-0023).

The grammar admits ONE sentence listing a subsequence of the timeline events
in onset order, each at most once: ``<source phrase> can be heard from <onset>
to <offset> seconds, <source phrase> [can be heard] from … and …``. Source
phrases are recognised by the frozen lexicon as their class, and times are the
event's own boundaries — so G1, G3, context terms, over-specific naming,
invented times, wrong order and repeats are impossible by construction. The
model still chooses WHICH events to mention and when to stop: omission is the
dimension left to measure.

Two smoke-test failures shaped this (ADR-0023): one event per sentence made
the model — asked for ONE short caption by the shared prompt — stop after a
single event; a free list of items made greedy decoding repeat one item until
max_tokens. A sampling penalty would fix the latter but would make the
branches differ in more than the grammar.
"""

from __future__ import annotations

import re
from typing import Any

from .llm import ChatTransport, LLMConfig, build_request

EMPTY_TEXT = "No target sound event was detected in this recording."
VERBS = ("can be heard", "can be detected")
SEPARATORS = (", ", ", and ", " and ", ", followed by ", ", while ")
GROUPED_PHRASES = {
    "sirens_and_alarms": "a siren- or alarm-like sound",
    "thunder_fireworks_gunshot": "an impulsive sound resembling thunder, fireworks, or a gunshot",
}


def source_phrase(class_id: str) -> str:
    """Subject phrase for a class; same class wording as `TemplateCaptioner`."""
    if class_id in GROUPED_PHRASES:
        return GROUPED_PHRASES[class_id]
    return f"the sound of {class_id.replace('_', ' ')}"


def event_clause(event: dict[str, Any]) -> str:
    return f"from {event['onset_s']:.1f} to {event['offset_s']:.1f} seconds"


def _quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_grammar(timeline: dict[str, Any]) -> str:
    events = timeline["events"]
    if not events:
        return f"root ::= {_quote(EMPTY_TEXT)}"
    items = [(source_phrase(e["class_id"]), event_clause(e)) for e in events]
    n = len(items)
    # f<i>: the caption starts with event i; r<j>: events j.. may follow, in order.
    lines = [
        "root ::= (" + " | ".join(f"f{i}" for i in range(n)) + ') "."',
        f"separator ::= {' | '.join(_quote(s) for s in SEPARATORS)}",
        f"verb ::= {' | '.join(_quote(' ' + v) for v in VERBS)}",
    ]
    for i, (phrase, clause) in enumerate(items):
        head = _quote(phrase[0].upper() + phrase[1:]) + " verb " + _quote(" " + clause)
        lines.append(f"f{i} ::= {head}" + (f" r{i + 1}" if i + 1 < n else ""))
        if i > 0:
            item = _quote(phrase) + " verb? " + _quote(" " + clause)
            rest = f" r{i + 1}" if i + 1 < n else ""
            lines.append(f"r{i} ::= (separator {item})?{rest}")
    return "\n".join(lines)


def align_evidence(text: str, timeline: dict[str, Any]) -> list[dict[str, Any]]:
    """Map each generated item back to the event it restates (G2).

    A repeated item claims the next still-unclaimed event with the same
    phrase and times; a repeat with nothing left to claim gets no evidence.
    """
    unclaimed = {}
    for event in timeline["events"]:
        key = (source_phrase(event["class_id"]).lower(), event_clause(event))
        unclaimed.setdefault(key, []).append(event["event_id"])
    evidence = []
    verbs = "|".join(re.escape(v) for v in VERBS)
    for phrase, clause in unclaimed.copy():
        pattern = re.compile(
            re.escape(phrase) + rf"(?: (?:{verbs}))? " + re.escape(clause), re.I
        )
        for match in pattern.finditer(text):
            ids = unclaimed[(phrase, clause)]
            if ids:
                evidence.append({"event_id": ids.pop(0),
                                 "mention_span": [match.start(), match.start() + len(phrase)]})
    return sorted(evidence, key=lambda item: item["mention_span"][0])


class ConstrainedLLMCaptioner:
    grounding_mode = "constrained"

    def __init__(self, transport: ChatTransport, config: LLMConfig):
        self.transport = transport
        self.config = config
        self.version = f"caption-grammar-v1+{config.model_name}"

    def caption(self, timeline: dict[str, Any], language: str = "en") -> dict[str, Any]:
        if language != "en":
            raise ValueError("RQ2 benchmark captions are English only (ADR-0004)")
        body = build_request(timeline, self.config, grammar=build_grammar(timeline))
        response = self.transport.complete(body)
        try:
            choice = response["choices"][0]
            text = choice["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"malformed LLM response: {response!r:.200}") from exc
        if not isinstance(text, str) or not text.strip():
            raise ValueError("LLM returned an empty caption")
        text = text.strip()
        return {
            "recording_id": timeline["recording_id"],
            "language": language,
            "text": text,
            "captioner_version": self.version,
            "grounding_mode": self.grounding_mode,
            "evidence": align_evidence(text, timeline),
            "generation": {
                "finish_reason": choice.get("finish_reason"),
                "predicted_tokens": response.get("usage", {}).get("completion_tokens"),
            },
        }
