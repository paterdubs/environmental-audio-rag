# ADR-0041 — Giai đoạn O: tối ưu SED sau báo cáo giữa kỳ

**Status:** Accepted 08/10/2026 — người dùng duyệt toàn bộ, gồm cả 5 đề xuất ở Decision §6
(đóng băng 24/10; chọn bằng micro; S8-lite; dùng DataSEC v4, không train lại RQ1 cũ; chính sách test §2).
**Date:** 2026-10-08

## Context

### 1. Vì sao mở lại tối ưu SED

Người dùng (08/10) chọn dồn thời gian còn lại vào SED: caption (RQ2) và RAG (RQ3) đã ổn, còn
chất lượng của chúng bị chặn bởi SED (S43: nDCG@10 structured/hybrid **giảm** khi corpus đổi sang
f2). ADR-0031 đã đóng băng f2 (`c3f0033`); mở lại là quyết định mới, nên cần ADR này.

### 2. Hồ sơ lỗi của hệ thống hiện tại (f2, đọc file đã lưu, không chạy lại test)

`ml/runs/sed_ensemble_s13_f2_20260929T045053Z/evaluation_cv_annotated.json`:

| Chỉ số | Giá trị |
|---|---|
| Event tham chiếu / event dự đoán | **740 / 295** |
| Micro P / R / F1 | 0.288 / **0.115** / 0.164 |
| Macro F1 | 0.121 |
| Lỗi chẩn đoán | deletion **349**, merging 34, confusion 7, fragmentation 4, insertion 1 |
| Lớp có F1 = 0 | 7/21: birds, crows, dog, jet, thunder, vehicle_idling, vehicle_pass_by |
| PSDS-1 / PSDS-2 | 0.316 / **0.725** |

Đọc: xếp hạng xác suất khá (PSDS-2) nhưng hệ thống **dự đoán quá ít event**. Khi biên lệch,
điểm vận hành tối đa F1 bị đẩy về phía bảo thủ, làm recall sụp. Định vị và recall gắn với nhau.

### 3. Chẩn đoán từ log train (sơ bộ, script nháp 08/10 — O0.2 sinh lại bằng script repo)

- **RQ1 có cơ chế rõ.** `history.json` của 3 B-v2 vs 3 C-v2: val mAP sau epoch 1 là
  0.389/0.378/0.407 (B) so với 0.514/0.501/0.514 (C) → trọng số DataSEC được nạp và có tác dụng.
  Khoảng cách gần như biến mất sau 5–7 epoch. Trên dev annotated, 134 recording, hậu xử lý in-sample:
  segment-F1 1 s B 0.690 so với C **0.717** (cả 3 C > cả 3 B), frame mAP +0.019, event-F1 chỉ
  +0.008. Trên test, PSDS-2 tăng +0.028 (p = 0.019, S41). Như vậy DataSEC dạy **nhận dạng**,
  không dạy **định vị**, vì nó chỉ có nhãn cấp clip.
- **Nút thắt là biên onset và event ngắn** (S12, S23): segment-F1 khoảng 0.69 nhưng event-F1 chỉ
  onset khoảng 0.27. Nới collar 0.2 → 1 s làm event-F1 dev gần gấp đôi (B-v2 0.208 → 0.404).

### 4. Phát hiện về dữ liệu (sơ bộ, script nháp 08/10 — O0.1 sinh lại bằng script repo)

1. **DataSEC có bản v4 (Zenodo 23097290, 02/10/2026).** Trang record ghi nguyên văn: *"V.4 fixes a
   bug in the uploaded file, where the number of Music files was not correct respect to what
   described in the text."* v4 có 4,292 file / 18 h 26 m. Bản repo đang dùng là record 17033970
   (MD5 `29fa9b8c…`), có 5,048 file, trong đó **1,001 clip Music dài 30 s** (khoảng 8.3 h).
   Hệ quả: D1 classifier và nhánh C của RQ1/RQ1-v2 được huấn luyện trên bản có lỗi upload.
