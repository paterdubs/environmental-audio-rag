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
| **A** | Chẩn đoán + cải thiện SED trên ghi âm môi trường thật (DataSED). Tiêu đề nháp: *"Where does event-level SED fail on real-world environmental recordings? Resolution ceilings, annotator agreement and boundary dispersion"* | Phân rã event-F1 thành trần độ phân giải / trần người / lỗi biên / bỏ sót; sửa từng nguyên nhân (SED v2) với ablation bỏ-từng-phần; baseline đầu tiên *đã báo cáo* trên DataSED (⚠️ phải xác minh chưa ai báo) | §2.2, §3 | Kết quả v2 (đang chạy), systematic search baseline DataSED |
| **B** | Transfer isolated → continuous **có kiểm soát leakage xuyên dataset** (C3, RQ1) | Đo được trùng nguồn DataSEC–DataSED; RQ1 âm tính có thống kê nhiều seed; ý tưởng thay pretraining bằng soundscape tổng hợp (§5) | §2.1 | RQ1-v2 (S9, ADR-0031 §2), thí nghiệm soundscape tổng hợp |
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
| S17 | **Không bão hoà; biên tản rộng và đối xứng** (bác bỏ giả thuyết ban đầu của ADR-0030) | v1 ensemble C, dev: frame âm trung vị p 0.008, ≥ 0.5 chỉ 2.3%; onset trung vị +0.00 s, [q25, q75] [−0.39, +0.51], trong ±0.2 s 30.2%, trễ 36.5%, sớm 33.3%. v2 seed 20260922 (sơ bộ): trong ±0.2 s 35.2% | [boundary_errors_20260926.md](measurements/boundary_errors_20260926.md) | Hướng A: lời giải thích đúng cho lỗi biên; ví dụ "trace đơn lẻ đánh lừa" |
| S18 | **SED v2 được chọn trên dev và tăng event-F1 trên test** (luật ghi trước, lựa chọn commit trước khi mở test) | CV dev (micro): 3 seed 0.1900 / 0.2096 / 0.2169; ensemble 3 seed **0.2129 ± 0.0622** được chọn, nhưng hơn run đơn chỉ 0.023 (≤ sd fold) nên "không được gọi là tốt hơn" run đơn. **Test một lần:** ensemble v2 micro **0.1476** [0.1088, 0.1866], macro **0.1369**; run đơn 0.1255 / 0.1198; v1 ensemble C 0.0941 / 0.0917. Bootstrap ghép cặp theo recording: v2 − v1 **+0.0536 [+0.0261, +0.0853]** | [sed_v2_selection_20260926.md](measurements/sed_v2_selection_20260926.md), [sed_ensemble_v2_20260926T155630Z_eval_cv.md](measurements/sed_ensemble_v2_20260926T155630Z_eval_cv.md), [rq1_multirun_bootstrap_sedv2_vs_v1_20260926.md](measurements/rq1_multirun_bootstrap_sedv2_vs_v1_20260926.md) | Hướng A: kết quả chính |
| S19 | **Độ phân giải thời gian là thành phần quyết định; AP frame không nhìn thấy điều này** | Bỏ nó (pool /64): CV dev 0.1900 → 0.1060 (−0.0840, gấp 1.6 lần ngưỡng nhiễu 0.0523), trong khi AP frame dev 0.667 so với 0.688 | [sed_v2_ablation_20260926.md](measurements/sed_v2_ablation_20260926.md) | Hướng A: bảng ablation; lý do phải báo metric mức event |
| S20 | Trần `pos_weight` 50 so với 10, và augmentation (mixup + FilterAugment): **không phân biệt được** (1 seed mỗi biến thể; luật S12 không đòi thêm seed) | Δ −0.0126 và +0.0068. Không augmentation thì AP frame thấp hơn (0.644 so với 0.688), nhưng event-F1 không giảm | như trên | Kết quả âm tính: augmentation giúp AP frame, không giúp event-F1 |
| S21 | **PSDS không tăng dù event-F1 tăng** | Test: PSDS-1 0.3447 so với 0.3489 (v1), PSDS-2 0.6744 so với 0.6987 | các file `*_eval_cv.md` ở trên | Hướng A: lợi ích nằm ở điểm vận hành đã chọn; chưa giải thích (§6) |
| S22 | **Lợi ích chủ yếu ở lớp phổ biến**, lớp hiếm vẫn bị bỏ sót | Dev in-sample: micro 0.1588 → 0.2120 (+0.053), macro 0.1308 → 0.1494 (+0.019). Frame dương có p < 0.5 của `horn` / `crows…` / `thunder…` ở v2 seed 1 là 75 / 73 / 58%. Deletion test 274 so với 27 insertion | `*_deveval_cv.md`, [boundary_errors_20260926.json](measurements/boundary_errors_20260926.json) | Hướng A; động cơ S11 (loss cho lớp hiếm) |
| S23 | Biên v2 tốt lên nhưng vẫn tản rộng | Onset trong ±0.2 s 35.8% (v1 30.2%), IQR [−0.54, +0.30] s. Chỉ onset 0.2708 (v1 0.2325), chỉ offset 0.4914 (v1 0.4975), segment F1 0.6869 (v1 0.6542) | [boundary_errors_20260926.md](measurements/boundary_errors_20260926.md), [sed_ceilings_v2_20260926.md](measurements/sed_ceilings_v2_20260926.md) | Hướng A: phần lỗi còn lại |
| S24 | Dev → test giảm ở cả v1 và v2 | v2 0.2129 (CV dev) → 0.1476 (test, −31%); v1 0.1538 → 0.0941 (−39%) | như trên | Mối đe doạ: θ global chọn trên dev 137 recording |
| S25 | cSEBB thua θ global trên **mọi** run v2 (lặp lại S14) | 6 run: cSEBB 0.0202–0.1379 so với θ global 0.1060–0.2169; ensemble 0.1275 so với 0.2129 | `ml/runs/*/sebb_cv_selection.json`, `summary_all.log` | Kết quả âm tính lặp lại |
| S26 | **RQ1-v2 — chỉ CV dev, sơ bộ** (S9, ADR-0031 §2). C-v2 (khởi tạo DataSEC) không tách biệt rõ khỏi B-v2 (khởi tạo AudioSet) dưới recipe v2, giống mẫu hình RQ1 gốc (ADR-0021) | CV dev θ global p25 mỗi seed: B-v2 0.1900 / 0.2096 / 0.2169 (mean 0.2055, sd 0.0139); C-v2 0.1913 / 0.2166 / 0.2170 (mean 0.2083, sd 0.0147). Chênh mean 3-seed +0.0028 — trong khoảng sd giữa seed của cả hai nhánh | `ml/runs/sed_polyphonic_20260926T{161726,172229,185208}Z/postproc_cv_selection.json` | **Chưa phải kết luận RQ1-v2**: đây là CV dev, không phải Welch/bootstrap trên test theo luật ghi trước (ADR-0031 §2). Test 6 run này chỉ mở sau vòng chọn cuối S13 (18/10) |
| S27 | Ensemble (d) C-v2 3-seed có CV dev **cao nhất trong mọi ứng viên non-Track2** tính tới nay — cao hơn cả (c), hệ thống đã chọn và test đêm 26/09 | (d) 0.2230 ± 0.0492 so với (c) đã chọn 0.2129 ± 0.0622 (test 0.1476) và (b) B-v2 đơn tốt nhất 0.2169. (e) 6-model (B-v2+C-v2 trộn) 0.2050 ± 0.0561 — **không** hơn (d) hay (c), trộn hai cách khởi tạo không giúp trên CV dev | `ml/runs/sed_ensemble_cv2_20260926T205405Z`, `sed_ensemble_bcv2_20260926T205412Z` | Ứng viên (d)/(e) đã ghi trước ở ADR-0031 §4; **không** đổi hệ thống đang phục vụ, không mở test cho (d)/(e) trước S13 |
| S28 | **Track 2a (T2a): BEATs strong đóng băng + head v2 gần bằng CNN14 fine-tune toàn bộ (v2), chỉ CV dev, chưa test** | CV dev global mỗi seed: 0.2015 / 0.1922 / 0.1953 (T2a). Ensemble (f1) T2a×3 **0.2114 ± 0.0491** — trong khoảng nhiễu của (c) v2 đã chọn/test (0.2129 ± 0.0622), thấp hơn (d) C-v2×3 (0.2230 ± 0.0492). (f3) T2a+B-v2 6-model **0.1813 ± 0.0496** — thấp hơn (f1), lặp lại mẫu hình (e): trộn hai họ không giúp. Encoder BEATs bị đóng băng hoàn toàn (chỉ train BiGRU+linear ~3.3M tham số trên 90.4M tham số encoder) | `ml/runs/sed_polyphonic_20260927T{064341,092605,113910}Z`, `sed_ensemble_t2a_20260927T141952Z`, `sed_ensemble_t2a_bv2_20260927T142003Z`, ADR-0032 §9 | Ủng hộ phát hiện gốc của PretrainedSED (frozen gần fine-tune) trên DataSED — khác domain (DESED) và khác kiến trúc so với v2 (CNN14+GRU). Ứng viên (f1)/(f3) ghi trước ở ADR-0032 §5, vào vòng chọn cuối S13 cùng (a)-(e) |
| S29 | cSEBB thua θ global **lần thứ ba**, trên một họ encoder hoàn toàn khác (transformer đóng băng, không phải CNN) | T2a: cSEBB tốt nhất mỗi seed 0.1502 / 0.1212 / 0.1295 so với θ global 0.2015 / 0.1922 / 0.1953; (f1) cSEBB 0.1333 so với global 0.2114 | `ml/runs/sed_polyphonic_20260927T*/sebb_cv_selection.json` | Kết quả âm tính tổng quát hoá qua 3 kiến trúc (v1 CNN, v2 CNN+GRU cải tiến, T2a transformer đóng băng) — đáng viết thành một câu khẳng định chắc trong paper, không chỉ là chi tiết vụn |

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
| cSEBB (phát hiện điểm đổi) | Ebbers và cộng sự, Interspeech 2024 | `ml/postprocessing/sebb.py`, `scripts/select_sebb_cv.py` | **thất bại** trên v1 (S14) và trên v2 seed 20260922: CV tốt nhất 0.0953 ± 0.0302 (τ 0.48, abs 0.15) so với θ global p25 0.1900 ± 0.0523 (`ml/runs/sed_polyphonic_20260926T033312Z/{sebb,postproc}_cv_selection.json`, sơ bộ 1/3 seed) | vẫn trong lưới chọn của v2 |
| Hysteresis (hai ngưỡng) | thực hành SED cổ điển | `ml/postprocessing/sebb.py::hysteresis_runs` | chưa đánh giá | ○ |
| CNN14 giữ độ phân giải (pool thời gian /8) | chẩn đoán S11/S13; CRNN DCASE pool thời gian ít | `PannsCNN14Encoder(time_pooling=…)` | **quyết định**: bỏ đi thì CV dev −0.084 (S19) | ✅ v2 |
| BiGRU 2 lớp chạy ở nhịp encoder | CRNN chuẩn | `SoundEventDetector(upsample="after_rnn")` | không ablate riêng (thuộc v2 đủ) | ✅ v2 |
| Warmup + cosine, lr encoder riêng | fine-tune pretrained | `ml/training/sed.py::build_optimizer/build_scheduler` | pilot: lr encoder 3e-4 (ADR-0030 §2); không ablate riêng | ✅ v2 |
| Random crop mỗi epoch | augmentation thời gian | `SedFeatureDataset(random_crop=True)` | không ablate riêng | ✅ v2 |
| Mixup (nhãn mềm) | Zhang và cộng sự, ICLR 2018; PANNs | `ml/training/augment.py` | ablate chung với FilterAugment: không phân biệt được trên event-F1, giúp AP frame (S20) | ✅ giữ trong v2 (không hại) |
| FilterAugment (cộng dB theo dải) | Nam và cộng sự, ICASSP 2022 | `ml/training/augment.py` | như dòng trên (S20) | ✅ giữ trong v2 (không hại) |
| Chọn checkpoint theo macro-AP dev | không phụ thuộc ngưỡng | `SedTrainingConfig(select_metric=…)` | epoch tốt nhất 17 / 23 / 28 cho 3 seed | ✅ v2 |
| Ensemble 3 seed v2 | thực hành chuẩn | `scripts/build_ensemble.py` | CV dev 0.2129 so với run đơn 0.1900; test 0.1476 so với 0.1255 (S18) | ✅ hệ thống được chọn |
| BEATs strong đóng băng + head v2 (T2a) | PretrainedSED (Schmid và cộng sự, 2024) | `ml/models/beats_frozen.py`, `ml/models/embedding_sed.py`, `ml/training/encoded.py` | CV dev ensemble 3 seed 0.2114 ± 0.0491, gần bằng v2 (S28) | ✅ ứng viên (f1)/(f3) cho S13 |
| Kaldi fbank viết lại bằng torch (không phụ thuộc torchaudio) | cần frontend đúng của BEATs pretrained | `ml/features/kaldi_fbank.py` | trùng bit torchaudio 2.11.0 (`tests/test_kaldi_fbank.py`) | ✅ dùng cho T2a |

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
5. **Phân bố xác suất + sai số biên có dấu** (`scripts/report_boundary_errors.py`).
   - **Giả thuyết ban đầu "posterior bão hoà làm onset trễ" bị chính phép đo này bác bỏ**
     (S17). Đây là ví dụ đáng kể trong paper: một trace thuyết phục nhưng sai về tổng thể.
   - Chẩn đoán đúng là **biên tản rộng, đối xứng**. Công cụ dùng lại được cho mọi hệ thống SED
     có dự đoán theo frame.

