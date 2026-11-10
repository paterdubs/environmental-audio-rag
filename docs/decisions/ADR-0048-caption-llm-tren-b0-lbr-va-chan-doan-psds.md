# ADR-0048 — Caption LLM (RQ2) trên event B0/LBR, chẩn đoán PSDS v1/v2 trên dev, PSDS B0 cùng lưới

**Status:** Accepted (người dùng duyệt kế hoạch 10/11/2026: "tôi duyệt theo như những gì bạn đề
xuất" — gồm lượt mở test thứ tư cho W5, đo PSDS B0 trên test bằng lưới log, dùng lại mức oracle
từ S8, chạy cả B0/V2/V3)
**Date:** 2026-11-10

## Context

1. **RQ2 với LLM chỉ có số trên f2** (ADR-0040). Hệ thống cuối là B0 (ADR-0041 §12) và LBR
   (ADR-0045 §12: V2 `f1` số chính, V3 `recall_first` demo); ADR-0044 và ADR-0047 chỉ chạy lại
   caption **template**. Người dùng chọn chạy lại ba nhánh LLM thay vì ghi hạn chế.
2. `generate_llm_captions` chưa nhận event LBR: `e2e_timelines` có `lbr_point` nhưng CLI không có
   cờ, và meta chỉ ghi `postproc.name` — mọi postproc LBR đều tên `manifest.json`, nên provenance
   không phân biệt được hệ thống.
3. **PAPER_NOTES §6 #8 (S21) còn mở:** v2 tăng event-F1 so với v1 nhưng PSDS-1/2 trên test không
   tăng (0.3447 / 0.6744 so với 0.3489 / 0.6987, `evaluation_cv.json`). ADR-0047 cho thấy lưới ngưỡng
   PSDS có thể quyết định PSDS (S66), nên lưới là một giả thuyết cần kiểm, cùng các giả thuyết khác.
4. **Lỗi trích số phát hiện 10/11:** tài liệu ngày 10/11 ghi PSDS của B0 trên test là 0.3489 /
   0.6987 — đó là số của ensemble C v1. Số đúng của B0 (test annotated, lưới tuyến tính
   `DEFAULT_THRESHOLD_GRID`, `evaluation_phase_o_annotated.json`) là **0.3131 / 0.7310**. Ngoài ra số
   của B0 tính trên lưới tuyến tính, còn số LBR "mới" tính trên lưới log: hai số không cùng thước.

## Decision

### 1. Caption LLM trên B0, V2, V3 (lượt mở test thứ tư cho W5)

**Đầu vào** — đúng như caption template của ADR-0044/0047:

| Nhãn | Split | `run_dir` (nơi ghi `captions/`) | Posterior | Postproc | Điểm |
|---|---|---|---|---|---|
| `B0` | dev | `sed_filtered_B0_oof_dev_20261107T181008Z` | chính nó | `…/sebb_cv_selection_annotated.json` | — |
| `lbrv2` | dev | `sed_lbr_oofevents_sed_lbr_B0_20261109T172809Z_f1_20261110T062901Z` | `sed_filtered_B0_oof_dev_20261107T181008Z` | `…/manifest.json` (event cross-fit) | `f1` |
| `lbrv3` | dev | `sed_lbr_oofevents_sed_lbr_B0v3_20261110T042337Z_recall_first_20261110T063606Z` | như trên | `…/manifest.json` | `recall_first` |
| `B0` | test | `sed_ensemble_B0_final_test_20261014T085016Z` | chính nó | `sed_oof_B0_h5_20261008T130849Z/sebb_cv_selection_annotated.json` | — |
| `lbrv2` | test | `sed_lbr_B0_20261109T172809Z` | `sed_ensemble_B0_final_test_20261014T085016Z` | `sed_lbr_B0_20261109T172809Z/manifest.json` | `f1` |
| `lbrv3` | test | `sed_lbr_B0v3_20261110T042337Z` | như trên | `sed_lbr_B0v3_20261110T042337Z/manifest.json` | `recall_first` |

Mỗi cặp (nhãn, split) có `run_dir` riêng nên file `captions/<nhánh>_<split>.jsonl` không đè nhau.
Thư mục `captions/` là phần **thêm vào** run đóng băng; không file đóng băng nào bị sửa (kiểm bằng
`freeze_artifacts`).

