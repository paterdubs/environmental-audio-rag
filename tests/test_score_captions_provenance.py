"""Provenance của `score_captions` khi run không có `metrics.json` (run LBR, ADR-0048)."""

import json
from pathlib import Path

import pytest

from ml.captioning.lexicon import CaptionLexicon
from ml.taxonomy import load_taxonomy
from scripts.score_captions import provenance

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def lexicon() -> CaptionLexicon:
    return CaptionLexicon.from_taxonomy(load_taxonomy(ROOT / "ml/configs/taxonomy.yaml"))


def _run(tmp_path: Path, lexicon: CaptionLexicon, *, meta_hash: str | None,
         metrics_hash: str | None) -> list[Path]:
    run = tmp_path / "sed_lbr_x"
    (run / "captions").mkdir(parents=True)
    manifest = {"taxonomy_sha256": lexicon.taxonomy.checksum, "split_sha256": "s" * 64}
    (run / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    if metrics_hash is not None:
        (run / "metrics.json").write_text(json.dumps({"test_predictions_sha256": metrics_hash}),
                                          encoding="utf-8")
    source = run / "captions" / "constrained_test.jsonl"
    source.write_text("", encoding="utf-8")
    meta = {"output_sha256": "o" * 64, "postproc_sha256": "p" * 64}
    if meta_hash is not None:
        meta["predictions_sha256"] = meta_hash
    source.with_suffix(".meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return [source]


def test_run_without_metrics_uses_the_prediction_hash_recorded_by_the_caption_meta(
        tmp_path, lexicon):
    sources = _run(tmp_path, lexicon, meta_hash="a" * 64, metrics_hash=None)
    result = provenance(sources[0].parents[1], "test", sources, lexicon, "annotated")
    assert result["predictions_sha256"] == "a" * 64
    assert result["postproc_sha256"] == "p" * 64


def test_old_caption_meta_without_hash_still_falls_back_to_metrics(tmp_path, lexicon):
    sources = _run(tmp_path, lexicon, meta_hash=None, metrics_hash="b" * 64)
    result = provenance(sources[0].parents[1], "test", sources, lexicon, "all")
    assert result["predictions_sha256"] == "b" * 64


def test_no_prediction_hash_anywhere_is_an_explicit_error(tmp_path, lexicon):
    sources = _run(tmp_path, lexicon, meta_hash=None, metrics_hash=None)
    with pytest.raises(SystemExit, match="predictions_sha256"):
        provenance(sources[0].parents[1], "test", sources, lexicon, "all")
