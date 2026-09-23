# ADR-0017 — Giao thức ECE calibration cho classifier DataSEC (D5)

**Status:** Accepted
**Date:** 2026-09-23

## Context

D5 trên board chỉ ghi "ECE calibration + reliability diagram" — chưa trả lời:
hiệu chuẩn cho head nào, bằng phương pháp nào, trên tập nào, và ECE tính ra sao.
Đây là quyết định kiến trúc/phương pháp, không phải chi tiết lập trình — chốt
trước khi Codex chạm D5, tránh lặp lại kiểu thiếu đặc tả đã chặn D4 (ADR-0016).

Không có code ECE nào trong `ml/evaluation/` — viết mới hoàn toàn theo đặc tả
dưới đây (Codex triển khai, đúng nguyên tắc phân việc ở
[AGENT_SYNC.md §0](../AGENT_SYNC.md)).

## Decision

### 1. Chỉ hiệu chuẩn head **coarse** (22-way), trên DataSEC

Head subclass (28-way) không hiệu chuẩn: 4 lớp có `n_test < 25`
([ADR-0006 §4](ADR-0006-danh-gia-subclass.md)) làm bin theo confidence gần như
trống ở các lớp đó — ECE tính ra sẽ là nhiễu, không phải số đo.

Không hiệu chuẩn trên DataSED: DataSED không có nhãn coarse độc lập theo kiểu
phân loại clip (nó là SED đa nhãn theo frame) — ECE cổ điển giả định phân loại
đơn nhãn có xác suất cộng dồn bằng 1 trên các lớp, không khớp bài toán đa nhãn
đó. Hiệu chuẩn ngưỡng SED đã có protocol riêng ở ADR-0003, không lẫn với ECE.

### 2. Phương pháp: temperature scaling, một tham số vô hướng $T$

Chuẩn của Guo et al. (2017) — chia mọi logit cho $T$ trước softmax:
$p_i = \text{softmax}(z_i / T)$. Chọn vì: (a) không đổi thứ hạng dự đoán (không
ảnh hưởng accuracy/macro-F1 đã báo ở D3), (b) một tham số, không thể overfit
trên tập dev nhỏ.

$T$ tối ưu bằng NLL trên **dev**, khoá lại, áp một lần lên **test** — đúng kỷ
luật `θ` của [ADR-0003](ADR-0003-threshold-va-post-processing.md): không chạm
test để tuning bất cứ thứ gì, kể cả $T$.

### 3. ECE: 15 bin đều theo confidence, báo cả trước và sau hiệu chuẩn

$$\text{ECE} = \sum_{b=1}^{15} \frac{|B_b|}{N} \left| \text{acc}(B_b) - \text{conf}(B_b) \right|$$

Báo **hai số** trên test (giống hai macro-F1 của D4): `ECE trước` (softmax thô,
$T=1$) và `ECE sau` ($T$ đã khoá từ dev). Nếu `ECE sau` không nhỏ hơn `ECE
trước`, đó là kết quả thật cần báo, không phải lỗi — ghi vào Hạn chế, không tự
điều chỉnh $T$ để ép ECE giảm.

### 4. Reliability diagram: một hình, 15 cột, đường chéo tham chiếu

Trục hoành = confidence trung bình mỗi bin, trục tung = accuracy thật mỗi bin.
Cỡ mẫu mỗi bin phải in kèm (không chỉ chiều cao cột) — bin ít mẫu ở vùng
confidence cao/thấp cực trị là hiện tượng thường gặp, cần thấy được để không
đọc nhầm một bin 3 mẫu thành tín hiệu mạnh.

## Nghiệm thu

```bash
.venv/Scripts/python.exe -m scripts.calibrate_classifier ml/runs/<run_id_D1>
```
sinh `docs/measurements/ece_datasec_<ngày>.md` có: $T$ đã chọn, ECE trước/sau
trên test, bảng 15 bin (confidence, accuracy, cỡ mẫu), và ảnh reliability
diagram (`docs/measurements/ece_datasec_<ngày>.png`, không commit ảnh lớn nếu
vượt giới hạn kho — dùng PNG nén, kiểm dung lượng trước khi thêm).

## Alternatives considered

- **Platt scaling / isotonic regression.** Nhiều tham số hơn, dễ overfit trên
  dev cỡ ~740 item (validation DataSEC) — không cần thiết khi temperature
  scaling đã đủ và giữ được thứ hạng dự đoán.
- **Hiệu chuẩn cả head subclass.** Loại vì lý do cỡ mẫu ở mục 1.
- **10 bin thay vì 15.** Cả hai đều là quy ước phổ biến; 15 chọn vì tập test
  DataSEC đủ lớn (740 item) để mỗi bin trung bình ~49 mẫu, không quá thưa.

## Evidence cần kiểm lại

- [ ] Cỡ mẫu bin cực trị (confidence gần 0 hoặc gần 1) sau khi chạy thật — nếu
      có bin < 10 mẫu, ghi rõ trong báo cáo là không đủ tin cậy thống kê.
