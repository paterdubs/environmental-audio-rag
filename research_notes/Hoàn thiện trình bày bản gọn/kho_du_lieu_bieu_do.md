# Kho dữ liệu cho biểu đồ mới của bản gọn (chỉ dùng artifact đã có, không đo mới)

Phạm vi: rà trong repo (chỉ đọc) xem artifact nào đã tính sẵn đủ để vẽ thêm biểu đồ matplotlib cho
`report/gon_src/*.md`, chủ yếu Chương 6. Mọi đường dẫn dưới đây tính từ gốc repo; link dạng `../../…`
trỏ từ thư mục ghi chú này về gốc repo. Không mở `predictions/test.npz`, không chạy lại đánh giá.
Mọi số trích dưới đây được đọc trực tiếp từ tệp JSON/MD/CSV bằng Python one-liner trong phiên này.

Hiện trạng: bản gọn dùng 14 hình: r01, r02 (Ch.3); r05, m05_dev_timeline (Ch.4); f03a, f03b, ảnh demo 03 (Ch.5);
r04, f01, r07, r13 (Ch.6); r12, r03, r08 (Phụ lục). Chương 6 chỉ có 4 hình (r04, f01, r07, r13), trong khi có
11 bảng `@@INCLUDE@@` — [06_ket_qua.md](../../report/gon_src/06_ket_qua.md).

---

## Câu hỏi 0 — Danh mục ưu tiên 37 hình mới (14 tầng A, 15 tầng B, 8 tầng C; C7–C8 có thể bỏ nếu cần giữ ≤ 35)

### Takeaway
Có đủ dữ liệu đã đóng băng cho khoảng 35 hình mới mà không cần đo thêm. Phần lớn nằm ở Chương 6 (RQ1–RQ3, LBR, PSDS,
bộ đo mô tả, truy hồi). Ba nguồn chính là `final_numbers_20261110.json`, `evaluation_phase_lbr_annotated.json` của
B0 và các JSON đo ngày 23–24/11 (`calibration`, `lbr_context`, `rq3_modes`, `retrieval_backfill_test`,
`retrieval_failures_test`, `caption_vs_gt_dev`, `checker_sensitivity_dev`, `grouped_captions_dev`). Bảy hình nên làm
trước vì mỗi hình gom một luận điểm chính: A1 (forest các hiệu), A2 (tầng C: chỉ LBR vượt 0), A3 (bốn cách đo so
với đồng thuận gán nhãn), A4 (điểm vận hành LBR), A6 (phân rã lỗi truy hồi), A8 (mô tả: so với dự đoán và so với
nhãn gốc), A9 (độ nhạy bộ đo).

### Cited Findings

Cột "Công": S = dưới 1 giờ (đọc 1 JSON, 1 kiểu biểu đồ), M = 1–3 giờ (ghép nhiều tệp hoặc nhiều panel), L = hơn 3 giờ.
Tên tệp ngắn gọn là `docs/measurements/<tên>`, trừ khi ghi rõ `ml/runs/…` hoặc `data/manifests/…`.

**Tầng A: Chương 6, thêm vào thân bài (ưu tiên cao nhất)**

