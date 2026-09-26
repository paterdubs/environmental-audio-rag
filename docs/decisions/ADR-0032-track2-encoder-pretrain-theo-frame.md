# ADR-0032 — Track 2: encoder pretrain theo frame (PretrainedSED) — thiết kế, cổng T0 và ứng viên ghi trước

**Status:** Proposed — agent quyết theo uỷ quyền ADR-0031 §3 (người dùng duyệt Track 2 ngày
26/09); **chờ người dùng duyệt**. Ứng viên §5 được ghi **trước** khi có bất kỳ số Track 2 nào và
không đổi sau khi có số. Cổng T0 bước 1–2 xong (26/09 tối); bước 3–4 chờ GPU, tức sau S9.
**Date:** 2026-09-26

## Context

- ADR-0031 §3 duyệt Track 2 qua cổng T0 và dự kiến làm `frame_mn10` trước.
- **Cổng T0 bước 1–2** (RELATED_WORK §2.1 (2), nay ở mức V3 vì đã đọc trực tiếp PDF v2, code và
  LICENSE):
  - **Frozen** (đóng băng transformer, chỉ train lớp tuyến tính) đạt DESED PSDS1 45.4–49.2, gần
    bằng fine-tune toàn bộ (47.6–49.2). BEATs strong: frozen 48.1, fine-tune 49.2.
  - `frame_mn06/10` **không có số nào trong bài**; README chỉ ghi "NEW".
  - License: PretrainedSED MIT; BEATs (`microsoft/unilm`) MIT; EfficientAT (nền của `frame_mn`) MIT;
    checkpoint ATST-F CC BY 4.0; M2D license riêng dạng PDF.
- **SED v2 (ADR-0030):** ba seed có CV dev 0.1900 / 0.2096 / 0.2169. Ablation cho thấy độ phân
  giải thời gian là yếu tố quyết định (bỏ nó thì −0.084), còn augmentation và trần `pos_weight`
  không phân biệt được (`sed_v2_ablation_20260926.md`).
- GPU 8 GB: fine-tune transformer khoảng 90M tham số ở cửa sổ 10 s có rủi ro bộ nhớ; frozen chỉ
  cần forward.

## Decision

### 1. Thứ tự: T2a (BEATs đóng băng + head) trước, T2b (`frame_mn10` fine-tune) sau

Quyết định này đổi thứ tự dự kiến ở ADR-0031 §3, dựa trên dữ kiện V3 có sau ngày duyệt:
- T2a có số trong bài;
- T2a rẻ: embedding tính một lần, head train nhanh, nên chạy đủ seed được;
- `frame_mn10` chưa có số nào.

Chỉ chọn **một** transformer, để giới hạn số ứng viên. BEATs được chọn: frozen 48.1 so với
ATST-F 47.7, và license repo MIT.

### 2. T2a — BEATs strong đóng băng + head

- Đầu vào: waveform 16 kHz (resample từ 44.1 kHz), cửa sổ 10 s và hop như v2, ghép như
  `collect_predictions`.
- Encoder: `BEATs_strong_1.pt` ở chế độ eval, không cập nhật trọng số. Đầu ra 250 × 768 / 10 s
  (40 ms), qua wrapper của repo.
- Cache embedding **chỉ cho train và dev**. Embedding test chỉ trích **sau** khi vòng chọn cuối
  đã commit (ADR-0031 §4), giống `dump_predictions`.
- Head: BiGRU 2×256 + tuyến tính 21 lớp, **giống head v2** (ADR-0030 §1), để so sánh cô lập phần
  encoder. Logit 40 ms được lặp (nearest) lên đúng lưới 10 ms của `logmel_panns_v1` theo từng
  recording. Nhờ vậy NPZ, hậu xử lý, đánh giá và ensemble với v2 dùng lại nguyên.
- Train:
  - 30 epoch, warmup 1 + cosine, BCE với trần `pos_weight` 10, random crop trên cửa sổ cache.
  - Không augmentation (ablation v2: không phân biệt được).
  - Checkpoint chọn theo macro-AP frame trên dev.
  - lr của head chọn bằng pilot dev {3e-4, 1e-3, 3e-3} như ADR-0030 §2.
  - Seed {20260922, 2, 3}.

### 3. T2b — `frame_mn10` fine-tune toàn bộ

