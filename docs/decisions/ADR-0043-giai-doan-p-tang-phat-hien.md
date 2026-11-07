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

(trống)

## Alternatives considered

| Phương án | Lý do không chọn |
|---|---|
| Chọn lại ensemble B0 + O-D vì macro cao nhất | Đã thua luật chọn micro ở tầng C; chọn lại sau khi thấy số là chọn theo kết quả |
| θ / ngưỡng theo lớp | A2: overfit dev; S55: cận trên oracle chỉ +0.005…+0.045 |
| Thêm model nhận dạng lớn (ATST-F) | O-D cho thấy nhận dạng mạnh hơn không đổi thành event-F1; chi phí GPU cao |

## Consequences

P1 tốn khoảng 10 run frame_mn (~50 phút/run) và không cần code. Nếu không ứng viên nào thắng, kết
quả âm tính vẫn được báo trong PAPER_NOTES và báo cáo; hệ thống cuối vẫn là B0.
