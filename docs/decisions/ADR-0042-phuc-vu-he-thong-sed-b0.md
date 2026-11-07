# ADR-0042 — Phục vụ hệ thống SED cuối giai đoạn O (B0)

**Status:** Accepted
**Date:** 2026-11-08

## Context

ADR-0041 §11 khóa B0 bằng OOF tầng C trước khi mở test; §12 đã đánh giá test đúng một lần:
macro 0.1366, micro 0.1806 (f2: 0.1206 / 0.1643; Δ micro +0.0164 [−0.0128, +0.0495]). B0 =
T2b + `--train-fixes`, ensemble 5 model fold, **suy luận cửa sổ chồng lấn hop 5 s gộp tam giác
sàn 0.3**, cSEBB `tau0.32_abs0.3` chọn trên OOF. Tầng phục vụ (ADR-0039) chỉ chạy cửa sổ không
chồng lấn của f2, nên phục vụ B0 nguyên trạng sẽ khác hệ thống đã đo. Người dùng duyệt O6
ngày 08/11.

## Decision

1. Manifest hệ thống phục vụ có thể khai `config.serving = {hop_seconds, window_weighting}`;
   `ServedSed` cắt cửa sổ theo hop đó và gộp bằng đúng `stack_predictions_by_recording` có trọng
   số như artifact đã đánh giá. Không có khóa này thì hành vi cũ giữ nguyên (f2 và mọi hệ thống
   trước).
2. Hệ thống mặc định/chính thức: `ml/runs/sed_served_B0_20261107T175659Z`, dựng bằng
   `scripts.build_served_system` từ 5 run fold `sed_polyphonic_20261008T092903Z`, `102530Z`,
   `111605Z`, `115845Z`, `123531Z`; file hậu xử lý là bản sao nguyên byte của
   `sed_oof_B0_h5_20261008T130849Z/sebb_cv_selection_annotated.json`, SHA-256 ghi trong manifest.
3. Parity so với artifact test đã đánh giá `sed_ensemble_B0_final_test_20261014T085016Z`
   (`inference_parity_sed_served_b0_20261107t175659z_cuda_20261107`): 142/142 recording đúng số
   frame; xác suất lệch tối đa 0.00203 (trung vị 0.000506); **351/352 event trùng khít**, 1 event
   của `S-0048` lệch quá collar. Lệch số học do phục vụ chạy batch 8 còn lúc dump dùng batch 24
   (cuDNN cộng khác thứ tự); cùng mức với parity CPU của f2 (294/299 trong collar). Đây là phép đo
   tái tạo, không phải đánh giá lại.
4. Rollback: đặt `EARAG_SERVED_RUN=ml/runs/sed_ensemble_t2b_20260927T200914Z` (f2); override luôn
   cho `official=false`.

## Alternatives considered

| Phương án | Lý do không chọn |
|---|---|
| Phục vụ B0 với cửa sổ không chồng lấn | Không phải hệ thống đã đo; ADR-0041 §7 đưa suy luận chồng lấn vào chính định nghĩa B0 |
| Giữ f2 cho demo | Demo sẽ công bố hệ thống khác hệ thống cuối được báo cáo |
| Chạy dump test lại với batch 8 để parity trùng bit | Mở test thêm một lần chỉ để làm đẹp parity; không đổi kết luận |

## Consequences

Phục vụ tải 5 checkpoint Frame-MobileNet (khoảng 5 × 12 MB) và chạy gấp khoảng 2 lần số cửa sổ
so với f2 (hop 5 s), cộng 5 model thay vì 3. RQ2/RQ3 trên B0 chạy lại ở S8-lite; các số W5/W6
trên f2 giữ nguyên làm kết quả lịch sử.
