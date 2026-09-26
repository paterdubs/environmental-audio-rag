# SED v2 — ablation bỏ-từng-phần (chỉ dev, ADR-0030 §4)

> Sinh bởi `scripts.report_sed_v2_ablation`. CV event-F1 **micro**, 5 fold dev; git `0a47915`. Không chạm test.

v2 đủ, 3 seed: CV mean 0.2055 ± 0.0139 (sd giữa seed). Ngưỡng nhiễu = 0.0523.

| Cấu hình | Run | Seed | Hậu xử lý | CV mean ± sd (fold) | Δ vs v2 đủ cùng seed | Đọc | AP frame dev |
|---|---|---:|---|---:|---:|---|---:|
| v2 đủ (seed 1/3) | `sed_polyphonic_20260926T033312Z` | 20260922 | theta `global\|25` | 0.1900 ± 0.0523 | — |  | 0.688 |
| v2 đủ (seed 2/3) | `sed_polyphonic_20260926T053024Z` | 2 | theta `global\|25` | 0.2096 ± 0.0510 | — |  | 0.667 |
| v2 đủ (seed 3/3) | `sed_polyphonic_20260926T064832Z` | 3 | theta `global\|25` | 0.2169 ± 0.0465 | — |  | 0.671 |
| không độ phân giải (pool /64) | `sed_polyphonic_20260926T075611Z` | 20260922 | theta `global\|25` | 0.1060 ± 0.0202 | -0.0840 | bỏ đi làm **giảm** | 0.667 |
| trần pos_weight 50 | `sed_polyphonic_20260926T085233Z` | 20260922 | theta `global\|25` | 0.1773 ± 0.0552 | -0.0126 | không phân biệt được | 0.676 |
| không augmentation | `sed_polyphonic_20260926T100315Z` | 20260922 | theta `global\|25` | 0.1968 ± 0.0509 | +0.0068 | không phân biệt được | 0.644 |
| ensemble C v1 | `sed_ensemble_C_clean_20260925T045631Z` | None | theta `global\|25` | 0.1538 ± 0.0214 | — |  | — |
