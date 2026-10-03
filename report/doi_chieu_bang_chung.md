# Đối chiếu bằng chứng — báo cáo giữa kỳ

> Mỗi dòng: khẳng định hoặc con số trong báo cáo → nguồn → artifact/code → run, cấu hình, split,
> tập đánh giá → giới hạn diễn giải → vị trí trong báo cáo. Bảng định lượng trong DOCX được chèn
> nguyên văn từ tệp sinh tự động (`docs/thesis/tables/*`, `report/tables/*`), nên mọi số trong các
> bảng đó truy về tệp nguồn ghi ngay dưới bảng. Bảng này liệt kê thêm các số được **nhắc lại trong
> văn xuôi** và các khẳng định định tính.
> Mức trạng thái: (a) thiết kế, (b) đã triển khai, (c) đã kiểm chứng bằng lệnh và artifact,
> (d) chưa thực hiện.

## 1. Dữ liệu (Chương 3)

| Khẳng định | Nguồn | Artifact / code | Phạm vi | Giới hạn diễn giải | Vị trí |
|---|---|---|---|---|---|
| DataSEC 5.048 tệp, 23,71 h, 44,1 kHz mono; DataSED 717 tệp, 18,68 h, 716 mono/1 stereo | Inventory | `data/manifests/datas{ec,ed}_inventory_summary.json` | Toàn archive | Số bài báo khác archive; báo cáo theo archive | 3.1, Bảng 3.2 |
| Archive 6.414.663.316 B và 4.510.378.259 B, MD5 khớp | D0 audit | `docs/measurements/archive_audit_20260922.md` | — | — | 3.1 |
| `voices` 1.900 (37,6%), `music` 1.001 (19,8%); lớp nhỏ nhất 50 tệp | Inventory | `docs/data_inventory.md` | DataSEC | Tỷ lệ 38:1 là 1.900/50 | 3.1.1 |
| 4.034 sự kiện đa âm/21 lớp phủ 703 bản ghi; 4.309 đơn âm/22 lớp; độ dài 0,41–296,5 s, trung vị 5,8 s | D2 audit | `data/manifests/datased_preparation_audit.json` | DataSED | — | 3.1.2 |
| 22/22 lớp gộp, 10/10 nhóm lớp con khớp, 0 nhãn lạ | Archive audit | `archive_audit_20260922.md`; `ml/configs/taxonomy.yaml` (SHA `67ca8a8c…`) | — | — | 3.2 |
| 21 lớp SED, `wind_turbine` không có trong nhãn đa âm | Taxonomy | `ml/configs/taxonomy.yaml` (`polyphonic: false`) | — | Không so 21 lớp với 22 lớp | 3.2 |
| Fingerprint gốc: 52,6% cặp âm vượt ngưỡng; sau sửa: positive min 1,0000, negative max 0,9205, 0/5.000 ≥ 0,95 | Hiệu chuẩn T3 | `data/interim/dedup/threshold_calibration.json`; ADR-0007 | 24 cặp dương, 5.000 cặp âm | — | 3.3.3 |
| T1/T2/T3 24/24/45.191 cặp; 84 nhóm; 3 nhóm xuyên dataset; 35 cặp duyệt tay (10/1/24) | D3 | `data/manifests/duplicate_audit.json`; `review_worksheet_20260923.md` | — | Duyệt tay 1 người | 3.3.3, Bảng 3.1 |
| Cặp trùng `Sirens-0046`↔`S-0233` 1,000000/35 s; `Sirens-0067`↔`S-0211`/13 s; `Train-0012`↔`S-0213` 0,9548/31 s | D3 | `docs/measurements/dedup_20260923.md` | — | — | 3.3.3 |
| Loại 11 đoạn (0,2179%) + 119 trùng nội bộ = 130 đoạn DataSEC | Exclusions | `data/manifests/exclusions.csv` (10 leak + 1 unsure + 119 duplicate) | — | Dải `minor` theo DATA_PLAN §7.6 | 3.3.3 |
| Tập chia 438/137/142 (60/20/20) và 3.434/744/740; 687 và 4.873 nhóm; SHA `d2924a5e…`, `e8d30990…` | Split đóng băng | `data/splits/*.frozen.json` | seed 20260922 | — | 3.3.4, Bảng 3.2 |
| Ngưỡng cohesion 0,93; khối 315 tệp mật độ 0,024 ở 0,85 | ADR-0012 | `docs/decisions/ADR-0012-nguong-cohesion.md` | DataSEC | — | 3.3.4 |
| D4 5/5 đạt; bỏ exclusion thì kiểm 5 thất bại đúng `Sirens-0046.wav` | D4 | `data/manifests/datase{c,d}_leakage_report.json`; ADR-0013; CLAUDE §10 23/09 | — | — | 3.3.4 |
| 14 bản ghi `S-0704…S-0717` không có nhãn đa âm (8/3/3); tập annotated dev 134, test 139 | Coverage | `docs/measurements/polyphonic_coverage_20260927.md`; ADR-0034 | — | Kết quả `all` cũ giữ nguyên | 3.4.1 |
| 8 cặp chú giải hai lần: 67/94 biên trong 0,2 s; lệch lớn nhất 12,72 s; 2/8 bất đồng; F1 người 0,5785 | Đo đồng thuận | `annotation_consistency_20260923.md`; `sed_ceilings_20260926.json` | 8 cặp | Cỡ mẫu rất nhỏ | 3.4.2 |
| Một phần âm thanh từ Freesound/AudioSet, có thêm âm thanh tay | Bài dataset (V3) | RELATED_WORK §1 | — | Mức trùng không định lượng | 2.4.4, 3.5 |

