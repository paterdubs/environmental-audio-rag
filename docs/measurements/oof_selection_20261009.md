# Tầng C — cross-fitted OOF

> θ/λ fit trên các fold khác; cấu hình và họ đã chọn bằng CV trên toàn OOF. CI ghép cặp 1000 lần, seed 20260922, có điều kiện trên lựa chọn đó; không đo bất định do chọn model/họ/cấu hình. Prior duration của mỗi fold suy từ nhãn các fold còn lại, không từ train gốc. Macro theo sed_eval (bỏ NaN). Không đọc test.

| Hệ thống | Họ | Macro | Micro | Nsys/Nref | Recall | Δ micro [95% CI] | Đạt luật |
|---|---|---:|---:|---:|---:|---|:---:|
| B0 | csebb | 0.1797 | 0.2342 | 1761/3294 | 0.1797 | — | — |
| TFKD | theta | 0.1756 | 0.2076 | 2227/3294 | 0.1740 | -0.0267 [-0.0522, -0.0004] | — |
| TF | theta | 0.1810 | 0.2136 | 2212/3294 | 0.1785 | -0.0206 [-0.0453, +0.0062] | — |
| ENS_B0_TFKD | theta | 0.1939 | 0.2305 | 2111/3294 | 0.1891 | -0.0037 [-0.0293, +0.0248] | — |

Lựa chọn theo luật: **B0**.
