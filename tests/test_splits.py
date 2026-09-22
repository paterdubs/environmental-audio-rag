import pandas as pd

from ml.dataops.splits import SplitConfig, grouped_multilabel_split


def test_grouped_split_keeps_duplicate_group_together() -> None:
    rows = pd.DataFrame(
        [
            {"item": f"item-{index}", "group": f"group-{index // 2}", "label": f"c{index % 3}"}
            for index in range(60)
        ]
    )
    split = grouped_multilabel_split(
        rows,
        item_col="item",
        group_col="group",
        label_col="label",
        config=SplitConfig(seed=7),
    )

    assert set(split["split"]) == {"train", "validation", "test"}
    assert split.groupby("group")["split"].nunique().max() == 1
    assert split["item"].nunique() == len(rows)


def test_grouped_split_is_deterministic() -> None:
    rows = pd.DataFrame(
        [
            {"item": f"item-{index}", "group": f"group-{index}", "label": f"c{index % 4}"}
            for index in range(80)
        ]
    )
    kwargs = {
        "item_col": "item",
        "group_col": "group",
        "label_col": "label",
        "config": SplitConfig(seed=11),
    }
    first = grouped_multilabel_split(rows, **kwargs)
    second = grouped_multilabel_split(rows.sample(frac=1, random_state=99), **kwargs)

    pd.testing.assert_frame_equal(first, second)


def test_grouped_split_accepts_multiple_labels_per_item() -> None:
    rows = pd.DataFrame(
        [
            {"item": f"item-{index}", "group": f"group-{index}", "label": label}
            for index in range(40)
            for label in (f"c{index % 3}", f"c{(index + 1) % 3}")
        ]
    )
    split = grouped_multilabel_split(
        rows,
        item_col="item",
        group_col="group",
        label_col="label",
        config=SplitConfig(seed=3),
    )

    assert len(split) == 40
    assert split["item"].is_unique
