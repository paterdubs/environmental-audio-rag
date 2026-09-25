"""Recording-bootstrap CI for the mean event-F1 of several runs per branch (W4 nghiệm thu).

Every run is scored on the same test recordings, so one bootstrap draw resamples recordings
once and re-scores **all** runs on that draw — the CI of a branch mean and of the difference
between branch means is paired by recording. Seed variation is not resampled: the runs are
kept as they are (n = 3–4 is too small to resample), so the CI answers "how much would the
mean move with another draw of recordings", while the spread across runs is reported beside.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np

Counts = Mapping[str, tuple[int, int, int]]  # recording -> (Nref, Nsys, Ntp)


def micro_f1(nref: float, nsys: float, ntp: float) -> float:
    return 2.0 * ntp / (nref + nsys) if nref + nsys else 0.0


def _branch_means(tensor: np.ndarray, weights: np.ndarray, groups: Sequence[np.ndarray]
                  ) -> list[float]:
    totals = np.tensordot(weights, tensor, axes=(0, 0))  # runs x 3
    f1 = np.array([micro_f1(*row) for row in totals])
    return [float(f1[index].mean()) for index in groups]


def paired_branch_bootstrap(counts_by_run: Mapping[str, Counts],
                            branches: Mapping[str, Sequence[str]], *, n_bootstrap: int = 1000,
                            confidence: float = 0.95, seed: int = 20260922) -> dict:
    """Mean F1 per branch and each pairwise difference (later − earlier branch), with CIs."""
    runs = [run for members in branches.values() for run in members]
    recordings = sorted(set.intersection(*(set(counts_by_run[r]) for r in runs)))
    if any(set(counts_by_run[r]) != set(recordings) for r in runs):
        raise ValueError("every run must be scored on the same recordings")
    tensor = np.array([[counts_by_run[run][rid] for run in runs] for rid in recordings],
                      dtype=float)  # recordings x runs x 3
    index = {run: i for i, run in enumerate(runs)}
    groups = [np.array([index[r] for r in members]) for members in branches.values()]
    names = list(branches)
    point = _branch_means(tensor, np.ones(len(recordings)), groups)
    rng = np.random.default_rng(seed)
    draws = np.empty((n_bootstrap, len(names)))
    for b in range(n_bootstrap):
        weights = np.bincount(rng.integers(0, len(recordings), len(recordings)),
                              minlength=len(recordings)).astype(float)
        draws[b] = _branch_means(tensor, weights, groups)
    alpha = (1.0 - confidence) / 2.0

    def interval(values: np.ndarray, estimate: float) -> dict:
        low, high = np.quantile(values, [alpha, 1.0 - alpha])
        return {"estimate": estimate, "lower": float(low), "upper": float(high)}

    result = {"n_recordings": len(recordings), "n_bootstrap": n_bootstrap,
              "confidence": confidence, "seed": seed,
              "branches": {name: {**interval(draws[:, i], point[i]),
                                  "runs": list(branches[name])}
                           for i, name in enumerate(names)}, "differences": {}}
    for i, first in enumerate(names):
        for j in range(i + 1, len(names)):
            result["differences"][f"{names[j]}-{first}"] = interval(
                draws[:, j] - draws[:, i], point[j] - point[i])
    return result
