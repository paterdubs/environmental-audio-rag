# Grounding caption — `sed_ensemble_C_clean_20260925T045631Z` (test)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` `6f5634bb…` · split `d2924a5e…` · taxonomy `67ca8a8c…` · prediction `c5e3007b…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

Temporal = tỷ lệ cặp mention đúng thứ tự onset (cặp bằng nhau tính đúng; **không** phải Kendall τ). Cột "≥2" chỉ tính caption có ít nhất 2 mention — caption 0–1 mention mặc định 1.0.

| Nhánh / mức | n | Halluc. ↓ | Halluc. micro ↓ | Omission ↓ | Temporal ↑ | Temporal ≥2 ↑ (n) | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 142 | 0.0000 | 0.0000 | 0.0358 | 1.0000 | 1.0000 (81) | 0.0000 | 0.0000 | 0.0000 | 2.37 |
| constrained_cover/e2e | 142 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (82) | 0.0000 | 0.0000 | 0.0000 | 2.50 |
| template/e2e | 142 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 (82) | 0.0000 | 0.0000 | 0.0000 | 2.87 |
| unconstrained/e2e | 142 | 0.0047 | 0.0094 | 0.0129 | 0.9542 | 0.8796 (54) | 0.0070 | 0.1305 | 0.4437 | 1.50 |

## CI 95% (bootstrap theo recording, 1000 lần)

| Nhánh / mức | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 0.000 [0.000, 0.000] | 0.036 [0.016, 0.059] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| constrained_cover/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| template/e2e | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| unconstrained/e2e | 0.005 [0.000, 0.012] | 0.013 [0.000, 0.031] | 0.880 [0.782, 0.955] | 0.131 [0.084, 0.181] | 0.444 [0.366, 0.521] | 0.007 [0.000, 0.021] |

## Hiệu số cặp (nhánh trước − nhánh sau), CI 95%

| So sánh | hallucination_rate | omission_rate | temporal_order_eligible | over_specific_rate | context_term_rate | forbidden_term_rate |
|---|---:|---:|---:|---:|---:|---:|
| constrained−unconstrained/e2e | -0.005 [-0.012, +0.000] | +0.023 [-0.004, +0.050] | +0.120 [+0.045, +0.218] | -0.131 [-0.181, -0.084] | -0.444 [-0.521, -0.366] | -0.007 [-0.021, +0.000] |
| constrained_cover−unconstrained/e2e | -0.005 [-0.012, +0.000] | -0.013 [-0.031, +0.000] | +0.120 [+0.045, +0.218] | -0.131 [-0.181, -0.084] | -0.444 [-0.521, -0.366] | -0.007 [-0.021, +0.000] |
| constrained_cover−constrained/e2e | +0.000 [+0.000, +0.000] | -0.036 [-0.059, -0.016] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
