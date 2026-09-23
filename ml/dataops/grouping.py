"""Khoá nhóm chống rò rỉ dùng cho split (DATA_PLAN §8.1–§8.4).

Một recording có thể bị buộc cùng split vì ba lý do độc lập:

1. Trùng nội dung — cùng `content_sha256` (T1/T2).
2. Cùng một `duplicate_group` của cổng D3 (T3, similarity ≥ ngưỡng).
3. Cùng một cặp `split_cohesion` — nghi ngờ ở dải review, chưa có quyết định
   ([ADR-0009 §3](../../docs/decisions/ADR-0009-nguong-phu-thuoc-overlap.md)).

Ba nguồn này phải được hợp nhất **trước** khi chia, không phải kiểm tra sau. Kiểm
sau chỉ phát hiện vi phạm; hợp nhất trước làm vi phạm không thể xảy ra.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from ml.dataops.duplicates import UnionFind


def build_leakage_groups(
    items: Iterable[str],
    *,
    content_key: Mapping[str, str],
    duplicate_groups: Mapping[str, Sequence[str]] | None = None,
    cohesion_pairs: Iterable[tuple[str, str]] = (),
) -> dict[str, str]:
    """Hợp nhất ba nguồn ràng buộc thành một khoá nhóm cho mỗi item.

    `items` là `file_id` đầy đủ (`<dataset>:<id>`). Thành viên của
    `duplicate_groups` hay `cohesion_pairs` nằm ngoài `items` — ví dụ file của
    dataset khác — bị bỏ qua: quan hệ xuyên dataset do luật loại trừ riêng lo,
    không phải do split.

    Khoá trả về là `file_id` nhỏ nhất trong nhóm, nên nó ổn định và không phụ
    thuộc thứ tự duyệt.
    """
    known = set(items)
    if not known:
        raise ValueError("Cannot build leakage groups for an empty item set")
    missing = known.difference(content_key)
    if missing:
        raise ValueError(
            f"Missing content key for {len(missing)} item(s), e.g. {sorted(missing)[0]}"
        )
    _reject_namespace_mismatch(known, duplicate_groups, cohesion_pairs)

    union = UnionFind()
    for item in known:
        union.add(item)

    by_content: dict[str, list[str]] = {}
    for item in known:
        by_content.setdefault(content_key[item], []).append(item)
    for members in by_content.values():
        for member in members[1:]:
            union.union(members[0], member)

    for members in (duplicate_groups or {}).values():
        present = [member for member in members if member in known]
        for member in present[1:]:
            union.union(present[0], member)

    for left, right in cohesion_pairs:
        if left in known and right in known:
            union.union(left, right)

    return {
        member: min(members)
        for members in union.groups().values()
        for member in members
    }


def _reject_namespace_mismatch(
    known: set[str],
    duplicate_groups: Mapping[str, Sequence[str]] | None,
    cohesion_pairs: Iterable[tuple[str, str]],
) -> None:
    """Chặn lỗi lệch namespace `file_id`, thay vì bỏ qua im lặng.

    Đã xảy ra thật: split dùng `datased:S-0001` còn cổng D3 dùng
    `datased:<đường dẫn tương đối>.wav`. Luật "bỏ qua thành viên ngoài tập" nuốt
    trọn toàn bộ ràng buộc và split vẫn chạy, vẫn ra kết quả trông hợp lý. Nếu
    một dataset có ràng buộc nhưng **không** khớp được item nào, đó là lỗi lệch
    tên chứ không phải dữ liệu sạch.
    """
    prefixes = {item.split(":", 1)[0] for item in known}
    referenced: set[str] = set()
    for members in (duplicate_groups or {}).values():
        referenced.update(members)
    for left, right in cohesion_pairs:
        referenced.update((left, right))

    for prefix in prefixes:
        candidates = {item for item in referenced if item.startswith(f"{prefix}:")}
        if candidates and not candidates & known:
            raise ValueError(
                f"Namespace mismatch for {prefix!r}: {len(candidates)} ràng buộc tham chiếu "
                f"file_id không có trong tập item, ví dụ {sorted(candidates)[0]!r} "
                f"so với {sorted(known)[0]!r}"
            )


def group_size_histogram(assignment: Mapping[str, str]) -> dict[int, int]:
    counts: dict[str, int] = {}
    for key in assignment.values():
        counts[key] = counts.get(key, 0) + 1
    histogram: dict[int, int] = {}
    for size in counts.values():
        histogram[size] = histogram.get(size, 0) + 1
    return dict(sorted(histogram.items()))


def largest_group(assignment: Mapping[str, str]) -> int:
    counts: dict[str, int] = {}
    for key in assignment.values():
        counts[key] = counts.get(key, 0) + 1
    return max(counts.values(), default=0)