| # | ID / tiêu đề đề xuất | Đích trong gon_src | Loại | Nguồn dữ liệu và khóa | Đã có ở bảng? | Công | Lưu ý |
|---|---|---|---|---|---|---|---|
| A1 | g01 "Các hiệu event-F1 chính và KTC 95%" | 06 "## Mức tin cậy của các so sánh" (hoặc ngay sau tbl:keyresults) | Forest plot ngang, tô màu theo loại tập (test / ngoài mẫu) | `final_numbers_20261110.json`: `rq1.v1.bootstrap_c_minus_b`, `rq1.v2.bootstrap_c_minus_b`, `sed.b0_minus_f2.{estimate,lower,upper}`, `sed.rows.lbrv2_f1.delta_micro_vs_b0`, `sed.rows.lbrv3_f1.delta_micro_vs_b0`; `rq1_multirun_bootstrap_sedv2_vs_v1_20260926.json` `differences["v1-v2"]` = −0,0536 [−0,0853; −0,0261] (**đảo dấu** để ra v2−v1); `lbr_context_20261123.json` `deltas.LBR_v2` (+0,0990 [+0,0761; +0,1200], ngoài mẫu) | Rải ở tbl:rq1, tbl:sedfinal, tbl:keyresults | M | Số trong final_numbers bọc dạng `{value, source, key}` → dùng hàm `_value()` của `build_research_figures.py`. Trộn tập 142 bản ghi (SED v1, "all") với 139 bản ghi (annotated) và ngoài mẫu 564: ghi n cạnh từng dòng. KTC không hiệu chỉnh so sánh bội (06 đã nói). |
| A2 | g02 "Tầng C: chỉ LBR vượt hệ cơ sở trên dự đoán ngoài mẫu" | 06 "## LBR và hệ thống cuối" (hoặc 04 "Cách chọn hệ thống") | Forest Δ micro so với B0 (OOF 564) + panel phụ: điểm tầng S trên dev | `oof_selection_20261009.json` `differences.{TF,TFKD,ENS_B0_TFKD}`; `oof_selection_20261014.json` `differences.{OD,ENS_B0_OD}`; `oof_selection_20261108.json` `differences.P1`; `oof_selection_20261108_P4.json` `differences.P4`; `ml/runs/sed_lbr_B0_20261109T172809Z/lbr_selection_annotated.json` `deltas.{LBR_v1,LBR_v2,LBR_v1_on_P1x3,LBR_v2_on_P1x3}`; `ml/runs/sed_lbr_B0v3_20261110T042337Z/lbr_application_annotated.json` `deltas.LBR_v3`. Panel tầng S: `tier_s_20261009.json` `rows[].vs_best_seed.mean`, `passes_screening` | Một phần ở tbl:lbrcontext | M | Giá trị: TF −0,0206, TFKD −0,0267, OD −0,0290 [−0,0546; +0,0001], P1 +0,0002, P4 −0,0082, LBR V1 +0,0701, V2 +0,0990, V3 +0,0716, V2 trên P1×3 +0,1160. Tầng S là CV dev 134 bản ghi, không phải cùng thước với OOF; số tầng S của P2/P3/P4 (0,1999/0,2225/0,2402) chỉ thấy trong PAPER_NOTES S61–S63, chưa thấy JSON gom (xem Gaps). |
| A3 | g04 "Event-F1 theo bốn cách đo, cạnh mức đồng thuận gán nhãn" | 06 "## Event-F1 khoảng 0,30 là cao hay thấp?" | Cột nhóm (4 chỉ số × 4 hệ) + đường đứt nét cho người | `calibration_20261123.json` `rows.{B0, "LBR V2, điểm f1", "LBR V3, điểm f1", "LBR V3, recall_first"}.{micro, collar_1s, segment_1s, intersection_recall, intersection_precision}`; `human.{micro_f1, event_f1_collar_1s, segment_f1_1s}`; `ratios` | Có: tbl:calibration (f11) | S | Người: 8 cặp, bản ghi khác với tập kiểm tra; không vẽ như "trần". Người không có chỉ số giao nhau trong `calibration`, nhưng có `intersection_f1` 0,9173 trong `lbr_selection_annotated.json` `human_ceiling.all`. |
| A4 | g05 "Điểm vận hành của các hệ SED: precision và recall theo giao nhau" | 06 "## LBR và hệ thống cuối" (cạnh fig:sedfinal) | Scatter trên mặt phẳng P–R giao nhau, kích thước điểm = event-F1 micro, nhãn nsys/740 | `ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/evaluation_phase_lbr_annotated.json`: `lbr.baseline.all` (B0), `lbr.points.{f1,recall_first}.all` (V2), `lbr_extra[0].points.{f1,recall_first}.all` (V3); khóa `intersection.micro.{precision,recall}`, `micro_f1`, `nsys`, `segment_f1_1s.micro` | Một phần ở tbl:sedfinal, f01_sed_final | S | Gồm cả hai điểm không phải cấu hình chính (V2 recall_first: micro 0,2917, nsys 412; V3 f1: micro 0,2731, nsys 395) → ghi rõ "điểm phụ". V3 chính là recall_first (P 0,7812, R 0,8203, nsys 668). |
| A5 | g03 "Event-F1 theo dung sai biên" | 06 "## Các thế hệ SED" (đoạn SED v1) hoặc "Event-F1 khoảng 0,30" | Đường: collar 0,2/0,5/1/2 s, mỗi run một đường, tô màu nhánh A/B/C | `collar_sensitivity_20260924.json`: 8 run (`sed_polyphonic_20260923T173234Z` = nhánh A; 3 run B; 4 run C), mỗi run `[{collar_s, f1, precision, recall}]` | Không (chỉ một câu trong text: 0,062 → 0,185) | S | Đây là SED v1, test 142 bản ghi, thời kỳ trước LBR. Muốn thêm hệ cuối thì chỉ có 2 điểm (0,2 s và 1 s) từ `calibration` → vẽ panel riêng, không nối chung đường. Gán nhánh cho run: đối chiếu `rq1_multiseed_clean_20260924.json` `runs`. |
| A6 | g24 "Vì sao truy hồi kết hợp thua: phân rã 705 cặp liên quan" | 06 "## RQ3" (đoạn "Ba điều cần đọc cùng nhau") | Cột chồng theo kho (f2/B0/V2/V3): hit, ngoài top-10, SED bỏ sót; thêm `sed_false_match` | `retrieval_failures_test_20261124.json` `results.<kho>.by_group.{all,duration,multi_class,single_class,temporal}.{hit, beyond_top10_or_miss, sed_miss, sed_false_match, retrieved}`; `parser_vs_gold.{n,different}` | Chỉ một số trong text (349/705) | S | B0: 261 + 95 + 349 = 705; f2: 277 + 78 + 350 = 705; V2: 253 + 71 + 381 = 705; V3: hit 417, false match 138, retrieved 555. Tập kiểm tra, bộ lọc chuẩn. Phân tích này được thực hiện sau khi đã thấy kết quả test (06 đã nói). |
| A7 | g22 "nDCG@10 theo chế độ và kho, kèm độ đúng bộ lọc" | 06 "## RQ3" (cạnh tbl:rq3final, tbl:rq3paired) | Cột nhóm có thanh KTC; ký hiệu/nhãn độ đúng bộ lọc trên cột vector | `final_numbers_20261110.json` `rq3.<kho>.ndcg10_gold.{structured_only/en, vector_only/en, hybrid/en, hybrid/vi}.{estimate,lower,upper}` (bọc `{value,…}`); `rq3_modes_20261123.json` `systems.<kho>.filter_exactness.{structured_only, vector_only, hybrid}` | Có: f05, f05b | S | KTC chồng nhau giữa các kho (06 đã nói), không tô "tốt nhất". Độ đúng bộ lọc của vector khoảng 0,27 (V3 0,493) là ý chính cần hiện. |
| A8 | g17 "Mô tả so với danh sách dự đoán và so với nhãn gốc" | 06 "## RQ2" (đoạn "Mô tả so với nhãn gốc") | Dumbbell: mỗi (hệ SED × cách sinh) một hàng, hai điểm vs_pred → vs_gt; hai panel ảo giác / bỏ sót | `caption_vs_gt_dev_20261124.json` `results["<hệ>/<cách>"].{e2e_vs_pred, e2e_vs_gt}.{hallucination_rate, omission_rate}.{estimate,lower,upper}` (16 tổ hợp; f2 có thêm `oracle`) | Có: tbl:captiontiers (f04b) | S–M | Tập phát triển (134), không phải test. Ý chính: so với nhãn gốc bỏ sót khoảng 0,34–0,42 ở f2/B0/V2 cho mọi cách sinh. |
| A9 | g18 "Bộ đo ảo giác bắt được những gì" | 06 "## RQ2" (đoạn "Giới hạn của bộ đo") | Cột ngang theo kiểu chèn lỗi + panel theo nguồn âm ngoài hệ lớp | `checker_sensitivity_dev_20261124.json` `pooled.by_kind.{swap_canonical, swap_synonym, insert_class, insert_oov}.{caught,n,rate}`; `pooled.by_oov_source.<cụm>.rate`; theo cách sinh: `results.<cách>.by_kind` | Không (chỉ text) | S | swap_canonical 1859/1860, swap_synonym 1860/1860, insert_class 2144/2144, insert_oov 1336/2144 = 0,623. Theo nguồn ngoài hệ lớp: "a hammer striking", "a clock ticking", "a phone vibrating" = 0; "a cat meowing" 0,985; còn lại 1,0. Dev. |
| A10 | g25 "Chế độ bổ sung: mức tăng nDCG@10 ghép cặp và thắng/hòa/thua" | 06 "### Chế độ bổ sung" (cạnh r13) | Forest Δ (backfill−vector, backfill−hybrid) × 4 kho × {gold,parsed} × {en,vi} + cột chồng thắng/hòa/thua | `retrieval_backfill_test_20261124.json` `results["<kho>/<gold|parsed>/<en|vi>"].summary.paired_ndcg@10.{"backfill−vector_only","backfill−hybrid"}.{estimate,lower,upper,p_permutation,win,tie,loss}`; `summary.mean.backfill.tier1_share` | r13 có giá trị trung bình, không có KTC | S–M | Ví dụ B0/gold/en: backfill−vector +0,0419 [+0,0194; +0,0691], thắng/hòa/thua 16/80/1; backfill−hybrid +0,1165, 41/56/0. JSON còn khóa `rrf−vector_only` (chế độ RRF) mà bản gọn không mô tả → bỏ hoặc chú thích. |
| A11 | g08 "PSDS phụ thuộc lưới ngưỡng" | 06 đoạn "**PSDS.**" hoặc Phụ lục B (cạnh f06) | Cột nhóm: PSDS-1/PSDS-2 × {lưới tuyến tính/cũ, lưới log} × {B0, V2, V3} | `final_numbers_20261110.json` `sed.rows.B0.{psds_linear, psds_log}`, `sed.rows.lbrv2_f1.{psds_old_grid, psds_log}`, `sed.rows.lbrv3_f1/lbrv3_recall_first.{psds_old_grid, psds_log}`; `lbr_psds_grid_20261110_annotated.json` `results[].curves.<lưới>.{n_points, events_at_lowest_threshold, boxes_never_included}` | Có một phần: f06 (Phụ lục), text 06 | S | B0 tuyến tính 0,3131/0,7310, log 0,3061/0,7452; V2 lưới cũ 0,2146/0,2960 → log 0,3512/0,6116. Lưới cũ cắt V2: 542 hộp không bao giờ được tính. **Không** dùng PSDS trong `evaluation_phase_lbr_annotated.json` hay trong sổ test vì đó là số lưới cũ. |
| A12 | g10 "F1 theo lớp của mô hình phân loại DataSEC" | 06 "## Mô hình phân loại DataSEC" | Cột ngang 22 lớp, nhãn n kiểm tra; lớp n < 10 vẽ rỗng | `report/tables/m02_classifier_per_class.md` (Đúng/tổng, F1), sinh từ `per_class_metrics_datasec_20260923.md`; tổng hợp: `ml/runs/classifier_datasec_20260923T121808Z/metrics.json` | Có: m02 (Phụ lục) | S | Nguồn ở dạng bảng MD, không có JSON → hoặc parse MD, hoặc đọc `metrics.json` (xem cấu trúc trước khi dùng). Lớp n < 10 không có F1. |
| A13 | g13 "SED v2: đóng góp của từng thay đổi (CV trên dev)" | 06 "## Các thế hệ SED" (đoạn SED v2) | Cột có thanh sd: 3 seed v2 đủ, bỏ độ phân giải (/64), trần pos_weight 50, bỏ tăng cường, tham chiếu v1 | `sed_v2_ablation_20260926.json` `full[]`, `ablations[]`, `references[]` → `{label, cv_mean, cv_sd}` | Có ở bảng nháp `docs/thesis/tables/05_sed_v2_ablation.md` (bản gọn không dùng) | S | Dev CV, không phải test. Giá trị: 0,1900/0,2096/0,2169 (đủ), 0,1060 (pool /64), 0,1773 (trần 50), 0,1968 (bỏ tăng cường), 0,1538 (ensemble C v1). Text nói "−0,0840". Tệp ghi `git.dirty=true`. |
| A14 | g14 "Trần event-F1 do độ phân giải thời gian và phân rã lỗi SED v1/v2" | 06 "## Các thế hệ SED" (đoạn SED v1) hoặc 04 "## Mô hình phát hiện sự kiện" | Panel trái: đường trần theo cỡ khối (0,01–1,28 s, log), đánh dấu 0,08 s (v2) và 0,64 s (CNN14); panel phải: cột chồng 886 sự kiện dev (khớp/lệch biên/bỏ sót) v1 và v2 | `sed_ceilings_20260926.json` (v1) và `sed_ceilings_v2_20260926.json`: `resolution_ceiling[].{block_s, event_f1, event_f1_collar_1s}`; `system.{n_reference, n_collar_match, n_overlap_but_boundary_miss, n_deleted, event_f1, event_f1_onset_only, event_f1_offset_only, segment_f1_1s}`; `human_agreement` | Một phần ở m03 (bản gọn không dùng) | S | Trần: 1,0 đến khối 0,32 s; 0,6294 ở 0,64 s; 0,3032 ở 1,28 s (collar 1 s: 0,9966; 0,9549). Trần tính từ nhãn, giống nhau ở hai tệp. Phân rã: v1 112/417/357, v2 148/377/361 (dev, 886 sự kiện). |

**Tầng B: kỹ thuật và phân tích (Ch.3–Ch.6)**

