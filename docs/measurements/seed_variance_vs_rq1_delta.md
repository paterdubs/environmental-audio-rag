# I7 — biến thiên giữa 2 seed, so với Δ RQ1 (C − B)

> ⚠️ **ĐÃ BỊ BÁC BỎ (24/09).** Báo cáo này chỉ dùng 2 run/nhánh và đánh giá thấp nhiễu giữa các lần chạy. Dữ liệu 5 run/nhánh cho kết luận ngược lại — xem [ADR-0021](../decisions/ADR-0021-rq1-ket-qua-am-tinh.md). Giữ lại làm lịch sử, không trích dẫn.

> Sinh bởi `scripts.report_seed_variance`. Không tính lại metric, chỉ đọc `evaluation.json` đã có của mỗi seed.

## Giá trị theo seed

| Metric | B seed0 | B seed1 | C seed0 | C seed1 |
|---|---:|---:|---:|---:|
| event-based F1 | 0.0616 | 0.0572 | 0.0518 | 0.0660 |
| PSDS-1 | 0.2558 | 0.2753 | 0.2950 | 0.2779 |
| PSDS-2 | 0.6713 | 0.6528 | 0.6467 | 0.6711 |

## Độ biến thiên seed so với Δ RQ1

| Metric | Biến thiên seed B | Biến thiên seed C | \|Δ RQ1\| (C−B, seed0) | Tỷ lệ \|Δ\|/biến thiên lớn nhất | Vượt biến thiên? |
|---|---:|---:|---:|---:|:---:|
| event-based F1 | 0.0045 | 0.0142 | 0.0098 | 0.69× | ⚠️ KHÔNG |
| PSDS-1 | 0.0196 | 0.0171 | 0.0392 | 2.00× | ✅ có |
| PSDS-2 | 0.0185 | 0.0244 | 0.0246 | 1.01× | ✅ có |

## Diễn giải
- **event-based F1**: Δ RQ1 **không** lớn hơn biến thiên seed — **không thể khẳng định** đây là tín hiệu thật thay vì nhiễu giữa các lần chạy. Phải ghi vào Hạn chế của báo cáo cuối, không diễn giải như kết luận.
- **PSDS-1**: Δ RQ1 vượt biến thiên seed rõ rệt (**2.00×**) — có thể coi là tín hiệu, dù vẫn chỉ 2 seed/nhánh.
- **PSDS-2**: Δ RQ1 vượt biến thiên seed nhưng chỉ **1.01×** — biên rất mỏng (~1%), không đủ chắc để gọi là tín hiệu rõ ràng với chỉ 2 seed/nhánh. Báo cáo cả hai khả năng, không chọn diễn giải có lợi hơn.