## 2. Phương pháp và triển khai (Chương 4–5)

| Khẳng định | Nguồn | Artifact / code | Trạng thái | Giới hạn | Vị trí |
|---|---|---|---|---|---|
| Loss phân cấp, λ_sub = 1, λ_cons = 0,5 | Code + D4 | `ml/models/hierarchical.py`; `consistency_sweep_datasec_20260923.md` | (c) | — | 4.2, CT 4.1 |
| Chuyển 92,23% tham số CNN14 | Checkpoint | `panns_checkpoint_20260923.md`; ADR-0018 | (c) | — | 4.2 |
| BCE có mask, `w_c = min(w_max, max(1, (T−P_c)/P_c))` | Code | `ml/training/sed.py::masked_bce`, `estimate_pos_weight` | (c) | — | 4.3.1 |
| `logmel_v1` 16 kHz/50 khung/s; `logmel_panns_v1` 32 kHz/100 khung/s | Config | `ml/configs/features.yaml` | (c) | CLAUDE §10 ghi "50 fps" cho panns là **sai**; config là chuẩn | 3.3.1, 4.3.2 |
| v1 nén /64 ≈ 0,64 s; trần 0,6294 | Code + đo | `ml/models/panns.py`; `sed_ceilings_20260926.json` | (c) | Đo trên dev, cây bẩn | 4.3.2, Bảng 6.3 |
| v2: /8, BiGRU 2×256, 30 epoch, lr 3e-4/1e-3, mixup 0,5, FilterAugment 0,5 ±6 dB, w_max 10 | Recipe | `scripts/train_sed.py` (recipe v2); ADR-0030 §9 | (c) | — | 4.3.3 |
| T2a BEATs đóng băng (~90,4 M) + BiGRU (~3,3 M) | ADR-0032 §9 | `ml/models/beats_frozen.py`, `embedding_sed.py` | (c) | Chỉ CV dev trước S13 | 4.3.4 |
| T2b frame_mn10 (~3 M), 16 kHz, 128 mel, 250 bước/10 s, lr 3e-4, chỉ mixup | Code | `ml/models/frame_mn_finetune.py`; `train_sed.py` recipe t2b | (c) | — | 4.3.4 |
| Ensemble trung bình xác suất, kiểm khớp thành viên | Code | `ml/evaluation/ensemble.py` | (c) | — | 4.3.5, CT 4.4 |
| Lưới cSEBB τ {0,32…1,28}, 6 kiểu gộp; f2 khóa τ 0,64 rel 2 | Code + chọn | `scripts/select_sebb_cv.py`; `s13_selection_20261018.json` | (c) | — | 4.4.2 |
| d_min p5, g_max p50 → p25; lưới θ 0,05–0,95 | Code | `ml/postprocessing/calibration.py`; `scripts/select_postproc_cv.py`; ADR-0003/0024 | (c) | — | 4.4.1 |
| Qwen3.5-9B Q4_K_M, llama.cpp b11158, nhiệt độ 0, seed 20260922 | Config | `ml/configs/caption_llm.yaml` | (c) | Tất định theo chuỗi request | 4.5.2 |
| GBNF dãy con theo onset; cover bắt buộc sự kiện đầu mỗi lớp | Code | `ml/captioning/constrained.py`; ADR-0023, ADR-0026 | (c) | — | 4.5.2 |
| Bốn vị từ thời gian, SQL ≡ Python (kiểm trên SQLite) | Code + test | `ml/retrieval/temporal.py`; tests retrieval | (c) | — | 4.6.2, Bảng 4.2 |
| Recall@k, MRR, nDCG@10 nhị phân, filter exactness | Code | `scripts/evaluate_retrieval.py::rank_metrics` | (c) | Bootstrap theo truy vấn | 4.7.2, CT 4.7 |
| Bộ truy vấn 100 câu 21/27/30/22; 97/100 có relevant trên test | Measurement | `retrieval_queryset_v2_20260925.md` | (c) | Chọn theo train | 4.7.2 |
| Bootstrap 1000 lần, seed 20260922, theo bản ghi | Code | `ml/evaluation/bootstrap.py` | (c) | — | 4.7.3 |
| API không import torch (kiểm AST trong CI); 8 contract JSON Schema | Code + CI | `tests/test_api_boundaries.py`; `contracts/`; `.github/workflows/ci.yml` | (c) | — | 5.1 |
| Upload: 415 nếu sai định dạng, ≤ 50 MB, ≤ 600 s | Code | `services/common/audio.py` | (c) | — | 5.2.2 |
| 7 bảng CSDL, chỉ mục GIN + HNSW | Migration | `db/migrations/001_event_store.sql` | (c) | — | 5.2.2 |
| `services/stream` chỉ là khung, chưa có mã | Repo | `services/stream/` rỗng | (d) | — | 1.5, 5.3 |
| Chưa có xác thực; mật khẩu Compose chỉ cho dev | Repo | `docker-compose.yml`; PLAN L6 | (d) | — | 5.3, 7.3 |
| Demo history 15 bản ghi TRAIN phủ 21 lớp; 5 câu hỏi chạy thật | Measurement | `demo_seed_20261002.md`, `demo_script_20261002.md` | (c) | — | 5.3 |
| Upload + phân tích 2,012 s; RAG 0,250 s (S-0016, CPU) | Measurement | `demo_f2_e2e_20261002.json` | (c) | Một lượt, không có thống kê | 5.3, Bảng 5.2 |
| pytest 738 pass (02/10); tại mốc báo cáo 744 pass, 4 skip | STATUS + lệnh | `docs/STATUS.md`; `report/kiem_tra_bao_cao.md` | (c) | 4 skip là test DB khi Docker tắt | 5.5 |
| Lỗi ghép cửa sổ (`7ada7d7`) làm đổi mọi số SED; 11 run tính lại | Git + CLAUDE §10 | commit `7ada7d7`, `3208dbb` | (c) | — | 5.5 |

