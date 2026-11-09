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
