# ADR-0045 — LBR: tinh chỉnh biên và chấm lại box học trên posterior OOF

**Status:** Accepted (người dùng duyệt kế hoạch 09/11/2026: "ta sẽ tiến hành theo kế hoạch mà bạn
đề ra"). Lượt mở test ở §8 **chờ người dùng duyệt riêng**.
**Date:** 2026-11-09

## Context

Giai đoạn O và P thay model (GRU, TF256, BEATs fine-tune, KD, thêm seed, cửa sổ 20 s, gain/EQ) nhưng
event-F1 OOF không vượt B0 (micro 0.2342, S53–S63), trong khi frame mAP lên tới 0.80. Thăm dò 09/11
bằng script nháp trên OOF B0 (PAPER_NOTES §5, dòng LBR; số sẽ sinh lại bằng script repo ở §9):

- Trong 2702 FN, 1477 event không có box cùng lớp. 789 trong số đó có posterior ≥ 0.9 trong span
  nhãn: box cSEBB tồn tại nhưng điểm (trung bình posterior) 0.8–0.9 < λ 0.9 và dài gấp 1.4–3.3 lần
  nhãn. 872 FN là lệch biên với box 1-1; onset dự đoán sớm, lớp dài lệch −1 đến −1.5 s.
- λ riêng theo lớp không giúp (0.2335); dịch onset toàn cục +0.1 s chỉ 0.2469.
- Trần: nếu biên của box 1-1 được sửa trong ±1 s, micro 0.4641.
- Bộ tinh chỉnh học (gradient boosting trên đường posterior quanh biên), cross-fit theo fold:
  0.3070; thêm chấm lại box (cross-fit lồng nhau) 0.3408; học trên OOF đơn model rồi áp lên OOF
  ensemble 3 seed P1: 0.3484.

Văn liệu cùng hướng: boundary-aware SED (RELATED_WORK §2.3 (15)) cho thấy lợi lớn nhất đến từ mô
hình hóa biên chứ không từ encoder. Chưa ai báo số SED trên DataSED (§2.3 (24)–(25)).

## Decision

### 1. Đầu vào (cố định)

- Posterior OOF `sed_oof_B0_h5_20261008T130849Z` (564 recording annotated, 5 fold
  `data/splits/datased_trainval_folds.csv`, nhóm theo `leakage_group`).
- Box ứng viên: cSEBB với tham số đã chọn của B0 (`step_filter_s` 0.32, `merge_abs` 0.3), giữ mọi
  box có điểm ≥ **0.5**.
- Nguồn train của refiner cuối: **chỉ B0 OOF** (người dùng chọn 09/11, phương án a). OOF P1×3
  (`sed_oof_P1_B0x3_h5_20261107T224434Z`) chỉ dùng kiểm độ vững ở §6.

### 2. Đặc trưng mỗi box (cho từng biên b ∈ {onset, offset})

- Meta (4 + 21): điểm box, độ dài box (s), onset (s), khoảng từ offset tới cuối recording (s),
  one-hot lớp.
- Posterior lớp của box tại t_b + k·0.08 s, k = −50…50 (101 giá trị, ±4 s), frame gần nhất;
  ngoài recording ghi −1.
- Max posterior của 20 lớp còn lại tại cùng vị trí, lấy mỗi 5 điểm (21 giá trị).

### 3. Đích và mô hình

- Box chồng lấn ≥ 1 event nhãn cùng lớp: Δ_on = onset của event chồng lấn có onset gần onset box
  nhất − onset box; Δ_off tương tự với offset. Chỉ dùng khi |Δ| ≤ 4 s.
- **Refiner:** hai `HistGradientBoostingRegressor` (loss `absolute_error`, `max_iter` 300,
  `learning_rate` 0.05, `max_leaf_nodes` 31, `min_samples_leaf` 20, `early_stopping` False,
  `random_state` 20260922). Áp: onset' = max(0, onset + Δ̂_on), offset' = offset + Δ̂_off; nếu
  offset' ≤ onset' + 0.04 thì offset' = onset' + 0.04.
- **Rescorer** (chỉ V2): `HistGradientBoostingClassifier` cùng siêu tham số. Đặc trưng = đặc trưng
  onset ⊕ phần đường cong của đặc trưng offset ⊕ Δ̂_on ⊕ Δ̂_off. Nhãn = box sau tinh chỉnh khớp một
  event nhãn cùng lớp theo tiêu chí chính (onset ±0.2 s, offset ±max(0.2 s, 0.2·L)), xét từng box
  độc lập.
- Không tune siêu tham số. Mọi giá trị trên là giá trị của lượt thăm dò.
- **Bổ sung 10/11 (trước khi có số tầng C):** sau khi lọc ngưỡng, các box giữ lại **cùng lớp giao
  hoặc chạm nhau được gộp** (onset nhỏ nhất, offset lớn nhất, điểm lớn nhất). Lượt tầng C đầu tiên
  dừng ở bước chọn ngưỡng đầu tiên của V1 vì `psds_eval` từ chối bảng có event cùng lớp chồng nhau —
  box tinh chỉnh có thể giãn vào nhau. Chưa có số nào được sinh; bản thăm dò không gộp.

### 4. Ứng viên và điểm vận hành

| # | Ứng viên | Điểm vận hành F1 (chính) | Điểm ưu tiên phát hiện (ADR-0046 §3) |
|---|---|---|---|
| V1 | Refiner, lọc theo điểm box | λ ∈ {0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95} | cùng lưới λ |
| V2 | Refiner + rescorer | t ∈ {0.005, 0.01, 0.02, …, 0.09, 0.10, 0.15, …, 0.85} | cùng lưới t |

Điểm F1 = micro event-F1 cao nhất trên các fold fit; điểm ưu tiên phát hiện theo ADR-0046 §3.

### 5. Cross-fit (tầng C)

Với mỗi fold ngoài k: refiner train trên các fold ≠ k. V2 lồng nhau: Δ̂ của fold j ≠ k từ refiner
train trên các fold ∉ {j, k}; rescorer học trên 4 fold fit với các Δ̂ đó; ngưỡng t chọn trên xác suất
OOF trong của rescorer; refiner cuối train trên 4 fold, rescorer cuối trên 4 fold, áp lên fold k.
Nhãn fold k không được dùng ở bất kỳ bước nào. Có test chứng minh điều này (§9).

### 6. Luật tầng C

- So với B0 OOF (0.2342) trên cùng recording/fold; bootstrap ghép cặp theo recording 1000 lần, seed
  20260922 (`ml.evaluation.multirun.paired_branch_bootstrap`).
- Đạt khi cận dưới CI 95% của Δ micro > 0 **và** kiểm độ vững cũng đạt: refiner/rescorer học trên B0
  OOF, áp lên P1×3 OOF, Δ so với P1×3 baseline có cận dưới > 0.
- Chọn micro cao nhất trong các ứng viên đạt; hòa (chênh < 0.005) thì chọn V1 (đơn giản hơn).
  Không ứng viên nào đạt → giữ B0, không mở test.
- Hạn: tầng C xong trước **18/11** (ADR-0043 §1).

### 7. Model cuối cho test

Fit trên đủ 5 fold OOF theo đúng quy trình §5, với 5 fold đóng vai fold fit (Δ̂ cho rescorer lấy từ
refiner 5 fold OOF; ngưỡng chọn trên xác suất OOF 5 fold). Lưu model kèm SHA-256 trong manifest run
`sed_lbr_<label>_<ts>`; chỉ nạp artifact do repo sinh và kiểm SHA trước khi nạp.

### 8. Test một lần (chờ duyệt riêng)

Áp model cuối lên posterior test của `sed_ensemble_B0_final_test_20261014T085016Z` (cùng tham số
cSEBB). Một lượt `evaluate_run --eval-set annotated`, tính cả hai điểm vận hành đã ghi trước; báo
macro trước micro, CI bootstrap, PSDS (quét lưới ngưỡng của ứng viên), và thước ứng dụng ADR-0046.
Bootstrap ghép cặp với B0 test. Ghi sổ test. Không chọn lại theo số test.

### 9. Mã nguồn

- `ml/postprocessing/boundary_refine.py` (torch-free): đặc trưng, đích, fit/predict, rescorer, áp.
- `scripts/fit_lbr_oof.py`: cross-fit, model cuối, manifest có `environment`.
- `report_oof` nhận họ `lbr`; `evaluate_run` nhận `family="lbr"`.
- Test: đệm biên recording, dấu Δ, **đổi nhãn fold held-out không đổi dự đoán của fold đó**, tất
  định, nạp model sai SHA bị từ chối.
- Script chẩn đoán sinh lại số ở Context: phân rã FN, posterior trong span bỏ sót, trần sửa biên.

### 10. Kết quả tầng C (09/11, `sed_lbr_B0_20261109T172809Z`, tree sạch `71b5a55`)

Nguồn: [oof_selection_20261109_LBR.md](../measurements/oof_selection_20261109_LBR.md),
[lbr_diagnosis_20261109.md](../measurements/lbr_diagnosis_20261109.md).

| Thước chính, 21 lớp, điểm F1 | Macro | Micro | Δ micro [95% CI] |
|---|---:|---:|---|
| B0 | 0.1797 | 0.2342 | — |
| V1 | 0.2343 | 0.3043 | +0.0701 [+0.0496, +0.0896] |
| **V2** | **0.2454** | **0.3332** | **+0.0990 [+0.0761, +0.1200]** |
| V2 áp lên P1×3 (kiểm chuyển) | 0.2622 | 0.3505 | +0.1160 [+0.0933, +0.1373] so P1×3 |

- Cả hai ứng viên đạt luật §6 ở nguồn và kiểm chuyển; **chọn V2** (micro cao nhất, hơn V1 > 0.005).
  Model cuối SHA-256 `e2d84c09…`, ngưỡng f1 0.01, recall_first 0.005.
- **Đánh đổi ghi nguyên văn:** V2 giảm segment-F1 1 s (0.7007 → 0.5684) và recall theo giao nhau
  (0.5495 → 0.4866): rescorer học "box có biên đúng collar 0.2 s" nên loại box chồng đúng nhưng lệch
  biên. Ở điểm ưu tiên phát hiện, ngưỡng V2 chạm đáy lưới (0.005) ở 5/5 fold; ngưỡng V1 chạm đáy
  λ_min 0.5 ở 5/5 fold — lưới, không phải dữ liệu, giới hạn điểm này. V1 ở điểm ưu tiên phát hiện
  cho recall giao nhau cao nhất (0.8339, P 0.6402) nhưng không phải ứng viên được chọn.
- Model cuối áp in-sample lên chính OOF cho micro 0.50 — chỉ kiểm đường ống; khoảng cách so với
  cross-fit (0.33) là mức overfit của GBM trên dữ liệu đã thấy.
- Chưa mở test.

### 11. Bổ sung 10/11 — cấu hình ứng dụng V3 (người dùng duyệt, ghi trước khi mở test)

**Vì sao.** §10 cho thấy V2 thắng thước chính nhưng không phục vụ được mục tiêu "phát hiện nhiều nhất"
của ADR-0046: rescorer của V2 học nhãn biên 0.2 s nên loại box chồng đúng mà lệch biên, và điểm ưu
tiên phát hiện của V2 chạm đáy lưới.

**V3** giữ nguyên refiner, đặc trưng, lưới t, cross-fit và hai điểm vận hành của V2. Chỉ đổi nhãn
của rescorer sang "giao nhau": box giao một event cùng lớp ≥ 10% thời lượng của cả box lẫn event
(`matches_intersection`, gần DTC/GTC 0.1 của thước giao nhau).

**Vai trò, ràng buộc.**
- V3 **không** qua luật §6 và không thay V2. Số chính của luận văn vẫn là V2.
- V3 là cấu hình ứng dụng: mặc định cho demo ở chế độ `recall_first`.
- V3 được tìm ra **sau** khi xem kết quả tầng C trên chính OOF này. Đây là lựa chọn hậu nghiệm
  trên OOF (không trên test) và phải ghi như vậy trong Hạn chế.
- V3 được chấm cùng lượt mở test với V2 (`evaluate_run --extra-lbr`), không mở test riêng.
- Không chọn lại giữa V2 và V3 theo số test.

**Số OOF** (bản xem trước chạy lúc tree bẩn, trùng từng chữ số với lượt thăm dò; run chính thức
chạy lại trên tree sạch theo `docs/notes/test_once_lbr.md` bước 1):

| 21 lớp | Micro chính | Segment 1 s | Giao nhau P | Giao nhau R | Giao nhau F1 |
|---|---:|---:|---:|---:|---:|
| B0, điểm F1 | 0.2342 | 0.7007 | 0.9476 | 0.5495 | 0.6956 |
| B0, điểm ưu tiên phát hiện | 0.1811 | 0.7776 | 0.6275 | 0.7799 | 0.6955 |
| V2, điểm F1 (§10) | 0.3332 | 0.5684 | — | 0.4866 | — |
| **V3, điểm F1** | 0.3058 | 0.7693 | 0.9591 | 0.6697 | 0.7887 |
| **V3, điểm ưu tiên phát hiện** | 0.2302 | 0.7594 | 0.6744 | **0.8336** | 0.7456 |
| V3 áp lên P1×3, ưu tiên phát hiện | 0.2582 | 0.7738 | 0.7710 | 0.8175 | 0.7936 |

- Δ micro thước chính so B0: V3 +0.0716 [+0.0489, +0.0917]; trên P1×3 +0.0816 [+0.0602, +0.1021].
- 19 lớp Việt Nam, V3 ưu tiên phát hiện: recall giao nhau 0.8379, P 0.6736.
- **Giới hạn của lưới, ghi nguyên văn:** ngưỡng V3 ở 5/5 fold là 0.85 (trần lưới t) cho điểm F1 và
  0.005 (đáy lưới) cho điểm ưu tiên phát hiện. Cả hai điểm đều bị lưới chặn. Không mở rộng lưới sau
  khi đã xem số này; mở rộng là việc của một lần ghi trước mới.

Mã: `matches_intersection` (`ml/postprocessing/boundary_refine.py`), `ALL_VARIANTS`/`RESCORER_LABELS`
(`lbr_crossfit.py`), `scripts/fit_lbr_application.py`, `evaluate_run --extra-lbr`.

### 12. Kết quả test (10/11, lượt mở test một lần, commit `98315fd`)

Một lượt `evaluate_run --extra-lbr`, test annotated n=139, nguồn
`sed_ensemble_B0_final_test_20261014T085016Z`, hai run LBR đóng băng. Nguồn:
[báo cáo](../measurements/sed_ensemble_B0_final_test_20261014T085016Z_eval_phase_lbr_annotated.md).

| 21 lớp, test | Macro | Micro | Nsys/Nref | Giao nhau R | Giao nhau P | Segment 1 s |
|---|---:|---:|---:|---:|---:|---:|
| B0 | 0.1366 | 0.1806 | 345/740 | 0.5351 | 0.9706 | 0.7260 |
| **V2, điểm f1 (số chính)** | **0.2356** | **0.2965** | 373/740 | 0.5108 | 0.9545 | 0.5965 |
| V3, điểm f1 | 0.1955 | 0.2731 | 395/740 | 0.6486 | 0.9836 | 0.7752 |
| V3, recall_first (demo) | 0.1754 | 0.2287 | 668/740 | **0.8203** | 0.7812 | 0.7821 |

- Δ micro so B0 (ghép cặp theo recording): V2 **+0.1159 [+0.0741, +0.1593]**; V3 f1 +0.0925
  [+0.0549, +0.1331]. CI không chạm 0.
- Hướng OOF được giữ trên test: V2 tăng thước chính và giảm độ phủ (recall giao nhau 0.5351 → 0.5108,
  segment-F1 0.7260 → 0.5965); V3 recall_first tăng recall giao nhau 0.5351 → 0.8203 với precision
  0.7812. 19 lớp Việt Nam, V3 recall_first: recall 0.8319, P 0.7810.
- Không chọn lại V2/V3 theo số test; V2 vẫn là số chính, V3 là cấu hình ứng dụng.
- PSDS ở lượt này tính trên `T_GRID` cũ (V2 0.2146 / 0.2960 so với B0 0.3489 / 0.6987). Lưới này cắt
  phần lớn box của V2; đo lại có ghi trước ở [ADR-0047](ADR-0047-rq2-rq3-tren-event-lbr.md) (bổ sung
  lưới PSDS): V2 0.3512 / 0.6116, V3 0.3369 / 0.6167. PSDS-2 của V2 vẫn thấp hơn B0.
- Sổ test: [test_ledger_20261110.md](../measurements/test_ledger_20261110.md); freeze:
  [artifact_freeze_20261110.md](../measurements/artifact_freeze_20261110.md), thiếu 0 artifact.

## Alternatives considered

1. λ riêng theo lớp trên cSEBB: đo được 0.2335, không tăng.
2. Dịch onset/offset toàn cục: 0.2469, nhỏ hơn hẳn LBR.
3. Hạ λ không tinh chỉnh: thêm box nhưng biên sai nên F1 không tăng.
4. Train lại với loss onset/offset hoặc EPN (boundary-aware SED): cần GPU, đổi recipe phải qua tầng
   S/C; O-E1 (RED không EPN) đã âm tính; không kịp mốc 18/11.
5. Train refiner trên hợp B0 + P1×3: chưa đo; để làm kiểm độ vững thay vì nguồn chính.

## Consequences

- Thêm họ hậu xử lý `lbr`. Nếu phục vụ, image inference cần `scikit-learn`.
- Thêm một lượt mở test cho SED (sau O5); báo rõ là lần tái sử dụng thích nghi.
- Caption/RAG đang dựng trên event B0 cSEBB; đổi sang LBR cần chạy lại S8-lite (thêm lượt test
  W5/W6) — không thuộc ADR này.

## Evidence cần kiểm lại

- **Rủi ro chọn lối thăm dò:** thiết kế đặc trưng, siêu tham số và lưới được thăm dò trên chính OOF
  này; số OOF có thể lạc quan. Test là phép xác nhận sạch duy nhất.
- Lệch phân phối: test là ensemble 5 model fold, refiner học trên OOF đơn model (kiểm bằng P1×3 ở §6).
- LBR học quy ước gán biên riêng của DataSED; không suy ra tổng quát cho dataset khác.
- Số thăm dò ở Context phải khớp số do script repo sinh; lệch thì ghi nguyên văn và dùng số repo.
