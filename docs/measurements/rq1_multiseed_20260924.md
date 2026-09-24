# RQ1 — tổng hợp đa seed

> Welch t-test hai phía, `equal_var=False`; không tính lại metric.
> Cỡ mẫu nhỏ (n được ghi rõ), nên diễn giải thận trọng.

| Metric | Nhánh | Mean ± SD | Min | Max | n |
|---|---|---:|---:|---:|---:|
| event-based F1 | B | 0.050505 ± 0.003934 | 0.046847 | 0.056895 | 5 |
| event-based F1 | C | 0.050889 ± 0.006899 | 0.039558 | 0.056787 | 5 |
| event-based F1 | A | 0.022044 ± N/A | 0.022044 | 0.022044 | 1 |
| PSDS-1 | B | 0.241817 ± 0.017352 | 0.213248 | 0.259578 | 5 |
| PSDS-1 | C | 0.253496 ± 0.013212 | 0.243080 | 0.275782 | 5 |
| PSDS-1 | A | 0.181968 ± N/A | 0.181968 | 0.181968 | 1 |
| PSDS-2 | B | 0.648546 ± 0.011826 | 0.640763 | 0.669036 | 5 |
| PSDS-2 | C | 0.645540 ± 0.013477 | 0.628961 | 0.665225 | 5 |
| PSDS-2 | A | 0.447463 ± N/A | 0.447463 | 0.447463 | 1 |

## Δ mean (C − B)

| Metric | Δ |
|---|---:|
| event-based F1 | +0.000383 |
| PSDS-1 | +0.011679 |
| PSDS-2 | -0.003006 |

## Welch t-test (C vs B)

| Metric | t | p |
|---|---:|---:|
| event-based F1 | 0.107871075194 | 0.917425152291 |
| PSDS-1 | 1.19742939613 | 0.267745138918 |
| PSDS-2 | -0.37489228669 | 0.717644957281 |

Không gọi là có ý nghĩa thống kê khi p ≥ 0.05.

⚠️ Các run `git.dirty=true` vẫn được giữ trong phép tính (không loại):
- `ml\runs\sed_polyphonic_20260924T015736Z`
- `ml\runs\sed_polyphonic_20260924T031616Z`
- `ml\runs\sed_polyphonic_20260924T021958Z`