## 3. Kết quả (Chương 6) — số nhắc lại trong văn xuôi

| Khẳng định | Artifact | Split / tập | Giới hạn | Vị trí |
|---|---|---|---|---|
| Classifier: coarse 0,8466; lớp con 0,6266 / 0,8453; nhất quán 0,9526; ECE 0,0332 → 0,0564 (T 1,5681) | `ml/runs/classifier_datasec_20260923T121808Z/metrics.json`; `ece_datasec_20260923.md` | DataSEC test 740 | ECE tăng sau hiệu chuẩn | 6.1, Bảng 6.1 |
| `vacuum_cleaner` 0/4, `air_compressor` 0/5; `vehicle_idling` 0,6154, `vehicle_pass_by` 0,6538 | `per_class_metrics_datasec_20260923.md` | DataSEC test | n < 10 chỉ số tuyệt đối | 6.1, PL C |
| RQ1-v1: B 0,0610, C 0,0539, C−B −0,0071 [−0,0164; +0,0021], p 0,2336; PSDS p 0,913/0,181 | `rq1_multiseed_clean_20260924.json`; `rq1_multirun_bootstrap_clean_20260925.json` | test all, 7 run sạch | Micro; run không tất định | 6.2.1, Bảng 6.2 |
| A 0,0360 / PSDS-2 0,4514; B 0,0621 / 0,6456 | `rq1_delta_official_20260924.md` | test all, run đơn | Run đơn | 6.2.1 |
| RQ1-v2: B 0,1221/0,1324, C 0,1147/0,1294, C−B −0,0029 [−0,0254; +0,0199], p 0,6965 (macro 0,4220), PSDS-2 +0,0279 p 0,0193 | `rq1_v2_multiseed_20260929.json`; `rq1_multirun_bootstrap_rq1_v2_annotated_20260929.json` | test annotated | Chưa hiệu chỉnh so sánh bội | 6.2.2 |
| Trần 0,6294/0,3032; người 0,5785; v1 onset 0,2325, offset 0,4975, segment 0,6542; 112/417/357 | `sed_ceilings_20260926.json`, `sed_ceilings_v2_20260926.json` | dev in-sample | Hai tệp `dirty=true`; chỉ chẩn đoán | 6.3.1, Bảng 6.3 |
| Collar 0,2 → 1 s: B 0,062 → 0,185 | `collar_sensitivity_20260924.md` | test, run B | Chẩn đoán | 6.3.1 |
| Posterior khung âm trung vị 0,008; IQR onset −0,39…+0,51 s; 30,2% trong ±0,2 s | `boundary_errors_20260926.md` | dev | — | 6.3.1 |
| v2 CV 0,1900/0,2096/0,2169; ablation −0,0840/−0,0126/+0,0068; AP 0,667 vs 0,688 | `sed_v2_ablation_20260926.json`; PAPER_NOTES S19–S20 | CV dev | 1 seed mỗi ablation | 6.3.2, Bảng 6.4 |
| v2 chọn (c) CV 0,2129 ± 0,0622 trước test (`ec71b20`); test all micro 0,1476 [0,1088; 0,1866], macro 0,1369; v2 − v1 +0,0536 [+0,0261; +0,0853]; PSDS 0,3447/0,6744 vs 0,3489/0,6987 | `sed_v2_selection_20260926.md`; `sed_ensemble_v2_20260926T155630Z_eval_cv.md`; `rq1_multirun_bootstrap_sedv2_vs_v1_20260926.md` | test all | Không gọi tốt hơn run đơn | 6.3.2 |
| A2 −48/−39/−41% vs −15/−4/−2%; A3 +0,0063/+0,0026/−0,0014 | `*_threshold_ablation_A2.md`, `*_median_filter_ablation_A3.md` | dev→test | — | 6.3.2 |
| S13: f2 CV 0,2383 ± 0,0562, chênh f4 0,0029; commit `c3f0033`; test f2 macro 0,1206, micro 0,1643 [0,1103; 0,2242], PSDS 0,3164/0,7253; f1 micro 0,1817; g1 macro 0,1617 | `s13_selection_20261018.json`; `s13_test_20261018.json` | dev annotated 134; test annotated 139 | Không chọn lại theo test | 6.3.3, Bảng 6.5, Hình 6.1 |
| f2 vs v2: micro 0,1643 vs 0,1500, macro 0,1206 vs 0,1389, PSDS-1 0,3164 vs 0,3458 | `s13_test_20261018.json` | test annotated | CI chồng lấp → không khẳng định | 6.3.3, Bảng 6.6 |
| f2: 7/21 lớp F1 = 0; 295 dự đoán / 740 tham chiếu; 349 bỏ sót | `ml/runs/sed_ensemble_s13_f2_20260929T045053Z/evaluation_cv_annotated.json` | test annotated | — | 6.3.3, PL C |
| cSEBB thua ở v1 (0,0582 vs 0,1538), v2, T2a; thắng ở f2 (0,2383 vs 0,2107) | `sebb_cv_…_20260926.md`; PAPER_NOTES S25, S29, S33; Bảng 6.7 | CV dev | Chênh nằm trong dao động fold; giả thuyết cơ chế chưa kiểm chứng | 6.3.4 |
| RQ2 f2 test: unconstrained ảo giác 0,0065/0,0112, bối cảnh 0,2887/0,4014, quá cụ thể ~0,14, từ cấm 0,0070; constrained omission 0,0925 oracle; hiệu +0,074 [+0,044; +0,107]; e2e +0,007 [−0,002; +0,019] | `caption_grounding_sed_ensemble_s13_f2_20260929T045053Z_test.{json,md}` | test all 142 | Bộ đo dựa từ điển | 6.4, Bảng 6.8 |
| RQ2 v1 → f2: omission constrained 0,036 → 0,012; ảo giác unconstrained 0,005 → 0,011 | `s8_summary_20261002.json` | test all | CI chồng lấp | 6.4, Bảng 6.9 |
| Lexicon vs người: precision 0,896, recall 0,936; 7/8 "bịa" là lỗi từ điển | `caption_mention_agreement_20260925.md`; evaluation_protocol §12 #2 | 60 mô tả test, 1 người | Hệ cũ (run B) | 6.4 |
| Ví dụ S-0009: mô tả đúng hợp đồng nhưng sai so với nhãn gốc | `…/captions/constrained_cover_dev.jsonl` | dev | Minh họa một bản ghi | 4.5.3, Hình 4.3 |
| RQ3: run B structured 0,5231, hybrid 0,4808/0,4716, vector 0,4179/0,3403; hybrid − structured −0,042 [−0,085; −0,004]; vector exactness 0,5866 | `s8_summary_20261002.json`; `retrieval_benchmark_test_20260925.md` | test, bộ lọc gold | Cận trên độ đúng bộ lọc | 6.5, Bảng 6.10 |
| RQ3 f2: structured 0,4161, hybrid 0,4147/0,4197, vector 0,5261/0,4890, exactness vector 0,274; parsed Δ −0,006…0,000 | `s8_summary_20261002.json` | test | Suy giảm; giả thuyết về recall chưa kiểm chứng | 6.5 |
| Câu trả lời: unsupported 0,000; 97/97 hợp đồng ở 8 cấu hình | `s8_summary_20261002.json`; `retrieval_answers_test*_20261002.md` | test | — | 6.5 |
| Parser 240/240 hợp lược đồ; exact 0,855/0,925; vị từ 0,767; validation hybrid Δ +0,012/−0,002 | `query_parser_20260928.json`; `retrieval_benchmark_validation_parsed_20260928.md` | template 200, paraphrase 40, validation | Δ dương không phải cải thiện | 6.6, Bảng 6.11 |
| Parity CUDA 299/299; CPU 290/299 trùng, 294/299 trong collar, Δp 0,0239 | `inference_parity_20260929.json`; `inference_parity_cpu_20261002.json` | output test đóng băng | Không phải metric test mới | 6.6, Bảng 6.12 |
| 40 lượt SED trên test, 10 dirty; 15 lượt S13 dirty; S8 log tạm | `test_ledger_20261002.json`; ADR-0031 §9; PAPER_NOTES §8 #11–12 | — | Hạn chế truy nguồn | 6.7, Bảng 6.13 |
| Frame macro-F1 B 0,5850 → 0,5705 cùng seed | PLAN nợ #5 | — | Nguyên nhân chưa xác định | 6.7 |