---

## 5. Ý tưởng chưa làm (future work / thí nghiệm tiếp)

| Ý tưởng | Vì sao đáng làm | Rủi ro / ràng buộc | Liên quan |
|---|---|---|---|
| **Transformer pretrain theo frame** (PretrainedSED: BEATs strong đóng băng ✅ 27/09, rồi `frame_mn10`) | 40 ms. Nguồn **V3** (đọc PDF v2): DESED PSDS1 fine-tune 0.476–0.492, **frozen 0.454–0.492** — gần bằng, nên đóng băng + head là cách rẻ trên 8 GB, chạy đủ seed. `frame_mn` không có số trong bài | Họ model mới, checkpoint ngoài; license: repo MIT, BEATs (unilm) MIT, ATST-F checkpoint CC BY 4.0, M2D riêng → loại; số trong bài là DESED, không phải DataSED | T2a **xong 27/09** (S28, CV dev); T2b `frame_mn10` (fine-tune toàn bộ) còn lại, cần T0 riêng (VRAM khác hẳn — không đóng băng). ADR-0032 |
| **Soundscape tổng hợp từ clip DataSEC** (kiểu DESED/Scaper) | Cơ chế transfer isolated → continuous **khác** pretraining; tạo nhãn mạnh cho lớp hiếm | Chỉ dùng DataSEC **train** và bỏ 130 clip đã loại (leakage); nhãn mạnh nhiễu do khoảng lặng trong clip | RQ1 hướng mới, CLAUDE §8; ADR-0031 §5: chỉ khi còn ≥ 1 tuần trước mốc 18/10 |
| Train chung nhãn mạnh (DataSED) + nhãn yếu (DataSEC) | Chuẩn DCASE Task 4 | Ánh xạ 22 → 21 lớp (bỏ `wind_turbine`) | RQ1 hướng mới |
| RQ1-v2: B vs C dưới recipe v2 | RQ1 âm tính có phải do kiến trúc thô? Thêm 3 model khởi tạo khác cho ensemble 6 model | +3 run (4–6 h; run B-v2 mất 78–117 phút) | **Đã duyệt 26/09** → S9, ADR-0031 §2 (phân tích ghi trước; test chỉ sau vòng chọn cuối) |
| Loss hiệu chuẩn tốt hơn (focal / asymmetric) thay `pos_weight` | Lớp hiếm bị bỏ sót: tỷ lệ frame dương có p < 0.5 của `horn` / `crows_seagulls_magpies` / `thunder_fireworks_gunshot` là 82 / 72 / 58% ở v1 ensemble C và 75 / 73 / 58% ở v2 seed 20260922 (sơ bộ) — v2 chưa sửa (`boundary_errors_20260926.json`); *không* còn động cơ "bão hoà" (đã bác bỏ) | Thêm một núm; chọn trên dev | S11, ADR-0031 §5 (sau Track 2, nếu còn thời gian) |
| Frequency dynamic convolution | SOTA DESED dòng CNN | Đổi kiến trúc conv, không dùng lại trọng số CNN14 | RELATED_WORK §2 |
| Hậu xử lý theo lớp khi có thêm dữ liệu | cSEBB gốc tune theo lớp | A2: overfit dev nhỏ | S4 |
| Báo segment-based metric song song | So được với DCASE 2016/2017 T3 | Không thay primary (không đổi thước đo sau khi thấy số) | evaluation_protocol §3.1 |