2. **8 recording train không có GT polyphonic vẫn được train với nhãn toàn 0.**
   `ml/datasets/features.py:162-173` cho recording không có event target 0 và `valid` = 1. Hai
   recording train **dài nhất** (S-0713, 818 s; S-0715, 660 s) thuộc nhóm này. Theo nhãn
   monophonic, 14 recording đó chứa 102 event thuộc 21 lớp (S30): vehicle_pass_by, thunder, crows,
   workshop… Đây là khoảng 1 giờ âm tính giả trong train. ADR-0034 mới sửa phần chấm điểm.
3. **8 cặp recording trùng byte được gán nhãn hai lần** (4 cặp train, 3 cặp dev, 1 cặp test). Ở
   train, model thấy cùng một audio với hai target mâu thuẫn, và audio đó có trọng số gấp đôi.
4. **Suy luận cắt cứng theo cửa sổ 10 s không chồng lấn** (`hop_frames = window_frames = 1000`
   cho cả v2 và T2b). Recording trung vị 80 s, dài nhất 818 s, nên mỗi recording bị cắt khoảng 8
   lần. f2 (`frame_mn`, không có sequence model) mất ngữ cảnh ở mỗi chỗ cắt.
5. **"Polyphonic" thực tế gần đơn âm:** trên lưới 0.1 s của train, 24% thời gian không có event,
   72% có đúng 1 event, 4% có từ 2 event trở lên.
6. **Độ dài event lệch mạnh theo lớp:** trung vị toàn bộ 5.8 s. Lớp ngắn có trung vị ≤ 3 s (horn,
   dog, voices, crows, chicken, cat, glass, thunder); lớp dài 20–38 s (jet, propeller, train)
   có onset dạng fade-in. Hầu hết lớp F1 = 0 thuộc hai nhóm này.
7. **Dữ liệu nhỏ:** mỗi lớp có 55–264 event trong train và chỉ 15–70 event trong test, nên macro
   test rất nhiễu. Dev 134 recording làm việc chọn hệ thống không ổn định (S40: thứ hạng test ≠
   thứ hạng CV dev).
8. **Nhãn có nhiễu biên:** event-F1 người–người 0.58 ở collar 0.2 s, 0.76 ở collar 1 s (8 cặp, D6).

### 5. Văn liệu (V2, qua WebSearch/WebFetch 08/10 — RELATED_WORK §2.3)

| Kỹ thuật | Nguồn | Số đã báo | Áp vào đây |
|---|---|---|---|
| Suy luận cửa sổ trượt chồng lấn, trung bình trọng số tam giác | RealDESED, Schmid và cs., arXiv 2607.16736 | PSDS1-M: hop 10 s 0.711 → 2.5 s **0.736**; mean > max; sàn tam giác 0.3 tốt nhất | Không cần train lại |
| Sequence model trên frame-MobileNet | EfficientSED, Morocutti và cs., EUSIPCO 2025 (arXiv 2503.11373) | AS-Strong PSDS1 fmn10 42.28 → +TF256 43.86; KD 45.25; checkpoint MIT | f2 là fmn10 **không** có sequence model |
| Học biên trực tiếp: RED layer + Event Proposal Network, focal loss onset/offset | Schmid và cs., IEEE SPL 2026 (arXiv 2601.04178) | AS-Strong-10, CRNN: PSDS1 41.1 → 48.0, F1 32.3 → 40.6 (so với SEBB) | Nhắm đúng nút thắt onset; **không có code** |
| Multi-iteration fine-tune + KD từ ensemble | Schmid và cs., DCASE 2024 hạng 1 (arXiv 2407.12997) | DESED PSDS1 0.692 single model | Dùng ensemble làm teacher |
| Nhãn mềm từ nhiều người gán | RealDESED | PSDS1-M 0.675 → 0.697 | 8 cặp gán đôi; làm mượt biên |
| Soundscape tổng hợp / trộn event cô lập | Scaper; Turpault/Ronchini và cs. arXiv 2109.14061 | Event không phải mục tiêu ảnh hưởng hiệu năng; domain gap | DataSEC → nhãn mạnh |
| Pseudo-label có điều kiện theo tag | FBCRNN + tag conditioning, arXiv 2103.06581 | Event-F1 50.1 → 53.4% | Nhãn clip DataSEC chặn lớp được phép |