## 4. Văn liệu (Chương 2)

Mọi trích dẫn chỉ dùng 14 nguồn mức V3 trong `docs/thesis/bibliography.bib`; mỗi ý được trích ghi ở
`docs/RELATED_WORK.md` §2.1–§2.2 kèm cách tiếp cận (đọc PDF/HTML trực tiếp, Crossref cho metadata).
Các chủ đề chưa có nguồn V3 (AAC và metric AAC, truy hồi âm thanh, quan hệ khoảng Allen, nDCG,
bootstrap) **không** được trích; báo cáo ghi rõ là khoảng trống tổng quan (2.5, 7.4).

## 5. Mâu thuẫn tài liệu đã phát hiện khi đối chiếu

| Mâu thuẫn | Tài liệu | Nguồn chân lý dùng trong báo cáo |
|---|---|---|
| Bảng "Phạm vi đã triển khai" và §4.2, §8.1, §8.4 của SYSTEM.md còn ghi ○ cho các phần đã xong | `docs/SYSTEM.md` | STATUS.md + measurements |
| `logmel_panns_v1` ghi "50 fps" trong nhật ký CLAUDE.md (W2) | `CLAUDE.md` §10 | `ml/configs/features.yaml`: 32 kHz / hop 320 = 100 khung/s |
| Tên tác giả trong bibliography.bib cũ (Artuso, Pompei, Akbaba, Morocutti) | `docs/thesis/bibliography.bib` | Crossref + nature.com; đã sửa |
| Hình `05_f2_per_class_event_f1.png` cũ ghi F1 cho lớp có 9 sự kiện và dùng nhãn tiếng Việt | `docs/thesis/figures/` | Không dùng; thay bằng bảng PL C |
| Chuỗi `S-0704…S-0717` trong DataSED không có nhãn đa âm nhưng SYSTEM §6.6 nói "14 recording không có polyphonic target event" như thể là dữ liệu thật | `docs/SYSTEM.md` | ADR-0034: thiếu nhãn, không phải im lặng |