---

## 6. Việc phải làm để thành dẫn chứng hợp lệ

| # | Việc | Vì sao |
|---:|---|---|
| ~~1~~ | ~~Đo bão hoà posterior có artifact~~ — **xong 26/09**: `boundary_errors_20260926.md`; giả thuyết bị bác bỏ (S17) | — |
| ~~2~~ | ~~**Event-F1 macro** bên cạnh micro cho mọi hệ thống~~ — **xong 26/09 tối**: `event_f1_macro_20260926` có cả v2 (ensemble 0.1369, run đơn 0.1198). **Người dùng chốt 26/09:** macro là con số chính, chọn vẫn bằng micro (ADR-0031 §1) | evaluation_protocol Q2 đòi macro; mọi số event-F1 headline đến nay là **micro** (`overall` của sed_eval) — lệch protocol, PLAN nợ #20 |
| 3 | Đối chiếu trực tiếp các số văn liệu lấy qua tóm tắt WebFetch (V2 → V3) | Bài học ADR-0015: tóm tắt từng báo sai license |
| 4 | Systematic search: đã có baseline nào trên DataSED chưa | Để được viết "baseline đầu tiên" |
| ~~5~~ | ~~Kết quả v2 (dev → chọn → test một lần)~~ — **xong 26/09 tối** (S18–S25; lựa chọn `ec71b20` trước test `43d5847`) | ADR-0030 §4–§5 |
| 8 | **Giải thích S21**: vì sao event-F1 tăng mà PSDS không tăng. Ví dụ: đo PSDS theo lớp, so đường ROC của v1 và v2, và xem θ global 0.95 có đặt v2 vào một điểm vận hành khác không | Không giải thích thì không được viết "v2 tốt hơn" chung chung; phải nói theo từng metric |
| 6 | Vòng chọn cuối 18/10 với ứng viên ghi trước; test RQ1-v2 chỉ mở **sau** khi lựa chọn cuối commit | ADR-0031 §2, §4: không số test nào có trước lựa chọn cuối hay dẫn hướng Track 2 |
| ~~7~~ | ~~PretrainedSED lên V3~~ — **xong 26/09 tối**: đọc PDF v2, code, LICENSE (RELATED_WORK §2.1 (2)); bắt được dòng "checkpoint cũ" sai phiên bản trong bản V2 | ADR-0031 §3, cổng T0 bước 1–2 |

