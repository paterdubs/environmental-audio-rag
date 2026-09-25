# ADR-0024 — Tối ưu SED: ensemble và chọn hậu xử lý bằng CV trên dev

**Status:** Accepted (25/09 tối) — luật chọn ghi **trước** khi có kết quả (§4); kết quả ở §5
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
- **Cập nhật 25/09 tối — lựa chọn đã chốt, commit trước test:** CV đủ cho 5 ứng viên;
  cả năm chọn `global|25`. Luật §3 chọn **ensemble C** (CV 0.1538 ± 0.0214); chênh với
  ensemble B xếp thứ hai +0.0204 < sd giữa fold → không gọi là "tốt hơn" B
  (`sed_optimization_20260925_dev.md`). Chưa chạy test nào với `postproc_cv.json`.
  Lưới θ đã kiểm trên dev: đỉnh ở 0.95–0.97, không cắt cụt đáng kể
  (`threshold_grid_edge_20260925.md`).

### 5. Kết quả (test chạy một lần mỗi ứng viên, sau commit `0387225`)

Cả 5 ứng viên chọn `global|25` (θ = 0.95 mọi lớp, `g_max` percentile 25). Nguồn:
`sed_optimization_20260925.md` (dev CV + test), `<run>_eval_cv.md`.

| Ứng viên | CV dev | event-F1 mặc định → CV [95% CI] | PSDS-1 | PSDS-2 |
|---|---:|---|---:|---:|
| **ensemble C (chọn)** | **0.1538** | 0.0636 → **0.0941** [0.0624, 0.1277] | 0.3166 → 0.3489 | 0.7053 → 0.6987 |
| ensemble B | 0.1334 | 0.0553 → 0.0969 [0.0651, 0.1298] | 0.2996 → 0.3174 | 0.6929 → 0.6800 |
| ensemble BC | 0.1236 | 0.0696 → 0.1001 [0.0656, 0.1336] | 0.3147 → 0.3402 | 0.7157 → 0.7074 |
| run đơn B `054531Z` | 0.1259 | 0.0621 → 0.1048 [0.0772, 0.1380] | 0.2818 → 0.2934 | 0.6456 → 0.6312 |
| run đơn C `061000Z` | 0.1198 | 0.0472 → 0.0801 [0.0549, 0.1079] | 0.2873 → 0.3150 | 0.6462 → 0.6324 |

**Đọc đúng:**

1. **Hậu xử lý chọn trên dev tổng quát hoá sang test**: event-F1 tăng ở 5/5 ứng viên
   (+0.030 … +0.043), precision **và** recall cùng tăng ở 5/5, PSDS-1 tăng 5/5.
   PSDS-2 giảm nhẹ 5/5 (−0.007 … −0.014). PSDS quét operating point nên không phụ
   thuộc θ — thay đổi PSDS đến từ `g_max` percentile 25 (gap ngắn hơn → ít gộp event).
   Cơ chế theo phân tích lỗi: nhầm lớp giảm mạnh (ensemble C 229 → 36), dự đoán ít
   event hơn (613 → 408 trên 740 tham chiếu) → **deletion thành lỗi chính** (232 → 293).
   Đây là điểm vận hành thiên về precision; recall vẫn thấp (0.073).
2. **Ensemble**: cùng nhánh, ensemble nâng PSDS-1/2 so với run đơn (B 0.3174/0.6800 vs
   0.2934/0.6312; C 0.3489/0.6987 vs 0.3150/0.6324); event-F1 lẫn lộn (C +0.014, B
   −0.008). Không kết luận ensemble cải thiện event-F1.
3. **Hệ thống được chọn không cao nhất trên test** (run đơn B 0.1048 > ensemble C
   0.0941), nhưng CI của mọi ứng viên chồng lấn lớn — test không phân biệt được các ứng
   viên. Đúng rủi ro đã ghi trước ở Đánh đổi; **không chọn lại**.
4. **CV dev lạc quan hơn test** (0.12–0.15 so với 0.08–0.10): CV là trung bình F1 trên
   fold ~27 recording. Không dùng số CV làm ước lượng hiệu năng test.

### 6. Provenance và quan hệ với ADR-0003

- Manifest 3 ensemble ghi `git.dirty=true` (build ở `1ca6bb4` khi tree bẩn). Dựng lại
  trên tree sạch `ed5289b` (25/09 tối): SHA-256 dự đoán dev/test **trùng khít** cả 3
  (B `bdabcbbb…`/`dd28f594…`, C `7a6e5f02…`/`c5e3007b…`, BC `8b76e3f6…`/`f3c800ac…`).
- CV run đơn: `select_postproc_cv --workers 8`, git `eb292a6`/`7c0c60a`, `dirty=false`.
  CV ensemble chạy bản tuần tự trước khi có trường `git`; bản song song tái lập đúng
  từng bit 5 fold + θ của ensemble B `global|25` (commit `eb292a6`).
- **ADR-0003 không đổi**: θ per-class + `g_max` percentile 50 vẫn là giao thức của số
  chính thức RQ1 (ADR-0021). Cấu hình `global|25` là của **hệ thống tối ưu** theo ADR
  này. Nợ kỹ thuật #8 (percentile `g_max` chọn không có cơ sở) đóng: cả 5 ứng viên chọn
  25 **trên dev** — cùng hướng A5 đã thấy trên test, nay có cơ sở hợp lệ.

## Consequences

### Tích cực

- Mọi lựa chọn (kiểu θ, percentile, hệ thống) đi qua dev; test chỉ để báo.
- Ensemble tái dùng dự đoán đã có — không tốn GPU.

### Đánh đổi

- CV trên dev 137 recording có phương sai lớn; luật §3 có thể chọn một hệ thống mà test
  cho thấy không phải tốt nhất — đó là cái giá của không tuning trên test, phải báo đúng
  như vậy.
- W5 (RQ2) giữ nguyên SED prediction đóng băng của run B `054531Z` (E5); hệ thống tối
  ưu chỉ đổi đầu vào cho W6 nếu có quyết định riêng. Lưu ý cho quyết định đó: cấu hình
  tối ưu dự đoán ít event hơn tham chiếu (deletion là lỗi chính) → retrieval trên event
  dự đoán sẽ bị giới hạn bởi recall SED.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| Chọn ensemble tốt nhất theo test (BC) | Tuning trên test |
| Chọn cấu hình θ/percentile theo A2/A5 | Hai ablation đó đo trên test |
| Trung bình logit | Một thành viên tự tin quá mức chi phối trung bình; trung bình xác suất ổn định hơn |
| CV chia ngẫu nhiên theo recording | Bản ghi gần trùng (cùng `leakage_group`) rơi vào hai fold → CV lạc quan giả |
