# PAPER_NOTES.md — Sổ tay dẫn chứng và ý tưởng cho paper

> **Vì sao có file này.** Người dùng (26/09/2026): đề tài tập trung vào **model, nghiên cứu và
> tối ưu**, có thể viết paper sau. Vì vậy **mọi phát hiện, kỹ thuật, nguồn và kết quả (kể cả
> âm tính)** phải được lưu ở dạng dùng lại được làm dẫn chứng và làm ý tưởng viết bài.
>
> **Quy tắc ghi:**
> - Mỗi dòng có đủ bốn phần: claim → số → nguồn (measurement / ADR / commit) → trạng thái.
> - Số chép **y nguyên** từ file measurement do script sinh (CLAUDE §5). Không làm tròn khác
>   nguồn.
> - Kết quả âm tính và kỹ thuật thất bại ghi **ngang hàng** kết quả dương tính: chúng là dẫn
>   chứng cho lựa chọn thiết kế.
> - Văn liệu chỉ ghi tên ngắn ở đây. Trích dẫn đầy đủ và **mức xác minh** (V0–V4) ở
>   [RELATED_WORK.md](RELATED_WORK.md). Chỉ nguồn V3/V4 được trích trong bài.
> - Cập nhật ở cuối mỗi block công việc (CLAUDE §9), cùng lúc với STATUS.

---

## 1. Hướng paper khả dĩ