| # | ID / tiêu đề đề xuất | Đích trong gon_src | Loại | Nguồn dữ liệu và khóa | Đã có ở bảng? | Công | Lưu ý |
|---|---|---|---|---|---|---|---|
| B1 | g23 "nDCG@10 theo nhóm câu hỏi" | 06 "## RQ3" (cạnh tbl:rq3groups) | Heatmap 4 kho × 4 nhóm, hai panel hybrid / vector (hoặc ô hiệu) | `rq3_modes_20261123.json` `systems.<kho>.by_group.{structured_only,vector_only,hybrid}.{duration,single_class,multi_class,temporal}` | Có: f05c | S | Số câu theo nhóm: temporal 30, multi_class 27, duration 22, single_class 21 (`data/manifests/retrieval_queryset_v2.json`); 97 câu được chấm. |
| B2 | g20 "Mô tả gộp: ngắn hơn, và nhãn 'độ tin cậy thấp' có nghĩa" | 06 "## RQ2" (đoạn "Mô tả gộp theo lớp") | Panel trái: độ dài trung bình theo mẫu so với gộp theo hệ; panel phải: tỷ lệ đúng của mệnh đề có/không có nhãn | `grouped_captions_dev_20261124.json` `results.<hệ>.{template,grouped}.chars_mean`, `.chars_max`; `results.<hệ>.hedging.{hedged, hedged_correct, plain, plain_correct, estimate, lower, upper}` | Không | S | V3: 400,4 → 119,0 ký tự; mệnh đề có nhãn đúng 17/98, không nhãn 202/228; hiệu 0,712 [0,628; 0,796]. Ngưỡng nhãn chọn trên chính tập dev này (trong mẫu). Ảo giác so với nhãn gốc theo lần nhắc (0,178) khác theo lớp (0,240) → dùng chỉ số theo lớp. |
| B3 | g27 "Bộ phân tích câu hỏi: độ đúng theo nhóm và cái giá trên nDCG" | 06 "### Bộ phân tích câu hỏi" (cạnh tbl:parser) | Cột độ đúng hoàn toàn theo nhóm × {mẫu, diễn đạt lại}; panel 2: nDCG kết hợp gold vs parsed theo kho | `query_parser_20260928.json` `predictions[].{dataset, group, exact}` (đếm), `summary.{template,paraphrase}`; `final_numbers_20261110.json` `rq3.<kho>.ndcg10_parsed_hybrid_en` so với `ndcg10_gold["hybrid/en"]` | Có: tbl:parser (10_parser_l2) | S | Đếm từ `predictions` là tổng hợp lại dữ liệu đã lưu, phải khớp `summary` (0,855 / 0,925). Ví dụ mẫu: duration 38 đúng / 6 sai. |
| B4 | g26 "Chất lượng câu trả lời theo kho" | 06 "## RQ3" (đoạn "**Câu trả lời.**") | Cột: số câu trả lời được /97, tỷ lệ trích dẫn đúng; ghi chú tỷ lệ khẳng định thiếu bằng chứng = 0 | `final_numbers_20261110.json` `rq3.<kho>.answers_hybrid_en.{n, answered, cited_relevant_share, unsupported_claim_rate, contract_ok}` | Có: f05 | S | V3 95/97, trích dẫn đúng 0,712; B0 0,915 (06). Số 0 không phải "tốt hơn" mà là hệ quả cấu tạo. |
| B5 | g28 "RQ1: DataSEC giúp hội tụ và nhận dạng, không giúp định vị" | 06 "## RQ1" | Panel trái: AP khung macro theo epoch (1, 3, 5, 10, 30) B so với C; panel phải: hiệu C−B theo chỉ số kèm "C > B ở x/9 cặp" | `rq1_mechanism_20261008_lf.json` `branch_means.{B,C}.selected_epochs.<epoch>.{macro_average_precision, macro_f1, loss}`; `comparison.<chỉ số>.{delta_c_minus_b, c_gt_b_pairs, total_pairs}` | Không | S | Dev, 134 bản ghi, 3 run mỗi nhánh. AP epoch 1: B 0,391, C 0,510. Hiệu: segment_f1_1s +0,027 (9/9), event_f1_collar_1s −0,0066 (4/9). Đã có PNG tự sinh `docs/measurements/rq1_mechanism_20261008_lf.png` (kiểu mặc định, cần vẽ lại cho đồng bộ). |
| B6 | g06 "Loại lỗi SED trên tập kiểm tra: hệ cơ sở và LBR chính" | 06 "## LBR và hệ thống cuối" | Cột chồng: deletion, merging, fragmentation, confusion, insertion | `…/evaluation_phase_o_annotated.json` `error_totals` (B0: deletion 344, merging 25, fragmentation 11, confusion 6, insertion 6); `…/evaluation_phase_lbr_annotated.json` `error_totals` (V2: 361/14/6/12/5); `n_events_estimate`, `n_error_instances` | Không | S | V3 không có `error_totals` (chỉ có `points`) → chỉ hai hệ. Đếm của bộ phân tích lỗi, không phải FN của event-F1 (mid-term review đã ghi deletion chẩn đoán ≠ FN). |
| B7 | g07 "F1 theo đoạn 1 s theo lớp: cái giá của LBR" | 06 "## LBR và hệ thống cuối" (cạnh r07) | Dumbbell 21 lớp B0 → V2 | `…/evaluation_phase_o_annotated.json` và `…/evaluation_phase_lbr_annotated.json` `application_metrics.segment_f1_1s.per_class` | Không (f09 chỉ có event-F1) | S | Có NaN (vd. `cat_fights_and_moans` ở B0) → bỏ hoặc đánh dấu. Tổng: 0,7260 → 0,5965. V3 có `intersection.per_class` trong `lbr_extra[0].points.*.all` nhưng không có event-F1 theo lớp. |
| B8 | g11 "Biểu đồ độ tin cậy của mô hình phân loại sau hiệu chuẩn nhiệt độ" | 06 "## Mô hình phân loại DataSEC" | Reliability diagram 15 bin + cột số mẫu; chú thích ECE trước/sau | `ece_datasec_20260923.md` bảng "Test reliability bins after dev-only temperature scaling" (Bin, Confidence, Accuracy, Items); T = 1,5681; ECE 0,033190 → 0,056394 | Chỉ text | S | **Chỉ có bin sau hiệu chuẩn**, không có bin trước → không vẽ được hai đường. Có sẵn PNG `docs/measurements/ece_datasec_20260923.png` (kiểu mặc định). |
| B9 | g31 "Mức đa âm theo thời gian ở ba tập" | 03 "## Hai bộ dữ liệu" hoặc "## Các lớp âm thanh" | Cột chồng 100%: 0/1/2/≥3 sự kiện cùng lúc | `data_profile_20261008_lf.json` `coverage_by_split.<split>.{counts, fractions}` (lưới 0,1 s; chỉ số mảng = số sự kiện đang hoạt động, cắt ở 3, theo `scripts/report_data_profile.py::grid_coverage`) | Không | S | Train 31,1%/65,3%/3,6%/0,09%; dev 31,5/61,9/5,9/0,75; test 26,4/67,4/6,1/0,13. Tệp ghi `git.dirty=true` (r01/r02 đã dùng cùng tệp). Đếm cả sự kiện cùng lớp. |
| B10 | g33 "Tìm bản trùng tầng 3: độ tương đồng và độ dài chồng nhau" | 03 "## Quy trình chuẩn bị dữ liệu" (D3, cạnh tbl:leakage) | Scatter (overlap_s, log) × similarity của 1.766 cặp review; vạch 0,85/0,95 và 3 s; 35 cặp xuyên bộ tô theo quyết định | `data/manifests/review_pairs.csv` (`tier, similarity, overlap_s, verdict`, 1.766 dòng); `data/manifests/review_worksheet.csv` (35 dòng, `similarity, overlap_s, decision`); ngưỡng ở `data/manifests/duplicate_audit.json` `thresholds` | Có: tbl:leakage (02_leakage_d3_d4) | M | Không có phân bố cặp dương/âm của bước hiệu chuẩn (chỉ có số tóm tắt dương min 1,0000, âm max 0,9205) → không vẽ được histogram hiệu chuẩn. `duplicate_audit.json` ghi `split_cohesion_pairs` 1.731 (trước ADR-0012), còn `split_cohesion_pairs.csv` hiện có 109 cặp. |
| B11 | g34 "Hai lần gán nhãn trên 8 cặp bản ghi giống hệt" | 03 "## Nhãn thiếu và độ nhất quán của nhãn" | Cột ngang theo cặp: số biên trong dung sai / tổng; điểm độ lệch biên lớn nhất (log) | `annotation_consistency_20260923.md` bảng cặp: 20/24, 8/8, 4/12, 26/38, 0/2, 9/10 (tổng 67/94); lệch lớn nhất 0,46/0,19/5,46/0,40/12,72/0,65 s; 2 cặp bất đồng lớp (S-0397/S-0585, S-0062/S-0198) | Chỉ text | S | n = 8 cặp; chỉ MD, không có JSON → parse bảng MD. |
| B12 | g38 "Chọn hậu xử lý trên dự đoán ngoài mẫu: lưới cSEBB và ngưỡng chung" | 04 "## Từ xác suất đến sự kiện trong hệ thống" | Heatmap τ (0,32/0,48/0,64/0,96) × kiểu gộp (abs 0,15/0,2/0,3; rel 1,5/2/3), ô = CV mean; panel phụ: θ chung với g_max p50 so với p25 | `ml/runs/sed_served_B0_20261107T175659Z/sebb_cv_selection_annotated.json` `cv.<config>.{params, mean, sd, folds}` (30 cấu hình), `selected`; `ml/runs/sed_oof_B0_h5_20261008T130849Z/postproc_cv_selection_annotated.json` `cv.{"global|50","global|25"}` | Không | S | Tốt nhất `tau0.32_abs0.3` 0,2336 ± 0,0227 (đang phục vụ); θ chung p50 0,1571 so với p25 0,2102. Dữ liệu ngoài mẫu 564 bản ghi, chính dữ liệu dùng để chọn → nói "trong vòng chọn". |
| B13 | g37 "Giới hạn độ dài suy từ tập huấn luyện, theo lớp" | 04 "## Từ xác suất đến sự kiện trong hệ thống" (đoạn **Ngưỡng**) | Dumbbell log: d_min, g_max theo lớp, cạnh trung vị độ dài sự kiện | `ml/runs/sed_oof_B0_h5_20261008T130849Z/postproc_cv_annotated.json` `per_class.<lớp>.{d_min_s, g_max_s, median_w, n_train_events, n_train_gaps}`; trung vị độ dài: `data_profile_20261008_lf.json` `poly_by_class_split[split=train].quantiles["0.5"]` | Không | S | Tệp này ghi `threshold_mode: global` (θ 0,9) và g_max theo percentile đã chọn; nếu hệ phục vụ dùng cSEBB thì d_min/g_max vẫn là phần prior, cần ghi rõ prior thuộc họ θ. |
| B14 | g45 "Thời gian tải lên + phân tích theo độ dài âm thanh (CPU)" | 05 "## Độ trễ" (cạnh tbl latency f13) | Scatter + đường RTF tham chiếu | `latency_lbrv3_20261123.json` `uploads[].{id, duration_s, elapsed_s, rtf, memory, skipped}`; `elapsed_s/rtf/query_s.{median,p95,max}` | Có: f13 | S | 12 lượt, 2 lượt `skipped` (S-0049, S-0713) → n = 10, độ dài 3,4–179,6 s, thời gian 0,99–11,96 s. Có một điểm lệch: S-0384 (108 s) mất 10,37 s, S-0480 (124 s) mất 7,90 s. `official=false`, `git.dirty=true`. |
| B15 | g41 "LBR đi được bao nhiêu quãng tới trần sửa biên ±1 s" | 06 "## LBR và hệ thống cuối" (cạnh tbl:lbrcontext) | Cột ngang có KTC: B0, θ theo lớp, dịch onset, LBR V1, V2, V2 trên P1×3, trần oracle 0,5/1/2 s | `lbr_context_20261123.json` `rows.<tên>.{micro,macro}`, `deltas.*.{estimate,lower,upper}`, `exploratory.{per_class_lambda, global_onset_shift}`, `oracle_ceiling_1s`; `lbr_diagnosis_20261109.json` `oracle.{0.5,1,2}` = 0,3703/0,4641/0,5230 | Có: f10 | S | OOF 564. "Thăm dò" (λ theo lớp 0,2335, dịch onset 0,2469) là số từ script nháp được đưa vào measurement; trần oracle là cận trên giả định, không phải hệ thật. `lbr_context` ghi `git.dirty=true`. |

**Tầng C: phụ lục và bằng chứng vận hành**

