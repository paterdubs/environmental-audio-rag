# ADR-0021 — RQ1 cho kết quả âm tính: kết luận, cách báo cáo, và dịch trọng tâm đóng góp

**Status:** Accepted
**Date:** 2026-09-24 · **Cập nhật số:** 2026-09-25 (sau `7ada7d7`, xem §5)

## Context

RQ1 hỏi pretraining thêm trên DataSEC (nhánh C) có cải thiện SED trên DataSED so
với chỉ AudioSet (nhánh B) không — đo bằng `Δ = C − B` (ADR-0002). Hai run thăm dò
đầu tiên cho C > B (+0.0089 event-F1 ở cả seed 0 và 1). Run chính thức trên tree
sạch (I8) cho **C < B** (−0.0173). Hai phát hiện kèm theo làm mọi số đơn lẻ mất
giá trị:

1. **Train SED không tất định cùng seed.** Code train giống hệt ở mọi revision
   (`git diff <rev> dd1adce -- scripts/train_sed.py ml/training ml/models
   ml/datasets ml/configs ml/features` rỗng), cùng seed 20260922, nhưng frame
   macro-F1 nhánh B 0.5850 → 0.5705. Classifier (D2) thì tái lập bit-for-bit.
2. **3/10 run B/C có `git.dirty=true`** (B `015736Z`, B `031616Z`, C `021958Z`)
   — nội dung chưa commit lúc chạy không kiểm được từ git.

K1 train thêm seed 2, 3 để có 5 run/nhánh.

## Decision

### 1. Phân tích chính = 7 run sạch; độ nhạy = 10 run

| | Phân tích chính (sạch, B n=3 · C n=4) | Độ nhạy (đủ, n=5 · n=5) |
|---|---|---|
| event-based F1 | B 0.0610±0.0048 · C 0.0539±0.0088 · **p=0.234** | B 0.0604±0.0039 · C 0.0535±0.0076 · p=0.124 |
| PSDS-1 | B 0.2902±0.0093 · C 0.2892±0.0139 · **p=0.913** | Δ +0.0100 · p=0.313 |
| PSDS-2 | B 0.6498±0.0037 · C 0.6591±0.0107 · **p=0.181** | Δ +0.0019 · p=0.772 |

Welch t-test hai phía. Không metric nào có p < 0.05 ở cả hai cách.
Nguồn: `rq1_multiseed_clean_20260924.md`, `rq1_multiseed_20260924.md`.

### 2. Kết luận RQ1 được phép viết

> Ở ngân sách fine-tune 8 epoch, pretraining thêm trên DataSEC **không tạo khác
> biệt đo được** so với chỉ pretraining AudioSet, trên cả event-based F1, PSDS-1
> và PSDS-2. Pretraining nói chung (B/C so với A) cải thiện rõ: event-F1 ~1.5–1.7×
> (A 0.036 so với B/C 0.054–0.061), PSDS-1 +0.08, PSDS-2 tăng ~0.2.

**Không được viết:** "DataSEC cải thiện …" dưới bất kỳ metric nào; bất kỳ Δ C−B
nào dưới dạng một điểm đơn lẻ không kèm độ lệch chuẩn và n.

### 3. Mọi số SED từ nay báo mean ± sd trên nhiều run

Hệ quả trực tiếp của phát hiện không tất định. Một run đơn lẻ chỉ được dùng làm
minh hoạ, có ghi rõ.

### 4. Dịch trọng tâm đóng góp sang C1/C2/C4

RQ1 (thuộc C3) trở thành phát hiện phụ có kiểm soát chặt: một kết quả âm tính
được đo đúng cách (rò rỉ xuyên dataset kiểm soát, tree sạch, nhiều run, kiểm
định thống kê). Đóng góp chính của khoá luận chuyển sang caption có căn cứ (C1),
metric grounding (C2) và RAG trên timeline (C4).

### 5. Cập nhật 25/09 — số tính lại sau khi sửa lỗi ghép cửa sổ (`7ada7d7`)

