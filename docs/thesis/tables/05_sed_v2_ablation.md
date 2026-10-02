# Bảng ablation SED v2 trên CV dev

> Sinh tự động bởi `scripts.build_thesis_tables` tại git `07fb1a1`.

| Nhóm | Cấu hình | Micro-F1 CV | SD fold | Δ so với v2 seed 1 | Run |
|---|---|---:|---:|---:|---|
| Đầy đủ | v2 đủ (seed 1/3) | 0.1900 | 0.0523 | 0.0000 | sed_polyphonic_20260926T033312Z |
| Đầy đủ | v2 đủ (seed 2/3) | 0.2096 | 0.0510 | 0.0196 | sed_polyphonic_20260926T053024Z |
| Đầy đủ | v2 đủ (seed 3/3) | 0.2169 | 0.0465 | 0.0270 | sed_polyphonic_20260926T064832Z |
| Ablation | không độ phân giải (pool /64) | 0.1060 | 0.0202 | -0.0840 | sed_polyphonic_20260926T075611Z |
| Ablation | trần pos_weight 50 | 0.1773 | 0.0552 | -0.0126 | sed_polyphonic_20260926T085233Z |
| Ablation | không augmentation | 0.1968 | 0.0509 | 0.0068 | sed_polyphonic_20260926T100315Z |
| Tham chiếu | ensemble C v1 | 0.1538 | 0.0214 | -0.0362 | sed_ensemble_C_clean_20260925T045631Z |

**Nguồn:** `docs/measurements/sed_v2_ablation_20260926.json`.