| # | ID / tiêu đề đề xuất | Đích trong gon_src | Loại | Nguồn dữ liệu và khóa | Đã có ở bảng? | Công | Lưu ý |
|---|---|---|---|---|---|---|---|
| C1 | g09 "Chẩn đoán PSDS: TPR trung bình tại các mức eFPR" | 90 Phụ lục B (cạnh f06_psds) | Đường TPR theo eFPR {5,10,30,60,100} cho v1, v2, f2, B0; hai lưới | `psds_diagnosis_20261110_annotated.json` `results.<hệ>.grids.{linear,log}.scenarios.{psds_1,psds_2}.{psds, mean_tpr_at, per_class_auc}`; `hypotheses.hypotheses.{H1,H2,H3}` | Có: f06 | M | Dev 134 bản ghi. Chỉ có TPR tại 5 điểm, không có cả đường ROC. Ví dụ B0 tuyến tính PSDS-1: TPR 0,500 / 0,528 / 0,549 / 0,557 / 0,557. |
| C2 | g16 "Vòng chọn hệ mốc: CV trên dev ± sd và micro trên tập kiểm tra" | 90 Phụ lục B (cạnh bảng 06_s13 và r08) | Dumbbell / hai cột điểm có thanh lỗi cho 11 ứng viên | `s13_ranking_annotated_20260928.json` `ranking[].annotated.score.{mean,sd,folds}`; `s13_test_20261018.json` `results[].{label, micro, micro_ci_lower, micro_ci_upper, macro, cv_rank}` | Có: 06_s13_ranking_test, r08 | M | Ứng viên a, b, c đã chạm test trước vòng chọn (`s13_selection_20261018.json` `test_state_before_selection`) → đánh dấu. KTC chồng nhau, không tô thắng. |
| C3 | g19 "Từ điển cụm từ so với người đọc (60 mô tả)" | 06 "Giới hạn của bộ đo" hoặc Phụ lục | Cột P/R + ma trận 2×2 cờ ảo giác | `caption_mention_agreement_20260925.json` `mentions.{precision, recall, tp, fp, fn}`, `over_specific.{precision,recall}`, `hallucination_flag.*`, `metric_bias.*` | Chỉ text | S | n = 60, run v1 nhánh B (`sed_polyphonic_20260924T054531Z`), test. P 0,896, R 0,936; cờ ảo giác: 0 cùng có, 2 chỉ từ điển, 2 chỉ người, 56 cùng không. |
| C4 | g46 "Độ khớp giữa hệ phục vụ và hệ đã đo (CUDA)" | 05 "## Độ trễ" hoặc Phụ lục | Histogram `prob_max_abs` theo bản ghi + cột sự kiện trùng / trong 1 khung / trong dung sai | `inference_parity_sed_lbr_b0v3_20261110t042337z_recall_first_cuda_20261110.json` `rows[].prob_max_abs` (142), `summary.{n_events 692, n_served_events 693, n_shared_events 573, n_within_frame 665, n_within_collar 691, prob_max_abs 0,00203}` | Có một phần: 11_serving_parity (bảng nháp, bản gọn không dùng) | S | So output đã đóng băng trên 142 bản ghi kiểm tra, **không** tính chỉ số. Bản CPU có tệp `inference_parity_cpu_*`, `inference_parity_v2_cpu_*` cho hệ cũ. |
| C5 | g50 "Sổ chạy và sổ dùng tập kiểm tra" | 90 Phụ lục (cạnh f14, f07) hoặc 06 "Mức tin cậy" | Cột ngang theo loại run; cột ngang theo loại lượt đo trên test | `run_registry_20261123.json` `by_task.<task>.n` (tổng 218: sed_polyphonic 103, sed_rewindow 51, sed_ensemble 25, sed_oof 13, retrieval_index 11, classifier 8, …); `test_ledger_20261124.json` `sed` (42 lượt), `other.<nhóm>` (Caption 35, Retrieval/câu trả lời 20, Ablation SED trên test 13, Parity 8, Caption lớp gộp 5, LBR PSDS 3, Classifier 2) | Có: f14, f07 | S | Trong sổ test, PSDS của lượt LBR là số lưới cũ (0,2146/0,2960) → không vẽ PSDS từ sổ. |
| C6 | g35 "DataSEC bản 3 và bản 4 theo lớp" | 03 "## Hai bộ dữ liệu" | Cột ghép đôi 22 lớp (thang log) | `datasec_v4_diff_20261008_lf.json` `v3.by_class`, `v4.by_class`, `v3/v4.{files,hours}`, `removed_paths` (756) | Không | S | 5.048 tệp/23,71 h → 4.292 tệp/17,41 h; 756 tệp bị bỏ, đều thuộc Music theo text Ch.3 (cần đếm lại theo lớp từ `by_class` khi vẽ). Đề tài dùng bản 3. |
| C7 | g42 "Đường huấn luyện mô hình phân loại DataSEC" | 04 "## Mô hình phân loại trên DataSEC" hoặc Phụ lục (cạnh r03) | Hai panel: loss; macro-F1 lớp gộp và tỷ lệ nhất quán, train và validation, 12 epoch | `ml/runs/classifier_datasec_20260923T121808Z/logs/history.json` `epochs[].{train,validation}.{loss, coarse_macro_f1, subclass_macro_f1_all, subclass_macro_f1_supported, parent_consistency_rate}` | Không | S | Run khóa chính thức, `git.dirty=false`. Epoch 1: validation macro-F1 0,590. |
| C8 | g12 "Quét hệ số nhất quán λ_cons" | 04 "## Mô hình phân loại trên DataSEC" | Đường 4 điểm λ ∈ {0; 0,25; 0,5; 1}: macro-F1 dev, nhất quán, lớp con n≥10; đánh dấu "bị loại" | `consistency_sweep_datasec_20260923.md` (bảng λ_cons, Dev coarse macro-F1, Dev parent-consistency, Dev subclass macro-F1 (n≥10), Guardrail) | Không | S | Dev; chỉ MD. λ = 0,5 được chọn qua luật có rào (không phải macro-F1 cao nhất: 0,25 có 0,8431). Cần giải thích luật để hình không gây hiểu nhầm. |

**Dự phòng (khi còn chỗ)**: g15 tách riêng phân rã lỗi dev v1/v2 khỏi A14; g21 BLEU-4/CIDEr theo cách sinh
(`caption_ngram_*_test_annotated.json` `scores["<cách>/e2e"].{bleu_4, cider}`; chỉ đo độ giống văn mẫu); g29 RQ1 theo
độ dài/đa âm (`rq1_duration_polyphony_20260924.json`, v1, test 142, nhóm <1 s chỉ 33 sự kiện); g30 19 lớp Việt Nam so với
21 lớp (`evaluation_phase_lbr_annotated.json` `lbr.points.*.vn`, `lbr.baseline.vn`); g32 độ dài bản ghi theo tập và độ
dài đoạn DataSEC (`data_profile…` `recording_duration_by_split`, `datasec_duration`); g36 số sự kiện đơn âm/đa âm theo lớp
(`data_profile…` `mono_vs_poly.by_class`); g39 F1 quanh mép lưới θ (`threshold_grid_edge_20260925.json`, dev v1); g40 độ
phân tán θ theo lớp (`ml/runs/sed_polyphonic_20260924T054531Z/threshold_ablation.json` `per_class.thetas`, dev); g43 cặp
lớp hay bị nhầm (`confusable_pairs_clean_dev_20260925.json` `pairs[].{pair,total,a_to_b,b_to_a}`, dev v1, 1.482 lượt);
g47 thời gian E2E qua các phiên bản phục vụ (`demo_{v2,f2,B0,lbrv3}_e2e_*.json` `upload_elapsed_s` 5,11/2,01/1,55/3,72 s,
`rag_elapsed_s`; n = 1 mỗi phiên bản, bản ghi nguồn khác nhau, không phải benchmark); g48 VRAM theo batch
(`track2_t0_frame_mn_20260927.json` `train_step_peak_mb` 8→48: 854,5–4705,2 MB trên 8192 MB); g49 khối lượng mã theo phần
(`workload_20261124.json` `python_lines`, `frontend_lines`, `test_functions`); pilot learning rate T2a/T2b
(`pilot_lr_t2a_20260927.json`, `pilot_lr_t2b_20260928.json` `pilots[].{learning_rate, curve}`).

### Inferences
- Chương 6 có thể tăng từ 4 lên khoảng 18–20 hình chỉ với tầng A và một phần tầng B; mỗi bảng chính (f04b, f05, f05b,
  f05c, f10, f11, f13) có một hình bổ trợ không lặp số mà nhấn ý chính bằng hình (khoảng tin cậy, độ đúng bộ lọc, phân
  rã lỗi).
- Nên ưu tiên các hình thể hiện **khoảng tin cậy và cái giá**, vì đó là chỗ bản gọn nhấn mạnh trong lời (KTC chứa 0,
  bỏ sót, độ đúng bộ lọc), còn bảng chỉ cho số.
- Phần lớn hình mới là công S vì dùng lại được `_style`, `_save`, `_value`, `SYSTEM_NAMES`, `METHOD_NAMES` trong
  `scripts/build_research_figures.py` và cơ chế đổi nhãn `--labels` khi xuất vào `report/gon_figures/`.

### Gaps
- Không tìm thấy JSON gom điểm tầng S của P2/P3/P4 (0,1999/0,2225/0,2402) và của O-D (0,2509); các số này có trong
  PAPER_NOTES S61–S63 và CLAUDE.md, có lẽ nằm trong `evaluation_cv_annotated.json` của từng run `sed_polyphonic_20261108T*`
  và `20261009T153325Z` — chưa mở để xác nhận.
- Không có bin reliability **trước** hiệu chuẩn, không có histogram cặp dương/âm của hiệu chuẩn tầng 3, không có event-F1
  theo lớp cho LBR ứng dụng (V3), không có đường ROC đầy đủ cho PSDS (chỉ TPR tại 5 mức eFPR).
- Số test cho ablation A2/A3/A5 (per-class θ giảm 39–48% từ dev sang test) không thấy ở dạng JSON trong
  `docs/measurements/` (các `threshold_ablation.json` trong `ml/runs` chỉ có số dev); chưa tìm tệp MD sinh bởi
  `report_threshold_ablation`.

---

## Câu hỏi 1 — Dữ liệu (Chương 3): phân bố lớp, độ dài, tập chia, rò rỉ/trùng, đồng thuận nhãn, mức đa âm nằm ở đâu?

