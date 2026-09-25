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

Cover variant (ADR-0026, ``cover=True``): the FIRST event of every class becomes
mandatory, later events of a class stay optional, onset order is unchanged. Class
omission is then impossible by construction; the only difference from the plain
branch is that one constraint, so comparing the two isolates its cost and benefit.

Token budget (ADR-0023 §7): the grammar bounds the caption length, so each request
gets ``max(max_tokens, characters of the longest admissible caption + 1)``. With the
shared 256-token cap, 16/558 captions were cut mid-sentence — breaking the very
contract the grammar is meant to guarantee. The bound is in CHARACTERS on purpose:
grammar text is ASCII, so every generated token spells at least one character (+1 for
end-of-sequence). A tokenizer count of the longest caption is NOT a bound — decoding
under a grammar emitted ~2 chars/token where canonical tokenization packs ~2.8, and 3
dev captions were still cut with that budget (v1.1). A larger cap does not change a
caption that ends on its own (checked: same text at 256 and at the full bound).

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


def first_occurrences(events: list[dict[str, Any]]) -> set[int]:
    """Indices of the earliest event of each class (events are in onset order)."""
    seen: set[str] = set()
    first = set()
    for index, event in enumerate(events):
        if event["class_id"] not in seen:
            seen.add(event["class_id"])
            first.add(index)
    return first


def build_grammar(timeline: dict[str, Any], cover: bool = False) -> str:
    events = timeline["events"]
    if not events:
        return f"root ::= {_quote(EMPTY_TEXT)}"
    items = [(source_phrase(e["class_id"]), event_clause(e)) for e in events]
    n = len(items)
    mandatory = first_occurrences(events) if cover else set()
    # f<i>: the caption starts with event i; r<j>: events j.. may follow, in order.
    # Cover: event 0 is a first occurrence, so the caption must start there.
    starts = [0] if cover else list(range(n))
    lines = [
        "root ::= (" + " | ".join(f"f{i}" for i in starts) + ') "."',
        f"separator ::= {' | '.join(_quote(s) for s in SEPARATORS)}",
        f"verb ::= {' | '.join(_quote(' ' + v) for v in VERBS)}",
    ]
    for i, (phrase, clause) in enumerate(items):
        head = _quote(phrase[0].upper() + phrase[1:]) + " verb " + _quote(" " + clause)
        if i in starts:
            lines.append(f"f{i} ::= {head}" + (f" r{i + 1}" if i + 1 < n else ""))
        if i > 0:
            item = "separator " + _quote(phrase) + " verb? " + _quote(" " + clause)
            rest = f" r{i + 1}" if i + 1 < n else ""
            body = item if i in mandatory else f"({item})?"
            lines.append(f"r{i} ::= {body}{rest}")
    return "\n".join(lines)


def longest_caption(timeline: dict[str, Any]) -> str:
    """The longest text `build_grammar` admits: every event, longest verb and separator."""
    events = timeline["events"]
    if not events:
        return EMPTY_TEXT
    verb, separator = max(VERBS, key=len), max(SEPARATORS, key=len)
    parts = []
    for index, event in enumerate(events):
        phrase = source_phrase(event["class_id"])
        if index == 0:
            parts.append(f"{phrase[0].upper()}{phrase[1:]} {verb} {event_clause(event)}")
        else:
            parts.append(f"{separator}{phrase} {verb} {event_clause(event)}")
    return "".join(parts) + "."


def token_budget(timeline: dict[str, Any], floor: int) -> int:
    """Tokens that can never be exhausted: one per character of the longest caption, +1."""
    return max(floor, len(longest_caption(timeline)) + 1)


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

    cover = False
    grammar_version = "caption-grammar-v1.2"

    def __init__(self, transport: ChatTransport, config: LLMConfig):
        self.transport = transport
        self.config = config
        self.version = f"{self.grammar_version}+{config.model_name}"

    def caption(self, timeline: dict[str, Any], language: str = "en") -> dict[str, Any]:
        if language != "en":
            raise ValueError("RQ2 benchmark captions are English only (ADR-0004)")
        budget = token_budget(timeline, self.config.max_tokens)
        body = build_request(timeline, self.config,
                             grammar=build_grammar(timeline, cover=self.cover),
                             max_tokens=budget)
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
                "token_budget": budget,
            },
        }


class CoverConstrainedLLMCaptioner(ConstrainedLLMCaptioner):
    """Constrained branch that must mention every class at least once (ADR-0026)."""

    cover = True
    grammar_version = "caption-grammar-cover-v1"
