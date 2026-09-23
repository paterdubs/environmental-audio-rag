"""Gom nhóm trùng lặp và luật xử lý cho cổng D3 (DATA_PLAN §7.4–§7.6).

Ba tầng phát hiện nằm ở `inventory.py` (T1) và `fingerprint.py` (T2, T3). Module
này nhận kết quả so khớp theo cặp, gom thành nhóm, và áp luật giữ/loại.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Literal

Tier = Literal["T1", "T2", "T3"]
Verdict = Literal["duplicate", "review", "distinct"]

ALARM_BANDS: tuple[tuple[float, str, str], ...] = (
    (0.0, "clean", "RQ1 hợp lệ như thiết kế"),
    (0.01, "minor", "Loại, ghi số vào báo cáo, RQ1 vẫn hợp lệ"),
    (0.05, "material", "Loại, chạy lại nhánh C, nêu rõ trong Hạn chế"),
    (float("inf"), "invalidating", "Δ transfer không còn diễn giải được như transfer"),
)


#: Ngưỡng similarity tối thiểu để một cặp `review` trở thành ràng buộc cùng split.
#: 0.93 nằm **trên** mức dương tính giả cao nhất đã đo khi hiệu chuẩn (0.9205 trên
#: 5,000 cặp ngẫu nhiên khác nhãn, ADR-0007). Dưới mức đó, cặp không mang bằng
#: chứng phân biệt được với nhiễu, mà vẫn phải trả giá bằng chất lượng split.
COHESION_MIN_SIMILARITY = 0.93


@dataclass(frozen=True)
class DuplicateThresholds:
    """Ngưỡng T3. Mặc định là điểm khởi đầu của DATA_PLAN §7.3, **phải hiệu chuẩn**."""

    duplicate_min: float = 0.95
    review_min: float = 0.85
    min_overlap_s: float = 3.0
    short_duplicate_min: float = 0.99
    evidence_min: float = 0.85

    def validate(self) -> None:
        if not 0.0 < self.review_min <= self.duplicate_min <= 1.0:
            raise ValueError("Require 0 < review_min <= duplicate_min <= 1")
        if not self.duplicate_min <= self.short_duplicate_min <= 1.0:
            raise ValueError("Require duplicate_min <= short_duplicate_min <= 1")
        if self.min_overlap_s <= 0:
            raise ValueError("min_overlap_s must be positive")

    def classify(
        self,
        similarity: float,
        overlap_s: float,
        *,
        required_overlap_s: float | None = None,
    ) -> Verdict:
        """Xếp loại một cặp. Ngưỡng **phụ thuộc độ dài đoạn chồng lấp**.

        Một cặp khớp trên 1 giây và một cặp khớp trên 42 giây không mang cùng
        lượng bằng chứng, nên không thể dùng chung ngưỡng. Đo được trên 45,191
        cặp T3 thật:

        | Dải similarity | Số cặp | Median overlap |
        |---|---:|---:|
        | [0.85, 0.93) | 44,489 | **1.0 s** |
        | [0.93, 0.95) | 391 | **1.0 s** |
        | [0.95, 0.99) | 212 | 14.5 s |
        | [0.99, 1.00] | 99 | 42.5 s |

        Mọi dải dưới 0.95 có median overlap đúng bằng sàn 1 giây: hai bản ghi môi
        trường bất kỳ đều có **một** cửa sổ 1 giây trông giống nhau. Đó là nhiễu
        của phép so 16.6 triệu cặp, không phải bằng chứng cùng nguồn.

        Vì vậy đoạn ngắn hơn `min_overlap_s` phải đạt `short_duplicate_min` và
        **không có dải review** — bằng chứng quá mỏng để đáng một quyết định.
        """
        self.validate()
        floor = self.min_overlap_s if required_overlap_s is None else required_overlap_s
        if floor <= 0:
            raise ValueError("required_overlap_s must be positive")
        if overlap_s < floor:
            return "distinct"
        if overlap_s < self.min_overlap_s:
            return "duplicate" if similarity >= self.short_duplicate_min else "distinct"
        if similarity >= self.duplicate_min:
            return "duplicate"
        if similarity >= self.review_min:
            return "review"
        return "distinct"


@dataclass(frozen=True)
class PairMatch:
    left_file_id: str
    right_file_id: str
    tier: Tier
    similarity: float
    overlap_s: float
    verdict: Verdict

    @property
    def is_cross_dataset(self) -> bool:
        return self.left_file_id.split(":", 1)[0] != self.right_file_id.split(":", 1)[0]


@dataclass
class DuplicateGroup:
    group_id: str
    members: tuple[str, ...]
    tiers: tuple[Tier, ...]
    min_similarity: float
    cross_dataset: bool
    needs_review: bool

    @property
    def datasets(self) -> tuple[str, ...]:
        return tuple(sorted({member.split(":", 1)[0] for member in self.members}))


class UnionFind:
    def __init__(self) -> None:
        self._parent: dict[str, str] = {}

    def add(self, item: str) -> None:
        self._parent.setdefault(item, item)

    def find(self, item: str) -> str:
        self.add(item)
        root = item
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[item] != root:
            self._parent[item], item = root, self._parent[item]
        return root

    def union(self, left: str, right: str) -> None:
        left_root, right_root = self.find(left), self.find(right)
        if left_root != right_root:
            self._parent[right_root] = left_root

    def groups(self) -> dict[str, list[str]]:
        clusters: dict[str, list[str]] = {}
        for item in self._parent:
            clusters.setdefault(self.find(item), []).append(item)
        return {root: sorted(members) for root, members in clusters.items()}


def build_groups(matches: Iterable[PairMatch]) -> list[DuplicateGroup]:
    """Gom **chỉ** các cặp `duplicate` thành nhóm liên thông.

    Cạnh `review` **không** được union. Hai lý do, lý do thứ hai là quyết định:

    1. Gom chúng chính là "xử lý tự động" mà DATA_PLAN §7.3 cấm.
    2. Đo được: union cả cạnh `review` tạo một thành phần liên thông khổng lồ
       **2,310 file** (2,200 DataSEC + 110 DataSED) với min-similarity đúng bằng
       0.850 — tức nó được nối hoàn toàn bằng cạnh yếu nhất. Đó là hiện tượng
       chaining của single-linkage, không phải một nhóm trùng lặp.

    Cặp `review` đi ra `collect_review_pairs` để người quyết định.
    """
    union = UnionFind()
    linked = [match for match in matches if match.verdict == "duplicate"]
    for match in linked:
        union.union(match.left_file_id, match.right_file_id)

    by_root: dict[str, list[PairMatch]] = {}
    for match in linked:
        by_root.setdefault(union.find(match.left_file_id), []).append(match)

    groups: list[DuplicateGroup] = []
    for index, (root, members) in enumerate(sorted(union.groups().items()), start=1):
        edges = by_root.get(root, [])
        groups.append(
            DuplicateGroup(
                group_id=f"dup-{index:04d}",
                members=tuple(members),
                tiers=tuple(sorted({edge.tier for edge in edges})),
                min_similarity=min(edge.similarity for edge in edges),
                cross_dataset=len({member.split(":", 1)[0] for member in members}) > 1,
                needs_review=False,
            )
        )
    return groups


def collect_review_pairs(matches: Iterable[PairMatch]) -> list[PairMatch]:
    """Cặp ở dải `review`, xếp theo similarity giảm dần để người xem từ trên xuống."""
    return sorted(
        (match for match in matches if match.verdict == "review"),
        key=lambda match: match.similarity,
        reverse=True,
    )


def human_review_queue(matches: Iterable[PairMatch]) -> list[PairMatch]:
    """Cặp `review` **xuyên dataset** — phần bắt buộc cần quyết định của người.

    Chỉ nhóm này ảnh hưởng RQ1: một clip pretraining trùng với recording ở dev
    hay test của benchmark thì Δ transfer không còn diễn giải được. Đo được trên
    dữ liệu thật: 35 cặp — làm tay được trong một buổi.
    """
    return [match for match in collect_review_pairs(matches) if match.is_cross_dataset]


def split_cohesion_pairs(
    matches: Iterable[PairMatch], *, min_similarity: float = COHESION_MIN_SIMILARITY
) -> list[tuple[str, str]]:
    """Cặp `review` **nội bộ** một dataset — ràng buộc "cùng split", không phải xoá.

    Vì sao được xử lý tự động mà không vi phạm DATA_PLAN §7.3: hành động ở đây
    **không phải loại trừ**. Giữ hai recording nghi ngờ trong cùng một split chỉ
    có thể làm giảm rò rỉ, không bao giờ che giấu nó, và không xoá dữ liệu nào.
    Điều §7.3 cấm là tự động *quyết định loại* — việc đó vẫn cần người.

    Nhưng "chỉ có thể làm giảm rò rỉ" **không** có nghĩa là miễn phí. Ràng buộc
    được lấy hợp bắc cầu, nên single-linkage chaining trên cạnh yếu tạo ra khối
    lớn — đúng lỗi [ADR-0009 §2](../../docs/decisions/ADR-0009-nguong-phu-thuoc-overlap.md)
    đã sửa cho cạnh `duplicate`. Ở ngưỡng review 0.85, DataSEC ra một khối **315
    file** mật độ 0.024 trộn bốn lớp. Vì vậy cohesion đòi bằng chứng mạnh hơn
    ngưỡng review: trên mức dương tính giả đã đo (ADR-0012).
    """
    return sorted(
        {
            tuple(sorted((match.left_file_id, match.right_file_id)))
            for match in matches
            if match.verdict == "review"
            and not match.is_cross_dataset
            and match.similarity >= min_similarity
        }
    )


@dataclass(frozen=True)
class Exclusion:
    file_id: str
    group_id: str
    reason_code: str
    decided_by: str


def within_dataset_exclusions(groups: Sequence[DuplicateGroup]) -> list[Exclusion]:
    """Giữ một representative mỗi nhóm nội bộ, loại phần còn lại (DATA_PLAN §7.5).

    Nhóm ở đây chỉ gồm cạnh `duplicate`; cặp `review` không bao giờ tới được hàm
    này, và phải được người quyết định rồi ghi tay `decided_by: human:<tên>`.
    """
    exclusions: list[Exclusion] = []
    for group in groups:
        if group.cross_dataset or group.needs_review:
            continue
        for member in group.members[1:]:
            exclusions.append(
                Exclusion(
                    file_id=member,
                    group_id=group.group_id,
                    reason_code="exclude_duplicate",
                    decided_by="rule:within_dataset_representative",
                )
            )
    return exclusions


def cross_dataset_exclusions(
    groups: Sequence[DuplicateGroup],
    *,
    datased_split: dict[str, str],
    pretraining_dataset: str = "datasec",
    benchmark_dataset: str = "datased",
) -> list[Exclusion]:
    """Loại clip pretraining trùng với dev/test của benchmark (DATA_PLAN §7.5).

    `datased_split` ánh xạ `file_id` → `train|validation|test`. Nhóm nào có thành
    viên benchmark nằm ngoài train thì **toàn bộ** clip pretraining trong nhóm bị
    loại. Nhóm chỉ chạm train được giữ, nhưng vẫn phải báo cáo.
    """
    held_out = {"validation", "test"}
    exclusions: list[Exclusion] = []
    for group in groups:
        if not group.cross_dataset or group.needs_review:
            continue
        benchmark_members = [
            member for member in group.members if member.startswith(f"{benchmark_dataset}:")
        ]
        splits = {datased_split.get(member, "unassigned") for member in benchmark_members}
        if not splits & held_out:
            continue
        for member in group.members:
            if member.startswith(f"{pretraining_dataset}:"):
                exclusions.append(
                    Exclusion(
                        file_id=member,
                        group_id=group.group_id,
                        reason_code="exclude_cross_dataset_leak",
                        decided_by="rule:cross_dataset_holdout",
                    )
                )
    return exclusions


@dataclass
class AlarmReport:
    leaked_files: int
    total_files: int
    ratio: float
    band: str
    action: str
    pending_review_groups: int = 0
    notes: list[str] = field(default_factory=list)


def alarm_band(leaked_files: int, total_files: int) -> tuple[str, str]:
    """Ngưỡng báo động DATA_PLAN §7.6."""
    if total_files <= 0:
        raise ValueError("total_files must be positive")
    ratio = leaked_files / total_files
    if ratio == 0:
        return ALARM_BANDS[0][1], ALARM_BANDS[0][2]
    for upper, band, action in ALARM_BANDS[1:]:
        if ratio < upper or upper == float("inf"):
            return band, action
    raise AssertionError("unreachable")


def assess_alarm(
    exclusions: Sequence[Exclusion],
    *,
    total_pretraining_files: int,
    pending_review_groups: int = 0,
) -> AlarmReport:
    leaked = {
        exclusion.file_id
        for exclusion in exclusions
        if exclusion.reason_code == "exclude_cross_dataset_leak"
    }
    band, action = alarm_band(len(leaked), total_pretraining_files)
    notes: list[str] = []
    if pending_review_groups:
        notes.append(
            f"{pending_review_groups} nhóm ở dải review chưa có quyết định người — "
            "tỷ lệ rò rỉ hiện tại là CẬN DƯỚI, không phải giá trị cuối"
        )
    return AlarmReport(
        leaked_files=len(leaked),
        total_files=total_pretraining_files,
        ratio=len(leaked) / total_pretraining_files,
        band=band,
        action=action,
        pending_review_groups=pending_review_groups,
        notes=notes,
    )