### Takeaway
Gần như mọi thống kê dữ liệu nằm trong một tệp: `data_profile_20261008_lf.json` (14 khóa). Kiểm trùng và rò rỉ nằm ở
`data/manifests/duplicate_audit.json`, `review_pairs.csv`, `review_worksheet.csv` và `dedup_20260923.md`. Độ nhất quán
gán nhãn chỉ có ở dạng MD (`annotation_consistency_20260923.md`). r01 và r02 mới dùng 3 trong 14 khóa của
data_profile; mức đa âm, độ dài bản ghi, khoảng cách cùng lớp, đơn âm/đa âm và nhãn thiếu chưa được vẽ.

### Cited Findings
- `data_profile_20261008_lf.json` có các khóa: `recording_duration_by_split`, `poly_by_class_split` (63 dòng = 21 lớp × 3 tập), `poly_event_duration`, `coverage_by_split`, `same_class_gaps`, `gaps_by_split`, `missing_poly_gt`, `identical_pairs` (8), `train_windows`, `mono_vs_poly`, `datasec_duration`, `datasec_by_class`; ghi `git.dirty=true`, revision `a700e07` — [data_profile](../../docs/measurements/data_profile_20261008_lf.json)
- r01 dùng `datasec_by_class` và `poly_by_class_split`; r02 dùng `poly_by_class_split[split=train].quantiles` — [build_research_figures.py](../../scripts/build_research_figures.py)
- Mức đa âm (lưới 0,1 s, chỉ số 0/1/2/≥3 sự kiện đang hoạt động): train 0,3105/0,6531/0,0355/0,00088; validation 0,3146/0,6193/0,0586/0,0075; test 0,2641/0,6740/0,0606/0,0013 — [data_profile](../../docs/measurements/data_profile_20261008_lf.json); ý nghĩa chỉ số theo `grid_coverage` — [report_data_profile.py](../../scripts/report_data_profile.py)
- Độ dài bản ghi trung bình: train 93,35 s (n 438), validation 101,47 s (137), test 87,86 s (142); đoạn DataSEC trung vị 8,72 s, p5 0,59 s, p95 49,91 s, max 481,5 s — [data_profile](../../docs/measurements/data_profile_20261008_lf.json)
- Sự kiện đa âm: 4.034, trung bình 12,46 s, trung vị 5,80 s, 194 sự kiện dưới 1 s (4,81%); khoảng trống cùng lớp 2.693, trung vị 4,23 s, 252 dưới 1 s — [data_profile](../../docs/measurements/data_profile_20261008_lf.json)
- Nhãn thiếu: train 8 bản ghi (3.562 s), validation 3 (1.410 s), test 3 (1.008 s), kèm số sự kiện đơn âm theo lớp — [data_profile](../../docs/measurements/data_profile_20261008_lf.json); 703/717 bản ghi có nhãn đa âm, 14 bản ghi chưa phủ trùng đúng các bản ghi `wind_turbine` — [polyphonic_coverage](../../docs/measurements/polyphonic_coverage_20260927.json)
- Đơn âm và đa âm: 4.034 sự kiện đa âm, 4.309 đơn âm (4.196 thuộc 21 lớp, 3.393 khớp chính xác), có `by_class` — [data_profile](../../docs/measurements/data_profile_20261008_lf.json)
- Kiểm trùng: cặp theo tầng T1 24, T2 24, T3 45.191; 84 nhóm; 3 nhóm xuyên bộ; 1.766 cặp review; 35 cặp xuyên bộ cần duyệt; ngưỡng 0,95/0,85/3 s, ngưỡng ngắn 0,99; rò rỉ 11/5.048 = 0,2179%, dải `minor` — [duplicate_audit.json](../../data/manifests/duplicate_audit.json)
- `review_pairs.csv` có 1.766 dòng với cột `left_file_id, right_file_id, tier, similarity, overlap_s, verdict` — [review_pairs.csv](../../data/manifests/review_pairs.csv); `review_worksheet.csv` 35 dòng có `similarity, overlap_s, decision, note` — [review_worksheet.csv](../../data/manifests/review_worksheet.csv); quyết định 10 trùng / 1 không chắc / 24 khác — [dedup_20260923.md](../../docs/measurements/dedup_20260923.md)
- Hiệu chuẩn ngưỡng cho đoạn ngắn: theo độ dài 1,0–2,5 s, cặp dương min 1,000000, cặp âm max 0,866121 → 0,739695 — [short_duplicate_calibration](../../docs/measurements/short_duplicate_calibration_20260923.md)
- Đồng thuận nhãn 8 cặp: biên trong dung sai 67/94; theo cặp 20/24, 8/8, 4/12, 26/38, 0/2, 9/10; lệch lớn nhất 12,72 s (`S-0289`/`S-0500`); 2 cặp bất đồng lớp — [annotation_consistency](../../docs/measurements/annotation_consistency_20260923.md)
- DataSEC bản 3 → 4: 5.048 tệp/23,71 h → 4.292 tệp/17,41 h; 756 đường dẫn bị bỏ, 0 thêm, 0 đổi; có `by_class` cho cả hai bản — [datasec_v4_diff](../../docs/measurements/datasec_v4_diff_20261008_lf.json)
- Tập chia và bảng rò rỉ đã có dạng bảng — [01_data_split.md](../../docs/thesis/tables/01_data_split.md), [02_leakage_d3_d4.md](../../docs/thesis/tables/02_leakage_d3_d4.md)

### Inferences
- Hình đa âm (B9) là bổ sung có giá trị nhất cho Ch.3 vì nó làm rõ vì sao chọn nhãn đa âm, mà hiện bản gọn chỉ nói bằng lời.
- Hình scatter trùng (B10) cho thấy trực quan vì sao ngưỡng phải phụ thuộc độ dài chồng nhau (cặp nhiễu tập trung ở overlap
  ngắn), bổ sung cho tbl:leakage chứ không thay nó.

### Gaps
- Không có tệp chứa phân bố độ tương đồng của 24 cặp dương và 5.000 cặp âm dùng để hiệu chuẩn tầng 3 (chỉ có min/max).
- Đồng thuận nhãn chỉ có MD; chưa thấy JSON.
- `duplicate_audit.json` vẫn ghi `split_cohesion_pairs: 1731` trong khi CSV hiện hành có 109 cặp (sau ADR-0012); hình nào
  dùng số cohesion phải lấy từ CSV và ghi rõ.

---

## Câu hỏi 2 — Phương pháp (Chương 4): ví dụ LBR, đường quét ngưỡng, prior độ dài, cấu hình mel, chế độ truy hồi, độ đúng parser

### Takeaway
Dữ liệu phương pháp đủ cho các hình: trần độ phân giải, lưới cSEBB và ngưỡng chung trên OOF, prior độ dài theo lớp,
điểm vận hành LBR, ngưỡng LBR theo fold, cơ chế RQ1, pilot learning rate và VRAM. **Không có** artifact để vẽ "ví dụ LBR
trước/sau trên một bản ghi" mà không mở dự đoán: `lbr_model.pkl` và NPZ là nhị phân; ví dụ timeline duy nhất là
m05_dev_timeline (dev, đang dùng).

