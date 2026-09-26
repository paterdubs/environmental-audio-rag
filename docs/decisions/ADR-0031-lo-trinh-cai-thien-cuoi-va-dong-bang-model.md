# ADR-0031 — Lộ trình tới hạn nộp: RQ1-v2, Track 2, vòng chọn cuối và mốc đóng băng model

**Status:** Accepted — người dùng duyệt 26/09/2026 ("làm theo những gì bạn cho là nên làm, nên
duyệt, ghi vào kế hoạch"), với mục tiêu **ưu tiên cải thiện kết quả**. Chi tiết kỹ thuật của
Track 2 chốt ở ADR-0032, viết sau cổng T0 (§3) và trước run đầy đủ đầu tiên.
**Date:** 2026-09-26

## Context

- **SED v2 (ADR-0030) đang train.** Run 1 (seed 20260922) có CV dev event-F1 0.1900 ± 0.0523
  (sơ bộ, 1/3 seed); mốc v1 là ensemble C 0.1538 ± 0.0214. Lựa chọn theo ADR-0030 §5 dự kiến
  commit 26–27/09.
- **Chỗ yếu còn lại, đo trên dev:**
  - Biên event: v1 có event-F1 chỉ onset 0.2325, segment F1 0.6542 (`sed_ceilings_20260926.md`).
  - Lớp hiếm bị bỏ sót (`boundary_errors_20260926.json`, `per_class`): tỷ lệ frame dương có xác
    suất < 0.5 của `horn`, `crows_seagulls_magpies`, `thunder_fireworks_gunshot` là 82%, 72%,
    58% ở v1 ensemble C, và 75%, 73%, 58% ở v2 seed 20260922 (sơ bộ). v2 chưa sửa chỗ này.
- **Con số chính.** Event-F1 headline từ trước tới nay là micro, trong khi evaluation_protocol
  Q2 đòi macro (PLAN nợ #20). Hệ thống v1 trên test: micro 0.0941, macro 0.0917
  (`event_f1_macro_20260926.md`).
- **ADR-0030 §6:** nếu v2 được chọn thì chạy lại caption e2e (W5) và RQ3 (W6). Làm ngay mà sau đó
  Track 2 thắng thì phải chạy lại lần hai, và mỗi lần là thêm một lượt mở test cho W5/W6.
- **Lịch.** Hôm nay 26/09, hạn nộp 09/11. W1–W6 xong sớm, W7 còn 7.4–7.7. PLAN chỉ đặt việc viết
  báo cáo ở W8, mà W8 chỉ dùng khi được gia hạn.

## Decision

### 1. Con số chính là event-F1 macro; thước chọn hệ thống vẫn là micro

- Mọi bảng kết quả SED từ 26/09: **macro trước, micro kèm**, per-class ở phụ lục (Q2).
- Mọi vòng chọn hệ thống (ADR-0024, ADR-0030 §5, §4 dưới đây) dùng CV dev event-F1 **micro**:
  - luật v2 đã ghi trước bằng micro; đổi bây giờ là đổi thước đo sau khi thấy số;
  - một thước cho mọi vòng thì các vòng so được với nhau;
  - micro cộng dồn số đếm của mọi lớp nên ít nhiễu hơn trên dev 137 recording, nơi lớp hiếm chỉ
    có vài event (cùng lý do per-class θ overfit ở A2).
- Báo thêm thứ hạng các ứng viên theo macro dev (`evaluate_run --split dev`), để xem có trùng
  thứ hạng micro không. Chỉ để báo, không dùng để chọn.
- Số đã báo giữ nguyên. Macro của 22 lần đánh giá cũ tra ở `event_f1_macro_20260926.md`.

### 2. RQ1-v2 (S9): v2 khởi tạo DataSEC × 3 seed

Gọi **B-v2** là v2 khởi tạo AudioSet (các run của ADR-0030), **C-v2** là v2 khởi tạo DataSEC.

- Lệnh: `scripts.train_sed --encoder panns --datasec-checkpoint
  ml/runs/classifier_datasec_20260923T121808Z/checkpoints/best.pt --recipe v2 --seed <s>`, với
  s ∈ {20260922, 2, 3}, cùng bộ seed với B-v2.
- Không cần sửa code. Đã kiểm 26/09: checkpoint DataSEC khớp encoder v2 đủ 74 tensor, cả tên lẫn
  shape, vì pool thời gian không có tham số.
- Thời điểm: ngay sau khi lựa chọn ADR-0030 §5 đã commit và logit test v2 đã sinh (bước này cần
  GPU để trùng bit). Code train giữ nguyên so với B-v2 tới khi 3 run xong, kiểm bằng `git diff`
  như ADR-0030 §8. Code Track 2 chỉ vào master sau đó.
- Phân tích, ghi trước:
  - Mọi run B-v2 và C-v2 dùng cùng họ hậu xử lý global (ADR-0024), chọn bằng CV dev của chính
    run đó.
  - Mỗi run được đánh giá test **một lần**, và chỉ **sau** khi lựa chọn vòng cuối (§4) đã commit.
    Trước đó chỉ dùng CV dev. Như vậy không số test nào có trước lựa chọn cuối, và hướng làm
    Track 2 (ví dụ có dùng khởi tạo DataSEC không) không thể bị số test dẫn dắt.
  - So C − B theo ADR-0021: Welch t-test cho event-F1 (macro và micro), PSDS-1, PSDS-2; bootstrap
    ghép cặp theo recording cho event-F1 micro trung bình (`report_multirun_bootstrap`).
  - Kết quả âm tính thì báo âm tính.
- Công cụ: `report_rq1_multiseed` và `report_multirun_bootstrap` hiện đọc cứng `evaluation.json`
  và `postproc.json`. Cần thêm tuỳ chọn tên file để đọc `evaluation_cv.json`, `postproc_cv.json`.
  Đây là script phân tích, không phải code train.

### 3. Track 2 (S10): PretrainedSED, qua cổng khả thi T0

- **T0, trước mọi run đầy đủ.** Đây là cổng kỹ thuật, không phải cổng hiệu năng:
  1. Nguồn lên V3: đọc trực tiếp bảng số trong bài (arXiv 2409.09546) và code repo
     `PretrainedSED`, không qua tóm tắt.
  2. License của checkpoint được dùng: đọc trực tiếp và ghi vào ADR-0032. Repo là MIT, nhưng
     checkpoint dựng từ model của nhóm khác có thể mang license riêng (bài học ADR-0015).
  3. Bộ nhớ: batch train vừa GPU 8 GB ở cửa sổ 10 s; ghi batch size.
  4. Một epoch trên dev đi hết đường ống: train → `dump_predictions --verify-dev` trùng bit → CV
     hậu xử lý.

  Đạt cả bốn thì đi tiếp. Hỏng mục nào thì ghi lý do và dừng Track 2 cho model đó.
- Thứ tự: `frame_mn10` trước (3.83M tham số theo README, rẻ để kiểm đường ống). BEATs hoặc ATST-F
  strong chỉ làm khi còn thời gian trước mốc §4 và qua T0 riêng.
- ADR-0032 ghi kiến trúc tích hợp (frontend, head 21 lớp, độ phân giải, lr) trước run đầy đủ đầu
  tiên. lr chọn bằng pilot trên dev như ADR-0030 §2. Mỗi model chạy 3 seed {20260922, 2, 3}.

### 4. Vòng chọn cuối tại mốc đóng băng model, 18/10/2026

- Sau mốc không thêm thí nghiệm model nào cho luận văn. Ứng viên chưa xong CV dev trước mốc thì
  không vào vòng.
- Ứng viên. Mỗi ứng viên được ghi vào đây hoặc vào ADR-0032 **trước** khi có CV dev của chính nó:
  - (a) ensemble C v1; (b) B-v2 run đơn seed 20260922; (c) ensemble B-v2 3 seed. Ba ứng viên này
    như ADR-0030 §5.
  - (d) ensemble C-v2 3 seed.
  - (e) ensemble B-v2 + C-v2, 6 model.
  - (f…) ứng viên Track 2, liệt kê ở ADR-0032.
  - (g…) ứng viên lớp hiếm (§5), liệt kê trước run.
- Luật như ADR-0030 §5:
  - Điểm là CV mean event-F1 micro (5 fold theo `leakage_group`, hai họ hậu xử lý của ADR-0030 §3).
  - Điểm cao nhất thắng; hoà thì chọn ít model hơn.
  - Nếu chênh lệch với hạng hai ≤ sd giữa fold của ứng viên thắng, ghi "không được gọi là tốt hơn".
- Lựa chọn commit **trước** khi mở test. Ứng viên nào chưa từng chạm test thì được test đúng một
  lần. Báo tất cả (`report_test_ledger`). Không chọn lại sau khi xem test.
- Ứng viên thắng là hệ thống SED cuối của luận văn, của paper và của hệ thống phục vụ.

### 5. Lớp hiếm và thống kê, sau Track 2 nếu còn thời gian trước mốc

- **Loss cho lớp hiếm (S11):** focal hoặc asymmetric thay `pos_weight`, áp lên họ model đang dẫn
  CV dev. Tham số chọn trên dev; ứng viên ghi trước run.
- **Soundscape tổng hợp từ DataSEC train** (bỏ 130 clip đã loại): chỉ làm khi còn ít nhất 1 tuần
  trước mốc; cần ADR riêng.
- **Seed thêm cho ablation v2 (S12):** ablation nào có |Δ| nằm trong khoảng 0.5–1.5 lần ngưỡng
  nhiễu của `report_sed_v2_ablation` thì chạy thêm seed 2 và 3. Dưới 0.5 lần ghi "không phân biệt
  được"; trên 1.5 lần ghi "có hiệu ứng".

### 6. S8 chạy một lần, sau mốc

Quyết định này thay thời điểm ghi ở ADR-0030 §6. Sau vòng chọn §4, trên hệ thống thắng, chạy đúng
một lần:

- caption e2e (W5): dev trước, test một lần;
- RQ3 (W6): nạp event của hệ thống thắng, benchmark dev rồi test một lần;
- đổi hệ thống phục vụ (ADR-0029 §1), rồi chạy lại parity 7.1.

Nếu (a) thắng thì không cần S8. Số W5/W6 cũ vẫn giữ và báo song song.

### 7. Lịch

| Thời gian | Việc |
|---|---|
| 26–27/09 | Chốt v2 theo Runbook (ADR-0030 §5); S9 chạy qua đêm |
| 28/09–18/10 | Track 2 (T0 → ADR-0032 → 3 seed); lớp hiếm; seed thêm cho ablation |
| 18/10 | Mốc đóng băng: vòng chọn §4, commit; sau đó test một lần các ứng viên mới và 6 run RQ1-v2 (§2) |
| 19/10–02/11 | S8 một lần; đóng W7 (7.4 image inference; 7.5 test một lần với cấu hình cuối; 7.6; 7.7); bộ lọc từ câu hỏi (§8); viết báo cáo |
| 03–09/11 | Hoàn thiện báo cáo và slide |
| 10–16/11 | Buffer W8, chỉ dùng khi được gia hạn |

### 8. Các duyệt khác cùng ngày

- ADR-0027, ADR-0029, ADR-0030 chuyển sang Accepted. Nguồn event (0027 §2) và hệ thống phục vụ
  (0029 §1) đổi một lần ở S8.
- ADR-0025: cụm từ tiếng Việt được duyệt tạm, xem lại khi hoàn thiện giao diện.
- Push lên nhánh phụ `wip/sed-v2` để sao lưu và chạy CI. Master trên remote chỉ nhận tuần đã xong.
- Chuyển câu hỏi tự nhiên thành bộ lọc: làm sau mốc, dùng Qwen với grammar như ADR-0023, đo độ
  chính xác parse trên query set v2, có ADR riêng. Việc này sẽ làm số RQ3 thấp đi: hiện
  `structured_only` dùng bộ lọc có sẵn trong query set, tức giả định câu hỏi luôn được parse đúng.
- Mở rộng mẫu người cho metric C2 và thêm xác thực: ưu tiên thấp nhất. C2 chỉ mở rộng nếu paper
  theo hướng C (PAPER_NOTES §1).

## Consequences

### Tích cực

- Chỉ một vòng chọn cuối, ứng viên ghi trước. W5/W6 chỉ chạy lại một lần.
- GPU không nằm không: S9 chạy trong lúc Track 2 được chuẩn bị trên CPU.
- Việc viết báo cáo có chỗ trong lịch trước hạn nộp.

### Đánh đổi

- Thêm lượt mở test: ứng viên mới của vòng cuối và từng run của RQ1-v2. Mọi lượt ghi vào sổ test.
- Code train đóng băng trong lúc S9 chạy.
- Ba tuần có thể chỉ đủ cho `frame_mn10`; BEATs/ATST-F là tuỳ chọn.
- Track 2 thêm phụ thuộc ngoài: checkpoint, có thể cả thư viện.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| Chạy S8 ngay khi v2 thắng | Có thể phải chạy lại sau Track 2, thêm lượt mở test cho W5/W6 |
| Chọn hệ thống bằng macro | Đổi thước sau khi đã thấy số v2; nhiễu hơn trên dev nhỏ; các vòng không so được |
| Bỏ RQ1-v2 | Mất câu trả lời "RQ1 âm tính có do kiến trúc thô không"; GPU rảnh bị bỏ phí |
| Track 2 bắt đầu bằng BEATs/ATST-F | Model lớn, rủi ro bộ nhớ 8 GB; `frame_mn10` rẻ để kiểm đường ống trước |
| Không đặt mốc đóng băng | Việc viết báo cáo không có chỗ trong lịch; thí nghiệm có thể kéo tới sát hạn |

## Evidence cần kiểm lại

- Số của PretrainedSED đang ở mức V2 (RELATED_WORK §2.1 (2)). T0 nâng lên V3 trước khi trích.
- Ước lượng 4–6 giờ cho S9 dựa trên thời gian hai run B-v2 đầu (117 và 78 phút mỗi run).
- Tỷ lệ frame dương < 0.5 của v2 mới có 1/3 seed, là số sơ bộ.
- Nguồn liên quan: ADR-0021, ADR-0024, ADR-0030; RELATED_WORK §2.1 (2); PAPER_NOTES §5.
