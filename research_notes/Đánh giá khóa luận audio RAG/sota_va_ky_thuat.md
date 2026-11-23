# Bối cảnh SOTA, dải hiệu năng và kỹ thuật cải thiện cho khóa luận SED + caption có căn cứ + RAG trên DataSEC/DataSED

> Ngày tra: **23/11/2026**. Lượt tra: khoảng 25 truy vấn WebSearch/WebFetch, cộng đọc lại repo (chỉ đọc). Không dùng Google
> Scholar hay cơ sở dữ liệu trả phí, nên "không thấy" chỉ có nghĩa là không thấy trong phạm vi này, không phải bằng chứng là không tồn tại.
>
> **Mức xác minh** theo quy ước V0–V4 của [docs/RELATED_WORK.md §0](../../docs/RELATED_WORK.md):
> - **[V1]**: chỉ thấy qua snippet tìm kiếm.
> - **[V2]**: đọc qua bản tóm tắt WebFetch của trang hoặc bảng, chưa tự đọc bảng gốc. Phải nâng lên V3 (curl + trích văn bản) trước khi đưa vào báo cáo, vì quy tắc repo chỉ cho trích V3/V4.
> - **[V3]**: tự đọc trực tiếp, hoặc nguồn đã ở mức V3 trong repo.
>
> **Hệ thống của đề tài, đối chiếu repo** (để người viết báo cáo khỏi phải tra lại):
> - **SED.** B0 dùng Frame-MobileNet `frame_mn10` (khoảng 3M tham số), tiền huấn luyện trên **AudioSet Strong** theo PretrainedSED/EfficientAT, độ phân giải 40 ms (250 bước/10 s) ([04_phuong_phap.md](../../report/final_src/04_phuong_phap.md)).
>   - Tinh chỉnh toàn bộ, không có mô hình chuỗi.
>   - 5 mô hình theo fold, suy luận chồng lấn bước 5 s với trọng số tam giác, cuối cùng qua cSEBB.
>   - LBR gồm hai HistGradientBoosting học trên xác suất OOF: một bộ tinh chỉnh biên, một bộ chấm lại hộp.
> - **Caption.** Qwen3.5-9B Q4_K_M (llama.cpp, nhiệt độ 0), có ngữ pháp GBNF.
> - **Retrieval.** BGE-M3 (1024 chiều) + PostgreSQL 16/pgvector; chế độ hybrid lọc cứng trước rồi mới xếp hạng cosine.
> - **Số test (annotated n = 139, **21 lớp đa âm**; không phải 22 lớp như đề bài viết, vì `wind_turbine` không có trong bản nhãn đa âm, [03_du_lieu.md](../../report/final_src/03_du_lieu.md)):**
>   - Event-F1 micro: B0 0,1806 [0,1261; 0,2384] → LBR V2 0,2965 [0,2293; 0,3603]. Macro: 0,1366 → 0,2356.
>   - PSDS trên lưới log: V2 0,3512 / 0,6116; V3 0,3369 / 0,6167; B0 0,3061 / 0,7452.
>   - nDCG@10 hybrid/EN: 0,383 (B0), 0,404 (V2), 0,670 (V3).
>   - Nguồn: [06_ket_qua.md](../../report/final_src/06_ket_qua.md).
>
> Collar dùng chung: onset 200 ms, offset max(200 ms, 20% độ dài); "micro" là `overall` của `sed_eval`.

## Câu hỏi 1. Bài báo dataset và các công trình theo sau: có baseline nào để so trực tiếp với số của khóa luận không?

### Takeaway
Tính đến 23/11/2026 vẫn **chưa có công bố nào báo event-based F1 hay PSDS trên DataSED**. Bài dataset không có baseline. Các công trình theo sau đều chỉ dùng phân loại, hỏi đáp trắc nghiệm hoặc frame mAP trên split ngẫu nhiên. Vì vậy số SED của khóa luận **không so trực tiếp được với bên ngoài**: đó là mốc tham chiếu nội bộ, phải diễn đạt là "chưa thấy công bố nào", không phải "lần đầu tiên". Các số phân loại DataSEC bên ngoài (91,83–97% accuracy) cao hơn macro-F1 0,8466 của đề tài, nhưng khác phiên bản, khác tập lớp, khác metric và khác cách chia nên cũng không so trực tiếp được.