Bên ngoài: Zhang & Virtanen (arXiv 2607.13571, 09/2026) dùng DataSED nhưng chia ngẫu nhiên theo
đoạn 10 s và đo frame mAP, nên **không** so trực tiếp được. Bài Forum Acusticum 2025 của Artuso
và cs. là phân loại (CLAP) trên DataSEC, không phải SED. Chưa thấy baseline SED nào trên DataSED.

### 6. Ràng buộc

- Test đã bị chạm 40 lần cho SED (`test_ledger_20261002`). Kết quả test của các ứng viên S13
  đã được nhìn thấy, ví dụ f1 (BEATs) có PSDS test cao hơn f2. Giai đoạn O **không** được dùng điều
  đó để chọn. Phải ghi rõ đây là tái sử dụng test thích nghi (adaptive reuse).
- GPU RTX 3070 Laptop 8 GB. Thời lượng run đo được: T2b khoảng 35–48 phút, B-v2/C-v2 65–117 phút,
  T2a khoảng 2.5 giờ.
- Hạn nộp 09/11; báo cáo cuối kế thừa bản giữa kỳ 63 trang.

## Decision

### 1. Thước đo (giữ ADR-0031 §1, thêm chỉ số ứng dụng)

- Con số chính: event-F1 **macro** (collar 0.2 s, `annotated`). Thước **chọn** hệ thống vẫn là
  event-F1 **micro**. Không đổi metric headline sau khi thấy số.
- Ghi trước, luôn báo kèm, **không** dùng để chọn: segment-F1 1 s (macro), event-F1 collar 1 s,
  PSDS-1/2, số event dự đoán so với tham chiếu, recall. Lý do: RAG cần phát hiện đủ event và
  định vị khoảng giây (S43), trong khi nhãn người chỉ khớp 0.58 ở collar 0.2 s.

### 2. Giao thức hai tầng, chọn trước khi mở test

- **Tầng S (sàng lọc):** train trên `train`, 1 seed, chấm CV hậu xử lý trên dev như S13. Mỗi
  thí nghiệm so với trung bình cùng phép chấm của 3 seed T2b. Nếu không vượt ít nhất một seed T2b
  tốt nhất thì không đi tiếp. Tầng S chỉ để lọc, không bao giờ để tuyên bố.
- **Tầng C (xác nhận):** gộp `train ∪ dev` annotated (khoảng 564 recording), chia 5 fold theo
  `leakage_group`, phân tầng theo lớp có mặt. Split gốc **không** đổi; fold chỉ là cách dùng lại
  phần không phải test. Mỗi cấu hình train 5 model và tạo dự đoán out-of-fold (OOF) trên cả 564
  recording. Hậu xử lý (θ global, cSEBB) chọn bằng CV lồng trên OOF.
  - Baseline cùng giao thức **B0** = công thức T2b + sửa dữ liệu §3 + suy luận chồng lấn §4.
  - Tối đa 3 ứng viên được đưa lên từ tầng S, cộng 1 ensemble liên họ ghi trước: trung bình
    hai họ tốt nhất.
- **Luật chọn (ghi trước):** chọn ứng viên có OOF micro cao nhất **trong số những ứng viên mà CI
  95% của Δ so với B0 không chứa 0**. Δ tính bằng bootstrap ghép cặp theo recording, 1000 lần,
  seed 20260922. Nếu không ứng viên nào đạt thì hệ thống cuối là **B0**. Hệ thống cuối là
  ensemble 5 model fold của nó.
- **Test:** lựa chọn được commit **trước** khi sinh logit test. Mỗi hệ thống sau chạy đúng một
  lần: hệ thống cuối, B0, và tối đa 2 ablation ghi trước. Ghi sổ test; so với f2 bằng bootstrap
  ghép cặp trên 139 recording. Báo mọi số, kể cả khi thứ tự trên test khác OOF.

### 3. Sửa dữ liệu (chỉ phía train; dev/test và cách chấm giữ nguyên)

