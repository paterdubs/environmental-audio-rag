# LBR trong bối cảnh (OOF 564 bản ghi annotated, 21 lớp)

> Sinh bởi `scripts.report_lbr_context`; không đọc test.

| Cấu hình | Micro | Macro | Δ micro [95% CI] |
|---|---:|---:|---|
| B0 (mốc) | 0.2342 | 0.1797 | — |
| Ngưỡng riêng từng lớp (thăm dò) | 0.2335 | — | — |
| Dịch onset toàn cục (thăm dò) | 0.2469 | — | — |
| LBR V1 | 0.3043 | 0.2343 | +0.0701 [+0.0496, +0.0896] so với B0 |
| LBR V2 (số chính) | 0.3332 | 0.2454 | +0.0990 [+0.0761, +0.1200] so với B0 |
| P1×3 (ensemble 3 seed, mốc) | 0.2344 | 0.1794 | — |
| LBR V2 học trên một mô hình, áp lên P1×3 | 0.3505 | 0.2622 | +0.1160 [+0.0933, +0.1373] so với P1x3 |
| Trần: sửa biên mọi hộp 1-1 trong ±1 s | 0.4641 | — | — |

Ngưỡng điểm 'ưu tiên phát hiện' của V2 nằm ở đáy lưới (0,005) ở 5/5 fold.