### Cited Findings
- Trần độ phân giải thời gian: khối 0,01–0,32 s → 1,0; 0,64 s → 0,6294 (collar 1 s 0,9966); 1,28 s → 0,3032 (0,9549) — [sed_ceilings_20260926](../../docs/measurements/sed_ceilings_20260926.json), [sed_ceilings_v2_20260926](../../docs/measurements/sed_ceilings_v2_20260926.json)
- Phân rã lỗi dev (886 sự kiện): v1 ensemble C khớp 112, lệch biên 417, bỏ sót 357, event-F1 0,1588, chỉ onset 0,2325, chỉ offset 0,4975, segment 0,6542; v2 148/377/361, 0,2120/0,2708/0,4914/0,6869 — [sed_ceilings_20260926](../../docs/measurements/sed_ceilings_20260926.json), [sed_ceilings_v2](../../docs/measurements/sed_ceilings_v2_20260926.json)
- Sai số biên (4 hệ, dev): onset v1 ensemble C trung vị 0,0 s, IQR −0,39…+0,51 s, trong dung sai 0,302, muộn 0,365, sớm 0,333; posterior khung âm trung vị 0,0078, khung dương 0,771 — [boundary_errors_20260926](../../docs/measurements/boundary_errors_20260926.json)
- Lỗi bỏ sót của B0 trên OOF: `fn_kinds`, `fn_kinds_per_class`, `missed_pmax_histogram`, `onset_error_median_per_class`, trần oracle 0,5/1/2 s = 0,3703/0,4641/0,5230 — [lbr_diagnosis_20261109](../../docs/measurements/lbr_diagnosis_20261109.json) (r05, r06 dùng tệp này)
- Lưới cSEBB của hệ phục vụ B0 (OOF 564, 5 fold theo `leakage_group`): 30 cấu hình; tốt nhất `tau0.32_abs0.3` 0,2336 ± 0,0227, kế đến `tau0.32_rel1.5` 0,2329; cấu hình được chọn `{step_filter_s 0.32, merge_abs 0.3, threshold 0.9}` — [sebb_cv_selection_annotated](../../ml/runs/sed_served_B0_20261107T175659Z/sebb_cv_selection_annotated.json)
- Ngưỡng chung trên OOF: `global|50` 0,1571 ± 0,0102; `global|25` 0,2102 ± 0,0185 (chọn p25) — [postproc_cv_selection_annotated](../../ml/runs/sed_oof_B0_h5_20261008T130849Z/postproc_cv_selection_annotated.json)
- Prior theo lớp suy từ train (`d_min_s`, `g_max_s`, `median_w`, `n_train_events`, `n_train_gaps`; θ 0,9), ví dụ `jet_aircrafts` d_min 3,83 s, g_max 9,83 s, median_w 191; `glass_breaking` 0,90 s / 0,72 s — [postproc_cv_annotated](../../ml/runs/sed_oof_B0_h5_20261008T130849Z/postproc_cv_annotated.json)
- Hệ phục vụ: cửa sổ trượt 5 s, trọng số `triangular:0.3`, 5 mô hình fold — [manifest](../../ml/runs/sed_served_B0_20261107T175659Z/manifest.json)
- Ngưỡng LBR theo fold: V3 `f1` 0,85 và `recall_first` 0,005 ở cả 5 fold (đáy lưới); V2 điểm test `thresholds.{f1: 0.01, recall_first: 0.005}` — [lbr_application_annotated](../../ml/runs/sed_lbr_B0v3_20261110T042337Z/lbr_application_annotated.json), [evaluation_phase_lbr_annotated](../../ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/evaluation_phase_lbr_annotated.json); `lbr_context` ghi `recall_first_threshold_folds_at_floor: 5` — [lbr_context](../../docs/measurements/lbr_context_20261123.json)
- θ quanh mép lưới (dev v1): ensemble B, g_max p25: θ 0,90/0,95/0,97/0,98/0,99 → 0,1266/0,1373/0,1364/0,1127/0,0863 — [threshold_grid_edge](../../docs/measurements/threshold_grid_edge_20260925.json)
- θ theo lớp của run v1 nhánh B trải từ 0,05 (`thunder_fireworks_gunshot`) đến 0,95, θ chung 0,95, chỉ có F1 dev — [threshold_ablation.json](../../ml/runs/sed_polyphonic_20260924T054531Z/threshold_ablation.json)
- Cơ chế RQ1 (dev, 3 run/nhánh): AP khung macro theo epoch 1/3/5/10/30, B 0,391/0,609/0,630/0,652/0,668, C bắt đầu 0,510; hiệu C−B: frame_map +0,019 (8/9 cặp), segment_f1_1s +0,027 (9/9), event_f1_collar_1s −0,0066 (4/9), onset-only +0,0145 (9/9) — [rq1_mechanism](../../docs/measurements/rq1_mechanism_20261008_lf.json)
- Cặp lớp hay bị thay thế (dev, 7 run v1): 6.202 sự kiện tham chiếu, 1.482 lượt thay thế, 153 cặp, có `a_to_b`, `b_to_a`, `total`; 15 cặp giả thuyết — [confusable_pairs](../../docs/measurements/confusable_pairs_clean_dev_20260925.json)
- Mô hình phân loại: 12 epoch, có loss, macro-F1 gộp, lớp con, nhất quán cho train/validation — [history.json](../../ml/runs/classifier_datasec_20260923T121808Z/logs/history.json); quét λ_cons 0/0,25/0,5/1 → macro-F1 dev 0,8375/0,8431/0,8230/0,8169, nhất quán 0,9514/0,9526/0,9583/0,9572, λ = 1 bị rào loại — [consistency_sweep](../../docs/measurements/consistency_sweep_datasec_20260923.md)
- Pilot learning rate: T2b lr 1e-4/3e-4/1e-3, AP epoch 3 = 0,657/0,707/0,681 (chọn 3e-4); T2a 3e-4/1e-3/3e-3 = 0,725/0,737/0,720 — [pilot_lr_t2b](../../docs/measurements/pilot_lr_t2b_20260928.json), [pilot_lr_t2a](../../docs/measurements/pilot_lr_t2a_20260927.json)
- Cấu hình mel: so sánh `logmel_v1` với `logmel_panns_v1` theo tỷ lệ khung (khoảng 2,0) và tương quan bao (0,988–0,998), chỉ vài tệp — [logmel_feature_comparison](../../docs/measurements/logmel_feature_comparison_20260923.md)
- Bộ câu hỏi truy hồi: 100 câu, temporal 30, multi_class 27, duration 22, single_class 21 — [retrieval_queryset_v2.json](../../data/manifests/retrieval_queryset_v2.json)
- Parser: 240 dự đoán có `dataset, group, exact`; theo mẫu duration 38 đúng/6 sai; diễn đạt lại mỗi nhóm 9–10/10 — [query_parser](../../docs/measurements/query_parser_20260928.json)

### Inferences
- Hình lưới cSEBB (B12) và prior độ dài (B13) cho Ch.4 một phần định lượng cho đoạn "Từ xác suất đến sự kiện", hiện chỉ có lời.
- Hình cơ chế RQ1 (B5) giải thích kết quả âm tính bằng số: DataSEC giúp khởi đầu nhanh và nhận dạng theo đoạn nhưng không giúp event-F1 theo biên.
- Ngưỡng `recall_first` của V3 nằm ở đáy lưới ở cả 5 fold: hình điểm vận hành (A4) nên ghi chú điều này, nếu không người đọc tưởng điểm đó là tối ưu bên trong.

### Gaps
- Không có ví dụ LBR trước/sau trên một bản ghi ở dạng JSON; muốn có phải đọc NPZ dự đoán và chạy LBR (đo mới) → loại.
- Cấu hình mel chỉ có bảng so sánh vài tệp; không có artifact "hình phổ mẫu" nào sẵn (vẽ phổ từ WAV train là tính mới nhưng không chạm test; cân nhắc riêng).

---

## Câu hỏi 3 — Kết quả (Chương 6): dữ liệu nào cho các hình kết quả?

### Takeaway
Tệp gốc cho hình kết quả là `final_numbers_20261110.json` (SED, RQ1, RQ2, RQ3, PSDS, demo) và
`evaluation_phase_{o,lbr}_annotated.json` của run B0 cuối (theo lớp, loại lỗi, điểm vận hành, F1 theo đoạn). Các phân
tích ngày 23–24/11 (`calibration`, `lbr_context`, `rq3_modes`, `retrieval_backfill_test`, `retrieval_failures_test`,
`caption_vs_gt_dev`, `checker_sensitivity_dev`, `grouped_captions_dev`) đều có KTC hoặc đếm chi tiết. Tầng C giai đoạn
O/P nằm trong 4 tệp `oof_selection_*`.

### Cited Findings
- `final_numbers_20261110.json`: `sed.rows.{f2,B0,lbrv2_f1,lbrv3_f1,lbrv3_recall_first}` với macro, micro, micro_ci, nsys, nref, intersection_recall/precision, segment_f1_1s, psds_*; `sed.b0_minus_f2`; `rq1.{v1,v2}.{branches, welch_p, bootstrap_c_minus_b}`; `rq2.{template, llm_e2e, llm_oracle}`; `rq3.<kho>.{ndcg10_gold, ndcg10_parsed_hybrid_en, answers_hybrid_en}`; `psds_diagnosis`; `demo`; `git.dirty=false` — [final_numbers](../../docs/measurements/final_numbers_20261110.json)
- Điểm vận hành trên test (139): B0 micro 0,1806, nsys 345, giao nhau P 0,9706; V2 f1 0,2965 / 373 / 0,9545; V2 recall_first 0,2917 / 412 / 0,9451; V3 f1 0,2731 / 395 / 0,9836; V3 recall_first 0,2287 / 668 / 0,7812; F1 theo đoạn 0,7260 / 0,5965 / 0,6652 / 0,7752 / 0,7821 — [evaluation_phase_lbr_annotated](../../ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/evaluation_phase_lbr_annotated.json)
- Loại lỗi: B0 deletion 344, merging 25, fragmentation 11, insertion 6, confusion 6 — [evaluation_phase_o_annotated](../../ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/evaluation_phase_o_annotated.json); V2 361/14/6/12/5 — [evaluation_phase_lbr_annotated](../../ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/evaluation_phase_lbr_annotated.json)
- Bốn cách đo: B0 0,1806/0,3889/0,7260/0,5351–0,9706; V2 0,2965/0,5157/0,5965/0,5108–0,9545; V3 f1 0,2731/0,4652/0,7752/0,6486–0,9836; V3 recall_first 0,2287/0,4190/0,7821/0,8203–0,7812; người 0,5785/0,7603/0,7425 (8 cặp) — [calibration](../../docs/measurements/calibration_20261123.json), [f11_calibration.md](../../report/final_tables/f11_calibration.md)
- Collar (SED v1, test): run nhánh A 0,036/0,068/0,085/0,102 ở 0,2/0,5/1/2 s; run B `054531Z` 0,062/0,132/0,185/0,222; run C `033537Z` 0,066/0,150/0,212/0,242 — [collar_sensitivity](../../docs/measurements/collar_sensitivity_20260924.json)
- Tầng C: TF 0,2136 (Δ −0,0206 [−0,0453; +0,0062]), TFKD 0,2076 (−0,0267 [−0,0522; −0,0004]), ENS_B0_TFKD 0,2305 (−0,0037) — [oof_selection_20261009](../../docs/measurements/oof_selection_20261009.json); OD 0,2052 (−0,0290 [−0,0546; +0,0001]), ENS_B0_OD 0,2303 (−0,0039) — [oof_selection_20261014](../../docs/measurements/oof_selection_20261014.json); P1 0,2344 (+0,0002 [−0,0142; +0,0141]) — [oof_selection_20261108](../../docs/measurements/oof_selection_20261108.json); P4 0,2260 (−0,0082 [−0,0258; +0,0088]) — [oof_selection_20261108_P4](../../docs/measurements/oof_selection_20261108_P4.json)
- LBR trên OOF: V1 +0,0701 [+0,0496; +0,0896]; V2 +0,0990 [+0,0761; +0,1200]; V1 trên P1×3 +0,0847; V2 trên P1×3 +0,1160 [+0,0933; +0,1373] — [lbr_selection_annotated](../../ml/runs/sed_lbr_B0_20261109T172809Z/lbr_selection_annotated.json); V3 +0,0716 [+0,0489; +0,0917], V3 trên P1×3 +0,0816 — [lbr_application_annotated](../../ml/runs/sed_lbr_B0v3_20261110T042337Z/lbr_application_annotated.json)
- Tầng S (dev CV, so với seed T2b tốt nhất 0,2330): TF-KD +0,0449 (4/5 fold), TF +0,0229 (5/5), O-A hop 5 s tam giác +0,0078, t2b +0,0053; ngưỡng sàng lọc chỉ ghi "trong nhiễu fold" cho đa số — [tier_s](../../docs/measurements/tier_s_20261009.json)
- SED v2 ablation (dev CV): xem A13 — [sed_v2_ablation](../../docs/measurements/sed_v2_ablation_20260926.json); v2−v1 test 142: tệp ghi `v1-v2` −0,0536 [−0,0853; −0,0261] — [rq1_multirun_bootstrap_sedv2_vs_v1](../../docs/measurements/rq1_multirun_bootstrap_sedv2_vs_v1_20260926.json)
- S13: 11 ứng viên, CV mean ± sd ± 5 fold; test micro, KTC, macro, PSDS — [s13_ranking_annotated](../../docs/measurements/s13_ranking_annotated_20260928.json), [s13_test](../../docs/measurements/s13_test_20261018.json); ứng viên a, b, c đã chạm test trước khi chọn — [s13_selection](../../docs/measurements/s13_selection_20261018.json)
- RQ1 đa seed: v1 B n 3 (0,0610 ± 0,0048, min 0,0557, max 0,0651), C n 4; v2 có thêm `event_f1_macro` — [rq1_multiseed_clean](../../docs/measurements/rq1_multiseed_clean_20260924.json), [rq1_v2_multiseed](../../docs/measurements/rq1_v2_multiseed_20260929.json) (r09 đã vẽ)
- PSDS: B0 tuyến tính 0,3131/0,7310, log 0,3061/0,7452; V2 lưới cũ 0,2146/0,2960 → log 0,3512/0,6116 — [final_numbers](../../docs/measurements/final_numbers_20261110.json), [lbr_psds_grid](../../docs/measurements/lbr_psds_grid_20261110_annotated.json), [lbr_psds_grid_b0](../../docs/measurements/lbr_psds_grid_20261110_annotated_b0.json); lưới cũ của V2: 412 sự kiện ở ngưỡng thấp nhất, 542 hộp không bao giờ được tính — [lbr_psds_grid](../../docs/measurements/lbr_psds_grid_20261110_annotated.json)
- Chẩn đoán PSDS (dev): `results.<v1|v2|f2|B0>.grids.{linear,log}.scenarios.{psds_1,psds_2}.{psds, psds_alpha_st0, mean_tpr_at, per_class_auc}`; eFPR {5,10,30,60,100}; H1, H3 "đủ điều kiện", H2 "không" — [psds_diagnosis](../../docs/measurements/psds_diagnosis_20261110_annotated.json), [f06_psds.md](../../report/final_tables/f06_psds.md)
- Phân loại DataSEC: bin reliability sau hiệu chuẩn (bin cuối (0,9333; 1] có 432 mẫu, độ tin cậy 0,9847, độ chính xác 0,9745); T = 1,5681; ECE 0,0332 → 0,0564 — [ece_datasec](../../docs/measurements/ece_datasec_20260923.md); F1 theo lớp — [m02_classifier_per_class.md](../../report/tables/m02_classifier_per_class.md)
- RQ2: `e2e.<cách>.<hệ>.{summary, ci}` và `paired.<cách>["<hệ>−<hệ>"]` cho 6 chỉ số; `oracle.<cách>` — [rq2_llm_systems test](../../docs/measurements/rq2_llm_systems_20261110_test_annotated.json) (r10 đã vẽ ba chỉ số)
- Mô tả so với nhãn gốc (dev 134): 16 tổ hợp, mỗi tổ hợp có `e2e_vs_pred` và `e2e_vs_gt` với hallucination/omission/event_precision/event_recall kèm KTC — [caption_vs_gt_dev](../../docs/measurements/caption_vs_gt_dev_20261124.json)
- Độ nhạy bộ đo: xem A9 — [checker_sensitivity_dev](../../docs/measurements/checker_sensitivity_dev_20261124.json); từ điển so với người — [caption_mention_agreement](../../docs/measurements/caption_mention_agreement_20260925.json)
- Mô tả gộp: xem B2 — [grouped_captions_dev](../../docs/measurements/grouped_captions_dev_20261124.json)
- BLEU/CIDEr so với văn mẫu (test 139): V2 constrained/e2e BLEU-4 0,358, CIDEr 3,600; constrained_cover 0,364/3,631 — [caption_ngram_sed_lbr_B0](../../docs/measurements/caption_ngram_sed_lbr_B0_20261109T172809Z_test_annotated.json)
- RQ3: hiệu ghép cặp hybrid−vector và hybrid−structured kèm KTC, độ đúng bộ lọc, nDCG theo nhóm — [rq3_modes](../../docs/measurements/rq3_modes_20261123.json); ví dụ B0 hybrid−vector −0,0746 [−0,1206; −0,0275], độ đúng bộ lọc vector 0,2711
- Chế độ bổ sung: theo kho × {gold,parsed} × {en,vi}, có KTC, p hoán vị, thắng/hòa/thua và `per_query` (97 câu) — [retrieval_backfill_test](../../docs/measurements/retrieval_backfill_test_20261124.json)
- Phân rã lỗi truy hồi: xem A6 — [retrieval_failures_test](../../docs/measurements/retrieval_failures_test_20261124.json)
- Câu trả lời: `answers_hybrid_en.{n, unsupported_claim_rate, contract_ok, answered, cited_relevant_share}` theo kho — [final_numbers](../../docs/measurements/final_numbers_20261110.json)

