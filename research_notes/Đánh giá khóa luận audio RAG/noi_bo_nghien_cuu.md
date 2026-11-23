# Đánh giá nội bộ phía nghiên cứu: KLTN environmental-audio-rag (dữ liệu, mô hình, thí nghiệm, kết quả, claim)

> Ngày 23/11/2026; hạn nộp 28/11/2026. Chỉ đọc repo (HEAD `49dbbb8`): không train, không đánh giá, không đọc thêm dự đoán test. Cách dẫn nguồn: `[đường-dẫn Lxx](../../đường-dẫn)`, đường dẫn tính từ gốc repo, link tương đối tính từ thư mục ghi chú này. "(tính lại)" là số người viết ghi chú tự tính từ số đã ghi sẵn trong artifact (cộng/chia/xếp hạng), **không** phải lượt đánh giá mới. Tầng: T0 = làm được trước 28/11 bằng artifact sẵn có hoặc ≤ vài GPU-giờ, không train lại hệ chính; T1 = sau khi nộp, trước bảo vệ (slide/Q&A/thí nghiệm trình bày miệng); T2 = hướng phát triển/paper.

## 1. Kiểm kê: đã làm gì, quy mô bao nhiêu, có xứng tầm KLTN không?

### Takeaway
Về khối lượng và độ chặt, đề tài **vượt rõ** mức thông thường của một KLTN Khoa học dữ liệu: khoảng 111 lượt huấn luyện (103 SED, 8 phân loại) trải trên khoảng 12 tổ hợp encoder/recipe, chạy trên một GPU laptop 8 GB; 5 thế hệ hệ SED, mỗi thế hệ chọn theo luật ghi trước; 48 ADR; 270 báo cáo đo; sổ test ghi 42 lượt SED (tổng 126 artifact chạm test); 129 run được đóng băng bằng SHA-256; 1.192 kiểm thử; ứng dụng đầu–cuối chạy Docker. Rủi ro khi bảo vệ **không** nằm ở "làm ít". Rủi ro nằm ở ba chỗ: báo cáo cuối giấu phần lớn quy mô này, mạch đóng góp bị phân tán, và vài câu trả lời RQ chưa được nói thẳng (xem mục 2).

### Cited Findings
**Mã nguồn và lịch sử làm việc**
- 397 commit từ 22/09 đến 11/11/2026 (tháng 9: 201, tháng 10: 112, tháng 11: 84). Theo loại: 136 feat, 125 docs, 58 exp, 45 fix. Nguồn: `git log` đọc-only trên master `49dbbb8`.
- Python khoảng 54,5 nghìn dòng: `ml/` 13.602 dòng trong 108 tệp, `scripts/` 27.069/139, `services/` 639/11, `tests/` 13.199/144. Frontend (TS/JS/CSS/HTML trong `services/`, không tính node_modules) 1.753 dòng. Đếm bằng `find | wc -l`.
- Có 873 hàm `test_*`. Lần kiểm cuối 11/11: pytest 1.192 đạt, 4 skip, 1 xfail; ruff sạch; có CI GitHub Actions — [report/final_src/05_trien_khai.md L43](../../report/final_src/05_trien_khai.md).
- 48 ADR (ADR-0001…ADR-0048) cộng README — [docs/decisions/](../../docs/decisions/).
- `docs/measurements/` có 488 tệp: 270 báo cáo .md, phần còn lại là .json/.png đi kèm.
- PAPER_NOTES ghi 70 phát hiện có artifact (S1–S69 và S64b), kể cả kết quả âm tính — [docs/PAPER_NOTES.md §2–§3](../../docs/PAPER_NOTES.md).

**Thực nghiệm**
- `ml/runs/` có 218 thư mục run (31 GB), `artifacts/` thêm 14 GB. Trong đó có 103 manifest huấn luyện SED (có trường `dataset_windows`) và 8 run `classifier_datasec_*`. 111 manifest ghi GPU là "NVIDIA GeForce RTX 3070 Laptop GPU". Nguồn: quét manifest đọc-only.
- 107 run có checkpoint, chia theo encoder/recipe: frame_mn/T2b 38; CNN14 v1 13; CNN14+BiGRU v2 9; BEATs fine-tune (O-D) 9; BEATs đóng băng (T2a) 7; TF256 6; TF256-KD 6; gain/EQ (P4) 6; GRU 1; RED 1; khác 11. Nguồn: quét manifest.
- Thời gian chạy ước lượng khoảng 117,5 giờ cho 98 run có mốc thời gian hợp lệ (tính lại: bắt đầu = timestamp trong tên thư mục, kết thúc = mtime của `metrics.json`). Đây chỉ là ước lượng; manifest không ghi thời lượng.
- Có 7.090 dòng mô tả sinh ra, nằm trong 36 tệp JSONL `ml/runs/*/captions/`, và 11 run chỉ mục truy hồi.
- Các vòng chọn hệ thống:
  - S13 có 11 ứng viên ghi trước — [06_ket_qua.md L50](../../report/final_src/06_ket_qua.md).
  - Giai đoạn O chọn hai tầng S/C trên 564 bản ghi ngoài mẫu (OOF) — [04_phuong_phap.md L59](../../report/final_src/04_phuong_phap.md).
  - Giai đoạn P thử bốn hướng (thêm seed, KD, cửa sổ 20 s, gain/EQ) — [06 L74](../../report/final_src/06_ket_qua.md).
  - Có 6 báo cáo tầng C dạng `docs/measurements/oof_selection_*`.
- Sổ test ghi 42 lượt đánh giá SED trên test, gồm 33 run/ensemble khác nhau (tính lại từ bảng) và ba điểm vận hành LBR. Ngoài ra có 84 artifact khác chạm test: 35 caption RQ2, 5 caption lớp gộp/wiring, 18 truy hồi, 13 ablation/chẩn đoán SED v1, 3 LBR, 2 phân loại, 8 parity — [docs/measurements/test_ledger_20261111.md L7, L60–67](../../docs/measurements/test_ledger_20261111.md).
- Đóng băng 129 run/ensemble, 5 checkpoint ngoài và 8 tệp đầu vào cố định; không thiếu tệp nào. Ba bộ kiểm tài liệu: 87 số trong 157 chỗ nhắc, 96 lệnh, 370 liên kết — [05_trien_khai.md L41](../../report/final_src/05_trien_khai.md); [artifact_freeze_20261111.md](../../docs/measurements/artifact_freeze_20261111.md).

**Dữ liệu**
- Kiểm trùng ba tầng: byte, tín hiệu 16 kHz, fingerprint MFCC hiệu chuẩn bằng 24 cặp dương và 5.000 cặp âm. Kết quả: 3 nhóm trùng xuyên bộ; 35 cặp được duyệt tay bằng tai (10 trùng, 1 không chắc, 24 khác). Bị loại: 11 đoạn DataSEC (0,2179%) cộng 119 bản sao nội bộ, tổng 130 — [03_du_lieu.md L40–48](../../report/final_src/03_du_lieu.md).
- Chia tập theo `leakage_group`. Cổng D4 đạt 5/5 và được chứng minh "không đạt rỗng" bằng phép thử ngược — [03 L50, L56](../../report/final_src/03_du_lieu.md).
- Phát hiện 14 bản ghi thiếu nhãn đa âm, từ đó tạo tập `annotated` (dev 134, test 139) — [03 L60](../../report/final_src/03_du_lieu.md). 8 cặp được gán nhãn hai lần cho event-F1 người–người 0,5785 — [03 L62](../../report/final_src/03_du_lieu.md).