- Checkpoint `frame_mn10_strong_1.pt`, dùng frontend của repo (128 mel, n_fft 512, win 400,
  hop 160 ở 16 kHz). Thay lớp 447 bằng 21 lớp; không thêm sequence model (như student trong bài).
- Recipe v2 ở những núm áp dụng được: 30 epoch, warmup 1 + cosine, mixup 0.5, trần 10, chọn
  checkpoint theo macro-AP dev. lr chọn bằng pilot dev {1e-4, 3e-4, 1e-3}. Seed {20260922, 2, 3}.
- Logit đưa lên lưới 10 ms như §2.

### 4. Cổng T0 bước 3–4, cho từng họ, trước run đầy đủ

- Bước 3: bộ nhớ vừa GPU 8 GB; ghi batch size.
- Bước 4: một epoch dev đi hết đường ống (train → dump `--verify-dev` trùng bit → CV hậu xử lý).
- Hỏng bước nào thì ghi lý do vào ADR này và dừng họ đó.
- Checkpoint tải từ release v0.0.1 được ghi SHA-256 vào ADR này, như ADR-0015.
- Code model ngoài: chỉ chép phần tối thiểu, kèm file LICENSE gốc (MIT), vào `ml/models/external/`.
  Không thêm phụ thuộc pip nếu không cần.
- Code Track 2 chỉ vào master **sau khi S9 xong**, vì RQ1-v2 cần code train giữ nguyên.

### 5. Ứng viên cho vòng chọn cuối (ADR-0031 §4), ghi trước khi có số

- (f1) ensemble T2a, 3 seed.
- (f2) ensemble T2b, 3 seed.
- (f3) ensemble T2a 3 seed + B-v2 3 seed (6 model).
- (f4) ensemble T2b 3 seed + B-v2 3 seed (6 model).

Họ nào không qua T0 hoặc chưa xong CV dev trước 18/10 thì bỏ các ứng viên của họ khỏi vòng.
Luật chọn như ADR-0031 §4 (CV dev micro; hoà thì chọn ít model hơn).

### 6. Không làm trong Track 2

Ghi ở đây để khỏi mở rộng giữa chừng:
- fine-tune toàn bộ BEATs/ATST-F (bộ nhớ);
- bỏ 2 lớp transformer cuối (thêm một núm);
- layer-wise lr decay (chỉ cần khi fine-tune transformer);
- M2D (license riêng); ASiT (chưa kiểm license).

## Consequences

### Tích cực

- Có encoder pretrain theo frame với chi phí thấp nhất; đủ 3 seed; head giống v2 nên hiệu số đo
  được phần encoder.
- Lưới 10 ms chung nên ensemble dị loại (f3, f4) không cần code đánh giá mới.

### Đánh đổi

- Frozen có thể thua fine-tune khoảng 1 điểm PSDS1 (DESED), và khoảng cách trên DataSED chưa biết.
- Cache embedding train + dev ước chừng 1–2 GB (fp16).
- Thêm code ngoài; embedding test chỉ có sau lựa chọn cuối.
- Thứ tự khác ADR-0031 §3; ghi ở đây, không sửa ADR đã duyệt.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| `frame_mn10` trước (ADR-0031 §3) | Không có số trong bài; T2a có số và rẻ hơn để chạy đủ seed |
| ATST-F thay BEATs | Frozen 47.7 < 48.1; checkpoint CC BY 4.0 (dùng được) — chọn một để giới hạn ứng viên |
| Head tuyến tính như bài | Head giống v2 cô lập được phần encoder; event DataSED dài, cần ngữ cảnh thời gian |
| Fine-tune BEATs toàn bộ | Rủi ro bộ nhớ 8 GB; bài cho thấy frozen gần bằng |
| Trích embedding test ngay | Trái nguyên tắc "không có gì từ test trước lựa chọn cuối" |

## Evidence cần kiểm lại

- Mọi số trong bài là trên DESED (miền nhà ở), không phải DataSED; "frozen gần fine-tune" có thể
  không đúng ở đây.
- License trọng số BEATs: repo `microsoft/unilm` là MIT, nhưng chưa đọc trang phát hành trọng
  số → ⚠️ xác minh lại trước khi công bố model.
- Kích thước checkpoint lấy từ API release; SHA-256 ghi khi tải (T0 bước 3).
