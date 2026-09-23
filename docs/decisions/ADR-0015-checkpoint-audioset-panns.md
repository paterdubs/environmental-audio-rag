# ADR-0015 — Nguồn checkpoint PANNs CNN14 pretrained trên AudioSet

**Status:** Accepted một phần — nguồn/hash/kiến trúc đã xác minh thật (Codex,
Task F1); phần chuẩn hoá thay `bn0` còn chờ B2 (xem
[ADR-0018](ADR-0018-nap-mot-phan-checkpoint-panns.md))
**Date:** 2026-09-23, cập nhật cùng ngày sau khi Codex xác minh trực tiếp

## Context

[ADR-0002](ADR-0002-encoder-va-nhanh-transfer.md) định nghĩa ba nhánh:

| Nhánh | Encoder init |
|---|---|
| A | Random |
| **B** | **PANNs CNN14 (AudioSet)** |
| **C** | **PANNs CNN14 → DataSEC** |

Cả B và C đều cần bắt đầu từ trọng số CNN14 đã pretrain trên AudioSet. Nhưng
`ml/models/panns.py` ghi rõ ở docstring: *"The implementation intentionally
does not download checkpoints."* Không có task nào trong `PLAN.md` hay board
từng giao việc lấy checkpoint này. Nếu D1 chạy `PannsCNN14Encoder()` khởi tạo
ngẫu nhiên rồi train trên DataSEC, kết quả **không phải** nhánh C như ADR-0002
định nghĩa — nó là "CNN14-kiến trúc-nhưng-scratch", một biến thể chưa được đặt
tên và không trả lời được RQ1 theo đúng thiết kế `C − B`.

Đây là một lỗ hổng kế hoạch, không phải lỗi code — phát hiện khi rà trước khi
giao D1 cho Codex.

## Decision

### 1. Nguồn checkpoint — đã xác minh thật (không còn suy từ tóm tắt tìm kiếm)

Bước đầu tìm qua WebSearch (23/09) chỉ là gợi ý hướng tra cứu, **không** dùng để
báo cáo — đúng cảnh báo ban đầu của ADR này. Codex (Task F1) sau đó tải thật và
đọc trực tiếp trang Zenodo, cho kết quả xác minh:

| Mục | Giá trị đã xác minh | Nguồn |
|---|---|---|
| Record Zenodo | `3576403` | đọc trực tiếp trang, không phải `3987831` như tìm kiếm ban đầu nêu hai khả năng |
| File | `Cnn14_mAP=0.431.pth` | cùng trên |
| Kích thước | 1,365,409,299 B (1.4 GB) | tải thật |
| MD5 | `595633ac2d1cac7ef04ebf70e2fee4e4` — **khớp** MD5 công bố trên trang | so trực tiếp |
| SHA-256 | `7f0ea3a7ad9622f7bdc22439a750e04efdc1641bc4c930ff8727bb92d3141a69` | tính từ file đã tải |
| **License** | **`not recorded`** — trường Rights trên record Zenodo **để trống** | đọc trực tiếp, Codex chủ động không suy diễn |

**Sửa một sai sót của phiên bản đầu ADR này:** bản nháp ban đầu ghi "CC-BY-4.0
(theo trang Zenodo)" dựa trên tóm tắt WebSearch — tóm tắt đó **sai**. Trang
Zenodo thật để trống trường Rights. Đây là ví dụ cụ thể vì sao CLAUDE.md §5 cấm
dùng tóm tắt tìm kiếm để báo cáo: tóm tắt có thể tự tin nêu một license không
tồn tại trên nguồn thật.

Repo mã nguồn chính thức (`github.com/qiuqiangkong/audioset_tagging_cnn`) có
file `LICENSE.MIT` ở gốc — nhưng đó là license cho **mã nguồn**, không có tuyên
bố tường minh rằng nó áp dụng cho **file trọng số** phân phối qua Zenodo. Hai
tài sản khác nhau, không tự động cùng license.

### 2. License chưa xác định → xử lý thận trọng, không giả định permissive

Vì Zenodo không ghi license cho trọng số, **không giả định CC-BY hay MIT áp
dụng cho checkpoint**. Xử lý theo nguyên tắc an toàn nhất:

- Dùng checkpoint cho **mục đích nghiên cứu/nội bộ** (huấn luyện, đo trong luận
  văn) — đây là cách sử dụng phổ biến, ít tranh cãi nhất với các checkpoint học
  thuật công bố không kèm license tường minh.
- **Không** công bố lại chính file checkpoint gốc, và **không** công bố
  checkpoint đã fine-tune tiếp trên DataSEC/DataSED kèm license permissive hơn
  `CC-BY-NC-SA-4.0` của dữ liệu (ADR-0001) — giữ nguyên tắc thận trọng nhất
  trong hai giới hạn (dữ liệu NC-SA, trọng số gốc không rõ license).
- Nếu cần công bố checkpoint cùng khóa luận, liên hệ tác giả gốc xin phép tường
  minh trước — không suy diễn từ MIT của repo mã nguồn.

### 3. Nếu không tải được / license không khớp: nhánh dự phòng

Nếu Task F1 xác nhận không truy cập được checkpoint gốc (mạng, hosting đổi, hay
license siết hơn công bố), **không** âm thầm coi CNN14-scratch là nhánh B/C.
Thay vào đó:

- Đổi tên nhánh: B → "CNN14-scratch (không AudioSet)", loại khỏi bảng `C − B`
  chính, chỉ báo tham khảo.
- Ghi rõ trong ADR-0002 addendum và trong Hạn chế của báo cáo cuối: RQ1 không
  tách được đóng góp AudioSet khỏi đóng góp kiến trúc CNN14.

## Nghiệm thu

Đã đạt — artifact tại `docs/measurements/panns_checkpoint_20260923.md`, sinh bởi
`scripts.report_panns_checkpoint`. Việc nạp trọng số **không** dùng
`PannsCNN14Encoder.load_local_checkpoint` (dành cho checkpoint tự repo lưu) —
checkpoint gốc khác cấu trúc, xem [ADR-0018](ADR-0018-nap-mot-phan-checkpoint-panns.md)
cho cách nạp đúng (`load_audioset_pretrained`, chỉ transplant `conv_block1…6`).

## Consequences

### Tích cực
- Chặn được một lỗi phương pháp lớn: train "nhánh B/C" mà không có AudioSet sẽ
  làm toàn bộ RQ1 vô nghĩa mà không ai nhận ra cho tới khi viết báo cáo.

### Đánh đổi
- Thêm một bước phụ thuộc mạng ngoài (tải ~300+ MB) vào pipeline vốn đã tự chứa
  dữ liệu cục bộ. Rủi ro: mạng chậm/bị chặn trong môi trường thật lúc chạy D1.
- Checkpoint không được commit vào git (đúng CLAUDE.md — cấm commit checkpoint).
  Phải ghi rõ trong `ml/runs/` manifest đường dẫn cục bộ + SHA-256 để tái lập.

## Alternatives considered

- **Bỏ nhánh B, chỉ so A và C.** Mất khả năng tách bạch "lợi ích AudioSet nói
  chung" khỏi "lợi ích DataSEC riêng" — đúng cảnh báo `C − A` đã ghi ở ADR-0002.
- **Dùng `panns_inference` (pip package) thay vì tải checkpoint tay.** Gói này
  bọc sẵn nhưng cố định kiến trúc/tiền xử lý theo bản đóng gói của họ, khó khớp
  chính xác `PannsCNN14Encoder` tự viết trong repo — rủi ro `strict=True` vỡ vì
  khác tên tham số chứ không phải khác license.

## Evidence cần kiểm lại

- [x] SHA-256 checkpoint thật — `7f0ea3a7ad9622f7bdc22439a750e04efdc1641bc4c930ff8727bb92d3141a69` (Codex, F1).
- [x] Record Zenodo chính xác — `3576403`, MD5 khớp trang.
- [x] License đọc trực tiếp — **không ghi trên Zenodo**, không phải CC-BY-4.0 như
      bản nháp đầu suy từ WebSearch.
- [ ] Chuẩn hoá thay `bn0` — chờ thống kê train DataSEC từ B2 (ADR-0018 §3).
- [ ] Nếu cần công bố checkpoint đã fine-tune: liên hệ tác giả xác nhận license
      tường minh cho trọng số, không chỉ mã nguồn.
