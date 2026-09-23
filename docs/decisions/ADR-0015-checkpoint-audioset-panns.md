# ADR-0015 — Nguồn checkpoint PANNs CNN14 pretrained trên AudioSet

**Status:** Proposed — chờ tải và xác minh thật (xem "Evidence cần kiểm lại")
**Date:** 2026-09-23

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

### 1. Nguồn checkpoint

Tìm thấy qua tra cứu công khai (WebSearch, 23/09/2026), **chưa tải/hash để xác
minh trực tiếp trong repo này** — đánh dấu ⚠️ CẦN XÁC MINH cho từng mục:

| Mục | Giá trị | Trạng thái |
|---|---|---|
| Tác giả gốc | Kong, Qiuqiang et al. — "PANNs: Large-Scale Pretrained Audio Neural Networks for Audio Pattern Recognition", IEEE/ACM TASLP 2020 | ⚠️ CẦN XÁC MINH số trang/DOI bài báo |
| Repo chính thức | `github.com/qiuqiangkong/audioset_tagging_cnn` | ⚠️ CẦN XÁC MINH còn hoạt động, README khớp |
| Kho lưu checkpoint | Zenodo, hai record xuất hiện trong tra cứu: `3576403` (tổng hợp mọi checkpoint PANNs) và `3987831` (dùng trong script tải của repo chính thức) | ⚠️ CẦN XÁC MINH record nào là bản chuẩn cho `Cnn14_mAP=0.431.pth` |
| File cần | `Cnn14_mAP=0.431.pth` — clip-level CNN14, 64 mel, 32 kHz, khớp `logmel_panns_v1` | ⚠️ CẦN XÁC MINH tên file và SHA-256 thật sau khi tải |
| License | CC-BY-4.0 (theo trang Zenodo) | ⚠️ CẦN XÁC MINH đọc trực tiếp trang bản quyền, không suy từ tóm tắt tìm kiếm |

**Không dùng các con số trên để báo cáo trong luận văn cho tới khi Task F1 (bên
dưới) tải và xác minh SHA-256 thật.** Đây đúng tinh thần CLAUDE.md §5: không bịa
trích dẫn, đánh dấu rõ khi chưa xác minh.

### 2. Tương thích license

CC-BY-4.0 (checkpoint) chỉ cần ghi công, không có điều khoản ShareAlike — không
xung đột với `CC-BY-NC-SA-4.0` của DataSEC/DataSED (ADR-0001). Hai license áp
lên hai tài sản khác nhau (trọng số vs dữ liệu) nên không cộng dồn điều khoản,
nhưng **checkpoint đã fine-tune tiếp trên DataSEC/DataSED thì sản phẩm phái sinh
đó thừa hưởng NC-SA của dữ liệu** — không được công bố checkpoint đã fine-tune
với license permissive hơn NC-SA. Ghi vào [DATA_PLAN.md §2](../DATA_PLAN.md)
khi có checkpoint fine-tune thật.

### 3. Nếu không tải được / license không khớp: nhánh dự phòng

Nếu Task F1 xác nhận không truy cập được checkpoint gốc (mạng, hosting đổi, hay
license siết hơn công bố), **không** âm thầm coi CNN14-scratch là nhánh B/C.
Thay vào đó:

- Đổi tên nhánh: B → "CNN14-scratch (không AudioSet)", loại khỏi bảng `C − B`
  chính, chỉ báo tham khảo.
- Ghi rõ trong ADR-0002 addendum và trong Hạn chế của báo cáo cuối: RQ1 không
  tách được đóng góp AudioSet khỏi đóng góp kiến trúc CNN14.

## Nghiệm thu

Task F1 (giao Codex, xem `docs/AGENT_SYNC.md`):

```bash
curl -fsSL -o /tmp/panns_checkpoint.pth "<URL xác minh được ở bước 1>"
sha256sum /tmp/panns_checkpoint.pth
```

Ghi SHA-256 thật, kích thước byte thật, và license đọc trực tiếp từ trang nguồn
vào `docs/measurements/panns_checkpoint_20260923.md`. Cập nhật ADR này từ
**Proposed** thành **Accepted** sau khi ba mục ⚠️ đầu được xác minh.

`PannsCNN14Encoder.load_local_checkpoint` đã có sẵn (`ml/models/panns.py`) và
nhận `strict=True` mặc định — kiểm tra checkpoint có đúng 6 khối kênh
`(64, 128, 256, 512, 1024, 2048)` khớp cấu hình mặc định của lớp trước khi nạp.

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

- [ ] SHA-256 checkpoint thật sau khi tải (Task F1).
- [ ] Record Zenodo chính xác (3576403 hay 3987831) — có thể cả hai trỏ cùng
      file vật lý, cần xác nhận bằng hash trùng nhau.
- [ ] Đọc trực tiếp trang license Zenodo, không suy từ kết quả tìm kiếm tóm tắt.