### Inferences
- Kết luận về quy mô: đủ và vượt chuẩn. Phần SED đi sâu theo chuỗi chẩn đoán → v2 → Track 2 → giao thức OOF hai tầng → LBR. Phần hạ tầng tái lập (ledger, freeze, bộ kiểm số liệu) hiếm thấy ở KLTN.
- Hội đồng dễ đánh vào ba điểm khác:
  - "Đề tài rộng, phần caption/RAG mỏng".
  - "Không có gì mới", vì mọi claim đã hạ xuống "áp dụng và mở rộng".
  - Mức làm chủ chi tiết. Khối lượng 48 ADR trong khoảng 7 tuần commit đủ lớn để hội đồng hỏi sâu về đặc trưng LBR, cross-fit, bootstrap ghép cặp, cSEBB. Nếu khoa có quy định khai báo công cụ hỗ trợ, cần chuẩn bị câu trả lời trung thực.

### Gaps
- Không có số GPU-giờ chính thức; con số 117,5 giờ chỉ là ước lượng từ mtime.
- Chưa đếm đủ số cấu hình hậu xử lý đã quét (nằm rải trong các `*_cv_selection*.json`).
- Chưa kiểm số trang PDF (venv không có pypdf); theo đề bài và CLAUDE.md §3 là 75 trang.

## 2. Từng RQ: kết quả chính, độ mạnh bằng chứng, phản biện dễ gặp, mức bảo vệ được

### Takeaway
- **Mạnh nhất:**
  - LBR: +0,116 micro trên test, CI không chứa 0, cùng hướng với kết quả OOF trên n = 564.
  - RQ1 âm tính: nhiều seed, hai công thức; ở v1, CI hẹp tới mức loại được mọi lợi ích lớn hơn 0,002.
- **Yếu nhất:**
  - **RQ3.** Trên 3/4 kho, hybrid **thua vector_only có ý nghĩa** (ví dụ V2: −0,087 [−0,136; −0,037]). Chương 6–7 không nhắc chữ "vector" lần nào, dù bảng f05 in số.
  - **RQ2.** "0 ảo giác" có được là nhờ cấu tạo của ngữ pháp. Mô tả constrained gần như là template. Ở mức từng caption, cờ ảo giác của bộ đo từ điển không trùng với cờ của người đọc ở ca nào (0/4).
- Số tuyệt đối thấp (micro 0,2965) bảo vệ được nếu đặt cạnh đồng thuận người, thước 1 s/segment và mốc DCASE.

### Cited Findings
**Phân loại DataSEC (câu hỏi phụ về lớp con)**
- Kết quả test: macro-F1 22 lớp 0,8466. Macro-F1 lớp con 0,6266 trên 28 nút, 0,8453 trên 5 nút có n ≥ 10. Nhất quán cha–con 0,9526. Hai lớp yếu nhất: vehicle_idling 0,6154, vehicle_pass_by 0,6538 — [06 L12](../../report/final_src/06_ket_qua.md).
- Accuracy test = 676/740 = **0,9135** (tính lại từ cột Correct/Total) — [per_class_metrics_datasec_20260923.md](../../docs/measurements/per_class_metrics_datasec_20260923.md). Báo cáo không nêu accuracy.
- Temperature scaling làm ECE trên test tăng từ 0,0332 lên 0,0564 — [06 L18](../../report/final_src/06_ket_qua.md).
- Quét λ của số hạng nhất quán (1 seed mỗi giá trị, đo trên dev):

  | λ | macro dev | nhất quán dev | Ghi chú |
  |---:|---:|---:|---|
  | 0 | 0,8375 | 0,9514 | |
  | 0,25 | 0,8431 | 0,9526 | |
  | 0,5 | 0,8230 | 0,9583 | được chọn theo luật "tối đa nhất quán trong rào −0,02" |
  | 1 | — | — | bị loại |

  Nguồn: [consistency_sweep_datasec_20260923.md](../../docs/measurements/consistency_sweep_datasec_20260923.md). Báo cáo lại viết "chọn bằng quét trên dev với điều kiện không làm giảm macro-F1" — [04 L38](../../report/final_src/04_phuong_phap.md). Câu này **không khớp**: macro dev đã giảm 0,0145. Hiệu ứng của λ nằm trong nhiễu.
