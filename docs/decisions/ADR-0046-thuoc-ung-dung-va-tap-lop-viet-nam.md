# ADR-0046 — Thước ứng dụng, điểm vận hành ưu tiên phát hiện và tập lớp Việt Nam

**Status:** Accepted (người dùng 09/11/2026: muốn "nới lỏng việc chấm một tí, mục tiêu là phải phát
hiện ra nhiều sự kiện nhất sau đó kèm theo độ chính xác", và "lượt bớt các class mà trong trường
hợp thực tế ở VN khó gặp"; duyệt tập lớp, sàn precision và chế độ demo theo đề xuất cùng ngày).
**Date:** 2026-11-09

## Context

- Thước chính (collar 0.2 s, 21 lớp; macro trước, chọn bằng micro — ADR-0031 §1) chặt hơn độ chính
  xác của chính nhãn: event-F1 người–người 0.5785 ở collar 0.2 s, 0.7603 ở collar 1 s (8 cặp, D6).
- ADR-0041 §1 đã ghi trước segment-F1 1 s và event-F1 collar 1 s là thước "luôn báo kèm, không dùng
  để chọn". ADR-0041 (Alternatives #3) loại việc đổi thước chính sang collar 1 s vì đó là đổi thước
  sau khi thấy số. ADR này giữ nguyên quyết định đó.
- Ứng dụng giám sát cần biết "có sự kiện trong khoảng thời gian đó không" hơn là biên chính xác tới
  0.2 s, và ưu tiên không bỏ sót.
- Thăm dò 09/11 trên OOF (script nháp): bỏ hai lớp hiếm ở Việt Nam chỉ thêm khoảng +0.01 micro; khớp
  theo chồng lấn cho P 0.78–0.82, R 0.62. **Số OOF cho các tập lớp đã được xem trước khi viết ADR
  này** — công khai ở đây, và đó là lý do tập lớp chọn theo tiêu chí thực tế, không theo điểm.

## Decision

### 1. Thước chính không đổi

Event-F1 collar 0.2 s, offset ±max(0.2 s, 0.2·L), 21 lớp polyphonic, `sed_eval`. Báo đầu tiên, macro
trước micro. Mọi vòng chọn hệ thống vẫn dùng micro theo thước này.

### 2. Thước ứng dụng (luôn báo kèm, không dùng để chọn hệ thống)

| Thước | Thư viện | Cấu hình |
|---|---|---|
| Event-F1 collar 1 s | `sed_eval` | đã có (ADR-0041 §1) |
| Segment-F1 1 s | `sed_eval` | đã có (ADR-0041 §1) |
| **Phát hiện theo giao nhau** (mới) | `psds_eval` | DTC 0.1, GTC 0.1, CTTC 0.3 (tiêu chí của PSDS-2); macro F từ `compute_macro_f_score`; micro precision/recall từ chính bảng đếm của thư viện |

Mỗi thước báo kèm trần người theo **cùng tiêu chí**, tính từ 8 cặp recording trùng
(`scripts.report_sed_ceilings::human_agreement`).

### 3. Điểm vận hành "ưu tiên phát hiện"

- Trên lưới ngưỡng của từng hệ thống (λ của B0/V1, t của V2; ADR-0045 §4), chọn điểm có **micro
  recall cao nhất theo tiêu chí giao nhau với điều kiện micro precision ≥ 0.6**, chọn trên các fold
  fit (cross-fit như ADR-0045 §5). Không điểm nào đạt sàn thì lấy điểm có precision cao nhất.
- Báo mọi thước (chính và ứng dụng) ở cả hai điểm vận hành. Điểm F1 vẫn là điểm dùng cho chọn hệ
  thống và so sánh với các giai đoạn trước.

### 4. Tập lớp ứng dụng Việt Nam (19 lớp)

- Bỏ `propeller_aircrafts` (máy bay cánh quạt, hiếm ngoài khu vực sân bay) và
  `crows_seagulls_magpies` (quạ, mòng biển, ác là, ít gặp ở đô thị Việt Nam).
- Giữ `jet_aircrafts` và `train` (phổ biến quanh Tân Sơn Nhất, Nội Bài và đường sắt Bắc–Nam), giữ
  `vehicle_pass_by` và `birds` dù đang yếu (phổ biến bậc nhất ở Việt Nam).
- Chỉ là góc nhìn đánh giá: lọc cả nhãn lẫn dự đoán; model vẫn dự đoán 21 lớp, không train lại.
  Luôn báo cạnh kết quả 21 lớp, không thay thế.

### 5. Demo

Chế độ mặc định của demo là **ưu tiên phát hiện**, có công tắc chuyển sang chế độ F1. Ẩn hai lớp ngoài
tập Việt Nam trên giao diện là tùy chọn cấu hình, mặc định tắt. Thuộc pha tùy chọn của ADR-0045;
không ảnh hưởng số đánh giá.

## Alternatives considered

1. Đổi thước chính sang collar 1 s hoặc chồng lấn: loại, giữ ADR-0041 (đổi thước sau khi thấy số).
2. Bỏ thêm `jet_aircrafts` và `train`: loại; phổ biến ở Việt Nam và lại đúng là lớp model yếu, nên
   trông như chọn theo điểm.
3. Train lại với 19 lớp: loại; không có lý do kỳ vọng tăng, tốn GPU sát mốc 18/11.
4. Gộp lớp dễ nhầm (jet+propeller, idling+pass_by, birds+crows): thăm dò chỉ thêm +0.002 micro;
   không đưa vào.
5. Chọn điểm ưu tiên phát hiện bằng F2: khó giải thích hơn sàn precision; không chọn.

## Consequences

- `ml.evaluation.application_metrics` thêm thước giao nhau, bộ lọc tập lớp, chọn điểm vận hành theo
  sàn precision; `evaluate_run` và báo cáo tầng C in thêm các cột này.
- Chấm lại B0 test theo thước mới để so ghép cặp với LBR là đọc lại output test đã có; ghi sổ test,
  không chọn gì từ đó.

## Evidence cần kiểm lại

- Số thước giao nhau từ `psds_eval` sẽ khác số thăm dò (thăm dò dùng điều kiện có chồng lấn > 0).
- **Tật của `psds_eval` phát hiện khi viết test (09/11):** `compute_macro_f_score` suy số nhãn bằng
  tp / tp_ratio, lớp không có TP thành NaN và bị bỏ khỏi trung bình → macro bị thổi phồng. Số macro
  chính tính số nhãn từ ground truth (lớp bỏ sót hết = 0); số theo ngữ nghĩa thư viện báo kèm
  (`macro_f1_psds_eval`). Micro dùng nguyên bảng đếm của thư viện.
- Trần người chỉ từ 8 cặp; tín hiệu, không phải nghiên cứu agreement.
- Tiêu chí "hiếm ở Việt Nam" là nhận định miền ứng dụng của người dùng, không có số đo tần suất.