### Inferences
- Hình forest A1 và A2 là cách gọn nhất để hiện quy tắc của bản gọn "KTC chứa 0 thì không gọi là tốt hơn"; A2 cho thấy trên OOF chỉ các biến thể LBR có KTC nằm hẳn bên phải 0.
- Cặp hình A3 + A4 trả lời trực quan đoạn "Event-F1 khoảng 0,30 là cao hay thấp?" và đoạn "LBR có đánh đổi": cùng một hệ có thể thấp theo biên chặt nhưng cao theo đoạn hoặc theo giao nhau.
- A6 (phân rã lỗi truy hồi) và A8 (mô tả so với nhãn gốc) cùng chứng minh luận điểm Thảo luận "độ đúng chủ yếu do SED", nên nên đặt gần nhau hoặc tham chiếu chéo.

### Gaps
- Không có event-F1 theo lớp của V3, không có `error_totals` của V3.
- Không có số test của ablation A2/A3/A5 dạng JSON (xem Câu hỏi 0).
- RQ2 `oracle` chỉ có trên f2 (tệp `caption_vs_gt_dev` ghi oracle cho f2), hệ khác chỉ e2e.

---

## Câu hỏi 4 — Hệ thống (Chương 5): độ trễ theo bước, số endpoint API, kích thước bảng DB, thời gian demo E2E

### Takeaway
Có số cho độ trễ tải lên theo độ dài (10 lượt), độ trễ truy vấn (5 lượt), thời gian E2E qua 4 phiên bản phục vụ, độ khớp
CUDA/CPU, VRAM theo batch và khối lượng mã. **Không có** độ trễ theo từng bước (SED, LBR, sinh mô tả, ghi DB, embedding)
và **không có** kích thước bảng DB trong artifact; số endpoint API chỉ có ở bảng sinh từ mã (f16).

### Cited Findings
- Độ trễ (CPU, hệ phục vụ B0 + LBR V3 recall_first): 12 lượt tải, 2 lượt `skipped`, n = 10; tải lên + phân tích trung vị 3,89 s, p95 11,96 s; RTF trung vị 0,072, p95 0,294; truy vấn trung vị 0,221 s (n 5); độ dài 3,36–179,63 s; mỗi lượt có `memory` (vd. "1.24GiB / 7.387GiB"); `official=false`, `git.dirty=true` — [latency_lbrv3](../../docs/measurements/latency_lbrv3_20261123.json); lượt bị bỏ khi upload lỗi hoặc trùng — [report_latency.py](../../scripts/report_latency.py)
- Bảng độ trễ đã có — [f13_latency.md](../../report/final_tables/f13_latency.md)
- E2E demo (CPU, n = 1 mỗi phiên bản): v2 5,113 s (2 sự kiện), f2 2,012 s (2), B0 1,552 s (1), LBR V3 3,721 s (3); RAG 0,270/0,250/0,364/0,273 s — [demo_v2_e2e](../../docs/measurements/demo_v2_e2e_20260928.json), [demo_f2_e2e](../../docs/measurements/demo_f2_e2e_20261002.json), [demo_B0_e2e](../../docs/measurements/demo_B0_e2e_20261107.json), [demo_lbrv3_e2e](../../docs/measurements/demo_lbrv3_e2e_20261110.json)
- Độ khớp phục vụ (CUDA, V3 recall_first, 142 bản ghi): đặc trưng trùng 142/142; xác suất lệch tối đa 0,00203, trung vị 0,00051; sự kiện 692 tham chiếu / 693 phục vụ, 573 trùng hệt, 665 trong 1 khung, 691 trong dung sai; 71 bản ghi có sự kiện lệch; có `rows[]` theo bản ghi — [inference_parity V3](../../docs/measurements/inference_parity_sed_lbr_b0v3_20261110t042337z_recall_first_cuda_20261110.json)
- VRAM Frame-MobileNet khi train: batch 8/16/24/32/48 → 854,5/1627,5/2400,2/3185,0/4705,2 MB trên GPU 8192 MB; ước 54,8 s/epoch ở batch 24 — [track2_t0_frame_mn](../../docs/measurements/track2_t0_frame_mn_20260927.json)
- Khối lượng (24/11): 456 commit, 50 ADR, 285 báo cáo đo, Python ml 13.717 / scripts 30.639 / tests 13.920 / services 640 dòng, frontend 1.185 dòng, 938 hàm test, 8 JSON schema, 218 thư mục run — [workload_20261124](../../docs/measurements/workload_20261124.json); bản 23/11 có số nhỏ hơn — [workload_20261123](../../docs/measurements/workload_20261123.json)
- Sổ run theo loại (218): sed_polyphonic 103, sed_rewindow 51, sed_ensemble 25, sed_oof 13, retrieval_index 11, classifier_datasec 8, sed_lbr 2, sed_lbr_oof_events 2, pseudo_labels 1, sed_filtered 1, sed_served 1; có `per_day`, `gpus`, `runs` — [run_registry](../../docs/measurements/run_registry_20261123.json)
- Bảng API sinh từ decorator FastAPI và bảng công nghệ — [f16_api.md](../../report/final_tables/f16_api.md), [f15_tech_stack.md](../../report/final_tables/f15_tech_stack.md)

### Inferences
- Với Ch.5, hình đáng làm nhất là scatter độ trễ theo độ dài (B14): nó cho thấy thời gian tăng gần tuyến tính theo độ dài, điều bảng trung vị/p95 không cho thấy.
- Hình E2E qua các phiên bản (g47) dễ bị đọc như benchmark; nếu dùng phải ghi rõ n = 1 và bản ghi khác nhau.