- Mốc ngoài từ chính nhóm tác giả bộ dữ liệu (Artuso và cs., Forum Acusticum 2025): CLAP zero-shot đạt tốt nhất 72,93%, CLAP cộng lớp tuyến tính đạt 91,83% accuracy. Cả hai đo trên **validation**, 21 lớp (có Airplane/Helicopter thay cho jet/propeller), đoạn 4 s, chia 500/100/100/100 mẫu cho mỗi phiên bản dữ liệu — [FA2025 PDF tr. 2292–2293](https://dael.euracoustics.org/confs/fa2025/data/articles/000340.pdf). Repo mới ghi bài này ở mức V2 và chưa trích số — [docs/RELATED_WORK.md L458–461](../../docs/RELATED_WORK.md).

**RQ1: huấn luyện thêm trên DataSEC có giúp SED không?**
- Công thức v1 (test all, 3 B so với 4 C, cây sạch): C − B = −0,0071 [−0,0164; +0,0021]. Welch p lần lượt 0,234 / 0,913 / 0,181 cho event-F1 / PSDS-1 / PSDS-2.
- Công thức v2 (test annotated, 3 so với 3, ghi trước, mở test sau khi khóa hệ cuối): C − B = −0,0029 [−0,0254; +0,0199], p 0,696 / 0,439 / 0,019. Nguồn cho cả hai: [report/final_tables/f03_rq1.md](../../report/final_tables/f03_rq1.md); [06 L22–30](../../report/final_src/06_ket_qua.md).
- Đọc theo kiểu "loại trừ": cận trên của CI loại được lợi ích > +0,0021 ở v1 (khoảng 3,4% tương đối) và > +0,0199 ở v2 (khoảng 15%) (tính lại).
- Cơ chế (dev in-sample, 9 cặp run v2). C − B theo từng chỉ số:
  - segment-F1 1 s: +0,0268, C cao hơn ở 9/9 cặp;
  - frame mAP: +0,0192, 8/9;
  - onset-only: +0,0145, 9/9;
  - event-F1 collar 1 s: −0,0066, chỉ 4/9.

  C dẫn mAP ở epoch 1 (khoảng 0,51 so với 0,39) rồi mất lợi thế sau vài epoch — [rq1_mechanism_20261008_lf.md](../../docs/measurements/rq1_mechanism_20261008_lf.md); [PAPER_NOTES L96 (S48)](../../docs/PAPER_NOTES.md).
- RQ1b: dùng DataSEC với nhãn mạnh giả từ teacher (giữ 1.952/2.846 clip) không qua được tầng S (0,2151 so với 0,2330) — [PAPER_NOTES L116 (S57)](../../docs/PAPER_NOTES.md).
- S48 và S57 **không có trong** `report/final_src` (grep không thấy).
- Kết quả PSDS-2 v2 p = 0,019 chưa hiệu chỉnh cho so sánh bội — [06 L28–30](../../report/final_src/06_ket_qua.md).
- Bản DataSEC đang dùng là v3 (5.048 tệp). Bản v4 (02/10/2026, 4.292 tệp) sửa lỗi số tệp Music — [RELATED_WORK L462–467](../../docs/RELATED_WORK.md).

**SED từ v1 đến LBR (không phải RQ nhưng là phần nặng nhất)**
- Chẩn đoán v1 trên dev:
  - trần do độ phân giải /64 là 0,6294;
  - onset-only 0,2325, offset-only 0,4975, segment 0,6542;
  - 886 sự kiện tham chiếu chia thành 112 khớp, 417 lệch biên, 357 bỏ sót.

  Nguồn: [06 L36](../../report/final_src/06_ket_qua.md); [sed_ceilings_20260926.md](../../docs/measurements/sed_ceilings_20260926.md).
- Tiến triển trên test annotated:

  | Hệ | v1 | v2 | f2 | B0 | LBR V2 |
  |---|---:|---:|---:|---:|---:|
  | Micro | 0,0945 | 0,1500 | 0,1643 | 0,1806 | 0,2965 [0,2293; 0,3603] |
  | Macro | 0,0924 | 0,1389 | 0,1206 | 0,1366 | 0,2356 |

  Từ v1 đến LBR V2, micro tăng 3,1 lần; từ B0 đến V2, micro tăng 64% và macro tăng 72% tương đối (tính lại). Nguồn: [docs/thesis/tables/04_sed_progress.md](../../docs/thesis/tables/04_sed_progress.md); [report/final_tables/f01_sed.md](../../report/final_tables/f01_sed.md).
- S13: tương quan hạng Spearman giữa CV dev và test micro là ρ = 0,62 trên 11 ứng viên, 0,49 nếu bỏ ứng viên a (tính lại từ [06_s13_ranking_test.md](../../docs/thesis/tables/06_s13_ranking_test.md)). f1 đứng thứ 4 trên dev nhưng có micro test cao nhất — [06 L56](../../report/final_src/06_ket_qua.md).
- Giai đoạn O: cả 3 ứng viên qua tầng S đều đảo chiều ở tầng C — [PAPER_NOTES L115 (S56)](../../docs/PAPER_NOTES.md). B0 − f2 trên test = +0,0164 [−0,0128; +0,0495] — [06 L72](../../report/final_src/06_ket_qua.md).
- LBR trên OOF (564 bản ghi):
  - B0 0,2342; V1 (chỉ tinh chỉnh biên) 0,3043; V2 0,3332, Δ +0,0990 [+0,0761; +0,1200];
  - kiểm chuyển sang P1×3: 0,3505 — [oof_selection_20261109_LBR.md](../../docs/measurements/oof_selection_20261109_LBR.md).
  - Mốc đơn giản: λ riêng theo lớp 0,2335; dịch onset toàn cục 0,2469. Trần nếu sửa biên trong ±1 s: 0,4641. Áp mô hình in-sample cho 0,50 (đo mức overfit của GBM) — [ADR-0045 L16–17, L129–130](../../docs/decisions/ADR-0045-lbr-tinh-chinh-bien-va-cham-lai-box.md).
  - Thiết kế LBR được thăm dò trên **chính** tập OOF dùng để chọn — [ADR-0045 L217–218](../../docs/decisions/ADR-0045-lbr-tinh-chinh-bien-va-cham-lai-box.md).
- LBR trên test: V2 +0,1159 [+0,0741; +0,1593]; V3 (điểm f1) +0,0925 [+0,0549; +0,1331] — [f01_sed.md](../../report/final_tables/f01_sed.md).
- Phân loại các sự kiện bị bỏ sót (FN) của B0 trên OOF:
  - miss_nothing 995, bnd_onset 656, miss_other_class_overlap 482, merged 309, bnd_offset 116, bnd_both 100, fragmented 44;
  - 789 sự kiện bị bỏ sót có xác suất khung ≥ 0,9 trong khoảng nhãn;
  - trung vị lệch onset −1,47 s ở jet và train, −1,06 s ở vehicle_pass_by.

  Nguồn: [lbr_diagnosis_20261109.md](../../docs/measurements/lbr_diagnosis_20261109.md).
- Đánh đổi của LBR: V2 làm segment-F1 giảm 0,7260 → 0,5965 và recall giao nhau giảm 0,5351 → 0,5108. V3 ở điểm recall_first đạt R 0,8203 / P 0,7812 với 668 sự kiện dự đoán trên 740 tham chiếu — [f02_intersection.md](../../report/final_tables/f02_intersection.md). PSDS trên lưới log: B0 0,3061/0,7452; V2 0,3512/0,6116; V3 0,3369/0,6167 — [06 L102](../../report/final_src/06_ket_qua.md).
- Ngưỡng của LBR chạm biên lưới: điểm recall_first của V2/V3 nằm ở 0,005 (đáy lưới) ở 5/5 fold; điểm f1 của V3 nằm ở 0,85 (trần lưới) — [ADR-0045 L124–128, L165–167](../../docs/decisions/ADR-0045-lbr-tinh-chinh-bien-va-cham-lai-box.md). Báo cáo không nhắc chi tiết này.
- Thước nới có sẵn trong JSON test đã đóng băng (không phải lượt đánh giá mới): event-F1 collar 1 s micro B0 0,3889 → V2 0,5157 (macro 0,3185 → 0,4496) — khóa `application_metrics` trong `ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/evaluation_phase_{o,lbr}_annotated.json`.
- Đồng thuận người–người (8 cặp): collar 0,2 s 0,5785; collar 1 s 0,7603; segment 1 s 0,7425; F1 giao nhau 0,9173 — [oof_selection_20261109_LBR.md, dòng "Người–người"](../../docs/measurements/oof_selection_20261109_LBR.md).
- So với người (tính lại; khác mẫu, chỉ 8 cặp):
  - V2 đạt khoảng 0,51 mức người ở collar 0,2 s và 0,68 ở collar 1 s;
  - segment-F1 của B0 bằng khoảng 0,98 mức người (0,726/0,7425);
  - V3 recall_first bằng khoảng 1,05 mức người (0,7821/0,7425).
- Bối cảnh ngoài:
  - DCASE 2016 T3 (ghi âm đời thực): event-F1 4,7–6,3% — [02 L39](../../report/final_src/02_co_so_ly_thuyet.md).
  - DCASE 2019 T4 (DESED, 10 lớp trong nhà): baseline event-based F-score 23,7 (dev) / 25,8 (eval); segment 53,7 (eval); hệ tốt nhất 42,7 (eval) — [DCASE 2019 Task 4 results](https://dcase.community/challenge2019/task-sound-event-detection-in-domestic-environments-results).
- Chưa có bài nào công bố event-F1 trên DataSED trong phạm vi đã tra (09/11):
  - arXiv 2607.13571 có dùng DataSED nhưng chia ngẫu nhiên đoạn 10 s và đo frame mAP 0,660;
  - PolyBench chỉ dùng 169 clip cho bài hỏi đáp;
  - bài mô tả bộ dữ liệu không có baseline.

  Nguồn: [RELATED_WORK L453–457, L468–473, L657, L731](../../docs/RELATED_WORK.md).

**RQ2: mô tả bám sát sự kiện** (test annotated, n = 139 cho mỗi hệ)
- Unconstrained: ảo giác 0,005–0,022; suy diễn bối cảnh 0,259–0,403; gọi tên quá cụ thể 0,126–0,140; từ cấm 0,007–0,014.
- Constrained và constrained-cover: 0 ở cả bốn chỉ số trên, trên cả bốn hệ SED.
- Bỏ sót của constrained: 0,007–0,013 với f2/B0/V2, nhưng 0,081 [0,051; 0,112] với V3. Constrained-cover bỏ sót 0.
- Nguồn: [rq2_llm_systems_20261110_test_annotated.md](../../docs/measurements/rq2_llm_systems_20261110_test_annotated.md); [f04_rq2.md](../../report/final_tables/f04_rq2.md).
- Template đạt 0 ở mọi chỉ số — [06 L120](../../report/final_src/06_ket_qua.md).
- So với caption template của cùng timeline: constrained đạt BLEU-4 0,3584 / CIDEr 3,60; cover 0,3639 / 3,63; unconstrained chỉ 0,0147 / 0,116. Tức là constrained gần như template — [caption_ngram_sed_lbr_B0_20261109T172809Z_test_annotated.md](../../docs/measurements/caption_ngram_sed_lbr_B0_20261109T172809Z_test_annotated.md).
- Kiểm chứng bộ đo bằng người: 60 caption unconstrained của hệ v1 B, một người đọc mù.
  - Mức mention: P 0,896, R 0,936.
  - Cờ "caption có bịa": lexicon có & người có = 0; lexicon có & người không = 2; lexicon không & người có = 2; cả hai không = 56. Kappa khoảng −0,03 (tính lại).
  - Recall của lexicon cho lỗi gọi tên quá cụ thể: 0,568.

  Nguồn: [caption_mention_agreement_20260925.md](../../docs/measurements/caption_mention_agreement_20260925.md). Báo cáo chỉ nêu P/R — [06 L130](../../report/final_src/06_ket_qua.md).
- Giao diện tiếng Việt dùng mô tả template — [04 L90](../../report/final_src/04_phuong_phap.md). Báo cáo vẫn viết "bộ sinh không thể bịa…" — [04 L75](../../report/final_src/04_phuong_phap.md), mâu thuẫn với tỷ lệ ảo giác của unconstrained.

**RQ3: truy hồi và câu trả lời có bằng chứng** (test, bộ lọc gold, tiếng Anh)
- nDCG@10 và độ trả lời:

  | Kho | hybrid | vector | structured | Có trả lời | Trích đúng GT |
  |---|---:|---:|---:|---:|---:|
  | f2 | 0,415 | 0,526 | 0,416 | 65/97 | 0,917 |
  | B0 | 0,383 | 0,458 | 0,392 | 58/97 | 0,915 |
  | V2 | 0,404 | 0,491 | 0,411 | 62/97 | 0,899 |
  | V3 | 0,670 | 0,630 | 0,683 | 95/97 | 0,712 |

  Nguồn: [f05_rq3.md](../../report/final_tables/f05_rq3.md).
- Hiệu ghép cặp theo truy vấn, hybrid − vector_only (en, test): f2 −0,111 [−0,166; −0,059]; B0 −0,075 [−0,121; −0,028]; V2 −0,087 [−0,136; −0,037]; V3 +0,040 [+0,004; +0,079]. Trên validation: f2 −0,142, V2 −0,088. Hybrid − structured luôn có |Δ| ≤ 0,013. Nguồn: [retrieval_benchmark_test_20261002.md](../../docs/measurements/retrieval_benchmark_test_20261002.md), [_s8lite_b0_gold_20261108](../../docs/measurements/retrieval_benchmark_test_s8lite_b0_gold_20261108.md), [_lbrv2_gold_20261110](../../docs/measurements/retrieval_benchmark_test_lbrv2_gold_20261110.md), [_lbrv3_gold_20261110](../../docs/measurements/retrieval_benchmark_test_lbrv3_gold_20261110.md).
- Theo nhóm câu hỏi (en, test), hybrid so với vector:

  | Nhóm | f2 | B0 | V2 | V3 |
  |---|---|---|---|---|
  | temporal | 0,126 vs 0,426 | 0,134 vs 0,330 | 0,209 vs 0,398 | 0,501 vs 0,501 |
  | multi_class | 0,151 vs 0,387 | 0,090 vs 0,264 | 0,140 vs 0,325 | 0,576 vs 0,592 |

  Lọc cứng thắng ở nhóm duration và single_class trên mọi kho; trên kho V3, structured thắng cả nhóm temporal (0,530). Nguồn: cùng các tệp trên.
- Filter exactness của vector_only chỉ 0,27 (0,49 với V3), so với 1,000 của hybrid.
- Chương 6–7 **không nhắc vector_only lần nào** (grep "vector" trong 06/07: 0 kết quả). RQ3 được viết lại thành "bộ lọc có cấu trúc đóng góp gì?" — [07 L21](../../report/final_src/07_ket_luan.md), trong khi RQ3 gốc hỏi so sánh ba chế độ — [01 L43](../../report/final_src/01_gioi_thieu.md).
- Câu trả lời được sinh tất định bằng template; LLM chỉ dùng để phân tích câu hỏi — [ml/retrieval/answer.py L1–7](../../ml/retrieval/answer.py); [04 L119](../../report/final_src/04_phuong_phap.md). Parser: hợp lược đồ 240/240; đúng hoàn toàn 0,855 (template) và 0,925 (paraphrase); đúng điều kiện thời gian 0,767 — [06 L151](../../report/final_src/06_ket_qua.md).

**Độ chặt của quy trình test**
- 42 lượt SED đã chạy trên test, 10 lượt có cờ dirty. ADR-0045 tự nhận đây là "lần tái sử dụng thích nghi" — [test_ledger L7](../../docs/measurements/test_ledger_20261111.md); [06 L168](../../report/final_src/06_ket_qua.md); [ADR-0045 L211](../../docs/decisions/ADR-0045-lbr-tinh-chinh-bien-va-cham-lai-box.md).
- Các ablation hậu xử lý v1 (A2/A3/A5) đã đo trên test. Về sau, θ chung và g_max p25 được chọn lại bằng CV trên dev, nhưng PLAN ghi rõ lựa chọn này "cùng hướng A5 đã thấy trên test" — [test_ledger L63](../../docs/measurements/test_ledger_20261111.md); [docs/PLAN.md L470](../../docs/PLAN.md); [04 L67](../../report/final_src/04_phuong_phap.md).
- Hai câu tuyệt đối trong báo cáo:
  - "Tập test… một lần" — [04 L123](../../report/final_src/04_phuong_phap.md);
  - "cây bẩn… không dùng cho số chính thức" — [05 L39](../../report/final_src/05_trien_khai.md).

  Trong khi đó, số mốc v1 ensemble C (0,0945/0,0941) lấy từ lượt có cờ dirty — [test_ledger, dòng sed_ensemble_C_clean](../../docs/measurements/test_ledger_20261111.md).
- Protocol yêu cầu "macro trước, micro kèm" — [evaluation_protocol.md L130–141](../../docs/evaluation_protocol.md). Abstract và kết luận lại dẫn micro trước, và CI chỉ có cho Δ micro — [00 L9](../../report/final_src/00_phan_dau.md); [07 L10](../../report/final_src/07_ket_luan.md).

### Inferences
Bảng mức bảo vệ:

| Điểm bị tấn công | Nguy hiểm | Báo cáo đã đỡ? | Còn thiếu |
|---|---|---|---|
| "Event-F1 0,30 quá thấp" | Cao | Một phần (DCASE 2016, người 0,5785, độ nhạy collar) | Chưa đặt V2/B0 cạnh người ở collar 1 s và segment; chưa nêu mốc DCASE 2019 (23,7–25,8); chưa nêu frame mAP 0,74–0,80, tức nút thắt là định vị chứ không phải nhận dạng |
| "RQ1 âm tính là thất bại" | TB | Tốt | Chưa có cách đọc "loại trừ lợi ích > x"; chưa có cơ chế S48 và RQ1b S57 |
| "LBR chỉ là hậu xử lý / overfit trên OOF" | TB–cao | Một phần | Chưa có mốc đơn giản (0,2335/0,2469), chưa so V1 với V2, chưa định vị trong văn liệu (RED/EPN, cSEBB), chưa nói thiết kế được thăm dò trên OOF, chưa nói ngưỡng chạm biên lưới |
| "PSDS-2 của V2 thấp hơn B0" | TB | Có, nói thẳng và có chẩn đoán | PSDS không có CI; chưa có đường P–R trên OOF cho thấy V3 trội hơn B0 ở điểm recall-first |
| "Test chỉ 139 bản ghi mà dùng 42 lần" | Cao với hội đồng chặt | Có sổ ghi và có nêu hạn chế | Thiếu lập luận "OOF và test cùng hướng" (+0,099 so với +0,116); chữ "một lần" mâu thuẫn với con số 42; θ chung từng được gợi ý từ test |
| "RQ2 hiển nhiên theo cấu tạo; LLM chẳng khác template" | Cao | Một phần | Chưa nói template thắng mọi chỉ số; chưa đo giá trị gia tăng của LLM (độ tự nhiên); chưa công bố kappa ≈ 0 của cờ ảo giác |
| **"Hybrid thua vector"** | **Rất cao** (thấy ngay trong f05) | **Không** | Cần đoạn trả lời thẳng: cơ chế, phân theo nhóm câu hỏi, và việc V3 đảo chiều |
| "C4 temporal: nDCG nhóm temporal 0,21 < vector 0,40" | Cao | Không | Cần nói kết quả phụ thuộc recall của SED và dung sai τ (mặc định 0) |
| "RAG nhưng không có G" | TB | Có nói câu trả lời là tất định | Cần một câu biện minh thiết kế (ưu tiên trung thành với bằng chứng) |
| "Bộ phân loại không so với ai" | Thấp–TB | Không | Accuracy 0,9135 đã có sẵn; có thể đặt cạnh 91,83% của FA2025 (khác phiên bản, khác tập đo) |

- Có một luận điểm thống nhất mà số liệu ủng hộ: **nhận dạng đã tốt** (frame mAP khoảng 0,74–0,80, segment-F1 xấp xỉ mức người); **nút thắt là định vị biên và độ phủ**. Lỗi định vị lan xuống mô tả (bỏ sót tăng khi timeline dày) và xuống truy hồi (bị chặn bởi recall của SED chứ không phải bởi event-F1; V2 tăng event-F1 nhưng nDCG đứng yên, V3 tăng độ phủ thì nDCG tăng). Đặt như vậy, các RQ trở thành các mặt của một luận điểm, và LBR là can thiệp chính.

### Gaps
- Chưa có CI cho PSDS, cho Δ macro của LBR, và cho hiệu nDCG giữa các kho. Dữ liệu per-query đã có trong JSON (khóa `per_query`) nhưng chưa được phân tích.
- Chỉ số bối cảnh và gọi tên quá cụ thể chưa được kiểm chứng riêng bằng người.
- Nguyên nhân SED không tất định vẫn chưa rõ (nợ #5) — [PLAN L467](../../docs/PLAN.md).

## 3. Baseline, ablation và phân tích hội đồng sẽ chờ đợi nhưng còn thiếu hoặc yếu

### Takeaway
Nhiều mốc đơn giản thật ra **đã có trong docs nhưng không vào báo cáo**: mốc hậu xử lý của LBR, θ chung so với θ riêng, nhánh A học từ đầu, cSEBB so với θ, phân tích nhầm lớp. Những thứ còn **thiếu hẳn**:
- mốc không fine-tune (AudioSet tagger hoặc CLAP zero-shot);
- đường cong theo lượng dữ liệu;
- ablation đặc trưng của LBR;
- đánh giá người mở rộng cho caption (thêm người đọc, đo độ tự nhiên);
- mốc truy hồi kiểu từ khóa (BM25) hoặc "lọc mềm";
- bảng chi phí tính toán;
- hiệu chỉnh so sánh bội.

### Cited Findings
**Đã có nhưng không thấy trong báo cáo**
- Mốc đơn giản cho LBR (0,2335/0,2469), trần ±1 s (0,4641), so sánh V1 với V2 — [ADR-0045](../../docs/decisions/ADR-0045-lbr-tinh-chinh-bien-va-cham-lai-box.md); grep "0,2469", "0,4641" trong final_src: 0 kết quả.
- Phân tích nhầm lớp: 1.482 lượt substitution trên 6.202 sự kiện tham chiếu (7 run, dev); chủ yếu là đồng xuất hiện trong cảnh, nhầm âm học thật chỉ có horn↔sirens (7/7 run) — [confusable_pairs_clean_dev_20260925.md](../../docs/measurements/confusable_pairs_clean_dev_20260925.md); [PAPER_NOTES L57 (S10)](../../docs/PAPER_NOTES.md).
- Khoảng cách nhận dạng – định vị: lớp train có frame AP 0,94 nhưng event-F1 chỉ 0,04; θ riêng theo lớp kiểu oracle chỉ thêm +0,005…+0,045 — [PAPER_NOTES L117 (S55)](../../docs/PAPER_NOTES.md).
- Nhãn thiếu và nhãn đôi: bỏ 8 bản ghi thiếu nhãn khỏi tập train và gộp 4 cặp gán đôi không làm đổi event-F1 (0,2330 so với 0,2327) — [PAPER_NOTES L98 (S50)](../../docs/PAPER_NOTES.md).
- Đường cong theo epoch của RQ1 có sẵn ở dạng PNG — [rq1_mechanism_20261008_lf.png](../../docs/measurements/rq1_mechanism_20261008_lf.png).
- Bảng theo lớp có trong Phụ lục C ([f09_per_class.md](../../report/final_tables/f09_per_class.md)): V2 có 3 lớp F1 = 0, trong đó vehicle_pass_by có 70 sự kiện tham chiếu.
- Ablation v2 chỉ có 1 seed — [06 L42](../../report/final_src/06_ket_qua.md).

**Thiếu hẳn**
- Grep "zero-shot", "linear probe", "learning curve", "BM25/tf-idf" trong docs/measurements, docs/decisions, final_src, ml và scripts: 0 tệp có nội dung (các "khớp" khác chỉ là tệp nhị phân).
- Không có số thời gian huấn luyện hay GPU-giờ trong báo cáo (grep "GPU-giờ", "phút": 0). Có một số đo độ trễ demo từ một lượt chạy (3,7 s / 0,27 s) — [05 L33](../../report/final_src/05_trien_khai.md).
- Kiểm định: dùng bootstrap ghép cặp và Welch; không có hiệu chỉnh Holm/Bonferroni (báo cáo có tự nhận ở [06 L30](../../report/final_src/06_ket_qua.md)).
- Ví dụ lỗi cụ thể: chỉ có một timeline dev S-0009 trên hệ f2 — [04 L92](../../report/final_src/04_phuong_phap.md). Không có ví dụ trước/sau LBR.

### Inferences
- Thứ tự ưu tiên theo "tác động trên hội đồng ÷ công sức":
  1. đưa các mốc và phân tích đã có vào báo cáo (rẻ, an toàn);
  2. thêm ví dụ trước/sau LBR và phân loại lỗi trên OOF;
  3. ablation LBR trên OOF (chỉ cần CPU);
  4. mốc zero-shot và đánh giá người (cần GPU hoặc công người, nên để T1).

### Gaps
- Chưa ước được kết quả của mốc zero-shot (cần chạy thử). Ánh xạ 527 lớp AudioSet sang 21 lớp là quyết định chủ quan và phải ghi trước.

## 4. Báo cáo có "bán rẻ" công sức không? Mạch truyện có thống nhất không?

### Takeaway
**Có bán rẻ.** Báo cáo trình bày ledger, freeze, giao thức OOF và các kết quả âm tính chính, nhưng thiếu ba thứ:
- quy mô thực nghiệm;
- phần lớn chẩn đoán và kết quả âm tính phụ;
- **LBR như một đóng góp.**

Bảng đóng góp C1–C4 vẫn là của đề cương. Can thiệp tốt nhất về số liệu (LBR, +64%) và giao thức đánh giá không nằm trong danh sách đóng góp, trong khi C1–C4 đều đã bị hạ xuống "áp dụng và mở rộng". Kết quả là hội đồng dễ đọc thành "nhiều thí nghiệm rời rạc, không có gì mới". Ngoài ra còn tồn đọng nhiều lỗi diễn giải từ lần tự rà soát 03/10.

### Cited Findings
- Đóng góp C1–C4 giữ nguyên từ đề cương ("Đề cương nêu bốn đóng góp"); không có LBR hay giao thức đánh giá — [01_gioi_thieu.md L57–66](../../report/final_src/01_gioi_thieu.md). ADR-0021 dời trọng tâm sang C1/C2/C4 từ 24/09 — [ADR-0021](../../docs/decisions/ADR-0021-rq1-ket-qua-am-tinh.md).
- Mục tiêu (3) có nhắc "tinh chỉnh biên sự kiện" — [01 L33](../../report/final_src/01_gioi_thieu.md), nhưng không có RQ hay đóng góp nào tương ứng. Chương 2 không định vị LBR so với văn liệu hồi quy biên; repo thì đã có Schmid và cs. 2026 về RED/EPN — [RELATED_WORK L378–395](../../docs/RELATED_WORK.md).
- Báo cáo có 786 dòng nguồn, chỉ 5 hình (một hình kết quả là f01) và 22 bảng (đếm `@@CAP:tbl` và `![]` trong final_src). Kịch bản bảo vệ dài 145 dòng, không có ngân hàng câu hỏi phản biện — [report/slide/kich_ban_bao_ve.md](../../report/slide/kich_ban_bao_ve.md).
- Phần **hiện ra** với người đọc:
  - ledger, freeze, bộ kiểm số liệu, 1.192 kiểm thử — [05 L39–43](../../report/final_src/05_trien_khai.md);
  - tầng S/C — [04 L59](../../report/final_src/04_phuong_phap.md);
  - RQ1 âm tính, ECE tăng, giai đoạn P âm tính (gói trong một đoạn), S13 đổi hạng, cSEBB chỉ thắng có điều kiện — [06](../../report/final_src/06_ket_qua.md).
- Phần **không hiện**: S10, S48, S55, S57, chi tiết đảo chiều ở S56, mốc LBR, κ của bộ đo caption, hybrid so với vector, accuracy của bộ phân loại, chi phí tính toán, 70 phát hiện trong PAPER_NOTES.
- Lỗi diễn giải trong tự rà 03/10 ([report/danh_gia_bao_cao_20261003.md L54–71](../../report/danh_gia_bao_cao_20261003.md)) **vẫn còn** trong final_src:
  - **K02** suy diễn giấy phép mô hình — [03 L7](../../report/final_src/03_du_lieu.md);
  - **K03** "gán nhãn độc lập", "người với người", "cải thiện nhỏ hơn… không phân biệt được" — [03 L62](../../report/final_src/03_du_lieu.md); [06 L36](../../report/final_src/06_ket_qua.md);
  - **K04** "cross-entropy… không phạt" — [04 L38](../../report/final_src/04_phuong_phap.md);
  - **K07** "không thể bịa" — [04 L75](../../report/final_src/04_phuong_phap.md);
  - **K09** "hiệu số… là một cận dưới" — [04 L131](../../report/final_src/04_phuong_phap.md);
  - **K11** "349 lỗi là bỏ sót" — [06 L66](../../report/final_src/06_ket_qua.md);
  - **K12** "không phải nhận dạng lớp" — [06 L36](../../report/final_src/06_ket_qua.md), [04 L61](../../report/final_src/04_phuong_phap.md); trong khi lbr_diagnosis có 482 FN loại miss_other_class_overlap;
  - **K13** "tuyệt đối" — [06 L161](../../report/final_src/06_ket_qua.md), [07 L21](../../report/final_src/07_ket_luan.md);
  - **K16** "một lần" và "cây bẩn" — [04 L123](../../report/final_src/04_phuong_phap.md), [05 L39](../../report/final_src/05_trien_khai.md).
  - Đã xử lý: K14 ([02 L75](../../report/final_src/02_co_so_ly_thuyet.md)) và K15 ([07 L17](../../report/final_src/07_ket_luan.md)).
- Lỗi mới phát hiện: câu λ "không làm giảm macro-F1" — [04 L38](../../report/final_src/04_phuong_phap.md) so với [consistency_sweep](../../docs/measurements/consistency_sweep_datasec_20260923.md).

### Inferences
- Nên viết lại mạch truyện thành **một luận điểm** (xem cuối mục 2) và thêm hai đóng góp, đều ở mức "áp dụng và mở rộng", không dùng chữ "lần đầu":
  - **C5**: cải thiện SED dựa trên chẩn đoán, kết thúc bằng LBR (tầng hậu xử lý học được, độc lập với mô hình gốc, cross-fit, đã kiểm chuyển);
  - **C6**: giao thức đánh giá chống chọn theo test (OOF hai tầng, ledger, freeze).
- Có thể nói "là mốc tham chiếu tái lập được trên DataSED với split cố định", kèm câu "trong phạm vi đã tra". Không viết "baseline đầu tiên". Phạm vi vẫn tôn trọng ADR-0001: không nói tới tội phạm hay khẩn cấp.

### Gaps
- Chưa đối chiếu nội dung slide `report/slide_bao_ve.pptx` với các khuyến nghị (chỉ đọc kịch bản .md).

## 5. Cải thiện nào làm được bằng artifact sẵn có, cái nào cần compute mới? Khuyến nghị phân tầng

### Takeaway
Phần lớn cải thiện có giá trị nhất là **T0 thuần văn bản và hình**, vẽ từ số đã có, không chạm test mới:
- trả lời thẳng câu hỏi hybrid so với vector;
- định vị LBR cùng các mốc đơn giản;
- một "hình hành trình" và thước so với người;
- bổ sung cơ chế RQ1;
- sửa các lỗi K;
- bảng quy mô công việc.

Thí nghiệm mới (ablation LBR trên OOF, mốc zero-shot, đánh giá người) nên để T1 và trình bày miệng. Thử nghiệm kiểm chứng ngoài bộ dữ liệu để T2.

### Cited Findings
- Dữ liệu per-query của truy hồi đã có trong JSON (khóa `per_query`, `paired_ndcg@10`) — [retrieval_benchmark_test_lbrv2_gold_20261110.json](../../docs/measurements/retrieval_benchmark_test_lbrv2_gold_20261110.json).
- Dự đoán OOF của B0 và sự kiện LBR cross-fit (dev) đã nằm trong freeze: `sed_oof_B0_h5_20261008T130849Z`, `sed_filtered_B0_oof_dev_20261107T181008Z`, `sed_lbr_oofevents_*` — [artifact_freeze_20261111.md L9–26](../../docs/measurements/artifact_freeze_20261111.md).
- Các script vẽ bảng/hình đã có sẵn: `scripts.build_final_tables`, `scripts.build_final_figures` — [CLAUDE.md §3](../../CLAUDE.md); [06 L92](../../report/final_src/06_ket_qua.md).
- Luật dự án: không chọn gì trên test; mọi lượt test mới phải ghi trước và vào ledger — [CLAUDE.md §5](../../CLAUDE.md); [04 L123](../../report/final_src/04_phuong_phap.md).

### Inferences
**T0: trước 28/11, không chạm test mới**

| Mã | Việc cụ thể | Phản biện được hóa giải | Giờ | Rủi ro | File |
|---|---|---|---:|---|---|
| T0-1 | Viết một đoạn RQ3 trả lời thẳng: các hiệu hybrid−vector đã có; hybrid ≈ structured; bảng theo nhóm (temporal/multi_class so với duration/single_class); cơ chế là lọc cứng trên sự kiện dự đoán nên bị chặn bởi recall của SED, còn vector bỏ qua ràng buộc (exactness 0,27); với V3 thì đảo chiều. Sửa cả kết luận RQ3 và abstract. | "Giấu kết quả bất lợi", "RQ3 trả lời lệch câu hỏi", "C4 kém ở chính nhóm temporal" | 2–3 | Thấp | 06 L137–147; 07 L21; 00 L9, L23; retrieval_benchmark_test_*.md |
| T0-2 | Thêm bảng "LBR trong bối cảnh" (số OOF): λ theo lớp 0,2335; dịch onset 0,2469; V1 0,3043; V2 0,3332; P1×3 0,3505; trần ±1 s 0,4641; in-sample 0,50. Nói rõ thiết kế được thăm dò trên OOF và ngưỡng chạm biên lưới. | "LBR chỉ là chỉnh ngưỡng", "overfit" | 2 | Thấp | 04 L61; 06 L78; ADR-0045; oof_selection_20261109_LBR.md |
| T0-3 | Đổi khung đóng góp: thêm C5 (LBR) và C6 (giao thức chống chọn theo test), ghi rõ "áp dụng và mở rộng". Định vị LBR so với RED/EPN (Schmid và cs. 2026) và cSEBB. Chỉ trích Phan và cs. nếu đã đọc trực tiếp (hiện mới ở mức V1). Viết một câu luận điểm thống nhất. | "Không có gì mới", "thí nghiệm rời rạc" | 3–4 | TB: không được để lọt chữ "lần đầu"; phải chạy `check_doc_claims` | 01 L55–66; 02 L41–45, L73–75; 07 L23–25; RELATED_WORK (15) |
| T0-4 | Vẽ "hình hành trình": micro và macro trên test annotated từ v1 → v2 → f2 → B0 → V2, kèm CI và số dev/OOF tương ứng; chú thích luật chọn ở từng bước; kẻ vạch đồng thuận người 0,5785. | "Làm ít", "kết quả thấp" | 2–3 | Thấp | 04_sed_progress.md; f01_sed.md; final_numbers_20261110.json; scripts/build_final_figures.py |
| T0-5 | Thêm bảng "thước và mức người": collar 0,2 s / 1 s / segment / giao nhau cho B0, V2, V3 so với người–người (8 cặp, ghi rõ khác mẫu). Thêm mốc DCASE 2019 T4 (23,7/25,8; DESED; chỉ để định cỡ). | "0,30 là quá thấp" | 1–2 | TB: không được viết "ngang người" (lưu ý K03) | evaluation_phase_{o,lbr}_annotated.json; oof_selection_20261109_LBR.md; 02 L39 |
| T0-6 | Bổ sung RQ1: câu "loại trừ lợi ích > 0,002 (v1) / > 0,02 (v2)"; cơ chế S48 kèm hình đường cong (gắn nhãn dev in-sample); RQ1b S57. | "RQ1 âm tính là làm chưa tới" | 2–3 | Thấp | rq1_mechanism_20261008_lf.{md,png}; f03_rq1.md; PAPER_NOTES S48/S57 |
| T0-7 | Sửa các lỗi K02, K03, K04, K07, K09, K11, K12, K13, K16 và câu λ (xem mục 4). Thêm một đoạn "tái sử dụng test": 42 lượt tương ứng 33 run, mỗi cấu hình mở một lần; θ chung từng được gợi ý từ A2/A5 trên test; OOF và test cùng hướng (+0,099/+0,116; V3 +0,072/+0,093); ρ dev–test của S13 = 0,62 là lý do chuyển sang OOF. | "Sai kiến thức", "khẳng định quá mức", "p-hacking trên test" | 3 | Thấp | 03, 04, 05, 06, 07; danh_gia_bao_cao_20261003.md |
| T0-8 | Thêm mục phân tích lỗi chỉ dùng dev/OOF: bảng phân loại FN (lbr_diagnosis); độ lệch onset theo lớp (lớp dài lệch −1 đến −1,5 s); nhầm lớp do đồng xuất hiện (S10); khoảng cách frame AP với event-F1 (S55); 2–3 timeline OOF trước/sau LBR. | "Không có phân tích lỗi hay ví dụ cụ thể" | 4–6 | Thấp–TB (phải viết script hình, chỉ đọc OOF) | lbr_diagnosis_20261109.*; confusable_pairs_clean_dev_20260925.md; detection_gap_20261009.md; ml/runs/sed_filtered_B0_oof_dev_*, sed_lbr_oofevents_* |
| T0-9 | Bộ phân loại: nêu accuracy 0,9135 (676/740), đặt cạnh FA2025 (91,83% trên validation, khác phiên bản/lớp/đoạn); nói thật rằng hiệu ứng của λ nằm trong nhiễu. | "Bộ phân loại tốt tới đâu, so với ai?" | 1 | Thấp (ghi đủ cảnh báo so sánh) | per_class_metrics_datasec_20260923.md; consistency_sweep_datasec_20260923.md; 06 L12 |
| T0-10 | RQ2: thừa nhận "theo cấu tạo" và việc constrained gần template (BLEU-4 0,36); template thắng mọi chỉ số và là thứ giao diện đang dùng; tác động thật nằm ở bối cảnh (0,26–0,40 → 0) và gọi tên quá cụ thể (0,13 → 0); công bố κ ≈ 0 của cờ ảo giác và recall 0,568 (bộ đo bảo thủ); nói rõ LLM có ích ở parser. | "RQ2 hiển nhiên", "LLM thừa", "bộ đo chưa kiểm chứng" | 2 | TB: claim C1/C2 yếu đi, nhưng tránh bị hội đồng tự bắt lỗi | caption_ngram_*; caption_mention_agreement_20260925.md; rq2_llm_systems_20261110_test_annotated.md |
| T0-11 | Bảng "khối lượng công việc" (phụ lục hoặc Chương 5): commit, ADR, báo cáo đo, 111 lượt huấn luyện, khoảng 117 giờ (ghi rõ là ước lượng), các họ encoder, 11 ứng viên S13, 6 vòng tầng C, ledger 42/126, 7.090 caption, 1.192 kiểm thử, LOC. | "Làm ít" | 1–2 | Thấp | mục 1 của ghi chú này |
| T0-12 (tùy chọn) | Thêm macro vào headline của abstract cho đúng protocol "macro trước" (V2 0,2356 so với B0 0,1366), ghi CI chỉ có cho micro. | Lệch protocol | 0,5 | Thấp | 00 L9, L23; evaluation_protocol L130–141 |

**T1: sau khi nộp, trước bảo vệ**
- **T1-1. Ngân hàng khoảng 20 câu phản biện.** Mỗi câu có trả lời 30 giây và slide dự phòng kèm bằng chứng. Gồm: test n = 139 dùng 42 lần; F1 thấp; RQ1; LBR overfit; PSDS-2; hybrid thua vector; RAG không có G; "theo cấu tạo"; DataSEC v4; trùng nguồn AudioSet; SED không tất định (nợ #5); tự làm chủ chi tiết. Khoảng 4–6 giờ. Rủi ro thấp. File: report/slide/kich_ban_bao_ve.md.
- **T1-2. Ablation LBR trên OOF, chỉ cần CPU.**
  - Nội dung: đường cong theo lượng dữ liệu (25/50/75/100% fold fit); bỏ từng nhóm đặc trưng (chỉ đường xác suất / thêm ngữ cảnh lớp khác / thêm meta); rescore-only.
  - Sinh lại bằng script repo các số LBR trên base khác vốn từ script nháp (B0 + O-D 0,2112 → 0,3472; TF256-KD 0,1372 → 0,3235) — [PAPER_NOTES L198](../../docs/PAPER_NOTES.md).
  - Hóa giải: "LBR phụ thuộc gì, cần bao nhiêu nhãn". Khoảng 4–6 giờ. Rủi ro TB: ghi là phân tích hậu nghiệm trên OOF, không chọn lại.
- **T1-3. Mốc zero-shot hoặc không fine-tune trên OOF (564 bản ghi, không đụng test).** PANNs CNN14 framewise 527 → 21 lớp, hoặc CLAP. Ghi ánh xạ lớp trước. Khoảng 1–2 GPU-giờ cộng 3 giờ công. Hóa giải: "huấn luyện có đáng không". Nếu muốn có số test thì phải ghi trước và vào ledger.
- **T1-4. Đánh giá người cho caption trên dev.** 2 người đọc × 100 mô tả (template / constrained / unconstrained), chấm ảo giác, bối cảnh, độ tự nhiên (Likert), tính κ. Khoảng 6–8 giờ công người. Hóa giải: "bộ đo từ điển", "LLM có giá trị gì".
- **T1-5. Truy hồi trên validation.** Thử BM25 và "lọc mềm" (vector xếp hạng, filter làm boost), thêm dung sai τ > 0 cho nhóm temporal. Khoảng 3–5 giờ CPU. Hóa giải: "hybrid thua vector". Trình bày như hướng sửa.
- **T1-6. Phân tích lại số test đã ghi.** Bootstrap ghép cặp giữa các kho (per-query đã có) và CI cho Δ macro của LBR. **Bắt buộc ghi trước và ghi vào ledger** dưới dạng "phân tích lại", vì đây là phép tính mới trên dự đoán test. Khoảng 2–3 giờ.
- **T1-7. Đo hiệu năng.** RTF/độ trễ trên N bản ghi dev, đo nhiều lượt (≤ 1 GPU-giờ, không dùng nhãn). Hóa giải: "tính thực tiễn".

**T2: phát triển tiếp / paper**
- Kiểm LBR trên bộ dữ liệu khác có nhãn mạnh (DESED/RealDESED, MAESTRO, URBAN-SED) theo cùng giao thức OOF.
- So LBR với huấn luyện nhận biết biên (RED/EPN).
- Chạy lại RQ1 với DataSEC v4; huấn luyện chung nhãn mạnh + nhãn yếu; soundscape tổng hợp từ DataSEC.
- Đường cong dữ liệu cho backbone SED (15–25 GPU-giờ).
- Gán nhãn lại 20–30 bản ghi DataSED để có trần đồng thuận người đáng tin.
- Thêm chỉ số bám sát phía âm thanh (FLAM/CLAP); so với hệ kiểu LA-RAG trên cùng bộ truy vấn; nghiên cứu với người dùng thật.

**Thứ tự nếu chỉ còn khoảng 12–15 giờ trước 28/11:** T0-1 → T0-7 → T0-2 → T0-3 → T0-5 → T0-4 → T0-6 → T0-10 → T0-11. T0-8 và T0-9 làm nếu còn thời gian. Mọi thay đổi số trong tài liệu phải qua `check_doc_claims`.

### Gaps
- Chưa ước được công dựng lại DOCX/PDF và cập nhật field sau khi sửa (theo nhật ký, khoảng 1–2 giờ cho mỗi lượt dựng).
- Chưa kiểm xem các khóa per-query trong JSON có đủ để làm bootstrap giữa các kho mà không cần chạy lại truy hồi hay không (mới xem tên khóa, chưa xem cấu trúc bên trong).
