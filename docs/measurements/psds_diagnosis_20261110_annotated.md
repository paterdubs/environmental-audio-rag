# Chẩn đoán PSDS trên dev — annotated (ADR-0048 §2)

> Sinh bởi `scripts.report_psds_diagnosis`. Chỉ dev; v1, v2, f2 là in-sample đối với hậu xử lý đã chọn trên dev, B0 dùng posterior OOF. Không đọc test.

Đầu vào: v1: `sed_ensemble_C_clean_20260925T045631Z` + `sed_ensemble_C_clean_20260925T045631Z/postproc_cv.json` (theta, n=134); v2: `sed_ensemble_v2_20260926T155630Z` + `sed_ensemble_v2_20260926T150934Z/postproc_cv.json` (theta, n=134); f2: `sed_ensemble_t2b_20260927T200914Z` + `sed_ensemble_t2b_20260927T200914Z/sebb_cv_selection_annotated.json` (csebb, n=134); B0: `sed_filtered_B0_oof_dev_20261107T181008Z` + `sed_filtered_B0_oof_dev_20261107T181008Z/sebb_cv_selection_annotated.json` (csebb, n=134).

## PSDS theo lưới và biến thể

| Hệ thống | Lưới | Điểm | Event ở ngưỡng thấp nhất | PSDS-1 | PSDS-2 | PSDS-1 α_st=0 | PSDS-2 α_st=0 | PSDS-1 DTC=GTC=0.5 | eFPR lớn nhất (PSDS-2) | Bỏ vì >50,000 event |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v1 | linear | 19/19 | 3172 | 0.2803 | 0.6356 | 0.5064 | 0.8105 | 0.5080 | 142.2 | 0 |
| v1 | log | 48/48 | 2805 | 0.2559 | 0.6717 | 0.4946 | 0.8326 | 0.4935 | 351.1 | 0 |
| v2 | linear | 19/19 | 1832 | 0.2917 | 0.6278 | 0.5197 | 0.8096 | 0.4796 | 68.5 | 0 |
| v2 | log | 48/48 | 2807 | 0.2805 | 0.6813 | 0.5156 | 0.8431 | 0.4904 | 337.4 | 0 |
| f2 | linear | 19/19 | 14671 | 0.2506 | 0.6478 | 0.4994 | 0.8173 | 0.4472 | 650.3 | 0 |
| f2 | log | 19/48 | 161527 | 0.2457 | 0.6320 | 0.4939 | 0.8053 | 0.4433 | 1793.6 | 29 |
| B0 | linear | 19/19 | 3074 | 0.3075 | 0.6570 | 0.5452 | 0.8277 | 0.4933 | 111.5 | 0 |
| B0 | log | 48/48 | 5694 | 0.2985 | 0.6422 | 0.5355 | 0.8160 | 0.4824 | 162.0 | 0 |

## TPR trung bình các lớp tại eFPR (lưới tuyến tính) và điểm đã chọn

| Hệ thống | Tiêu chí | event-F1 micro | Điểm đã chọn (eFPR, TPR) | TPR@5 | TPR@10 | TPR@30 | TPR@60 | TPR@100 |
|---|---|---:|---|---:|---:|---:|---:|---:|
| v1 | psds_1 | 0.1605 | (1.0, 0.380) | 0.484 | 0.495 | 0.516 | 0.516 | 0.516 |
| v1 | psds_2 | 0.1605 | (0.7, 0.552) | 0.690 | 0.735 | 0.807 | 0.846 | 0.853 |
| v2 | psds_1 | 0.2139 | (1.0, 0.371) | 0.499 | 0.512 | 0.527 | 0.528 | 0.528 |
| v2 | psds_2 | 0.2139 | (1.2, 0.552) | 0.709 | 0.758 | 0.820 | 0.842 | 0.842 |
| f2 | psds_1 | 0.2313 | (0.4, 0.364) | 0.466 | 0.487 | 0.500 | 0.505 | 0.519 |
| f2 | psds_2 | 0.2313 | (0.3, 0.466) | 0.738 | 0.759 | 0.816 | 0.840 | 0.859 |
| B0 | psds_1 | 0.2132 | (0.7, 0.412) | 0.500 | 0.528 | 0.549 | 0.557 | 0.557 |
| B0 | psds_2 | 0.2132 | (0.5, 0.514) | 0.701 | 0.759 | 0.826 | 0.852 | 0.876 |

