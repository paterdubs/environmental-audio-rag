# Event-F1 micro và macro cho mọi lần đánh giá SED

> Sinh bởi `scripts.report_event_f1_macro`. Macro = nanmean F1 theo lớp đã lưu (= `class_wise_average` của sed_eval); **không chạy lại test**. git `aa5b32a`.

| Run | File | Split | Hậu xử lý | Event-F1 micro | Event-F1 macro |
|---|---|---|---|---:|---:|
| `sed_ensemble_B_clean_20260925T045606Z` | `evaluation.json` | test | `postproc.json` | 0.0553 | 0.0600 |
| `sed_ensemble_B_clean_20260925T045606Z` | `evaluation_cv.json` | test | `postproc_cv.json` | 0.0969 | 0.0811 |
| `sed_ensemble_BC_clean_20260925T045658Z` | `evaluation.json` | test | `postproc.json` | 0.0696 | 0.0683 |
| `sed_ensemble_BC_clean_20260925T045658Z` | `evaluation_cv.json` | test | `postproc_cv.json` | 0.1001 | 0.0854 |
| `sed_ensemble_C_clean_20260925T045631Z` | `evaluation.json` | test | `postproc.json` | 0.0636 | 0.0732 |
| `sed_ensemble_C_clean_20260925T045631Z` | `evaluation_cv.json` | test | `postproc_cv.json` | 0.0941 | 0.0917 |
| `sed_polyphonic_20260923T173234Z` | `evaluation.json` | test | `postproc.json` | 0.0360 | 0.0287 |
| `sed_polyphonic_20260924T015736Z` | `evaluation.json` | test | `postproc.json` | 0.0616 | 0.0671 |
| `sed_polyphonic_20260924T021958Z` | `evaluation.json` | test | `postproc.json` | 0.0518 | 0.0585 |
| `sed_polyphonic_20260924T031616Z` | `evaluation.json` | test | `postproc.json` | 0.0572 | 0.0696 |
| `sed_polyphonic_20260924T033537Z` | `evaluation.json` | test | `postproc.json` | 0.0660 | 0.0796 |
| `sed_polyphonic_20260924T054531Z` | `evaluation.json` | test | `postproc.json` | 0.0621 | 0.0771 |
| `sed_polyphonic_20260924T054531Z` | `evaluation_cv.json` | test | `postproc_cv.json` | 0.1048 | 0.1003 |
| `sed_polyphonic_20260924T061000Z` | `evaluation.json` | test | `postproc.json` | 0.0472 | 0.0555 |
| `sed_polyphonic_20260924T061000Z` | `evaluation_cv.json` | test | `postproc_cv.json` | 0.0801 | 0.0820 |
| `sed_polyphonic_20260924T070927Z` | `evaluation.json` | test | `postproc.json` | 0.0651 | 0.0755 |
| `sed_polyphonic_20260924T072736Z` | `evaluation.json` | test | `postproc.json` | 0.0477 | 0.0658 |
| `sed_polyphonic_20260924T074656Z` | `evaluation.json` | test | `postproc.json` | 0.0557 | 0.0620 |
| `sed_polyphonic_20260924T080715Z` | `evaluation.json` | test | `postproc.json` | 0.0546 | 0.0658 |
| `sed_polyphonic_20260925T205837Z` | `evaluation.json` | test | `postproc.json` | 0.0725 | 0.0694 |
| `sed_polyphonic_20260925T211704Z` | `evaluation.json` | test | `postproc.json` | 0.0548 | 0.0569 |
| `sed_polyphonic_20260925T213732Z` | `evaluation.json` | test | `postproc.json` | 0.0614 | 0.0726 |
