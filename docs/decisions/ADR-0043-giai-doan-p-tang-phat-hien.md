# ADR-0043 — Giai đoạn P: tăng khả năng phát hiện sau B0

**Status:** Accepted (người dùng yêu cầu 08/11: "vẫn phải tìm cách tăng sự hiệu quả … tập trung
vào tăng khả năng phát hiện sự kiện âm thanh")
**Date:** 2026-11-08

## Context

B0 là hệ thống cuối giai đoạn O (ADR-0041 §11–§12) và đã được test một lần. Chẩn đoán S55: lỗi
chủ đạo là **bỏ sót event (deletion) và lệch onset**, nhất là event dài bị cắt mảnh; model nhận
dạng mạnh hơn (GRU, TF256, O-D) không đổi thành event-F1 (S56). Hạn nộp khóa luận 28/11; báo cáo
cần số cuối trước khoảng 19/11.

## Decision

### 1. Giao thức (giữ ADR-0041 §2)

- Mốc so sánh duy nhất là **B0 OOF** `sed_oof_B0_h5_20261008T130849Z` (micro 0.2342) trên cùng 5
  fold, suy luận hop 5 s tam giác, prior theo fold.
- Ứng viên thay đổi recipe đi qua tầng S (dev, phải vượt seed T2b tốt nhất 0.2330) rồi tầng C.
  Ứng viên **không đổi recipe** (P1) vào thẳng tầng C.
- Luật chọn: ứng viên có micro OOF cao nhất trong số ứng viên có CI 95% của Δ so với B0 nằm trên
  0 (bootstrap ghép cặp 1000 lần, seed 20260922). Không ai đạt → giữ B0.
- **Test:** chỉ mở nếu có ứng viên thắng; khi đó test **thêm một lần** cho hệ thống thắng, báo
  rõ là lần dùng test thứ hai sau O5 (chính sách tái sử dụng thích nghi, ADR-0041 §6 #5).
- Mốc đóng băng giai đoạn P: **18/11**. Việc chưa xong tầng C trước mốc thì không được chọn.

### 2. Ứng viên ghi trước (theo thứ tự chạy)

| # | Ứng viên | Recipe | Tầng S? |
|---|---|---|---|
| P1 | **B0 nhiều seed**: mỗi fold thêm seed 2 và 3 (như T2b {20260922, 2, 3}); hệ thống = trung bình xác suất 3 OOF (15 model) | B0 nguyên vẹn | Không |
| P2 | **KD (O-G)**: student frame_mn recipe B0, target mềm = trung bình xác suất teacher ensemble B0 + O-D của cùng fold, trộn với nhãn cứng | đặc tả chi tiết ghi ở §3 trước khi train | Có |
| P3 | **Cửa sổ train dài 20 s** (suy luận hop 10 s tam giác) | B0 với `--window-seconds 20` | Có |
| P4 | **Augmentation gain ±6 dB + EQ ngẫu nhiên** trên waveform | B0 + augmentation | Có |

P2–P4 cần code mới; mỗi thay đổi code ghi vào §3 trước run đầu tiên của ứng viên đó.

### 3. Chi tiết bổ sung trước khi train (điền dần)

**P3 (ghi 08/11, trước run đầu):** `train_sed --window-seconds 20` (mặc định 10 giữ mọi run cũ);
cửa sổ train/đánh giá trong lúc train = hop 20 s không chồng lấn như B0 ở 10 s; mọi knob khác là
recipe `t2b` + `--train-fixes`, lr 3e-4, batch 24, seed 20260922. Tầng S: như ADR-0041 §2 — CV
θ/cSEBB dev annotated trên prediction dev không chồng lấn của chính run (mốc seed T2b 0.2330 cũng
chấm như vậy). Qua tầng S thì tầng C 5 fold, OOF dựng từ dump hop 10 s tam giác sàn 0.3 (cùng tỉ
lệ hop/cửa sổ 1/2 như B0).

**P4 (ghi 08/11, trước run đầu):** recipe `p4_gaineq` = `t2b` + `gain_eq_p 0.5`: với xác suất 0.5
mỗi batch train (trước mixup), mỗi cửa sổ waveform nhận (a) gain ngẫu nhiên đều trong ±6 dB và
(b) EQ: đường cong gain theo tần số dựng bằng `filter_gains_db` (±6 dB, dạng step/linear như
FilterAugment) trên 64 dải tuyến tính, nội suy tuyến tính lên các bin rFFT của cả cửa sổ, nhân
phổ rồi iFFT. Không clip biên độ. Tầng S như P3; tầng C dùng hop 5 s tam giác như B0.

**P2 (ghi 08/11, trước run đầu):** student = recipe B0 (`t2b` + `--train-fixes`, lr 3e-4,
batch 24, seed 20260922) với `--soft-teachers`: target frame = 0.5·nhãn cứng + 0.5·trung bình xác
suất hai teacher (`ml/training/distill.py`). Teacher dự đoán trên split `train` của chính student
bằng `dump_predictions --split train --hop-seconds 5 --weighting triangular:0.3` (xác suất teacher
trên dữ liệu nó đã train — KD thông thường). Teacher phải cùng `cv_fold` với student, nên không
teacher nào thấy fold giữ lại; code từ chối nếu lệch.
- Tầng S: teacher = O-B `sed_polyphonic_20261008T062333Z` (T2b + sửa dữ liệu, train trên `train`)
  và O-D tầng S `sed_polyphonic_20261009T153325Z`. Chấm như P3.
- Tầng C fold k: teacher = B0 fold k và O-D fold k (các run nguồn của
  `sed_oof_B0_h5_20261008T130849Z` và `sed_oof_OD_h5_20261013T220951Z`); OOF hop 5 s tam giác.

## Alternatives considered

| Phương án | Lý do không chọn |
|---|---|
| Chọn lại ensemble B0 + O-D vì macro cao nhất | Đã thua luật chọn micro ở tầng C; chọn lại sau khi thấy số là chọn theo kết quả |
| θ / ngưỡng theo lớp | A2: overfit dev; S55: cận trên oracle chỉ +0.005…+0.045 |
| Thêm model nhận dạng lớn (ATST-F) | O-D cho thấy nhận dạng mạnh hơn không đổi thành event-F1; chi phí GPU cao |

## Consequences

P1 tốn khoảng 10 run frame_mn (~50 phút/run) và không cần code. Nếu không ứng viên nào thắng, kết
quả âm tính vẫn được báo trong PAPER_NOTES và báo cáo; hệ thống cuối vẫn là B0.
