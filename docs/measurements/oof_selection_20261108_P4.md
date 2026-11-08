# Tầng C — cross-fitted OOF

> θ/λ fit trên các fold khác; cấu hình và họ đã chọn bằng CV trên toàn OOF. CI ghép cặp 1000 lần, seed 20260922, có điều kiện trên lựa chọn đó; không đo bất định do chọn model/họ/cấu hình. Prior duration của mỗi fold suy từ nhãn các fold còn lại, không từ train gốc. Macro theo sed_eval (bỏ NaN). Không đọc test.

| Hệ thống | Họ | Macro | Micro | Nsys/Nref | Recall | Δ micro [95% CI] | Đạt luật |
|---|---|---:|---:|---:|---:|---|:---:|
| B0 | csebb | 0.1797 | 0.2342 | 1761/3294 | 0.1797 | — | — |
| P4 | csebb | 0.1661 | 0.2260 | 1626/3294 | 0.1688 | -0.0082 [-0.0258, +0.0088] | — |

Lựa chọn theo luật: **B0**.
