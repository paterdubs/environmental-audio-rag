# Chọn hệ thống SED cuối — chỉ bằng CV trên dev (ADR-0030 §5)

> Sinh bởi `scripts.select_sed_v2`. Không đọc test. Event-F1 **micro** (như ADR-0024), CV 5 fold theo `leakage_group`; điểm = cấu hình hậu xử lý tốt nhất của mỗi ứng viên.
> git `8795960`, dirty=False.

| Hạng | Ứng viên | Run | Model | Họ hậu xử lý | Cấu hình | CV mean ± sd |
|---:|---|---|---:|---|---|---:|
| 1 | v2 ensemble 3 seed ◀ chọn | `sed_ensemble_v2_20260926T150934Z` | 3 | theta | `global\|25` | 0.2129 ± 0.0622 |
| 2 | v2 run đơn (seed 20260922) | `sed_polyphonic_20260926T033312Z` | 1 | theta | `global\|25` | 0.1900 ± 0.0523 |
| 3 | ensemble C v1 | `sed_ensemble_C_clean_20260925T045631Z` | 4 | theta | `global\|25` | 0.1538 ± 0.0214 |

Chênh với `v2 run đơn (seed 20260922)` là +0.0229, **không** lớn hơn sd giữa fold (0.0622) — không được gọi là tốt hơn ứng viên đó.

Bước tiếp: commit file này, rồi mới `scripts.dump_predictions --split test` cho ứng viên được chọn và `scripts.evaluate_run` một lần.
