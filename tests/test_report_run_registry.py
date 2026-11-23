from scripts import report_run_registry as rr


def test_describe_reads_task_date_and_git_state():
    run = rr.describe("sed_polyphonic_20261008T092903Z",
                      {"task": "sed_polyphonic", "complete": True, "git": {"dirty": False},
                       "split_sha256": "abc", "environment": {"gpu": "RTX"}})
    assert run["date"] == "20261008" and run["complete"] and not run["dirty"]
    assert run["gpu"] == "RTX"


def test_describe_falls_back_to_the_run_name_when_task_is_missing():
    assert rr.describe("sed_ensemble_v2_20260926T120000Z", {})["task"] == "sed_ensemble_v2"


def test_summarise_counts_status_hashes_and_days_per_task():
    runs = [rr.describe(name, m) for name, m in (
        ("sed_polyphonic_20260922T000000Z", {"complete": True, "git": {"dirty": True},
                                             "split_sha256": "old"}),
        ("sed_polyphonic_20261008T000000Z", {"complete": False, "split_sha256": "new"}),
        ("sed_lbr_20261109T000000Z", {"complete": True, "split_sha256": "new"}))]
    data = rr.summarise(runs)
    sed = data["by_task"]["sed_polyphonic"]
    assert (sed["n"], sed["complete"], sed["dirty"], sed["split_hashes"]) == (2, 1, 1, 2)
    assert (sed["first"], sed["last"]) == ("20260922", "20261008")
    assert data["per_day"]["20261109"] == {"sed_lbr": 1}
    assert list(data["by_task"])[0] == "sed_polyphonic"
