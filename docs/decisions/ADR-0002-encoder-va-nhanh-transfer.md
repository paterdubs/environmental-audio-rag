# ADR-0002 — Encoder và thiết kế ba nhánh transfer

**Status:** Accepted
**Date:** 2026-09-22

## Context

RQ1 hỏi: *pretraining trên DataSEC cải thiện SED trên DataSED đến mức nào?*
Trả lời được câu này cần chọn encoder và thiết kế thí nghiệm so sánh.

Ràng buộc và dữ kiện:

| Dữ kiện | Giá trị | Nguồn |
|---|---|---|
| DataSED | 717 recording, 18.6847 h | `datased_inventory_summary.json` |
| DataSEC | 5,048 clip, 22 coarse + 28 subclass | `datasec_archive_audit.json` |
| **Imbalance DataSEC** | **38:1; `voices`+`music` = 57.5%** | `datasec_archive_audit.json` |
| GPU | RTX 3070 Laptop, 8 GB | `ml/runs/…/manifest.json` |
| Baseline hiện có | CNN 3 block + BiGRU, frame macro-F1 0.359448 | `sed_polyphonic_20260922T115340Z` |
| Thời gian còn lại | 8 tuần | [CLAUDE.md](../../CLAUDE.md) |

**Vấn đề cốt lõi của thiết kế thí nghiệm.** So "scratch" với "pretrain trên
DataSEC" sẽ trộn hai hiệu ứng: lợi ích của pretraining *nói chung*, và lợi ích
*riêng* của DataSEC. Với 717 recording, gần như chắc chắn pretraining bất kỳ cũng
thắng scratch — và báo Δ đó như đóng góp của DataSEC là sai.

**Vấn đề thứ hai.** 57.5% DataSEC là `voices` và `music`, hai lớp ít liên quan
nhất tới đánh giá tiếng ồn môi trường. Pretraining với sampling đồng nhất sẽ cho
một encoder chuyên phân biệt nói/nhạc.

## Decision

### 1. Ba nhánh, không phải hai

| Nhánh | Encoder init | Fine-tune | Vai trò |
|---|---|---|---|
| **A** | Random | DataSED | Baseline dưới |
| **B** | PANNs CNN14 (AudioSet) | DataSED | Đóng góp của pretraining tổng quát |
| **C** | PANNs CNN14 → DataSEC | DataSED | Đóng góp **thêm** của DataSEC |

**RQ1 được trả lời bằng `C − B`, không phải `C − A`.** `C − A` phải được báo cáo
nhưng dán nhãn rõ là "tổng lợi ích của mọi pretraining", không phải lợi ích của
DataSEC.

### 2. Encoder đề xuất: PANNs CNN14 pretrained trên AudioSet

### 3. Baseline giữ nguyên CNN+BiGRU hiện có

Không viết lại. Nó đã có số đo và đóng vai trò nhánh A.

### 4. Pretraining DataSEC dùng class-balanced sampling

Sampling nghịch đảo tần suất lớp, hoặc loss weighting tương đương. Ablation A6 so
với uniform sampling để định lượng ảnh hưởng.

### 5. Ba nhánh dùng cùng training budget

Cùng split, cùng seed set, cùng số epoch × batch, cùng scheduler. Post-processing
hiệu chuẩn **độc lập** cho từng nhánh trên dev của nhánh đó.

## Consequences

### Tích cực

- `C − B` tách được đóng góp của DataSEC khỏi đóng góp của AudioSet — đây là điều
  phần lớn nghiên cứu transfer bỏ qua.
- PANNs có weights công khai, kiến trúc ổn định, và đã được dùng rộng rãi cho SED
  nên rủi ro kỹ thuật thấp trong 8 tuần.
- Giữ baseline hiện có nghĩa là nhánh A xong ngay, không tốn thêm thời gian.
- Class-balanced sampling làm nhánh C đo đúng thứ cần đo.

### Đánh đổi

- **Ba nhánh tốn gấp ba thời gian train** so với thiết kế hai nhánh. Nếu trễ,
  cut-list trong [PLAN.md](../PLAN.md) cho phép bỏ nhánh A (vì nó chỉ là baseline
  dưới) chứ **không** được bỏ nhánh B — bỏ B là mất câu trả lời cho RQ1.
- CNN14 có ~81M tham số. Với 8 GB VRAM và window 10 s, có thể phải giảm batch size
  hoặc dùng gradient accumulation. Rủi ro R6.
- PANNs dùng cấu hình log-mel riêng (32 kHz, 64 mel). Hiện tại đang dùng 16 kHz.
  Phải hoặc trích lại feature theo cấu hình PANNs, hoặc chấp nhận lệch domain và
  ghi rõ. **Quyết định: trích lại feature cho nhánh B/C**, tạo `logmel_panns_v1`.
- Class-balanced sampling làm mỗi epoch thấy `voices` ít hơn nhiều so với số file
  thực có — chấp nhận, vì mục tiêu là encoder tổng quát chứ không phải classifier
  DataSEC tốt nhất.

### Rủi ro chấp nhận

Nếu cổng D3 phát hiện DataSEC trùng nguồn đáng kể với dev/test DataSED, `C − B`
không diễn giải được như transfer. Xem [DATA_PLAN §7.6](../DATA_PLAN.md).

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| **BEATs / AST / PaSST** | Mạnh hơn trên giấy, nhưng nặng hơn, tốn VRAM hơn, và tích hợp phức tạp hơn trong 8 tuần. Dự án tiền nhiệm đặt BEATs làm kiến trúc đích nhưng **chưa bao giờ chạy được**, phải dùng PANNs thay thế — đó là bằng chứng trực tiếp về rủi ro lịch trình |
| **Chỉ hai nhánh (scratch vs DataSEC)** | Trộn hai hiệu ứng, không trả lời được RQ1 |
| **Chỉ hai nhánh (AudioSet vs AudioSet+DataSEC)** | Đúng về phương pháp nhưng mất baseline dưới, khó cho người đọc định cỡ độ khó của bài toán |
| **Train encoder riêng từ đầu trên DataSEC** | 5,048 clip quá ít để học biểu diễn tổng quát; và sẽ bị `voices`/`music` chi phối |
| **Uniform sampling khi pretrain** | Encoder học chủ yếu nói vs nhạc — xem Context |

## Evidence cần kiểm lại

- [ ] PANNs CNN14 vừa 8 GB VRAM với window 10 s, batch ≥ 4.
- [ ] Cấu hình log-mel của PANNs và chi phí trích lại feature cho 717 + 5,048 file.
- [ ] Class-balanced sampling có thực sự cải thiện transfer không (ablation A6).
- [ ] `load_classifier_encoder()` hiện dùng `strict=True` — phải kiểm tương thích
      khi encoder là CNN14 chứ không phải `AudioEncoder`.