---

## 7. Bảng / hình dự kiến cho paper

| Hình / bảng | Nội dung | Nguồn số |
|---|---|---|
| Hình 1 | Event-F1 theo độ dài khối quyết định (trần độ phân giải), vạch ngang trần người 0.58, điểm hệ thống v1/v2 | `sed_ceilings_*.json` |
| Hình 2 | Phân rã lỗi (khớp / lệch biên / bỏ sót) v1 so với v2 | `report_sed_ceilings --run` cho từng hệ thống |
| Hình 3 | Phân bố sai số onset/offset có dấu (v1 so với v2) + phân bố xác suất frame âm/dương | `boundary_errors_*.json` (`scripts/report_boundary_errors.py`) |
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
6. Metric headline trước 26/09 là micro, trong khi Q2 đòi macro (§6 #2). Từ 26/09 báo macro
   trước, nhưng thước **chọn** hệ thống vẫn là micro (ADR-0031 §1) — paper phải nói rõ hai thước
   này khác nhau và báo thứ hạng theo macro dev để người đọc tự kiểm.
7. License checkpoint AudioSet không ghi (ADR-0015); dữ liệu CC-BY-NC-SA → model công bố phải
   cùng license.
8. Nhiều số văn liệu hiện ở mức V2 (lấy qua tóm tắt) — chưa được trích. PretrainedSED đã lên V3
   (26/09); còn DCASE 2016 T3, bài DataSED (PLAN nợ #21).
9. v2 cải thiện event-F1 (micro +0.054 với CI ghép cặp không chứa 0; macro +0.045) nhưng **không**
   cải thiện PSDS-1/2 (S21). CI bootstrap chỉ đo độ bất định do mẫu recording, không đo độ lệch giữa
   seed. Hệ thống được chọn không được gọi là tốt hơn run đơn (S18).
10. Ablation v2 chỉ 1 seed mỗi biến thể; kết luận "không phân biệt được" (S20) không có nghĩa là
    "không có hiệu ứng".

---

## 9. Nhật ký giai đoạn cải thiện SED (ADR-0030)

| Ngày | Việc | Commit / artifact |
|---|---|---|
| 26/09 | Chẩn đoán trần + phân rã lỗi | `dd5d3b9`, `sed_ceilings_20260926.md` |
| 26/09 | cSEBB + CV (âm tính trên v1) | `9dc78dc`, `sebb_cv_…_20260926.md` |
| 26/09 | Code SED v2, `dump_predictions` (trùng bit), `evaluate_run --split dev` | `8b1df60` |
| 26/09 | ADR-0030 (Proposed) + pilot lr encoder 3e-4 | `ead5a2f` |
| 26/09 | Hàng đợi 6 run v2 (3 seed + 3 ablation), bắt đầu 10:33 trên tree sạch `e808df4` | `ml/runs/sed_polyphonic_20260926T033312Z`, … (điền khi xong) |
| 26/09 | Run 1 (seed 20260922) xong 12:30: AP frame dev tốt nhất 0.688 (epoch 17), không tụt tới epoch 30. CV dev θ global p25 **0.1900 ± 0.0523** (v1 ensemble C 0.1538 ± 0.0214); cSEBB 0.0953. `dump --verify-dev` trùng bit. **Sơ bộ, 1/3 seed** | `ml/runs/sed_polyphonic_20260926T033312Z/` |
| 26/09 | Mã thoát 127 của mọi run v2: cuDNN khi giải phóng GRU nhiều lớp có dropout (chế độ train) lúc tắt, trên Windows; artifact đã ghi xong. Follower CV kiểm `manifest.complete` | ADR-0030 §8, TRAINING_OPS_PLAN |
| 26/09 | Đo phân bố xác suất + sai số biên → bác bỏ "bão hoà" (S17) | `boundary_errors_20260926.md` (`550daec`) |
| 26/09 | Luật chọn §5 thành code + công cụ ablation, macro, `build_ensemble --splits` | `550daec` |
| 26/09 | Người dùng duyệt lộ trình: macro là con số chính, chọn bằng micro; RQ1-v2 (S9); Track 2 qua cổng T0 (S10); vòng chọn cuối có ứng viên ghi trước, mốc đóng băng 18/10; S8 một lần sau mốc. Kiểm checkpoint DataSEC khớp encoder v2 (74 tensor) | ADR-0031 |
| 26/09 (tối) | T0 bước 1–2 cho Track 2: PretrainedSED lên V3, chuỗi license; đổi thứ tự sang BEATs đóng băng + head trước `frame_mn10` (frozen gần fine-tune; `frame_mn` không có số); ứng viên (f1)–(f4) ghi trước khi có số | RELATED_WORK §2.1 (2), ADR-0032 (`df8f3c0`) |
| 26/09 | Hàng đợi v2 xong 18:10; CV từng run xong 18:37 (6 run, tree sạch). Run: seed 20260922 `033312Z`, seed 2 `053024Z`, seed 3 `064832Z`, pool /64 `075611Z`, trần 50 `085233Z`, không augmentation `100315Z` | `ml/runs/sed_polyphonic_20260926T*` |
| 26/09 (tối) | Ensemble chỉ-dev bằng script repo (`150934Z`, `dev.npz` trùng từng byte bản xem trước); ablation; biên; phân rã lỗi v2; macro dev (S19–S25) | `8795960` |
| 26/09 (tối) | **Lựa chọn commit trước khi mở test**: ensemble v2 3 seed | `ec71b20` (tree sạch) |
| 26/09 (tối) | Test một lần cho (b) và (c); ensemble dev+test `155630Z` (dev trùng SHA); sổ test, macro; bootstrap ghép cặp v2 − v1 +0.0536 [+0.0261, +0.0853] (S18) | `43d5847` + commit tài liệu này |
| 26/09 23:17 | S9 (RQ1-v2) bắt đầu: 3 run C-v2 tại `43d5847` | `scratchpad/s9_queue.log` |
| 27/09 03:53 | S9 xong: 3 run C-v2 hoàn tất trên tree sạch, code train vẫn trùng `e808df4`. CV dev sơ bộ (S26) chưa tách biệt B-v2/C-v2 | `sed_polyphonic_20260926T{161726,172229,185208}Z` |
| 27/09 04:42 | Dựng ensemble (d) C-v2 3-seed và (e) B-v2+C-v2 6-model (ADR-0031 §4), chạy CV dev cả hai họ hậu xử lý. (d) có CV cao nhất trong mọi ứng viên non-Track2 (S27) | `sed_ensemble_cv2_20260926T205405Z`, `sed_ensemble_bcv2_20260926T205412Z` |
| 27/09 | Sửa nợ #24 (`best_validation` theo đúng `select_metric`) | `4135d17` |
| 27/09 | Push `wip/sed-v2` (người dùng cho phép); người dùng duyệt ADR-0032 (Track 2 thật): tải `BEATs_strong_1.pt` (SHA-256 `db13a79a…`, khớp kích thước release v0.0.1); chép tối thiểu mã BEATs từ PretrainedSED @`1aa47e48` (`ml/models/external/beats/`, MIT) | `52f2f45` |
| 27/09 | T0 bước 3–4 T2a: VRAM 1.6 GB/batch 24, ~64 s mã hoá/epoch; 1 epoch dev hết đường ống (`verify-dev` trùng bit) | `docs/measurements/track2_t0_beats_20260927.md`, `7437760` |
| 27/09 | Pilot lr head T2a: 3 epoch × {3e-4, 1e-3, 3e-3} → chọn **0.001** (AP dev epoch 3: 0.7248/0.7372/0.7203). Sự cố: `report_pilot_lr.py` in tiếng Việt ra console cp1252 (Windows) vỡ `UnicodeEncodeError`, hàng đợi đọc biến lr rỗng, 3 run "chính thức" lỗi tham số dòng lệnh ngay khi khởi tạo (chưa chạm GPU, không mất dữ liệu). Sửa `sys.stdout.reconfigure(utf-8)`, viết lại hàng đợi (sửa luôn lỗi `exit` trong subshell không dừng được vòng lặp cha, và `rc=$?` bị `$(date …)` ghi đè trước khi đọc) | `9ac9866`, `7036028` |
| 27/09 | 3 seed T2a (BEATs đóng băng + head v2, lr 0.001) train + CV xong; ensemble (f1)/(f3) dựng + CV xong (S28–S29) | `sed_polyphonic_20260927T{064341,092605,113910}Z`, `sed_ensemble_t2a_20260927T141952Z`, `sed_ensemble_t2a_bv2_20260927T142003Z` |
