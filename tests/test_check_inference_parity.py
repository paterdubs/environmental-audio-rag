from pathlib import Path

import pytest

from scripts import check_inference_parity as parity


def _no_git(root):
    raise FileNotFoundError("git")


def test_revision_uses_env_when_git_binary_missing(monkeypatch):
    monkeypatch.setattr(parity, "git_state", _no_git)
    monkeypatch.setenv("GIT_REVISION", "abc123")
    monkeypatch.setenv("GIT_DIRTY", "False")
    assert parity.revision() == {"revision": "abc123", "dirty": "False", "source": "env"}


def test_revision_refuses_without_git_or_env(monkeypatch):
    monkeypatch.setattr(parity, "git_state", _no_git)
    monkeypatch.delenv("GIT_REVISION", raising=False)
    with pytest.raises(RuntimeError, match="GIT_REVISION"):
        parity.revision()


def test_cli_accepts_custom_run_and_postproc() -> None:
    args = parity.parse_args(["--run", "ml/runs/example", "--reference-run",
                              "ml/runs/reference", "--postproc", "chosen.json"])
    assert args.run == Path("ml/runs/example") and args.postproc == "chosen.json"
    assert args.reference_run == Path("ml/runs/reference")


def test_custom_v2_output_name_comes_from_manifest(tmp_path) -> None:
    run = tmp_path / "run"
    run.mkdir()
    (run / "manifest.json").write_text(
        '{"config": {"ensemble_label": "v2"}}', encoding="utf-8")
    assert parity.output_stem(run, "cuda") == "inference_parity_v2_cuda"


def test_lbr_output_name_carries_run_point_and_device(tmp_path) -> None:
    lbr = tmp_path / "sed_lbr_B0v3_20261110T042337Z"
    assert (parity.output_stem(tmp_path, "cuda", (lbr, "recall_first"))
            == "inference_parity_sed_lbr_b0v3_20261110t042337z_recall_first_cuda")


def test_cli_accepts_lbr_run_and_point() -> None:
    args = parity.parse_args(["--lbr-run", "ml/runs/sed_lbr_x", "--lbr-point", "f1"])
    assert args.lbr_run == Path("ml/runs/sed_lbr_x") and args.lbr_point == "f1"