### Cited Findings
- **Bài dataset** (Fredianelli L., Artuso F., Pompei G., Licitra G., Iannace G., Akbaba A., *Environmental Noise Dataset for Sound Event Classification and Detection*, *Scientific Data* 12:1712, 2025, DOI 10.1038/s41597-025-05991-w) [V3, repo đã đọc toàn văn] — [Nature](https://www.nature.com/articles/s41597-025-05991-w); [docs/RELATED_WORK.md §1](../../docs/RELATED_WORK.md).
  - Bài chỉ có các mục Background/Methods/Data Record/Technical Validation/Usage Notes: không có mô hình, metric hay split khuyến nghị.
  - DataSEC được mô tả trong bài là bản cũ (4.292 file / 18 h 26 m).
  - Nguồn âm thanh một phần lấy từ Freesound và AudioSet, có cắt/trộn/thêm âm thanh bằng tay.
- **Phiên bản DataSEC trên Zenodo** [V2] — [Zenodo DataSEC v4](https://zenodo.org/records/23097290); [docs/RELATED_WORK.md §2.3 (23)](../../docs/RELATED_WORK.md).
  - v4 (record 23097290) công bố 02/10/2026, có 4.292 file và sửa lỗi số file Music.
  - Repo dùng v3 (17033970, 5.048 file). DataSED (15346092) chỉ có một phiên bản.
- **Artuso F., Pompei G., Akbaba A., Iannace G., D'Alessandro F., Fidecaro F., Licitra G., Fredianelli L., *Enhanced Environmental Sound Event Classification through Transfer Learning with CLAP Model*, Forum Acusticum Euronoise 2025 (Málaga, 23–26/06/2025), tr. 2289–2294, DOI 10.61782/fa.2025.0340** [V3: tự đọc trực tiếp cả 6 trang PDF trong lượt này] — [PDF FA2025](https://dael.euracoustics.org/confs/fa2025/data/articles/000340.pdf).
  - **Dữ liệu.** Dựng từ freesound.org và bản ghi của nhóm tác giả, gồm **21 lớp** (Airplane, Bells, Birds, Cats, Chicken coop, Cicadas and crickets, Clacson, Crows and seagulls, Dogs, Glass breaking, Helicopter, Lawn mower and brush cutter, Music, Sirens and alarms, Thunder/fireworks/gunshot, Train, Vacuum cleaner/fan/hairdryer, Vehicle idling, Vehicle pass-by, Voices, Workshop).
  - **Cách chia.** Đoạn dài 1–10 s; mỗi phiên bản dữ liệu có 500/100/100/100 mẫu cho train/validation/early-stopping/test.
  - **Kết quả.** CLAP gốc (zero-shot, audio encoder HTS-AT, embedding d = 1024) tốt nhất **72,93%** accuracy trên validation với đoạn 4 s (thấp nhất 60,42% với 1 s). Thêm một lớp tuyến tính 1024 → 21 trên embedding CLAP đạt **91,83%** trên validation (4 s).
  - **Không báo số trên tập test, không có SED.** Câu kết của bài: bước tiếp theo là đưa mô hình vào pipeline SED.
  - Trong 6 trang, bài **không gọi tên DataSEC** và danh mục tham khảo không có DOI Zenodo.
- **Dự án học phần trên GitHub về DataSEC v4** (tác giả "goyumsamuditha", không phải bài bình duyệt) [V2] — [GitHub](https://github.com/goyumsamuditha/datasec-uncertainty-aware-sound-classification).
  - 4.292 clip, 22 lớp, 654 clip test.
  - CLAP linear probe 97,09% accuracy / 95,34% macro-F1; PANNs CNN14 95,72% / 92,03%; CLAP zero-shot 85,32% / 83,21%; SVM MFCC 85,63% / 75,71%.
  - Tác giả ghi rõ **không dựng được split theo nguồn** vì DataSEC "lacks reliable per-file source IDs".
- **Số phân loại của khóa luận** [V3, repo] — [06_ket_qua.md](../../report/final_src/06_ket_qua.md); [03_du_lieu.md](../../report/final_src/03_du_lieu.md).
  - Macro-F1 **0,8466** trên 22 lớp gộp, tập test DataSEC v3.
  - Chia 70/15/15 theo nhóm trùng `leakage_group`, ngưỡng gom 0,93.
- **Zhang S. & Virtanen T., *Cover First, Disagree Softly…*, arXiv:2607.13571v2** [repo V2] — [docs/RELATED_WORK.md §2.3 (21)](../../docs/RELATED_WORK.md).
  - Dùng nhãn đa âm DataSED nhưng chia ngẫu nhiên 6.808 đoạn 10 s theo tỷ lệ 8:1:1, CNN14 đóng băng.
  - Đo frame mAP/AULC (0,660): không phải SED event-based, không chia theo recording.
- **PolyBench, Chen Y. và cs., arXiv:2603.05128v4 (chấp nhận Interspeech 2026 theo repo)** [V2] — [arXiv HTML](https://arxiv.org/html/2603.05128v4); [docs/RELATED_WORK.md §2.3 (24)](../../docs/RELATED_WORK.md).
  - Dùng **169 clip** từ DataSED (3–89 s) có sự kiện chồng nhau, cho 5 tác vụ trắc nghiệm.
  - Bảng 1, accuracy: Qwen3-Omni-30B-A3B đạt Counting **57,5%**, Detection **63,4%**; Audio Flamingo 3 đạt 53,4% / 37,2%.
  - Tác vụ Detection "does not require LALMs to output precise timestamps".
  - Mô tả nguồn trong bài ("4,292 real-world samples across 22 sound event classes") thực ra là số của **DataSEC bản cũ**, nên mô tả nguồn tự mâu thuẫn.
- **Lượt tra 23/11/2026** (`"DataSED" OR "DataSEC" … Fredianelli 2026`; `"DataSED" polyphonic sound event detection arXiv`): chỉ trả về bài dataset, các record Zenodo, ResearchGate/PubMed và repo GitHub ở trên; **không có bài nào báo SED event-based** — [Zenodo DataSED](https://zenodo.org/records/15346092); [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12572321/). Kết luận này trùng với các lượt tra 26/09, 09/11 và 11/11 của repo — [docs/RELATED_WORK.md §10](../../docs/RELATED_WORK.md).

### Inferences
- **Câu phòng thủ an toàn:** "Theo phạm vi tra đến 23/11/2026 (không gồm cơ sở dữ liệu trả phí), chưa thấy công bố nào báo event-based F1 hay PSDS trên DataSED. Các công trình dùng dataset này là phân loại (FA2025), hỏi đáp trắc nghiệm của LALM (PolyBench) và frame mAP trên split ngẫu nhiên (Zhang & Virtanen). Vì vậy kết quả SED của khóa luận là mốc tham chiếu nội bộ, được kiểm soát bằng chọn trên dev/OOF và một lần mở test, chứ không phải so sánh SOTA."
- **Nếu hội đồng hỏi "sao phân loại DataSEC của các em thấp hơn 91–97%?"**, câu trả lời có bốn điểm:
  - (a) Khác phiên bản dữ liệu (v3 5.048 file so với v4/FA2025).
  - (b) Khác tập lớp (22 so với 21) và khác metric (macro-F1 so với accuracy). Accuracy bị `voices`/`music` (57,5% dữ liệu) chi phối.
  - (c) FA2025 chỉ báo trên validation.
  - (d) Cách chia: khóa luận chia theo nhóm trùng sau khi audit, đã tìm thấy cặp trùng xuyên dataset với similarity 1,000. Repo GitHub tự thừa nhận không chia theo nguồn được.
  - Giả thuyết **chưa kiểm**: một phần chênh lệch đến từ việc các đoạn cùng nguồn rơi vào cả train lẫn test ở split ngẫu nhiên.
- PolyBench là bằng chứng gián tiếp quý cho Câu hỏi 4: ngay cả LALM 30B mạnh nhất cũng chỉ đếm đúng 57,5% câu trắc nghiệm trên audio DataSED, mà không phải xuất timestamp.

### Gaps
- Chưa truy được "cited by" (Google Scholar/Scopus) của DOI 10.1038/s41597-025-05991-w. Có thể còn bài hội nghị Inter-Noise hoặc AIA, luận văn ở Ý chưa được index.
- FA2025 không ghi rõ con số 500/100/100/100 là theo lớp hay tổng, cũng không ghi đúng là DataSEC.
- PolyBench mới đọc qua tóm tắt WebFetch. Bảng và văn bản lệch nhau: văn bản ghi Concurrency 83,1%, bảng ghi 76,0% ACC.

## Câu hỏi 2. Dải giá trị điển hình trên ghi âm thật đa âm: đặt "event-F1 micro ≈ 0,30, 21 lớp, ghi âm thật" vào đâu cho trung thực?

### Takeaway
Cùng họ metric (collar onset 200 ms / offset 200 ms–20%), hệ CRNN baseline của DESED đạt F-score khoảng 0,37–0,41 và hệ đứng đầu 0,60–0,68 (clip 10 s, 10 lớp, ngưỡng 0,5, rất nhiều dữ liệu huấn luyện). Ghi âm thật kiểu TUT/DCASE 2016 chỉ đạt event-F1 khoảng 5% (chỉ onset, collar 250 ms). Event-F1 micro 0,2965 (macro 0,2356) của khóa luận nằm giữa hai mốc này và bằng khoảng **51% đồng thuận người–người đo trên chính DataSED (0,5785)**. PSDS của khóa luận dùng **đúng tham số scenario của DCASE**: PSDS-1 0,31–0,35 ngang CRNN baseline DESED (0,315–0,359), PSDS-2 0,61–0,75 nằm giữa CRNN baseline (0,54) và BEATs baseline (0,76–0,80). Các mốc này chỉ để định cỡ, khác dataset nên không so trực tiếp.

### Cited Findings
- **DCASE 2016 Task 3** (TUT Sound Events 2016, ghi âm thật; nhà 11 lớp, khu dân cư 7 lớp) [repo V3] — [kết quả DCASE 2016 T3](https://dcase.community/challenge2016/task-sound-event-detection-in-real-life-audio-results); [docs/RELATED_WORK.md §2.1 (4)](../../docs/RELATED_WORK.md).
  - Metric chính: ER theo đoạn 1 s.
  - Event-based dùng collar 250 ms, chỉ onset: baseline segment ER 0,8773 / F1 34,3%, event ER 1,7303 / **F1 6,3%**.
  - Top: Adavanne 0,8051 / 47,8%, event F1 4,8%. Event-F1 của nhóm top và baseline nằm trong khoảng **4,7–6,3%**.
- **DCASE 2017 Task 3** (TUT Sound Events 2017; 6 lớp đường phố: brakes squeaking, car, children, large vehicle, people speaking, people walking; 1 h 32 m / 24 bản ghi để train, 29 m / 8 bản ghi để đánh giá) [V2] — [kết quả DCASE 2017 T3](https://dcase.community/challenge2017/task-sound-event-detection-in-real-life-audio-results).
  - Chỉ báo metric theo đoạn: baseline ER **0,9358** / F1 **42,8%**.
  - Top theo ER: Adavanne_TUT_task3_1 0,7914 / 41,7%; Adavanne_2 0,8061 / 42,9%; Lee_SNU_3 0,8080 / 40,8%; Lu_THU_1 0,8251 / 39,6%.
  - Trang **không** báo event-based.
- **DCASE 2022 Task 4** (DESED, eval) [V2] — [kết quả DCASE 2022 T4](https://dcase.community/challenge2022/task-sound-event-detection-in-domestic-environments-results).
  - PSDS1 / PSDS2: baseline **0,315 / 0,543**; baseline "(AudioSet)" **0,345 / 0,540**; top Ebbers_UPB_task4_1 (ensemble CRNN) **0,552 / 0,786**. Team ranking của Ebbers dùng PSDS2 0,824 từ một submission khác.
  - "F-score" eval: baseline 37,3; baseline AudioSet 41,1; Ebbers_UPB_task4_1 59,8.
  - Trang không định nghĩa F-score.
- **DCASE 2023 Task 4a** (DESED, eval) [V2] — [kết quả DCASE 2023 T4a](https://dcase.community/challenge2023/task-sound-event-detection-with-weak-labels-and-synthetic-soundscapes-results).
  - Baseline **0,327 (0,317–0,339) / 0,538 (0,515–0,566)**; Baseline_BEATS **0,510 / 0,798**.
  - Top không ensemble: Kim_GIST-HanwhaVision **0,591 / 0,835**; Zhang_IOA 0,562 / 0,830; Wenxin_TJU 0,546 / 0,831; Xiao_FMSG 0,551 / 0,813; Guan_HIT 0,526 / 0,855.
  - Top có ensemble: Zhang_IOA **0,625 / 0,903**. CI tính từ 3 run cộng bootstrap.
  - F-score eval: baseline **0,377**, BEATs baseline **0,567**, Kim **0,684**.
- **Định nghĩa trên trang mô tả task DCASE 2023** [V2] — [task DCASE 2023 T4](https://dcase.community/challenge2023/task-sound-event-detection-with-weak-labels-and-synthetic-soundscapes).
  - PSDS scenario 1: DTC 0,7, GTC 0,7, α_ST 1, α_CT 0, e_max 100.
  - PSDS scenario 2: DTC 0,1, GTC 0,1, CTTC 0,3, α_CT 0,5, α_ST 1, e_max 100.
  - F-score: "event-based measures with a 200 ms collar on onsets and a 200 ms / 20% of the events length collar on offsets", ngưỡng **cố định 0,5**. Trang không ghi macro hay micro.
  - 10 lớp, clip 10 s.
  - Số trên tập dev: baseline 0,359 ± 0,006 / 0,562 ± 0,012; BEATs baseline 0,500 ± 0,004 / 0,762 ± 0,008.
- **Tham số PSDS của khóa luận trùng hệt DCASE**: S1 dtc/gtc 0,7, α_ct 0, α_st 1, max_efpr 100; S2 dtc/gtc 0,1, cttc 0,3, α_ct 0,5, α_st 1, max_efpr 100 [V3, repo] — [docs/evaluation_protocol.md §3.3](../../docs/evaluation_protocol.md).
- **DCASE 2024 Task 4** (DESED + MAESTRO, eval) [V2] — [kết quả DCASE 2024 T4](https://dcase.community/challenge2024/task-sound-event-detection-with-heterogeneous-training-dataset-and-potentially-missing-labels-results).
  - Baseline: PSDS (DESED) **0,475**, mpAUC (MAESTRO) **0,646**.
  - Top: Schmid_CPJKU_task4_2 **0,646 / 0,711**; Nam_KAIST 0,586 / 0,738; Zhang_BUPT 0,523 / 0,704; Chen_CHT 0,495 / 0,733; Kim_GIST 0,567 / 0,665. Top có ensemble: Schmid_CPJKU_task4_4 **0,680 / 0,739**.
  - Trang không định nghĩa công thức điểm xếp hạng.
- **MAESTRO Real (DCASE 2023 Task 4b, nhãn mềm, ghi âm thật)** [V2] — [kết quả DCASE 2023 T4b](https://dcase.community/challenge2023/task-sound-event-detection-with-soft-labels-results).
  - Baseline: F1_MO 43,44, ER_m 0,484, **F1_m (micro) 74,13**, **F1_M (macro) 35,28**.
  - Top: Bai_JLESS_task4b_4 F1_MO 60,74 / ER_m 0,320 / F1_m 81,01 / F1_M 37,33.
  - Một abstract định nghĩa F1_MO là "macro-average F1 score with optimum threshold per class". Trang không ghi độ dài đoạn.
- **STARSS23 (DCASE 2023 Task 3, SELD trên cảnh thật)** [V1/V2; số của bên thứ ba, không phải bảng chính thức] — [arXiv:2401.17129](https://arxiv.org/pdf/2401.17129).
  - Baseline audio-only SELDnet23 trên dev-test: ER20° 0,57, F20° **29,9%**, LE 21,6°, LR 47,7%.
  - F20° tính trên đoạn 1 s không chồng, kèm ngưỡng góc 20°.
- **RealDESED** (ghi âm nhà thật, 2026) [repo V3] — [docs/RELATED_WORK.md §2.3 (17)](../../docs/RELATED_WORK.md).
  - ATST-F, PSDS1-M (macro): raw 0,662, median 0,693, cSEBB 0,731.
  - PSDS1 chuẩn có variance penalty: 0,487 / 0,528 / 0,573.
- **Cances, Guyot, Pellegrini (WASPAA 2019, arXiv:1906.06909)**, DCASE 2018 Task 4 eval [V2] — [arXiv](https://arxiv.org/abs/1906.06909).
  - Event-based F-score 22,9% với phương pháp thống kê, lên 32,0% với phương pháp tham số theo lớp. Bài không ghi collar.
- **Trần người trên DataSED** [V3, repo] — [docs/PAPER_NOTES.md D6](../../docs/PAPER_NOTES.md).
  - Đo trên 8 cặp recording giống từng byte được gán nhãn hai lần: event-F1 người–người **0,5785** (collar 0,2 s) và 0,7603 (collar 1 s).
  - Cùng nguồn: nới collar làm event-F1 của v1-B tăng từ 0,062 (0,2 s) lên 0,185 (1 s) và 0,222 (2 s) ([PAPER_NOTES S8](../../docs/PAPER_NOTES.md)).
- **Đặc điểm DataSED** [V3, repo] — [03_du_lieu.md](../../report/final_src/03_du_lieu.md).
  - 717 bản ghi, trung bình khoảng 94 s, dài nhất 818,3 s.
  - 4.034 sự kiện đa âm thuộc 21 lớp, phủ 703 bản ghi.
  - Sự kiện dài 0,41–296,5 s, trung vị 5,8 s.

### Inferences
- **Bảng định cỡ đề xuất cho slide hoặc báo cáo** (mọi dòng là dataset khác, chỉ để định cỡ):

| Bối cảnh | Metric | Baseline | Top | Khóa luận (test) |
|---|---|---|---|---|
| DCASE 2016 T3, ghi âm thật | event-F1, chỉ onset, collar 250 ms | 6,3% | 4,7–6,3% | — (protocol chặt hơn: có cả offset) |
| DCASE 2017 T3, ghi âm thật | segment F1 / ER | 42,8% / 0,9358 | 41,7–42,9% / 0,79 | segment-F1 1 s: 0,5965 (V2) – 0,7821 (V3 recall_first) |
| DESED 2022–2023 (clip 10 s, 10 lớp) | F-score collar 200 ms / 20%, ngưỡng 0,5 | 0,373–0,411 | 0,598–0,684 | micro 0,2965, macro 0,2356 (điểm vận hành chọn trên OOF) |
| DESED 2022–2024 | PSDS1 / PSDS2 (cùng tham số) | 0,315–0,510 / 0,538–0,798 | 0,552–0,680 / 0,786–0,903 | 0,3061–0,3512 / 0,6116–0,7452 (lưới log) |
| MAESTRO Real 2023 | F1 micro / macro | 74,13 / 35,28 | 81,01 / 37,33–45,98 | micro/macro chênh nhau như vậy cũng xuất hiện ở khóa luận (0,2965 / 0,2356) |
| Trần người DataSED | event-F1 collar 0,2 s | — | 0,5785 | V2 ≈ 51% trần; B0 ≈ 31% trần |

- **Vì sao DataSED khó hơn DESED** (giải thích, không phải khẳng định số):
  - Bản ghi dài 94 s so với 10 s, có sự kiện tới 296,5 s; collar onset 200 ms vẫn chặt với sự kiện dài.
  - 21 lớp so với 10.
  - Chỉ 564 bản ghi có nhãn cho train + dev, không có dữ liệu weak/unlabeled cùng miền như DESED.
  - Chính người gán nhãn chỉ đồng thuận ở mức 0,5785.
  - Do đó việc macro 0,2356 thấp hơn F-score của CRNN baseline DESED (0,373–0,377) **không** phải bằng chứng hệ kém, mà cũng không được diễn giải là "tương đương".
- **Cách đọc PSDS:** tham số scenario trùng DCASE nên con số cùng thang. PSDS-1 của khóa luận ở mức CRNN baseline DESED; PSDS-2 của B0 (0,7452, lưới log) tiệm cận BEATs baseline DESED (0,762 trên dev / 0,798 trên eval). Nhưng PSDS phụ thuộc dataset, số lớp và lưới ngưỡng; chính khóa luận đã chứng minh lưới ngưỡng làm PSDS của LBR đổi từ 0,2146 lên 0,3512 (S66). Vì vậy chỉ được viết "cùng dải với", không viết "bằng".
- **Câu diễn đạt đề xuất:** "Event-F1 micro 0,30 với collar chặt trên ghi âm thật 21 lớp cao hơn nhiều mốc ghi âm thật DCASE 2016 (khoảng 5%, chỉ onset) và thấp hơn mốc clip tổng hợp/bán tổng hợp DESED (F-score 0,37–0,68). Con số này bằng khoảng một nửa mức đồng thuận người–người đo trên chính DataSED (0,58)."
- MAESTRO Real cho thấy chênh lệch micro/macro lớn là đặc trưng của ghi âm thật mất cân bằng lớp: micro 74–81 so với macro 35–46. Đây là căn cứ ngoài để giải thích việc khóa luận báo cả hai và macro thấp hơn.

### Gaps
- Chưa xác minh F-score DCASE 2022/2023 là macro: trang không ghi, quy ước DCASE thường là macro.
- Chưa có số STARSS23 chính thức từ trang DCASE.
- MAESTRO: chưa rõ độ dài đoạn và ngưỡng.
- Chưa có số đồng thuận người–người cho DESED để so "% trần".
- Trang kết quả DCASE 2017 không ghi độ dài đoạn: 1 s theo quy ước nhưng chưa kiểm trong lượt này.
- Mọi số DCASE ở đây là V2. Cần curl + trích văn bản như repo đã làm với DCASE 2016 trước khi đưa vào báo cáo.

## Câu hỏi 3. Encoder tiền huấn luyện cho SED: cái nào dùng ngay được làm bộ trích đặc trưng frame-level đóng băng, cho baseline hoặc cải thiện nhanh; DCASE 2024/2025 dùng gì?

### Takeaway
Xu hướng DCASE từ 2023 là transformer frame-level tiền huấn luyện (BEATs, ATST-Frame, PaSST) đóng băng hoặc fine-tune, thay cho CRNN học từ đầu. Khóa luận đã đi đúng xu hướng này: BEATs đóng băng, BEATs fine-tune và `frame_mn` lấy từ cùng họ checkpoint AudioSet-Strong của PretrainedSED. Bằng chứng nội bộ cho thấy encoder mạnh hơn (frame mAP 0,80) **không** chuyển thành event-F1, nên đổi encoder có kỳ vọng thấp trong 5 ngày. Thứ dùng ngay được và đáng làm nhất là **head 447 lớp AudioSet-Strong có sẵn trong các checkpoint**: nó cho một baseline zero-shot không cần huấn luyện trên DataSED. ATST-F là ứng viên T1. EAT, AudioMAE và CED không có checkpoint SED frame-level sẵn trong phạm vi tra.

### Cited Findings
- **Schmid và cs., *Effective Pre-Training of Audio Transformers for Sound Event Detection*, ICASSP 2025, arXiv:2409.09546v2** [repo V3] — [docs/RELATED_WORK.md §2.1 (2)](../../docs/RELATED_WORK.md); [PretrainedSED](https://github.com/fschmid56/PretrainedSED).
  - AudioSet Strong PSDS1, đủ pipeline: ATST-F 45,8, BEATs 46,5, fPaSST 45,4, M2D 46,3, ASiT 46,2.
  - DESED: fine-tune 47,6–49,2; **đóng băng 45,4–49,2** (M2D đóng băng 49,2 cao nhất).
  - Kết quả trên MAESTRO ngoài miền không cải thiện rõ.
  - Checkpoint đều có head **447 lớp**: `frame_mn10_strong_1.pt` khoảng 15,5 MB, `BEATs_strong_1.pt` khoảng 364 MB, `ATST-F_strong_1.pt` khoảng 344 MB.
  - License: repo MIT; checkpoint ATST-F CC BY 4.0; M2D có license riêng nên repo loại.
- **Shao N., Li X., Li X., *Fine-tune the pretrained ATST model for sound event detection*, ICASSP 2024 (arXiv:2309.08153)** [V2] — [arXiv](https://arxiv.org/abs/2309.08153).
  - Abstract báo **0,587 / 0,812** PSDS1/PSDS2 trên dữ liệu DCASE Task 4; abstract không ghi split.
- **DCASE 2023 T4a** [V2] — [task](https://dcase.community/challenge2023/task-sound-event-detection-with-weak-labels-and-synthetic-soundscapes); [kết quả](https://dcase.community/challenge2023/task-sound-event-detection-with-weak-labels-and-synthetic-soundscapes-results).
  - Baseline BEATs đưa "frame-level embeddings … in a late-fusion fashion with the existing CRNN baseline classifier".
  - PSDS1 trên eval tăng từ 0,327 lên **0,510**, PSDS2 từ 0,538 lên **0,798**.
- **DCASE 2022 T4** [V2] — [kết quả DCASE 2022 T4](https://dcase.community/challenge2022/task-sound-event-detection-in-domestic-environments-results).
  - Bản baseline "(AudioSet)" dùng embedding tiền huấn luyện AudioSet (tên PANNs là theo hiểu biết, chưa xác minh trên trang) chỉ tăng PSDS1 từ 0,315 lên 0,345, còn PSDS2 giảm nhẹ từ 0,543 xuống 0,540.
- **DCASE 2024 T4** [V2] — [kết quả DCASE 2024 T4](https://dcase.community/challenge2024/task-sound-event-detection-with-heterogeneous-training-dataset-and-potentially-missing-labels-results).
  - Tên hệ thống cho thấy dùng ATST (Schmid_CPJKU "ATST S2.I2", Cai "MAT-ATST", Lee "FDY-CRNN_with_ATST_and_BEATs"), BEATs (Lyu "CCRN_BEATs") và PaSST (ensemble CPJKU "Ensemble_15 ATST, BEATs, PaSST").
  - Hạng 1 CPJKU dùng fine-tune nhiều vòng, nhiều giai đoạn kèm KD từ ensemble; ATST DT + cSEBB đạt 0,692 trên DESED public eval ([docs/RELATED_WORK.md §2.3 (18)](../../docs/RELATED_WORK.md), repo V3).
- **DCASE 2025 Task 4 không phải SED** mà là *Spatial Semantic Segmentation of Sound Scenes* (S5): tách và gán nhãn sự kiện từ tín hiệu đa kênh, tối đa 3 sự kiện đồng thời [V2] — [arXiv:2506.10676](https://arxiv.org/html/2506.10676v1); [trang task](https://dcase.community/challenge2025/task-spatial-semantic-segmentation-of-sound-scenes).
  - DCASE 2026 Task 4 tiếp tục S5 [V1 + repo] — [docs/RELATED_WORK.md §10 (08/10)](../../docs/RELATED_WORK.md).
  - Như vậy chuỗi "DESED SED" của DCASE dừng ở 2024.
- **Bằng chứng nội bộ của khóa luận** [V3, repo] — [docs/PAPER_NOTES.md S28, S32, S51, S53, S55, S56](../../docs/PAPER_NOTES.md).
  - BEATs đóng băng + BiGRU (T2a) ngang CNN14 fine-tune (CV dev 0,2114 so với 0,2129).
  - `frame_mn10` 3M tham số ngang mô hình 80–90M.
  - BEATs fine-tune (O-D) có frame mAP **0,8023** nhưng event-F1 OOF chỉ **0,2052**, thấp hơn B0 0,2342: Δ −0,0290 [−0,0546; +0,0001].
  - Ba ứng viên thắng ở tầng S (TF256-KD, TF256, O-D) đều đảo chiều ở tầng C.
- **EfficientSED (Morocutti và cs., EUSIPCO 2025)** [repo V3] — [docs/RELATED_WORK.md §2.3 (16)](../../docs/RELATED_WORK.md).
  - fmn10 có KD 42,28; thêm TF256 43,86; KD mở rộng 45,25 (PSDS1 AudioSet Strong, 407 lớp eval).
- **FLAM (Wu và cs., ICML 2025, arXiv:2505.05335)**, CLAP frame-level cho open-vocabulary SED [V2] — [arXiv HTML](https://arxiv.org/html/2505.05335v2).
  - DESED PSDS **9,37** (FLAM) so với MGA-CLAP 14,72 (huấn luyện lại) và **26,4** (số tự báo của MGA-CLAP).
  - Đầu vào cố định 10 s, khoảng 0,3125 s mỗi frame.
  - Tác giả nêu giới hạn với bản ghi dài.

### Inferences
- **Dùng ngay được trong vài ngày:** BEATs-strong, ATST-F-strong, fPaSST-strong (đều có trong PretrainedSED, cùng frontend và head 447 lớp) cùng `frame_mn10` mà repo đã vendor. M2D bị loại vì license, nên nếu hội đồng hỏi "sao không dùng M2D, frozen tốt nhất DESED 49,2?" thì đã có câu trả lời ở ADR-0032.
- **Không dùng ngay được:** EAT, AudioMAE, CED. Trong phạm vi tra không thấy checkpoint SED frame-level AudioSet-Strong công khai cho các model này; dùng chúng phải tự huấn luyện head frame-level, việc này thuộc T1/T2.
- **Baseline nhanh nhất có giá trị:** suy luận zero-shot bằng head 447 lớp AS-Strong (BEATs hoặc ATST-F hoặc frame_mn10), ánh xạ nhiều-về-một sang 21 lớp DataSED bằng max xác suất, chọn θ hoặc cSEBB trên 564 bản ghi train ∪ dev có nhãn (không cần cross-fit vì mô hình không học trên DataSED), rồi mở test một lần đã ghi trước. Baseline này trả lời câu "một mô hình SED tổng quát có sẵn làm được bao nhiêu khi không học gì trên DataSED?", đúng loại so sánh hội đồng thích đòi (xem Câu hỏi 7).
- **Kỳ vọng về đổi encoder:** thấp đối với event-F1. Bằng chứng nội bộ (S55, S56) và LBR (+0,0990 OOF) cùng chỉ ra nút thắt nằm ở dựng event từ posterior. Điều này khớp văn liệu boundary-aware (CRNN PSDS1 41,1 → 48,0 trên AS-Strong, [docs/RELATED_WORK.md §2.3 (15)](../../docs/RELATED_WORK.md)).
- CLAP và FLAM zero-shot có PSDS rất thấp trên DESED (0,09–0,26), xa SED có giám sát (0,5+). Đây là căn cứ để nói "CLAP không thay được SED khi cần timestamp".

### Gaps
- Chưa có số ATST-F trên DataSED (repo chưa chạy).
- Chưa kiểm danh sách 447 lớp AS-Strong cho ánh xạ: `workshop`, `chicken_coop`, `cicadas_and_crickets`, `vehicle_idling` cần xem có lớp tương ứng không.
- Chưa có số SED frame-level của EAT, CED, AudioMAE.
- Abstract ATST-SED không ghi split. Định nghĩa "PSDS (DESED)" của DCASE 2024 chưa đọc.

## Câu hỏi 4. LALM end-to-end ("sao không cho Gemini/Qwen-Omni nghe trực tiếp?"): grounding thời gian, hallucination, audio dài; head-to-head có khả thi trên 1 GPU 8 GB không và nên thiết kế thế nào?

### Takeaway
Văn liệu 2025–2026 cho câu trả lời khá nhất quán. Dùng **zero-shot**, LALM yếu ở định vị thời gian:
- Qwen2.5-Omni-7B chỉ đạt **Eb-F1 13,7** trên DESED với tolerance 0,2 s; Qwen2-Audio-7B đạt 3,4.
- Trên TAG-Bench, hệ tốt nhất chỉ đạt mIoU 31,2, Gemini-3.1-Pro 26,4, và mọi model báo thiếu 79–100% số lần xuất hiện khi một câu hỏi có nhiều khoảng đúng.
- LALM có thiên lệch "có" mạnh nhất ở âm thanh môi trường (HalluAudio), giảm hiệu năng khi audio dài (BLAB) và khi đa âm (PolyBench, trên chính audio DataSED).

Tuy vậy, LALM **được fine-tune** (SFT/RL trên 15 nghìn mẫu DESED) đạt Eb-F1 49–58, nên câu đúng là "LALM có sẵn chưa làm được, và muốn làm được cần nhiều nhãn mạnh hơn DataSED có", không phải "LALM không làm được". Một head-to-head nhỏ **khả thi** chỉ trên dev: Qwen2.5-Omni-7B GGUF Q4_K_M 4,68 GB qua llama.cpp, khoảng 40 bản ghi dev, dưới 2 GPU-giờ.

### Cited Findings
- **Shi Y. và cs., *Towards Fine-grained Temporal Perception: Post-Training LALMs with Audio-Side Time Prompt*, arXiv:2604.13715 (15/04/2026; "Submitted to Interspeech 2026")** [V2] — [arXiv HTML](https://arxiv.org/html/2604.13715).
  - SED trên DESED (15.041 mẫu train / 1.153 mẫu test), Eb-F1 tolerance 0,2 s; bài không ghi macro hay micro.
  - Zero-shot: Qwen2-Audio-7B **3,4**, Qwen2.5-Omni-7B **13,7**. Audio-Flamingo2-3B fine-tune đạt 8,9.
  - SFT: Qwen2-Audio 49,8, Qwen2.5-Omni 48,9, Kimi-Audio 50,9. TimePro-RL: 58,4 / 57,6.
  - Grounding trên FTAR, mIoU zero-shot: Qwen2-Audio 11,9, Qwen2.5-Omni 27,7.
  - Bài không có baseline SED truyền thống.
- **Dai Y. và cs., *TAG-Bench: Benchmarking Temporal Audio Grounding in Large Audio Language Models*, arXiv:2609.01542v2 (02/09/2026)** [V2] — [arXiv HTML](https://arxiv.org/html/2609.01542v2).
  - 1.750 cặp truy vấn–bản ghi, 149,5 h, bản ghi trung bình **307,6 s**, dài nhất 1.200 s; 22,1% truy vấn có từ 2 khoảng đúng trở lên.
  - 21 hệ thống, mIoU / R@0,7: FireRedAudio **31,2 / 21,5** (cao nhất); MOSS-Audio-8B-Thinking 29,6 / 18,2; **Gemini-3.1-Pro 26,4 / 13,7**; LAT-Audio 19,7 / 8,3; TimeAudio 12,4 / 3,1; MiMo-Audio-7B 12,2 / 3,4; **Audio Flamingo 3 8,7 / 2,0**; Kimi-Audio-7B 1,4 / 0,2.
  - Câu hỏi nhiều khoảng đúng bị **báo thiếu 79,3–100%** (Gemini-3.1-Pro 82,1%); độ đúng số lần cao nhất chỉ 13,2%.
  - Ở hai tập con dài, FireRedAudio đạt 20,6 / 21,7, MOSS-8B-Thinking chỉ 4,8 / 4,1. Tác giả lưu ý độ dài bị nhiễu bởi nguồn dữ liệu và phân bố truy vấn.
  - Benchmark không có baseline SED, CLAP hay FLAM.
- **HalluAudio (Zhao F. và cs., arXiv:2604.19300v1, 21/04/2026)** [V2] — [arXiv HTML](https://arxiv.org/html/2604.19300).
  - Tập con âm thanh có khoảng 1.958 câu hỏi–đáp, thuộc 7 tác vụ, gồm "mismatched query" (hỏi về một âm không có mặt).
  - Accuracy trung bình (mismatched query trong ngoặc): Qwen2.5-Omni **84,69 (98,17)**; MiMo-Audio 82,52 (95,33); Step-Audio-2 72,64 (62,65); GPT-4o-Audio 71,00 (39,84); **Qwen2-Audio 67,36 (11,43)**; Audio Flamingo-3 64,79 (83,67); Gemini-2.5-Flash 39,35 (78,24); Kimi-Audio 38,76 (6,40).
  - Nguyên văn: "affirmative bias is most pronounced in environmental sound tasks".
  - Venue ACL 2026 chưa xác minh.
- **Kuan C.-Y. & Lee H., *Can Large Audio-Language Models Truly Hear?…*, ICASSP 2025 (arXiv:2410.16130)** [V2] — [arXiv](https://arxiv.org/abs/2410.16130).
  - LALM "hallucinating non-existent sound events, misidentifying the order of sound events"; chain-of-thought nhiều lượt cải thiện kết quả. Abstract không có số.
  - ECHO (Kuan, Huang, Lee 2024) đã ở mức V3 trong repo ([docs/RELATED_WORK.md §2.4 (29)](../../docs/RELATED_WORK.md)).
- **PolyBench trên audio DataSED** [V2] — [arXiv HTML](https://arxiv.org/html/2603.05128v4). Qwen3-Omni-30B-A3B Counting 57,5% / Detection 63,4%; Audio Flamingo 3 53,4% / 37,2%. Bài kết luận LALM "clear performance degradation under polyphonic conditions"; điểm Concurrency cao bị thổi phồng do thiên lệch Yes/No.
- **DCASE 2025 Task 5 (Audio QA), eval** [V2] — [kết quả DCASE 2025 T5](https://dcase.community/challenge2025/task-audio-question-answering-results).
  - Phần 2, mà tôi suy là *Temporal Soundscapes QA* (trang chỉ ghi Part 1/2/3): Qwen2-Audio 38,52, AudioFlamingo2 32,18, Gemini 2.0 Flash **43,18**, Kimi-Audio 42,58.
  - Top có xếp hạng 65,31 (Sun_Antgroup); hệ "additional" không xếp hạng 74,52.
- **Audio Flamingo 3 kèm grounding frame-level (arXiv:2609.15215)** [V1, snippet] — [arXiv HTML](https://arxiv.org/html/2609.15215). Trên DCASE 2025 T5 temporal soundscapes (dev), accuracy tăng từ 57,80% lên 71,26%; tăng nhiều nhất ở câu hỏi onset/offset.
- **BLAB: Brutally Long Audio Bench (arXiv:2505.03054, ICML 2025)** [V1/V2 qua snippet] — [arXiv](https://arxiv.org/abs/2505.03054).
  - Clip trung bình 51 phút; hiệu năng audio LM "declining as duration increases".
  - Kém ở định vị, suy luận thời gian và đếm; khoảng cách lớn giữa model mở và Gemini.
- **MMAU** (trắc nghiệm, không đòi timestamp) [V1] — [trang MMAU](https://www.cs.umd.edu/content/mmau-massive-multi-task-audio-understanding-and-reasoning-benchmark).
  - Tổng: Gemini 2.0 Flash 59,93%, Qwen2-Audio 52,50%.
  - Báo cáo Qwen2.5-Omni [V2] ghi MMAU Sound: Qwen2.5-Omni-7B **67,87**, Qwen2-Audio 54,95, Gemini-Pro-V1.5 56,75 — [arXiv:2503.20215](https://arxiv.org/html/2503.20215).
- **Qwen2.5-Omni (arXiv:2503.20215)** [V2] — [arXiv HTML](https://arxiv.org/html/2503.20215).
  - Audio encoder khởi tạo từ Whisper-large-v3; 16 kHz, 128 mel.
  - "each frame of audio representation roughly corresponds to a 40ms segment"; TMRoPE dùng ID thời gian tuyệt đối 40 ms; attention theo khối 2 s.
  - Không ghi độ dài audio tối đa.
- **llama.cpp hỗ trợ Qwen2.5-Omni** (đầu vào audio + ảnh, không xuất tiếng) qua libmtmd, PR #13784; ggml-org phát hành GGUF 3B và 7B [V2] — [llama.cpp multimodal.md](https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md); [commit #13784](https://cdn04132025.gitlink.org.cn/replica/llama.cpp/commit/bc583e3c63c04a11d287c108ea9e6a515ead0423).
  - Bản 7B: Q4_K_M **4,68 GB**, Q8_0 8,1 GB, F16 15,2 GB ([HF ggml-org/Qwen2.5-Omni-7B-GGUF](https://huggingface.co/ggml-org/Qwen2.5-Omni-7B-GGUF)).
  - Tài liệu cũ hơn ghi audio "highly experimental", có thể giảm chất lượng (theo tóm tắt tìm kiếm).
- **SAR-LM (Taheri, Ma, Benetos, arXiv:2511.06483, 11/2025)**, pipeline biểu diễn ký hiệu: audio → đặc trưng có cấu trúc, đọc được → LLM [V2] — [arXiv](https://arxiv.org/abs/2511.06483).
  - Đánh giá trên MMAU/MMAR/OmniBench, "competitive results", nhấn mạnh truy vết lỗi được.
  - Theo repo, SAR-LM dùng tag PANNs có timestamp và ghi nhận model 7B "frequently hallucinated" ([ADR-0022](../../docs/decisions/ADR-0022-llm-va-lexicon-cho-rq2.md)).
- **Phần cứng của đề tài:** RTX 3070 Laptop 8 GB [V3, repo] — [docs/SYSTEM.md](../../docs/SYSTEM.md). GPU hạ xung nhiệt ở 88–91 °C ([PAPER_NOTES S54](../../docs/PAPER_NOTES.md)).

### Inferences
- **Trả lời hội đồng (gợi ý 4 ý):**
  1. **Đo được, không phải cảm tính:** LALM có sẵn yếu ở đúng thứ khóa luận cần, tức timestamp và đếm sự kiện lặp: DESED Eb-F1 13,7 (Qwen2.5-Omni-7B); TAG-Bench mIoU ≤ 31,2, R@0,7 ≤ 21,5%; báo thiếu 79–100% số lần xuất hiện.
  2. **DataSED rơi đúng vùng LALM yếu nhất:** bản ghi trung bình 94 s, dài tới 818 s; khoảng 5,7 sự kiện mỗi bản ghi (4.034/703); đa âm. Kết hợp với BLAB, PolyBench và TAG-Bench, đây là suy luận, không phải số đo trên DataSED.
  3. **Grounding và kiểm chứng:** pipeline giữ LLM ngoài khâu nghe. LLM chỉ diễn đạt danh sách sự kiện có mã bằng chứng, nên mọi sai sót truy được về một sự kiện SED. Ngược lại, LALM có thiên lệch "có" mạnh nhất ở âm thanh môi trường (Qwen2-Audio chỉ đúng 11,43% câu mismatched query).
  4. **Không nói quá:** LALM fine-tune đạt Eb-F1 49–58 trên DESED và Gemini-3.1-Pro đứng gần đầu TAG-Bench. Hạn chế thật của hướng LALM với đề tài là dữ liệu (DataSED chỉ có 438 bản ghi train, 564 nếu gộp dev, so với 15.041 mẫu DESED dùng để SFT), chạy cục bộ/offline, và khả năng tái lập (model đóng thay phiên bản).
- **Thiết kế head-to-head khả thi (T0, chỉ dev, không chạm test):**
  - **Model:**
    - Qwen2.5-Omni-7B Q4_K_M chạy qua `llama-server`/`llama-mtmd-cli`. Repo đã chạy llama.cpp cho Qwen3.5-9B Q4_K_M, nên hai model phải chạy lần lượt, không cùng lúc.
    - Dự phòng: Qwen2.5-Omni-3B nếu 7B + mmproj + KV cache vượt 8 GB.
    - Ước tính VRAM (suy luận, chưa đo): 4,68 GB + mmproj của encoder kiểu Whisper-large-v3 (khoảng 1,3 GB nếu f16) + KV cache khoảng 2,5 nghìn token audio cho 94 s (25 token/s) ≈ 6,5–7 GB.
  - **Dữ liệu:** khoảng 40 bản ghi trong 134 bản ghi dev annotated, chọn bằng seed cố định, phân tầng theo số lớp và theo khoảng thời lượng.
    - Bản ghi trên 120 s cắt cửa sổ 30 s không chồng rồi cộng offset tuyệt đối.
    - Ghi trước danh sách bản ghi kèm hash.
  - **Prompt:** tập đóng 21 lớp (tên + mô tả ngắn lấy từ taxonomy), yêu cầu JSON `{class, onset_s, offset_s}`.
    - Hai chế độ: (a) JSON bị ràng buộc bằng GBNF để luôn parse được; (b) tự do, để đo tỷ lệ parse fail như TAG-Bench.
    - Nhiệt độ 0. Thêm một câu hỏi mức bản ghi "các lớp nào có mặt?".
  - **Đối chứng hallucination:**
    - (i) Cùng prompt trên đoạn chỉ có nền hoặc nhiễu hồng cùng độ dài.
    - (ii) Câu hỏi có/không về một lớp chắc chắn vắng mặt trong GT, kiểu mismatched query của HalluAudio.
  - **Metric:**
    - Tỷ lệ lớp bịa so với **GT** (H_gt, cùng công thức H của RQ2 nhưng so với nhãn gốc) và tỷ lệ bỏ sót O_gt.
    - Event-F1 cùng cấu hình `sed_eval`; F1 giao nhau (DTC/GTC 0,1).
    - Sai số tuyệt đối onset trên các cặp khớp; độ đúng số lần theo cặp (lớp, bản ghi); tỷ lệ parse fail; thời gian và VRAM.
  - **Mốc so:** sự kiện OOF cross-fit của B0, LBR V2 và LBR V3 trên **cùng** bản ghi dev (đã có, không cần test). Bootstrap ghép cặp theo bản ghi; với n = 40, CI sẽ rộng nên báo dạng mô tả.
  - **Ghi trước** bằng một ADR mới (repo có quy trình): model hash, prompt, giải mã, danh sách bản ghi, metric. Kết quả chỉ là minh họa trên dev, không kết luận "tốt hơn".
  - **Kỳ vọng:** dựa trên 13,7 Eb-F1 (DESED zero-shot) và hiện tượng báo thiếu của TAG-Bench, event-F1 của LALM nhiều khả năng thấp hơn xa LBR (OOF 0,3332). Phát hiện lớp ở mức bản ghi có thể gần hơn. Phải báo cả hai, kể cả khi LALM thắng ở mức bản ghi.
- **Gemini/GPT-4o:** chỉ nên chạy (T1) nếu nhóm chấp nhận gửi audio CC BY-NC-SA lên API và ghi rõ phiên bản model.
  - Không tái lập được lâu dài, nên chỉ dùng làm minh họa.
  - TAG-Bench và DCASE 2025 T5 đã cung cấp số Gemini để trích thay vì phải chạy.

### Gaps
- Chưa có số LALM nào làm SED (timestamp) trên DataSED.
- Chưa rõ kích thước mmproj của Qwen2.5-Omni-7B, độ dài audio tối đa, và chất lượng audio trong llama.cpp so với bản HF bf16.
- Chưa kiểm Qwen3-Omni-30B-A3B có chạy được trên 8 GB không; nhiều khả năng không, nếu không lượng tử hóa nặng.
- Chưa đọc trực tiếp bảng gốc của TAG-Bench, HalluAudio, 2604.13715 và DCASE 2025 T5. Ánh xạ Part 2 = Temporal Soundscapes là suy luận.
- Abstract của Kuan & Lee 2025 không có số.

## Câu hỏi 5. Audio retrieval, audio RAG và caption có căn cứ: công trình nào gần nhất, khóa luận khác ở đâu, có thêm nhanh được baseline CLAP không?

### Takeaway
Gần nhất vẫn là **LA-RAG (2026)**: audio → bản ghi sự kiện có timestamp → kho SQL → LLM. Mới xuất hiện sau lượt tra 11/11 có **HARP (SLT 2026)**, kết luận "hybrid keyword + vector là cấu hình vững nhất", ủng hộ thiết kế hybrid của khóa luận. Khóa luận khác ở bốn điểm:
- Vị từ quan hệ **giữa hai sự kiện** viết bằng SQL.
- Câu trả lời tất định kèm bộ đếm khẳng định thiếu bằng chứng (0,000).
- Caption bị ràng buộc bằng ngữ pháp.
- Provenance qua hash.

Một baseline **CLAP retrieval** (không SED) làm được trong khoảng 1 ngày, vài phút GPU. Nó sẽ cô lập giá trị của SED + bộ lọc: kỳ vọng tốt ở truy vấn một lớp, không biểu diễn được before/after/thời lượng.

### Cited Findings
- **LA-RAG / LongAudio-RAG (Hegde và cs., arXiv:2602.14612v4, 2026)** [repo V3] — [arXiv](https://arxiv.org/abs/2602.14612); [docs/RELATED_WORK.md §2.4 (26)](../../docs/RELATED_WORK.md).
  - AGM (CNN + BiGRU) sinh bản ghi (sự kiện, start, end, confidence, loudness) lưu trong SQLite.
  - Truy xuất theo intent kèm cửa sổ thời gian tuyệt đối, rồi LLM sinh câu trả lời. Offline 76,88% (Home-IoT), 71,10% (Industrial-IoT).
  - Không thấy vị từ quan hệ giữa hai sự kiện.
- **HARP: Agentic Hybrid Retrieval and Analysis for Long-Form Audio (Li C.-J., …, Watanabe S., arXiv:2609.14116, SLT 2026)** [V2] — [arXiv](https://arxiv.org/abs/2609.14116).
  - Hybrid retrieval (keyword + vector) là cấu hình vững nhất.
  - Ghép metadata với audio truy hồi được làm accuracy câu trả lời tăng khoảng **10%** và accuracy lập luận khoảng **6%**.
  - Nguyên văn: accuracy câu trả lời đơn thuần "overestimates system capability".
  - Abstract không nói rõ đánh chỉ mục sự kiện SED hay embedding CLAP.
- **Các công trình RAG audio dài khác** [V1, chỉ thấy tiêu đề/danh mục tham khảo] — [PlanRAG-Audio](https://arxiv.org/pdf/2605.20414); [GRGA](https://arxiv.org/html/2608.24048).
  - PlanRAG-Audio (arXiv:2605.20414): lập kế hoạch + RAG cho audio dài.
  - GRGA (arXiv:2608.24048): agent truy hồi dạng đồ thị cho audio cuộc họp, kèm tập LongAudioQA.
- **Mốc retrieval của CLAP** (theo Bảng 2 của bài FLAM), R@1 text→audio / audio→text [V2] — [FLAM arXiv HTML](https://arxiv.org/html/2505.05335v2).
  - LAION-CLAP: AudioCaps **36,1 / 46,8**, Clotho **16,1 / 22,7**.
  - FLAM: 32,1 / 43,3 và 13,8 / 16,7.
- **CLAP zero-shot trên dữ liệu kiểu DataSEC** [V3 / V2] — [PDF FA2025](https://dael.euracoustics.org/confs/fa2025/data/articles/000340.pdf); [GitHub](https://github.com/goyumsamuditha/datasec-uncertainty-aware-sound-classification).
  - FA2025: 72,93% accuracy trên validation, đoạn 4 s, 21 lớp [V3].
  - Repo học phần: 85,32% accuracy / 83,21% macro-F1 trên DataSEC v4 [V2].
- **CLAP và FLAM không định vị tốt:** DESED PSDS 9,37 (FLAM) và 26,4 (MGA-CLAP, tự báo); đầu vào cố định 10 s [V2] — [FLAM](https://arxiv.org/html/2505.05335v2).
- **Caption có căn cứ hoặc có timestamp** [repo V3] — [docs/RELATED_WORK.md §2.4](../../docs/RELATED_WORK.md).
  - TAC (Kumar và cs. 2026): Hal% đo bằng FLAM với τ = 0,25, kèm EvtF1/SegF1.
  - ECHO (Kuan và cs. 2024): ECHO-I/ECHO-S theo kiểu CHAIR.
  - Xie và cs. (2024): quan hệ thời gian trong caption, đang ở V2.
- **Số RQ3 của khóa luận** [V3, repo] — [06_ket_qua.md](../../report/final_src/06_ket_qua.md); [PAPER_NOTES S37, R4, R5](../../docs/PAPER_NOTES.md).
  - Độ đúng bộ lọc 1,000; khẳng định thiếu bằng chứng 0,000.
  - nDCG@10 hybrid/EN với bộ lọc gold: 0,383 (B0), 0,404 (V2), 0,670 (V3; hiệu ứng độ phủ, trích đúng GT 0,712 so với 0,915).
  - Parser: đúng ngữ nghĩa hoàn toàn 0,855 (template) / 0,925 (diễn đạt lại).

### Inferences
- **Định vị so với văn liệu:** LA-RAG và HARP cho thấy kiến trúc "SED/metadata → kho có cấu trúc → hybrid retrieval → LLM" là hướng được cộng đồng chấp nhận năm 2026. Khóa luận không nên tuyên bố mới về kiến trúc. Đóng góp nằm ở:
  - (i) Vị từ Allen giữa hai sự kiện, có bộ kiểm SQL ↔ Python.
  - (ii) Đánh giá bộ lọc gold so với parsed, tách lỗi parser.
  - (iii) Câu trả lời ràng buộc bằng chứng, đo được tỷ lệ khẳng định thiếu bằng chứng.
  - (iv) Caption có ngữ pháp với G1–G3 kiểm bằng máy.
  - (v) Provenance đầy đủ.
  - HARP còn cảnh báo accuracy câu trả lời thổi phồng năng lực. Điều này trùng với cách khóa luận báo "trích đúng GT" cạnh nDCG.
- **Thiết kế baseline CLAP (T0):**
  - **Mã hóa:** LAION-CLAP hoặc MS-CLAP; mỗi bản ghi chia cửa sổ 10 s, bước 5 s.
  - **Điểm bản ghi:** max (hoặc trung bình top-3) cosine giữa embedding câu truy vấn tiếng Anh và các cửa sổ.
  - **Truy vấn nhiều lớp:** thử hai cách, (a) toàn câu; (b) tích hoặc min điểm theo từng lớp.
  - **Chọn cấu hình** (cách gộp, cửa sổ) trên **validation** (134 bản ghi dev, cùng 100 truy vấn), rồi mở test một lần với nDCG@10 theo bốn nhóm truy vấn.
  - **Kỳ vọng:** cạnh tranh ở truy vấn một lớp (CLAP zero-shot 73–85% accuracy trên dữ liệu kiểu DataSEC); kém hoặc vô nghĩa ở truy vấn quan hệ thời gian và thời lượng, vì không có cơ chế lọc. Đây là phép đo trực tiếp cho câu "vì sao cần SED + bộ lọc cứng".
- **Biến thể T1:** dùng embedding audio CLAP làm cột vector trong pgvector thay cho embedding text BGE-M3 của tài liệu template, giữ nguyên bộ lọc cứng. Cách này kiểm "vector âm thanh hay vector mô tả".
  - CLAP text encoder chỉ hỗ trợ tiếng Anh (cần kiểm), nên truy vấn tiếng Việt vẫn cần BGE-M3 hoặc dịch.
  - Đây là một lý do thiết kế để trả lời hội đồng.

### Gaps
- Chưa kiểm license checkpoint LAION-CLAP và MS-CLAP; cần chạy cổng license như ADR-0032.
- Chưa có số CLAP trên bản ghi dài kiểu DataSED.
- Chưa đọc toàn văn HARP, PlanRAG-Audio, GRGA để biết có so với LA-RAG hay LALM end-to-end không.
- Chưa xác minh text encoder của LAION-CLAP/MS-CLAP chỉ hỗ trợ tiếng Anh.

## Câu hỏi 6. Kỹ thuật hậu xử lý và cải thiện SED nhanh có số báo cáo: repo đã làm gì, còn lại gì?

### Takeaway
Repo đã làm gần hết các "quick win" chuẩn: θ chung so với θ theo lớp, median filter, ensemble, cSEBB, suy luận chồng lấn, focal loss, KD, pseudo-label, tăng cường dữ liệu. Thêm vào đó là một kỹ thuật vượt chuẩn (LBR, +0,0990 OOF, +0,1159 test). Phần lớn chỉ là kết quả âm tính hoặc trung tính, trừ độ phân giải thời gian và LBR. Còn lại: hysteresis (có code, chưa đo), TTA dịch thời gian/tần số (không tìm được nguồn SED báo lợi ích), LBR trên ensemble liên họ (thăm dò +0,014, CI chạm 0), mở rộng lưới ngưỡng rescorer, mean-teacher với dữ liệu không nhãn. Không mục nào có kỳ vọng lớn trong 5 ngày.

### Cited Findings
- **cSEBB (Ebbers, Germain, Wichern, Le Roux, Interspeech 2024):** trên 13 hệ DCASE 2023 T4a, trung bình **+4,1 PSDS1 / +3,4 F1** so với median filter, cùng collar với đề tài [repo V3] — [docs/RELATED_WORK.md §2.1 (1)](../../docs/RELATED_WORK.md).
  - Trong repo, cSEBB thua θ chung trên posterior đã làm mượt (v1, v2, T2a) và thắng trên T2b 40 ms ([PAPER_NOTES S14, S25, S29, S33](../../docs/PAPER_NOTES.md)). B0 dùng cSEBB.
- **RealDESED:** PSDS1-M raw 0,662 → median 0,693 → cSEBB 0,731; bước suy luận 10 → 2,5 s cho 0,711 → 0,736 [repo V3] — [docs/RELATED_WORK.md §2.3 (17)](../../docs/RELATED_WORK.md).
  - Trong repo, suy luận chồng lấn tăng θ nhưng không tăng hệ sau cSEBB ở tầng S; ở OOF có ích (h5 tam giác 0,2336 so với h10 0,2201) và được đưa vào B0 ([PAPER_NOTES S49, S52](../../docs/PAPER_NOTES.md)).
- **Boundary-aware SED (Schmid và cs., IEEE SPL 2026):** CRNN PSDS1 41,1 → 48,0, collar-F1 32,3 → 40,6 (SEBB → RED + loss onset/offset + EPN, AS-Strong-10) [repo V3] — [docs/RELATED_WORK.md §2.3 (15)](../../docs/RELATED_WORK.md).
  - Repo thử RED đơn lẻ (O-E1): âm tính, 0,2188 so với 0,2330. EPN chưa làm ([PAPER_NOTES S51](../../docs/PAPER_NOTES.md)).
- **Độ phân giải thời gian (Boes & Van hamme, báo cáo kỹ thuật DCASE 2021 T4, arXiv:2210.10208)** [V2] — [arXiv](https://arxiv.org/abs/2210.10208).
  - Đổi pooling của CRNN mean-teacher nâng PSDS kịch bản "lax" từ 0,527 lên **0,7312** trên validation. Kịch bản "strict" chỉ tăng từ 0,342 lên 0,3609, vì pooling baseline vốn đã tối ưu.
  - Repo: bỏ độ phân giải (về pool /64) làm CV dev giảm −0,0840; trần độ phân giải 0,6294 với khối 0,64 s ([PAPER_NOTES S11, S19](../../docs/PAPER_NOTES.md)).
  - Bài này là **công trình đi trước** cho mục "trần độ phân giải" đang đánh dấu ⚠️ CẦN XÁC MINH ở [PAPER_NOTES §4.1](../../docs/PAPER_NOTES.md).
- **Hậu xử lý theo lớp (Cances và cs., WASPAA 2019):** event-F1 22,9% → 32,0% trên DCASE 2018 T4 với phương pháp tham số theo lớp [V2] — [arXiv:1906.06909](https://arxiv.org/abs/1906.06909).
  - Repo: θ theo lớp quá khớp dev (dev → test −48% / −39% / −41%), median filter không có hiệu ứng rõ ([PAPER_NOTES S4, S5](../../docs/PAPER_NOTES.md)).
  - Theo một snippet, baseline DCASE dùng median filter cố định cửa sổ 7 [V1] — [Interspeech 2023 Lin](https://www.isca-archive.org/interspeech_2023/lin23_interspeech.pdf).
- **Mean-teacher / pseudo-label / KD.**
  - Baseline DCASE 2023 "is a mean-teacher model" [V2] — [task DCASE 2023](https://dcase.community/challenge2023/task-sound-event-detection-with-weak-labels-and-synthetic-soundscapes).
  - CPJKU 2024 dùng ensemble 46 model sinh pseudo-label mềm ở I2.S1 [repo V3] — [docs/RELATED_WORK.md §2.3 (18)](../../docs/RELATED_WORK.md).
  - Repo: pseudo-label DataSEC (O-F) âm tính (0,2151 so với 0,2330); KD 0,5/0,5 âm tính (0,1999); thêm seed không tăng (+0,0002) ([PAPER_NOTES S57, S60, S61](../../docs/PAPER_NOTES.md)).
- **Tăng cường dữ liệu.**
  - FilterAugment tăng PSDS **+6,50%** so với +2,13% của frequency masking [repo V3] — [docs/RELATED_WORK.md §2.2](../../docs/RELATED_WORK.md).
  - Repo: mixup + FilterAugment giúp AP frame, không giúp event-F1 (S20); gain/EQ đảo chiều ở tầng C (−0,0082) (S63) — [PAPER_NOTES](../../docs/PAPER_NOTES.md).
- **TTA:** tìm `test-time augmentation sound event detection PSDS` không thấy nguồn SED nào báo lợi ích của TTA dịch thời gian. Chỉ có TTA xoay cho SELD (DCASE 2022 T3, 16 mẫu xoay) [V1] — [báo cáo DCASE2022 Han](https://dcase.community/documents/challenge2022/technical_reports/DCASE2022_Han_54_t3.pdf).
- **LBR của khóa luận** [V3, repo] — [PAPER_NOTES S64, S65, §5](../../docs/PAPER_NOTES.md).
  - OOF 0,2342 → **0,3332** (Δ +0,0990 [+0,0761; +0,1200]); test 0,1806 → 0,2965 (Δ +0,1159 [+0,0741; +0,1593]).
  - Thăm dò LBR trên ensemble B0 + O-D: 0,3472, hơn B0 + V2 **+0,014 [−0,001; +0,029]**.
  - Ngưỡng của rescorer nằm ở mép lưới ở cả 5/5 fold (S64b).
  - Hysteresis có code (`hysteresis_runs`) nhưng "chưa đánh giá" (PAPER_NOTES §3).

### Inferences
- **Đã làm (đủ để trả lời hội đồng "đã thử các quick win chuẩn chưa"):** θ chung/theo lớp, median filter, ensemble và seed, cSEBB, suy luận chồng lấn có trọng số tam giác, độ phân giải 40–80 ms, focal loss, KD, pseudo-label, tăng cường dữ liệu, cửa sổ 20 s, và LBR. Phần âm tính là thế mạnh phương pháp: chọn hai tầng (S → C) đã chặn bốn lần đảo chiều.
- **Còn lại, xếp theo kỳ vọng / chi phí:**
  1. **Mở rộng lưới ngưỡng rescorer của LBR** (ngưỡng đang ở mép lưới, S64b). Chọn trên OOF, rẻ. Nhưng thay cấu hình hệ thống đồng nghĩa phải mở test thêm một lần đã ghi trước, nên xếp T1.
  2. **LBR trên ensemble liên họ B0 + O-D.** Thăm dò +0,014 với CI chạm 0, kỳ vọng nhỏ, cũng cần ghi trước và mở test, nên xếp T1.
  3. **Hysteresis và prior thời lượng theo lớp có co về chung (shrinkage), chỉ trên OOF.** Kỳ vọng thấp vì LBR đã thay vai trò dựng biên. Có thể chạy T0 như "đã đo, không dùng", không mở test.
  4. **TTA dịch thời gian/tần số trước cSEBB/LBR.** Không có nguồn SED báo lợi ích; với posterior 40 ms đã gộp chồng lấn, kỳ vọng thấp, nên xếp T1/T2.
  5. **Mean-teacher với DataSEC làm dữ liệu không nhãn/nhãn yếu.** Chuẩn DCASE, nhưng bằng chứng nội bộ cho thấy DataSEC không giúp định vị (S48, S57). Chi phí cao, nên xếp T2.
- **Không nên làm trong 5 ngày:** ngưỡng hoặc điểm vận hành LBR theo lớp (21 bậc tự do, quá khớp như S4); đổi encoder (S56).

### Gaps
- Không tìm được nguồn định lượng cho TTA trong SED đơn kênh.
- Chưa đọc toàn văn Cances 2019 để biết collar và loại hậu xử lý.
- Con số "median filter 7 frame" mới ở V1.

## Câu hỏi 7 (mục tiêu 2–3). Baseline hoặc so sánh còn thiếu mạnh nhất mà hội đồng có thể đòi; kỹ thuật cải thiện nào xếp đầu theo lợi ích/chi phí (T0/T1/T2)?

### Takeaway
- **Baseline SED còn thiếu mạnh nhất:** một mô hình SED tổng quát **không học trên DataSED**, cụ thể là head AudioSet-Strong 447 lớp của PretrainedSED ánh xạ sang 21 lớp. Chỉ cần suy luận, chọn trên OOF, mở test một lần. Nó trả lời câu "có cần huấn luyện riêng không?".
- **So sánh hệ thống còn thiếu mạnh nhất:** LALM end-to-end. Văn liệu đủ để trả lời ngay; một head-to-head nhỏ trên dev bằng Qwen2.5-Omni-7B qua llama.cpp chạy được trong 1–2 ngày.
- **Cho RQ3:** baseline CLAP không dùng SED.
- **Không có kỹ thuật T0 nào hứa hẹn tăng event-F1 lớn.** Lợi ích lớn nhất trong 5 ngày đến từ diễn giải và định cỡ (bảng DCASE, chuẩn hóa theo trần người, sửa "22 lớp" thành "21 lớp") và từ ba baseline trên, không đến từ tối ưu tiếp.

### Cited Findings
- Checkpoint PretrainedSED có head AudioSet-Strong **447 lớp**. Repo đã tải, kiểm SHA-256 và license: `frame_mn10_strong_1.pt`, `BEATs_strong_1.pt`, `ATST-F_strong_1.pt`; repo bỏ head khi dùng làm encoder [repo V3] — [docs/RELATED_WORK.md §2.1 (2)](../../docs/RELATED_WORK.md); [ADR-0032](../../docs/decisions/ADR-0032-track2-encoder-pretrain-theo-frame.md).
- **Bằng chứng LALM** [V2] — [arXiv:2604.13715](https://arxiv.org/html/2604.13715); [TAG-Bench](https://arxiv.org/html/2609.01542v2); [HalluAudio](https://arxiv.org/html/2604.19300); [HF GGUF](https://huggingface.co/ggml-org/Qwen2.5-Omni-7B-GGUF).
  - DESED zero-shot Eb-F1: Qwen2.5-Omni-7B 13,7 / Qwen2-Audio-7B 3,4.
  - TAG-Bench mIoU ≤ 31,2, báo thiếu 79–100%.
  - HalluAudio: thiên lệch "có" ở âm thanh môi trường.
  - GGUF 7B Q4_K_M 4,68 GB.
- **CLAP** [V2] — [FLAM](https://arxiv.org/html/2505.05335v2); [GitHub DataSEC](https://github.com/goyumsamuditha/datasec-uncertainty-aware-sound-classification).
  - LAION-CLAP AudioCaps T2A R@1 36,1.
  - CLAP zero-shot 85,32% accuracy trên DataSEC v4.
- **Ràng buộc của đề tài:** RTX 3070 Laptop 8 GB; chỉ chọn trên dev/OOF; mọi lần chạm test ghi sổ tự động [V3, repo] — [docs/SYSTEM.md](../../docs/SYSTEM.md); [04_phuong_phap.md](../../report/final_src/04_phuong_phap.md).
- **Đánh đổi của các điểm vận hành LBR** [V3, repo] — [06_ket_qua.md](../../report/final_src/06_ket_qua.md).
  - V2 giảm segment-F1 từ 0,7260 xuống 0,5965 và PSDS-2 từ 0,7452 xuống 0,6116.
  - V3 recall_first đạt recall giao nhau 0,8203 với precision 0,7812.

### Inferences
**Bảng xếp hạng đề xuất.** Chi phí là ước tính của người viết từ khối lượng dữ liệu, chưa đo. Lợi ích là định tính, kèm bằng chứng.

| # | Việc | Tier | Chi phí ước tính | Lợi ích kỳ vọng (bằng chứng) | Giao thức chống tinh chỉnh trên test |
|---|---|---|---|---|---|
| 1 | Viết lại phần định cỡ: bảng DCASE 2016/2017/2022–2024 + MAESTRO (Câu hỏi 2), chuẩn hóa theo trần người (V2 ≈ 51% của 0,5785), sửa "22 lớp" → "21 lớp", câu "chưa thấy công bố nào" (Câu hỏi 1) | T0 | khoảng 0,5 ngày, 0 GPU | **Cao về phòng thủ.** Chặn câu "0,30 là thấp" bằng mốc ngoài | Không chạm dữ liệu; nâng nguồn DCASE lên V3 trước khi trích |
| 2 | Chỉ số bổ sung trên output test **đã đóng băng**: segment ER/F1 1 s, event-F1 chỉ onset collar 250 ms (kiểu DCASE 2016), macro theo lớp, phân theo khoảng độ dài sự kiện | T0 | vài giờ, 0 GPU | Trung bình: cho phép so cùng kiểu metric với DCASE 2016/2017 | Ghi trước là "báo cáo bổ sung, không chọn"; ghi vào sổ test |
| 3 | **Baseline SED zero-shot AS-Strong** (BEATs-strong hoặc frame_mn10, head 447 lớp → 21 lớp, max xác suất các lớp ánh xạ) | T0 | khoảng 1 ngày người, ≤ 1–3 GPU-giờ cho 564 bản ghi OOF + 139 test (khoảng 15 + 3,6 h audio) | **Cao về lập luận.** Kỳ vọng thấp hơn B0/LBR, vì không học quy ước nhãn và lớp gộp của DataSED. Nếu ngược lại thì đó là phát hiện quan trọng | Ghi trước bảng ánh xạ (theo tên lớp, trước khi chạy); chọn θ/cSEBB trên train ∪ dev (564 bản ghi, không cần cross-fit); mở test **một lần** |
| 4 | **Head-to-head LALM trên dev** (Qwen2.5-Omni-7B Q4_K_M qua llama.cpp; khoảng 40 bản ghi dev; H_gt/O_gt, event-F1, onset MAE, độ đúng số lần, đối chứng nền/nhiễu) | T0 | 1–2 ngày người, < 2 GPU-giờ (khoảng 1 h audio) | **Cao về lập luận** (câu hỏi chắc chắn bị hỏi). Kỳ vọng event-F1 LALM ≪ LBR, mức bản ghi gần hơn (DESED 13,7; TAG-Bench) | Chỉ dev, so với sự kiện OOF cross-fit của B0/LBR; **không mở test**; ghi trước bằng ADR |
| 5 | **Baseline CLAP cho RQ3** (cửa sổ 10 s, bước 5 s; gộp max/top-3; 100 truy vấn) | T0 | khoảng 1 ngày người, vài phút GPU | Trung bình–cao: cô lập giá trị SED + bộ lọc. Kỳ vọng tốt ở truy vấn 1 lớp, kém ở quan hệ thời gian/thời lượng | Chọn cách gộp trên validation 134 bản ghi; mở test một lần; kiểm license checkpoint trước |
| 6 | Hysteresis + prior thời lượng theo lớp có co về chung, chỉ đo trên OOF | T0 (tùy chọn) | vài giờ | Thấp (LBR đã thay vai trò dựng biên) | Không mở test; ghi "đã đo, không dùng" |
| 7 | Mở rộng lưới ngưỡng rescorer LBR (ngưỡng ở mép lưới 5/5 fold) | T1 | khoảng 0,5 ngày | Thấp–trung bình | Chọn trên OOF; một lần test mới đã ghi trước |
| 8 | LBR trên ensemble B0 + O-D | T1 | khoảng 1 ngày | Thấp (OOF +0,014 [−0,001; +0,029]) | Như dòng 7 |
| 9 | ATST-F-strong (CC BY 4.0) đóng băng hoặc fine-tune, rồi LBR | T1 | 1–2 tuần GPU (GPU hạ xung nhiệt) | Thấp với event-F1 (S56: frame mAP 0,80 không thành event-F1) | Hai tầng S → C như giai đoạn O |
| 10 | Gemini/GPT-4o trên tập dev nhỏ (nếu chính sách dữ liệu cho phép) | T1 | 0,5–1 ngày | Minh họa; không tái lập lâu dài | Chỉ dev; ghi phiên bản model và ngày |
| 11 | Vector audio CLAP trong pgvector + bộ lọc cứng | T1 | 1–2 ngày | Trung bình (so vector âm thanh với vector mô tả) | Validation chọn, test một lần |
| 12 | TTA dịch thời gian/tần số | T1/T2 | 1 ngày | Thấp, không có bằng chứng SED | OOF |
| 13 | Huấn luyện boundary-aware đầu–cuối (RED + loss onset/offset + EPN đầy đủ) | T2 | nhiều tuần | Có bằng chứng ngoài (CRNN PSDS1 41,1 → 48,0); RED đơn lẻ trong repo âm tính | Hai tầng |
| 14 | LALM fine-tune cho SED trên DataSED (kiểu TimePro-RL: SFT 48,9 → RL 57,6 trên DESED) | T2 | lớn; thiếu nhãn (438 bản ghi train so với 15.041 mẫu) | Không rõ | — |
| 15 | Soundscape tổng hợp từ DataSEC (Scaper) + mean-teacher; open-vocabulary SED (FLAM/COSED); gán nhãn lại nhiều người/nhãn mềm (RealDESED) | T2 | lớn | Hướng paper | — |

- **Thứ tự đề xuất cho 5 ngày (23–28/11):** (1) và (2) trước hết, vì chỉ là việc viết. Sau đó (3), vì là baseline định lượng sạch nhất, chạy được trong một lần test. Sau đó (4) và (5), song song nếu có người. Nếu thiếu thời gian, (4) và (5) có thể **chỉ ghi trước thành kế hoạch** trong báo cáo nộp, rồi chạy trước buổi bảo vệ. Như vậy đủ trả lời hội đồng mà không vội vàng mở test.
- **Rủi ro cần nói trước:**
  - Baseline (3) phụ thuộc chất lượng ánh xạ lớp. Các lớp gộp như `thunder_fireworks_gunshot` và `sirens_and_alarms` ánh xạ nhiều-về-một, còn `workshop` và `chicken_coop` có thể không có lớp tương ứng.
  - Head-to-head (4) phụ thuộc chất lượng audio trong llama.cpp đã lượng tử hóa: số thấp có thể là do công cụ, không do model. Cần một mẫu kiểm chéo bằng HF bf16 (3B) nếu được.
  - Mọi kết quả (4) là dev n ≈ 40, CI rộng, không được viết thành "pipeline tốt hơn LALM", chỉ được viết "trên mẫu này…".

### Gaps
- Chưa kiểm danh sách 447 lớp AS-Strong và tính khả thi của ánh xạ từng lớp.
- Chưa đo VRAM thật của Qwen2.5-Omni-7B + mmproj trên RTX 3070 8 GB.
- Chưa kiểm license LAION-CLAP/MS-CLAP.
- Ước tính GPU-giờ là suy luận từ khối lượng audio (test khoảng 139 × 94 s ≈ 3,6 h), chưa đo.
