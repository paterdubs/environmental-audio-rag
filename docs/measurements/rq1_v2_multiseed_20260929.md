# RQ1 — tổng hợp đa seed

> Welch t-test hai phía, `equal_var=False`; không tính lại metric.
> Đọc `evaluation_cv_annotated.json` của từng run. Macro = trung bình F theo lớp (bỏ NaN), như sed_eval.
> Cỡ mẫu nhỏ (n được ghi rõ), nên diễn giải thận trọng.

| Metric | Nhánh | Mean ± SD | Min | Max | n |
|---|---|---:|---:|---:|---:|
| event-based F1 (macro) | B | 0.122084 ± 0.008500 | 0.114126 | 0.131039 | 3 |
| event-based F1 (macro) | C | 0.114666 ± 0.011430 | 0.101600 | 0.122811 | 3 |
| event-based F1 (micro) | B | 0.132355 ± 0.006796 | 0.127476 | 0.140117 | 3 |
| event-based F1 (micro) | C | 0.129428 ± 0.009866 | 0.118531 | 0.137755 | 3 |
| PSDS-1 | B | 0.330475 ± 0.011766 | 0.323282 | 0.344054 | 3 |
| PSDS-1 | C | 0.323826 ± 0.004662 | 0.318650 | 0.327695 | 3 |
| PSDS-2 | B | 0.659191 ± 0.009657 | 0.648802 | 0.667893 | 3 |
| PSDS-2 | C | 0.687051 ± 0.007868 | 0.680373 | 0.695725 | 3 |

## Δ mean (C − B)

| Metric | Δ |
|---|---:|
| event-based F1 (macro) | -0.007417 |
| event-based F1 (micro) | -0.002927 |
| PSDS-1 | -0.006649 |
| PSDS-2 | +0.027860 |

## Welch t-test (C vs B)

| Metric | t | p |
|---|---:|---:|
| event-based F1 (macro) | -0.901912529937 | 0.422018866668 |
| event-based F1 (micro) | -0.423242310208 | 0.69648683891 |
| PSDS-1 | -0.909879817066 | 0.438861616565 |
| PSDS-2 | 3.87392142784 | 0.019333700065 |

Không gọi là có ý nghĩa thống kê khi p ≥ 0.05.