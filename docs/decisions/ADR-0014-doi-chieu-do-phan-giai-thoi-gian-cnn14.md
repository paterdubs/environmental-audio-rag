# ADR-0014 — Đối chiếu độ phân giải thời gian khi cắm CNN14 vào SoundEventDetector

**Status:** Accepted
**Date:** 2026-09-23

## Context

C1 giao cho Codex: sửa `load_classifier_encoder` (`ml/models/audio.py:78`) để nhận
CNN14. Codex đo trực tiếp qua `tests/test_panns.py` và `tests/test_models.py` rồi
dừng lại, đúng giao thức §6:

> `PannsCNN14Encoder` nhận 128 frame và trả `(B, C, 2)` — giảm thời gian **/64**.
> `SoundEventDetector` hiện trả `(B, T, 21)` và loss dùng target ở toàn bộ T frame.
> Thay encoder rồi chỉ sửa `strict=True` sẽ làm logit CNN14 có T/64 frame và SED
> loss lỗi shape — đây không phải tương thích checkpoint thuần tuý.

Đo lại: `AudioEncoder` dùng `MaxPool2d(kernel=(2,1))` — chỉ pool tần số, giữ
nguyên T. `PannsCNN14Encoder` dùng `avg_pool2d(kernel=(2,2))` sáu lần — pool **cả
hai chiều**, T còn T/64. `SoundEventDetector.__init__` hardcode
`self.encoder = AudioEncoder()`, không nhận tham số — nên trước C1, CNN14 không
thể cắm vào SED head bằng bất kỳ cách nào, kể cả nếu `strict=True` được sửa đúng.

### Cửa sổ SED thật đủ dài, nhưng biên là có thật

`ml/training/sed.py` dùng `window_frames=500` — ở `logmel_v1` 50 fps là 10 giây,
qua sáu lần floor-chia-2 (500→250→125→62→31→15→7) không về 0. Nhưng một input
ngắn hơn `2^6 = 64` frame **sẽ** về 0 giữa chừng và `avg_pool2d` ném lỗi PyTorch
khó đọc ở lần pool cuối, không phải lỗi rõ ràng ở đầu vào.

## Decision

### 1. `SoundEventDetector` nhận `encoder` qua constructor

Giống `PannsAudioClassifier` đã làm. Không đổi hành vi mặc định
(`encoder=None` → vẫn `AudioEncoder()`).

### 2. Phục hồi T bằng nearest-neighbor interpolate, không phải linear

```python
target_frames = inputs.shape[-1]
encoded = self.encoder(inputs)
if encoded.shape[-1] != target_frames:
    encoded = nn.functional.interpolate(encoded, size=target_frames, mode="nearest")
```

Khi `T_out == T_in` (đường `AudioEncoder` cũ), điều kiện không kích hoạt — hành vi
cũ giữ nguyên, đã kiểm bằng test hồi quy.

Nearest được chọn thay vì linear: mỗi frame đã pool mang thông tin của một cửa sổ
~64 frame gốc thông qua receptive field của conv+pool. Linear interpolation giữa
hai frame đã pool sẽ **bịa ra** một giá trị trung gian không ứng với bất kỳ context
âm thanh thật nào. Nearest chỉ lặp lại đúng giá trị đã tính — đây cũng là cách
PANNs gốc (Kong et al., 2020) khôi phục framewise output sau pooling.

### 3. Guard tường minh cho input quá ngắn

`PannsCNN14Encoder.forward` kiểm `frames < time_reduction` (= 64) và raise
`ValueError` nêu rõ số frame tối thiểu, thay vì để `avg_pool2d` ném lỗi khó đọc
ở lần pool cuối cùng.

### 4. `load_classifier_encoder` kiểm khớp kiểu encoder trước khi `strict=True`