| # | Hướng | Đóng góp chính | Dẫn chứng đã có | Còn thiếu |
|---|---|---|---|---|
| **A** | Chẩn đoán + cải thiện SED trên ghi âm môi trường thật (DataSED). Tiêu đề nháp: *"Where does event-level SED fail on real-world environmental recordings? Resolution ceilings, annotator agreement and posterior saturation"* | Phân rã event-F1 thành trần độ phân giải / trần người / lỗi biên / bỏ sót; sửa từng nguyên nhân (SED v2) với ablation bỏ-từng-phần; baseline đầu tiên *đã báo cáo* trên DataSED (⚠️ phải xác minh chưa ai báo) | §2.2, §3 | Kết quả v2 (đang chạy), đo bão hoà posterior có artifact (§6 #1), systematic search baseline DataSED |
| **B** | Transfer isolated → continuous **có kiểm soát leakage xuyên dataset** (C3, RQ1) | Đo được trùng nguồn DataSEC–DataSED; RQ1 âm tính có thống kê nhiều seed; ý tưởng thay pretraining bằng soundscape tổng hợp (§5) | §2.1 | RQ1-v2 (ADR-0030 §7), thí nghiệm soundscape tổng hợp |
| **C** | Caption có căn cứ kiểm được bằng máy + RAG trên timeline (C1, C2, C4) | Đánh đổi ràng buộc ↔ độ phủ và cách giải; metric hallucination không cần caption người viết; truy vấn có vị từ thời gian | §2.3, §2.4 | Chạy lại trên SED v2 (ADR-0030 §6); systematic search AAC hallucination (RELATED_WORK §4) |

Hướng A gần nhất với trọng tâm "model, nghiên cứu, tối ưu". Hướng B và C dùng lại cùng hạ tầng.

---

## 2. Phát hiện đã chốt (có artifact)

### 2.1 Dữ liệu, leakage, nhãn

| # | Phát hiện | Số | Nguồn | Dùng cho |
|---:|---|---|---|---|
| D1 | DataSEC và DataSED **có chung bản ghi nguồn** | 3 cặp trùng; `Sirens-0046`↔`S-0233` sim 1.000000 trên 35 s, `Sirens-0067`↔`S-0211` 1.000000 trên 13 s, `Train-0012`↔`S-0213` 0.9548 trên 31 s | [dedup_20260923.md](measurements/dedup_20260923.md), ADR-0009 | Hướng B: động cơ của kiểm soát leakage |
| D2 | Rò rỉ sau duyệt tay | 11 clip / 5,048 = **0.2179%** → dải `minor` | CLAUDE §3, ADR-0010, `review_worksheet_20260923.md` | Hướng B: phần phương pháp |
| D3 | Cổng leakage **không pass rỗng** | Bỏ loại trừ → kiểm 5 FAIL, gọi đúng `Sirens-0046.wav` | ADR-0013, CLAUDE §3 | Hướng B: cổng kiểm được chứng minh có hiệu lực |
| D4 | Hai lỗi lệch namespace từng làm cổng **pass rỗng** (giao rỗng luôn "sạch") | `create_splits` bỏ qua ràng buộc; "0 clip rò rỉ" trong khi có sim 1.0 | CLAUDE §10 (23/09) | Bài học phương pháp: cổng dữ liệu phải chứng minh chạm dữ liệu |
| D5 | Fingerprint theo đặc tả gốc không phân biệt được gì; sửa bằng bỏ C0 + chuẩn hoá corpus | Trước: 52.6% cặp ngẫu nhiên vượt ngưỡng; sau: positive min 1.0000, negative max 0.9205 | ADR-0007 | Hướng B: phụ lục phương pháp dedup |
| D6 | **Đồng thuận người gán nhãn** đo miễn phí từ 8 cặp recording giống từng byte | 67/94 biên trong 0.2 s; 2/8 cặp bất đồng lớp; lệch lớn nhất 12.72 s; **event-F1 người vs người 0.5785** (collar 0.2 s), 0.7603 (collar 1 s) | [annotation_consistency_20260923.md](measurements/annotation_consistency_20260923.md), [sed_ceilings_20260926.md](measurements/sed_ceilings_20260926.md) | Hướng A: trần thực tế; Hạn chế: cỡ mẫu 8 cặp |

### 2.2 SED

| # | Phát hiện | Số | Nguồn | Dùng cho |
|---:|---|---|---|---|
| S1 | **RQ1 âm tính** (pretraining thêm DataSEC không giúp so với chỉ AudioSet) | 7 run sạch: B 0.0610 ± 0.0048, C 0.0539 ± 0.0088 event-F1, Welch p = 0.234; bootstrap ghép cặp C − B −0.0071 [−0.0164, +0.0021] | [rq1_multiseed_clean_20260924.md](measurements/rq1_multiseed_clean_20260924.md), [rq1_multirun_bootstrap_clean_20260925.md](measurements/rq1_multirun_bootstrap_clean_20260925.md), ADR-0021 | Hướng B |
| S2 | Pretraining nói chung giúp rõ (B/C vs A) | Run chính thức: A 0.0360, B 0.0621, C 0.0472 event-F1; PSDS-2 0.4514 / 0.6456 / 0.6462 | [rq1_delta_official_20260924.md](measurements/rq1_delta_official_20260924.md) | Hướng A/B |
| S3 | Train SED **không tất định** cùng seed (classifier thì tất định bit-for-bit) | frame macro-F1 B 0.5850 → 0.5705 cùng code, cùng seed | PLAN nợ #5 | Hạn chế; lý do bắt buộc nhiều seed |
| S4 | Per-class θ **overfit dev** có hệ thống | Dev → test per-class −48% / −39% / −41% (A/B/C), global −15% / −4% / −2% | `*_threshold_ablation_A2.md` | Hướng A: vì sao chọn θ global |
| S5 | Median filter không có hiệu ứng rõ | Δ +0.0063 / +0.0026 / −0.0014 | `*_median_filter_ablation_A3.md` | Ablation |
| S6 | Percentile `g_max` 25 tốt hơn 50 (chọn lại trên dev bằng CV) | 5/5 ứng viên chọn global 0.95 + p25 | [sed_optimization_20260925.md](measurements/sed_optimization_20260925.md), ADR-0024 | Hướng A |
| S7 | Ensemble + hậu xử lý chọn trên dev | Ensemble C: test event-F1 **0.0941** [0.0624, 0.1277], PSDS-1 0.3489, PSDS-2 0.6987 | như trên | Hệ thống v1 tốt nhất (mốc so sánh cho v2) |
| S8 | Nới collar làm event-F1 tăng ~3× | B: 0.062 (0.2 s) → 0.185 (1 s) → 0.222 (2 s) | [collar_sensitivity_20260924.md](measurements/collar_sensitivity_20260924.md) | Hướng A: động cơ chẩn đoán biên |
| S9 | Trần `pos_weight` 10 tốt nhất trên dev (n = 1/trần) | dev 0.1233 (10) vs 0.0814 (50); test 0.0725 vs 0.0621 | [ablation_a4_pos_weight_20260926.md](measurements/ablation_a4_pos_weight_20260926.md), ADR-0028 | Hướng A: nối với S12 (bão hoà) |
| S10 | Cặp lớp nhầm: chỉ 4/15 giả thuyết âm học xác nhận mạnh; nhiều cặp nhầm là **đồng xuất hiện trong cảnh** | 1,482 lượt substitution trên dev, 7 run | [confusable_pairs_clean_dev_20260925.md](measurements/confusable_pairs_clean_dev_20260925.md), taxonomy.md §8.1 | Hướng A: phân tích lỗi |
| S11 | **Trần độ phân giải**: model *hoàn hảo* nhưng ra quyết định theo khối | 0.64 s → **0.6294**; 1.28 s → 0.3032; ≤ 0.32 s → 1.0000 (dev, cận trên) | [sed_ceilings_20260926.md](measurements/sed_ceilings_20260926.md) | Hướng A: hình 1 (§4) |
| S12 | **Phân rã lỗi** hệ thống v1 trên dev (in-sample) | 886 event: 112 khớp collar, **417 chồng đúng lớp nhưng lệch biên**, 357 bỏ sót; event-F1 0.1588, chỉ onset **0.2325**, chỉ offset 0.4975, segment F1 (1 s) **0.6542** | như trên | Hướng A: "nhận ra được nhưng đặt biên sai" |
| S13 | Nguyên nhân kiến trúc: CNN14 trong repo pool thời gian cả 6 khối (/64); CNN14 gốc khối 6 pool (1,1) → /32, và có dropout 0.2 sau mỗi khối mà bản trong repo không có | 1000 frame (10 s @ 100 fps) → 15 khối ≈ 0.667 s | `ml/models/panns.py`, code gốc `audioset_tagging_cnn/pytorch/models.py` (đối chiếu 26/09) | Hướng A: vì sao trần 0.63 |
| S14 | **cSEBB thất bại trên posterior v1** (kết quả âm tính) | CV tốt nhất 0.0582 ± 0.0220 (τ 1.28 s, rel 2) so với 0.1538 ± 0.0214 của ADR-0024 | [sebb_cv_sed_ensemble_C_clean_20260925T045631Z_20260926.md](measurements/sebb_cv_sed_ensemble_C_clean_20260925T045631Z_20260926.md) | Hướng A: hậu xử lý không cứu được posterior bão hoà |
| S15 | Giao thức "chọn trên dev, commit, rồi mới sinh logit test": đường dump tái tạo **trùng từng bit** logit lúc train | SHA-256 dev trùng khít trên run `054531Z` | commit `8b1df60`, `scripts/dump_predictions.py` | Phương pháp: chứng minh test không bị dùng để chọn |
| S16 | Parity phục vụ | Đặc trưng 142/142 trùng; logit trùng bit khi cùng batch; 332/408 event trùng khít, 405/408 trong collar khi phục vụ từng file (nhiễu fp16 theo thành phần batch) | [inference_parity_20260925.md](measurements/inference_parity_20260925.md), ADR-0029 §7 | Phụ lục kỹ thuật |

### 2.3 Caption (RQ2 — C1, C2)

| # | Phát hiện | Số | Nguồn |
|---:|---|---|---|
| C1 | Chỉ nhận timeline, LLM gần như không bịa nguồn âm; lỗi thật của sinh tự do là suy diễn bối cảnh, gọi tên quá cụ thể, từ cấm G3 | test, run B | ADR-0022 §5, [caption_grounding_sed_polyphonic_20260924T054531Z_test.md](measurements/caption_grounding_sed_polyphonic_20260924T054531Z_test.md) |
| C2 | Ràng buộc đổi lấy bỏ sót | omission constrained − unconstrained **+0.224** [+0.178, +0.274] | như trên |
| C3 | Nhánh "buộc phủ đủ lớp" giải đánh đổi | omission 0, không thua unconstrained ở metric nào | ADR-0026 |
| C4 | SED tốt hơn → caption e2e tốt hơn | omission constrained 0.284 → 0.036 trên SED tối ưu | [caption_grounding_sed_ensemble_C_clean_20260925T045631Z_test.md](measurements/caption_grounding_sed_ensemble_C_clean_20260925T045631Z_test.md) |
| C5 | Lexicon so với người đọc mù 60 caption | precision 0.896, recall 0.936 | [caption_mention_agreement_20260925.md](measurements/caption_mention_agreement_20260925.md), ADR-0022 §6 |

### 2.4 Retrieval (RQ3 — C4)

| # | Phát hiện | Số | Nguồn |
|---:|---|---|---|
| R1 | Lọc cứng theo vị từ là thành phần quyết định | nDCG@10 test EN: structured 0.523, hybrid 0.481 [0.424, 0.539], vector 0.418 | [retrieval_benchmark_test_20260925.md](measurements/retrieval_benchmark_test_20260925.md) |
| R2 | Vector trong tập đã lọc không giúp với document template | hybrid − structured −0.042 [−0.085, −0.004] | như trên |
| R3 | Câu trả lời ràng buộc evidence | unsupported-claim 0.000 | [retrieval_answers_test_20260925.md](measurements/retrieval_answers_test_20260925.md) |

---

## 3. Kỹ thuật đã thử — nhật ký (kể cả thất bại)

| Kỹ thuật | Nguồn ý tưởng | Code | Kết quả | Trạng thái |
|---|---|---|---|---|
| Ensemble trung bình xác suất nhiều run | thực hành chuẩn | `scripts/build_ensemble.py` | +0.03…+0.04 event-F1 test cùng với hậu xử lý CV (S7) | ✅ dùng |
| θ global vs per-class | ADR-0003, A2 | `ml/postprocessing/calibration.py` | per-class overfit dev (S4) | ✅ global |
| Duration prior từ train (median, `d_min`, `g_max`) | ADR-0003 | `ml/postprocessing/events.py` | `g_max` p25 tốt hơn (S6) | ✅ dùng |
| Trần `pos_weight` | A4 | `scripts/train_sed.py --pos-weight-cap` | 10 tốt nhất trên dev (S9) | → vào v2 |
| cSEBB (phát hiện điểm đổi) | Ebbers và cộng sự, Interspeech 2024 | `ml/postprocessing/sebb.py`, `scripts/select_sebb_cv.py` | **thất bại** trên posterior v1 (S14) | vào lưới chọn của v2 |
| Hysteresis (hai ngưỡng) | thực hành SED cổ điển | `ml/postprocessing/sebb.py::hysteresis_runs` | chưa đánh giá | ○ |
| CNN14 giữ độ phân giải (pool thời gian /8) | chẩn đoán S11/S13; CRNN DCASE pool thời gian ít | `PannsCNN14Encoder(time_pooling=…)` | đang chạy | ◐ v2 |
| BiGRU 2 lớp chạy ở nhịp encoder | CRNN chuẩn | `SoundEventDetector(upsample="after_rnn")` | đang chạy | ◐ v2 |
| Warmup + cosine, lr encoder riêng | fine-tune pretrained | `ml/training/sed.py::build_optimizer/build_scheduler` | pilot: lr encoder 3e-4 (ADR-0030 §2) | ◐ v2 |
| Random crop mỗi epoch | augmentation thời gian | `SedFeatureDataset(random_crop=True)` | đang chạy | ◐ v2 |
| Mixup (nhãn mềm) | Zhang và cộng sự, ICLR 2018; PANNs | `ml/training/augment.py` | đang chạy | ◐ v2 |
| FilterAugment (cộng dB theo dải) | Nam và cộng sự, ICASSP 2022 | `ml/training/augment.py` | đang chạy | ◐ v2 |
| Chọn checkpoint theo macro-AP dev | không phụ thuộc ngưỡng | `SedTrainingConfig(select_metric=…)` | đang chạy | ◐ v2 |

**Bài học từ pilot (ADR-0030 §2):** mỗi thành phần v2 riêng lẻ chỉ làm chậm hội tụ ban đầu
(AP dev sau 120 bước 0.32–0.40 so với v1 0.47), nhưng cộng dồn thì chậm hẳn (0.158). Không có
thành phần nào *hỏng*. Không có augmentation, v1 overfit từ epoch 3 (AP dev 0.617 → 0.593 ở
epoch 8). → Ý cho paper: công thức train quan trọng ngang kiến trúc.

---

## 4. Chẩn đoán có thể thành đóng góp phương pháp

1. **Trần độ phân giải ("oracle-at-resolution").** Với bất kỳ encoder nào có hệ số pool thời
   gian r, tính event-F1 của một model hoàn hảo ra quyết định theo khối r frame, **chỉ từ
   ground truth**. Rẻ, không cần train, và cho biết kiến trúc có thể đạt tối đa bao nhiêu
   trước khi train. → `scripts/report_sed_ceilings.py`.
   ⚠️ CẦN XÁC MINH: đã có công trình nào phân tích trần event-F1 theo độ phân giải chưa
   (RELATED_WORK §2).
2. **Đồng thuận người gán nhãn từ bản trùng.** Dataset thật hay chứa recording trùng được
   chú giải hai lần. Đây là một phép đo inter-annotator agreement miễn phí, cho trần thực tế
   của metric (D6).
3. **Tách onset / offset / segment.** Ba con số (0.23 / 0.50 / 0.65) định vị lỗi nằm ở biên
   onset, không phải ở nhận dạng (S12).
4. **Phân rã lỗi ba nhóm:** khớp / chồng đúng lớp nhưng lệch biên / bỏ sót (S12). Khác
   taxonomy lỗi của `errors.py` ở chỗ tách riêng nhóm "phát hiện được nhưng biên sai".
5. **Chẩn đoán bão hoà posterior (giả thuyết, cần artifact):** `pos_weight` lớn → xác suất cao
   cả ngoài event → CV đẩy θ lên 0.95 → onset trễ; và hậu xử lý phát hiện điểm đổi (cSEBB)
   mất tác dụng (S14). v2 kiểm giả thuyết này bằng ablation trần 50 so với 10 (ADR-0030 §4).

---

## 5. Ý tưởng chưa làm (future work / thí nghiệm tiếp)

| Ý tưởng | Vì sao đáng làm | Rủi ro / ràng buộc | Liên quan |
|---|---|---|---|
| **Transformer pretrain theo frame** (PretrainedSED: `frame_mn10`, ATST-F/BEATs strong) | 40 ms; DESED PSDS1 0.476–0.492 sau fine-tune (theo bài gốc) | Họ model mới, checkpoint ngoài (MIT), cần 16 kHz / 128 mel; ADR riêng | ADR-0030 §7 (Track 2, chờ duyệt) |
| **Soundscape tổng hợp từ clip DataSEC** (kiểu DESED/Scaper) | Cơ chế transfer isolated → continuous **khác** pretraining; tạo nhãn mạnh cho lớp hiếm | Chỉ dùng DataSEC **train** và bỏ 130 clip đã loại (leakage); nhãn mạnh nhiễu do khoảng lặng trong clip | RQ1 hướng mới, CLAUDE §8 |
| Train chung nhãn mạnh (DataSED) + nhãn yếu (DataSEC) | Chuẩn DCASE Task 4 | Ánh xạ 22 → 21 lớp (bỏ `wind_turbine`) | RQ1 hướng mới |
| RQ1-v2: B vs C dưới recipe v2 | RQ1 âm tính có phải do kiến trúc thô? | +3 run (~4.5 h) | ADR-0030 §7 |
| Loss hiệu chuẩn tốt hơn (focal / asymmetric) thay `pos_weight` | Trực tiếp nhắm bão hoà posterior | Thêm một núm; chọn trên dev | §4 mục 5 |
| Frequency dynamic convolution | SOTA DESED dòng CNN | Đổi kiến trúc conv, không dùng lại trọng số CNN14 | RELATED_WORK §2 |
| Hậu xử lý theo lớp khi có thêm dữ liệu | cSEBB gốc tune theo lớp | A2: overfit dev nhỏ | S4 |
| Báo segment-based metric song song | So được với DCASE 2016/2017 T3 | Không thay primary (không đổi thước đo sau khi thấy số) | evaluation_protocol §3.1 |

---

## 6. Việc phải làm để thành dẫn chứng hợp lệ

| # | Việc | Vì sao |
|---:|---|---|
| 1 | Đo bão hoà posterior có artifact (phân bố xác suất trên frame âm/dương theo lớp, v1 vs v2) | §4 mục 5 hiện chỉ là quan sát trên một trace |
| 2 | **Event-F1 macro** bên cạnh micro cho mọi hệ thống | evaluation_protocol Q2 đòi macro; mọi số event-F1 headline đến nay là **micro** (`overall` của sed_eval) — lệch protocol, xem PLAN nợ #20 |
| 3 | Đối chiếu trực tiếp các số văn liệu lấy qua tóm tắt WebFetch (V2 → V3) | Bài học ADR-0015: tóm tắt từng báo sai license |
| 4 | Systematic search: đã có baseline nào trên DataSED chưa | Để được viết "baseline đầu tiên" |
| 5 | Kết quả v2 (dev → chọn → test một lần) | ADR-0030 §4–§5 |

---

## 7. Bảng / hình dự kiến cho paper

| Hình / bảng | Nội dung | Nguồn số |
|---|---|---|
| Hình 1 | Event-F1 theo độ dài khối quyết định (trần độ phân giải), vạch ngang trần người 0.58, điểm hệ thống v1/v2 | `sed_ceilings_*.json` |
| Hình 2 | Phân rã lỗi (khớp / lệch biên / bỏ sót) v1 so với v2 | `report_sed_ceilings --run` cho từng hệ thống |
| Hình 3 | Trace posterior một recording (bão hoà v1 so với v2) | cần artifact (§6 #1) |
| Hình 4 | Đường cong học v1 (overfit epoch 3) so với v2 | `logs/history.json` |
| Bảng 1 | Ablation bỏ-từng-phần v2 (CV event-F1 dev, macro-AP, PSDS dev) | ADR-0030 §4 |
| Bảng 2 | Kết quả test một lần + CI 95%, v1 và v2 | `evaluation*.json` |
| Bảng 3 | RQ1 nhiều seed | `rq1_multiseed_clean_20260924.md` |
| Bảng bối cảnh | DCASE 2016 T3 (ghi âm thật): event-F1 onset-only collar 250 ms 4.7–6.3%, segment F1 34–48% — **khác dataset, chỉ để định cỡ** | RELATED_WORK §2.1 |

---

## 8. Mối đe doạ tính hợp lệ (viết thẳng vào paper)

1. Một split đóng băng; dev 137, test 142 recording → CI rộng (ví dụ event-F1 v1 [0.062, 0.128]).
2. Train SED không tất định → cần ≥ 3 seed cho mọi so sánh; ablation v2 chỉ 1 seed.
3. Trần người chỉ từ 8 cặp.
4. Chưa có baseline công bố trên DataSED (bài dataset không có thí nghiệm — theo tóm tắt, cần
   đối chiếu trực tiếp).
5. Collar 0.2 s chặt hơn độ chính xác của nhãn (D6).
6. Metric headline là micro, trong khi Q2 đòi macro (§6 #2).
7. License checkpoint AudioSet không ghi (ADR-0015); dữ liệu CC-BY-NC-SA → model công bố phải
   cùng license.
8. Nhiều số văn liệu hiện ở mức V2 (lấy qua tóm tắt) — chưa được trích.

---

## 9. Nhật ký giai đoạn cải thiện SED (ADR-0030)

| Ngày | Việc | Commit / artifact |
|---|---|---|
| 26/09 | Chẩn đoán trần + phân rã lỗi | `dd5d3b9`, `sed_ceilings_20260926.md` |
| 26/09 | cSEBB + CV (âm tính trên v1) | `9dc78dc`, `sebb_cv_…_20260926.md` |
| 26/09 | Code SED v2, `dump_predictions` (trùng bit), `evaluate_run --split dev` | `8b1df60` |
| 26/09 | ADR-0030 (Proposed) + pilot lr encoder 3e-4 | `ead5a2f` |
| 26/09 | Hàng đợi 6 run v2 (3 seed + 3 ablation), bắt đầu 10:33 trên tree sạch `e808df4` | `ml/runs/sed_polyphonic_20260926T033312Z`, … (điền khi xong) |
