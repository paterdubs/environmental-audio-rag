"""CLI caption LLM nhận event LBR (ADR-0048): cờ `--lbr-point`, provenance postproc đủ đường dẫn."""

import json
from pathlib import Path

import pytest

from ml.dataops.inventory import sha256_file
from scripts import generate_llm_captions as cli


def test_lbr_point_is_optional_and_limited_to_frozen_operating_points():
    assert cli.parse_args(["ml/runs/x"]).lbr_point is None
    assert cli.parse_args(["ml/runs/x", "--lbr-point", "recall_first"]).lbr_point == "recall_first"
    with pytest.raises(SystemExit):
        cli.parse_args(["ml/runs/x", "--lbr-point", "f2"])


def test_postproc_provenance_keeps_the_path_because_every_lbr_postproc_is_manifest_json(tmp_path):
    first = tmp_path / "sed_lbr_a" / "manifest.json"
    second = tmp_path / "sed_lbr_b" / "manifest.json"
    for path, body in ((first, {"a": 1}), (second, {"b": 2})):
        path.parent.mkdir()
        path.write_text(json.dumps(body), encoding="utf-8")
    a = cli.postproc_provenance(first, "f1", root=tmp_path)
    b = cli.postproc_provenance(second, None, root=tmp_path)
    assert a == {"postproc": "sed_lbr_a/manifest.json", "postproc_sha256": sha256_file(first),
                 "lbr_point": "f1"}
    assert b["postproc"] == "sed_lbr_b/manifest.json" and b["lbr_point"] is None
    assert a["postproc_sha256"] != b["postproc_sha256"]


def test_postproc_outside_the_repo_is_recorded_as_an_absolute_posix_path(tmp_path):
    path = tmp_path / "postproc.json"
    path.write_text("{}", encoding="utf-8")
    record = cli.postproc_provenance(path, None, root=tmp_path / "elsewhere")
    assert record["postproc"] == path.resolve().as_posix()


def test_e2e_level_forwards_lbr_point_and_default_postproc(monkeypatch, tmp_path):
    calls = []

    def fake(run_dir, split, taxonomy, postproc_path=None, predictions_run=None, lbr_point=None):
        calls.append((run_dir, split, postproc_path, predictions_run, lbr_point))
        return {"S-0001": {"events": []}}

    monkeypatch.setattr(cli, "e2e_timelines", fake)
    args = cli.parse_args([str(tmp_path / "run"), "--split", "dev", "--postproc",
                           str(tmp_path / "m.json"), "--lbr-point", "f1"])
    assert cli.e2e_level(args, taxonomy=None) == {"S-0001": {"events": []}}
    assert calls == [(tmp_path / "run", "dev", tmp_path / "m.json", tmp_path / "run", "f1")]
    assert cli.resolved_postproc(cli.parse_args([str(tmp_path / "run")])) == (
        tmp_path / "run" / "postproc.json")


def test_meta_has_the_lbr_point_field_even_for_non_lbr_runs():
    source = Path(cli.__file__).read_text(encoding="utf-8")
    assert "**postproc_provenance(" in source
