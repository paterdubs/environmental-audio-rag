from pathlib import Path
from typing import Any

import pytest

from ml.captioning.lexicon import CaptionLexicon
from ml.captioning.llm import (
    LLMConfig,
    UnconstrainedLLMCaptioner,
    build_request,
    build_user_prompt,
    prompt_sha256,
)
from ml.captioning.timeline import canonicalize_timeline
from ml.evaluation.grounding import evaluate_grounding
from ml.taxonomy import load_taxonomy
from scripts.generate_llm_captions import check_test_gate

ROOT = Path(__file__).parents[1]
CONFIG = LLMConfig.from_yaml(ROOT / "ml" / "configs" / "caption_llm.yaml")


class FakeTransport:
    def __init__(self, response: dict[str, Any]):
        self.response = response
        self.bodies: list[dict[str, Any]] = []

    def complete(self, body: dict[str, Any]) -> dict[str, Any]:
        self.bodies.append(body)
        return self.response


def reply(text: str, finish: str = "stop") -> dict[str, Any]:
    return {"choices": [{"message": {"content": text}, "finish_reason": finish}],
            "usage": {"completion_tokens": 7}}


@pytest.fixture()
def taxonomy():
    return load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")


@pytest.fixture()
def timeline(taxonomy):
    return canonicalize_timeline(
        "datased:S-0001", 30.0,
        [{"class_id": "sirens_and_alarms", "onset_s": 1.234, "offset_s": 5.0, "score": 0.37},
         {"class_id": "birds", "onset_s": 10.0, "offset_s": 12.0, "score": 0.91}],
        taxonomy,
    )


def test_config_pins_model_hash_and_greedy_decoding() -> None:
    assert len(CONFIG.model_sha256) == 64
    assert CONFIG.temperature == 0.0
    assert CONFIG.enable_thinking is False


def test_prompt_omits_scores_so_oracle_and_e2e_share_a_format(timeline) -> None:
    prompt = build_user_prompt(timeline)
    assert "score" not in prompt and "0.37" not in prompt
    assert '"onset_s": 1.23' in prompt
    assert "30.0 s" in prompt


def test_unconstrained_request_has_no_grammar_and_pins_decoding(timeline) -> None:
    body = build_request(timeline, CONFIG)
    assert "grammar" not in body
    assert body["temperature"] == 0.0 and body["seed"] == CONFIG.seed
    assert body["chat_template_kwargs"] == {"enable_thinking": False}
    assert build_request(timeline, CONFIG, grammar='root ::= "x"')["grammar"] == 'root ::= "x"'


def test_prompt_hash_is_stable() -> None:
    assert prompt_sha256() == prompt_sha256()
    assert len(prompt_sha256()) == 64


def test_forbidden_output_is_recorded_not_rejected(timeline, taxonomy) -> None:
    """RQ2 measures G1-G3 violations of free generation, so they must survive."""
    transport = FakeTransport(reply("  Emergency sirens wail as birds sing.  "))
    caption = UnconstrainedLLMCaptioner(transport, CONFIG).caption(timeline)
    lexicon = CaptionLexicon.from_taxonomy(taxonomy)

    assert caption["text"] == "Emergency sirens wail as birds sing."
    assert caption["grounding_mode"] == "unconstrained"
    assert caption["evidence"] == []
    assert caption["generation"] == {"finish_reason": "stop", "predicted_tokens": 7}
    assert evaluate_grounding(timeline, caption, lexicon).forbidden_term_rate == 1.0


@pytest.mark.parametrize("response", [{}, {"choices": []}, reply("   ")])
def test_malformed_or_empty_response_fails_loudly(timeline, response) -> None:
    with pytest.raises(ValueError):
        UnconstrainedLLMCaptioner(FakeTransport(response), CONFIG).caption(timeline)


def test_test_split_requires_the_current_lexicon_hash() -> None:
    check_test_gate("dev", "a" * 64, None)
    check_test_gate("test", "a" * 64, "a" * 64)
    with pytest.raises(SystemExit, match="đóng băng"):
        check_test_gate("test", "a" * 64, None)
    with pytest.raises(SystemExit):
        check_test_gate("test", "a" * 64, "b" * 64)


def test_lexicon_hash_changes_when_a_phrase_changes(taxonomy) -> None:
    lexicon = CaptionLexicon.from_taxonomy(taxonomy)
    extended = CaptionLexicon(taxonomy, {**lexicon.phrases, "birds": ("birds", "bird")})
    assert lexicon.sha256() == CaptionLexicon.from_taxonomy(taxonomy).sha256()
    assert extended.sha256() != lexicon.sha256()