So `set(self.encoder.state_dict())` với khoá trong checkpoint. Lệch → raise với
tên lớp encoder hiện tại và vài khoá thiếu/thừa đầu tiên, thay vì để PyTorch báo
lỗi `strict` chung chung không nói encoder nào đang được mong đợi.

## Giới hạn khoa học — phải nêu, không chỉ sửa code

**Phục hồi shape không phục hồi thông tin.** Sau `interpolate`, tensor có đúng T
frame để loss và metric chạy được, nhưng độ phân giải thời gian **thật** của
nhánh CNN14 vẫn bị chặn ở khối 64 frame — mỗi khối 64 frame liên tiếp mang cùng
một giá trị dự đoán, vì chúng cùng đến từ một frame đã pool. Ở `logmel_v1` 50 fps,
64 frame = **1.28 giây**.

[evaluation_protocol.md](../evaluation_protocol.md) dùng collar **0.2 giây** cho
biên sự kiện. Một sự kiện ngắn hơn 1.28 giây, hoặc một cặp biên onset/offset nằm
trong cùng khối 64 frame, **không thể** được nhánh CNN14 định vị chính xác hơn
mức khối — bất kể loss hội tụ tốt đến đâu. Nhánh `AudioEncoder` (baseline) không
có giới hạn này.

**Hệ quả cho RQ1 (C − B).** Nếu nhánh C (PANNs) thua nhánh B ở collar 0.2s, phải
phân biệt được hai khả năng: (a) transfer từ DataSEC không giúp ích, hay (b) độ
phân giải khối 1.28s của CNN14 tự nó áp trần lên metric bất kể transfer tốt hay
không. Không phân biệt được hai khả năng này thì kết luận về RQ1 không có cơ sở.

## Consequences

### Tích cực

- CNN14 cắm được vào `SoundEventDetector` mà không vỡ `AudioEncoder` cũ — cả hai
  đường có test riêng.
- Lỗi sai kiểu encoder hoặc input quá ngắn giờ báo rõ nguyên nhân, không phải
  `RuntimeError` chung chung của PyTorch.

### Đánh đổi / việc còn nợ

- **Chưa đo được** ảnh hưởng thật của khối 1.28s lên metric event-based F1/PSDS.
  Ghi vào nợ kỹ thuật: sau khi có D1 (train E1), đo per-frame agreement giữa dự
  đoán CNN14 và ground truth ở độ phân giải khối so với độ phân giải frame, trước
  khi diễn giải RQ1.
- Có thể cần báo cáo **hai** phép đo cho nhánh C: metric ở collar chuẩn 0.2s, và
  một collar nới bằng đúng độ phân giải khối, để tách bạch hai khả năng ở trên.
  Quyết định này để sau khi có số đo thật, không suy đoán trước.

## Alternatives considered

- **Giảm số lớp pool của CNN14** (ví dụ chỉ pool tần số ở vài khối cuối). Từ bỏ
  kiến trúc CNN14 chuẩn — nếu thesis dẫn "PANNs CNN14" phải đúng như công bố.
- **Đổi target SED về frame rate thấp hơn** (downsample nhãn/collar theo khối
  64 frame). Không khả thi: `evaluation_protocol.md`, cổng D3 fingerprint, và độ
  nhất quán chú giải đã đo (collar 0.2s) đều neo vào 50 fps của toàn bộ dự án.
- **Linear interpolation thay vì nearest.** Tạo cảm giác độ phân giải cao hơn
  thật, dễ đọc nhầm rằng CNN14 định vị được biên chính xác hơn khả năng thật.

## Evidence cần kiểm lại

- Sau D1: đo tỷ lệ sự kiện DataSED ngắn hơn 1.28s trong ground truth — nếu cao,
  giới hạn ở trên ảnh hưởng phần lớn sự kiện chứ không phải trường hợp biên.
- So sánh event-based F1 của nhánh C ở hai collar (0.2s và ~1.3s) để tách bạch
  hai khả năng nêu trên.
