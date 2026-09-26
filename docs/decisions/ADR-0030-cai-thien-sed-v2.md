# ADR-0030 — Cải thiện SED (v2): chẩn đoán, văn liệu, kế hoạch và luật chọn ghi trước

**Status:** Proposed — agent đề xuất 26/09 theo yêu cầu người dùng ("SED quá thấp, tự nghĩ cách,
tìm hiểu văn liệu"); **chờ duyệt**. Luật chọn §5 ghi **trước** khi có bất kỳ số v2 nào.
**Date:** 2026-09-26

## Context

Event-F1 test của hệ thống tốt nhất (ensemble C, ADR-0024) là 0.094. Nó giới hạn mọi tầng sau:
caption e2e và RAG (khoảng 45% recording được trích dẫn đúng theo ground truth).

### 1. Chẩn đoán (chỉ dev + ground truth, `sed_ceilings_20260926.md`)

| Câu hỏi | Kết quả |
|---|---|
| Trần event-F1 của model **hoàn hảo** ra quyết định theo khối 0.64 s (CNN14 trong repo) | **0.63** |
| Như trên với khối ≤ 0.32 s | 1.00 |
| Người so với người (8 cặp recording giống từng byte, chú giải hai lần) | **0.58** |
| Hệ thống hiện tại trên dev (in-sample): event-F1 / chỉ onset / chỉ offset | 0.159 / **0.23** / 0.50 |
| Segment-based F1 (1 s) của hệ thống hiện tại | **0.654** |
| Phân rã 886 event dev | 112 khớp · **417 chồng đúng lớp nhưng lệch biên** · 357 bỏ sót |

Đọc: model **nhận ra** âm thanh khá tốt (segment F1 0.65), nhưng **đặt onset sai** và bỏ sót
40% event. Có ba nguyên nhân đo được:

1. **Độ phân giải thời gian.** `PannsCNN14Encoder` pool thời gian ở cả 6 khối (/64 → 0.64 s
   ở 100 fps). CNN14 gốc **không** pool ở khối 6 (/32). Code gốc
   `audioset_tagging_cnn/pytorch/models.py`, đối chiếu 26/09, dùng `pool_size=(2, 2)` cho
   khối 1–5 và `(1, 1)` cho khối 6, kèm dropout 0.2 sau mỗi khối; encoder của repo không có
   dropout này. Chỉ riêng việc pool thêm đã chặn event-F1 ở 0.63 ngay cả khi model hoàn hảo.
2. **Posterior bão hoà.** `pos_weight` tới 50 đẩy xác suất lên cao ngay cả ngoài event. Ví dụ
   S-0021, lớp `vehicle_pass_by`: điểm dao động 0.5–1.0 suốt recording, kể cả đoạn 56–89 s
   không có event đó. Vì thế CV chọn θ = 0.95, và onset rơi vào chỗ điểm *chạm* 0.95 thay vì
   chỗ điểm bắt đầu tăng. Hậu xử lý không cứu được: cSEBB (Ebbers và cộng sự 2024, §2) trên
   posterior v1 chỉ đạt CV **0.058 ± 0.022**, so với 0.154 ± 0.021 của ADR-0024
   (`sebb_cv_sed_ensemble_C_clean_20260925T045631Z_20260926.md`).
3. **Công thức train tối giản.** 8 epoch, lr 1e-3 cố định cho cả encoder đã pretrain, cửa sổ
   cố định (mỗi epoch thấy đúng các crop cũ), không augmentation.

### 2. Văn liệu

Trích dẫn đầy đủ, mức xác minh và nhật ký tra cứu nằm ở [RELATED_WORK §2.1, §10](../RELATED_WORK.md).
Chỉ bài SEBBs đã được đọc trực tiếp (V3); các số còn lại là V2, lấy qua tóm tắt hoặc
abstract, và phải đối chiếu trước khi trích vào báo cáo.

- **Mốc cho recording thật:** DCASE 2016 Task 3 (ghi âm thật, hai cảnh home/residential area)
  lấy segment ER 1 s làm metric chính. Event-F1 **onset-only, collar 250 ms** của baseline là
  6.3%, của ba hệ thống đứng đầu 4.7–6.3%, trong khi segment-F1 là 34–48% (trang task + trang
  kết quả DCASE 2016, đối chiếu 26/09). Protocol của ta (onset 200 ms **và** offset) còn chặt
  hơn. Event-F1 thấp là đặc thù của dữ liệu thật, nhưng hệ thống của ta còn cách xa cả trần
  phân giải lẫn trần người.
- **DataSED** (Fredianelli và cộng sự, *Scientific Data* 2025): theo tóm tắt, bài không có
  thí nghiệm baseline nào, nên chưa có mốc so sánh trực tiếp.
- **Công thức kiểu DCASE Task 4:** CRNN ít pool thời gian, BiGRU, mixup, FilterAugment.
  Mức pool cụ thể của baseline DCASE là hiểu biết của agent, ⚠️ chưa đối chiếu nguồn.
  FilterAugment (Nam và cộng sự, ICASSP 2022; abstract): PSDS tăng 6.50%, so với 2.13% của
  frequency masking.
- **cSEBB** (Ebbers, Germain, Wichern, Le Roux, Interspeech 2024) tách biên event khỏi độ
  tin cậy. Trên 13 hệ thống DCASE 2023, nó tăng trung bình 4.1 điểm PSDS1 và 3.4 điểm
  collar-F1, đúng metric của ta. Mã tham chiếu license AGPL-3.0; repo tự viết lại theo mô tả
  trong bài (`ml/postprocessing/sebb.py`).
- **Transformer pretrain theo frame trên AudioSet Strong** (Schmid và cộng sự, ICASSP 2025;
  repo `PretrainedSED`, MIT):
  - Độ phân giải 40 ms.
  - Fine-tune trên DESED đạt PSDS1 0.476–0.492.
  - Có bản MobileNet 1.6M/3.8M tham số (`frame_mn06/10`).

## Decision

### 1. SED v2 = CNN14 sửa ba nguyên nhân trên (Track 1)

`scripts.train_sed --recipe v2`. Mọi mặc định vẫn là v1, nên số RQ1 và parity của inference
không đổi (test `tests/test_sed_v2.py`).

| Núm | v1 (RQ1) | v2 | Lý do |
|---|---|---|---|
| Pool thời gian CNN14 | 2,2,2,2,2,2 (/64, 0.64 s) | 2,2,2,1,1,1 (/8, 80 ms) | Nguyên nhân 1. Trọng số conv không đổi, checkpoint AudioSet/DataSEC vẫn nạp được |
| GRU | 1×128, chạy trên frame đã lặp | 2×256, chạy ở nhịp encoder, lặp logit sau | Chuẩn CRNN |
| Epoch / lịch lr | 8, lr 1e-3 cố định | 30, warmup 1 + cosine | Train đủ |
| lr encoder | = lr head | pilot §2 | Encoder đã pretrain |
| Cửa sổ train | cố định | random crop mỗi epoch | Augmentation thời gian |
| Augmentation | không | mixup p 0.5 (α 0.2, nhãn mềm) + FilterAugment p 0.5 (±6 dB) | Văn liệu §2 |
| Trần `pos_weight` | 50 | 10 | Nguyên nhân 2; A4 trên dev: trần 10 tốt nhất (ADR-0028) |
| Chọn checkpoint | frame macro-F1 @0.5 | frame macro-AP dev | Không phụ thuộc ngưỡng |

### 2. Pilot lr encoder (dev, trước mọi run v2 chính thức)

Smoke-test 1 epoch của v2 đạt macro-AP dev 0.096, trong khi v1 sau 1 epoch đạt 0.522. Probe 120
bước (300 cửa sổ dev, `scratchpad/probe_v2.py`) cho thấy không có thành phần nào *hỏng*:
từng thành phần chỉ làm chậm, nhưng cộng dồn lại thì chậm hẳn.

| Biến thể | AP dev sau 120 bước |
|---|---:|
| v1 | 0.473 |
| Chỉ đổi kiến trúc | 0.395 |
| Chỉ đổi cách train | 0.353 |
| Kiến trúc + lr encoder 1e-4 | 0.325 |
| Kiến trúc + augmentation | 0.322 |
| Đủ bộ v2 | 0.158 |

lr encoder cho mọi run v2 được chọn bằng đường cong 3 epoch trên dev. Ứng viên: 1e-4, 3e-4,
1e-3. Luật (ghi trước khi chạy): AP dev cao nhất ở epoch 3. Lr hằng số, 300 cửa sổ dev,
seed 0.

| lr encoder | AP dev epoch 1 | epoch 2 | epoch 3 |
|---|---:|---:|---:|
| 1e-4 | 0.236 | 0.464 | 0.582 |
| **3e-4** | 0.462 | 0.584 | **0.597** |
| 1e-3 | 0.427 | 0.504 | 0.589 |
| v1 (tham chiếu) | 0.525 | 0.590 | 0.628 |

→ **lr encoder 3e-4** cho mọi run v2. v1 vẫn nhỉnh hơn ở epoch 3, nhưng không có
augmentation thì v1 đạt đỉnh ở epoch 3 rồi overfit. Đường cong 8 epoch của run
`054531Z`: AP dev 0.522, 0.583, **0.617**, 0.615, 0.605, 0.607, 0.601, 0.593. Còn v2 được
thiết kế để train 30 epoch. Chênh lệch giữa ba mức lr nhỏ (0.582–0.597), nên đây là lựa chọn
thực dụng, không phải kết luận.

### 3. Hậu xử lý v2 — chọn bằng CV trên dev như ADR-0024 §2

Họ ứng viên:

- **ADR-0024 global:** θ global × `g_max` p ∈ {50, 25}. Per-class bị loại vì A2 cho thấy nó
  overfit dev ở cả ba nhánh.
- **cSEBB:** lưới `scripts.select_sebb_cv` gồm 5 τ × 6 luật gộp × λ.

Luật: chọn cấu hình có CV mean cao nhất (event-F1, 5 fold theo `leakage_group`).

### 4. Ablation bỏ-từng-phần (chỉ dev, seed 20260922)

- v2 đủ.
- v2 với pool /64 (không có độ phân giải).
- v2 với trần `pos_weight` 50.
- v2 không augmentation.

Metric chính là CV event-F1 dev (§3). Metric phụ là macro-AP dev và PSDS-1/2 dev
(`evaluate_run --split dev`, in-sample). Không chạy test cho biến thể ablation. Chênh lệch nhỏ
hơn max(sd giữa fold, 2 × sd giữa seed của v2 đủ) được ghi là không phân biệt được.

### 5. Chọn hệ thống cuối — luật ghi trước

Ứng viên:

- (a) ensemble C v1, CV 0.1538 ± 0.0214 (đã có).
- (b) v2 đủ, run đơn seed 20260922.
- (c) ensemble trung bình xác suất của v2 đủ với 3 seed {20260922, 2, 3} (cùng bộ seed của
  các run B sạch).

Điểm của mỗi ứng viên là CV mean event-F1 dev (§3). Chọn điểm cao nhất; nếu hoà thì chọn ít
model hơn.

Event-F1 ở đây là **micro**, tức `overall` của sed_eval, giống code ADR-0024. Chọn micro để
so ngang với con số 0.1538 đã có. Điều này lệch với Q2 của evaluation_protocol, vốn đòi báo
macro. Vì vậy mọi bảng kết quả v2 báo **thêm macro và per-class**; macro chỉ để báo, không
dùng để chọn (PLAN nợ #20). Lựa chọn được **commit trước** khi mở test. Sau đó (b) và (c) mỗi cái được đánh
giá test đúng một lần, và báo **tất cả**, kể cả khi v2 thua v1. Không chọn lại sau khi xem
test (như ADR-0024 §3).

### 6. Hạ nguồn

Nếu v2 được chọn: caption e2e (W5) và RQ3 (W6) được chạy lại trên event v2, dev trước, test
một lần. Số cũ vẫn giữ và báo song song. Việc phục vụ (ADR-0029) đổi sang v2 qua
`ml/models/sed_factory.py`: kiến trúc đọc từ manifest, v1 khi manifest thiếu khoá.

### 7. Không đổi và tuỳ chọn

- **RQ1 giữ nguyên** (ADR-0021): mọi số RQ1 là kiến trúc v1.
- **Tuỳ chọn, chờ duyệt: RQ1-v2.** Chạy v2 đủ với khởi tạo DataSEC (nhánh C) × 3 seed, so với
  B theo đúng giao thức ADR-0021 (Welch, bootstrap ghép cặp), để trả lời câu hỏi "RQ1 âm tính
  có phải do kiến trúc thô không".
- **Track 2, chờ duyệt:** `PretrainedSED` (`frame_mn10`, sau đó ATST-F/BEATs strong). Nó thêm
  một họ model và checkpoint ngoài (MIT), cần 16 kHz waveform và cần ADR riêng. Cùng luật chọn
  §5.

## Consequences

- Sửa đúng nguyên nhân đo được thay vì dò siêu tham số.
- Ablation bỏ-từng-phần trả lời thành phần nào đóng góp, và chỉ dùng dev.
- Tốn GPU: khoảng 90 phút/run 30 epoch trên RTX 3070 Laptop. 4 ablation + 2 seed khoảng 9 giờ;
  RQ1-v2 thêm khoảng 4.5 giờ.
- Nếu v2 được chọn, W5/W6 phải tính lại, và sổ test (`report_test_ledger`) sẽ ghi thêm các
  dòng v2.

## Alternatives considered

| Phương án | Vì sao không chọn (bây giờ) |
|---|---|
| Chỉ đổi hậu xử lý (cSEBB, hysteresis) | Đã đo: posterior v1 bão hoà, cSEBB CV 0.058 < 0.154 |
| Đổi metric chính sang segment-based | Là đổi thước đo sau khi thấy số; segment F1 chỉ báo làm bối cảnh |
| Per-class θ / luật gộp theo lớp | A2: 21 tham số overfit dev 142 recording |
| Nhảy thẳng sang transformer (Track 2) | Đổi họ model, checkpoint ngoài, pipeline 16 kHz; làm sau khi v2 cho biết phần còn lại |
| Tổng hợp soundscape từ DataSEC (kiểu DESED/Scaper) | Hướng mạnh nhưng là một đóng góp khác; ghi CLAUDE §8 |

## Nguồn

- Trích dẫn đầy đủ, mức xác minh, nhật ký tra cứu: [RELATED_WORK §2.1, §10](../RELATED_WORK.md).
- Phát hiện, kỹ thuật, ý tưởng cho paper: [PAPER_NOTES.md](../PAPER_NOTES.md).

## Evidence cần kiểm lại

- `sed_ceilings_20260926.md`: trần 0.63 là **cận trên** (làm tròn biên về khối gần nhất).
- Trần người 0.58 chỉ từ 8 cặp.
- Số văn liệu §2 trích từ nguồn: bài Ebbers và cộng sự (PDF Interspeech), arXiv 2409.09546,
  trang kết quả DCASE 2016 T3, bài FilterAugment (arXiv 2110.03282), README `PretrainedSED`.
