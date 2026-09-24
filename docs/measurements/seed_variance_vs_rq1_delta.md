# I7 — biến thiên giữa 2 seed, so với Δ RQ1 (C − B)

> ⚠️ **ĐÃ BỊ BÁC BỎ (24/09).** Báo cáo này chỉ dùng 2 run/nhánh và đánh giá thấp nhiễu giữa các lần chạy. Dữ liệu 5 run/nhánh cho kết luận ngược lại — xem [ADR-0021](../decisions/ADR-0021-rq1-ket-qua-am-tinh.md). Giữ lại làm lịch sử, không trích dẫn.

> Sinh bởi `scripts.report_seed_variance`. Không tính lại metric, chỉ đọc `evaluation.json` đã có của mỗi seed.

## Giá trị theo seed

| Metric | B seed0 | B seed1 | C seed0 | C seed1 |
|---|---:|---:|---:|---:|
| event-based F1 | 0.0479 | 0.0468 | 0.0568 | 0.0561 |
| PSDS-1 | 0.2132 | 0.2419 | 0.2512 | 0.2441 |
| PSDS-2 | 0.6690 | 0.6408 | 0.6290 | 0.6652 |

## Độ biến thiên seed so với Δ RQ1

| Metric | Biến thiên seed B | Biến thiên seed C | \|Δ RQ1\| (C−B, seed0) | Tỷ lệ \|Δ\|/biến thiên lớn nhất | Vượt biến thiên? |
|---|---:|---:|---:|---:|:---:|
| event-based F1 | 0.0011 | 0.0007 | 0.0089 | 8.20× | ✅ có |
| PSDS-1 | 0.0287 | 0.0071 | 0.0380 | 1.32× | ✅ có |
| PSDS-2 | 0.0283 | 0.0363 | 0.0401 | 1.11× | ✅ có |

## Diễn giải
- **event-based F1**: Δ RQ1 vượt biến thiên seed rõ rệt (**8.20×**) — có thể coi là tín hiệu, dù vẫn chỉ 2 seed/nhánh.
- **PSDS-1**: Δ RQ1 vượt biến thiên seed nhưng chỉ **1.32×** — biên rất mỏng (~32%), không đủ chắc để gọi là tín hiệu rõ ràng với chỉ 2 seed/nhánh. Báo cáo cả hai khả năng, không chọn diễn giải có lợi hơn.
- **PSDS-2**: Δ RQ1 vượt biến thiên seed nhưng chỉ **1.11×** — biên rất mỏng (~11%), không đủ chắc để gọi là tín hiệu rõ ràng với chỉ 2 seed/nhánh. Báo cáo cả hai khả năng, không chọn diễn giải có lợi hơn.