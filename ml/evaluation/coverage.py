"""Recordings that can be scored against polyphonic ground truth (ADR-0034, PLAN nợ #25).

DataSED's original `Polyphonic_sound_detection.csv` covers 703 of the 717 recordings; the 14
`wind_turbine` recordings have no polyphonic rows at all, so scoring them treats audible events as
silence. `data/manifests/datased_polyphonic_unannotated.csv` lists them (written by
`scripts.report_polyphonic_coverage` from the raw archive). With `eval_set="annotated"` every
dev/test scorer drops them; `"all"` keeps the historical behaviour so earlier numbers reproduce.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
UNANNOTATED_MANIFEST = ROOT / "data" / "manifests" / "datased_polyphonic_unannotated.csv"
EVAL_SETS = ("all", "annotated")


def unannotated_recordings(path: Path = UNANNOTATED_MANIFEST) -> frozenset[str]:
    return frozenset(pd.read_csv(path)["recording_id"].astype(str))


def eval_suffix(eval_set: str) -> str:
    """File-name suffix so annotated-only results never overwrite the historical ones."""
    if eval_set not in EVAL_SETS:
        raise ValueError(f"eval_set must be one of {EVAL_SETS}, got {eval_set!r}")
    return "" if eval_set == "all" else f"_{eval_set}"


def restrict[T](by_recording: Mapping[str, T], eval_set: str,
                unannotated: frozenset[str] | None = None) -> dict[str, T]:
    """Keep every recording (`all`) or only those with polyphonic ground truth (`annotated`)."""
    eval_suffix(eval_set)
    if eval_set == "all":
        return dict(by_recording)
    drop = unannotated_recordings() if unannotated is None else unannotated
    kept = {rid: value for rid, value in by_recording.items() if rid not in drop}
    if not kept:
        raise ValueError("no annotated recording left to score")
    return kept
