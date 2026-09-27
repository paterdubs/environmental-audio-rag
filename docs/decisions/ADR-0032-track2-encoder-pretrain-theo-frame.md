# ADR-0032 — Track 2: encoder pretrain theo frame (PretrainedSED) — thiết kế, cổng T0 và ứng viên ghi trước

**Status:** Accepted — người dùng duyệt 27/09/2026 ("tải checkpoint BEATs và làm Track 2 thật").
Ứng viên §5 được ghi **trước** khi có bất kỳ số Track 2 nào và không đổi sau khi có số. Cổng T0
cho T2a: bước 1–2 xong 26/09 tối, bước 3–4 xong 27/09 (§7). Luật pilot lr (§8) ghi và commit
trước khi chạy pilot.
**Date:** 2026-09-26 (duyệt và cập nhật 2026-09-27)

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

### 7. Cổng T0 cho T2a — kết quả (27/09)

**Nguồn đã ghim.**
- Checkpoint `BEATs_strong_1.pt`, release v0.0.1: 364,091,999 B (khớp kích thước release),
  SHA-256 `db13a79ae90a0cfd0f9911a6a1d8cdb89324322bee642dcfe32de022123b8b54`. Code kiểm hash này
  mỗi lần nạp.
- Mã BEATs chép từ PretrainedSED commit `1aa47e48` vào `ml/models/external/beats/`, kèm LICENSE
  MIT của PretrainedSED và của `microsoft/unilm`. `NOTICE.md` ghi SHA-256 từng file gốc và 3 chỗ
  sửa.
- Checkpoint gồm 250 tensor encoder (90,354,032 tham số) và head AudioSet 447 lớp (bỏ).

**Bước 3 — bộ nhớ và tốc độ** (`track2_t0_beats_20260927.md`, chỉ cửa sổ dev). Đạt.
- Đỉnh VRAM khi forward encoder ở batch 24 là 1604 MB; một bước train head ở batch 24 là 1615 MB
  (GPU 8192 MB).
- 0.0111 s/cửa sổ (fp16), tức khoảng 64 s mã hoá mỗi epoch cho 4311 cửa sổ train và 1462 dev.
- fp16 lệch fp32 tối đa 0.0027 trên embedding (cosine làm tròn 1).
- Kiểm đường ống: head AudioSet của chính checkpoint gọi đúng nghĩa nhiều lớp DataSED (Church
  bell, Caterwaul, Vehicle horn, Music, Male speech). Đây là kiểm, không phải metric.

**Bước 4 — một epoch hết đường ống** (`sed_polyphonic_20260927T053736Z`, tree sạch `2026292f`).
Đạt.
- Run `complete`, `dirty=false`. Mã thoát 127 là lỗi giả đã biết của GRU nhiều lớp
  (TRAINING_OPS_PLAN §7 #6).
- `dump_predictions --verify-dev` trùng từng bit logit dev lúc train.
- CV hậu xử lý: kết quả ghi ở §9 khi chạy xong.

**Chỗ làm khác bản nháp §2, có lý do.**
1. **Không cache embedding.** Encoder chạy trong đường dữ liệu (`ml/training/encoded.py`) và mã
   hoá crop mới mỗi epoch.
   - Random crop giữ đúng nghĩa của v2 (bước 10 ms), thay vì crop trên các cửa sổ đã cache.
   - Chi phí đo được chỉ khoảng 64 s/epoch, và không tốn thêm đĩa (ổ D còn 8.5 GB).
   - Nguyên tắc về test giữ nguyên: embedding test chỉ sinh khi `dump_predictions --split test`
     chạy sau vòng chọn cuối.
2. **Đầu vào** là cache waveform 16 kHz int16 (`scripts.cache_waveforms`, dùng cùng
   `librosa.load` như log-mel), cho mọi split. Đây là tiền xử lý đầu vào như log-mel đã có cho
   test, không phải đầu ra của model.
3. **fbank Kaldi viết lại bằng torch** (`ml/features/kaldi_fbank.py`), vì torchaudio không là phụ
   thuộc. Kết quả trùng từng bit torchaudio 2.11.0 trên CPU (tín hiệu tổng hợp và 8 cửa sổ dev
   thật). Ở cấu hình của BEATs có đúng một bộ lọc mel rỗng (kênh 3, luôn bằng log ε); torchaudio
   cũng vậy.
4. **"40 ms" của BEATs là danh nghĩa.**
   - Patch 16×16 trên fbank 998×128 cho 62 bước thời gian (160 ms) × 8 dải tần = 496 token.
   - PretrainedSED gộp chuỗi 496 token trải phẳng về 250 bằng adaptive average pooling (bài
     báo chỉ ghi "S = 496 … căn về 40 ms").
   - Checkpoint `strong_1` được huấn luyện với đúng phép gộp đó, nên vị trí *i* được dùng như
     khung 40 ms thứ *i*. Độ phân giải thật có thể thô hơn 40 ms — đó là câu hỏi cho kết quả
     T2a, không phải lỗi port.
5. Mã ngoài sửa chỗ #3: layerdrop của bản gốc rút `np.random` ở mọi forward, kể cả eval, làm
   dịch chuỗi random crop. Giờ chỉ rút khi train; hành vi eval không đổi.

### 8. Pilot lr head và run đầy đủ của T2a (ghi trước khi chạy pilot)

- Pilot như ADR-0030 §2:
  - 3 run × 3 epoch, lr head ∈ {3e-4, 1e-3, 3e-3};
  - lr hằng số (`--warmup-epochs 0 --no-cosine-decay`), seed 0, recipe `t2a` cho mọi núm khác;
  - toàn bộ dev (1462 cửa sổ) thay vì 300 cửa sổ, vì ở đây rẻ.
- **Luật:** chọn lr có macro-AP frame dev cao nhất ở epoch 3.
- Run đầy đủ: recipe `t2a` với lr đã chọn, seed {20260922, 2, 3}, mỗi run trên tree sạch và code
  train không đổi giữa ba run.
- Sau mỗi run: CV cả hai họ hậu xử lý (`select_postproc_cv --modes global`, `select_sebb_cv`),
  như các ứng viên (a)–(e).
- Sau ba run: dựng (f1) T2a × 3 và (f3) T2a × 3 + B-v2 × 3 bằng `build_ensemble --splits dev`,
  rồi CV. Không mở test (ADR-0031 §4).

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
- ~~Kích thước checkpoint lấy từ API release; SHA-256 ghi khi tải (T0 bước 3).~~ Đã ghi ở §7
  (27/09): kích thước khớp release. Release không công bố hash để đối chiếu, nên SHA-256 là của
  bản đã tải.
