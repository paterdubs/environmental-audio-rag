# Đóng băng artifact báo cáo

> Sinh bởi `scripts.freeze_artifacts`; chỉ đọc file hiện có, không chạy lại huấn luyện hay đánh giá. `MISSING` là thiếu trên máy hiện tại, không phải hash bịa.

Git lúc bắt đầu: `edec27b978fa30a8572fd6c2f8a6afa727ac0fbe` · dirty=False

## Run và ensemble

| Hệ thống | Run | Artifact có/thiếu | Hop (s) | Gộp | Fold |
|---|---|---:|---|---|---|
| v1 A (scratch) | `sed_polyphonic_20260923T173234Z` | 5/0 | — | — | — |
| v1 B (AudioSet) | `sed_polyphonic_20260924T054531Z` | 7/0 | — | — | — |
| v1 C (AudioSet→DataSEC) | `sed_polyphonic_20260924T061000Z` | 7/0 | — | — | — |
| v1 ensemble C | `sed_ensemble_C_clean_20260925T045631Z` | 18/0 | — | — | — |
| v2 B | `sed_polyphonic_20260926T033312Z` | 10/0 | — | — | — |
| v2 ensemble B | `sed_ensemble_v2_20260926T155630Z` | 15/0 | — | — | — |
| C-v2 ensemble | `sed_ensemble_cv2_20260926T205405Z` | 14/0 | — | — | — |
| T2a ensemble | `sed_ensemble_t2a_20260927T141952Z` | 14/0 | — | — | — |
| T2b ensemble (served f2 source) | `sed_ensemble_t2b_20260927T200914Z` | 14/0 | — | — | — |
| Served B0 system (ADR-0042) | `sed_served_B0_20261107T175659Z` | 12/0 | — | — | [0, 1, 2, 3, 4] |
| B0 final test ensemble (ADR-0041 §12) | `sed_ensemble_B0_final_test_20261014T085016Z` | 17/0 | 5.0 | triangular:0.3 | [0, 1, 2, 3, 4] |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `sed_oof_B0_h5_20261008T130849Z` | 20/0 | 5.0 | triangular:0.3 | [0, 1, 2, 3, 4] |
| B0 OOF dev corpus (ADR-0044) | `sed_filtered_B0_oof_dev_20261107T181008Z` | 19/0 | 5.0 | triangular:0.3 | [0, 1, 2, 3, 4] |
| S11 focal ensemble | `sed_ensemble_s11_focal_t2b_20260928T185207Z` | 14/0 | — | — | — |
| S13 f2 test output | `sed_ensemble_s13_f2_20260929T045053Z` | 8/0 | — | — | — |
| phase O: pseudo_datasec_s_20261013T221755Z | `pseudo_datasec_s_20261013T221755Z` | 1/0 | 5.0 | triangular:0.3 | — |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `sed_ensemble_B0_final_test_20261014T085016Z` | 17/0 | 5.0 | triangular:0.3 | [0, 1, 2, 3, 4] |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z` | 14/0 | 2.5 | triangular:0.3 | — |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `sed_ensemble_f2_h2.5_uniform_20261008T074349Z` | 14/0 | 2.5 | uniform | — |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `sed_ensemble_f2_h5_triangular0.3_20261008T064740Z` | 14/0 | 5.0 | triangular:0.3 | — |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `sed_filtered_B0_oof_dev_20261107T181008Z` | 19/0 | 5.0 | triangular:0.3 | [0, 1, 2, 3, 4] |
| phase O: sed_oof_B0_h10_20261008T130820Z | `sed_oof_B0_h10_20261008T130820Z` | 15/0 | — | — | [0, 1, 2, 3, 4] |
| phase O: sed_oof_B0_h5_20261008T130849Z | `sed_oof_B0_h5_20261008T130849Z` | 20/0 | 5.0 | triangular:0.3 | [0, 1, 2, 3, 4] |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `sed_oof_ENS_B0_OD_h5_20261013T221030Z` | 37/0 | 5.0 | triangular:0.3 | [0, 1, 2, 3, 4] |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `sed_oof_ENS_B0_TFKD_h5_20261008T224454Z` | 37/0 | 5.0 | triangular:0.3 | [0, 1, 2, 3, 4] |
| phase O: sed_oof_OD_h5_20261013T220951Z | `sed_oof_OD_h5_20261013T220951Z` | 20/0 | 5.0 | triangular:0.3 | [0, 1, 2, 3, 4] |
| phase O: sed_oof_TF_h10_20261009T035119Z | `sed_oof_TF_h10_20261009T035119Z` | 15/0 | — | — | [0, 1, 2, 3, 4] |
| phase O: sed_oof_TF_h5_20261009T035153Z | `sed_oof_TF_h5_20261009T035153Z` | 20/0 | 5.0 | triangular:0.3 | [0, 1, 2, 3, 4] |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `sed_oof_TFKD_h10_20261008T224140Z` | 15/0 | — | — | [0, 1, 2, 3, 4] |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `sed_oof_TFKD_h5_20261008T224209Z` | 20/0 | 5.0 | triangular:0.3 | [0, 1, 2, 3, 4] |
| phase O: sed_polyphonic_20261008T092903Z | `sed_polyphonic_20261008T092903Z` | 3/0 | — | — | 0 |
| phase O: sed_polyphonic_20261008T102530Z | `sed_polyphonic_20261008T102530Z` | 3/0 | — | — | 1 |
| phase O: sed_polyphonic_20261008T111605Z | `sed_polyphonic_20261008T111605Z` | 3/0 | — | — | 2 |
| phase O: sed_polyphonic_20261008T115845Z | `sed_polyphonic_20261008T115845Z` | 3/0 | — | — | 3 |
| phase O: sed_polyphonic_20261008T123531Z | `sed_polyphonic_20261008T123531Z` | 3/0 | — | — | 4 |
| phase O: sed_polyphonic_20261008T185245Z | `sed_polyphonic_20261008T185245Z` | 3/0 | — | — | 0 |
| phase O: sed_polyphonic_20261008T193842Z | `sed_polyphonic_20261008T193842Z` | 3/0 | — | — | 1 |
| phase O: sed_polyphonic_20261008T202607Z | `sed_polyphonic_20261008T202607Z` | 3/0 | — | — | 2 |
| phase O: sed_polyphonic_20261008T211301Z | `sed_polyphonic_20261008T211301Z` | 3/0 | — | — | 3 |
| phase O: sed_polyphonic_20261008T215900Z | `sed_polyphonic_20261008T215900Z` | 3/0 | — | — | 4 |
| phase O: sed_polyphonic_20261008T224300Z | `sed_polyphonic_20261008T224300Z` | 3/0 | — | — | 0 |
| phase O: sed_polyphonic_20261008T234743Z | `sed_polyphonic_20261008T234743Z` | 3/0 | — | — | 1 |
| phase O: sed_polyphonic_20261009T005328Z | `sed_polyphonic_20261009T005328Z` | 3/0 | — | — | 2 |
| phase O: sed_polyphonic_20261009T015949Z | `sed_polyphonic_20261009T015949Z` | 3/0 | — | — | 3 |
| phase O: sed_polyphonic_20261009T030150Z | `sed_polyphonic_20261009T030150Z` | 3/0 | — | — | 4 |
| phase O: sed_polyphonic_20261013T180511Z | `sed_polyphonic_20261013T180511Z` | 3/0 | — | — | 0 |
| phase O: sed_polyphonic_20261013T185600Z | `sed_polyphonic_20261013T185600Z` | 3/0 | — | — | 1 |
| phase O: sed_polyphonic_20261013T194339Z | `sed_polyphonic_20261013T194339Z` | 3/0 | — | — | 2 |
| phase O: sed_polyphonic_20261013T203013Z | `sed_polyphonic_20261013T203013Z` | 3/0 | — | — | 3 |
| phase O: sed_polyphonic_20261013T211846Z | `sed_polyphonic_20261013T211846Z` | 3/0 | — | — | 4 |
| phase O: sed_rewindow_B0_f0_h5_20261008T130621Z | `sed_rewindow_B0_f0_h5_20261008T130621Z` | 4/0 | 5.0 | triangular:0.3 | 0 |
| phase O: sed_rewindow_B0_f0_h5_test_20261014T084758Z | `sed_rewindow_B0_f0_h5_test_20261014T084758Z` | 4/0 | 5.0 | triangular:0.3 | 0 |
| phase O: sed_rewindow_B0_f1_h5_20261008T130644Z | `sed_rewindow_B0_f1_h5_20261008T130644Z` | 4/0 | 5.0 | triangular:0.3 | 1 |
| phase O: sed_rewindow_B0_f1_h5_test_20261014T084829Z | `sed_rewindow_B0_f1_h5_test_20261014T084829Z` | 4/0 | 5.0 | triangular:0.3 | 1 |
| phase O: sed_rewindow_B0_f2_h5_20261008T130708Z | `sed_rewindow_B0_f2_h5_20261008T130708Z` | 4/0 | 5.0 | triangular:0.3 | 2 |
| phase O: sed_rewindow_B0_f2_h5_test_20261014T084856Z | `sed_rewindow_B0_f2_h5_test_20261014T084856Z` | 4/0 | 5.0 | triangular:0.3 | 2 |
| phase O: sed_rewindow_B0_f3_h5_20261008T130733Z | `sed_rewindow_B0_f3_h5_20261008T130733Z` | 4/0 | 5.0 | triangular:0.3 | 3 |
| phase O: sed_rewindow_B0_f3_h5_test_20261014T084923Z | `sed_rewindow_B0_f3_h5_test_20261014T084923Z` | 4/0 | 5.0 | triangular:0.3 | 3 |
| phase O: sed_rewindow_B0_f4_h5_20261008T130755Z | `sed_rewindow_B0_f4_h5_20261008T130755Z` | 4/0 | 5.0 | triangular:0.3 | 4 |
| phase O: sed_rewindow_B0_f4_h5_test_20261014T084950Z | `sed_rewindow_B0_f4_h5_test_20261014T084950Z` | 4/0 | 5.0 | triangular:0.3 | 4 |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m1_20261008T060426Z | `sed_rewindow_f2_h2.5_triangular0.3_m1_20261008T060426Z` | 4/0 | 2.5 | triangular:0.3 | — |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m2_20261008T060530Z | `sed_rewindow_f2_h2.5_triangular0.3_m2_20261008T060530Z` | 4/0 | 2.5 | triangular:0.3 | — |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m3_20261008T060629Z | `sed_rewindow_f2_h2.5_triangular0.3_m3_20261008T060629Z` | 4/0 | 2.5 | triangular:0.3 | — |
| phase O: sed_rewindow_f2_h2.5_uniform_m1_20261008T073910Z | `sed_rewindow_f2_h2.5_uniform_m1_20261008T073910Z` | 4/0 | 2.5 | uniform | — |
| phase O: sed_rewindow_f2_h2.5_uniform_m2_20261008T074045Z | `sed_rewindow_f2_h2.5_uniform_m2_20261008T074045Z` | 4/0 | 2.5 | uniform | — |
| phase O: sed_rewindow_f2_h2.5_uniform_m3_20261008T074220Z | `sed_rewindow_f2_h2.5_uniform_m3_20261008T074220Z` | 4/0 | 2.5 | uniform | — |
| phase O: sed_rewindow_f2_h5_triangular0.3_m1_20261008T064524Z | `sed_rewindow_f2_h5_triangular0.3_m1_20261008T064524Z` | 4/0 | 5.0 | triangular:0.3 | — |
| phase O: sed_rewindow_f2_h5_triangular0.3_m2_20261008T064611Z | `sed_rewindow_f2_h5_triangular0.3_m2_20261008T064611Z` | 4/0 | 5.0 | triangular:0.3 | — |
| phase O: sed_rewindow_f2_h5_triangular0.3_m3_20261008T064653Z | `sed_rewindow_f2_h5_triangular0.3_m3_20261008T064653Z` | 4/0 | 5.0 | triangular:0.3 | — |
| phase O: sed_rewindow_OD_f0_h5_20261013T220452Z | `sed_rewindow_OD_f0_h5_20261013T220452Z` | 4/0 | 5.0 | triangular:0.3 | 0 |
| phase O: sed_rewindow_OD_f1_h5_20261013T220548Z | `sed_rewindow_OD_f1_h5_20261013T220548Z` | 4/0 | 5.0 | triangular:0.3 | 1 |
| phase O: sed_rewindow_OD_f2_h5_20261013T220645Z | `sed_rewindow_OD_f2_h5_20261013T220645Z` | 4/0 | 5.0 | triangular:0.3 | 2 |
| phase O: sed_rewindow_OD_f3_h5_20261013T220747Z | `sed_rewindow_OD_f3_h5_20261013T220747Z` | 4/0 | 5.0 | triangular:0.3 | 3 |
| phase O: sed_rewindow_OD_f4_h5_20261013T220845Z | `sed_rewindow_OD_f4_h5_20261013T220845Z` | 4/0 | 5.0 | triangular:0.3 | 4 |
| phase O: sed_rewindow_TF_f0_h5_20261009T034839Z | `sed_rewindow_TF_f0_h5_20261009T034839Z` | 4/0 | 5.0 | triangular:0.3 | 0 |
| phase O: sed_rewindow_TF_f1_h5_20261009T034909Z | `sed_rewindow_TF_f1_h5_20261009T034909Z` | 4/0 | 5.0 | triangular:0.3 | 1 |
| phase O: sed_rewindow_TF_f2_h5_20261009T034941Z | `sed_rewindow_TF_f2_h5_20261009T034941Z` | 4/0 | 5.0 | triangular:0.3 | 2 |
| phase O: sed_rewindow_TF_f3_h5_20261009T035014Z | `sed_rewindow_TF_f3_h5_20261009T035014Z` | 4/0 | 5.0 | triangular:0.3 | 3 |
| phase O: sed_rewindow_TF_f4_h5_20261009T035045Z | `sed_rewindow_TF_f4_h5_20261009T035045Z` | 4/0 | 5.0 | triangular:0.3 | 4 |
| phase O: sed_rewindow_TFKD_f0_h5_20261008T223935Z | `sed_rewindow_TFKD_f0_h5_20261008T223935Z` | 4/0 | 5.0 | triangular:0.3 | 0 |
| phase O: sed_rewindow_TFKD_f1_h5_20261008T223959Z | `sed_rewindow_TFKD_f1_h5_20261008T223959Z` | 4/0 | 5.0 | triangular:0.3 | 1 |
| phase O: sed_rewindow_TFKD_f2_h5_20261008T224023Z | `sed_rewindow_TFKD_f2_h5_20261008T224023Z` | 4/0 | 5.0 | triangular:0.3 | 2 |
| phase O: sed_rewindow_TFKD_f3_h5_20261008T224049Z | `sed_rewindow_TFKD_f3_h5_20261008T224049Z` | 4/0 | 5.0 | triangular:0.3 | 3 |
| phase O: sed_rewindow_TFKD_f4_h5_20261008T224114Z | `sed_rewindow_TFKD_f4_h5_20261008T224114Z` | 4/0 | 5.0 | triangular:0.3 | 4 |
| phase O: sed_served_B0_20261107T175659Z | `sed_served_B0_20261107T175659Z` | 12/0 | — | — | [0, 1, 2, 3, 4] |

## SHA-256 và sự tồn tại

| Nhóm | Đường dẫn | Kiểu | Tồn tại | SHA-256 |
|---|---|---|:---:|---|
| v1 A (scratch) | `ml/runs/sed_polyphonic_20260923T173234Z/manifest.json` | run_manifest | có | `9c9eb5452573b8e358ca22fdfdaedaa4e25a093309761868f3bfea74dc5435ec` |
| v1 A (scratch) | `ml/runs/sed_polyphonic_20260923T173234Z/predictions/dev.npz` | prediction | có | `fc01a3e14bcf86a9ff016b024dcb7a20d9da4de75a05a8a214737ef0a9636bc0` |
| v1 A (scratch) | `ml/runs/sed_polyphonic_20260923T173234Z/predictions/test.npz` | prediction | có | `664b61cc72b7905693151f10d680c4cafca4d2826efb39f4f66cbaa3d8f1a04a` |
| v1 A (scratch) | `ml/runs/sed_polyphonic_20260923T173234Z/postproc.json` | postproc_or_sebb | có | `88bd1df200053c89d121db04d45896cdee7434dc1bd83a4802a445dd0607e8e9` |
| v1 A (scratch) | `ml/runs/sed_polyphonic_20260923T173234Z/checkpoints/best.pt` | best_checkpoint | có | `2f0fc26f732b36c90590e2313aeadf95c847d33803e6370263145ddb204227fc` |
| v1 B (AudioSet) | `ml/runs/sed_polyphonic_20260924T054531Z/manifest.json` | run_manifest | có | `952d6fd3112fa9ef73a95f359168b561ae909659d5dc971c086328c7b48ee703` |
| v1 B (AudioSet) | `ml/runs/sed_polyphonic_20260924T054531Z/predictions/dev.npz` | prediction | có | `9cd0e7b74aca16d15921de27af390bfa29f5ee7c6324824fdf347067f83ef28f` |
| v1 B (AudioSet) | `ml/runs/sed_polyphonic_20260924T054531Z/predictions/test.npz` | prediction | có | `42818510d015469a678db5530eee37f51f8b01fd53c6c150a708e870a32fa430` |
| v1 B (AudioSet) | `ml/runs/sed_polyphonic_20260924T054531Z/postproc.json` | postproc_or_sebb | có | `3caf552f87c17b2e5b8082466a3823fcab639cf6ed49ad045b612107236522ae` |
| v1 B (AudioSet) | `ml/runs/sed_polyphonic_20260924T054531Z/postproc_cv.json` | postproc_or_sebb | có | `384b1c588f27b9ba572e1b8fd23d56d4a7e971f665bba69e56f3d2f046377fa9` |
| v1 B (AudioSet) | `ml/runs/sed_polyphonic_20260924T054531Z/postproc_cv_selection.json` | postproc_or_sebb | có | `e8e7e98c364f5ea7df4ad48cff26dd4d9da0057e1977b0cd9a61bcf8dd06a670` |
| v1 B (AudioSet) | `ml/runs/sed_polyphonic_20260924T054531Z/checkpoints/best.pt` | best_checkpoint | có | `428896df645e84180e0e28308665c698b5d89c22fe2348c96760e858e37dcdd4` |
| v1 C (AudioSet→DataSEC) | `ml/runs/sed_polyphonic_20260924T061000Z/manifest.json` | run_manifest | có | `e29ae57720789624867090b98643c2e312c814a9c901504feca0ff351a65d692` |
| v1 C (AudioSet→DataSEC) | `ml/runs/sed_polyphonic_20260924T061000Z/predictions/dev.npz` | prediction | có | `eb189a28ddcd0eed3f040e559b8d1cf58fa56d4db0efab364a8750b6b2c3524c` |
| v1 C (AudioSet→DataSEC) | `ml/runs/sed_polyphonic_20260924T061000Z/predictions/test.npz` | prediction | có | `8561bd0639051114125cc130e8a40768cde79c5e1aa37c4990bcc37c11ffc0b8` |
| v1 C (AudioSet→DataSEC) | `ml/runs/sed_polyphonic_20260924T061000Z/postproc.json` | postproc_or_sebb | có | `0dd954c84218d38e91879f64040110a47a09d84334b486765ed8a987d7b8bac1` |
| v1 C (AudioSet→DataSEC) | `ml/runs/sed_polyphonic_20260924T061000Z/postproc_cv.json` | postproc_or_sebb | có | `d929c9073eba8c15bd90e986f46e549964ac86e8e137cee3eb894daf4e05fd7b` |
| v1 C (AudioSet→DataSEC) | `ml/runs/sed_polyphonic_20260924T061000Z/postproc_cv_selection.json` | postproc_or_sebb | có | `ee5aaaef637350b06c3035a17040b41fb7eef05b038c673ed0bd210595ff8da0` |
| v1 C (AudioSet→DataSEC) | `ml/runs/sed_polyphonic_20260924T061000Z/checkpoints/best.pt` | best_checkpoint | có | `39dd7fe721d5da470f328763c6e26a04a2fa3f521304246eb6e8f7e0bc4ca229` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/manifest.json` | run_manifest | có | `27f84d8685faab1070751adf241a5ebb3ee5ca3fb4153e5dfc955be3c7c14f05` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/predictions/dev.npz` | prediction | có | `4af86f6d7966773007693e451274bc3608e1b857981ce1b6a78bcd8b300e9574` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/predictions/test.npz` | prediction | có | `ea87a2ea6c52159729780715825cbac616f756f07643c1d76f7ab1c5fca99f1e` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/postproc.json` | postproc_or_sebb | có | `72b89077c7aa6e071d86c4330311e6d6db8e63a60774a86d91b759b4b31ee050` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/postproc_cv.json` | postproc_or_sebb | có | `d05c7e00ba3c9df7190f88c9a711e4c39d9c1241f40df0ee2556780ef2a1962f` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `d05c7e00ba3c9df7190f88c9a711e4c39d9c1241f40df0ee2556780ef2a1962f` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/postproc_cv_selection.json` | postproc_or_sebb | có | `3e34c09dcd4756fc14148886f8c28aaa18afcc25d2fd5b08a98d53e2e28e5398` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `a6d9bea572b4ee54474924ae633db53227e7b07ecb15e85d338b4e8fb05653e3` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/sebb_cv_selection.json` | postproc_or_sebb | có | `595086477ed8d08c2bef9674d07252982bd52270739ec2a4ae51db4939e87c4e` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `827111907cfdd9f5bf536fa5b639556178797c6166edb1a726382a1103a806df` |
| v1 ensemble C | `ml/runs/sed_polyphonic_20260924T033537Z/manifest.json` | dependency_manifest | có | `dec6541d6a94d6b9183e7824ffd0d46dd587686b3b9291fd5b6179d36e39f044` |
| v1 ensemble C | `ml/runs/sed_polyphonic_20260924T061000Z/manifest.json` | dependency_manifest | có | `e29ae57720789624867090b98643c2e312c814a9c901504feca0ff351a65d692` |
| v1 ensemble C | `ml/runs/sed_polyphonic_20260924T072736Z/manifest.json` | dependency_manifest | có | `ecaee872df41f2b4b34d688202fa28593c0885c183080b15096353ffed411fa1` |
| v1 ensemble C | `ml/runs/sed_polyphonic_20260924T080715Z/manifest.json` | dependency_manifest | có | `edb4884b8f5c0566110842f7aa768e8605f87bbc75bf7a81da3e233b30b583c1` |
| v1 ensemble C | `ml/runs/sed_polyphonic_20260924T033537Z/checkpoints/best.pt` | best_checkpoint | có | `33b48f66954aa03013e9e18432c0650cf8bbe1b020d3762c2e0a84e5e9f38938` |
| v1 ensemble C | `ml/runs/sed_polyphonic_20260924T061000Z/checkpoints/best.pt` | best_checkpoint | có | `39dd7fe721d5da470f328763c6e26a04a2fa3f521304246eb6e8f7e0bc4ca229` |
| v1 ensemble C | `ml/runs/sed_polyphonic_20260924T072736Z/checkpoints/best.pt` | best_checkpoint | có | `62333fa6c40b2030b647cb97965d17febcdc8c5438657b7fe632806f12973124` |
| v1 ensemble C | `ml/runs/sed_polyphonic_20260924T080715Z/checkpoints/best.pt` | best_checkpoint | có | `99b7c6f0783552bc591d4fb709e594488c424129b74e86204fd50e8cc88c94ab` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/manifest.json` | run_manifest | có | `3b23ab0658c219d249a14118185cb427e8e65c5f93e76d18baaf4ffd287b3e46` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/predictions/dev.npz` | prediction | có | `afda4e5c58ccaed641968855a5fa694b2a176ffa61bad05b71711663092e8c88` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/predictions/test.npz` | prediction | có | `15fa4cef90b561c639417bd761c41db8f53b778e1b3177005a362147e307c555` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/postproc_cv.json` | postproc_or_sebb | có | `49d2f412420f33e49824c227c59a194c94d513a4eccb520039640809c2c8c176` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `49d2f412420f33e49824c227c59a194c94d513a4eccb520039640809c2c8c176` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/postproc_cv_selection.json` | postproc_or_sebb | có | `39811afb908831172e8e15bb1bed1dc4d89d323efe71849bc0b0a26e3f6ecbcd` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `428a5fea7ccd6c17a448d43019bd56f362e70d8828215d1ffb942aec82adaea0` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/sebb_cv_selection.json` | postproc_or_sebb | có | `afeaa5437bb5bf220ae8b1136452e4e5f6dbf7a69fd361bb97d13bc3e3480aa5` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `bd6b7951dabaccfeb2460ac740196c3eceae50f3820ccb359f9dff7fd3f39275` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/checkpoints/best.pt` | best_checkpoint | có | `4c340341c3bd788a42ea542e27c50dc9e2c1efcf09336fdd254d5e2956d52f8d` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/manifest.json` | run_manifest | có | `b645368cd003d713de53050e6a9a4de86bb930618616b557fe64bc8b2ab590e9` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/predictions/dev.npz` | prediction | có | `55ed1fa87d486d7813c9fcae65c863e13039f00dd1ad69425b205787df3abe18` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/predictions/test.npz` | prediction | có | `86554be67758970d32da8e427feb7e921fb1e7960670d23ed4fe171a864a7597` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/postproc_cv.json` | postproc_or_sebb | có | `765f4141fb840249e3765e410d982c5f64c3c3a1a18e338cd4a0b9fb560aa2d6` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `765f4141fb840249e3765e410d982c5f64c3c3a1a18e338cd4a0b9fb560aa2d6` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/postproc_cv_selection.json` | postproc_or_sebb | có | `bba2b5ec94c801bfe26393935b2903330ed8f12c19e82fd7f9e39dbfd54f5a6a` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `2e86c3e5aa486e11f01ca87e99dcf071609eb640dcb996618a8a87d7909902d0` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/sebb_cv_selection.json` | postproc_or_sebb | có | `a7bd0fb402589e5167eb15aa3d947ff9b8afe4fdbcc0caa0faf07196a0f7a9fe` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `a4cd11307dc4aefbddb4d2ed9bcde09c48c3bba4431debc25a236e02d7ba9020` |
| v2 ensemble B | `ml/runs/sed_polyphonic_20260926T033312Z/manifest.json` | dependency_manifest | có | `3b23ab0658c219d249a14118185cb427e8e65c5f93e76d18baaf4ffd287b3e46` |
| v2 ensemble B | `ml/runs/sed_polyphonic_20260926T053024Z/manifest.json` | dependency_manifest | có | `aa9128c39debdff72259d9cbfbae4d1bb19a4eacdb73ae6af1166a42bed6716c` |
| v2 ensemble B | `ml/runs/sed_polyphonic_20260926T064832Z/manifest.json` | dependency_manifest | có | `c90ae371d76dd8b11d4a249372f888dd84264bbaabd04d40e4acb76ab7ec2edf` |
| v2 ensemble B | `ml/runs/sed_polyphonic_20260926T033312Z/checkpoints/best.pt` | best_checkpoint | có | `4c340341c3bd788a42ea542e27c50dc9e2c1efcf09336fdd254d5e2956d52f8d` |
| v2 ensemble B | `ml/runs/sed_polyphonic_20260926T053024Z/checkpoints/best.pt` | best_checkpoint | có | `2c7fa6ade03840ba6a3f1a199c452aaca2ed16b5406273f643fdbb68db4f61d9` |
| v2 ensemble B | `ml/runs/sed_polyphonic_20260926T064832Z/checkpoints/best.pt` | best_checkpoint | có | `fbd9cf2ad81688a2df60c45da65012b78a63ef3a620e3f0adf96c6a07167f0dc` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/manifest.json` | run_manifest | có | `d4da4f19529a12813e95095c5ec75847397b2579e2af3bb02438448bc17207bb` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/predictions/dev.npz` | prediction | có | `e1b5a0f42dfd5c3eac8032fe6bb69ef0db3babad7c4c2e5a9fde1be20f61597b` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/postproc_cv.json` | postproc_or_sebb | có | `7398b397957754cef9ae7050d2c8fc228d88c10b4c187fbf153fe54a57e5c6b5` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `7398b397957754cef9ae7050d2c8fc228d88c10b4c187fbf153fe54a57e5c6b5` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/postproc_cv_selection.json` | postproc_or_sebb | có | `a060ce0b79cf830728e58a5595d7c60b397863da0a6ff17475b0723aee5f9394` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `f3e8fe2949538205284524508c800f7622eba65a3307a9c1230473395cab128c` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/sebb_cv_selection.json` | postproc_or_sebb | có | `8faeeeb6beced5cdc85e328d865af989aad1789884b6c7e336024ce8bd0dd88d` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `5c8e889b8218d0219b4ec5f35824a4974222de56601cd79519766060ed976452` |
| C-v2 ensemble | `ml/runs/sed_polyphonic_20260926T161726Z/manifest.json` | dependency_manifest | có | `6514ba94587324be01e1a65495fb874e0ca24c8eb21328378a2121f2ad5e8511` |
| C-v2 ensemble | `ml/runs/sed_polyphonic_20260926T172229Z/manifest.json` | dependency_manifest | có | `51873580e29e7ed7d8960296b453f54c2eeb691d565f8c7d01d06574d487a4ac` |
| C-v2 ensemble | `ml/runs/sed_polyphonic_20260926T185208Z/manifest.json` | dependency_manifest | có | `1c33b137448e62972e90eccaf8ec27a9067170bfe7ba17209e8a6795d10a36be` |
| C-v2 ensemble | `ml/runs/sed_polyphonic_20260926T161726Z/checkpoints/best.pt` | best_checkpoint | có | `dc357762d087ff6b8326163cdfc2785461c98f6e62e448f77badba241c04a20c` |
| C-v2 ensemble | `ml/runs/sed_polyphonic_20260926T172229Z/checkpoints/best.pt` | best_checkpoint | có | `cfdc656a8d119450a17a2e4176d9ae3b81f4d8b4b788bdfda672aabd6477e6d4` |
| C-v2 ensemble | `ml/runs/sed_polyphonic_20260926T185208Z/checkpoints/best.pt` | best_checkpoint | có | `6931b599931e128bdddb7058daf6e7b9be9ad73b6bf58ceb62e6d782c2057bc7` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/manifest.json` | run_manifest | có | `8d686d26d85741ab3aaf1b2c1d4672f1049cc427477018fe2ca0d4d19bde814a` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/predictions/dev.npz` | prediction | có | `5635f79f2a6bda6f1dc891bc7f2bdaeafcf866e32b550935880805c9ea618e4a` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/postproc_cv.json` | postproc_or_sebb | có | `8db423e54224d2c094252891979ecd7c91123db6aafe33ed3af035fe1b2e3c0c` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `8db423e54224d2c094252891979ecd7c91123db6aafe33ed3af035fe1b2e3c0c` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/postproc_cv_selection.json` | postproc_or_sebb | có | `ee049ad142e737344aced5293a56aac6ff4d813420f35e6e061a33b210124729` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `58c5afeacdd9af710ad8ae7ee9cefd98df23599da1fa4a2ca1327eeb1bcce050` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/sebb_cv_selection.json` | postproc_or_sebb | có | `38edef469384ff913fcc5d1fbabdb89d15f61d2cc0da5e1a0ff490694715c422` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `d95de8e5c452dbbb9ebc7dc601225f9a141c0b1f74098f5695868bbe48a7a046` |
| T2a ensemble | `ml/runs/sed_polyphonic_20260927T064341Z/manifest.json` | dependency_manifest | có | `395df376b5c3039e10b15bd1495533d7ab071f008848ec52027a007c3f05a621` |
| T2a ensemble | `ml/runs/sed_polyphonic_20260927T092605Z/manifest.json` | dependency_manifest | có | `ba22349d6eb8b9647308047e37dde8c884f419d900ed9a6391dd096b4b4a6cb5` |
| T2a ensemble | `ml/runs/sed_polyphonic_20260927T113910Z/manifest.json` | dependency_manifest | có | `d6727a90fc57d7bb8e66d33afc8f9dd73889396cb95e28d9071f6cf826005ea4` |
| T2a ensemble | `ml/runs/sed_polyphonic_20260927T064341Z/checkpoints/best.pt` | best_checkpoint | có | `f4190718826de3d5ad611a2ff617ce7517306962f73dd20235d8ab8392a385c5` |
| T2a ensemble | `ml/runs/sed_polyphonic_20260927T092605Z/checkpoints/best.pt` | best_checkpoint | có | `5f69972598923c33eed7ee0a0e04b32118d37514d331ace59dd6eb8512d3f1f2` |
| T2a ensemble | `ml/runs/sed_polyphonic_20260927T113910Z/checkpoints/best.pt` | best_checkpoint | có | `dbe017a7d24ddecf49fac8a4f1370c475b9ab4b90418024d8a1244df7595cc00` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/manifest.json` | run_manifest | có | `c21a71f64c32875e4bf7c0750ad762a24746dfa576ff6ec989dc9bc461c6cfdd` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/predictions/dev.npz` | prediction | có | `08b14a95edbda75585156e6c64ba86a73d4afd25371ec10c171482d2ee03bc2a` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/postproc_cv.json` | postproc_or_sebb | có | `6c2cdada49c2eaec48460b6b4d94dbf02ba3deabc0674746c1e08fadddaf11fd` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `6c2cdada49c2eaec48460b6b4d94dbf02ba3deabc0674746c1e08fadddaf11fd` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/postproc_cv_selection.json` | postproc_or_sebb | có | `7e8a2f16637c7188a4ba9ed513304e00b87f1802e10705fa9f6216ae235ceac3` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `d8def980349b0925c3c2e7b08412ac88dc46af65f2dbb31437d9028325e09053` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/sebb_cv_selection.json` | postproc_or_sebb | có | `9ee5bed95346f54a74b9cf047160b048923ae5f0f87870a9e2f3964fec5db8b8` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `7187bb30bd03c9d0096ef1679513080c4308fa9266721e0afed4bdb9e6c82ca0` |
| T2b ensemble (served f2 source) | `ml/runs/sed_polyphonic_20260927T172924Z/manifest.json` | dependency_manifest | có | `17388e20e2cc97b57e5ef693a2d627c57e814b9826a92c28b2ecc27077174160` |
| T2b ensemble (served f2 source) | `ml/runs/sed_polyphonic_20260927T180358Z/manifest.json` | dependency_manifest | có | `b7d793ae28c9a0cc2b89f981c194ea43621d2d20a8c9634c257de756b9a2e0ce` |
| T2b ensemble (served f2 source) | `ml/runs/sed_polyphonic_20260927T185137Z/manifest.json` | dependency_manifest | có | `30c6f4045ef5c38a3b3cd0d7a5ae9fb05f86279877e383e5fe862ed7ccfcbb3c` |
| T2b ensemble (served f2 source) | `ml/runs/sed_polyphonic_20260927T172924Z/checkpoints/best.pt` | best_checkpoint | có | `5090beb60bbd38ae00396506d0d64d910de66dec914ddbf92f1c2bcf39561a8d` |
| T2b ensemble (served f2 source) | `ml/runs/sed_polyphonic_20260927T180358Z/checkpoints/best.pt` | best_checkpoint | có | `787e15395f05ef52d219e190286cba35b3d79e8681f974fc87410b825133663d` |
| T2b ensemble (served f2 source) | `ml/runs/sed_polyphonic_20260927T185137Z/checkpoints/best.pt` | best_checkpoint | có | `6bfa01b3217387c36f508a7f46d87db391e30060748db680a3bed08662e3a44f` |
| Served B0 system (ADR-0042) | `ml/runs/sed_served_B0_20261107T175659Z/manifest.json` | run_manifest | có | `bfbd823207fb48d1b11575c77a36f765d4adf429b288979b905006bf9eb44c46` |
| Served B0 system (ADR-0042) | `ml/runs/sed_served_B0_20261107T175659Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `1610d24bc08a836896e60b8d2014225d80be2c77a083d1c5d4e0fb08d218cf10` |
| Served B0 system (ADR-0042) | `ml/runs/sed_polyphonic_20261008T092903Z/manifest.json` | dependency_manifest | có | `6154acde23ee7facb72b14bed6544d981cd5eca0d545587ca7241f228d10cee7` |
| Served B0 system (ADR-0042) | `ml/runs/sed_polyphonic_20261008T102530Z/manifest.json` | dependency_manifest | có | `53997a8bf3effdec70426a718c36a9e01d04d8912523744c5df6411d5c740e6f` |
| Served B0 system (ADR-0042) | `ml/runs/sed_polyphonic_20261008T111605Z/manifest.json` | dependency_manifest | có | `e70ff656db7ede7fbedf4c940fd1e5996487b4b9cef87f0264688d127a778b5e` |
| Served B0 system (ADR-0042) | `ml/runs/sed_polyphonic_20261008T115845Z/manifest.json` | dependency_manifest | có | `059e34a311fe0728e95c159819b51410bad9533e19a31a2f031c4c7e0a435089` |
| Served B0 system (ADR-0042) | `ml/runs/sed_polyphonic_20261008T123531Z/manifest.json` | dependency_manifest | có | `5cb5ae17ef3c5050494a042af4136d388a75066d5660f84036244b3046142183` |
| Served B0 system (ADR-0042) | `ml/runs/sed_polyphonic_20261008T092903Z/checkpoints/best.pt` | best_checkpoint | có | `b4117b20ec2db7a888f86d5dc7a6f7859d2b4e03f2ab75734f7e664c0bf04d08` |
| Served B0 system (ADR-0042) | `ml/runs/sed_polyphonic_20261008T102530Z/checkpoints/best.pt` | best_checkpoint | có | `13d49939c718dfbb5f4c9b6f9a54894ed2cf4a914147aac8c6a8a8322be8383b` |
| Served B0 system (ADR-0042) | `ml/runs/sed_polyphonic_20261008T111605Z/checkpoints/best.pt` | best_checkpoint | có | `fffead0ee1e0e142fbce0a562e4fb24bf7ee9b5bc47fbc67813f668d9e976e56` |
| Served B0 system (ADR-0042) | `ml/runs/sed_polyphonic_20261008T115845Z/checkpoints/best.pt` | best_checkpoint | có | `4f50d4fba9ce74bb0bb78e3bb26b6702f4aab805311e47af01e32ff959ae08bd` |
| Served B0 system (ADR-0042) | `ml/runs/sed_polyphonic_20261008T123531Z/checkpoints/best.pt` | best_checkpoint | có | `dc3f346fef30fe030dc6f361d5fafb352a0e58b23a3ed22277f69a0cb08be5f0` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/manifest.json` | run_manifest | có | `9e95f5a567f00d2e1d2cb0e98418031ebfd22c2a9895b1532a4d9277524f2e3f` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/predictions/test.npz` | prediction | có | `9e0a458f94c2f7ec2d17fb1865401527d8ccdb6da413d71026bef2846e8311f0` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_polyphonic_20261008T092903Z/manifest.json` | dependency_manifest | có | `6154acde23ee7facb72b14bed6544d981cd5eca0d545587ca7241f228d10cee7` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_polyphonic_20261008T102530Z/manifest.json` | dependency_manifest | có | `53997a8bf3effdec70426a718c36a9e01d04d8912523744c5df6411d5c740e6f` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_polyphonic_20261008T111605Z/manifest.json` | dependency_manifest | có | `e70ff656db7ede7fbedf4c940fd1e5996487b4b9cef87f0264688d127a778b5e` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_polyphonic_20261008T115845Z/manifest.json` | dependency_manifest | có | `059e34a311fe0728e95c159819b51410bad9533e19a31a2f031c4c7e0a435089` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_polyphonic_20261008T123531Z/manifest.json` | dependency_manifest | có | `5cb5ae17ef3c5050494a042af4136d388a75066d5660f84036244b3046142183` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_rewindow_B0_f0_h5_test_20261014T084758Z/manifest.json` | dependency_manifest | có | `802a2a8d91d09b2038156afa397f2809de2196524abebc3b59ed9245ef448f44` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_rewindow_B0_f1_h5_test_20261014T084829Z/manifest.json` | dependency_manifest | có | `798a60d02ad7841428a68faca58f2a836688e33234a665f52f2e3ddbde3b7456` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_rewindow_B0_f2_h5_test_20261014T084856Z/manifest.json` | dependency_manifest | có | `cc480cdf9ac4fdd9b16397cd6349ce6055ce2495b7342b51e7b25919ef08fc11` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_rewindow_B0_f3_h5_test_20261014T084923Z/manifest.json` | dependency_manifest | có | `c9f4ccf6f62fbfb599dafea4d984b92f02edbc053d5c698ca46a72532ef2787b` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_rewindow_B0_f4_h5_test_20261014T084950Z/manifest.json` | dependency_manifest | có | `0b2e41f949ab0ff954f8a93d3b4308f60865bda1e91713e52dfeadb234cd41bc` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_polyphonic_20261008T092903Z/checkpoints/best.pt` | best_checkpoint | có | `b4117b20ec2db7a888f86d5dc7a6f7859d2b4e03f2ab75734f7e664c0bf04d08` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_polyphonic_20261008T102530Z/checkpoints/best.pt` | best_checkpoint | có | `13d49939c718dfbb5f4c9b6f9a54894ed2cf4a914147aac8c6a8a8322be8383b` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_polyphonic_20261008T111605Z/checkpoints/best.pt` | best_checkpoint | có | `fffead0ee1e0e142fbce0a562e4fb24bf7ee9b5bc47fbc67813f668d9e976e56` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_polyphonic_20261008T115845Z/checkpoints/best.pt` | best_checkpoint | có | `4f50d4fba9ce74bb0bb78e3bb26b6702f4aab805311e47af01e32ff959ae08bd` |
| B0 final test ensemble (ADR-0041 §12) | `ml/runs/sed_polyphonic_20261008T123531Z/checkpoints/best.pt` | best_checkpoint | có | `dc3f346fef30fe030dc6f361d5fafb352a0e58b23a3ed22277f69a0cb08be5f0` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_oof_B0_h5_20261008T130849Z/manifest.json` | run_manifest | có | `bf4895001f012b2c2648fee80dbd6fc066bb375a8521378b0f441c6d8c60f0a5` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_oof_B0_h5_20261008T130849Z/predictions/dev.npz` | prediction | có | `3204c825eb1a435946d6a2436fb419979961cf86a6677be6abdda3a85dad049d` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_oof_B0_h5_20261008T130849Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `8a67286306e598bf9fae0b86c1b84b40cae1ac660544bd49ad91eaae9b958ab6` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_oof_B0_h5_20261008T130849Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `96bd2a449c875e46d2e87a692ec1f0fdbfc7eb4758976eea9dd4e9f14e48cbf2` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_oof_B0_h5_20261008T130849Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `1610d24bc08a836896e60b8d2014225d80be2c77a083d1c5d4e0fb08d218cf10` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_polyphonic_20261008T092903Z/manifest.json` | dependency_manifest | có | `6154acde23ee7facb72b14bed6544d981cd5eca0d545587ca7241f228d10cee7` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_polyphonic_20261008T102530Z/manifest.json` | dependency_manifest | có | `53997a8bf3effdec70426a718c36a9e01d04d8912523744c5df6411d5c740e6f` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_polyphonic_20261008T111605Z/manifest.json` | dependency_manifest | có | `e70ff656db7ede7fbedf4c940fd1e5996487b4b9cef87f0264688d127a778b5e` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_polyphonic_20261008T115845Z/manifest.json` | dependency_manifest | có | `059e34a311fe0728e95c159819b51410bad9533e19a31a2f031c4c7e0a435089` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_polyphonic_20261008T123531Z/manifest.json` | dependency_manifest | có | `5cb5ae17ef3c5050494a042af4136d388a75066d5660f84036244b3046142183` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_rewindow_B0_f0_h5_20261008T130621Z/manifest.json` | dependency_manifest | có | `6bbb1155de7183032bc1b89989b7491c9976ad54a4ed44b8eb003750de5bbb19` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_rewindow_B0_f1_h5_20261008T130644Z/manifest.json` | dependency_manifest | có | `ee84e01477fa15f32a5c6a313b9a66b5632d1b1ab6326aeea847eef9d234b952` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_rewindow_B0_f2_h5_20261008T130708Z/manifest.json` | dependency_manifest | có | `6ced2d2071e599ac6c2cfa6f2b18a9d904c8a2a7d88ce1fb85e844c8f7482ffd` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_rewindow_B0_f3_h5_20261008T130733Z/manifest.json` | dependency_manifest | có | `c5eb38569d93ab32271169c3843c40d5feb350b47b68a526c333943915e77650` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_rewindow_B0_f4_h5_20261008T130755Z/manifest.json` | dependency_manifest | có | `38e0ce4db58e9657c888cb42f77de495920f3a999c877db2754ad5ea1da45f68` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_polyphonic_20261008T092903Z/checkpoints/best.pt` | best_checkpoint | có | `b4117b20ec2db7a888f86d5dc7a6f7859d2b4e03f2ab75734f7e664c0bf04d08` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_polyphonic_20261008T102530Z/checkpoints/best.pt` | best_checkpoint | có | `13d49939c718dfbb5f4c9b6f9a54894ed2cf4a914147aac8c6a8a8322be8383b` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_polyphonic_20261008T111605Z/checkpoints/best.pt` | best_checkpoint | có | `fffead0ee1e0e142fbce0a562e4fb24bf7ee9b5bc47fbc67813f668d9e976e56` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_polyphonic_20261008T115845Z/checkpoints/best.pt` | best_checkpoint | có | `4f50d4fba9ce74bb0bb78e3bb26b6702f4aab805311e47af01e32ff959ae08bd` |
| B0 OOF h5 (ADR-0041 §11, postproc source) | `ml/runs/sed_polyphonic_20261008T123531Z/checkpoints/best.pt` | best_checkpoint | có | `dc3f346fef30fe030dc6f361d5fafb352a0e58b23a3ed22277f69a0cb08be5f0` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_filtered_B0_oof_dev_20261107T181008Z/manifest.json` | run_manifest | có | `8c04ce2caff2983e86d8c432632ea4d19bdc282afc26e294f5b3dff99f356f92` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_filtered_B0_oof_dev_20261107T181008Z/predictions/dev.npz` | prediction | có | `3ba7fc3776f14c4b60436503354e6196576678167cae7583620b3a3485872b45` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_filtered_B0_oof_dev_20261107T181008Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `1610d24bc08a836896e60b8d2014225d80be2c77a083d1c5d4e0fb08d218cf10` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_oof_B0_h5_20261008T130849Z/manifest.json` | dependency_manifest | có | `bf4895001f012b2c2648fee80dbd6fc066bb375a8521378b0f441c6d8c60f0a5` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_polyphonic_20261008T092903Z/manifest.json` | dependency_manifest | có | `6154acde23ee7facb72b14bed6544d981cd5eca0d545587ca7241f228d10cee7` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_polyphonic_20261008T102530Z/manifest.json` | dependency_manifest | có | `53997a8bf3effdec70426a718c36a9e01d04d8912523744c5df6411d5c740e6f` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_polyphonic_20261008T111605Z/manifest.json` | dependency_manifest | có | `e70ff656db7ede7fbedf4c940fd1e5996487b4b9cef87f0264688d127a778b5e` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_polyphonic_20261008T115845Z/manifest.json` | dependency_manifest | có | `059e34a311fe0728e95c159819b51410bad9533e19a31a2f031c4c7e0a435089` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_polyphonic_20261008T123531Z/manifest.json` | dependency_manifest | có | `5cb5ae17ef3c5050494a042af4136d388a75066d5660f84036244b3046142183` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_rewindow_B0_f0_h5_20261008T130621Z/manifest.json` | dependency_manifest | có | `6bbb1155de7183032bc1b89989b7491c9976ad54a4ed44b8eb003750de5bbb19` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_rewindow_B0_f1_h5_20261008T130644Z/manifest.json` | dependency_manifest | có | `ee84e01477fa15f32a5c6a313b9a66b5632d1b1ab6326aeea847eef9d234b952` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_rewindow_B0_f2_h5_20261008T130708Z/manifest.json` | dependency_manifest | có | `6ced2d2071e599ac6c2cfa6f2b18a9d904c8a2a7d88ce1fb85e844c8f7482ffd` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_rewindow_B0_f3_h5_20261008T130733Z/manifest.json` | dependency_manifest | có | `c5eb38569d93ab32271169c3843c40d5feb350b47b68a526c333943915e77650` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_rewindow_B0_f4_h5_20261008T130755Z/manifest.json` | dependency_manifest | có | `38e0ce4db58e9657c888cb42f77de495920f3a999c877db2754ad5ea1da45f68` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_polyphonic_20261008T092903Z/checkpoints/best.pt` | best_checkpoint | có | `b4117b20ec2db7a888f86d5dc7a6f7859d2b4e03f2ab75734f7e664c0bf04d08` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_polyphonic_20261008T102530Z/checkpoints/best.pt` | best_checkpoint | có | `13d49939c718dfbb5f4c9b6f9a54894ed2cf4a914147aac8c6a8a8322be8383b` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_polyphonic_20261008T111605Z/checkpoints/best.pt` | best_checkpoint | có | `fffead0ee1e0e142fbce0a562e4fb24bf7ee9b5bc47fbc67813f668d9e976e56` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_polyphonic_20261008T115845Z/checkpoints/best.pt` | best_checkpoint | có | `4f50d4fba9ce74bb0bb78e3bb26b6702f4aab805311e47af01e32ff959ae08bd` |
| B0 OOF dev corpus (ADR-0044) | `ml/runs/sed_polyphonic_20261008T123531Z/checkpoints/best.pt` | best_checkpoint | có | `dc3f346fef30fe030dc6f361d5fafb352a0e58b23a3ed22277f69a0cb08be5f0` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/manifest.json` | run_manifest | có | `c888a447e76ca6a2ecbfdfa5a33f93fe32c1020a33ae7d01567aed8a7f60f316` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/predictions/dev.npz` | prediction | có | `5dc73d082d11b8be4b40bd56a5b6b74d552998733ba42b0adef8b04af7de2ba2` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/postproc_cv.json` | postproc_or_sebb | có | `5ad788b03837e9d9f7553e81c5a8e37363eb0faf6b4d094c654f09a72847a0d2` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `5ad788b03837e9d9f7553e81c5a8e37363eb0faf6b4d094c654f09a72847a0d2` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/postproc_cv_selection.json` | postproc_or_sebb | có | `aa2c4ea695b494f96ba33538c15142a0f93d57278519f2fdae4dcb414c4567ba` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `299295b6637f146d224fac7df2c97a9b4b1c0a18fbabdbdf930db1c3910c7f78` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/sebb_cv_selection.json` | postproc_or_sebb | có | `754ac73ce6bfae7c0b6d82eaa337c261e3bf094b75c0b453d913a9bf089ba87b` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `1826ae546cbba285ca3f9d4061c06ae9e0f416e38037466432e6c3a251b39e1d` |
| S11 focal ensemble | `ml/runs/sed_polyphonic_20260928T165635Z/manifest.json` | dependency_manifest | có | `9f73e68c254d3f40275f4f35622e49cea5f0707a26b4d66e328841649fb79ac4` |
| S11 focal ensemble | `ml/runs/sed_polyphonic_20260928T173526Z/manifest.json` | dependency_manifest | có | `ff089e7aec7f1eb38565ed8834a9f45132f20b05e6e80c13dbea6452b4830fae` |
| S11 focal ensemble | `ml/runs/sed_polyphonic_20260928T181509Z/manifest.json` | dependency_manifest | có | `b431788b98ae40d4c9b3851e06a2fb3ac1b88ddca69b0d2fa7dce9477ef513c3` |
| S11 focal ensemble | `ml/runs/sed_polyphonic_20260928T165635Z/checkpoints/best.pt` | best_checkpoint | có | `e91cef7d466520c42456d707fbb387ca7267b94ac895f5e0529db1cb473e7654` |
| S11 focal ensemble | `ml/runs/sed_polyphonic_20260928T173526Z/checkpoints/best.pt` | best_checkpoint | có | `fea868afd66177743fb7545584f4ff5a6f5d279b39d27c161ebe10f230531388` |
| S11 focal ensemble | `ml/runs/sed_polyphonic_20260928T181509Z/checkpoints/best.pt` | best_checkpoint | có | `65b70c55516cc3cafe4c1833486417214aee1313a29aea3ff3415edf3a26d846` |
| S13 f2 test output | `ml/runs/sed_ensemble_s13_f2_20260929T045053Z/manifest.json` | run_manifest | có | `6e47cd6a272c972861db9078f74fcb53a4a82b0a7e064ed7259bac5cce1529fd` |
| S13 f2 test output | `ml/runs/sed_ensemble_s13_f2_20260929T045053Z/predictions/test.npz` | prediction | có | `86b4287d881b515020253d7e0880ecf61f0b39e1fd737bfe3a71243ae1af5dac` |
| S13 f2 test output | `ml/runs/sed_polyphonic_20260927T172924Z/manifest.json` | dependency_manifest | có | `17388e20e2cc97b57e5ef693a2d627c57e814b9826a92c28b2ecc27077174160` |
| S13 f2 test output | `ml/runs/sed_polyphonic_20260927T180358Z/manifest.json` | dependency_manifest | có | `b7d793ae28c9a0cc2b89f981c194ea43621d2d20a8c9634c257de756b9a2e0ce` |
| S13 f2 test output | `ml/runs/sed_polyphonic_20260927T185137Z/manifest.json` | dependency_manifest | có | `30c6f4045ef5c38a3b3cd0d7a5ae9fb05f86279877e383e5fe862ed7ccfcbb3c` |
| S13 f2 test output | `ml/runs/sed_polyphonic_20260927T172924Z/checkpoints/best.pt` | best_checkpoint | có | `5090beb60bbd38ae00396506d0d64d910de66dec914ddbf92f1c2bcf39561a8d` |
| S13 f2 test output | `ml/runs/sed_polyphonic_20260927T180358Z/checkpoints/best.pt` | best_checkpoint | có | `787e15395f05ef52d219e190286cba35b3d79e8681f974fc87410b825133663d` |
| S13 f2 test output | `ml/runs/sed_polyphonic_20260927T185137Z/checkpoints/best.pt` | best_checkpoint | có | `6bfa01b3217387c36f508a7f46d87db391e30060748db680a3bed08662e3a44f` |
| phase O: pseudo_datasec_s_20261013T221755Z | `ml/runs/pseudo_datasec_s_20261013T221755Z/manifest.json` | run_manifest | có | `9d5a6196a9f725d20b2735ee227e08b7d61e15c19fb540afb903d12bfc1c418b` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/manifest.json` | run_manifest | có | `9e95f5a567f00d2e1d2cb0e98418031ebfd22c2a9895b1532a4d9277524f2e3f` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_ensemble_B0_final_test_20261014T085016Z/predictions/test.npz` | prediction | có | `9e0a458f94c2f7ec2d17fb1865401527d8ccdb6da413d71026bef2846e8311f0` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_polyphonic_20261008T092903Z/manifest.json` | dependency_manifest | có | `6154acde23ee7facb72b14bed6544d981cd5eca0d545587ca7241f228d10cee7` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_polyphonic_20261008T102530Z/manifest.json` | dependency_manifest | có | `53997a8bf3effdec70426a718c36a9e01d04d8912523744c5df6411d5c740e6f` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_polyphonic_20261008T111605Z/manifest.json` | dependency_manifest | có | `e70ff656db7ede7fbedf4c940fd1e5996487b4b9cef87f0264688d127a778b5e` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_polyphonic_20261008T115845Z/manifest.json` | dependency_manifest | có | `059e34a311fe0728e95c159819b51410bad9533e19a31a2f031c4c7e0a435089` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_polyphonic_20261008T123531Z/manifest.json` | dependency_manifest | có | `5cb5ae17ef3c5050494a042af4136d388a75066d5660f84036244b3046142183` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_rewindow_B0_f0_h5_test_20261014T084758Z/manifest.json` | dependency_manifest | có | `802a2a8d91d09b2038156afa397f2809de2196524abebc3b59ed9245ef448f44` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_rewindow_B0_f1_h5_test_20261014T084829Z/manifest.json` | dependency_manifest | có | `798a60d02ad7841428a68faca58f2a836688e33234a665f52f2e3ddbde3b7456` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_rewindow_B0_f2_h5_test_20261014T084856Z/manifest.json` | dependency_manifest | có | `cc480cdf9ac4fdd9b16397cd6349ce6055ce2495b7342b51e7b25919ef08fc11` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_rewindow_B0_f3_h5_test_20261014T084923Z/manifest.json` | dependency_manifest | có | `c9f4ccf6f62fbfb599dafea4d984b92f02edbc053d5c698ca46a72532ef2787b` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_rewindow_B0_f4_h5_test_20261014T084950Z/manifest.json` | dependency_manifest | có | `0b2e41f949ab0ff954f8a93d3b4308f60865bda1e91713e52dfeadb234cd41bc` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_polyphonic_20261008T092903Z/checkpoints/best.pt` | best_checkpoint | có | `b4117b20ec2db7a888f86d5dc7a6f7859d2b4e03f2ab75734f7e664c0bf04d08` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_polyphonic_20261008T102530Z/checkpoints/best.pt` | best_checkpoint | có | `13d49939c718dfbb5f4c9b6f9a54894ed2cf4a914147aac8c6a8a8322be8383b` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_polyphonic_20261008T111605Z/checkpoints/best.pt` | best_checkpoint | có | `fffead0ee1e0e142fbce0a562e4fb24bf7ee9b5bc47fbc67813f668d9e976e56` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_polyphonic_20261008T115845Z/checkpoints/best.pt` | best_checkpoint | có | `4f50d4fba9ce74bb0bb78e3bb26b6702f4aab805311e47af01e32ff959ae08bd` |
| phase O: sed_ensemble_B0_final_test_20261014T085016Z | `ml/runs/sed_polyphonic_20261008T123531Z/checkpoints/best.pt` | best_checkpoint | có | `dc3f346fef30fe030dc6f361d5fafb352a0e58b23a3ed22277f69a0cb08be5f0` |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `ml/runs/sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z/manifest.json` | run_manifest | có | `1d9a005c0a64b2f077465d9cf9dca9435cd402f326ceb1d6fd6dddcf2579d49a` |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `ml/runs/sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z/predictions/dev.npz` | prediction | có | `7b704544e65c3c3980ea7ab980e151e91ca7745ba68ada3d58a258fb0bb0cf82` |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `ml/runs/sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `28a8ede064bd16dc964e14fd5176de298c630e5b67eff46a3a852d1da27c3ec7` |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `ml/runs/sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `71e8885ee9973a1b9e31045c367d594eae05ae34c0a5bf17c018789c9680bbd9` |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `ml/runs/sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `3acdb605b8a1befbc57009589ed3e6b239d39d4fec5a1c5c4f076c38e8944c0a` |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `ml/runs/sed_polyphonic_20260927T172924Z/manifest.json` | dependency_manifest | có | `17388e20e2cc97b57e5ef693a2d627c57e814b9826a92c28b2ecc27077174160` |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `ml/runs/sed_polyphonic_20260927T180358Z/manifest.json` | dependency_manifest | có | `b7d793ae28c9a0cc2b89f981c194ea43621d2d20a8c9634c257de756b9a2e0ce` |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `ml/runs/sed_polyphonic_20260927T185137Z/manifest.json` | dependency_manifest | có | `30c6f4045ef5c38a3b3cd0d7a5ae9fb05f86279877e383e5fe862ed7ccfcbb3c` |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `ml/runs/sed_rewindow_f2_h2.5_triangular0.3_m1_20261008T060426Z/manifest.json` | dependency_manifest | có | `2b9c8b71dd85884ea031e9a0c736c1fcb8ac39d1717c432f39decacc5c0df6a9` |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `ml/runs/sed_rewindow_f2_h2.5_triangular0.3_m2_20261008T060530Z/manifest.json` | dependency_manifest | có | `dc86815e48f270570650fddbb81b1a9a968f130167d7f3722b7194ad0018f345` |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `ml/runs/sed_rewindow_f2_h2.5_triangular0.3_m3_20261008T060629Z/manifest.json` | dependency_manifest | có | `310789331e51b681b84d084984d93672fc948c1bf816701bc94936d66f4ac18a` |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `ml/runs/sed_polyphonic_20260927T172924Z/checkpoints/best.pt` | best_checkpoint | có | `5090beb60bbd38ae00396506d0d64d910de66dec914ddbf92f1c2bcf39561a8d` |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `ml/runs/sed_polyphonic_20260927T180358Z/checkpoints/best.pt` | best_checkpoint | có | `787e15395f05ef52d219e190286cba35b3d79e8681f974fc87410b825133663d` |
| phase O: sed_ensemble_f2_h2.5_triangular0.3_20261008T060746Z | `ml/runs/sed_polyphonic_20260927T185137Z/checkpoints/best.pt` | best_checkpoint | có | `6bfa01b3217387c36f508a7f46d87db391e30060748db680a3bed08662e3a44f` |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `ml/runs/sed_ensemble_f2_h2.5_uniform_20261008T074349Z/manifest.json` | run_manifest | có | `5858f73e69dd37a2526f6a11db9cbc27487d5187bc148be859335bbe715f0f49` |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `ml/runs/sed_ensemble_f2_h2.5_uniform_20261008T074349Z/predictions/dev.npz` | prediction | có | `9c1aab3a5df7a9243f952b6a3dd391a3509c7a6652ce5e00ce47aa2eee667faa` |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `ml/runs/sed_ensemble_f2_h2.5_uniform_20261008T074349Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `6fddff290ae798c300566d82d2528e0befdd5e280e3d241f9c45d620cee5422d` |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `ml/runs/sed_ensemble_f2_h2.5_uniform_20261008T074349Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `7c64c21c2bcf2679df5184f18c04716e19433d96283d1a041e26ba01d17d2d66` |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `ml/runs/sed_ensemble_f2_h2.5_uniform_20261008T074349Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `3d08fdb93f097b115df2e39ad8e65d10ed03a4b27061e831f367936b150e1131` |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `ml/runs/sed_polyphonic_20260927T172924Z/manifest.json` | dependency_manifest | có | `17388e20e2cc97b57e5ef693a2d627c57e814b9826a92c28b2ecc27077174160` |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `ml/runs/sed_polyphonic_20260927T180358Z/manifest.json` | dependency_manifest | có | `b7d793ae28c9a0cc2b89f981c194ea43621d2d20a8c9634c257de756b9a2e0ce` |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `ml/runs/sed_polyphonic_20260927T185137Z/manifest.json` | dependency_manifest | có | `30c6f4045ef5c38a3b3cd0d7a5ae9fb05f86279877e383e5fe862ed7ccfcbb3c` |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `ml/runs/sed_rewindow_f2_h2.5_uniform_m1_20261008T073910Z/manifest.json` | dependency_manifest | có | `dc06c8dd42edd2e40cbab94464c3dfdba0a307e73e5788e1ce0ed1dc96d3730e` |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `ml/runs/sed_rewindow_f2_h2.5_uniform_m2_20261008T074045Z/manifest.json` | dependency_manifest | có | `cdffd0c1a12b353b26a256609299f60c1a701f47bc957746edfbf869c65a5433` |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `ml/runs/sed_rewindow_f2_h2.5_uniform_m3_20261008T074220Z/manifest.json` | dependency_manifest | có | `46e020e6b688eb3291dd7c6863dd49a278b35e23e9a263224fad8887e1fa29ad` |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `ml/runs/sed_polyphonic_20260927T172924Z/checkpoints/best.pt` | best_checkpoint | có | `5090beb60bbd38ae00396506d0d64d910de66dec914ddbf92f1c2bcf39561a8d` |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `ml/runs/sed_polyphonic_20260927T180358Z/checkpoints/best.pt` | best_checkpoint | có | `787e15395f05ef52d219e190286cba35b3d79e8681f974fc87410b825133663d` |
| phase O: sed_ensemble_f2_h2.5_uniform_20261008T074349Z | `ml/runs/sed_polyphonic_20260927T185137Z/checkpoints/best.pt` | best_checkpoint | có | `6bfa01b3217387c36f508a7f46d87db391e30060748db680a3bed08662e3a44f` |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `ml/runs/sed_ensemble_f2_h5_triangular0.3_20261008T064740Z/manifest.json` | run_manifest | có | `6edbe1bb28011fa5c53d4586151a7445f04b6806b52ef10cd6264454f7766089` |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `ml/runs/sed_ensemble_f2_h5_triangular0.3_20261008T064740Z/predictions/dev.npz` | prediction | có | `02d233154f3390b56cf0e723f6fb16fa656c842f0f8bf2dfdc94bc7ba1e198ce` |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `ml/runs/sed_ensemble_f2_h5_triangular0.3_20261008T064740Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `4dbd0e0e80701a11984eec24daf9bbb4322a298df37fceb2ad60e4abbf533309` |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `ml/runs/sed_ensemble_f2_h5_triangular0.3_20261008T064740Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `3a41700655c62ed5b5aeac2089e604a37c7c435e172a994cc237548a8e071982` |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `ml/runs/sed_ensemble_f2_h5_triangular0.3_20261008T064740Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `5e9020f558849ece824ffb72ca098324479ea4504f503c77f12830ef2c3619df` |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `ml/runs/sed_polyphonic_20260927T172924Z/manifest.json` | dependency_manifest | có | `17388e20e2cc97b57e5ef693a2d627c57e814b9826a92c28b2ecc27077174160` |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `ml/runs/sed_polyphonic_20260927T180358Z/manifest.json` | dependency_manifest | có | `b7d793ae28c9a0cc2b89f981c194ea43621d2d20a8c9634c257de756b9a2e0ce` |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `ml/runs/sed_polyphonic_20260927T185137Z/manifest.json` | dependency_manifest | có | `30c6f4045ef5c38a3b3cd0d7a5ae9fb05f86279877e383e5fe862ed7ccfcbb3c` |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `ml/runs/sed_rewindow_f2_h5_triangular0.3_m1_20261008T064524Z/manifest.json` | dependency_manifest | có | `879ace02e3532640e8a75ad93f0db862f62a6f0d0d6219c6d5a93a6401ffb45c` |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `ml/runs/sed_rewindow_f2_h5_triangular0.3_m2_20261008T064611Z/manifest.json` | dependency_manifest | có | `009af4430b9cf4943b9610c58e188ba8fd0438a75819ddd4c1ba4213b40b4015` |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `ml/runs/sed_rewindow_f2_h5_triangular0.3_m3_20261008T064653Z/manifest.json` | dependency_manifest | có | `a3d4500105bf03af5c6720c46dc47de42ab4059e7b7547e7f28687050228b4ba` |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `ml/runs/sed_polyphonic_20260927T172924Z/checkpoints/best.pt` | best_checkpoint | có | `5090beb60bbd38ae00396506d0d64d910de66dec914ddbf92f1c2bcf39561a8d` |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `ml/runs/sed_polyphonic_20260927T180358Z/checkpoints/best.pt` | best_checkpoint | có | `787e15395f05ef52d219e190286cba35b3d79e8681f974fc87410b825133663d` |
| phase O: sed_ensemble_f2_h5_triangular0.3_20261008T064740Z | `ml/runs/sed_polyphonic_20260927T185137Z/checkpoints/best.pt` | best_checkpoint | có | `6bfa01b3217387c36f508a7f46d87db391e30060748db680a3bed08662e3a44f` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_filtered_B0_oof_dev_20261107T181008Z/manifest.json` | run_manifest | có | `8c04ce2caff2983e86d8c432632ea4d19bdc282afc26e294f5b3dff99f356f92` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_filtered_B0_oof_dev_20261107T181008Z/predictions/dev.npz` | prediction | có | `3ba7fc3776f14c4b60436503354e6196576678167cae7583620b3a3485872b45` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_filtered_B0_oof_dev_20261107T181008Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `1610d24bc08a836896e60b8d2014225d80be2c77a083d1c5d4e0fb08d218cf10` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_oof_B0_h5_20261008T130849Z/manifest.json` | dependency_manifest | có | `bf4895001f012b2c2648fee80dbd6fc066bb375a8521378b0f441c6d8c60f0a5` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_polyphonic_20261008T092903Z/manifest.json` | dependency_manifest | có | `6154acde23ee7facb72b14bed6544d981cd5eca0d545587ca7241f228d10cee7` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_polyphonic_20261008T102530Z/manifest.json` | dependency_manifest | có | `53997a8bf3effdec70426a718c36a9e01d04d8912523744c5df6411d5c740e6f` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_polyphonic_20261008T111605Z/manifest.json` | dependency_manifest | có | `e70ff656db7ede7fbedf4c940fd1e5996487b4b9cef87f0264688d127a778b5e` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_polyphonic_20261008T115845Z/manifest.json` | dependency_manifest | có | `059e34a311fe0728e95c159819b51410bad9533e19a31a2f031c4c7e0a435089` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_polyphonic_20261008T123531Z/manifest.json` | dependency_manifest | có | `5cb5ae17ef3c5050494a042af4136d388a75066d5660f84036244b3046142183` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_rewindow_B0_f0_h5_20261008T130621Z/manifest.json` | dependency_manifest | có | `6bbb1155de7183032bc1b89989b7491c9976ad54a4ed44b8eb003750de5bbb19` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_rewindow_B0_f1_h5_20261008T130644Z/manifest.json` | dependency_manifest | có | `ee84e01477fa15f32a5c6a313b9a66b5632d1b1ab6326aeea847eef9d234b952` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_rewindow_B0_f2_h5_20261008T130708Z/manifest.json` | dependency_manifest | có | `6ced2d2071e599ac6c2cfa6f2b18a9d904c8a2a7d88ce1fb85e844c8f7482ffd` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_rewindow_B0_f3_h5_20261008T130733Z/manifest.json` | dependency_manifest | có | `c5eb38569d93ab32271169c3843c40d5feb350b47b68a526c333943915e77650` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_rewindow_B0_f4_h5_20261008T130755Z/manifest.json` | dependency_manifest | có | `38e0ce4db58e9657c888cb42f77de495920f3a999c877db2754ad5ea1da45f68` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_polyphonic_20261008T092903Z/checkpoints/best.pt` | best_checkpoint | có | `b4117b20ec2db7a888f86d5dc7a6f7859d2b4e03f2ab75734f7e664c0bf04d08` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_polyphonic_20261008T102530Z/checkpoints/best.pt` | best_checkpoint | có | `13d49939c718dfbb5f4c9b6f9a54894ed2cf4a914147aac8c6a8a8322be8383b` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_polyphonic_20261008T111605Z/checkpoints/best.pt` | best_checkpoint | có | `fffead0ee1e0e142fbce0a562e4fb24bf7ee9b5bc47fbc67813f668d9e976e56` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_polyphonic_20261008T115845Z/checkpoints/best.pt` | best_checkpoint | có | `4f50d4fba9ce74bb0bb78e3bb26b6702f4aab805311e47af01e32ff959ae08bd` |
| phase O: sed_filtered_B0_oof_dev_20261107T181008Z | `ml/runs/sed_polyphonic_20261008T123531Z/checkpoints/best.pt` | best_checkpoint | có | `dc3f346fef30fe030dc6f361d5fafb352a0e58b23a3ed22277f69a0cb08be5f0` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_oof_B0_h10_20261008T130820Z/manifest.json` | run_manifest | có | `ba83ce5789af6ffe3eae2e218b9e045cc19040750db65e1c8ea8d98fd7e86962` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_oof_B0_h10_20261008T130820Z/predictions/dev.npz` | prediction | có | `ce3bd6b656cc8c4c393c371cf78d9df49c02d55c8943e6dff28c3919cf5d78a8` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_oof_B0_h10_20261008T130820Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `00f4d1bedb7d6419251ca540caca817ad89de01513bcbd2279a6da9f00ae171e` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_oof_B0_h10_20261008T130820Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `376fb56659967b3c7c1ccf1b1813a66312699690ad7e2b82f00dee5d4cc4cd8f` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_oof_B0_h10_20261008T130820Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `75b1d633a1d1368337d0d5b7d787176ae6bf5eeff6bf8ca35789f861ecbe8716` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_polyphonic_20261008T092903Z/manifest.json` | dependency_manifest | có | `6154acde23ee7facb72b14bed6544d981cd5eca0d545587ca7241f228d10cee7` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_polyphonic_20261008T102530Z/manifest.json` | dependency_manifest | có | `53997a8bf3effdec70426a718c36a9e01d04d8912523744c5df6411d5c740e6f` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_polyphonic_20261008T111605Z/manifest.json` | dependency_manifest | có | `e70ff656db7ede7fbedf4c940fd1e5996487b4b9cef87f0264688d127a778b5e` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_polyphonic_20261008T115845Z/manifest.json` | dependency_manifest | có | `059e34a311fe0728e95c159819b51410bad9533e19a31a2f031c4c7e0a435089` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_polyphonic_20261008T123531Z/manifest.json` | dependency_manifest | có | `5cb5ae17ef3c5050494a042af4136d388a75066d5660f84036244b3046142183` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_polyphonic_20261008T092903Z/checkpoints/best.pt` | best_checkpoint | có | `b4117b20ec2db7a888f86d5dc7a6f7859d2b4e03f2ab75734f7e664c0bf04d08` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_polyphonic_20261008T102530Z/checkpoints/best.pt` | best_checkpoint | có | `13d49939c718dfbb5f4c9b6f9a54894ed2cf4a914147aac8c6a8a8322be8383b` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_polyphonic_20261008T111605Z/checkpoints/best.pt` | best_checkpoint | có | `fffead0ee1e0e142fbce0a562e4fb24bf7ee9b5bc47fbc67813f668d9e976e56` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_polyphonic_20261008T115845Z/checkpoints/best.pt` | best_checkpoint | có | `4f50d4fba9ce74bb0bb78e3bb26b6702f4aab805311e47af01e32ff959ae08bd` |
| phase O: sed_oof_B0_h10_20261008T130820Z | `ml/runs/sed_polyphonic_20261008T123531Z/checkpoints/best.pt` | best_checkpoint | có | `dc3f346fef30fe030dc6f361d5fafb352a0e58b23a3ed22277f69a0cb08be5f0` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_oof_B0_h5_20261008T130849Z/manifest.json` | run_manifest | có | `bf4895001f012b2c2648fee80dbd6fc066bb375a8521378b0f441c6d8c60f0a5` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_oof_B0_h5_20261008T130849Z/predictions/dev.npz` | prediction | có | `3204c825eb1a435946d6a2436fb419979961cf86a6677be6abdda3a85dad049d` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_oof_B0_h5_20261008T130849Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `8a67286306e598bf9fae0b86c1b84b40cae1ac660544bd49ad91eaae9b958ab6` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_oof_B0_h5_20261008T130849Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `96bd2a449c875e46d2e87a692ec1f0fdbfc7eb4758976eea9dd4e9f14e48cbf2` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_oof_B0_h5_20261008T130849Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `1610d24bc08a836896e60b8d2014225d80be2c77a083d1c5d4e0fb08d218cf10` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_polyphonic_20261008T092903Z/manifest.json` | dependency_manifest | có | `6154acde23ee7facb72b14bed6544d981cd5eca0d545587ca7241f228d10cee7` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_polyphonic_20261008T102530Z/manifest.json` | dependency_manifest | có | `53997a8bf3effdec70426a718c36a9e01d04d8912523744c5df6411d5c740e6f` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_polyphonic_20261008T111605Z/manifest.json` | dependency_manifest | có | `e70ff656db7ede7fbedf4c940fd1e5996487b4b9cef87f0264688d127a778b5e` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_polyphonic_20261008T115845Z/manifest.json` | dependency_manifest | có | `059e34a311fe0728e95c159819b51410bad9533e19a31a2f031c4c7e0a435089` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_polyphonic_20261008T123531Z/manifest.json` | dependency_manifest | có | `5cb5ae17ef3c5050494a042af4136d388a75066d5660f84036244b3046142183` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_rewindow_B0_f0_h5_20261008T130621Z/manifest.json` | dependency_manifest | có | `6bbb1155de7183032bc1b89989b7491c9976ad54a4ed44b8eb003750de5bbb19` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_rewindow_B0_f1_h5_20261008T130644Z/manifest.json` | dependency_manifest | có | `ee84e01477fa15f32a5c6a313b9a66b5632d1b1ab6326aeea847eef9d234b952` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_rewindow_B0_f2_h5_20261008T130708Z/manifest.json` | dependency_manifest | có | `6ced2d2071e599ac6c2cfa6f2b18a9d904c8a2a7d88ce1fb85e844c8f7482ffd` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_rewindow_B0_f3_h5_20261008T130733Z/manifest.json` | dependency_manifest | có | `c5eb38569d93ab32271169c3843c40d5feb350b47b68a526c333943915e77650` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_rewindow_B0_f4_h5_20261008T130755Z/manifest.json` | dependency_manifest | có | `38e0ce4db58e9657c888cb42f77de495920f3a999c877db2754ad5ea1da45f68` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_polyphonic_20261008T092903Z/checkpoints/best.pt` | best_checkpoint | có | `b4117b20ec2db7a888f86d5dc7a6f7859d2b4e03f2ab75734f7e664c0bf04d08` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_polyphonic_20261008T102530Z/checkpoints/best.pt` | best_checkpoint | có | `13d49939c718dfbb5f4c9b6f9a54894ed2cf4a914147aac8c6a8a8322be8383b` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_polyphonic_20261008T111605Z/checkpoints/best.pt` | best_checkpoint | có | `fffead0ee1e0e142fbce0a562e4fb24bf7ee9b5bc47fbc67813f668d9e976e56` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_polyphonic_20261008T115845Z/checkpoints/best.pt` | best_checkpoint | có | `4f50d4fba9ce74bb0bb78e3bb26b6702f4aab805311e47af01e32ff959ae08bd` |
| phase O: sed_oof_B0_h5_20261008T130849Z | `ml/runs/sed_polyphonic_20261008T123531Z/checkpoints/best.pt` | best_checkpoint | có | `dc3f346fef30fe030dc6f361d5fafb352a0e58b23a3ed22277f69a0cb08be5f0` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_oof_ENS_B0_OD_h5_20261013T221030Z/manifest.json` | run_manifest | có | `0e42b40713c5a7cddf8058ecd3280982f479d616d0a6d6cbc31c4e22e86fec66` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_oof_ENS_B0_OD_h5_20261013T221030Z/predictions/dev.npz` | prediction | có | `5bc22cdb1be9a88296e93cbfb9d0f1dd8fe15918a81a7e8a47acf9dbb5bb9905` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_oof_ENS_B0_OD_h5_20261013T221030Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `9b6f9a509744d63abcfecca6f4f79cbbc608f1cc3dc19d1ca4c405d325138c90` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_oof_ENS_B0_OD_h5_20261013T221030Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `53e1a802a46fff6a9b7e8fdd431522a16469f02f3452133b723915e729aec073` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_oof_ENS_B0_OD_h5_20261013T221030Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `62153b86954b8c086f688579fd4e1813a0734a597681ed1c5c89b7d863b94cd9` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_oof_B0_h5_20261008T130849Z/manifest.json` | dependency_manifest | có | `bf4895001f012b2c2648fee80dbd6fc066bb375a8521378b0f441c6d8c60f0a5` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_oof_OD_h5_20261013T220951Z/manifest.json` | dependency_manifest | có | `a797bd33106d5b08a1566cb2afe8e33e7ac8bc794adda6fe4075a24c57b84c17` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261008T092903Z/manifest.json` | dependency_manifest | có | `6154acde23ee7facb72b14bed6544d981cd5eca0d545587ca7241f228d10cee7` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261008T102530Z/manifest.json` | dependency_manifest | có | `53997a8bf3effdec70426a718c36a9e01d04d8912523744c5df6411d5c740e6f` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261008T111605Z/manifest.json` | dependency_manifest | có | `e70ff656db7ede7fbedf4c940fd1e5996487b4b9cef87f0264688d127a778b5e` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261008T115845Z/manifest.json` | dependency_manifest | có | `059e34a311fe0728e95c159819b51410bad9533e19a31a2f031c4c7e0a435089` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261008T123531Z/manifest.json` | dependency_manifest | có | `5cb5ae17ef3c5050494a042af4136d388a75066d5660f84036244b3046142183` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261013T180511Z/manifest.json` | dependency_manifest | có | `2f4c02aee3829dc4435b5bd69de3b65f0d7b016a3f0dfa636c43f8dae61c5291` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261013T185600Z/manifest.json` | dependency_manifest | có | `b031527db82cbde4fcf50711d0a0bb351e1dd79dbebc256ad13e8954e7caa29f` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261013T194339Z/manifest.json` | dependency_manifest | có | `1b9601d80eddaea51c2b6803524afdc0987f07085f6e4bb66b8e8dc64ce618f9` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261013T203013Z/manifest.json` | dependency_manifest | có | `d3626cb529f873ff098a73f7175e86c41c126aeb0da3599b35246e19c6af6571` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261013T211846Z/manifest.json` | dependency_manifest | có | `2a157daa6aeb3c798882a4b25e26703793208de1ab45f5532b9f223cb527aeec` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_rewindow_B0_f0_h5_20261008T130621Z/manifest.json` | dependency_manifest | có | `6bbb1155de7183032bc1b89989b7491c9976ad54a4ed44b8eb003750de5bbb19` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_rewindow_B0_f1_h5_20261008T130644Z/manifest.json` | dependency_manifest | có | `ee84e01477fa15f32a5c6a313b9a66b5632d1b1ab6326aeea847eef9d234b952` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_rewindow_B0_f2_h5_20261008T130708Z/manifest.json` | dependency_manifest | có | `6ced2d2071e599ac6c2cfa6f2b18a9d904c8a2a7d88ce1fb85e844c8f7482ffd` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_rewindow_B0_f3_h5_20261008T130733Z/manifest.json` | dependency_manifest | có | `c5eb38569d93ab32271169c3843c40d5feb350b47b68a526c333943915e77650` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_rewindow_B0_f4_h5_20261008T130755Z/manifest.json` | dependency_manifest | có | `38e0ce4db58e9657c888cb42f77de495920f3a999c877db2754ad5ea1da45f68` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_rewindow_OD_f0_h5_20261013T220452Z/manifest.json` | dependency_manifest | có | `68d7603cc01c02fe65aa9023a5365f0ad4007f5270c550418685f89937227940` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_rewindow_OD_f1_h5_20261013T220548Z/manifest.json` | dependency_manifest | có | `53b37e19b6242b3a4c5685c22831c5f7ab3cfa4b2a4d6ae9fe5fa327335f56fc` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_rewindow_OD_f2_h5_20261013T220645Z/manifest.json` | dependency_manifest | có | `bb64844f45f7342903b34ff37871c80b960244815449200ad3176acc1b821647` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_rewindow_OD_f3_h5_20261013T220747Z/manifest.json` | dependency_manifest | có | `ae3936339a978ee8ad48b135cfdc69b6dfe1fa0171959dc416de15876d0c3642` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_rewindow_OD_f4_h5_20261013T220845Z/manifest.json` | dependency_manifest | có | `a931c21bbab39631fb0ddd292ce0bac3782f7fd8ad3b7126cc59f84556fbffd2` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261008T092903Z/checkpoints/best.pt` | best_checkpoint | có | `b4117b20ec2db7a888f86d5dc7a6f7859d2b4e03f2ab75734f7e664c0bf04d08` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261008T102530Z/checkpoints/best.pt` | best_checkpoint | có | `13d49939c718dfbb5f4c9b6f9a54894ed2cf4a914147aac8c6a8a8322be8383b` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261008T111605Z/checkpoints/best.pt` | best_checkpoint | có | `fffead0ee1e0e142fbce0a562e4fb24bf7ee9b5bc47fbc67813f668d9e976e56` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261008T115845Z/checkpoints/best.pt` | best_checkpoint | có | `4f50d4fba9ce74bb0bb78e3bb26b6702f4aab805311e47af01e32ff959ae08bd` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261008T123531Z/checkpoints/best.pt` | best_checkpoint | có | `dc3f346fef30fe030dc6f361d5fafb352a0e58b23a3ed22277f69a0cb08be5f0` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261013T180511Z/checkpoints/best.pt` | best_checkpoint | có | `f88767f972c0aa96a4b2af1b5f66f14f0a036b73540ed5b736781892e54de4ec` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261013T185600Z/checkpoints/best.pt` | best_checkpoint | có | `73d5995c452d2d98bb90b68ca1cd77a5a80ae2beba1ed8acd8de61af9b2ffd65` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261013T194339Z/checkpoints/best.pt` | best_checkpoint | có | `7bbfba4dc403065046868a15518bb5be79160fd118eb3f743f3860b05b62a515` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261013T203013Z/checkpoints/best.pt` | best_checkpoint | có | `8db0e5fcc7c0508b7c20cd8412cf492b221e8d221f71aac5251c56b9e61fff56` |
| phase O: sed_oof_ENS_B0_OD_h5_20261013T221030Z | `ml/runs/sed_polyphonic_20261013T211846Z/checkpoints/best.pt` | best_checkpoint | có | `aee8350700af3716f163bec0c71474214a89cdb663d968e418c2f98f21d687f6` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_oof_ENS_B0_TFKD_h5_20261008T224454Z/manifest.json` | run_manifest | có | `54969998175dc95eb5f98c74b182835c14e6076288fe53bbff687ba634c2a1c2` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_oof_ENS_B0_TFKD_h5_20261008T224454Z/predictions/dev.npz` | prediction | có | `fbc9386027507832d247849d6baf621ae6f03f2abb7684e0dd9de2056920ff81` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_oof_ENS_B0_TFKD_h5_20261008T224454Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `e8934b8eb9e985a8d56530503c05a0f899575d1ed8053261e1d8d25d5cb5aa61` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_oof_ENS_B0_TFKD_h5_20261008T224454Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `665c31f922fae067ed1c0148b78ecdd4e5342363132e6f590c49aba9de72c413` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_oof_ENS_B0_TFKD_h5_20261008T224454Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `0aa8be78a619bad67f572086f1bd9284fb1827c7e8e4be0d920d5c1947e7d5ca` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_oof_B0_h5_20261008T130849Z/manifest.json` | dependency_manifest | có | `bf4895001f012b2c2648fee80dbd6fc066bb375a8521378b0f441c6d8c60f0a5` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_oof_TFKD_h5_20261008T224209Z/manifest.json` | dependency_manifest | có | `4ca73d2b7d72260737c89122e8f0a2adef246198c9817719d8b81d11db9166b3` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T092903Z/manifest.json` | dependency_manifest | có | `6154acde23ee7facb72b14bed6544d981cd5eca0d545587ca7241f228d10cee7` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T102530Z/manifest.json` | dependency_manifest | có | `53997a8bf3effdec70426a718c36a9e01d04d8912523744c5df6411d5c740e6f` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T111605Z/manifest.json` | dependency_manifest | có | `e70ff656db7ede7fbedf4c940fd1e5996487b4b9cef87f0264688d127a778b5e` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T115845Z/manifest.json` | dependency_manifest | có | `059e34a311fe0728e95c159819b51410bad9533e19a31a2f031c4c7e0a435089` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T123531Z/manifest.json` | dependency_manifest | có | `5cb5ae17ef3c5050494a042af4136d388a75066d5660f84036244b3046142183` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T185245Z/manifest.json` | dependency_manifest | có | `1e6ce38ea54e5cf96b8247563735c21090f85309868b2c729dd5149d5d31305a` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T193842Z/manifest.json` | dependency_manifest | có | `8f80f41febd784390e1cd476d332f665e9a533f64206bac86e35b6c8b9396562` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T202607Z/manifest.json` | dependency_manifest | có | `bdb97eb2ac8f2962ce7cbb68e58fd934952b656c57b21b197aea7ebcea39bcad` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T211301Z/manifest.json` | dependency_manifest | có | `6dc7108aa306786f1fd8ea97659b5b524ec598f97a6396312a5d3ebd717dd330` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T215900Z/manifest.json` | dependency_manifest | có | `e3e3164b9268d1013cd8de83748a219c69520dff6143717c59230d81de3cabda` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_rewindow_B0_f0_h5_20261008T130621Z/manifest.json` | dependency_manifest | có | `6bbb1155de7183032bc1b89989b7491c9976ad54a4ed44b8eb003750de5bbb19` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_rewindow_B0_f1_h5_20261008T130644Z/manifest.json` | dependency_manifest | có | `ee84e01477fa15f32a5c6a313b9a66b5632d1b1ab6326aeea847eef9d234b952` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_rewindow_B0_f2_h5_20261008T130708Z/manifest.json` | dependency_manifest | có | `6ced2d2071e599ac6c2cfa6f2b18a9d904c8a2a7d88ce1fb85e844c8f7482ffd` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_rewindow_B0_f3_h5_20261008T130733Z/manifest.json` | dependency_manifest | có | `c5eb38569d93ab32271169c3843c40d5feb350b47b68a526c333943915e77650` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_rewindow_B0_f4_h5_20261008T130755Z/manifest.json` | dependency_manifest | có | `38e0ce4db58e9657c888cb42f77de495920f3a999c877db2754ad5ea1da45f68` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_rewindow_TFKD_f0_h5_20261008T223935Z/manifest.json` | dependency_manifest | có | `837005761cb77357bbbd39b5d9d272739ac3f48db38fb6aec6d8702f6e20bb84` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_rewindow_TFKD_f1_h5_20261008T223959Z/manifest.json` | dependency_manifest | có | `66827a4d5a90584609a6c4839c854dd4b23812fdadddd2ae4c865651e95701a1` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_rewindow_TFKD_f2_h5_20261008T224023Z/manifest.json` | dependency_manifest | có | `6adf07e70ecff26b10d84692f8357bfa37a6f19c0e104a11423960c95505c32a` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_rewindow_TFKD_f3_h5_20261008T224049Z/manifest.json` | dependency_manifest | có | `71506d31595d185d634268f4bff8f606a666e9bbcd3ef9278d63f09b35f23f7a` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_rewindow_TFKD_f4_h5_20261008T224114Z/manifest.json` | dependency_manifest | có | `46e4e28faf5f0f656339f7d39fd90521185e74179f6e1b907c37677c61a374d5` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T092903Z/checkpoints/best.pt` | best_checkpoint | có | `b4117b20ec2db7a888f86d5dc7a6f7859d2b4e03f2ab75734f7e664c0bf04d08` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T102530Z/checkpoints/best.pt` | best_checkpoint | có | `13d49939c718dfbb5f4c9b6f9a54894ed2cf4a914147aac8c6a8a8322be8383b` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T111605Z/checkpoints/best.pt` | best_checkpoint | có | `fffead0ee1e0e142fbce0a562e4fb24bf7ee9b5bc47fbc67813f668d9e976e56` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T115845Z/checkpoints/best.pt` | best_checkpoint | có | `4f50d4fba9ce74bb0bb78e3bb26b6702f4aab805311e47af01e32ff959ae08bd` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T123531Z/checkpoints/best.pt` | best_checkpoint | có | `dc3f346fef30fe030dc6f361d5fafb352a0e58b23a3ed22277f69a0cb08be5f0` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T185245Z/checkpoints/best.pt` | best_checkpoint | có | `b5512f9d01b9c9ebd73d26ee84dbf9c029d17a29446293a2a32a6a65070d9f2b` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T193842Z/checkpoints/best.pt` | best_checkpoint | có | `737dcf6f03a5cf5cd4b261502bb95db9d4e83606197ca30ccd2f8a9f8696d651` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T202607Z/checkpoints/best.pt` | best_checkpoint | có | `be2c4bae6af85532d9c184cddd75fde7090facec619ca1b787b0421efcc95108` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T211301Z/checkpoints/best.pt` | best_checkpoint | có | `7e2e3f5214c90c41e1a477407f49273941ebfc7aecd6b1310ce9065b3cdea643` |
| phase O: sed_oof_ENS_B0_TFKD_h5_20261008T224454Z | `ml/runs/sed_polyphonic_20261008T215900Z/checkpoints/best.pt` | best_checkpoint | có | `0cec04467c486cdf0c003e71e7d0ee73c29215f5fd62a8a3f26aeb2e0dee41d9` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_oof_OD_h5_20261013T220951Z/manifest.json` | run_manifest | có | `a797bd33106d5b08a1566cb2afe8e33e7ac8bc794adda6fe4075a24c57b84c17` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_oof_OD_h5_20261013T220951Z/predictions/dev.npz` | prediction | có | `c7dc4f9abf2e06f3d7ffea27aad83de91676176c8692d8d4db87f40f7e69b861` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_oof_OD_h5_20261013T220951Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `746a3242ceea00a7fd13d26c0b95c8988b53e64f2bb24ac0d0fd4387b6a9f883` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_oof_OD_h5_20261013T220951Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `da101c71010fdd2de0011ce97c78b0a4183b90ab91555a50f464e8f833ace33e` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_oof_OD_h5_20261013T220951Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `3bb5c7d38ec5d818daf109b19b3c5bd0f451bdc2f3bd0c4e3d022d51a986c223` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_polyphonic_20261013T180511Z/manifest.json` | dependency_manifest | có | `2f4c02aee3829dc4435b5bd69de3b65f0d7b016a3f0dfa636c43f8dae61c5291` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_polyphonic_20261013T185600Z/manifest.json` | dependency_manifest | có | `b031527db82cbde4fcf50711d0a0bb351e1dd79dbebc256ad13e8954e7caa29f` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_polyphonic_20261013T194339Z/manifest.json` | dependency_manifest | có | `1b9601d80eddaea51c2b6803524afdc0987f07085f6e4bb66b8e8dc64ce618f9` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_polyphonic_20261013T203013Z/manifest.json` | dependency_manifest | có | `d3626cb529f873ff098a73f7175e86c41c126aeb0da3599b35246e19c6af6571` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_polyphonic_20261013T211846Z/manifest.json` | dependency_manifest | có | `2a157daa6aeb3c798882a4b25e26703793208de1ab45f5532b9f223cb527aeec` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_rewindow_OD_f0_h5_20261013T220452Z/manifest.json` | dependency_manifest | có | `68d7603cc01c02fe65aa9023a5365f0ad4007f5270c550418685f89937227940` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_rewindow_OD_f1_h5_20261013T220548Z/manifest.json` | dependency_manifest | có | `53b37e19b6242b3a4c5685c22831c5f7ab3cfa4b2a4d6ae9fe5fa327335f56fc` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_rewindow_OD_f2_h5_20261013T220645Z/manifest.json` | dependency_manifest | có | `bb64844f45f7342903b34ff37871c80b960244815449200ad3176acc1b821647` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_rewindow_OD_f3_h5_20261013T220747Z/manifest.json` | dependency_manifest | có | `ae3936339a978ee8ad48b135cfdc69b6dfe1fa0171959dc416de15876d0c3642` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_rewindow_OD_f4_h5_20261013T220845Z/manifest.json` | dependency_manifest | có | `a931c21bbab39631fb0ddd292ce0bac3782f7fd8ad3b7126cc59f84556fbffd2` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_polyphonic_20261013T180511Z/checkpoints/best.pt` | best_checkpoint | có | `f88767f972c0aa96a4b2af1b5f66f14f0a036b73540ed5b736781892e54de4ec` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_polyphonic_20261013T185600Z/checkpoints/best.pt` | best_checkpoint | có | `73d5995c452d2d98bb90b68ca1cd77a5a80ae2beba1ed8acd8de61af9b2ffd65` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_polyphonic_20261013T194339Z/checkpoints/best.pt` | best_checkpoint | có | `7bbfba4dc403065046868a15518bb5be79160fd118eb3f743f3860b05b62a515` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_polyphonic_20261013T203013Z/checkpoints/best.pt` | best_checkpoint | có | `8db0e5fcc7c0508b7c20cd8412cf492b221e8d221f71aac5251c56b9e61fff56` |
| phase O: sed_oof_OD_h5_20261013T220951Z | `ml/runs/sed_polyphonic_20261013T211846Z/checkpoints/best.pt` | best_checkpoint | có | `aee8350700af3716f163bec0c71474214a89cdb663d968e418c2f98f21d687f6` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_oof_TF_h10_20261009T035119Z/manifest.json` | run_manifest | có | `3cdfd83feacfaeb14278adbbfeb78a057e0113a8f70da0417448fe220743a533` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_oof_TF_h10_20261009T035119Z/predictions/dev.npz` | prediction | có | `ec2ea6472225df0392b506bca0cbb2c3b88a48e352748d6d1594ce4b80060f71` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_oof_TF_h10_20261009T035119Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `b311ecd833c96e0ceb7514c397df2240607e795c91729debea68357af076352e` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_oof_TF_h10_20261009T035119Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `afd97a915a1bc714e9594c9f2f1986fe87bc07519baae533aa8f25ba5a5bb6be` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_oof_TF_h10_20261009T035119Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `968f1af6da4ab12a078505580bec795b51afa367c3175157d598cf00713988f7` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_polyphonic_20261008T224300Z/manifest.json` | dependency_manifest | có | `3bb785109952bc983962eb2955915a86261464a61dee364f04b1730990be8ca7` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_polyphonic_20261008T234743Z/manifest.json` | dependency_manifest | có | `aea0ab892b79643a97083ac0499b58756fc613b8508eb7411602c738d30b6275` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_polyphonic_20261009T005328Z/manifest.json` | dependency_manifest | có | `5dbc735830077af955df3893e2c55a2045ff3b104d9e9742b6da6943f13ebff7` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_polyphonic_20261009T015949Z/manifest.json` | dependency_manifest | có | `5524006b790621c08977f7ae941942c2d28c0a0eab5a52a70e538b3287ae0d86` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_polyphonic_20261009T030150Z/manifest.json` | dependency_manifest | có | `a2cd571f1d65da7aaa08fd6d1745843f8d7a8703d537f6699997f28c2970131d` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_polyphonic_20261008T224300Z/checkpoints/best.pt` | best_checkpoint | có | `de144c7b434850ae0ce7cb10f090cab7ac2801a56ca697dccc9341f60e2b6298` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_polyphonic_20261008T234743Z/checkpoints/best.pt` | best_checkpoint | có | `da670e1f28deb8c9a97e05cc838051cbf5ad5a45f0b99fbcfdc9f0e920a58de8` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_polyphonic_20261009T005328Z/checkpoints/best.pt` | best_checkpoint | có | `d18a03a79697fbf1d9db9ef576b85ff9c4fb4c2b6b86f68c0df76d96b4c46b05` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_polyphonic_20261009T015949Z/checkpoints/best.pt` | best_checkpoint | có | `673f0ea996bc5bc92204fcd49a7aae69616e9f0c1787485bcec5f10996c713ba` |
| phase O: sed_oof_TF_h10_20261009T035119Z | `ml/runs/sed_polyphonic_20261009T030150Z/checkpoints/best.pt` | best_checkpoint | có | `e58fcdf5c20da365d7f9aa2e34bad33e58f39a3e975d83db8699c4b21248b83c` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_oof_TF_h5_20261009T035153Z/manifest.json` | run_manifest | có | `d9063bd547f8bc7197929ef29566d3a08c54460cc9a85cd9fa3ca5f4bb0b39b6` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_oof_TF_h5_20261009T035153Z/predictions/dev.npz` | prediction | có | `6e789071f06c37e81c363bfcff280c54534a9548fb1c0971f228cd8544840963` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_oof_TF_h5_20261009T035153Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `c5985145fa93caaea94f2838867bd81ccf67e0dada275fd9d1077465ac3af9a2` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_oof_TF_h5_20261009T035153Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `aa21ddd110b154a6528be38905994bbf679782ca572dc3f36905274c32abdd92` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_oof_TF_h5_20261009T035153Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `cc7ad106a73b483f5502771b1d43358861cd3a3b8064f0a2a8fafbc3ab7f7dab` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_polyphonic_20261008T224300Z/manifest.json` | dependency_manifest | có | `3bb785109952bc983962eb2955915a86261464a61dee364f04b1730990be8ca7` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_polyphonic_20261008T234743Z/manifest.json` | dependency_manifest | có | `aea0ab892b79643a97083ac0499b58756fc613b8508eb7411602c738d30b6275` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_polyphonic_20261009T005328Z/manifest.json` | dependency_manifest | có | `5dbc735830077af955df3893e2c55a2045ff3b104d9e9742b6da6943f13ebff7` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_polyphonic_20261009T015949Z/manifest.json` | dependency_manifest | có | `5524006b790621c08977f7ae941942c2d28c0a0eab5a52a70e538b3287ae0d86` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_polyphonic_20261009T030150Z/manifest.json` | dependency_manifest | có | `a2cd571f1d65da7aaa08fd6d1745843f8d7a8703d537f6699997f28c2970131d` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_rewindow_TF_f0_h5_20261009T034839Z/manifest.json` | dependency_manifest | có | `f835352994940e1dbd7fd57795d04de54ecd683671df7caa885d64bf1e6ad246` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_rewindow_TF_f1_h5_20261009T034909Z/manifest.json` | dependency_manifest | có | `7f2cceaf232e90dddc3e0b651d1906651fb79f64a3010831138d98cc6e3af67e` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_rewindow_TF_f2_h5_20261009T034941Z/manifest.json` | dependency_manifest | có | `356efb0ed07f768d4bbc288da225f6ceae030e58a876e6eea150aa744a5a1e38` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_rewindow_TF_f3_h5_20261009T035014Z/manifest.json` | dependency_manifest | có | `5b939af0e41f2af57cc1ef77d109d98aa8fbd40405b5ff7436f2ca0216b61009` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_rewindow_TF_f4_h5_20261009T035045Z/manifest.json` | dependency_manifest | có | `8ff0c3115241154f660bbfb024e37896630b0c8146a5e22add5520f796dd33e7` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_polyphonic_20261008T224300Z/checkpoints/best.pt` | best_checkpoint | có | `de144c7b434850ae0ce7cb10f090cab7ac2801a56ca697dccc9341f60e2b6298` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_polyphonic_20261008T234743Z/checkpoints/best.pt` | best_checkpoint | có | `da670e1f28deb8c9a97e05cc838051cbf5ad5a45f0b99fbcfdc9f0e920a58de8` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_polyphonic_20261009T005328Z/checkpoints/best.pt` | best_checkpoint | có | `d18a03a79697fbf1d9db9ef576b85ff9c4fb4c2b6b86f68c0df76d96b4c46b05` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_polyphonic_20261009T015949Z/checkpoints/best.pt` | best_checkpoint | có | `673f0ea996bc5bc92204fcd49a7aae69616e9f0c1787485bcec5f10996c713ba` |
| phase O: sed_oof_TF_h5_20261009T035153Z | `ml/runs/sed_polyphonic_20261009T030150Z/checkpoints/best.pt` | best_checkpoint | có | `e58fcdf5c20da365d7f9aa2e34bad33e58f39a3e975d83db8699c4b21248b83c` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_oof_TFKD_h10_20261008T224140Z/manifest.json` | run_manifest | có | `e2a4109c9ff7d8efd780d857e1ab450a96a4bc92e93fe457d2250cfbe5d3cf26` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_oof_TFKD_h10_20261008T224140Z/predictions/dev.npz` | prediction | có | `ed76391c4a6e80768641a520f945188b789fbc4d6312b1ad33535ed019b897d0` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_oof_TFKD_h10_20261008T224140Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `45e38322b98ea81adf0f00b84d8540cd05e89924a7104816b7a9fae7099617d6` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_oof_TFKD_h10_20261008T224140Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `79f696194889e85791d3d3b3d716dc7cd260107a06de30e76b2212fd0f27b46b` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_oof_TFKD_h10_20261008T224140Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `87127d589b93dcfa6e1a94d5154266661f4e1c2e6e8e9db28e5362bc689aa45b` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_polyphonic_20261008T185245Z/manifest.json` | dependency_manifest | có | `1e6ce38ea54e5cf96b8247563735c21090f85309868b2c729dd5149d5d31305a` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_polyphonic_20261008T193842Z/manifest.json` | dependency_manifest | có | `8f80f41febd784390e1cd476d332f665e9a533f64206bac86e35b6c8b9396562` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_polyphonic_20261008T202607Z/manifest.json` | dependency_manifest | có | `bdb97eb2ac8f2962ce7cbb68e58fd934952b656c57b21b197aea7ebcea39bcad` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_polyphonic_20261008T211301Z/manifest.json` | dependency_manifest | có | `6dc7108aa306786f1fd8ea97659b5b524ec598f97a6396312a5d3ebd717dd330` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_polyphonic_20261008T215900Z/manifest.json` | dependency_manifest | có | `e3e3164b9268d1013cd8de83748a219c69520dff6143717c59230d81de3cabda` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_polyphonic_20261008T185245Z/checkpoints/best.pt` | best_checkpoint | có | `b5512f9d01b9c9ebd73d26ee84dbf9c029d17a29446293a2a32a6a65070d9f2b` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_polyphonic_20261008T193842Z/checkpoints/best.pt` | best_checkpoint | có | `737dcf6f03a5cf5cd4b261502bb95db9d4e83606197ca30ccd2f8a9f8696d651` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_polyphonic_20261008T202607Z/checkpoints/best.pt` | best_checkpoint | có | `be2c4bae6af85532d9c184cddd75fde7090facec619ca1b787b0421efcc95108` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_polyphonic_20261008T211301Z/checkpoints/best.pt` | best_checkpoint | có | `7e2e3f5214c90c41e1a477407f49273941ebfc7aecd6b1310ce9065b3cdea643` |
| phase O: sed_oof_TFKD_h10_20261008T224140Z | `ml/runs/sed_polyphonic_20261008T215900Z/checkpoints/best.pt` | best_checkpoint | có | `0cec04467c486cdf0c003e71e7d0ee73c29215f5fd62a8a3f26aeb2e0dee41d9` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_oof_TFKD_h5_20261008T224209Z/manifest.json` | run_manifest | có | `4ca73d2b7d72260737c89122e8f0a2adef246198c9817719d8b81d11db9166b3` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_oof_TFKD_h5_20261008T224209Z/predictions/dev.npz` | prediction | có | `734276a00bd9632368852ef722e0393e00d320260cdd022775d0eb0848ee13bb` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_oof_TFKD_h5_20261008T224209Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `132a2673ed3c2411a30d593a19381e669c8dcbd18d1979c7631f90354d493237` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_oof_TFKD_h5_20261008T224209Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `73d230ef9a87949b25922d7de44c2dd87b3d71c9b46f172432a45f2cc498210b` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_oof_TFKD_h5_20261008T224209Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `ced6ba5daf78f5f1bc5999374e62c6a0c8e95979a17adadaaa37074dc782f7ab` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_polyphonic_20261008T185245Z/manifest.json` | dependency_manifest | có | `1e6ce38ea54e5cf96b8247563735c21090f85309868b2c729dd5149d5d31305a` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_polyphonic_20261008T193842Z/manifest.json` | dependency_manifest | có | `8f80f41febd784390e1cd476d332f665e9a533f64206bac86e35b6c8b9396562` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_polyphonic_20261008T202607Z/manifest.json` | dependency_manifest | có | `bdb97eb2ac8f2962ce7cbb68e58fd934952b656c57b21b197aea7ebcea39bcad` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_polyphonic_20261008T211301Z/manifest.json` | dependency_manifest | có | `6dc7108aa306786f1fd8ea97659b5b524ec598f97a6396312a5d3ebd717dd330` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_polyphonic_20261008T215900Z/manifest.json` | dependency_manifest | có | `e3e3164b9268d1013cd8de83748a219c69520dff6143717c59230d81de3cabda` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_rewindow_TFKD_f0_h5_20261008T223935Z/manifest.json` | dependency_manifest | có | `837005761cb77357bbbd39b5d9d272739ac3f48db38fb6aec6d8702f6e20bb84` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_rewindow_TFKD_f1_h5_20261008T223959Z/manifest.json` | dependency_manifest | có | `66827a4d5a90584609a6c4839c854dd4b23812fdadddd2ae4c865651e95701a1` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_rewindow_TFKD_f2_h5_20261008T224023Z/manifest.json` | dependency_manifest | có | `6adf07e70ecff26b10d84692f8357bfa37a6f19c0e104a11423960c95505c32a` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_rewindow_TFKD_f3_h5_20261008T224049Z/manifest.json` | dependency_manifest | có | `71506d31595d185d634268f4bff8f606a666e9bbcd3ef9278d63f09b35f23f7a` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_rewindow_TFKD_f4_h5_20261008T224114Z/manifest.json` | dependency_manifest | có | `46e4e28faf5f0f656339f7d39fd90521185e74179f6e1b907c37677c61a374d5` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_polyphonic_20261008T185245Z/checkpoints/best.pt` | best_checkpoint | có | `b5512f9d01b9c9ebd73d26ee84dbf9c029d17a29446293a2a32a6a65070d9f2b` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_polyphonic_20261008T193842Z/checkpoints/best.pt` | best_checkpoint | có | `737dcf6f03a5cf5cd4b261502bb95db9d4e83606197ca30ccd2f8a9f8696d651` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_polyphonic_20261008T202607Z/checkpoints/best.pt` | best_checkpoint | có | `be2c4bae6af85532d9c184cddd75fde7090facec619ca1b787b0421efcc95108` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_polyphonic_20261008T211301Z/checkpoints/best.pt` | best_checkpoint | có | `7e2e3f5214c90c41e1a477407f49273941ebfc7aecd6b1310ce9065b3cdea643` |
| phase O: sed_oof_TFKD_h5_20261008T224209Z | `ml/runs/sed_polyphonic_20261008T215900Z/checkpoints/best.pt` | best_checkpoint | có | `0cec04467c486cdf0c003e71e7d0ee73c29215f5fd62a8a3f26aeb2e0dee41d9` |
| phase O: sed_polyphonic_20261008T092903Z | `ml/runs/sed_polyphonic_20261008T092903Z/manifest.json` | run_manifest | có | `6154acde23ee7facb72b14bed6544d981cd5eca0d545587ca7241f228d10cee7` |
| phase O: sed_polyphonic_20261008T092903Z | `ml/runs/sed_polyphonic_20261008T092903Z/predictions/dev.npz` | prediction | có | `c00b1b60410a4e42902f0934318768cb28bc5ee750abc5ded57f49ee1fb2fd5d` |
| phase O: sed_polyphonic_20261008T092903Z | `ml/runs/sed_polyphonic_20261008T092903Z/checkpoints/best.pt` | best_checkpoint | có | `b4117b20ec2db7a888f86d5dc7a6f7859d2b4e03f2ab75734f7e664c0bf04d08` |
| phase O: sed_polyphonic_20261008T102530Z | `ml/runs/sed_polyphonic_20261008T102530Z/manifest.json` | run_manifest | có | `53997a8bf3effdec70426a718c36a9e01d04d8912523744c5df6411d5c740e6f` |
| phase O: sed_polyphonic_20261008T102530Z | `ml/runs/sed_polyphonic_20261008T102530Z/predictions/dev.npz` | prediction | có | `6907c29a63495f0f92a674c519a8870daf00ed3050b3c401044e1a9fcc866edd` |
| phase O: sed_polyphonic_20261008T102530Z | `ml/runs/sed_polyphonic_20261008T102530Z/checkpoints/best.pt` | best_checkpoint | có | `13d49939c718dfbb5f4c9b6f9a54894ed2cf4a914147aac8c6a8a8322be8383b` |
| phase O: sed_polyphonic_20261008T111605Z | `ml/runs/sed_polyphonic_20261008T111605Z/manifest.json` | run_manifest | có | `e70ff656db7ede7fbedf4c940fd1e5996487b4b9cef87f0264688d127a778b5e` |
| phase O: sed_polyphonic_20261008T111605Z | `ml/runs/sed_polyphonic_20261008T111605Z/predictions/dev.npz` | prediction | có | `7700dddb9e440768d7516e6f773349a52a379de050f1a5f2d3b71062889eb3b3` |
| phase O: sed_polyphonic_20261008T111605Z | `ml/runs/sed_polyphonic_20261008T111605Z/checkpoints/best.pt` | best_checkpoint | có | `fffead0ee1e0e142fbce0a562e4fb24bf7ee9b5bc47fbc67813f668d9e976e56` |
| phase O: sed_polyphonic_20261008T115845Z | `ml/runs/sed_polyphonic_20261008T115845Z/manifest.json` | run_manifest | có | `059e34a311fe0728e95c159819b51410bad9533e19a31a2f031c4c7e0a435089` |
| phase O: sed_polyphonic_20261008T115845Z | `ml/runs/sed_polyphonic_20261008T115845Z/predictions/dev.npz` | prediction | có | `976f7fa885662ba890fcb61b7e2140dd255b52e089a96c1babcb643fbcdd85c3` |
| phase O: sed_polyphonic_20261008T115845Z | `ml/runs/sed_polyphonic_20261008T115845Z/checkpoints/best.pt` | best_checkpoint | có | `4f50d4fba9ce74bb0bb78e3bb26b6702f4aab805311e47af01e32ff959ae08bd` |
| phase O: sed_polyphonic_20261008T123531Z | `ml/runs/sed_polyphonic_20261008T123531Z/manifest.json` | run_manifest | có | `5cb5ae17ef3c5050494a042af4136d388a75066d5660f84036244b3046142183` |
| phase O: sed_polyphonic_20261008T123531Z | `ml/runs/sed_polyphonic_20261008T123531Z/predictions/dev.npz` | prediction | có | `a2429913c1aa3d8d64749572a1358c1d667fac0102ede990517a739bc16703c5` |
| phase O: sed_polyphonic_20261008T123531Z | `ml/runs/sed_polyphonic_20261008T123531Z/checkpoints/best.pt` | best_checkpoint | có | `dc3f346fef30fe030dc6f361d5fafb352a0e58b23a3ed22277f69a0cb08be5f0` |
| phase O: sed_polyphonic_20261008T185245Z | `ml/runs/sed_polyphonic_20261008T185245Z/manifest.json` | run_manifest | có | `1e6ce38ea54e5cf96b8247563735c21090f85309868b2c729dd5149d5d31305a` |
| phase O: sed_polyphonic_20261008T185245Z | `ml/runs/sed_polyphonic_20261008T185245Z/predictions/dev.npz` | prediction | có | `90cac86953b61b928b0d0fd2c44f87ab1ba0b2c206a54fb8710e34d7f970b6c1` |
| phase O: sed_polyphonic_20261008T185245Z | `ml/runs/sed_polyphonic_20261008T185245Z/checkpoints/best.pt` | best_checkpoint | có | `b5512f9d01b9c9ebd73d26ee84dbf9c029d17a29446293a2a32a6a65070d9f2b` |
| phase O: sed_polyphonic_20261008T193842Z | `ml/runs/sed_polyphonic_20261008T193842Z/manifest.json` | run_manifest | có | `8f80f41febd784390e1cd476d332f665e9a533f64206bac86e35b6c8b9396562` |
| phase O: sed_polyphonic_20261008T193842Z | `ml/runs/sed_polyphonic_20261008T193842Z/predictions/dev.npz` | prediction | có | `4b98d8ed54ceea67abc02f2856fbf92d6ce43afc0e50da7ab103501589ccc810` |
| phase O: sed_polyphonic_20261008T193842Z | `ml/runs/sed_polyphonic_20261008T193842Z/checkpoints/best.pt` | best_checkpoint | có | `737dcf6f03a5cf5cd4b261502bb95db9d4e83606197ca30ccd2f8a9f8696d651` |
| phase O: sed_polyphonic_20261008T202607Z | `ml/runs/sed_polyphonic_20261008T202607Z/manifest.json` | run_manifest | có | `bdb97eb2ac8f2962ce7cbb68e58fd934952b656c57b21b197aea7ebcea39bcad` |
| phase O: sed_polyphonic_20261008T202607Z | `ml/runs/sed_polyphonic_20261008T202607Z/predictions/dev.npz` | prediction | có | `5421c349fa4b4335df2f8acd4191539fe357fb288c04be43c69c4cc4515706b9` |
| phase O: sed_polyphonic_20261008T202607Z | `ml/runs/sed_polyphonic_20261008T202607Z/checkpoints/best.pt` | best_checkpoint | có | `be2c4bae6af85532d9c184cddd75fde7090facec619ca1b787b0421efcc95108` |
| phase O: sed_polyphonic_20261008T211301Z | `ml/runs/sed_polyphonic_20261008T211301Z/manifest.json` | run_manifest | có | `6dc7108aa306786f1fd8ea97659b5b524ec598f97a6396312a5d3ebd717dd330` |
| phase O: sed_polyphonic_20261008T211301Z | `ml/runs/sed_polyphonic_20261008T211301Z/predictions/dev.npz` | prediction | có | `596df3e0da57cf6a0384cd739f69e9d9c18c07b8b4c30610c18fab6f755b5be6` |
| phase O: sed_polyphonic_20261008T211301Z | `ml/runs/sed_polyphonic_20261008T211301Z/checkpoints/best.pt` | best_checkpoint | có | `7e2e3f5214c90c41e1a477407f49273941ebfc7aecd6b1310ce9065b3cdea643` |
| phase O: sed_polyphonic_20261008T215900Z | `ml/runs/sed_polyphonic_20261008T215900Z/manifest.json` | run_manifest | có | `e3e3164b9268d1013cd8de83748a219c69520dff6143717c59230d81de3cabda` |
| phase O: sed_polyphonic_20261008T215900Z | `ml/runs/sed_polyphonic_20261008T215900Z/predictions/dev.npz` | prediction | có | `4c04ac2712e4d5823523fe3c7742dabacbc7fcc44feb19abe3aab4ef8a67b884` |
| phase O: sed_polyphonic_20261008T215900Z | `ml/runs/sed_polyphonic_20261008T215900Z/checkpoints/best.pt` | best_checkpoint | có | `0cec04467c486cdf0c003e71e7d0ee73c29215f5fd62a8a3f26aeb2e0dee41d9` |
| phase O: sed_polyphonic_20261008T224300Z | `ml/runs/sed_polyphonic_20261008T224300Z/manifest.json` | run_manifest | có | `3bb785109952bc983962eb2955915a86261464a61dee364f04b1730990be8ca7` |
| phase O: sed_polyphonic_20261008T224300Z | `ml/runs/sed_polyphonic_20261008T224300Z/predictions/dev.npz` | prediction | có | `be4f3aaa12c0fa21792602ba422ab1271b6d9e8fa4f6b1ee10e24c4620b9ecbd` |
| phase O: sed_polyphonic_20261008T224300Z | `ml/runs/sed_polyphonic_20261008T224300Z/checkpoints/best.pt` | best_checkpoint | có | `de144c7b434850ae0ce7cb10f090cab7ac2801a56ca697dccc9341f60e2b6298` |
| phase O: sed_polyphonic_20261008T234743Z | `ml/runs/sed_polyphonic_20261008T234743Z/manifest.json` | run_manifest | có | `aea0ab892b79643a97083ac0499b58756fc613b8508eb7411602c738d30b6275` |
| phase O: sed_polyphonic_20261008T234743Z | `ml/runs/sed_polyphonic_20261008T234743Z/predictions/dev.npz` | prediction | có | `6c8c5855ffae507231feb20aa8cee599d8d7fa89f8f59902fbe499cfa1dcd099` |
| phase O: sed_polyphonic_20261008T234743Z | `ml/runs/sed_polyphonic_20261008T234743Z/checkpoints/best.pt` | best_checkpoint | có | `da670e1f28deb8c9a97e05cc838051cbf5ad5a45f0b99fbcfdc9f0e920a58de8` |
| phase O: sed_polyphonic_20261009T005328Z | `ml/runs/sed_polyphonic_20261009T005328Z/manifest.json` | run_manifest | có | `5dbc735830077af955df3893e2c55a2045ff3b104d9e9742b6da6943f13ebff7` |
| phase O: sed_polyphonic_20261009T005328Z | `ml/runs/sed_polyphonic_20261009T005328Z/predictions/dev.npz` | prediction | có | `229c7d480da9fc84a4ff9185e9d0db6b8701b74e5a6c9e6cd504cd82df6d3caa` |
| phase O: sed_polyphonic_20261009T005328Z | `ml/runs/sed_polyphonic_20261009T005328Z/checkpoints/best.pt` | best_checkpoint | có | `d18a03a79697fbf1d9db9ef576b85ff9c4fb4c2b6b86f68c0df76d96b4c46b05` |
| phase O: sed_polyphonic_20261009T015949Z | `ml/runs/sed_polyphonic_20261009T015949Z/manifest.json` | run_manifest | có | `5524006b790621c08977f7ae941942c2d28c0a0eab5a52a70e538b3287ae0d86` |
| phase O: sed_polyphonic_20261009T015949Z | `ml/runs/sed_polyphonic_20261009T015949Z/predictions/dev.npz` | prediction | có | `fbb60abef00ae411baba9bbf9d400d4c77be2b3d04cc2191cd480ad04a19bf5d` |
| phase O: sed_polyphonic_20261009T015949Z | `ml/runs/sed_polyphonic_20261009T015949Z/checkpoints/best.pt` | best_checkpoint | có | `673f0ea996bc5bc92204fcd49a7aae69616e9f0c1787485bcec5f10996c713ba` |
| phase O: sed_polyphonic_20261009T030150Z | `ml/runs/sed_polyphonic_20261009T030150Z/manifest.json` | run_manifest | có | `a2cd571f1d65da7aaa08fd6d1745843f8d7a8703d537f6699997f28c2970131d` |
| phase O: sed_polyphonic_20261009T030150Z | `ml/runs/sed_polyphonic_20261009T030150Z/predictions/dev.npz` | prediction | có | `831c5525bd02188afe7d5fc930ad7fc37f0c88129ae92eb60d37fb9e596d2e43` |
| phase O: sed_polyphonic_20261009T030150Z | `ml/runs/sed_polyphonic_20261009T030150Z/checkpoints/best.pt` | best_checkpoint | có | `e58fcdf5c20da365d7f9aa2e34bad33e58f39a3e975d83db8699c4b21248b83c` |
| phase O: sed_polyphonic_20261013T180511Z | `ml/runs/sed_polyphonic_20261013T180511Z/manifest.json` | run_manifest | có | `2f4c02aee3829dc4435b5bd69de3b65f0d7b016a3f0dfa636c43f8dae61c5291` |
| phase O: sed_polyphonic_20261013T180511Z | `ml/runs/sed_polyphonic_20261013T180511Z/predictions/dev.npz` | prediction | có | `3d050d0c277815de1a636a80a34c8fdf6b1beffe91babe67aa030e968f8c8113` |
| phase O: sed_polyphonic_20261013T180511Z | `ml/runs/sed_polyphonic_20261013T180511Z/checkpoints/best.pt` | best_checkpoint | có | `f88767f972c0aa96a4b2af1b5f66f14f0a036b73540ed5b736781892e54de4ec` |
| phase O: sed_polyphonic_20261013T185600Z | `ml/runs/sed_polyphonic_20261013T185600Z/manifest.json` | run_manifest | có | `b031527db82cbde4fcf50711d0a0bb351e1dd79dbebc256ad13e8954e7caa29f` |
| phase O: sed_polyphonic_20261013T185600Z | `ml/runs/sed_polyphonic_20261013T185600Z/predictions/dev.npz` | prediction | có | `81517888a2a643b264bf7c750d7c80f7e7a86488392e12430356a6fe6294fed7` |
| phase O: sed_polyphonic_20261013T185600Z | `ml/runs/sed_polyphonic_20261013T185600Z/checkpoints/best.pt` | best_checkpoint | có | `73d5995c452d2d98bb90b68ca1cd77a5a80ae2beba1ed8acd8de61af9b2ffd65` |
| phase O: sed_polyphonic_20261013T194339Z | `ml/runs/sed_polyphonic_20261013T194339Z/manifest.json` | run_manifest | có | `1b9601d80eddaea51c2b6803524afdc0987f07085f6e4bb66b8e8dc64ce618f9` |
| phase O: sed_polyphonic_20261013T194339Z | `ml/runs/sed_polyphonic_20261013T194339Z/predictions/dev.npz` | prediction | có | `8415b3112f9178a1375845816339342b6c8b7ce353bd1a592bf6ee65792c74ef` |
| phase O: sed_polyphonic_20261013T194339Z | `ml/runs/sed_polyphonic_20261013T194339Z/checkpoints/best.pt` | best_checkpoint | có | `7bbfba4dc403065046868a15518bb5be79160fd118eb3f743f3860b05b62a515` |
| phase O: sed_polyphonic_20261013T203013Z | `ml/runs/sed_polyphonic_20261013T203013Z/manifest.json` | run_manifest | có | `d3626cb529f873ff098a73f7175e86c41c126aeb0da3599b35246e19c6af6571` |
| phase O: sed_polyphonic_20261013T203013Z | `ml/runs/sed_polyphonic_20261013T203013Z/predictions/dev.npz` | prediction | có | `acde9f4341453bc3d66dd292980c75799813f8c483ba589069fbb6bfac714d4e` |
| phase O: sed_polyphonic_20261013T203013Z | `ml/runs/sed_polyphonic_20261013T203013Z/checkpoints/best.pt` | best_checkpoint | có | `8db0e5fcc7c0508b7c20cd8412cf492b221e8d221f71aac5251c56b9e61fff56` |
| phase O: sed_polyphonic_20261013T211846Z | `ml/runs/sed_polyphonic_20261013T211846Z/manifest.json` | run_manifest | có | `2a157daa6aeb3c798882a4b25e26703793208de1ab45f5532b9f223cb527aeec` |
| phase O: sed_polyphonic_20261013T211846Z | `ml/runs/sed_polyphonic_20261013T211846Z/predictions/dev.npz` | prediction | có | `5fe91f89340f4d3d90c2f02aaee07e5281a09f1e3472a158af999f0d7f295865` |
| phase O: sed_polyphonic_20261013T211846Z | `ml/runs/sed_polyphonic_20261013T211846Z/checkpoints/best.pt` | best_checkpoint | có | `aee8350700af3716f163bec0c71474214a89cdb663d968e418c2f98f21d687f6` |
| phase O: sed_rewindow_B0_f0_h5_20261008T130621Z | `ml/runs/sed_rewindow_B0_f0_h5_20261008T130621Z/manifest.json` | run_manifest | có | `6bbb1155de7183032bc1b89989b7491c9976ad54a4ed44b8eb003750de5bbb19` |
| phase O: sed_rewindow_B0_f0_h5_20261008T130621Z | `ml/runs/sed_rewindow_B0_f0_h5_20261008T130621Z/predictions/dev.npz` | prediction | có | `4ec365ec5ed724d280d5d47b4b24754e4db01a2a4c9426610e83b0d0745d1bd9` |
| phase O: sed_rewindow_B0_f0_h5_20261008T130621Z | `ml/runs/sed_polyphonic_20261008T092903Z/manifest.json` | dependency_manifest | có | `6154acde23ee7facb72b14bed6544d981cd5eca0d545587ca7241f228d10cee7` |
| phase O: sed_rewindow_B0_f0_h5_20261008T130621Z | `ml/runs/sed_polyphonic_20261008T092903Z/checkpoints/best.pt` | best_checkpoint | có | `b4117b20ec2db7a888f86d5dc7a6f7859d2b4e03f2ab75734f7e664c0bf04d08` |
| phase O: sed_rewindow_B0_f0_h5_test_20261014T084758Z | `ml/runs/sed_rewindow_B0_f0_h5_test_20261014T084758Z/manifest.json` | run_manifest | có | `802a2a8d91d09b2038156afa397f2809de2196524abebc3b59ed9245ef448f44` |
| phase O: sed_rewindow_B0_f0_h5_test_20261014T084758Z | `ml/runs/sed_rewindow_B0_f0_h5_test_20261014T084758Z/predictions/test.npz` | prediction | có | `8ab65b0fb732f4a5fa1b0dd7cae11eae7b2240c3a7ea6139b34e2ed200a2cf26` |
| phase O: sed_rewindow_B0_f0_h5_test_20261014T084758Z | `ml/runs/sed_polyphonic_20261008T092903Z/manifest.json` | dependency_manifest | có | `6154acde23ee7facb72b14bed6544d981cd5eca0d545587ca7241f228d10cee7` |
| phase O: sed_rewindow_B0_f0_h5_test_20261014T084758Z | `ml/runs/sed_polyphonic_20261008T092903Z/checkpoints/best.pt` | best_checkpoint | có | `b4117b20ec2db7a888f86d5dc7a6f7859d2b4e03f2ab75734f7e664c0bf04d08` |
| phase O: sed_rewindow_B0_f1_h5_20261008T130644Z | `ml/runs/sed_rewindow_B0_f1_h5_20261008T130644Z/manifest.json` | run_manifest | có | `ee84e01477fa15f32a5c6a313b9a66b5632d1b1ab6326aeea847eef9d234b952` |
| phase O: sed_rewindow_B0_f1_h5_20261008T130644Z | `ml/runs/sed_rewindow_B0_f1_h5_20261008T130644Z/predictions/dev.npz` | prediction | có | `6201c16b04bb3d4ca573e9352e8f1fb7de93f73564fbe217b222183e087abf6b` |
| phase O: sed_rewindow_B0_f1_h5_20261008T130644Z | `ml/runs/sed_polyphonic_20261008T102530Z/manifest.json` | dependency_manifest | có | `53997a8bf3effdec70426a718c36a9e01d04d8912523744c5df6411d5c740e6f` |
| phase O: sed_rewindow_B0_f1_h5_20261008T130644Z | `ml/runs/sed_polyphonic_20261008T102530Z/checkpoints/best.pt` | best_checkpoint | có | `13d49939c718dfbb5f4c9b6f9a54894ed2cf4a914147aac8c6a8a8322be8383b` |
| phase O: sed_rewindow_B0_f1_h5_test_20261014T084829Z | `ml/runs/sed_rewindow_B0_f1_h5_test_20261014T084829Z/manifest.json` | run_manifest | có | `798a60d02ad7841428a68faca58f2a836688e33234a665f52f2e3ddbde3b7456` |
| phase O: sed_rewindow_B0_f1_h5_test_20261014T084829Z | `ml/runs/sed_rewindow_B0_f1_h5_test_20261014T084829Z/predictions/test.npz` | prediction | có | `951540d74908a07b3bc8c7f09549c8c79bbfb96afbcfa695bd8f91f3900427d9` |
| phase O: sed_rewindow_B0_f1_h5_test_20261014T084829Z | `ml/runs/sed_polyphonic_20261008T102530Z/manifest.json` | dependency_manifest | có | `53997a8bf3effdec70426a718c36a9e01d04d8912523744c5df6411d5c740e6f` |
| phase O: sed_rewindow_B0_f1_h5_test_20261014T084829Z | `ml/runs/sed_polyphonic_20261008T102530Z/checkpoints/best.pt` | best_checkpoint | có | `13d49939c718dfbb5f4c9b6f9a54894ed2cf4a914147aac8c6a8a8322be8383b` |
| phase O: sed_rewindow_B0_f2_h5_20261008T130708Z | `ml/runs/sed_rewindow_B0_f2_h5_20261008T130708Z/manifest.json` | run_manifest | có | `6ced2d2071e599ac6c2cfa6f2b18a9d904c8a2a7d88ce1fb85e844c8f7482ffd` |
| phase O: sed_rewindow_B0_f2_h5_20261008T130708Z | `ml/runs/sed_rewindow_B0_f2_h5_20261008T130708Z/predictions/dev.npz` | prediction | có | `edcf5e734b27d02dc8c0301e027d04962f9d0d98d3f22616e98f1146892210c0` |
| phase O: sed_rewindow_B0_f2_h5_20261008T130708Z | `ml/runs/sed_polyphonic_20261008T111605Z/manifest.json` | dependency_manifest | có | `e70ff656db7ede7fbedf4c940fd1e5996487b4b9cef87f0264688d127a778b5e` |
| phase O: sed_rewindow_B0_f2_h5_20261008T130708Z | `ml/runs/sed_polyphonic_20261008T111605Z/checkpoints/best.pt` | best_checkpoint | có | `fffead0ee1e0e142fbce0a562e4fb24bf7ee9b5bc47fbc67813f668d9e976e56` |
| phase O: sed_rewindow_B0_f2_h5_test_20261014T084856Z | `ml/runs/sed_rewindow_B0_f2_h5_test_20261014T084856Z/manifest.json` | run_manifest | có | `cc480cdf9ac4fdd9b16397cd6349ce6055ce2495b7342b51e7b25919ef08fc11` |
| phase O: sed_rewindow_B0_f2_h5_test_20261014T084856Z | `ml/runs/sed_rewindow_B0_f2_h5_test_20261014T084856Z/predictions/test.npz` | prediction | có | `6f90bf4ec17cde7818db91efd959878051f9727ffd06528505b284fdf313fffd` |
| phase O: sed_rewindow_B0_f2_h5_test_20261014T084856Z | `ml/runs/sed_polyphonic_20261008T111605Z/manifest.json` | dependency_manifest | có | `e70ff656db7ede7fbedf4c940fd1e5996487b4b9cef87f0264688d127a778b5e` |
| phase O: sed_rewindow_B0_f2_h5_test_20261014T084856Z | `ml/runs/sed_polyphonic_20261008T111605Z/checkpoints/best.pt` | best_checkpoint | có | `fffead0ee1e0e142fbce0a562e4fb24bf7ee9b5bc47fbc67813f668d9e976e56` |
| phase O: sed_rewindow_B0_f3_h5_20261008T130733Z | `ml/runs/sed_rewindow_B0_f3_h5_20261008T130733Z/manifest.json` | run_manifest | có | `c5eb38569d93ab32271169c3843c40d5feb350b47b68a526c333943915e77650` |
| phase O: sed_rewindow_B0_f3_h5_20261008T130733Z | `ml/runs/sed_rewindow_B0_f3_h5_20261008T130733Z/predictions/dev.npz` | prediction | có | `0690d78908db094595449c76d39c72419fc8e72d40123e7bfaa9dcf4652b696d` |
| phase O: sed_rewindow_B0_f3_h5_20261008T130733Z | `ml/runs/sed_polyphonic_20261008T115845Z/manifest.json` | dependency_manifest | có | `059e34a311fe0728e95c159819b51410bad9533e19a31a2f031c4c7e0a435089` |
| phase O: sed_rewindow_B0_f3_h5_20261008T130733Z | `ml/runs/sed_polyphonic_20261008T115845Z/checkpoints/best.pt` | best_checkpoint | có | `4f50d4fba9ce74bb0bb78e3bb26b6702f4aab805311e47af01e32ff959ae08bd` |
| phase O: sed_rewindow_B0_f3_h5_test_20261014T084923Z | `ml/runs/sed_rewindow_B0_f3_h5_test_20261014T084923Z/manifest.json` | run_manifest | có | `c9f4ccf6f62fbfb599dafea4d984b92f02edbc053d5c698ca46a72532ef2787b` |
| phase O: sed_rewindow_B0_f3_h5_test_20261014T084923Z | `ml/runs/sed_rewindow_B0_f3_h5_test_20261014T084923Z/predictions/test.npz` | prediction | có | `cea681c6defee7fd1a931552d212f39241549d9a44deb1081f9ee610ec4dca59` |
| phase O: sed_rewindow_B0_f3_h5_test_20261014T084923Z | `ml/runs/sed_polyphonic_20261008T115845Z/manifest.json` | dependency_manifest | có | `059e34a311fe0728e95c159819b51410bad9533e19a31a2f031c4c7e0a435089` |
| phase O: sed_rewindow_B0_f3_h5_test_20261014T084923Z | `ml/runs/sed_polyphonic_20261008T115845Z/checkpoints/best.pt` | best_checkpoint | có | `4f50d4fba9ce74bb0bb78e3bb26b6702f4aab805311e47af01e32ff959ae08bd` |
| phase O: sed_rewindow_B0_f4_h5_20261008T130755Z | `ml/runs/sed_rewindow_B0_f4_h5_20261008T130755Z/manifest.json` | run_manifest | có | `38e0ce4db58e9657c888cb42f77de495920f3a999c877db2754ad5ea1da45f68` |
| phase O: sed_rewindow_B0_f4_h5_20261008T130755Z | `ml/runs/sed_rewindow_B0_f4_h5_20261008T130755Z/predictions/dev.npz` | prediction | có | `4d1494be1363e494b73caed36167b4397e133b595ef173be6b033b0db5dfd6d7` |
| phase O: sed_rewindow_B0_f4_h5_20261008T130755Z | `ml/runs/sed_polyphonic_20261008T123531Z/manifest.json` | dependency_manifest | có | `5cb5ae17ef3c5050494a042af4136d388a75066d5660f84036244b3046142183` |
| phase O: sed_rewindow_B0_f4_h5_20261008T130755Z | `ml/runs/sed_polyphonic_20261008T123531Z/checkpoints/best.pt` | best_checkpoint | có | `dc3f346fef30fe030dc6f361d5fafb352a0e58b23a3ed22277f69a0cb08be5f0` |
| phase O: sed_rewindow_B0_f4_h5_test_20261014T084950Z | `ml/runs/sed_rewindow_B0_f4_h5_test_20261014T084950Z/manifest.json` | run_manifest | có | `0b2e41f949ab0ff954f8a93d3b4308f60865bda1e91713e52dfeadb234cd41bc` |
| phase O: sed_rewindow_B0_f4_h5_test_20261014T084950Z | `ml/runs/sed_rewindow_B0_f4_h5_test_20261014T084950Z/predictions/test.npz` | prediction | có | `4247a7bba7e7bc4a763757e4604a4150900abf198d67cd82478405ef4a240c1b` |
| phase O: sed_rewindow_B0_f4_h5_test_20261014T084950Z | `ml/runs/sed_polyphonic_20261008T123531Z/manifest.json` | dependency_manifest | có | `5cb5ae17ef3c5050494a042af4136d388a75066d5660f84036244b3046142183` |
| phase O: sed_rewindow_B0_f4_h5_test_20261014T084950Z | `ml/runs/sed_polyphonic_20261008T123531Z/checkpoints/best.pt` | best_checkpoint | có | `dc3f346fef30fe030dc6f361d5fafb352a0e58b23a3ed22277f69a0cb08be5f0` |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m1_20261008T060426Z | `ml/runs/sed_rewindow_f2_h2.5_triangular0.3_m1_20261008T060426Z/manifest.json` | run_manifest | có | `2b9c8b71dd85884ea031e9a0c736c1fcb8ac39d1717c432f39decacc5c0df6a9` |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m1_20261008T060426Z | `ml/runs/sed_rewindow_f2_h2.5_triangular0.3_m1_20261008T060426Z/predictions/dev.npz` | prediction | có | `c3d0fc1c5a048a370f75d4b85a954946dc52ee01f02624f96c912c5bdceb8eac` |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m1_20261008T060426Z | `ml/runs/sed_polyphonic_20260927T172924Z/manifest.json` | dependency_manifest | có | `17388e20e2cc97b57e5ef693a2d627c57e814b9826a92c28b2ecc27077174160` |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m1_20261008T060426Z | `ml/runs/sed_polyphonic_20260927T172924Z/checkpoints/best.pt` | best_checkpoint | có | `5090beb60bbd38ae00396506d0d64d910de66dec914ddbf92f1c2bcf39561a8d` |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m2_20261008T060530Z | `ml/runs/sed_rewindow_f2_h2.5_triangular0.3_m2_20261008T060530Z/manifest.json` | run_manifest | có | `dc86815e48f270570650fddbb81b1a9a968f130167d7f3722b7194ad0018f345` |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m2_20261008T060530Z | `ml/runs/sed_rewindow_f2_h2.5_triangular0.3_m2_20261008T060530Z/predictions/dev.npz` | prediction | có | `f5d0df1343985a88d0bf99752c054efcb7dea260c38b6f50b105d43868d49849` |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m2_20261008T060530Z | `ml/runs/sed_polyphonic_20260927T180358Z/manifest.json` | dependency_manifest | có | `b7d793ae28c9a0cc2b89f981c194ea43621d2d20a8c9634c257de756b9a2e0ce` |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m2_20261008T060530Z | `ml/runs/sed_polyphonic_20260927T180358Z/checkpoints/best.pt` | best_checkpoint | có | `787e15395f05ef52d219e190286cba35b3d79e8681f974fc87410b825133663d` |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m3_20261008T060629Z | `ml/runs/sed_rewindow_f2_h2.5_triangular0.3_m3_20261008T060629Z/manifest.json` | run_manifest | có | `310789331e51b681b84d084984d93672fc948c1bf816701bc94936d66f4ac18a` |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m3_20261008T060629Z | `ml/runs/sed_rewindow_f2_h2.5_triangular0.3_m3_20261008T060629Z/predictions/dev.npz` | prediction | có | `51ea581c607a07927e609d2278348a9c33ee37226e6b11cf521017481167b8cd` |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m3_20261008T060629Z | `ml/runs/sed_polyphonic_20260927T185137Z/manifest.json` | dependency_manifest | có | `30c6f4045ef5c38a3b3cd0d7a5ae9fb05f86279877e383e5fe862ed7ccfcbb3c` |
| phase O: sed_rewindow_f2_h2.5_triangular0.3_m3_20261008T060629Z | `ml/runs/sed_polyphonic_20260927T185137Z/checkpoints/best.pt` | best_checkpoint | có | `6bfa01b3217387c36f508a7f46d87db391e30060748db680a3bed08662e3a44f` |
| phase O: sed_rewindow_f2_h2.5_uniform_m1_20261008T073910Z | `ml/runs/sed_rewindow_f2_h2.5_uniform_m1_20261008T073910Z/manifest.json` | run_manifest | có | `dc06c8dd42edd2e40cbab94464c3dfdba0a307e73e5788e1ce0ed1dc96d3730e` |
| phase O: sed_rewindow_f2_h2.5_uniform_m1_20261008T073910Z | `ml/runs/sed_rewindow_f2_h2.5_uniform_m1_20261008T073910Z/predictions/dev.npz` | prediction | có | `4bf57080ec995613ae95af2db9cafa09e8815f972ff5f39262d6ec6242600e6a` |
| phase O: sed_rewindow_f2_h2.5_uniform_m1_20261008T073910Z | `ml/runs/sed_polyphonic_20260927T172924Z/manifest.json` | dependency_manifest | có | `17388e20e2cc97b57e5ef693a2d627c57e814b9826a92c28b2ecc27077174160` |
| phase O: sed_rewindow_f2_h2.5_uniform_m1_20261008T073910Z | `ml/runs/sed_polyphonic_20260927T172924Z/checkpoints/best.pt` | best_checkpoint | có | `5090beb60bbd38ae00396506d0d64d910de66dec914ddbf92f1c2bcf39561a8d` |
| phase O: sed_rewindow_f2_h2.5_uniform_m2_20261008T074045Z | `ml/runs/sed_rewindow_f2_h2.5_uniform_m2_20261008T074045Z/manifest.json` | run_manifest | có | `cdffd0c1a12b353b26a256609299f60c1a701f47bc957746edfbf869c65a5433` |
| phase O: sed_rewindow_f2_h2.5_uniform_m2_20261008T074045Z | `ml/runs/sed_rewindow_f2_h2.5_uniform_m2_20261008T074045Z/predictions/dev.npz` | prediction | có | `ad2d5e879c30484a4b179fe4351da0d23f5cbc459e0da5bc90a9dcffe0272014` |
| phase O: sed_rewindow_f2_h2.5_uniform_m2_20261008T074045Z | `ml/runs/sed_polyphonic_20260927T180358Z/manifest.json` | dependency_manifest | có | `b7d793ae28c9a0cc2b89f981c194ea43621d2d20a8c9634c257de756b9a2e0ce` |
| phase O: sed_rewindow_f2_h2.5_uniform_m2_20261008T074045Z | `ml/runs/sed_polyphonic_20260927T180358Z/checkpoints/best.pt` | best_checkpoint | có | `787e15395f05ef52d219e190286cba35b3d79e8681f974fc87410b825133663d` |
| phase O: sed_rewindow_f2_h2.5_uniform_m3_20261008T074220Z | `ml/runs/sed_rewindow_f2_h2.5_uniform_m3_20261008T074220Z/manifest.json` | run_manifest | có | `46e020e6b688eb3291dd7c6863dd49a278b35e23e9a263224fad8887e1fa29ad` |
| phase O: sed_rewindow_f2_h2.5_uniform_m3_20261008T074220Z | `ml/runs/sed_rewindow_f2_h2.5_uniform_m3_20261008T074220Z/predictions/dev.npz` | prediction | có | `795b19f03b7aa815b5cdebefb43d722921bb8430f62888f6c52b9b90c5d82e09` |
| phase O: sed_rewindow_f2_h2.5_uniform_m3_20261008T074220Z | `ml/runs/sed_polyphonic_20260927T185137Z/manifest.json` | dependency_manifest | có | `30c6f4045ef5c38a3b3cd0d7a5ae9fb05f86279877e383e5fe862ed7ccfcbb3c` |
| phase O: sed_rewindow_f2_h2.5_uniform_m3_20261008T074220Z | `ml/runs/sed_polyphonic_20260927T185137Z/checkpoints/best.pt` | best_checkpoint | có | `6bfa01b3217387c36f508a7f46d87db391e30060748db680a3bed08662e3a44f` |
| phase O: sed_rewindow_f2_h5_triangular0.3_m1_20261008T064524Z | `ml/runs/sed_rewindow_f2_h5_triangular0.3_m1_20261008T064524Z/manifest.json` | run_manifest | có | `879ace02e3532640e8a75ad93f0db862f62a6f0d0d6219c6d5a93a6401ffb45c` |
| phase O: sed_rewindow_f2_h5_triangular0.3_m1_20261008T064524Z | `ml/runs/sed_rewindow_f2_h5_triangular0.3_m1_20261008T064524Z/predictions/dev.npz` | prediction | có | `2ce14cacc7cb11af7fdc596f0040be12cea9c21b2a651c2e84cc89c998c09585` |
| phase O: sed_rewindow_f2_h5_triangular0.3_m1_20261008T064524Z | `ml/runs/sed_polyphonic_20260927T172924Z/manifest.json` | dependency_manifest | có | `17388e20e2cc97b57e5ef693a2d627c57e814b9826a92c28b2ecc27077174160` |
| phase O: sed_rewindow_f2_h5_triangular0.3_m1_20261008T064524Z | `ml/runs/sed_polyphonic_20260927T172924Z/checkpoints/best.pt` | best_checkpoint | có | `5090beb60bbd38ae00396506d0d64d910de66dec914ddbf92f1c2bcf39561a8d` |
| phase O: sed_rewindow_f2_h5_triangular0.3_m2_20261008T064611Z | `ml/runs/sed_rewindow_f2_h5_triangular0.3_m2_20261008T064611Z/manifest.json` | run_manifest | có | `009af4430b9cf4943b9610c58e188ba8fd0438a75819ddd4c1ba4213b40b4015` |
| phase O: sed_rewindow_f2_h5_triangular0.3_m2_20261008T064611Z | `ml/runs/sed_rewindow_f2_h5_triangular0.3_m2_20261008T064611Z/predictions/dev.npz` | prediction | có | `15e626c488e3c541ad910676ec6545e4cb180bfbd1a96dd2577faee99036bd30` |
| phase O: sed_rewindow_f2_h5_triangular0.3_m2_20261008T064611Z | `ml/runs/sed_polyphonic_20260927T180358Z/manifest.json` | dependency_manifest | có | `b7d793ae28c9a0cc2b89f981c194ea43621d2d20a8c9634c257de756b9a2e0ce` |
| phase O: sed_rewindow_f2_h5_triangular0.3_m2_20261008T064611Z | `ml/runs/sed_polyphonic_20260927T180358Z/checkpoints/best.pt` | best_checkpoint | có | `787e15395f05ef52d219e190286cba35b3d79e8681f974fc87410b825133663d` |
| phase O: sed_rewindow_f2_h5_triangular0.3_m3_20261008T064653Z | `ml/runs/sed_rewindow_f2_h5_triangular0.3_m3_20261008T064653Z/manifest.json` | run_manifest | có | `a3d4500105bf03af5c6720c46dc47de42ab4059e7b7547e7f28687050228b4ba` |
| phase O: sed_rewindow_f2_h5_triangular0.3_m3_20261008T064653Z | `ml/runs/sed_rewindow_f2_h5_triangular0.3_m3_20261008T064653Z/predictions/dev.npz` | prediction | có | `b144334832fb689a2d5aa69add7befa1c630c6a6de9913408536ccbba14b4eac` |
| phase O: sed_rewindow_f2_h5_triangular0.3_m3_20261008T064653Z | `ml/runs/sed_polyphonic_20260927T185137Z/manifest.json` | dependency_manifest | có | `30c6f4045ef5c38a3b3cd0d7a5ae9fb05f86279877e383e5fe862ed7ccfcbb3c` |
| phase O: sed_rewindow_f2_h5_triangular0.3_m3_20261008T064653Z | `ml/runs/sed_polyphonic_20260927T185137Z/checkpoints/best.pt` | best_checkpoint | có | `6bfa01b3217387c36f508a7f46d87db391e30060748db680a3bed08662e3a44f` |
| phase O: sed_rewindow_OD_f0_h5_20261013T220452Z | `ml/runs/sed_rewindow_OD_f0_h5_20261013T220452Z/manifest.json` | run_manifest | có | `68d7603cc01c02fe65aa9023a5365f0ad4007f5270c550418685f89937227940` |
| phase O: sed_rewindow_OD_f0_h5_20261013T220452Z | `ml/runs/sed_rewindow_OD_f0_h5_20261013T220452Z/predictions/dev.npz` | prediction | có | `404119b1112278dbe77fb4b60d9785f6ea94a1d7d22642ff609d530a50a2e72f` |
| phase O: sed_rewindow_OD_f0_h5_20261013T220452Z | `ml/runs/sed_polyphonic_20261013T180511Z/manifest.json` | dependency_manifest | có | `2f4c02aee3829dc4435b5bd69de3b65f0d7b016a3f0dfa636c43f8dae61c5291` |
| phase O: sed_rewindow_OD_f0_h5_20261013T220452Z | `ml/runs/sed_polyphonic_20261013T180511Z/checkpoints/best.pt` | best_checkpoint | có | `f88767f972c0aa96a4b2af1b5f66f14f0a036b73540ed5b736781892e54de4ec` |
| phase O: sed_rewindow_OD_f1_h5_20261013T220548Z | `ml/runs/sed_rewindow_OD_f1_h5_20261013T220548Z/manifest.json` | run_manifest | có | `53b37e19b6242b3a4c5685c22831c5f7ab3cfa4b2a4d6ae9fe5fa327335f56fc` |
| phase O: sed_rewindow_OD_f1_h5_20261013T220548Z | `ml/runs/sed_rewindow_OD_f1_h5_20261013T220548Z/predictions/dev.npz` | prediction | có | `067a594cf0d6be85a5f30bb2c84f00f90b55959a095932ac237d2469657d08a4` |
| phase O: sed_rewindow_OD_f1_h5_20261013T220548Z | `ml/runs/sed_polyphonic_20261013T185600Z/manifest.json` | dependency_manifest | có | `b031527db82cbde4fcf50711d0a0bb351e1dd79dbebc256ad13e8954e7caa29f` |
| phase O: sed_rewindow_OD_f1_h5_20261013T220548Z | `ml/runs/sed_polyphonic_20261013T185600Z/checkpoints/best.pt` | best_checkpoint | có | `73d5995c452d2d98bb90b68ca1cd77a5a80ae2beba1ed8acd8de61af9b2ffd65` |
| phase O: sed_rewindow_OD_f2_h5_20261013T220645Z | `ml/runs/sed_rewindow_OD_f2_h5_20261013T220645Z/manifest.json` | run_manifest | có | `bb64844f45f7342903b34ff37871c80b960244815449200ad3176acc1b821647` |
| phase O: sed_rewindow_OD_f2_h5_20261013T220645Z | `ml/runs/sed_rewindow_OD_f2_h5_20261013T220645Z/predictions/dev.npz` | prediction | có | `c9a57a30702af2417727fc6cfb983755e81409e80f7b465e88d4e6731ccfc5e3` |
| phase O: sed_rewindow_OD_f2_h5_20261013T220645Z | `ml/runs/sed_polyphonic_20261013T194339Z/manifest.json` | dependency_manifest | có | `1b9601d80eddaea51c2b6803524afdc0987f07085f6e4bb66b8e8dc64ce618f9` |
| phase O: sed_rewindow_OD_f2_h5_20261013T220645Z | `ml/runs/sed_polyphonic_20261013T194339Z/checkpoints/best.pt` | best_checkpoint | có | `7bbfba4dc403065046868a15518bb5be79160fd118eb3f743f3860b05b62a515` |
| phase O: sed_rewindow_OD_f3_h5_20261013T220747Z | `ml/runs/sed_rewindow_OD_f3_h5_20261013T220747Z/manifest.json` | run_manifest | có | `ae3936339a978ee8ad48b135cfdc69b6dfe1fa0171959dc416de15876d0c3642` |
| phase O: sed_rewindow_OD_f3_h5_20261013T220747Z | `ml/runs/sed_rewindow_OD_f3_h5_20261013T220747Z/predictions/dev.npz` | prediction | có | `7f8625e13bbfa0a2449570f11d0088761c34151737f9d53e2cdeef62a4c44bf8` |
| phase O: sed_rewindow_OD_f3_h5_20261013T220747Z | `ml/runs/sed_polyphonic_20261013T203013Z/manifest.json` | dependency_manifest | có | `d3626cb529f873ff098a73f7175e86c41c126aeb0da3599b35246e19c6af6571` |
| phase O: sed_rewindow_OD_f3_h5_20261013T220747Z | `ml/runs/sed_polyphonic_20261013T203013Z/checkpoints/best.pt` | best_checkpoint | có | `8db0e5fcc7c0508b7c20cd8412cf492b221e8d221f71aac5251c56b9e61fff56` |
| phase O: sed_rewindow_OD_f4_h5_20261013T220845Z | `ml/runs/sed_rewindow_OD_f4_h5_20261013T220845Z/manifest.json` | run_manifest | có | `a931c21bbab39631fb0ddd292ce0bac3782f7fd8ad3b7126cc59f84556fbffd2` |
| phase O: sed_rewindow_OD_f4_h5_20261013T220845Z | `ml/runs/sed_rewindow_OD_f4_h5_20261013T220845Z/predictions/dev.npz` | prediction | có | `7ca6f2640b20c131b3304a82c7de9a46b1e8099b08cd323b928c83b6ed8e3c69` |
| phase O: sed_rewindow_OD_f4_h5_20261013T220845Z | `ml/runs/sed_polyphonic_20261013T211846Z/manifest.json` | dependency_manifest | có | `2a157daa6aeb3c798882a4b25e26703793208de1ab45f5532b9f223cb527aeec` |
| phase O: sed_rewindow_OD_f4_h5_20261013T220845Z | `ml/runs/sed_polyphonic_20261013T211846Z/checkpoints/best.pt` | best_checkpoint | có | `aee8350700af3716f163bec0c71474214a89cdb663d968e418c2f98f21d687f6` |
| phase O: sed_rewindow_TF_f0_h5_20261009T034839Z | `ml/runs/sed_rewindow_TF_f0_h5_20261009T034839Z/manifest.json` | run_manifest | có | `f835352994940e1dbd7fd57795d04de54ecd683671df7caa885d64bf1e6ad246` |
| phase O: sed_rewindow_TF_f0_h5_20261009T034839Z | `ml/runs/sed_rewindow_TF_f0_h5_20261009T034839Z/predictions/dev.npz` | prediction | có | `5166b1024c1e1cb631619ebc67fe2bcbd4c815e67821c0e8b6265634d7dae9be` |
| phase O: sed_rewindow_TF_f0_h5_20261009T034839Z | `ml/runs/sed_polyphonic_20261008T224300Z/manifest.json` | dependency_manifest | có | `3bb785109952bc983962eb2955915a86261464a61dee364f04b1730990be8ca7` |
| phase O: sed_rewindow_TF_f0_h5_20261009T034839Z | `ml/runs/sed_polyphonic_20261008T224300Z/checkpoints/best.pt` | best_checkpoint | có | `de144c7b434850ae0ce7cb10f090cab7ac2801a56ca697dccc9341f60e2b6298` |
| phase O: sed_rewindow_TF_f1_h5_20261009T034909Z | `ml/runs/sed_rewindow_TF_f1_h5_20261009T034909Z/manifest.json` | run_manifest | có | `7f2cceaf232e90dddc3e0b651d1906651fb79f64a3010831138d98cc6e3af67e` |
| phase O: sed_rewindow_TF_f1_h5_20261009T034909Z | `ml/runs/sed_rewindow_TF_f1_h5_20261009T034909Z/predictions/dev.npz` | prediction | có | `cfe6d7a2e37a5a0b108be2a4b086f7538a72cedec897f31f64fb15331553fae6` |
| phase O: sed_rewindow_TF_f1_h5_20261009T034909Z | `ml/runs/sed_polyphonic_20261008T234743Z/manifest.json` | dependency_manifest | có | `aea0ab892b79643a97083ac0499b58756fc613b8508eb7411602c738d30b6275` |
| phase O: sed_rewindow_TF_f1_h5_20261009T034909Z | `ml/runs/sed_polyphonic_20261008T234743Z/checkpoints/best.pt` | best_checkpoint | có | `da670e1f28deb8c9a97e05cc838051cbf5ad5a45f0b99fbcfdc9f0e920a58de8` |
| phase O: sed_rewindow_TF_f2_h5_20261009T034941Z | `ml/runs/sed_rewindow_TF_f2_h5_20261009T034941Z/manifest.json` | run_manifest | có | `356efb0ed07f768d4bbc288da225f6ceae030e58a876e6eea150aa744a5a1e38` |
| phase O: sed_rewindow_TF_f2_h5_20261009T034941Z | `ml/runs/sed_rewindow_TF_f2_h5_20261009T034941Z/predictions/dev.npz` | prediction | có | `e409f05ca16f9e80bce99090332a447ea72356d819d4084d7c136e37f4df0916` |
| phase O: sed_rewindow_TF_f2_h5_20261009T034941Z | `ml/runs/sed_polyphonic_20261009T005328Z/manifest.json` | dependency_manifest | có | `5dbc735830077af955df3893e2c55a2045ff3b104d9e9742b6da6943f13ebff7` |
| phase O: sed_rewindow_TF_f2_h5_20261009T034941Z | `ml/runs/sed_polyphonic_20261009T005328Z/checkpoints/best.pt` | best_checkpoint | có | `d18a03a79697fbf1d9db9ef576b85ff9c4fb4c2b6b86f68c0df76d96b4c46b05` |
| phase O: sed_rewindow_TF_f3_h5_20261009T035014Z | `ml/runs/sed_rewindow_TF_f3_h5_20261009T035014Z/manifest.json` | run_manifest | có | `5b939af0e41f2af57cc1ef77d109d98aa8fbd40405b5ff7436f2ca0216b61009` |
| phase O: sed_rewindow_TF_f3_h5_20261009T035014Z | `ml/runs/sed_rewindow_TF_f3_h5_20261009T035014Z/predictions/dev.npz` | prediction | có | `e5555a1b47d043b5a28930dcc126cc2dc9f29e4fb46f9a28546c0a70678dcd7c` |
| phase O: sed_rewindow_TF_f3_h5_20261009T035014Z | `ml/runs/sed_polyphonic_20261009T015949Z/manifest.json` | dependency_manifest | có | `5524006b790621c08977f7ae941942c2d28c0a0eab5a52a70e538b3287ae0d86` |
| phase O: sed_rewindow_TF_f3_h5_20261009T035014Z | `ml/runs/sed_polyphonic_20261009T015949Z/checkpoints/best.pt` | best_checkpoint | có | `673f0ea996bc5bc92204fcd49a7aae69616e9f0c1787485bcec5f10996c713ba` |
| phase O: sed_rewindow_TF_f4_h5_20261009T035045Z | `ml/runs/sed_rewindow_TF_f4_h5_20261009T035045Z/manifest.json` | run_manifest | có | `8ff0c3115241154f660bbfb024e37896630b0c8146a5e22add5520f796dd33e7` |
| phase O: sed_rewindow_TF_f4_h5_20261009T035045Z | `ml/runs/sed_rewindow_TF_f4_h5_20261009T035045Z/predictions/dev.npz` | prediction | có | `15e668b31aaddbf106fce3f254cf68a9e371d6928a67b45c31ba4cc6e2110103` |
| phase O: sed_rewindow_TF_f4_h5_20261009T035045Z | `ml/runs/sed_polyphonic_20261009T030150Z/manifest.json` | dependency_manifest | có | `a2cd571f1d65da7aaa08fd6d1745843f8d7a8703d537f6699997f28c2970131d` |
| phase O: sed_rewindow_TF_f4_h5_20261009T035045Z | `ml/runs/sed_polyphonic_20261009T030150Z/checkpoints/best.pt` | best_checkpoint | có | `e58fcdf5c20da365d7f9aa2e34bad33e58f39a3e975d83db8699c4b21248b83c` |
| phase O: sed_rewindow_TFKD_f0_h5_20261008T223935Z | `ml/runs/sed_rewindow_TFKD_f0_h5_20261008T223935Z/manifest.json` | run_manifest | có | `837005761cb77357bbbd39b5d9d272739ac3f48db38fb6aec6d8702f6e20bb84` |
| phase O: sed_rewindow_TFKD_f0_h5_20261008T223935Z | `ml/runs/sed_rewindow_TFKD_f0_h5_20261008T223935Z/predictions/dev.npz` | prediction | có | `2c2fd1fa9f0a65d4996f6a8aaf618125193d64cc57090c0f6677067976371ed2` |
| phase O: sed_rewindow_TFKD_f0_h5_20261008T223935Z | `ml/runs/sed_polyphonic_20261008T185245Z/manifest.json` | dependency_manifest | có | `1e6ce38ea54e5cf96b8247563735c21090f85309868b2c729dd5149d5d31305a` |
| phase O: sed_rewindow_TFKD_f0_h5_20261008T223935Z | `ml/runs/sed_polyphonic_20261008T185245Z/checkpoints/best.pt` | best_checkpoint | có | `b5512f9d01b9c9ebd73d26ee84dbf9c029d17a29446293a2a32a6a65070d9f2b` |
| phase O: sed_rewindow_TFKD_f1_h5_20261008T223959Z | `ml/runs/sed_rewindow_TFKD_f1_h5_20261008T223959Z/manifest.json` | run_manifest | có | `66827a4d5a90584609a6c4839c854dd4b23812fdadddd2ae4c865651e95701a1` |
| phase O: sed_rewindow_TFKD_f1_h5_20261008T223959Z | `ml/runs/sed_rewindow_TFKD_f1_h5_20261008T223959Z/predictions/dev.npz` | prediction | có | `da7b0fd286ac24ffb505bd7e499828e0a36ba2aaf1cd281c12d69d25a636a8e8` |
| phase O: sed_rewindow_TFKD_f1_h5_20261008T223959Z | `ml/runs/sed_polyphonic_20261008T193842Z/manifest.json` | dependency_manifest | có | `8f80f41febd784390e1cd476d332f665e9a533f64206bac86e35b6c8b9396562` |
| phase O: sed_rewindow_TFKD_f1_h5_20261008T223959Z | `ml/runs/sed_polyphonic_20261008T193842Z/checkpoints/best.pt` | best_checkpoint | có | `737dcf6f03a5cf5cd4b261502bb95db9d4e83606197ca30ccd2f8a9f8696d651` |
| phase O: sed_rewindow_TFKD_f2_h5_20261008T224023Z | `ml/runs/sed_rewindow_TFKD_f2_h5_20261008T224023Z/manifest.json` | run_manifest | có | `6adf07e70ecff26b10d84692f8357bfa37a6f19c0e104a11423960c95505c32a` |
| phase O: sed_rewindow_TFKD_f2_h5_20261008T224023Z | `ml/runs/sed_rewindow_TFKD_f2_h5_20261008T224023Z/predictions/dev.npz` | prediction | có | `937d4a9c9e70a790fd6fb1c13c9987fa1f02daf7218ededd2b6bef1c37a82e11` |
| phase O: sed_rewindow_TFKD_f2_h5_20261008T224023Z | `ml/runs/sed_polyphonic_20261008T202607Z/manifest.json` | dependency_manifest | có | `bdb97eb2ac8f2962ce7cbb68e58fd934952b656c57b21b197aea7ebcea39bcad` |
| phase O: sed_rewindow_TFKD_f2_h5_20261008T224023Z | `ml/runs/sed_polyphonic_20261008T202607Z/checkpoints/best.pt` | best_checkpoint | có | `be2c4bae6af85532d9c184cddd75fde7090facec619ca1b787b0421efcc95108` |
| phase O: sed_rewindow_TFKD_f3_h5_20261008T224049Z | `ml/runs/sed_rewindow_TFKD_f3_h5_20261008T224049Z/manifest.json` | run_manifest | có | `71506d31595d185d634268f4bff8f606a666e9bbcd3ef9278d63f09b35f23f7a` |
| phase O: sed_rewindow_TFKD_f3_h5_20261008T224049Z | `ml/runs/sed_rewindow_TFKD_f3_h5_20261008T224049Z/predictions/dev.npz` | prediction | có | `423f0667cadbcbb23766c08acc215e8a5fe2a0b5c3e64657ac91d6630eea4cc0` |
| phase O: sed_rewindow_TFKD_f3_h5_20261008T224049Z | `ml/runs/sed_polyphonic_20261008T211301Z/manifest.json` | dependency_manifest | có | `6dc7108aa306786f1fd8ea97659b5b524ec598f97a6396312a5d3ebd717dd330` |
| phase O: sed_rewindow_TFKD_f3_h5_20261008T224049Z | `ml/runs/sed_polyphonic_20261008T211301Z/checkpoints/best.pt` | best_checkpoint | có | `7e2e3f5214c90c41e1a477407f49273941ebfc7aecd6b1310ce9065b3cdea643` |
| phase O: sed_rewindow_TFKD_f4_h5_20261008T224114Z | `ml/runs/sed_rewindow_TFKD_f4_h5_20261008T224114Z/manifest.json` | run_manifest | có | `46e4e28faf5f0f656339f7d39fd90521185e74179f6e1b907c37677c61a374d5` |
| phase O: sed_rewindow_TFKD_f4_h5_20261008T224114Z | `ml/runs/sed_rewindow_TFKD_f4_h5_20261008T224114Z/predictions/dev.npz` | prediction | có | `91475de4e5826690448b9d9e7632c46c9a4ad50222423dcacade44b5bf73747a` |
| phase O: sed_rewindow_TFKD_f4_h5_20261008T224114Z | `ml/runs/sed_polyphonic_20261008T215900Z/manifest.json` | dependency_manifest | có | `e3e3164b9268d1013cd8de83748a219c69520dff6143717c59230d81de3cabda` |
| phase O: sed_rewindow_TFKD_f4_h5_20261008T224114Z | `ml/runs/sed_polyphonic_20261008T215900Z/checkpoints/best.pt` | best_checkpoint | có | `0cec04467c486cdf0c003e71e7d0ee73c29215f5fd62a8a3f26aeb2e0dee41d9` |
| phase O: sed_served_B0_20261107T175659Z | `ml/runs/sed_served_B0_20261107T175659Z/manifest.json` | run_manifest | có | `bfbd823207fb48d1b11575c77a36f765d4adf429b288979b905006bf9eb44c46` |
| phase O: sed_served_B0_20261107T175659Z | `ml/runs/sed_served_B0_20261107T175659Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `1610d24bc08a836896e60b8d2014225d80be2c77a083d1c5d4e0fb08d218cf10` |
| phase O: sed_served_B0_20261107T175659Z | `ml/runs/sed_polyphonic_20261008T092903Z/manifest.json` | dependency_manifest | có | `6154acde23ee7facb72b14bed6544d981cd5eca0d545587ca7241f228d10cee7` |
| phase O: sed_served_B0_20261107T175659Z | `ml/runs/sed_polyphonic_20261008T102530Z/manifest.json` | dependency_manifest | có | `53997a8bf3effdec70426a718c36a9e01d04d8912523744c5df6411d5c740e6f` |
| phase O: sed_served_B0_20261107T175659Z | `ml/runs/sed_polyphonic_20261008T111605Z/manifest.json` | dependency_manifest | có | `e70ff656db7ede7fbedf4c940fd1e5996487b4b9cef87f0264688d127a778b5e` |
| phase O: sed_served_B0_20261107T175659Z | `ml/runs/sed_polyphonic_20261008T115845Z/manifest.json` | dependency_manifest | có | `059e34a311fe0728e95c159819b51410bad9533e19a31a2f031c4c7e0a435089` |
| phase O: sed_served_B0_20261107T175659Z | `ml/runs/sed_polyphonic_20261008T123531Z/manifest.json` | dependency_manifest | có | `5cb5ae17ef3c5050494a042af4136d388a75066d5660f84036244b3046142183` |
| phase O: sed_served_B0_20261107T175659Z | `ml/runs/sed_polyphonic_20261008T092903Z/checkpoints/best.pt` | best_checkpoint | có | `b4117b20ec2db7a888f86d5dc7a6f7859d2b4e03f2ab75734f7e664c0bf04d08` |
| phase O: sed_served_B0_20261107T175659Z | `ml/runs/sed_polyphonic_20261008T102530Z/checkpoints/best.pt` | best_checkpoint | có | `13d49939c718dfbb5f4c9b6f9a54894ed2cf4a914147aac8c6a8a8322be8383b` |
| phase O: sed_served_B0_20261107T175659Z | `ml/runs/sed_polyphonic_20261008T111605Z/checkpoints/best.pt` | best_checkpoint | có | `fffead0ee1e0e142fbce0a562e4fb24bf7ee9b5bc47fbc67813f668d9e976e56` |
| phase O: sed_served_B0_20261107T175659Z | `ml/runs/sed_polyphonic_20261008T115845Z/checkpoints/best.pt` | best_checkpoint | có | `4f50d4fba9ce74bb0bb78e3bb26b6702f4aab805311e47af01e32ff959ae08bd` |
| phase O: sed_served_B0_20261107T175659Z | `ml/runs/sed_polyphonic_20261008T123531Z/checkpoints/best.pt` | best_checkpoint | có | `dc3f346fef30fe030dc6f361d5fafb352a0e58b23a3ed22277f69a0cb08be5f0` |
| checkpoint/cache ngoài | `artifacts/checkpoints/Cnn14_mAP=0.431.pth` | AudioSet_CNN14 | có | `7f0ea3a7ad9622f7bdc22439a750e04efdc1641bc4c930ff8727bb92d3141a69` |
| checkpoint/cache ngoài | `artifacts/checkpoints/BEATs_strong_1.pt` | BEATs | có | `db13a79ae90a0cfd0f9911a6a1d8cdb89324322bee642dcfe32de022123b8b54` |
| checkpoint/cache ngoài | `artifacts/checkpoints/frame_mn10_strong_1.pt` | frame_mn10 | có | `4a0fe320d5369987b772394c51881fb20a602967e6842f72f3e5c8181065ece7` |
| checkpoint/cache ngoài | `artifacts/llm/Qwen_Qwen3.5-9B-Q4_K_M.gguf` | Qwen_GGUF | có | `d784ce9eda1a5a7b51e8f705a9e6310844bf4f173654d115823c775fdea56d43` |
| checkpoint/cache ngoài | `artifacts/hf/models--BAAI--bge-m3` | tree | có | `3e942530b983ead63fecf1a36a34b8b581eccf464da7351e19c27f23ddb6b94c` |

## File nguồn đóng băng

| Đường dẫn | Tồn tại | SHA-256 |
|---|:---:|---|
| `data/splits/datased_polyphonic.frozen.json` | có | `c3d29189b5fcd3f407077d032cf48647dd731e695fa96e6b7e23a6f24861a1bf` |
| `data/splits/datased_trainval_folds.csv` | có | `eaa30dc17f59c73dcbc8f3c554f1ae29b8ac9a13eeb64876062beea27c67c733` |
| `ml/configs/taxonomy.yaml` | có | `67ca8a8c53278cd438d7d06a4ba09e277f3f9a6df99460bdbec1d3a927729a3a` |
| `ml/configs/caption_lexicon.yaml` | có | `184cdc6af18454a16b885f5cd8ece848c3e635df951f8edb1f8f1b794db2d578` |
| `ml/configs/caption_lexicon_vi.yaml` | có | `35ccf58cd888f53025bf7525e28bbaad0dc378ac912abdfd5e8bca886b67ac5e` |
| `ml/configs/caption_llm.yaml` | có | `94770dc649568c8b9617a9d1ced135e9abaf89a06a92dd4c92f44467937c91b8` |
| `ml/retrieval/query_set.py` | có | `3c406f0490a7a115c93af28725678761c11543bf3a285ebd55bd8620a9706a49` |
| `ml/captioning/constrained.py` | có | `469f2a2aca30839c0164ef13deb18aa845a21e5ff4f5b356019b9cace94f06ff` |
