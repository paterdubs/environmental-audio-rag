import json
from pathlib import Path

import numpy as np
from jsonschema import Draft202012Validator

from scripts.filter_predictions import build_manifest, keep_windows

SCHEMA = Path(__file__).resolve().parents[1] / "contracts/run_manifest.schema.json"


def test_keep_windows_selects_only_recordings_of_the_split() -> None:
    ids = np.asarray(["S-1", "S-1", "S-2", "S-3"], dtype=np.str_)
    assert keep_windows(ids, {"S-1", "S-3"}).tolist() == [True, True, False, True]
    assert not keep_windows(ids, set()).any()


def test_manifest_matches_run_contract_and_records_environment() -> None:
    source = {"task": "sed_oof", "split_sha256": "a" * 64,
              "data_manifest_sha256": "b" * 64, "taxonomy_sha256": "c" * 64}
    manifest = build_manifest(
        run_id="sed_filtered_x_20261109T000000Z", argv=["ml/runs/src", "--split", "validation"],
        class_ids=("birds", "voices"), source=source, source_name="src",
        split="validation", recordings=3, copies={})
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(manifest)
    assert set(manifest["environment"]) == {"python", "numpy"}
    assert manifest["config"]["source_run"] == "src"