**Giữ nguyên:** model Qwen3.5-9B Q4_K_M (SHA-256 trong `caption_llm.yaml`), llama.cpp b11158 với
`-c 4096 -np 1`, prompt (`PROMPT_VERSION`), grammar constrained v1.2 / cover v1, ngân sách token
ADR-0023 §7, lexicon EN đóng băng ADR-0022 (`--frozen-lexicon-sha256`), tham số sinh greedy.

**Chỉ sinh mức `e2e`** (`--levels e2e`). Mức `oracle` dựng từ ground truth nên không phụ thuộc hệ
thống SED: dùng lại caption oracle đã sinh ở S8 (`sed_ensemble_s13_f2_20260929T045053Z/captions/`).
Script tổng hợp **kiểm** timeline oracle của S8 trùng khít timeline oracle dựng lại cho đúng tập
recording; lệch thì không dùng lại và báo.

**Kiểm token trên dev (trước hàng đợi, không đọc test)** — đếm bằng `/apply-template` +
`/tokenize` của server: B0 và V2 tối đa prompt 748 + ngân sách 1688 = 2436 token. V3 tối đa
S-0279 (38 event): prompt 1428 + ngân sách theo ký tự 3414 = 4842 > 4096; ngân sách là trần theo
ký tự, caption dài nhất grammar cho phép là 1053 token chuẩn. **Ghi trước cách xử lý:** không đổi
`-c`, `max_tokens` hay grammar. Caption dừng vì hết context hay hết `max_tokens` đều tính là bị
cắt (`finish_reason = length`), báo số lượng như một kết quả. Nếu một request **lỗi** (HTTP lỗi,
server từ chối), hàng đợi dừng và chờ người dùng quyết.

**Thứ tự (hàng đợi, mỗi bước kiểm `git status --porcelain` rỗng và mã thoát):**

1. Dev: `B0` → `lbrv2` → `lbrv3`; mỗi nhãn chạy `unconstrained` → `constrained` →
   `constrained_cover`, mỗi file một lượt liền (llama.cpp chỉ tất định theo chuỗi request).
2. **Cổng dev tự động:** mỗi file đủ 134 caption; ba nhánh cùng timeline (script tự kiểm,
   `check_same_timelines`); không request lỗi. Caption bị cắt không làm trượt cổng nhưng được ghi.
3. Test: cùng thứ tự, với `--frozen-lexicon-sha256`.

**Chấm và báo:** `score_captions` (`--eval-set annotated` là số chính; test báo thêm `all` làm độ
nhạy), `report_caption_per_class`, `report_caption_ngram` (tham khảo). Bảng tổng hợp mới
`scripts.report_rq2_llm_systems`: theo nhánh × hệ thống (f2 từ S8, B0, V2, V3), CI bootstrap theo
recording, hiệu số cặp so với f2 và so với B0 trên recording chung. **Không chọn hay đổi gì** từ
các số này (hệ thống phục vụ, nhánh caption, lexicon đều giữ).

### 2. Chẩn đoán PSDS v1/v2 — chỉ dev (S21)

**Hệ thống**, mỗi cái với hậu xử lý đã khóa:

| Nhãn | Posterior dev | Hậu xử lý | Ghi chú |
|---|---|---|---|
| `v1` | `sed_ensemble_C_clean_20260925T045631Z` | `postproc_cv.json` (θ global) | cấu hình có số test ở S21 |
| `v2` | `sed_ensemble_v2_20260926T155630Z` | `sed_ensemble_v2_20260926T150934Z/postproc_cv.json` | như S21 (`dev.npz` trùng hash, ADR-0035) |
| `f2` | `sed_ensemble_t2b_20260927T200914Z` | `sebb_cv_selection_annotated.json` (cSEBB) | bối cảnh |
| `B0` | `sed_filtered_B0_oof_dev_20261107T181008Z` | `sebb_cv_selection_annotated.json` | bối cảnh, posterior OOF |

`v1`, `v2`, `f2` là dev **in-sample** đối với ngưỡng/hậu xử lý đã chọn; PSDS quét toàn dải ngưỡng
nên ít phụ thuộc điểm đã chọn hơn event-F1, nhưng vẫn ghi rõ. Eval set chính `annotated` (134),
báo kèm `all` (137).

