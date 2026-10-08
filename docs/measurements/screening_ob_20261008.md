# Tầng S — sàng lọc bằng CV dev

> Chỉ sàng lọc; không chọn hệ thống cuối hoặc tuyên bố cải thiện. Họ thắng theo CV mean (hòa giữ θ); ghép fold bằng cùng recording/leakage_group. Δ < sd baseline ghi trong nhiễu fold. Không đọc test.

| Run | Họ | Cấu hình | Mean ± sd | 5 fold | Họ thắng |
|---|---|---|---:|---|:---:|
| t2b_seed_20260922 | theta | `global\|25` | 0.2330 ± 0.0400 | 0.2025, 0.2551, 0.2931, 0.2035, 0.2109 | có |
| t2b_seed_20260922 | csebb | `tau0.64_rel2` | 0.2240 ± 0.0660 | 0.1954, 0.2567, 0.2047, 0.3185, 0.1449 | — |
| ob_train_fixes | theta | `global\|25` | 0.2327 ± 0.0499 | 0.1975, 0.2591, 0.3058, 0.1831, 0.2179 | có |
| ob_train_fixes | csebb | `tau0.48_rel2` | 0.2172 ± 0.0467 | 0.1534, 0.2111, 0.2419, 0.2784, 0.2014 | — |

| Ứng viên | So sánh | Δ mean | Fold cao hơn baseline | Cảnh báo |
|---|---|---:|---:|---|
| ob_train_fixes | theta | -0.0004 | 3/5 | trong nhiễu fold |
| ob_train_fixes | csebb | -0.0068 | 2/5 | trong nhiễu fold |
| ob_train_fixes | họ thắng | -0.0004 | 3/5 | trong nhiễu fold |

> Họ thắng của ứng viên giống baseline.
