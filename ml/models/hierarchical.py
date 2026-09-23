"""Hierarchical DataSEC classifier: coarse + subclass head, một encoder chung.

`DataSECFeatureDataset` đã trả `(feature, coarse_index, subclass_index)` với
`subclass_index = -1` cho 12 lớp coarse không có subclass — nhưng chưa có model
nào tiêu thụ cặp nhãn này. Module này thêm head thứ hai và một loss phụ ép
xác suất subclass ở lại đúng "gia đình" coarse của nó (ADR-0015).
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor, nn

from ml.taxonomy import Taxonomy

IGNORE_SUBCLASS = -1
_CONSISTENCY_EPS = 1e-8


def build_family_mask(
    taxonomy: Taxonomy, coarse_ids: tuple[str, ...], subclass_ids: tuple[str, ...]
) -> Tensor:
    """Ma trận `(num_coarse, num_subclass)` — 1 nếu subclass thuộc gia đình coarse đó.

    12 coarse không subclass có hàng toàn 0: không có "gia đình" nào để ép mất
    khối lượng xác suất vào, và mask toàn 0 khiến hàng đó không đóng góp gì cho
    consistency loss (đúng ý — những item này đã bị `ignore_index` loại ở subclass
    loss, phải loại giống hệt ở đây).
    """
    subclass_position = {value: index for index, value in enumerate(subclass_ids)}
    mask = torch.zeros((len(coarse_ids), len(subclass_ids)), dtype=torch.float32)
    for coarse_index, item in enumerate(taxonomy.classes):
        for subclass in item.subclasses:
            mask[coarse_index, subclass_position[subclass]] = 1.0
    return mask


@dataclass(frozen=True)
class HierarchicalLossWeights:
    """Trọng số ba thành phần loss. Mặc định cân bằng — chưa hiệu chuẩn (D6/ADR-0015 evidence)."""

    subclass: float = 1.0
    consistency: float = 0.5

    def __post_init__(self) -> None:
        if self.subclass < 0 or self.consistency < 0:
            raise ValueError("Trọng số loss không được âm")


class HierarchicalAudioClassifier(nn.Module):
    """Một encoder, hai head tuyến tính: coarse (22-way) và subclass (28-way)."""

    def __init__(
        self,
        encoder: nn.Module,
        *,
        num_coarse: int,
        num_subclass: int,
        dropout: float = 0.2,
    ) -> None:
        super().__init__()
        self.encoder = encoder
        self.dropout = nn.Dropout(dropout)
        self.coarse_head = nn.Linear(encoder.output_channels, num_coarse)
        self.subclass_head = nn.Linear(encoder.output_channels, num_subclass)

    def forward(self, inputs: Tensor) -> tuple[Tensor, Tensor]:
        embedding = self.dropout(self.encoder(inputs).mean(dim=-1))
        return self.coarse_head(embedding), self.subclass_head(embedding)


def hierarchical_loss(
    coarse_logits: Tensor,
    subclass_logits: Tensor,
    coarse_target: Tensor,
    subclass_target: Tensor,
    family_mask: Tensor,
    *,
    weights: HierarchicalLossWeights | None = None,
    coarse_weight: Tensor | None = None,
) -> dict[str, Tensor]:
    """Ba thành phần: coarse CE, subclass CE (ignore -1), và consistency.

    Consistency ép **tổng xác suất** subclass rơi vào đúng gia đình của coarse
    thật, độc lập với việc có đoán đúng subclass hay không — đây là mục tiêu
    huấn luyện tương ứng trực tiếp với metric "parent-consistency rate" đã định
    nghĩa ở [ADR-0006 §2](../../docs/decisions/ADR-0006-danh-gia-subclass.md).
    Không có nó, CE 28-way một mình không phạt việc đặt khối lượng xác suất lớn
    ở một gia đình sai miễn là lớp đúng vẫn là argmax.

    `coarse_weight` (trọng số nghịch tần suất lớp, ADR-0002 §4) áp cho **riêng**
    CE của coarse. Chỉ `total` mang gradient — `coarse`/`subclass`/`consistency`
    trả về đã `.detach()`, dùng để **ghi log**, không dùng để `backward()` lại;
    ghép các thành phần đã detach sẽ làm subclass/consistency không nhận được
    gradient dù `total.backward()` chạy bình thường.
    """
    weights = weights or HierarchicalLossWeights()
    valid = subclass_target != IGNORE_SUBCLASS
    coarse_loss = nn.functional.cross_entropy(coarse_logits, coarse_target, weight=coarse_weight)

    if valid.any():
        # `cross_entropy(..., ignore_index=X)` chia tổng loss cho số phần tử
        # HỢP LỆ trong chính lệnh gọi đó. Batch nào có 100% item thuộc 12 lớp
        # coarse không subclass (rows liền kề trong `datasec_classification.csv`
        # thường cùng lớp — 12/22 lớp là loại này) sẽ có 0 phần tử hợp lệ, và
        # PyTorch trả **NaN** thay vì 0. Bắt được thật: validation loss ra NaN
        # ở lần chạy `--epochs 1` đầu tiên vì `shuffle=False` giữ nguyên thứ tự
        # theo lớp. Chỉ gọi cross_entropy khi chắc có ít nhất 1 phần tử hợp lệ.
        subclass_loss = nn.functional.cross_entropy(
            subclass_logits, subclass_target, ignore_index=IGNORE_SUBCLASS
        )
        probabilities = nn.functional.softmax(subclass_logits[valid], dim=-1)
        family = family_mask[coarse_target[valid]]
        mass = (probabilities * family).sum(dim=-1).clamp_min(_CONSISTENCY_EPS)
        consistency_loss = -torch.log(mass).mean()
    else:
        subclass_loss = coarse_logits.new_zeros(())
        consistency_loss = coarse_logits.new_zeros(())

    total = coarse_loss + weights.subclass * subclass_loss + weights.consistency * consistency_loss
    return {
        "total": total,
        "coarse": coarse_loss.detach(),
        "subclass": subclass_loss.detach(),
        "consistency": consistency_loss.detach(),
    }


def parent_consistency_rate(
    coarse_prediction: Tensor, subclass_prediction: Tensor, family_mask: Tensor
) -> float:
    """Tỷ lệ item mà subclass dự đoán (argmax) thuộc đúng gia đình coarse dự đoán.

    Đây là metric của ADR-0006 §2, không phải loss — dùng để báo cáo trên DataSED
    (không có subclass ground truth) đối chiếu với baseline random ở ADR-0006 §7.
    Item mà coarse dự đoán thuộc 12 lớp không subclass bị loại — gia đình rỗng
    không có khái niệm "đúng".
    """
    family_size = family_mask.sum(dim=-1)
    has_family = family_size[coarse_prediction] > 0
    if not has_family.any():
        return float("nan")
    family = family_mask[coarse_prediction[has_family]]
    hits = family.gather(1, subclass_prediction[has_family].unsqueeze(-1)).squeeze(-1)
    return float(hits.mean().item())