### Gaps
- Không có độ trễ theo bước trong pipeline (SED / LBR / mô tả / embedding / ghi DB) trong bất kỳ artifact nào đã xem; muốn có phải đo mới.
- Không có kích thước bảng DB, số dòng `events`/`documents` hay dung lượng index trong artifact đã xem; `retrieval_index` runs có thể ghi số document (chưa mở manifest để xác nhận).
- Tệp workload nào sinh bảng f12 (23/11 hay 24/11) chưa kiểm; hình phải dùng đúng tệp đó.

---

## Câu hỏi 5 — Tệp nào là nguồn chuẩn/đóng băng, để hình dùng đúng số trong lời văn?

### Takeaway
Số trong lời văn Chương 6 bám `final_numbers_20261110.json` (git sạch) và các tệp mà `docs/claims.yaml` trỏ tới.
`artifact_freeze_20261111.json` chỉ khóa run (129 run, 5 tệp ngoài, 8 đầu vào), không khóa tệp đo. Hình mới nên đọc từ
đúng danh sách `SOURCES` của `build_research_figures.py`, `report_key_results.py` và các nguồn `@@NOTE@@` đang ghi trong
gon_src. Có một bẫy quan trọng: PSDS của LBR trong tệp đánh giá run và trong sổ test là số lưới cũ.

### Cited Findings
- `docs/claims.yaml` trỏ nhiều nhất tới `final_numbers_20261110.json` (11 lần), `rq3_modes_20261123.json` (7), `oof_selection_20261109_LBR.json` (5), `rq2_llm_systems_20261110_test_annotated.json` (4), `lbr_psds_grid_20261110_annotated_b0.json` (4), `calibration_20261123.json` (4), `rq1_multirun_bootstrap_phase_o_b0_vs_f2_20261014.json` (3), `psds_diagnosis_20261110_annotated.json` (3); và khai báo nguồn SED chính là `ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/evaluation_phase_lbr_annotated.json`, PSDS của B0 từ `evaluation_phase_o_annotated.json`, lưới từ `lbr_psds_grid_20261110_annotated.json` — [claims.yaml](../../docs/claims.yaml)
- `artifact_freeze_20261111.json` có khóa `runs` (129), `external` (5), `frozen_inputs` (8), `skip_test_predictions: false` — [artifact_freeze_20261111](../../docs/measurements/artifact_freeze_20261111.json)
- `build_research_figures.py` đọc: `data_profile_20261008_lf`, `s13_test_20261018`, `s13_ranking_annotated_20260928`, `final_numbers_20261110`, `lbr_context_20261123`, `calibration_20261123`, `lbr_diagnosis_20261109`, manifest hệ phục vụ B0, thư mục run B0 cuối, `rq1_multiseed_clean_20260924`, `rq1_v2_multiseed_20260929`, `rq2_llm_systems_20261110_test_annotated`, `rq3_modes_20261123`, `run_registry_20261123`, `retrieval_backfill_test_20261124` — [build_research_figures.py](../../scripts/build_research_figures.py)
- `report_key_results.py` đọc thêm `caption_vs_gt_dev_20261124`, `latency_lbrv3_20261123` — [report_key_results.py](../../scripts/report_key_results.py)
- Bẫy PSDS: `evaluation_phase_lbr_annotated.json` ghi `psds` 0,2146/0,2960 cho V2 (lưới `T_GRID` cũ), sổ test `sed[0]` ghi cùng số; final_numbers tách `psds_old_grid` và `psds_log` (0,3512/0,6116) — [evaluation_phase_lbr_annotated](../../ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/evaluation_phase_lbr_annotated.json), [test_ledger_20261124](../../docs/measurements/test_ledger_20261124.json), [final_numbers](../../docs/measurements/final_numbers_20261110.json)
- Cờ git của nguồn: `final_numbers` sạch (`089ef00`); `lbr_context_20261123` dirty, `latency_lbrv3_20261123` dirty, `data_profile_20261008_lf` dirty, `sed_v2_ablation_20260926` dirty; `rq3_modes`, `caption_vs_gt_dev`, `checker_sensitivity_dev`, `grouped_captions_dev`, `psds_diagnosis`, `lbr_psds_grid` sạch — các tệp tương ứng trong [docs/measurements](../../docs/measurements/)
- Manifest của `report/gon_figures` ghi nguồn `final_numbers_20261110.json`, revision `f7f0e34`, `dirty: true`, dpi 300 — [gon_figures/manifest.json](../../report/gon_figures/manifest.json)

### Inferences
- Mọi hình mới cần một manifest giống r-figures (nguồn + SHA-256) và nên dựng lại trên tree sạch, vì manifest hiện tại của gon_figures ghi `dirty: true`.
- Khi một số xuất hiện ở cả tệp gốc và final_numbers (vd. KTC của V2−B0), nên đọc từ final_numbers để trùng chính xác với lời văn; dùng tệp gốc chỉ cho chi tiết final_numbers không có (theo lớp, theo lỗi, theo câu hỏi).
- Nếu bổ sung số mới vào lời văn từ các hình này, cần thêm claim vào `docs/claims.yaml` để `check_doc_claims` kiểm được.

### Gaps
- Chưa kiểm hết tệp nào trong danh sách tầng B/C đã có claim trong `docs/claims.yaml` (vd. `retrieval_failures_test`, `checker_sensitivity_dev` có thể chưa có).

---

## Câu hỏi 6 — Hình đã có nhưng bản gọn không dùng; bảng nào nên đọc thành biểu đồ

### Takeaway
Bốn hình nghiên cứu đã dựng sẵn trong `report/gon_figures/` (r06, r09, r10, r11) được bản đầy đủ dùng nhưng bị bỏ khi
rút gọn; đưa lại là công gần như bằng 0. Thêm vài hình cũ (kiến trúc SED, ECE, cơ chế RQ1) có sẵn nhưng kiểu dáng
không đồng bộ. Khoảng 12 bảng trong bản gọn có thể kèm biểu đồ.

### Cited Findings
- Có trong `report/gon_figures/` nhưng không xuất hiện trong `report/gon_src/*.md`: `r06_onset_bias.png`, `r09_rq1_seeds.png`, `r10_rq2_errors.png`, `r11_rq3_queries.png` — [gon_figures](../../report/gon_figures/), [gon_src](../../report/gon_src/)
- Bản đầy đủ dùng: r06 ở `04_phuong_phap.md` dòng 79, r09 ở `06_ket_qua.md` dòng 58, r10 ở dòng 212, r11 ở dòng 281 — [final_src/04](../../report/final_src/04_phuong_phap.md), [final_src/06](../../report/final_src/06_ket_qua.md)
- Đích gợi ý: r06 → 04 "## Tinh chỉnh biên học được (LBR)" (lời văn đã nói "biên đầu bị đoán sớm… −1,5 s"); r09 → 06 "## RQ1" (lời văn nói 4 seed C phủ trọn khoảng của B); r10 → 06 "## RQ2" (cạnh tbl:rq2final); r11 → 06 "## RQ3" (cạnh tbl:rq3paired) — [06_ket_qua.md](../../report/gon_src/06_ket_qua.md), [04_phuong_phap.md](../../report/gon_src/04_phuong_phap.md)
- Hình cũ khác không dùng: `report/figures/m02_sed_architectures.png` (kiến trúc SED), `m03_s13_dev_vs_test.png` (trùng ý r08), `m04_data_pipeline.png` (đã thay bằng sơ đồ Word); `docs/thesis/figures/03_sed_v2_t2b_architecture.png`, `04_event_f1_progress.png` (bị r04 thay), `05_f2_per_class_event_f1.png` (bị r07 thay), `07_demo_interface.png`; `report/final_figures/s01–s06` (đã thay bằng `@@DIAGRAM@@`) — [report/figures](../../report/figures/), [docs/thesis/figures](../../docs/thesis/figures/), [final_figures](../../report/final_figures/)
- PNG tự sinh trong thư mục đo: `ece_datasec_20260923.png`, `rq1_mechanism_20261008_lf.png` — [docs/measurements](../../docs/measurements/)
- Ảnh demo chưa dùng: `01-start.png`, `02-timeline.png`, `04-rag-evidence.png` (bản gọn dùng `03-filter-chip.png` và f03a/f03b) — [demo_screenshots](../../docs/demo_screenshots/)
- Bảng nên kèm biểu đồ (bảng → hình gợi ý): f11_calibration → A3; f01_sed → A4; f10_lbr_context → B15; f04_rq2 → r10 (có sẵn); f04b_caption_tiers → A8; f05_rq3 → A7; f05b_rq3_paired → A1/r11; f05c_rq3_groups → B1; 10_parser_l2 → B3; f13_latency → B14; f06_psds → A11/C1; 03_rq1 → r09 (có sẵn); m02_classifier_per_class → A12; 06_s13_ranking_test → C2 (r08 đã có); f14_run_registry, f07_ledger → C5; f12_workload → g49 — [final_tables](../../report/final_tables/), [report/tables](../../report/tables/), [docs/thesis/tables](../../docs/thesis/tables/)
- Bảng nên giữ dạng bảng: f00_key_results, m01_classifier, 01_data_split, 02_leakage_d3_d4, f08_freeze, f15_tech_stack, f16_api, m08_taxonomy (số rời hoặc văn bản, không có trục so sánh) — cùng các thư mục trên

### Inferences
- Thêm lại r06, r09, r10, r11 và làm 7 hình tầng A ưu tiên cao là cách nhanh nhất để Chương 6 có khoảng 15 hình mà không phải dựng nhiều mã mới.
- `m02_sed_architectures.png` hoặc `03_sed_v2_t2b_architecture.png` có thể lấp chỗ thiếu sơ đồ mô hình SED ở Ch.4, nhưng vì bản gọn chuyển sang sơ đồ Word sửa được, nên vẽ lại bằng `@@DIAGRAM@@` thay vì dùng ảnh cũ (kiểu dáng và tên gọi cũ: "f2", "v2").

### Gaps
- Chưa mở xem nội dung từng PNG cũ để chắc nhãn (tên hệ cũ, tiếng Anh) có khớp thuật ngữ bản gọn (hệ mốc, hệ cơ sở, LBR chính, LBR ứng dụng); r06/r09/r10/r11 trong gon_figures đã qua bước `--labels` nên nhiều khả năng đã khớp.
