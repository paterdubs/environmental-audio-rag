# Chẩn đoán PSDS trên dev — all (ADR-0048 §2)

> Sinh bởi `scripts.report_psds_diagnosis`. Chỉ dev; v1, v2, f2 là in-sample đối với hậu xử lý đã chọn trên dev, B0 dùng posterior OOF. Không đọc test.

Đầu vào: v1: `sed_ensemble_C_clean_20260925T045631Z` + `sed_ensemble_C_clean_20260925T045631Z/postproc_cv.json` (theta, n=137); v2: `sed_ensemble_v2_20260926T155630Z` + `sed_ensemble_v2_20260926T150934Z/postproc_cv.json` (theta, n=137); f2: `sed_ensemble_t2b_20260927T200914Z` + `sed_ensemble_t2b_20260927T200914Z/sebb_cv_selection_annotated.json` (csebb, n=137); B0: `sed_filtered_B0_oof_dev_20261107T181008Z` + `sed_filtered_B0_oof_dev_20261107T181008Z/sebb_cv_selection_annotated.json` (csebb, n=134).

## PSDS theo lưới và biến thể

| Hệ thống | Lưới | Điểm | Event ở ngưỡng thấp nhất | PSDS-1 | PSDS-2 | PSDS-1 α_st=0 | PSDS-2 α_st=0 | PSDS-1 DTC=GTC=0.5 | eFPR lớn nhất (PSDS-2) | Bỏ vì >50,000 event |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v1 | linear | 19/19 | 3304 | 0.2806 | 0.6372 | 0.5061 | 0.8112 | 0.5089 | 138.5 | 0 |
| v1 | log | 48/48 | 2868 | 0.2567 | 0.6781 | 0.4948 | 0.8357 | 0.4953 | 337.1 | 0 |
| v2 | linear | 19/19 | 1875 | 0.2921 | 0.6292 | 0.5196 | 0.8103 | 0.4795 | 65.2 | 0 |
| v2 | log | 48/48 | 2871 | 0.2811 | 0.6867 | 0.5157 | 0.8460 | 0.4914 | 333.7 | 0 |
| f2 | linear | 19/19 | 15120 | 0.2523 | 0.6487 | 0.5007 | 0.8189 | 0.4489 | 621.2 | 0 |
| f2 | log | 19/48 | 183349 | 0.2474 | 0.6341 | 0.4953 | 0.8074 | 0.4463 | 1761.6 | 29 |
| B0 | linear | 19/19 | 3074 | 0.3075 | 0.6570 | 0.5452 | 0.8277 | 0.4933 | 111.5 | 0 |
| B0 | log | 48/48 | 5694 | 0.2985 | 0.6422 | 0.5355 | 0.8160 | 0.4824 | 162.0 | 0 |

## TPR trung bình các lớp tại eFPR (lưới tuyến tính) và điểm đã chọn

| Hệ thống | Tiêu chí | event-F1 micro | Điểm đã chọn (eFPR, TPR) | TPR@5 | TPR@10 | TPR@30 | TPR@60 | TPR@100 |
|---|---|---:|---|---:|---:|---:|---:|---:|
| v1 | psds_1 | 0.1588 | (1.1, 0.380) | 0.488 | 0.495 | 0.516 | 0.516 | 0.516 |
| v1 | psds_2 | 0.1588 | (0.8, 0.552) | 0.689 | 0.739 | 0.807 | 0.849 | 0.853 |
| v2 | psds_1 | 0.2120 | (1.0, 0.371) | 0.499 | 0.515 | 0.528 | 0.528 | 0.528 |
| v2 | psds_2 | 0.2120 | (1.3, 0.552) | 0.716 | 0.758 | 0.820 | 0.842 | 0.842 |
| f2 | psds_1 | 0.2298 | (0.5, 0.364) | 0.466 | 0.487 | 0.502 | 0.509 | 0.519 |
| f2 | psds_2 | 0.2298 | (0.4, 0.466) | 0.741 | 0.764 | 0.817 | 0.840 | 0.862 |
| B0 | psds_1 | 0.2132 | (0.7, 0.412) | 0.500 | 0.528 | 0.549 | 0.557 | 0.557 |
| B0 | psds_2 | 0.2132 | (0.5, 0.514) | 0.701 | 0.759 | 0.826 | 0.852 | 0.876 |