`stack_predictions_by_recording` nối cửa sổ cuối (căn theo cuối audio) thay vì đặt
theo `frame_offsets_s` → ~10 s cuối mỗi recording bị nhân đôi và dịch trễ. Cả 11
run được quét θ lại trên dev và đánh giá test một lần (`3208dbb`); bảng §1 là số
mới. **Kết luận không đổi** — không metric nào p < 0.05 ở cả hai cách chọn tập run.
Khác biệt đáng ghi: event-F1 giờ nghiêng về **B > C** ở cả hai phân tích (Δ −0.007,
p 0.12–0.23) — vẫn không có ý nghĩa, nhưng không được viết "C nhỉnh hơn". Số trước
khi sửa: `git show 84d4405:docs/measurements/rq1_multiseed_clean_20260924.md`.

## Consequences

### Tích cực

- Kết luận đứng vững dưới cả hai cách chọn tập run — không phụ thuộc quyết định
  xử lý run dirty.
- Chẩn đoán nguyên nhân event-F1 thấp đã có số (`collar_sensitivity_20260924.md`):
  nới collar onset 0.2 → 1.0 s làm event-F1 tăng ~3 lần (B run chính thức
  0.0621 → 0.1851). **Định vị thời gian là nút thắt lớn**, đúng như ADR-0014 dự
  báo. Ở collar 2 s F1 vẫn chỉ ~0.2 → còn nút thắt thứ hai là nhận dạng lớp
  (lỗi nhầm lớp là loại lỗi lớn nhất: 410 ở run B chính thức `054531Z`, 360 ở run
  C chính thức `061000Z`, trên 740 event tham chiếu). B ≈ C ở mọi mức collar.
- Phân tích theo độ dài (K5, `rq1_duration_polyphony_20260924.md`): recall thấp
  ở **mọi** bin độ dài (0.00–0.09), không riêng sự kiện ngắn — nhất quán với việc
  collar onset 0.2 s áp cho mọi sự kiện bất kể dài ngắn.

### Đánh đổi

- n nhỏ (3–5 run/nhánh): "không khác biệt đo được" ≠ "chứng minh bằng nhau".
  Kiểm định chỉ có sức mạnh phát hiện khác biệt cỡ độ lệch chuẩn giữa run
  (~0.004–0.007 event-F1). Phải nói rõ giới hạn này.
- K5: cột F1 theo bin **không diễn giải được** — reference lọc theo bin nhưng
  estimate giữ mọi dự đoán của recording → precision bị kéo xuống nhân tạo. Chỉ
  recall theo bin có nghĩa.
- K4 (per-class): vài lớp có hướng nhất quán (`chicken_coop` C>B 12/12 cặp,
  `birds` 1/12, `voices` 1/12) nhưng 21 lớp × 12 cặp → vài lớp "nhất quán" là
  kỳ vọng do ngẫu nhiên. Không diễn giải từng lớp mà không hiệu chỉnh so sánh bội.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| Chỉ báo run chính thức đơn lẻ (I8) | Run đơn lẻ đảo dấu so với run thăm dò — không tất định làm số đơn lẻ vô nghĩa |
| Loại hẳn 3 run dirty | Làm n nhỏ hơn nữa; báo cả hai và chứng minh kết luận không đổi mạnh hơn |
| Train thêm tới khi C > B có ý nghĩa | Tìm kiếm kết quả có lợi — vi phạm tinh thần evaluation_protocol |
| Tăng epoch fine-tune để "cho DataSEC cơ hội" | Hợp lệ như một thí nghiệm mới có đặc tả trước, không phải để cứu RQ1 hiện tại; ghi vào §8 ý tưởng để dành |

## Evidence cần kiểm lại

- [ ] Nguyên nhân không tất định (op CUDA nào) — chưa xác minh.
- [ ] Nếu còn ngân sách: lặp lại so sánh với fine-tune dài hơn, đặc tả trước khi chạy.
