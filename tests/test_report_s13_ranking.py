import json
from pathlib import Path

import pytest

import scripts.report_s13_ranking as report_s13_ranking
from scripts.report_s13_ranking import load_candidate, rank_candidates


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _selection(
    family: str,
    mean: float,
    *,
    sd: float = 0.02,
    eval_set: str | None = "annotated",
    dirty: bool = False,
) -> dict:
    config = "global|25" if family == "theta" else "tau0.64_rel2"
    payload = {
        "selected": (
            {"threshold_mode": "global", "g_max_percentile": 25.0}
            if family == "theta"
            else {"config": config}
        ),
        "cv": {config: {"mean": mean, "sd": sd, "folds": [mean] * 5}},
        "git": {"revision": "abc", "dirty": dirty},
    }
    if eval_set is not None:
        payload["eval_set"] = eval_set
    return payload


def _run(
    root: Path,
    name: str,
    *,
    theta: float,
    csebb: float,
    models: int = 1,
    sd: float = 0.02,
    annotated_eval_set: str = "annotated",
) -> Path:
    run = root / name
    run.mkdir()
    members = [f"member_{index}" for index in range(models)] if models > 1 else []
    _write(run / "manifest.json", {"config": {"members": members}})
    _write(
        run / "postproc_cv_selection_annotated.json",
        _selection("theta", theta, sd=sd, eval_set=annotated_eval_set),
    )
    _write(
        run / "sebb_cv_selection_annotated.json",
        _selection("csebb", csebb, sd=sd, eval_set=annotated_eval_set),
    )
    # File lịch sử all không bắt buộc có eval_set hoặc provenance sạch.
    _write(
        run / "postproc_cv_selection.json",
        _selection("theta", theta - 0.01, eval_set=None, dirty=True),
    )
    _write(
        run / "sebb_cv_selection.json",
        _selection("csebb", csebb - 0.01, eval_set=None, dirty=True),
    )
    return run


def test_exact_tie_prefers_fewer_models(tmp_path: Path) -> None:
    ensemble = _run(tmp_path, "ensemble", theta=0.2, csebb=0.1, models=3)
    single = _run(tmp_path, "single", theta=0.2, csebb=0.1)

    ranking, _ = rank_candidates(
        [load_candidate(f"ens={ensemble}"), load_candidate(f"one={single}")]
    )

    assert [candidate.label for candidate in ranking] == ["one", "ens"]
    assert ranking[0].models == 1


def test_gap_within_leader_fold_sd_is_flagged(tmp_path: Path) -> None:
    leader = _run(tmp_path, "leader", theta=0.21, csebb=0.1, sd=0.02)
    second = _run(tmp_path, "second", theta=0.20, csebb=0.1, sd=0.001)

    ranking, note = rank_candidates(
        [load_candidate(f"a={leader}"), load_candidate(f"b={second}")]
    )

    assert ranking[0].label == "a"
    assert "không được gọi là tốt hơn hạng 2" in note
    assert "+0.0100" in note


def test_mismatched_eval_set_is_rejected(tmp_path: Path) -> None:
    run = _run(
        tmp_path,
        "wrong_eval_set",
        theta=0.2,
        csebb=0.1,
        annotated_eval_set="all",
    )

    with pytest.raises(ValueError, match="eval_set không khớp"):
        load_candidate(f"bad={run}", "annotated")


def test_better_family_and_folds_are_loaded(tmp_path: Path) -> None:
    run = _run(tmp_path, "csebb_wins", theta=0.15, csebb=0.22)

    candidate = load_candidate(f"f2={run}")

    assert candidate.score.family == "csebb"
    assert candidate.score.mean == pytest.approx(0.22)
    assert candidate.score.folds == pytest.approx((0.22,) * 5)
    assert candidate.delta_vs_all == pytest.approx(0.01)


def test_main_configures_utf8_before_parsing_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeStdout:
        configured = False

        def reconfigure(self, *, encoding: str, errors: str) -> None:
            assert encoding == "utf-8"
            assert errors == "replace"
            self.configured = True

    stdout = FakeStdout()

    def stop_after_check() -> None:
        assert stdout.configured
        raise RuntimeError("dừng sau khi kiểm thứ tự")

    monkeypatch.setattr(report_s13_ranking.sys, "stdout", stdout)
    monkeypatch.setattr(report_s13_ranking, "parse_args", stop_after_check)

    with pytest.raises(RuntimeError, match="dừng sau khi kiểm thứ tự"):
        report_s13_ranking.main()
