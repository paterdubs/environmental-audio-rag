import numpy as np

from scripts.filter_predictions import keep_windows


def test_keep_windows_selects_only_recordings_of_the_split() -> None:
    ids = np.asarray(["S-1", "S-1", "S-2", "S-3"], dtype=np.str_)
    assert keep_windows(ids, {"S-1", "S-3"}).tolist() == [True, True, False, True]
    assert not keep_windows(ids, set()).any()
