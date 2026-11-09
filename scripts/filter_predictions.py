"""Keep only the recordings of one frozen split from a prediction artifact (ADR-0044, S8-lite).

    .venv/Scripts/python.exe -m scripts.filter_predictions ml/runs/sed_oof_B0_h5_<ts> \\
        --split validation --label B0_oof_dev --copy sebb_cv_selection_annotated.json

B0's fold models were trained on train ∪ dev, so its plain dev predictions are in-sample. Its OOF
artifact scores every dev recording with the one fold model that did not see it; this script cuts
that artifact down to the dev recordings and writes `ml/runs/sed_filtered_<label>_<ts>/` with
`predictions/dev.npz`, a manifest, and byte copies of the requested post-processing files.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import platform
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from ml.evaluation.predictions import load_predictions, save_predictions
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from ml.training.common import sha256_file

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ROOT / "data" / "splits" / "datased_polyphonic.csv"
SHARED = ("split_sha256", "data_manifest_sha256", "taxonomy_sha256")


def keep_windows(recording_ids: np.ndarray, keep: set[str]) -> np.ndarray:
    return np.asarray([str(r) in keep for r in recording_ids], dtype=bool)


def build_manifest(*, run_id: str, argv: list[str], class_ids: tuple[str, ...] | list[str],
                   source: dict, source_name: str, split: str, recordings: int,
                   copies: dict[str, str]) -> dict:
    """Manifest theo contracts/run_manifest.schema.json (có `environment`, như build_oof)."""
    return {
        "run_id": run_id, "task": "sed_filtered", "complete": True,
        "command": ["python", "-m", "scripts.filter_predictions", *argv],
        "class_ids": list(class_ids), **{k: source[k] for k in SHARED},
        "config": {"source_run": source_name, "source_task": source.get("task"),
                   "split": split, "recordings": recordings, "copied_sha256": copies},
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "git": git_state(ROOT),
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run", type=Path)
    parser.add_argument("--split", choices=("train", "validation", "test"), required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--copy", nargs="*", default=[])
    args = parser.parse_args()
    class_ids = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml").polyphonic_class_ids
    source = json.loads((args.run / "manifest.json").read_text(encoding="utf-8"))
    artifact = load_predictions(args.run / "predictions" / "dev.npz", expected_class_ids=class_ids)
    splits = pd.read_csv(SPLITS)
    keep_ids = set(splits.loc[splits["split"] == args.split, "recording_id"].astype(str))
    mask = keep_windows(artifact.recording_ids, keep_ids)
    if not mask.any():
        raise SystemExit(f"{args.run.name}: không có recording nào thuộc split {args.split}")
    filtered = dataclasses.replace(
        artifact, logits=artifact.logits[mask], targets=artifact.targets[mask],
        recording_ids=artifact.recording_ids[mask], frame_offsets_s=artifact.frame_offsets_s[mask],
        mask=artifact.mask[mask])
    out = ROOT / "ml" / "runs" / f"sed_filtered_{args.label}_{datetime.now(UTC):%Y%m%dT%H%M%SZ}"
    digest = save_predictions(out / "predictions" / "dev.npz", filtered,
                              expected_class_ids=class_ids)
    copies = {}
    for name in args.copy:
        shutil.copyfile(args.run / name, out / name)
        copies[name] = sha256_file(out / name)
    kept = sorted({str(r) for r in filtered.recording_ids})
    manifest = build_manifest(run_id=out.name, argv=sys.argv[1:], class_ids=class_ids,
                              source=source, source_name=args.run.name, split=args.split,
                              recordings=len(kept), copies=copies)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out / "metrics.json").write_text(json.dumps({"dev_predictions_sha256": digest}, indent=2),
                                      encoding="utf-8")
    print(json.dumps({"run_dir": str(out), "recordings": len(kept)}, indent=1))


if __name__ == "__main__":
    main()
