import pytest

pytest.importorskip("pycocoevalcap")

from scripts.report_caption_ngram import ngram_scores, tokenize  # noqa: E402


def test_tokenizer_keeps_decimals_and_hyphenated_words() -> None:
    assert tokenize("A siren- or alarm-like sound, from 12.4 to 13.1 seconds.") == (
        "a siren or alarm-like sound from 12.4 to 13.1 seconds")


def test_identical_captions_score_perfect_bleu_and_differ_from_paraphrase() -> None:
    refs = {"1": "A bird is audible from 0.0 to 2.0 seconds.",
            "2": "Music is audible from 1.0 to 3.0 seconds."}
    same = ngram_scores(refs, dict(refs))
    paraphrase = ngram_scores(refs, {"1": "Birds chirp briefly.", "2": "Music plays."})
    assert same["bleu_4"] == pytest.approx(1.0)
    assert paraphrase["bleu_4"] < same["bleu_4"] and paraphrase["cider"] < same["cider"]
    assert same["n"] == 2