**Đo:** PSDS-1/2 trên lưới tuyến tính (`DEFAULT_THRESHOLD_GRID`, như `evaluate_run`) và lưới log
(`PSDS_GRID_LOG = geomspace(1e-5, 0.99, 48)`, ADR-0047); PSDS với `alpha_st = 0`; biến thể PSDS-1
với DTC = GTC = 0.5; TPR trung bình các lớp tại eFPR ∈ {5, 10, 30, 60, 100}/giờ; AUC theo lớp; vị
trí điểm vận hành đã chọn (eFPR, TPR); số event GT không được bắt ở bất kỳ điểm lưới nào.

**Luật ghi trước.** Δ = PSDS(v2) − PSDS(v1) theo cấu hình chuẩn (lưới tuyến tính).

- **Điều kiện tiên quyết:** dev tái hiện hiện tượng S21 — event-F1 dev v2 > v1 và Δ ≤ 0 ở ít nhất
  một trong PSDS-1/2. Không tái hiện → kết luận "dev không tái hiện S21", không diễn giải giả
  thuyết nào.
- **H1 (lưới cắt đường cong):** đủ điều kiện nếu trên lưới log Δ đổi dấu hoặc |Δ| giảm ≥ 50%.
- **H2 (lợi ích chỉ quanh điểm vận hành):** đủ điều kiện nếu TPR v2 ≥ v1 tại mọi eFPR ≤ eFPR của
  điểm v2 đã chọn, và TPR v2 < v1 tại ít nhất một nửa các eFPR lớn hơn.
- **H3 (phạt độ lệch giữa lớp, `alpha_st`):** đủ điều kiện nếu với `alpha_st = 0` Δ đổi dấu hoặc
  |Δ| giảm ≥ 50%.
- **H4 (tiêu chí giao nhau chặt):** đủ điều kiện nếu với DTC = GTC = 0.5 Δ của PSDS-1 đổi dấu hoặc
  |Δ| giảm ≥ 50%.
- Báo mọi giả thuyết, kể cả không đủ điều kiện. "Đã giải thích S21" chỉ khi ít nhất một giả thuyết
  đủ điều kiện; nếu không, ghi "chưa giải thích được trên dev". Không quay lại sửa luật sau khi xem số.

### 3. PSDS của B0 trên test bằng lưới log (một lượt chạm test, chỉ PSDS)

`report_lbr_psds_grid` thêm tùy chọn chấm B0: box cSEBB từ posterior
`sed_ensemble_B0_final_test_20261014T085016Z/predictions/test.npz` và postproc
`sed_oof_B0_h5_20261008T130849Z/sebb_cv_selection_annotated.json` (đúng cấu hình O5), annotated
n=139, trên **cả hai** lưới. Kiểm toàn vẹn: số trên lưới tuyến tính phải trùng 0.3131178… /
0.7309525… của `evaluation_phase_o_annotated.json`; lệch thì dừng. Lưới log là đúng
`PSDS_GRID_LOG`, không thử lưới khác. Không chọn gì; chỉ để bảng B0 ↔ LBR cùng thước.

### 4. Sửa số trích sai

Bảy chỗ ghi B0 = 0.3489 / 0.6987 (CLAUDE §3 và §10, STATUS, PAPER_NOTES S66, ADR-0045 §12,
ADR-0047 hai chỗ) được sửa theo artifact, kèm ghi rõ lưới. Thêm `docs/claims.yaml` +
`scripts.check_doc_claims`: đối chiếu số chính trong tài liệu với artifact, chạy trước commit tài
liệu.

## Alternatives considered

| Phương án | Lý do không chọn |
|---|---|
| Giữ số LLM trên f2, ghi hạn chế | Người dùng chọn chạy lại |
| Sinh lại cả mức oracle | ~7 giờ GPU thêm; oracle không phụ thuộc hệ thống SED, kiểm trùng khít đủ |
| Chỉ V2 hoặc chỉ B0 | B0 là hệ thống nền, V2 số chính, V3 demo — người dùng chọn cả ba |
| Nâng `-c` lên 8192 cho V3 | Đổi cấu hình runtime đã khóa; kiểm token dev cho thấy thực tế vừa |
| Chẩn đoán S21 trên test | Chạm test để giải thích, không cần; dev đủ để kiểm giả thuyết |
| Đo lại PSDS v1/v2 trên test bằng lưới log | Thêm hai lượt chạm test không phục vụ quyết định nào |

## Consequences

