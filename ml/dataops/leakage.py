"""Năm kiểm bắt buộc trước khi freeze split (DATA_PLAN §8.4).

Mỗi kiểm trả về một `CheckResult` có `violations` liệt kê **cụ thể** thứ vi phạm,
không chỉ đếm. Một cổng chỉ báo "fail" mà không nói fail ở đâu thì không dùng được.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

HELD_OUT_SPLITS = frozenset({"validation", "test"})


@dataclass(frozen=True)
class CheckResult:
    number: int
    name: str
    passed: bool
    violations: list[str] = field(default_factory=list)
    note: str = ""

    @property
    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.number}. {self.name} ({len(self.violations)} vi phạm)"


def _split_spread(assignment: Mapping[str, str], key_of: Mapping[str, str]) -> dict[str, set[str]]:
    spread: dict[str, set[str]] = {}
    for item, split in assignment.items():
        key = key_of.get(item)
        if key is None:
            continue
        spread.setdefault(key, set()).add(split)
    return spread


def check_group_integrity(
    assignment: Mapping[str, str], group_of: Mapping[str, str]
) -> CheckResult:
    """Kiểm 1: không group nào xuất hiện ở hai split."""
    violations = [
        f"group={group} splits={sorted(splits)}"
        for group, splits in sorted(_split_spread(assignment, group_of).items())
        if len(splits) > 1
    ]
    return CheckResult(1, "Group không nằm ở hai split", not violations, violations)


def check_hash_integrity(
    assignment: Mapping[str, str], sha256_of: Mapping[str, str]
) -> CheckResult:
    """Kiểm 2: không `sha256` nào xuất hiện ở hai split."""
    violations = [
        f"sha256={digest} splits={sorted(splits)}"
        for digest, splits in sorted(_split_spread(assignment, sha256_of).items())
        if len(splits) > 1
    ]
    return CheckResult(2, "SHA-256 không nằm ở hai split", not violations, violations)


def check_duplicate_pairs_within_split(
    assignment: Mapping[str, str], duplicate_groups: Mapping[str, Sequence[str]]
) -> CheckResult:
    """Kiểm 3: không cặp T2/T3 duplicate nào xuyên split.

    Thành viên không nằm trong `assignment` (ví dụ file của dataset khác) bị bỏ
    qua — quan hệ xuyên dataset là việc của kiểm 5.
    """
    violations: list[str] = []
    for group_id, members in sorted(duplicate_groups.items()):
        splits = {assignment[member] for member in members if member in assignment}
        if len(splits) > 1:
            violations.append(f"group={group_id} splits={sorted(splits)}")
    return CheckResult(3, "Nhóm trùng lặp không xuyên split", not violations, violations)


def check_class_coverage(
    assignment: Mapping[str, str],
    labels: Mapping[str, Sequence[str]],
    *,
    expected_classes: Sequence[str],
    allowed_empty: Sequence[str] = (),
) -> CheckResult:
    """Kiểm 4: mọi class có ≥ 1 mẫu ở mỗi split."""
    splits = sorted(set(assignment.values()))
    present: dict[str, set[str]] = {split: set() for split in splits}
    for item, split in assignment.items():
        present[split].update(labels.get(item, ()))

    exempt = set(allowed_empty)
    violations = [
        f"class={class_id} vắng ở split={split}"
        for split in splits
        for class_id in expected_classes
        if class_id not in present[split] and class_id not in exempt
    ]
    note = f"Ngoại lệ đã khai: {sorted(exempt)}" if exempt else ""
    return CheckResult(4, "Mọi class có mặt ở mọi split", not violations, violations, note)


def check_cross_dataset_exclusions_applied(
    assignment: Mapping[str, str],
    duplicate_groups: Mapping[str, Sequence[str]],
    excluded: Sequence[str],
    *,
    pretraining_prefix: str = "datasec:",
) -> CheckResult:
    """Kiểm 5: clip pretraining trùng với dev/test của benchmark đã bị loại hết."""
    excluded_set = set(excluded)
    violations: list[str] = []
    for group_id, members in sorted(duplicate_groups.items()):
        held_out = {
            assignment[member]
            for member in members
            if member in assignment and assignment[member] in HELD_OUT_SPLITS
        }
        if not held_out:
            continue
        for member in members:
            if member.startswith(pretraining_prefix) and member not in excluded_set:
                violations.append(f"{member} còn lại dù group={group_id} chạm {sorted(held_out)}")
    return CheckResult(
        5, "Clip pretraining trùng dev/test đã bị loại", not violations, violations
    )


def run_all(results: Sequence[CheckResult]) -> dict:
    if len(results) != 5:
        raise ValueError("DATA_PLAN §8.4 yêu cầu đúng 5 kiểm")
    return {
        "passed": all(result.passed for result in results),
        "checks": [
            {
                "number": result.number,
                "name": result.name,
                "passed": result.passed,
                "violation_count": len(result.violations),
                "violations": result.violations[:50],
                "violations_truncated": max(0, len(result.violations) - 50),
                "note": result.note,
            }
            for result in results
        ],
    }
