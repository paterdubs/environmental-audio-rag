# Sổ test — mọi lần đánh giá trên test

> Sinh bởi `scripts.report_test_ledger`. Chỉ đọc artifact đã có. Mọi dòng dưới đây đã chạy trên test; không có cấu hình nào được chọn bằng test (θ, prior, hệ thống, percentile đều chọn trên dev — ADR-0003, ADR-0024, ADR-0028).

## SED — 40 lần đánh giá trên test

| Run | Đánh giá | Nhánh | Seed | Trần pos_weight | Hậu xử lý | Dirty | Event-F1 | PSDS-1 | PSDS-2 |
|---|---|---|---:|---|---|:---:|---:|---:|---:|
| `sed_ensemble_B_clean_20260925T045606Z` | `evaluation.json` | ensemble B_clean | — | — | `postproc.json` | có | 0.0553 | 0.2996 | 0.6929 |
| `sed_ensemble_B_clean_20260925T045606Z` | `evaluation_cv.json` | ensemble B_clean | — | — | `postproc_cv.json` | có | 0.0969 | 0.3174 | 0.6800 |
| `sed_ensemble_BC_clean_20260925T045658Z` | `evaluation.json` | ensemble BC_clean | — | — | `postproc.json` | có | 0.0696 | 0.3147 | 0.7157 |
| `sed_ensemble_BC_clean_20260925T045658Z` | `evaluation_cv.json` | ensemble BC_clean | — | — | `postproc_cv.json` | có | 0.1001 | 0.3402 | 0.7074 |
| `sed_ensemble_C_clean_20260925T045631Z` | `evaluation.json` | ensemble C_clean | — | — | `postproc.json` | có | 0.0636 | 0.3166 | 0.7053 |
| `sed_ensemble_C_clean_20260925T045631Z` | `evaluation_cv.json` | ensemble C_clean | — | — | `postproc_cv.json` | có | 0.0941 | 0.3489 | 0.6987 |
| `sed_ensemble_C_clean_20260925T045631Z` | `evaluation_cv_annotated.json` | ensemble C_clean | — | — | `postproc_cv_annotated.json` | có | 0.0945 | 0.3486 | 0.6991 |
| `sed_ensemble_s13_d_20260929T045021Z` | `evaluation_cv_annotated.json` | ensemble s13_d | — | — | `postproc_cv_annotated.json` | không | 0.1323 | 0.3440 | 0.7115 |
| `sed_ensemble_s13_e_20260929T045030Z` | `evaluation_cv_annotated.json` | ensemble s13_e | — | — | `postproc_cv_annotated.json` | không | 0.1392 | 0.3651 | 0.7155 |
| `sed_ensemble_s13_f1_20260929T045044Z` | `evaluation_cv_annotated.json` | ensemble s13_f1 | — | — | `postproc_cv_annotated.json` | không | 0.1817 | 0.4341 | 0.8016 |
| `sed_ensemble_s13_f2_20260929T045053Z` | `evaluation_cv_annotated.json` | ensemble s13_f2 | — | — | `sebb_cv_selection_annotated.json` | không | 0.1643 | 0.3164 | 0.7253 |
| `sed_ensemble_s13_f3_20260929T045102Z` | `evaluation_cv_annotated.json` | ensemble s13_f3 | — | — | `postproc_cv_annotated.json` | không | 0.1544 | 0.4264 | 0.8065 |
| `sed_ensemble_s13_f4_20260929T045115Z` | `evaluation_cv_annotated.json` | ensemble s13_f4 | — | — | `postproc_cv_annotated.json` | không | 0.1543 | 0.3988 | 0.7688 |
| `sed_ensemble_s13_g1_20260929T045129Z` | `evaluation_cv_annotated.json` | ensemble s13_g1 | — | — | `postproc_cv_annotated.json` | không | 0.1774 | 0.3724 | 0.7659 |
| `sed_ensemble_s13_g2_20260929T045146Z` | `evaluation_cv_annotated.json` | ensemble s13_g2 | — | — | `sebb_cv_selection_annotated.json` | không | 0.1722 | 0.3338 | 0.7349 |
| `sed_ensemble_v2_20260926T155630Z` | `evaluation_cv.json` | ensemble v2 | — | — | `postproc_cv.json` | không | 0.1476 | 0.3447 | 0.6744 |
| `sed_ensemble_v2_20260926T155630Z` | `evaluation_cv_annotated.json` | ensemble v2 | — | — | `postproc_cv_annotated.json` | không | 0.1500 | 0.3458 | 0.6767 |
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
| `sed_polyphonic_20260926T033312Z` | `evaluation_cv.json` | B | 20260922 | 10.0 | `postproc_cv.json` | không | 0.1255 | 0.3225 | 0.6657 |
| `sed_polyphonic_20260926T033312Z` | `evaluation_cv_annotated.json` | B | 20260922 | 10.0 | `postproc_cv_annotated.json` | không | 0.1275 | 0.3233 | 0.6679 |
| `sed_polyphonic_20260926T053024Z` | `evaluation_cv_annotated.json` | B | 2 | 10.0 | `postproc_cv.json` | không | 0.1401 | 0.3241 | 0.6488 |
| `sed_polyphonic_20260926T064832Z` | `evaluation_cv_annotated.json` | B | 3 | 10.0 | `postproc_cv.json` | không | 0.1295 | 0.3441 | 0.6609 |
| `sed_polyphonic_20260926T161726Z` | `evaluation_cv_annotated.json` | C | 20260922 | 10.0 | `postproc_cv.json` | không | 0.1378 | 0.3251 | 0.6804 |
| `sed_polyphonic_20260926T172229Z` | `evaluation_cv_annotated.json` | C | 2 | 10.0 | `postproc_cv.json` | không | 0.1320 | 0.3277 | 0.6851 |
| `sed_polyphonic_20260926T185208Z` | `evaluation_cv_annotated.json` | C | 3 | 10.0 | `postproc_cv.json` | không | 0.1185 | 0.3186 | 0.6957 |

