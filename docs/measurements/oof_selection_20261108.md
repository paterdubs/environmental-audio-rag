# Tầng C — cross-fitted OOF

> θ/λ fit trên các fold khác; cấu hình và họ đã chọn bằng CV trên toàn OOF. CI ghép cặp 1000 lần, seed 20260922, có điều kiện trên lựa chọn đó; không đo bất định do chọn model/họ/cấu hình. Prior duration của mỗi fold suy từ nhãn các fold còn lại, không từ train gốc. Macro theo sed_eval (bỏ NaN). Không đọc test.

| Hệ thống | Họ | Macro | Micro | Nsys/Nref | Recall | Δ micro [95% CI] | Đạt luật |
|---|---|---:|---:|---:|---:|---|:---:|
| B0 | csebb | 0.1797 | 0.2342 | 1761/3294 | 0.1797 | — | — |
| P1 | csebb | 0.1794 | 0.2344 | 1902/3294 | 0.1849 | +0.0002 [-0.0142, +0.0141] | — |

Lựa chọn theo luật: **B0**.
