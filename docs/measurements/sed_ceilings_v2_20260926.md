# Trần event-F1 của SED — chẩn đoán trên dev

> Sinh bởi `scripts.report_sed_ceilings`. Chỉ dev + ground truth; không chạm test. Event-F1 = `sed_eval`, collar onset 0.2 s, offset max(0.2 s, 20% độ dài) như protocol.

## 1. Trần do độ phân giải (model hoàn hảo, quyết định theo khối)

| Khối | Độ dài | Event-F1 (collar 0.2 s) | Event-F1 (collar 1 s) |
|---:|---:|---:|---:|
| 1 | 0.01 s | 1.0000 | 1.0000 |
| 4 | 0.04 s | 1.0000 | 1.0000 |
| 8 | 0.08 s | 1.0000 | 1.0000 |
| 16 | 0.16 s | 1.0000 | 1.0000 |
| 32 | 0.32 s | 1.0000 | 1.0000 |
| 64 | 0.64 s | 0.6294 | 0.9966 |
| 128 | 1.28 s | 0.3032 | 0.9549 |

CNN14 trong repo ra quyết định theo khối ≈ 0.64 s (1000 frame → 15 khối; ADR-0014). Mô phỏng làm tròn biên về khối gần nhất nên là **cận trên**.

## 2. Trần do người gán nhãn (cặp recording giống từng byte)

8 cặp, trung bình hai chiều: event-F1 collar 0.2 s **0.5785**, collar 1 s 0.7603. Cỡ mẫu nhỏ — tín hiệu, không phải nghiên cứu agreement.

## 3. Phân rã lỗi hệ thống hiện tại (`sed_ensemble_v2_20260926T150934Z`, dev, in-sample)

| Hạng mục | Số event |
|---|---:|
| Event tham chiếu | 886 |
| Khớp collar (TP) | 148 |
| Chồng đúng lớp nhưng lệch biên | 377 |
| Bỏ sót (không dự đoán nào chồng đúng lớp) | 361 |
| Event dự đoán | 510 |

| Metric | Giá trị |
|---|---:|
| Event-F1 (onset + offset) | 0.2120 |
| Event-F1 chỉ onset | 0.2708 |
| Event-F1 chỉ offset | 0.4914 |
| Segment-based F1 (1 s) | 0.6869 |
