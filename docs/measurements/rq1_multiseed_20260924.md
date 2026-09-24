# RQ1 — tổng hợp đa seed

> Welch t-test hai phía, `equal_var=False`; không tính lại metric.
> Cỡ mẫu nhỏ (n được ghi rõ), nên diễn giải thận trọng.

| Metric | Nhánh | Mean ± SD | Min | Max | n |
|---|---|---:|---:|---:|---:|
| event-based F1 | B | 0.060356 ± 0.003855 | 0.055699 | 0.065142 | 5 |
| event-based F1 | C | 0.053494 ± 0.007641 | 0.047224 | 0.066025 | 5 |
| event-based F1 | A | 0.036018 ± N/A | 0.036018 | 0.036018 | 1 |
| PSDS-1 | B | 0.280366 ± 0.016544 | 0.255782 | 0.300212 | 5 |
| PSDS-1 | C | 0.290369 ± 0.012351 | 0.277870 | 0.309327 | 5 |
| PSDS-1 | A | 0.205855 ± N/A | 0.205855 | 0.205855 | 1 |
| PSDS-2 | B | 0.654689 ± 0.009742 | 0.645587 | 0.671312 | 5 |
| PSDS-2 | C | 0.656636 ± 0.010784 | 0.646197 | 0.671145 | 5 |
| PSDS-2 | A | 0.451445 ± N/A | 0.451445 | 0.451445 | 1 |

## Δ mean (C − B)

| Metric | Δ |
|---|---:|
| event-based F1 | -0.006862 |
| PSDS-1 | +0.010003 |
| PSDS-2 | +0.001948 |

## Welch t-test (C vs B)

| Metric | t | p |
|---|---:|---:|
| event-based F1 | -1.79301730253 | 0.123868507845 |
| PSDS-1 | 1.08342358407 | 0.312645181209 |
| PSDS-2 | 0.299688088134 | 0.772130482099 |

Không gọi là có ý nghĩa thống kê khi p ≥ 0.05.

⚠️ Các run `git.dirty=true` vẫn được giữ trong phép tính (không loại):
- `ml\runs\sed_polyphonic_20260924T015736Z`
- `ml\runs\sed_polyphonic_20260924T031616Z`
- `ml\runs\sed_polyphonic_20260924T021958Z`