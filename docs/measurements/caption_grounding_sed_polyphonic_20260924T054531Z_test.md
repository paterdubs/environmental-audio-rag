# Grounding caption — `sed_polyphonic_20260924T054531Z` (test)

> Sinh bởi `scripts.score_captions`. Lexicon `caption-lexicon-v2` sha256 `6f5634bb7837817c…`. Mơ hồ xử theo hướng có lợi cho caption (ADR-0022 §3) → Δ so với unconstrained là cận dưới.

| Nhánh / mức | n | Halluc. ↓ | Omission ↓ | Temporal ↑ | Forbidden ↓ | Over-specific ↓ | Context ↓ | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| constrained/e2e | 142 | 0.0000 | 0.2842 | 0.9986 | 0.0000 | 0.0000 | 0.0000 | 2.75 |
| constrained/oracle | 142 | 0.0000 | 0.0995 | 0.9983 | 0.0000 | 0.0000 | 0.0000 | 3.06 |
| template/e2e | 142 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 6.13 |
| template/oracle | 142 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 5.21 |
| unconstrained/e2e | 142 | 0.0038 | 0.0599 | 0.9025 | 0.0141 | 0.1856 | 0.4225 | 3.13 |
| unconstrained/oracle | 142 | 0.0126 | 0.0124 | 0.9413 | 0.0070 | 0.1365 | 0.3239 | 2.01 |
