# ADR-0024 — Tối ưu SED: ensemble và chọn hậu xử lý bằng CV trên dev

**Status:** Proposed — luật chọn ghi **trước** khi có đủ kết quả (xem §4)
**Date:** 2026-09-25

## Context

Sau khi tính lại (ADR-0021 §5), event-F1 SED chỉ ~0.06. Ba hướng tối ưu không cần
train lại được chọn làm trước (người dùng, 25/09):

1. **Ensemble** — trung bình xác suất của các run đã đóng băng (giảm nhiễu giữa run,
   vấn đề đã thấy ở RQ1).
2. **Kiểu θ** — A2 cho thấy θ per-class (21 tham số) overfit dev; global ổn định hơn.
3. **Percentile `g_max`** — A5 gợi ý 25 tốt hơn 50.

Quan sát ở (2) và (3) đến từ **test**, nên không được dùng để chọn cấu hình. Và với ba
ensemble đã có kết quả test, chọn "ensemble tốt nhất theo test" cũng là tuning trên test.

## Decision

### 1. Ensemble

`scripts.build_ensemble`: trung bình xác suất (không phải logit), đổi ngược về logit để
giữ contract `PredictionArtifact`; từ chối thành viên lệch cửa sổ/offset/mask/target/
split hoặc khác `split_sha256`/`data_manifest_sha256`/taxonomy. Thành viên chỉ lấy run
**sạch**: B = `054531Z`, `070927Z`, `074656Z`; C = `033537Z`, `061000Z`, `072736Z`,
`080715Z`; BC = cả 7.

### 2. Chọn cấu hình hậu xử lý trong mỗi hệ thống — chỉ bằng dev

`scripts.select_postproc_cv`: 5 fold trên dev, chia theo `leakage_group` (bản ghi gần
trùng không bị tách fold), thứ tự fold cố định bằng hash có seed. Lưới cấu hình:
{per_class, global} × `g_max` percentile {50, 25}; `d_min` giữ 5 (A5: phẳng). Mỗi cấu
hình fit θ trên 4 fold, đo event-F1 trên fold còn lại. **Chọn cấu hình có CV mean lớn
nhất; nếu không lớn hơn hẳn mặc định (per_class, 50) thì giữ mặc định.** Cấu hình thắng
fit lại trên toàn dev → `postproc_cv.json`. Luật này nằm trong code **trước khi có số
CV nào**.

### 3. Chọn hệ thống cuối — chỉ bằng dev (ghi trước)

Ứng viên: ensemble B, C, BC và **run đơn chính thức** B `054531Z`, C `061000Z` (để trả
lời "ensemble có giúp không" bằng dev, không bằng test).

- Điểm của một ứng viên = CV mean event-F1 của cấu hình được chọn ở §2.
- **Hệ thống tối ưu = ứng viên có điểm cao nhất**; bằng nhau thì chọn ứng viên ít
  model hơn.
- Mỗi ứng viên được đánh giá test **một lần** với `postproc_cv.json` của nó
  (`evaluate_run --tag cv`). Báo **tất cả** kết quả test, đánh dấu ứng viên được chọn
  theo luật; không chọn lại sau khi xem test.
- Báo kèm độ lệch chuẩn giữa các fold. Chênh lệch nhỏ hơn mức đó không được gọi là
  "tốt hơn".
- Luật nằm trong `scripts.report_sed_optimization` (`select_system` chỉ nhận số dev).
  Trình tự: đủ CV của mọi ứng viên → `--dev-only` ghi CV + lựa chọn, **commit** → mới
  chạy `evaluate_run --tag cv` → bản đầy đủ. Git chứng minh lựa chọn có trước test.

### 4. Đã biết gì khi viết ADR này (công khai để phản biện được)

- **Đã biết:** kết quả test của 3 ensemble với hậu xử lý mặc định (event-F1 B 0.0553,
  C 0.0636, BC 0.0696; PSDS-2 0.693/0.705/0.716); CV mean của cấu hình (per_class, 50)
  cho 3 ensemble (B 0.0779, C 0.0662, BC 0.0656).
- **Chưa biết:** CV của 3 cấu hình còn lại, CV của run đơn, mọi kết quả test với
  `postproc_cv.json`.
- **Cập nhật 25/09 chiều (vẫn trước mọi test với `postproc_cv.json`):** CV đủ 4 cấu hình
  của 3 ensemble đã có — cả ba chọn `global|25`. CV run đơn và mọi kết quả test với
  `postproc_cv.json` vẫn chưa biết.

## Consequences

### Tích cực

- Mọi lựa chọn (kiểu θ, percentile, hệ thống) đi qua dev; test chỉ để báo.
- Ensemble tái dùng dự đoán đã có — không tốn GPU.

### Đánh đổi

- CV trên dev 137 recording có phương sai lớn; luật §3 có thể chọn một hệ thống mà test
  cho thấy không phải tốt nhất — đó là cái giá của không tuning trên test, phải báo đúng
  như vậy.
- W5 (RQ2) giữ nguyên SED prediction đóng băng của run B `054531Z` (E5); hệ thống tối
  ưu chỉ đổi đầu vào cho W6 nếu có quyết định riêng.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| Chọn ensemble tốt nhất theo test (BC) | Tuning trên test |
| Chọn cấu hình θ/percentile theo A2/A5 | Hai ablation đó đo trên test |
| Trung bình logit | Một thành viên tự tin quá mức chi phối trung bình; trung bình xác suất ổn định hơn |
| CV chia ngẫu nhiên theo recording | Bản ghi gần trùng (cùng `leakage_group`) rơi vào hai fold → CV lạc quan giả |