| # | Việc | Ghi chú |
|---|---|---|
| DO-1 | Tải DataSEC v4, kiểm MD5 `11e0ae00…`, so `sha256` từng file với inventory v3 | Nếu v4 ⊂ v3 và chỉ bớt Music: lọc danh sách, không trích đặc trưng lại; exclusion D3 giữ nguyên. Nếu có file mới: chạy D3/D4 cho phần mới. Số RQ1/D1 cũ giữ nhãn "DataSEC v3" kèm hạn chế. |
| DO-2 | Bỏ recording train không có GT polyphonic khỏi loss | Không dùng nhãn monophonic thay polyphonic (khác quy ước gán) |
| DO-3 | 4 cặp gán đôi trong train → một mẫu, target mềm = trung bình hai bản | Không sửa annotation gốc; dev/test giữ nguyên |
| DO-4 | (sàng lọc) Lấy mẫu cửa sổ cân bằng: giới hạn cửa sổ/recording mỗi epoch, ưu tiên cửa sổ chứa lớp ngắn/hiếm | Đo ở tầng S |

Không sửa raw annotation, split đóng băng, taxonomy hay 21 lớp polyphonic.

### 4. Hướng kỹ thuật, theo thứ tự ưu tiên (giá rẻ, ích lợi lớn trước)

| ID | Hướng | Chi phí | Cần train lại? |
|---|---|---|---|
| O-A | Suy luận chồng lấn: hop 2.5/5 s, trung bình trọng số tam giác (sàn 0.3), áp cho f2/f1/v2 trên dev | Vài giờ code | Không |
| O-B | DO-2 + DO-3 trên công thức T2b (1 seed) | 1 run (~45 phút) | Có |
| O-C | EfficientSED fmn10 + BiGRU / TF256 (checkpoint AudioSet Strong, MIT) | Vendor + 2 run | Có |
| O-D | Fine-tune transformer frame-level (ATST-F strong, CC BY 4.0; BEATs strong, MIT), fp16 + lr giảm theo lớp. Có cổng T0 về VRAM/thời gian | 1 cổng + 1–2 run (2–4 giờ/run) | Có |
| O-E | Học biên: head onset/offset phụ với focal loss (biến thể đơn giản kiểu RED); thử RED đầy đủ nếu kịp. Kèm target biên mềm | Code + 2 run | Có |
| O-F | DataSEC → nhãn mạnh (RQ1b): pseudo-label teacher × mặt nạ tag DataSEC (chỉ DataSEC train v4, trừ 130 clip đã loại) + trộn event ngắn vào recording train DataSED có kiểm soát SNR | Code + 2 run | Có |
| O-G | KD: ensemble tốt nhất làm teacher → student đơn, train trên DataSED train (+ DataSEC ở O-F) | 1–2 run | Có |
| O-H | Hậu xử lý theo **2 nhóm** lớp (ngắn/dài, theo trung vị độ dài event ở train) thay vì 21 θ riêng | CV | Không |

O-F là thí nghiệm có kiểm soát cho câu hỏi của GVHD: *nếu biến DataSEC thành nhãn mạnh thì nó có
giúp định vị không?* So sánh B0 với B0 + O-F trên cùng 5 fold.

### 5. Lịch (cần người dùng duyệt) và cut-list

| Khối | Ngày | Việc |
|---|---|---|
| O0 | 08–10/10 | DO-1; script repo cho hồ sơ dữ liệu + cơ chế RQ1; DO-2/DO-3; O-A (code + dev); file fold |
| O1 | 10–14/10 | Tầng S: O-B, O-C, cổng T0 + O-D, DO-4 |
| O2 | 13–17/10 | Tầng S: O-E, O-H |
| O3 | 15–19/10 | Tầng S: O-F, O-G |
| O4 | 19–23/10 | Tầng C: B0 + ≤ 3 ứng viên + ensemble liên họ × 5 fold; chọn; **commit** |
| O5 | 24/10 | Test một lần, sổ test, bootstrap so f2 — **đóng băng model** |
| O6 | 25–27/10 | Phục vụ hệ thống mới, parity, S8-lite (Decision §6, câu 3) |
| Viết | 25/10–09/11 | Cập nhật báo cáo cuối từ bản giữa kỳ; buffer tới 16/11 |