## AUC theo lớp (lưới tuyến tính, v1 → v2)

| Lớp | PSDS-1 v1 | PSDS-1 v2 | Δ | PSDS-2 v1 | PSDS-2 v2 | Δ |
|---|---:|---:|---:|---:|---:|---:|
| birds | 0.306 | 0.538 | +0.232 | 0.955 | 0.961 | +0.006 |
| cat_fights_and_moans | 0.268 | 0.182 | -0.086 | 0.701 | 0.720 | +0.019 |
| chicken_coop | 0.694 | 0.798 | +0.103 | 0.991 | 0.973 | -0.017 |
| cicadas_and_crickets | 0.500 | 0.541 | +0.042 | 0.787 | 0.760 | -0.027 |
| crows_seagulls_magpies | 0.628 | 0.557 | -0.071 | 0.768 | 0.747 | -0.021 |
| dog_barkings_and_howlings | 0.107 | 0.107 | +0.000 | 0.373 | 0.349 | -0.024 |
| glass_breaking | 0.464 | 0.428 | -0.036 | 0.903 | 0.903 | -0.000 |
| horn | 0.407 | 0.409 | +0.001 | 1.000 | 0.996 | -0.003 |
| injected_psds_world_label | 0.141 | 0.187 | +0.046 | 0.485 | 0.479 | -0.006 |
| jet_aircrafts | 0.405 | 0.456 | +0.050 | 0.800 | 0.791 | -0.009 |
| lawn_mower_brush_cutter_olive_shaker | 0.605 | 0.498 | -0.108 | 0.880 | 0.925 | +0.045 |
| music | 0.617 | 0.564 | -0.053 | 0.877 | 0.884 | +0.006 |
| propeller_aircrafts | 0.894 | 0.899 | +0.005 | 0.924 | 0.896 | -0.027 |
| sirens_and_alarms | 0.591 | 0.550 | -0.041 | 0.746 | 0.719 | -0.027 |
| thunder_fireworks_gunshot | 0.484 | 0.488 | +0.004 | 0.541 | 0.543 | +0.002 |
| train | 0.661 | 0.743 | +0.082 | 0.988 | 0.994 | +0.006 |
| vacuum_cleaner_fan_hairdryer | 0.826 | 0.827 | +0.001 | 0.823 | 0.970 | +0.148 |
| vehicle_idling | 0.335 | 0.358 | +0.023 | 0.814 | 0.741 | -0.073 |
| vehicle_pass_by | 0.290 | 0.276 | -0.014 | 0.802 | 0.840 | +0.038 |
| voices | 0.455 | 0.550 | +0.095 | 0.919 | 0.888 | -0.031 |
| workshop | 0.949 | 0.957 | +0.008 | 0.958 | 0.935 | -0.023 |

## Luật ghi trước (ADR-0048 §2)

Δ = v2 − v1. Δ event-F1 micro dev +0.0533; Δ PSDS lưới tuyến tính: psds_1 +0.0116, psds_2 -0.0079.

**Tái hiện S21 trên dev:** có.

| Giả thuyết | Tiêu chí | Δ trước | Δ sau | Kết luận |
|---|---|---:|---:|---|
| H1 | psds_2 | -0.0079 | +0.0087 | đủ điều kiện |
| H2 | psds_2 | eFPR chọn 1.3 | thấp [] / cao ['5.0', '10.0', '30.0', '60.0', '100.0'] | không |
| H3 | psds_2 | -0.0079 | -0.0009 | đủ điều kiện |

**Đã giải thích S21 trên dev:** có (ít nhất một giả thuyết đủ điều kiện).

Kiểm nhất quán v1: PSDS lưới tuyến tính tính lại trùng `dev_evaluation_cv.json`.

git: `2a21661ac2a3fab01174e31a1b8d66ab54be6800` dirty=False
