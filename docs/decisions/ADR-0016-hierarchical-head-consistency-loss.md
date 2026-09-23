# ADR-0016 — Hierarchical head và consistency loss cho DataSEC

**Status:** Accepted
**Date:** 2026-09-23

## Context

D4 trên board: "Subclass head + consistency loss; báo hai số macro-F1
(ADR-0006 §3)". `DataSECFeatureDataset` đã trả `(feature, coarse_index,
subclass_index)` với `subclass_index = -1` cho 12 lớp coarse không subclass,
nhưng chưa có model nào tiêu thụ cặp nhãn này — `AudioClassifier` và
`PannsAudioClassifier` chỉ có một head 22-way.

Câu hỏi kiến trúc chưa trả lời: hai head chia sẻ gì, và "consistency loss" tính
thế nào? Đây là quyết định kiến trúc — thuộc về tôi theo bảng phân việc, không
giao Codex tự chọn.

## Decision

### 1. Một encoder, hai head tuyến tính độc lập

`HierarchicalAudioClassifier` (`ml/models/hierarchical.py`) nhận `encoder` qua
constructor (giống `SoundEventDetector`, `PannsAudioClassifier`), thêm
`coarse_head: Linear(C, 22)` và `subclass_head: Linear(C, 28)` trên cùng một
embedding. Không dùng hai encoder riêng — sẽ gấp đôi chi phí VRAM vốn đã eo hẹp
ở 8 GB (ADR-0002 rủi ro R6).

### 2. Ba thành phần loss, không phải hai

```
total = coarse_CE + λ_sub · subclass_CE(ignore_index=-1) + λ_cons · consistency
```

`subclass_CE` một mình **không đủ**: CE 28-way tối ưu để lớp đúng là argmax,
nhưng không phạt việc đặt phần lớn khối lượng xác suất vào một gia đình coarse
sai miễn là lớp đúng vẫn nhỉnh hơn một chút. Đó chính xác là điều
"parent-consistency rate" ở [ADR-0006 §2](ADR-0006-danh-gia-subclass.md) đo được
trên DataSED — nếu train không tối ưu trực tiếp cho nó, không có lý do gì để
tin model sẽ nhất quán khi suy luận trên dữ liệu không có subclass ground truth.

### 3. Công thức consistency loss

Với `M ∈ {0,1}^(22×28)` là ma trận thành viên gia đình (build một lần từ
taxonomy, `build_family_mask`):

```
mass_i = Σ_{s ∈ family(coarse_i)} softmax(subclass_logits_i)_s
consistency = mean_i [ -log(mass_i) ]     (chỉ trên item có subclass_target != -1)
```

Đây là cross-entropy giữa phân phối dự đoán và "phân phối gia đình đúng", không
phải giữa dự đoán và một subclass cụ thể — phạt khối lượng xác suất rơi ra ngoài
gia đình, độc lập với việc có chọn đúng subclass bên trong gia đình hay không.

12 lớp coarse không subclass có hàng `M` toàn 0 — item thuộc các lớp này đã bị
`ignore_index=-1` loại khỏi `subclass_CE`, và bị cùng mask `valid` loại khỏi
consistency. Không có "gia đình rỗng" nào bị ép khối lượng vào chính nó.

### 4. Trọng số mặc định `λ_sub=1.0, λ_cons=0.5`, chưa hiệu chuẩn

Đặt tạm để không chặn D1/D4 chạy được. **Phải hiệu chuẩn trên dev**, không phải
chọn tuỳ ý — thêm vào "Evidence cần kiểm lại".

### 5. Metric suy luận: `parent_consistency_rate`, tách khỏi loss

Hàm riêng nhận **prediction** (không phải logits huấn luyện), loại item có
coarse dự đoán thuộc nhóm không subclass (trả `NaN` nếu không còn mẫu nào) —
dùng để so với baseline random đã đặc tả ở
[ADR-0006 §7](ADR-0006-danh-gia-subclass.md#7-đặc-tả-baseline-random-cho-parent-consistency-bổ-sung-2026-09-23).

## Consequences

### Tích cực
- Metric suy luận (parent-consistency) và mục tiêu huấn luyện (consistency
  loss) giờ đo cùng một đại lượng — không lệch mục tiêu.
- Tái dùng được cho cả `AudioEncoder` và `PannsCNN14Encoder` nhờ constructor
  nhận encoder, nhất quán với `SoundEventDetector` (ADR-0014).

### Đánh đổi
- Thêm một siêu tham số (`λ_cons`) chưa hiệu chuẩn — nợ kỹ thuật, phải quét trên
  dev trước khi báo số D4 là kết luận cuối.
- Head subclass 28-way học trên tập cực mất cân bằng theo `leakage_group` (một
  số subclass có 19-21 file). **Đã chốt ở D1** (`scripts/train_classifier.py`):
  `make_class_balanced_sampler(level="coarse")` — cân bằng theo coarse, không
  theo subclass. Head subclass vẫn học trên phân bố lệch tự nhiên của nó trong
  mỗi batch đã cân bằng coarse; nếu D4 cho macro-F1 subclass thấp bất thường ở
  vài node, cân nhắc lại mức lấy mẫu.

## Bổ sung 2026-09-23 — sửa lỗi NaN bắt được khi chạy D1 thật

`hierarchical_loss` bản đầu gọi `nn.functional.cross_entropy(subclass_logits,
subclass_target, ignore_index=IGNORE_SUBCLASS)` **vô điều kiện**. PyTorch chia
tổng loss cho số phần tử **hợp lệ trong chính batch đó** — nếu 100% item trong
batch thuộc 12 lớp coarse không có subclass (`subclass_target` toàn `-1`), số
chia là 0 và hàm trả **NaN**, không phải 0 như trực giác.

Bắt được thật khi chạy `scripts.train_classifier --epochs 1`: validation loss
ra NaN. Nguyên nhân — validation loader dùng `shuffle=False`, và các dòng
trong `datasec_classification.csv` giữ nguyên thứ tự theo thư mục nguồn (cùng
lớp nằm liền kề), nên hoàn toàn có thể có một batch 32 item toàn thuộc một lớp
không-subclass. Train loader dùng `ClassBalancedSampler` (lấy mẫu đều theo
lớp mỗi batch) nên tình huống này hiếm xảy ra ở train — chính vì thế train loss
không lộ ra bug mà validation loss lộ ra ngay ở epoch đầu.

Sửa: chỉ gọi `cross_entropy` cho subclass/consistency khi `valid.any()`; batch
toàn `-1` trả `subclass_loss = consistency_loss = 0` thay vì NaN. Thêm
`test_hierarchical_loss_handles_a_batch_with_no_subclass_at_all` khoá lại hành
vi đúng (`tests/test_hierarchical.py`, 11/11 pass).

## Alternatives considered

- **Head subclass điều kiện theo coarse dự đoán** (28-way chia thành 10 head
  con, mỗi head chỉ dự đoán trong gia đình của nó). Chính xác hơn về mặt kiến
  trúc nhưng phức tạp hoá huấn luyện (phải định tuyến gradient theo coarse dự
  đoán, dễ vỡ khi coarse dự đoán sai) — không cần thiết khi consistency loss đã
  đạt cùng mục tiêu với ít thay đổi hơn.
- **Bỏ consistency loss, chỉ dùng hai CE.** Không tối ưu trực tiếp cho metric sẽ
  báo cáo — rủi ro model học "trúng nhãn nhưng lệch gia đình" mà loss không thấy.
- **Multi-task SED + subclass cùng lúc.** Đã loại ở `CLAUDE.md` §8 ý tưởng để
  dành — ngoài phạm vi D4.

## Evidence cần kiểm lại

- [ ] Quét `λ_cons ∈ {0, 0.25, 0.5, 1.0}` trên dev DataSEC, chọn theo
      parent-consistency + subclass macro-F1 (n≥10 node), không phải theo cảm giác.
- [ ] `ClassBalancedSampler` áp theo coarse hay theo subclass khi cả hai head
      cùng train — nếu theo coarse, 4 subclass nhỏ vẫn có thể dưới-sample.
