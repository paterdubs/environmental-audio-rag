# Tầng S — sàng lọc bằng CV dev

> Chỉ sàng lọc; không chọn hệ thống cuối hoặc tuyên bố cải thiện. Họ thắng theo CV mean (hòa giữ θ); ghép fold bằng cùng recording/leakage_group. Δ < sd baseline ghi trong nhiễu fold. Không đọc test.

| Run | Họ | Cấu hình | Mean ± sd | 5 fold | Họ thắng |
|---|---|---|---:|---|:---:|
| f2 | theta | `global\|25` | 0.2107 ± 0.0343 | 0.1598, 0.2323, 0.2500, 0.2006, 0.2105 | — |
| f2 | csebb | `tau0.64_rel2` | 0.2383 ± 0.0562 | 0.1860, 0.2889, 0.2358, 0.3008, 0.1799 | có |
| f2_h2.5_triangular0.3 | theta | `global\|25` | 0.2342 ± 0.0424 | 0.2188, 0.2680, 0.2893, 0.2033, 0.1914 | có |
| f2_h2.5_triangular0.3 | csebb | `tau0.64_abs0.3` | 0.2278 ± 0.0388 | 0.1838, 0.2328, 0.2315, 0.2868, 0.2042 | — |

| Ứng viên | So sánh | Δ mean | Fold cao hơn baseline | Cảnh báo |
|---|---|---:|---:|---|
| f2_h2.5_triangular0.3 | theta | +0.0235 | 4/5 | trong nhiễu fold |
| f2_h2.5_triangular0.3 | csebb | -0.0105 | 1/5 | trong nhiễu fold |
| f2_h2.5_triangular0.3 | họ thắng | -0.0041 | 3/5 | trong nhiễu fold |
