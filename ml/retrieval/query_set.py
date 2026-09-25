"""Retrieval query set v2 (ADR-0027): four groups, EN + VI text, chosen on TRAIN only.

Queries are picked by how often their condition holds in the **train** split's
annotations — never dev or test, never a system output — so the set can be frozen
before any retrieval run. Relevance is declared as ground truth and computed per corpus
by `ml.retrieval.relevance` (evaluation_protocol §9.1).

Groups (SYSTEM §8.5): single class · two classes together · temporal relation ·
long event. The single-class group is capped by the 21 polyphonic classes.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from itertools import combinations, permutations
from typing import Any

from ml.retrieval.relevance import GROUND_TRUTH, satisfied
from ml.retrieval.temporal import Event

GROUP_SIZES = {"single_class": 21, "multi_class": 27, "temporal": 30, "duration": 22}
TEMPORAL_QUOTA = {"before": 8, "after": 8, "overlaps": 7, "within": 7}
DURATION_THRESHOLDS_S = (10.0, 30.0)
MIN_TRAIN_SUPPORT = 3

EN = {
    "single_class": "Which recordings contain {a}?",
    "multi_class": "Which recordings contain both {a} and {b}?",
    "before": "Which recordings have {a} before {b}?",
    "after": "Which recordings have {a} after {b}?",
    "overlaps": "Which recordings have {a} overlapping with {b}?",
    "within": "Which recordings have {a} during {b}?",
    "duration": "Which recordings have {a} lasting longer than {t:g} seconds?",
}
VI = {
    "single_class": "Bản ghi nào có {a}?",
    "multi_class": "Bản ghi nào có cả {a} và {b}?",
    "before": "Bản ghi nào có {a} trước {b}?",
    "after": "Bản ghi nào có {a} sau {b}?",
    "overlaps": "Bản ghi nào có {a} chồng lên {b}?",
    "within": "Bản ghi nào có {a} trong lúc có {b}?",
    "duration": "Bản ghi nào có {a} kéo dài hơn {t:g} giây?",
}
Candidate = tuple[str, dict[str, Any], dict[str, Any]]  # (template key, filters, fill values)


def _support(train: Mapping[str, Sequence[Event]], filters: dict[str, Any]) -> int:
    return sum(satisfied(events, filters) for events in train.values())


def _top(train, candidates: list[Candidate], k: int) -> list[tuple[Candidate, int]]:
    """Highest train support first; ties by the candidate's own text (deterministic)."""
    scored = [(c, _support(train, c[1])) for c in candidates]
    scored = [(c, n) for c, n in scored if n >= MIN_TRAIN_SUPPORT]
    scored.sort(key=lambda item: (-item[1], repr(item[0][1])))
    return scored[:k]


def _temporal_candidates(class_ids: Sequence[str], train) -> list[tuple[Candidate, int]]:
    chosen: list[tuple[Candidate, int]] = []
    taken: set[tuple[str, str, str]] = set()
    for predicate, quota in TEMPORAL_QUOTA.items():
        pool = []
        for a, b in permutations(class_ids, 2):
            mirror = ("before", b, a) if predicate == "after" else None
            if mirror in taken:  # after(a, b) is before(b, a): same relevant set
                continue
            filters = {"temporal": {"predicate": predicate, "a": a, "b": b, "tolerance_s": 0.0}}
            pool.append((predicate, filters, {"a": a, "b": b}))
        for candidate, n in _top(train, pool, quota):
            taken.add((predicate, candidate[2]["a"], candidate[2]["b"]))
            chosen.append((candidate, n))
    return chosen


def _candidates(group: str, class_ids: Sequence[str], train) -> list[tuple[Candidate, int]]:
    if group == "single_class":
        pool = [("single_class", {"classes_all": [c]}, {"a": c}) for c in class_ids]
    elif group == "multi_class":
        pool = [("multi_class", {"classes_all": [a, b]}, {"a": a, "b": b})
                for a, b in combinations(class_ids, 2)]
    elif group == "temporal":
        return _temporal_candidates(class_ids, train)
    else:
        pool = [("duration", {"duration": {"class_id": c, "min_s": t}}, {"a": c, "t": t})
                for c in class_ids for t in DURATION_THRESHOLDS_S]
    return _top(train, pool, GROUP_SIZES[group])


def build_query_set(train: Mapping[str, Sequence[Event]], class_ids: Sequence[str],
                    name_en: Callable[[str], str], name_vi: Callable[[str], str]
                    ) -> list[dict[str, Any]]:
    """Queries chosen from train annotations only; texts rendered in EN and VI."""
    queries: list[dict[str, Any]] = []
    for group in GROUP_SIZES:
        for (key, filters, fill), support in _candidates(group, class_ids, train):
            en = {k: name_en(v) if k in "ab" else v for k, v in fill.items()}
            vi = {k: name_vi(v) if k in "ab" else v for k, v in fill.items()}
            queries.append({
                "query_id": f"q-{len(queries) + 1:03d}", "group": group,
                "question": EN[key].format(**en), "question_vi": VI[key].format(**vi),
                "filters": filters, "support_train": support,
                "relevance": {"type": "recording_ids", "source": GROUND_TRUTH},
            })
    return queries