Cắt theo thứ tự khi trễ: O-E RED đầy đủ → O-G → O-D → O-F → DO-4. **Không** cắt: O-A, DO-1, DO-2,
DO-3, tầng C, luật chọn, test một lần.

### 6. Điểm người dùng phải quyết trước khi train

| # | Câu hỏi | Đề xuất |
|---|---|---|
| 1 | Mốc đóng băng model **24/10**, viết báo cáo từ 25/10? | Đồng ý; nếu cần thêm thời gian thì cắt theo cut-list, không lùi mốc |
| 2 | Thước chọn: giữ **micro** (ADR-0031) hay đổi sang macro OOF? | Giữ micro; macro vẫn là số chính |
| 3 | Sau O5: S8 đầy đủ (3 nhánh LLM, khoảng 1 ngày) hay **S8-lite** (retrieval + caption template EN/VI + `constrained_cover`)? | S8-lite; số RQ2 LLM đầy đủ của f2 giữ làm kết quả chính |
| 4 | Giai đoạn O dùng DataSEC **v4**; có train lại D1 trên v4 không? | Dùng v4; không train lại D1 cho RQ1 cũ, chỉ ghi hạn chế |
| 5 | Chấp nhận chính sách test §2 (tái sử dụng thích nghi, báo rõ)? | Đồng ý — không còn tập độc lập nào khác |

## Consequences

- Chi phí GPU tầng C: họ fmn khoảng 5 × 45 phút cho mỗi cấu hình; họ transformer khoảng
  5 × (2–4) giờ. Tối đa khoảng 1.5 ngày GPU, chạy qua đêm.
- Hệ thống cuối là ensemble 5 fold. Nếu thuộc họ transformer, suy luận CPU trong container sẽ
  chậm; khi đó O-G (student) là đường phục vụ.
- f2, S13, RQ1/RQ1-v2 và mọi số đã báo **giữ nguyên làm lịch sử**. Số mới là "giai đoạn O" với
  giao thức riêng.
- Nếu O-F dương tính, RQ1 có thêm kết quả cơ chế (RQ1b): DataSEC giúp định vị khi được chuyển
  thành nhãn mạnh. Nếu âm tính thì báo âm tính.
- Rủi ro đã biết: checkpoint AudioSet Strong có thể đã thấy một phần audio nguồn của DataSED
  (S31); test đã bị tái sử dụng thích nghi; fold OOF dùng lại dev cũ nên chỉ test mới độc lập.

## Alternatives considered

1. **Dừng tối ưu, chỉ viết báo cáo:** an toàn về lịch nhưng bỏ phí các nguyên nhân đã đo được
   (§4.2, §4.4) có thể sửa rẻ.
2. **Chỉ hậu xử lý (O-A, O-H):** rẻ, nhưng không chạm event ngắn bị bỏ sót.
3. **Đổi metric chính sang collar 1 s hoặc segment-F1:** bị loại vì đổi thước đo sau khi thấy số.
   Chỉ được báo kèm như §1.
4. **Chia lại split hoặc gộp test vào CV:** bị loại vì phá khả năng so với mọi số trước và mất
   tập độc lập duy nhất.
5. **Thêm dataset ngoài (DESED, AudioSet Strong trực tiếp):** ngoài scope ADR-0001; chỉ dùng qua
   checkpoint đã pretrain.
6. **M2D:** license riêng, đã loại ở ADR-0032.

## Evidence cần kiểm lại

- Mọi số ở Context §3–§4 đến từ script nháp ngày 08/10 → O0.1/O0.2 sinh lại bằng script repo
  thành measurement trước khi dùng trong PAPER_NOTES hoặc báo cáo.
- Văn liệu §5 đang ở V2 (qua tóm tắt WebFetch). Phải đọc PDF trước khi trích dẫn: RealDESED (số
  hop/tam giác), boundary-aware SPL 2026 (Bảng I/III), EfficientSED (bảng sequence model, KD).
- DataSEC v4: MD5 và danh sách file chưa tải về kiểm.
- Đánh giá DO-2 ở tầng S: bỏ khoảng 1 giờ train có thể làm thiếu mẫu lớp dài (vehicle_pass_by).
  So sánh có/không ở O-B.
