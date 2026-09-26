# Sổ test — mọi lần đánh giá trên test

> Sinh bởi `scripts.report_test_ledger`. Chỉ đọc artifact đã có. Mọi dòng dưới đây đã chạy trên test; không có cấu hình nào được chọn bằng test (θ, prior, hệ thống, percentile đều chọn trên dev — ADR-0003, ADR-0024, ADR-0028).

## SED — 22 lần đánh giá trên test

| Run | Đánh giá | Nhánh | Seed | Trần pos_weight | Hậu xử lý | Dirty | Event-F1 | PSDS-1 | PSDS-2 |
|---|---|---|---:|---|---|:---:|---:|---:|---:|
| `sed_ensemble_B_clean_20260925T045606Z` | `evaluation.json` | ensemble B_clean | — | — | `postproc.json` | có | 0.0553 | 0.2996 | 0.6929 |
| `sed_ensemble_B_clean_20260925T045606Z` | `evaluation_cv.json` | ensemble B_clean | — | — | `postproc_cv.json` | có | 0.0969 | 0.3174 | 0.6800 |
| `sed_ensemble_BC_clean_20260925T045658Z` | `evaluation.json` | ensemble BC_clean | — | — | `postproc.json` | có | 0.0696 | 0.3147 | 0.7157 |
| `sed_ensemble_BC_clean_20260925T045658Z` | `evaluation_cv.json` | ensemble BC_clean | — | — | `postproc_cv.json` | có | 0.1001 | 0.3402 | 0.7074 |
| `sed_ensemble_C_clean_20260925T045631Z` | `evaluation.json` | ensemble C_clean | — | — | `postproc.json` | có | 0.0636 | 0.3166 | 0.7053 |
| `sed_ensemble_C_clean_20260925T045631Z` | `evaluation_cv.json` | ensemble C_clean | — | — | `postproc_cv.json` | có | 0.0941 | 0.3489 | 0.6987 |
| `sed_polyphonic_20260923T173234Z` | `evaluation.json` | A | 20260922 | 50 (mặc định) | `postproc.json` | không | 0.0360 | 0.2059 | 0.4514 |
| `sed_polyphonic_20260924T015736Z` | `evaluation.json` | B | 20260922 | 50 (mặc định) | `postproc.json` | có | 0.0616 | 0.2558 | 0.6713 |
| `sed_polyphonic_20260924T021958Z` | `evaluation.json` | C | 20260922 | 50 (mặc định) | `postproc.json` | có | 0.0518 | 0.2950 | 0.6467 |
| `sed_polyphonic_20260924T031616Z` | `evaluation.json` | B | 1 | 50 (mặc định) | `postproc.json` | có | 0.0572 | 0.2753 | 0.6528 |
| `sed_polyphonic_20260924T033537Z` | `evaluation.json` | C | 1 | 50 (mặc định) | `postproc.json` | không | 0.0660 | 0.2779 | 0.6711 |
| `sed_polyphonic_20260924T054531Z` | `evaluation.json` | B | 20260922 | 50 (mặc định) | `postproc.json` | không | 0.0621 | 0.2818 | 0.6456 |
| `sed_polyphonic_20260924T054531Z` | `evaluation_cv.json` | B | 20260922 | 50 (mặc định) | `postproc_cv.json` | không | 0.1048 | 0.2934 | 0.6312 |
| `sed_polyphonic_20260924T061000Z` | `evaluation.json` | C | 20260922 | 50 (mặc định) | `postproc.json` | không | 0.0472 | 0.2873 | 0.6462 |
| `sed_polyphonic_20260924T061000Z` | `evaluation_cv.json` | C | 20260922 | 50 (mặc định) | `postproc_cv.json` | không | 0.0801 | 0.3150 | 0.6324 |
| `sed_polyphonic_20260924T070927Z` | `evaluation.json` | B | 2 | 50 (mặc định) | `postproc.json` | không | 0.0651 | 0.2887 | 0.6512 |
| `sed_polyphonic_20260924T072736Z` | `evaluation.json` | C | 2 | 50 (mặc định) | `postproc.json` | không | 0.0477 | 0.3093 | 0.6634 |
| `sed_polyphonic_20260924T074656Z` | `evaluation.json` | B | 3 | 50 (mặc định) | `postproc.json` | không | 0.0557 | 0.3002 | 0.6525 |
| `sed_polyphonic_20260924T080715Z` | `evaluation.json` | C | 3 | 50 (mặc định) | `postproc.json` | không | 0.0546 | 0.2824 | 0.6557 |
| `sed_polyphonic_20260925T205837Z` | `evaluation.json` | B | 20260922 | 10.0 | `postproc.json` | không | 0.0725 | 0.3010 | 0.6292 |
| `sed_polyphonic_20260925T211704Z` | `evaluation.json` | B | 20260922 | 30.0 | `postproc.json` | không | 0.0548 | 0.2722 | 0.6656 |
| `sed_polyphonic_20260925T213732Z` | `evaluation.json` | B | 20260922 | inf | `postproc.json` | không | 0.0614 | 0.2687 | 0.6643 |

## Thành phần khác chạm test

- **Caption (RQ2)** (8): `caption_grounding_sed_ensemble_C_clean_20260925T045631Z_test.md`, `caption_grounding_sed_polyphonic_20260924T054531Z_test.md`, `caption_lexicon_audit_test_20260925.md`, `caption_ngram_sed_ensemble_C_clean_20260925T045631Z_test.md`, `caption_ngram_sed_polyphonic_20260924T054531Z_test.md`, `caption_per_class_sed_ensemble_C_clean_20260925T045631Z_test.md`, `caption_per_class_sed_polyphonic_20260924T054531Z_test.md`, `caption_vi_template_sed_polyphonic_20260924T054531Z_test.md`
- **Caption: lớp gộp / wiring** (5): `grouped_class_wording_sed_ensemble_C_clean_20260925T045631Z_test.md`, `grouped_class_wording_sed_polyphonic_20260924T054531Z_test.md`, `sed_polyphonic_20260923T173234Z_caption_wiring_test.md`, `sed_polyphonic_20260924T015736Z_caption_wiring_test.md`, `sed_polyphonic_20260924T021958Z_caption_wiring_test.md`
- **Retrieval (RQ3) / câu trả lời** (2): `retrieval_answers_test_20260925.md`, `retrieval_benchmark_test_20260925.md`
- **Ablation / chẩn đoán SED trên test** (13): `branch_per_class_all_20260924.md`, `branch_per_class_clean_20260924.md`, `collar_sensitivity_20260924.md`, `rq1_duration_polyphony_20260924.md`, `sed_polyphonic_20260923T173234Z_duration_prior_ablation_A5.md`, `sed_polyphonic_20260923T173234Z_median_filter_ablation_A3.md`, `sed_polyphonic_20260923T173234Z_threshold_ablation_A2.md`, `sed_polyphonic_20260924T015736Z_duration_prior_ablation_A5.md`, `sed_polyphonic_20260924T015736Z_median_filter_ablation_A3.md`, `sed_polyphonic_20260924T015736Z_threshold_ablation_A2.md`, `sed_polyphonic_20260924T021958Z_duration_prior_ablation_A5.md`, `sed_polyphonic_20260924T021958Z_median_filter_ablation_A3.md`, `sed_polyphonic_20260924T021958Z_threshold_ablation_A2.md`
- **Classifier DataSEC** (2): `d4_consistency_selected_test_20260923.md`, `per_class_metrics_datasec_20260923.md`
- **Parity phục vụ (so với output đóng băng)** (1): `inference_parity_20260925.md`
