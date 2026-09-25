from scripts.select_postproc_cv import G_MAX_PERCENTILES, MODES, assign_folds, build_tasks


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