## AUC theo lớp (lưới tuyến tính, v1 → v2)

| Lớp | PSDS-1 v1 | PSDS-1 v2 | Δ | PSDS-2 v1 | PSDS-2 v2 | Δ |
|---|---:|---:|---:|---:|---:|---:|
| birds | 0.306 | 0.538 | +0.232 | 0.955 | 0.961 | +0.006 |
| cat_fights_and_moans | 0.266 | 0.181 | -0.085 | 0.693 | 0.714 | +0.020 |
| chicken_coop | 0.696 | 0.798 | +0.102 | 0.991 | 0.973 | -0.018 |
| cicadas_and_crickets | 0.500 | 0.541 | +0.042 | 0.787 | 0.760 | -0.027 |
| crows_seagulls_magpies | 0.628 | 0.556 | -0.071 | 0.768 | 0.747 | -0.021 |
| dog_barkings_and_howlings | 0.107 | 0.107 | +0.000 | 0.372 | 0.348 | -0.024 |
| glass_breaking | 0.462 | 0.427 | -0.035 | 0.903 | 0.903 | -0.000 |
| horn | 0.407 | 0.408 | +0.001 | 1.000 | 0.996 | -0.004 |
| injected_psds_world_label | 0.141 | 0.187 | +0.045 | 0.477 | 0.473 | -0.005 |
| jet_aircrafts | 0.404 | 0.454 | +0.050 | 0.799 | 0.788 | -0.011 |
| lawn_mower_brush_cutter_olive_shaker | 0.605 | 0.497 | -0.108 | 0.878 | 0.925 | +0.047 |
| music | 0.613 | 0.563 | -0.051 | 0.873 | 0.882 | +0.009 |
| propeller_aircrafts | 0.893 | 0.898 | +0.005 | 0.922 | 0.896 | -0.027 |
| sirens_and_alarms | 0.589 | 0.548 | -0.041 | 0.742 | 0.716 | -0.026 |
| thunder_fireworks_gunshot | 0.496 | 0.500 | +0.004 | 0.554 | 0.556 | +0.002 |
| train | 0.660 | 0.742 | +0.082 | 0.987 | 0.994 | +0.007 |
| vacuum_cleaner_fan_hairdryer | 0.830 | 0.831 | +0.001 | 0.827 | 0.974 | +0.148 |
| vehicle_idling | 0.333 | 0.355 | +0.021 | 0.809 | 0.736 | -0.073 |
| vehicle_pass_by | 0.288 | 0.275 | -0.014 | 0.799 | 0.838 | +0.039 |
| voices | 0.454 | 0.549 | +0.095 | 0.917 | 0.885 | -0.032 |
| workshop | 0.958 | 0.959 | +0.002 | 0.967 | 0.937 | -0.030 |

## Luật ghi trước (ADR-0048 §2)

Δ = v2 − v1. Δ event-F1 micro dev +0.0534; Δ PSDS lưới tuyến tính: psds_1 +0.0114, psds_2 -0.0078.

**Tái hiện S21 trên dev:** có.

| Giả thuyết | Tiêu chí | Δ trước | Δ sau | Kết luận |
|---|---|---:|---:|---|
| H1 | psds_2 | -0.0078 | +0.0095 | đủ điều kiện |
| H2 | psds_2 | eFPR chọn 1.2 | thấp [] / cao ['5.0', '10.0', '30.0', '60.0', '100.0'] | không |
| H3 | psds_2 | -0.0078 | -0.0010 | đủ điều kiện |

**Đã giải thích S21 trên dev:** có (ít nhất một giả thuyết đủ điều kiện).

git: `5ff89539b264b658020552d5d0d804a4c4fba2d6` dirty=False