Sổ test thêm 9 file caption test (ba nhánh × ba hệ thống, mức e2e; dev cũng 9 file), một lượt
PSDS B0. Freeze phải
thêm caption mới. Số RQ2 của báo cáo cuối dùng B0/V2/V3; số f2 giữ làm mốc. Nếu V3 có caption bị
cắt, đó là giới hạn của ngân sách sinh khi timeline dày, ghi vào hạn chế, không sửa.

## Bổ sung 10/11 (đêm) — giới hạn event mỗi điểm vận hành của chẩn đoán PSDS (ghi trước lượt chạy)

Hai lượt chẩn đoán đầu tiên dừng vì `MemoryError` (4–7 GiB) trong `psds_eval` khi dựng evaluator cho
f2; **chưa có số nào được ghi hay xem** (script dừng trước khi ghi file). Đo số event theo ngưỡng
trên dev annotated (chỉ đếm): cSEBB của f2 cho 161,527 box ở ngưỡng 1e-5 và 50,786 ở 0.01 (độ phân
giải 40 ms, không làm mượt chồng lấn); B0 5,694; v1 2,805; v2 2,807. `psds_eval` nối event × nhãn
theo từng recording nên chi phí tăng theo bình phương số box.

**Quy tắc cố định:** mọi hệ thống, mọi lưới — điểm vận hành có **hơn 50,000 event** bị bỏ, và số
điểm bị bỏ được ghi ở mỗi ô (`n_skipped_over_cap`). Chỉ f2 bị ảnh hưởng (các ngưỡng thấp), nên PSDS
của f2 là PSDS của đường cong cụt ở phía eFPR cao, không so thẳng với số khác; f2 chỉ là hệ thống
bối cảnh, không nằm trong luật H1–H4 (chỉ v1 và v2). Không đổi luật H1–H4, lưới hay kịch bản.
Chạy tuần tự từng lượt (annotated rồi all), không song song với llama.cpp.

## Kết quả 11/11

**§1 Caption LLM.** 18 file caption (dev 9, test 9), tất cả `dirty=False`, 0 caption bị cắt, cổng dev đạt. Test annotated n=139, omission:

| Nhánh | f2 | B0 | V2 | V3 |
|---|---:|---:|---:|---:|
| unconstrained | 0.005 | 0.000 | 0.004 | 0.023 |
| constrained | 0.012 | 0.013 | 0.007 | 0.081 |
| constrained-cover | 0.000 | 0.000 | 0.000 | 0.000 |

Hallucination ≤ 0.022 và từ cấm 0 ở mọi nhánh LLM; template EN/VI 0 lỗi. Với V3 nhánh constrained bỏ sót nhiều lớp hơn (V3 − f2 +0.069 [+0.041, +0.097]) — hiệu ứng timeline dày; cover giữ 0. Chi tiết [rq2_llm_systems_20261110_test_annotated](../measurements/rq2_llm_systems_20261110_test_annotated.md).

Ghi nhận trung thực: (1) llama-server gặp CUDA out of memory khi sinh constrained_cover của V3 trên dev (GPU còn bị tiến trình khác chiếm), khởi động lại và chạy lại đúng file đó — chuỗi request sau lần khởi động lại khác chuỗi trước; (2) lần chấm đầu ghi `dirty=true` vì file sinh giữa chừng (như S13), đã xóa và chấm lại với đầu ra ngoài repo; (3) kiểm token dev trước khi chạy cho thấy V3 có thể vượt context 4096 ở timeline 38 event, nhưng không caption nào bị cắt thực tế.

**§2 Chẩn đoán PSDS.** Xem PAPER_NOTES S68: tái hiện S21 ở PSDS-2 (Δ −0.0078) nhưng không ở PSDS-1 (+0.0114); H1 và H3 đủ điều kiện, H2 không. Đường tới đó có một lần sửa trước khi chạy: `MemoryError` trong `psds_eval` với cSEBB của f2 (161,527 box) → quy tắc bỏ điểm >50,000 event (bổ sung ở trên, ghi trước, chưa xem số).

**§3 PSDS B0 cùng lưới trên test.** B0 0.3061 / 0.7452 (lưới log), lưới tuyến tính tái tạo đúng 0.3131 / 0.7310. So cùng lưới log: V2 0.3512 / 0.6116 và V3 0.3369 / 0.6167 — PSDS-1 của LBR cao hơn B0, PSDS-2 thấp hơn.

**§4 Sửa số trích sai** — xong (`efcb73e`), `check_doc_claims` bắt lại lỗi cùng loại.
