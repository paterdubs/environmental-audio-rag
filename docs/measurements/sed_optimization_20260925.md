# Tối ưu SED — chọn hậu xử lý và hệ thống trên dev (ADR-0024)

> Sinh bởi `scripts.report_sed_optimization sed_ensemble_B_clean_20260925T045606Z sed_ensemble_C_clean_20260925T045631Z sed_ensemble_BC_clean_20260925T045658Z sed_polyphonic_20260924T054531Z sed_polyphonic_20260924T061000Z`. Không tính lại metric: chỉ đọc `postproc_cv_selection.json`, `evaluation.json`, `evaluation_cv.json` của từng ứng viên.

Luật chọn (ADR-0024 §2–§3, ghi trước khi có số): trong mỗi ứng viên chọn cấu hình có CV mean lớn nhất (không hơn hẳn mặc định thì giữ `per_class` p50); giữa các ứng viên chọn CV mean lớn nhất, hoà thì ít model hơn. Test chỉ để báo.

## 1. CV 5 fold trên dev (event-F1, mean ± sd giữa fold)

| Ứng viên | model | `per_class` p50 | `per_class` p25 | `global` p50 | `global` p25 | chọn |
|---|---:|---:|---:|---:|---:|---|
| ensemble B_clean | 3 | 0.0779 ± 0.0120 | 0.0950 ± 0.0169 | 0.0962 ± 0.0158 | 0.1334 ± 0.0240 | `global` p25 |
| ensemble C_clean | 4 | 0.0662 ± 0.0202 | 0.1078 ± 0.0420 | 0.1057 ± 0.0238 | 0.1538 ± 0.0214 | `global` p25 |
| ensemble BC_clean | 7 | 0.0656 ± 0.0097 | 0.1070 ± 0.0306 | 0.0944 ± 0.0256 | 0.1236 ± 0.0199 | `global` p25 |
| run đơn B `20260924T054531Z` | 1 | 0.0457 ± 0.0184 | 0.0837 ± 0.0342 | 0.0810 ± 0.0204 | 0.1259 ± 0.0367 | `global` p25 |
| run đơn C `20260924T061000Z` | 1 | 0.0579 ± 0.0157 | 0.0893 ± 0.0326 | 0.0781 ± 0.0283 | 0.1198 ± 0.0422 | `global` p25 |

## 2. Hệ thống được chọn (chỉ bằng dev)

**ensemble C_clean** (`sed_ensemble_C_clean_20260925T045631Z`), CV mean 0.1538 ± 0.0214.
Chênh lệch với ứng viên xếp thứ hai `sed_ensemble_B_clean_20260925T045606Z` là +0.0204, **không** lớn hơn sd giữa fold (0.0214) — không được gọi là tốt hơn ứng viên đó (ADR-0024 §3).

## 3. Test — mỗi cấu hình chạy một lần, báo tất cả

| Ứng viên | hậu xử lý | event-F1 [95% CI] | PSDS-1 | PSDS-2 |
|---|---|---:|---:|---:|
| ensemble B_clean | mặc định `per_class` p50 | 0.0553 [0.0355, 0.0773] | 0.2996 | 0.6929 |
| ensemble B_clean | CV `global` p25 | 0.0969 [0.0651, 0.1298] | 0.3174 | 0.6800 |
| ensemble C_clean ◀ chọn | mặc định `per_class` p50 | 0.0636 [0.0395, 0.0886] | 0.3166 | 0.7053 |
| ensemble C_clean ◀ chọn | CV `global` p25 | 0.0941 [0.0624, 0.1277] | 0.3489 | 0.6987 |
| ensemble BC_clean | mặc định `per_class` p50 | 0.0696 [0.0471, 0.0969] | 0.3147 | 0.7157 |
| ensemble BC_clean | CV `global` p25 | 0.1001 [0.0656, 0.1336] | 0.3402 | 0.7074 |
| run đơn B `20260924T054531Z` | mặc định `per_class` p50 | 0.0621 [0.0410, 0.0859] | 0.2818 | 0.6456 |
| run đơn B `20260924T054531Z` | CV `global` p25 | 0.1048 [0.0772, 0.1380] | 0.2934 | 0.6312 |
| run đơn C `20260924T061000Z` | mặc định `per_class` p50 | 0.0472 [0.0301, 0.0671] | 0.2873 | 0.6462 |
| run đơn C `20260924T061000Z` | CV `global` p25 | 0.0801 [0.0549, 0.1079] | 0.3150 | 0.6324 |

⚠️ Có ứng viên với `git.dirty=true` (xem JSON).
