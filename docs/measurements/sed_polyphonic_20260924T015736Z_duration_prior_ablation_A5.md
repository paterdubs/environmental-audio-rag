# Ablation A5 — percentile duration prior — `sed_polyphonic_20260924T015736Z`

> Sinh bởi `scripts.report_duration_prior_ablation ml\runs\sed_polyphonic_20260924T015736Z`. θ per-class giữ nguyên từ `postproc.json` đã đóng băng; chỉ percentile suy `d_min_s`/`g_max_s` đổi. Không sửa artifact chính thức.

Baseline (percentile 5/50, ADR-0003): event-based F1 test = **0.0479**

## Quét percentile `d_min_s` (giữ `g_max_s` ở percentile 50)

| Percentile d_min | Event F1 | Δ so baseline |
|---:|---:|---:|
| 1 | 0.0443 | -0.0037 |
| 5 (baseline) | 0.0479 | +0.0000 |
| 10 | 0.0457 | -0.0022 |
| 25 | 0.0449 | -0.0030 |

## Quét percentile `g_max_s` (giữ `d_min_s` ở percentile 5)

| Percentile g_max | Event F1 | Δ so baseline |
|---:|---:|---:|
| 25 | 0.0607 | +0.0128 |
| 75 | 0.0311 | -0.0168 |

## Diễn giải

Khoảng biến thiên F1 giữa các percentile là **0.0296** — đủ lớn để percentile ảnh hưởng tới kết quả. Xem bảng trên để biết percentile nào tốt hơn baseline; **không** tự đổi percentile chính thức chỉ từ một ablation post-hoc — cần một vòng chọn trên dev nếu muốn thay đổi ADR-0003.