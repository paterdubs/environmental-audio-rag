# Tầng S — sàng lọc bằng CV dev

> Chỉ sàng lọc; không chọn hệ thống cuối hoặc tuyên bố cải thiện. Họ thắng theo CV mean (hòa giữ θ); ghép fold bằng cùng recording/leakage_group. Δ < sd baseline ghi trong nhiễu fold. Không đọc test.

| Run | Họ | Cấu hình | Mean ± sd | 5 fold | Họ thắng |
|---|---|---|---:|---|:---:|
| f2 | theta | `global\|25` | 0.2107 ± 0.0343 | 0.1598, 0.2323, 0.2500, 0.2006, 0.2105 | — |
| f2 | csebb | `tau0.64_rel2` | 0.2383 ± 0.0562 | 0.1860, 0.2889, 0.2358, 0.3008, 0.1799 | có |
| h2.5_triangular0.3 | theta | `global\|25` | 0.2342 ± 0.0424 | 0.2188, 0.2680, 0.2893, 0.2033, 0.1914 | có |
| h2.5_triangular0.3 | csebb | `tau0.64_abs0.3` | 0.2278 ± 0.0388 | 0.1838, 0.2328, 0.2315, 0.2868, 0.2042 | — |
| h2.5_uniform | theta | `global\|25` | 0.2329 ± 0.0340 | 0.2097, 0.2564, 0.2810, 0.2039, 0.2133 | có |
| h2.5_uniform | csebb | `tau0.32_rel1.5` | 0.2303 ± 0.0258 | 0.2028, 0.2500, 0.2212, 0.2642, 0.2132 | — |
| h5_triangular0.3 | theta | `global\|25` | 0.2408 ± 0.0474 | 0.2100, 0.2551, 0.3180, 0.2150, 0.2060 | có |
| h5_triangular0.3 | csebb | `tau0.32_rel1.5` | 0.2377 ± 0.0564 | 0.1928, 0.3011, 0.2297, 0.2900, 0.1752 | — |

| Ứng viên | So sánh | Δ mean | Fold cao hơn baseline | Cảnh báo |
|---|---|---:|---:|---|
| h2.5_triangular0.3 | theta | +0.0235 | 4/5 | trong nhiễu fold |
| h2.5_triangular0.3 | csebb | -0.0105 | 1/5 | trong nhiễu fold |
| h2.5_triangular0.3 | họ thắng | -0.0041 | 3/5 | trong nhiễu fold |
| h2.5_uniform | theta | +0.0222 | 5/5 | trong nhiễu fold |
| h2.5_uniform | csebb | -0.0080 | 2/5 | trong nhiễu fold |
| h2.5_uniform | họ thắng | -0.0054 | 3/5 | trong nhiễu fold |
| h5_triangular0.3 | theta | +0.0302 | 4/5 | trong nhiễu fold |
| h5_triangular0.3 | csebb | -0.0005 | 2/5 | trong nhiễu fold |
| h5_triangular0.3 | họ thắng | +0.0025 | 3/5 | trong nhiễu fold |

> Cảnh báo: h2.5_triangular0.3: họ thắng khác baseline (csebb → theta); xem cả so sánh cùng họ.
> Cảnh báo: h2.5_uniform: họ thắng khác baseline (csebb → theta); xem cả so sánh cùng họ.
> Cảnh báo: h5_triangular0.3: họ thắng khác baseline (csebb → theta); xem cả so sánh cùng họ.
