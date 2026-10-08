import json
from pathlib import Path

from scripts.select_postproc_cv import (
    G_MAX_PERCENTILES,
    MODES,
    assign_folds,
    build_tasks,
    is_oof_run,
    priors_for,
)


def test_oof_runs_are_recognised_from_the_manifest_task(tmp_path: Path) -> None:
    oof, dev = tmp_path / "oof", tmp_path / "dev"
    for run, task in ((oof, "sed_oof"), (dev, "sed_ensemble")):
        run.mkdir()
        (run / "manifest.json").write_text(json.dumps({"task": task}), encoding="utf-8")
    assert is_oof_run(oof) and not is_oof_run(dev)
    assert not is_oof_run(tmp_path / "missing")


def test_held_out_folds_use_their_own_priors_and_the_refit_uses_all() -> None:
    """ADR-0041 §4: on OOF runs a fold's priors must not come from its own labels."""
    ctx = {"priors_by_p": {25.0: "all"}, "fold_priors": {0: {25.0: "not-0"}, 1: {25.0: "not-1"}}}
    assert priors_for(ctx, 25.0, 0) == "not-0" and priors_for(ctx, 25.0, 1) == "not-1"
    assert priors_for(ctx, 25.0, None) == "all"
    assert priors_for({"priors_by_p": {25.0: "train"}}, 25.0, 0) == "train"


def test_tasks_cover_every_config_once_with_slow_fits_first() -> None:
    serial = build_tasks(5, speculative_refits=False)
    parallel = build_tasks(5, speculative_refits=True)
    grid = {(m, p, k) for m in MODES for p in G_MAX_PERCENTILES for k in range(5)}
    assert len(serial) == len(set(serial)) and set(serial) == grid
    refits = {(m, p, None) for m in MODES for p in G_MAX_PERCENTILES}
    assert len(parallel) == len(set(parallel)) and set(parallel) == grid | refits
    assert parallel[:2] == [("per_class", p, None) for p in G_MAX_PERCENTILES]
    assert all(t[0] == "per_class" for t in parallel[:12])


def test_group_k_fold_keeps_leakage_groups_together_and_is_deterministic() -> None:
    ids = [f"S-{i:04d}" for i in range(40)]
    groups = {r: f"g{i // 2}" for i, r in enumerate(ids)}  # pairs share a group
    folds = assign_folds(ids, groups, 5)
    assert folds == assign_folds(list(reversed(ids)), groups, 5)
    for i in range(0, 40, 2):
        assert folds[ids[i]] == folds[ids[i + 1]]
    assert set(folds.values()) == {0, 1, 2, 3, 4}


def test_tasks_can_be_restricted_to_the_global_mode() -> None:
    """ADR-0030 §3: v2 selects among global thresholds only (A2: per-class overfits dev)."""
    tasks = build_tasks(5, speculative_refits=False, modes=("global",))
    assert {mode for mode, _, _ in tasks} == {"global"}
    assert len(tasks) == 5 * len(G_MAX_PERCENTILES)
