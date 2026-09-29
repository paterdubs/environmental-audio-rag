from pathlib import Path

import pytest

from ml.inference import engine


def test_served_settings_default_to_official_s13_f2(monkeypatch) -> None:
    monkeypatch.delenv("EARAG_SERVED_RUN", raising=False)
    monkeypatch.delenv("EARAG_SERVED_POSTPROC", raising=False)
    run, postproc, official = engine.served_settings()
    assert run == engine.SERVED_ENSEMBLE.resolve()
    assert postproc == "sebb_cv_selection_annotated.json"
    assert official is True


def test_served_settings_allow_override_without_making_it_official(monkeypatch) -> None:
    monkeypatch.setenv("EARAG_SERVED_RUN", "ml/runs/sed_ensemble_v2_20260926T150934Z")
    monkeypatch.setenv("EARAG_SERVED_POSTPROC", "postproc_cv.json")
    run, postproc, official = engine.served_settings()
    assert run == (engine.ROOT / Path("ml/runs/sed_ensemble_v2_20260926T150934Z")).resolve()
    assert postproc == "postproc_cv.json"
    assert official is False


def test_served_settings_reject_paths_outside_the_repository(monkeypatch) -> None:
    monkeypatch.setenv("EARAG_SERVED_RUN", "../outside")
    with pytest.raises(ValueError, match="repository"):
        engine.served_settings()