## Thành phần khác chạm test

- **Caption (RQ2)** (8): `caption_grounding_sed_ensemble_C_clean_20260925T045631Z_test.md`, `caption_grounding_sed_polyphonic_20260924T054531Z_test.md`, `caption_lexicon_audit_test_20260925.md`, `caption_ngram_sed_ensemble_C_clean_20260925T045631Z_test.md`, `caption_ngram_sed_polyphonic_20260924T054531Z_test.md`, `caption_per_class_sed_ensemble_C_clean_20260925T045631Z_test.md`, `caption_per_class_sed_polyphonic_20260924T054531Z_test.md`, `caption_vi_template_sed_polyphonic_20260924T054531Z_test.md`
- **Caption: lớp gộp / wiring** (5): `grouped_class_wording_sed_ensemble_C_clean_20260925T045631Z_test.md`, `grouped_class_wording_sed_polyphonic_20260924T054531Z_test.md`, `sed_polyphonic_20260923T173234Z_caption_wiring_test.md`, `sed_polyphonic_20260924T015736Z_caption_wiring_test.md`, `sed_polyphonic_20260924T021958Z_caption_wiring_test.md`
- **Retrieval (RQ3) / câu trả lời** (2): `retrieval_answers_test_20260925.md`, `retrieval_benchmark_test_20260925.md`
- **Ablation / chẩn đoán SED trên test** (13): `branch_per_class_all_20260924.md`, `branch_per_class_clean_20260924.md`, `collar_sensitivity_20260924.md`, `rq1_duration_polyphony_20260924.md`, `sed_polyphonic_20260923T173234Z_duration_prior_ablation_A5.md`, `sed_polyphonic_20260923T173234Z_median_filter_ablation_A3.md`, `sed_polyphonic_20260923T173234Z_threshold_ablation_A2.md`, `sed_polyphonic_20260924T015736Z_duration_prior_ablation_A5.md`, `sed_polyphonic_20260924T015736Z_median_filter_ablation_A3.md`, `sed_polyphonic_20260924T015736Z_threshold_ablation_A2.md`, `sed_polyphonic_20260924T021958Z_duration_prior_ablation_A5.md`, `sed_polyphonic_20260924T021958Z_median_filter_ablation_A3.md`, `sed_polyphonic_20260924T021958Z_threshold_ablation_A2.md`
- **Classifier DataSEC** (2): `d4_consistency_selected_test_20260923.md`, `per_class_metrics_datasec_20260923.md`
- **Parity phục vụ (so với output đóng băng)** (4): `inference_parity_20260925.md`, `inference_parity_cpu_20260927.md`, `inference_parity_v2_cpu_20260928.md`, `inference_parity_v2_cuda_20260928.md`
