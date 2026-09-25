from scripts.select_postproc_cv import assign_folds


def test_group_k_fold_keeps_leakage_groups_together_and_is_deterministic() -> None:
    ids = [f"S-{i:04d}" for i in range(40)]
    groups = {r: f"g{i // 2}" for i, r in enumerate(ids)}  # pairs share a group
    folds = assign_folds(ids, groups, 5)
    assert folds == assign_folds(list(reversed(ids)), groups, 5)
    for i in range(0, 40, 2):
        assert folds[ids[i]] == folds[ids[i + 1]]
    assert set(folds.values()) == {0, 1, 2, 3, 4}
