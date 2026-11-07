# ADR-0044 — S8-lite: chạy lại caption template và RAG trên hệ thống B0

**Status:** Accepted (người dùng duyệt O6 và S8-lite ngày 08/11: "hoàn tất hệ thống")
**Date:** 2026-11-08

## Context

B0 là hệ thống SED cuối (ADR-0041 §11–§12) và đã là hệ thống phục vụ mặc định (ADR-0042). Mọi số
W5 (caption) và W6 (RAG) hiện có đều tính trên f2 (ADR-0040). Báo cáo phải mô tả đúng một hệ thống
từ đầu đến cuối, nên RQ2/RQ3 cần chạy lại trên event của B0.

Khác với f2, năm model fold của B0 được train trên train ∪ dev, nên `predictions/dev.npz` của
chúng là **in-sample**. Artifact OOF `sed_oof_B0_h5_20261008T130849Z` chấm mỗi recording dev bằng
đúng model fold không thấy nó; đây cũng là artifact đã dùng để chọn cSEBB `tau0.32_abs0.3`.

## Decision

### 1. Đầu vào

- **Validation (dev):** artifact OOF của B0 lọc còn các recording split `validation` bằng
  `scripts.filter_predictions` (không train, không dump lại; chỉ cắt cửa sổ). Ra
  `ml/runs/sed_filtered_B0_oof_dev_<ts>/predictions/dev.npz`. Corpus validation vì thế gồm
  recording dev **có GT** (OOF chỉ dựng trên tập annotated), khác 137 recording của corpus f2;
  số validation B0 và f2 không so trực tiếp.
- **Test:** `sed_ensemble_B0_final_test_20261014T085016Z/predictions/test.npz` — đúng artifact
  đã đánh giá ở O5, không dump lại.
- Hậu xử lý: `sed_oof_B0_h5_20261008T130849Z/sebb_cv_selection_annotated.json` cho cả hai.
- Không đổi lexicon EN/VI, query set, BGE-M3, parser output đã khóa (ADR-0036), contract.

### 2. Phạm vi (rút gọn so với ADR-0040)

- **W6 đầy đủ:** dựng lại corpus `validation` và `test` bằng `--replace`; bốn cấu hình
  (gold/parsed × retrieval/answers) trên validation, kiểm wiring, rồi đúng bốn cấu hình đó trên
  test.
- **W5 chỉ template EN và VI** (tất định, không gọi LLM): `scripts.score_template_e2e` (mới;
  `score_captions`/`report_vi_template` lấy timeline từ file caption LLM nên không dùng được),
  mức `e2e` trên dev rồi test, `--eval-set annotated` (test cũng báo `all` làm độ nhạy). Mức
  `oracle` không phụ thuộc SED nên giữ số của S8. Ba nhánh LLM không chạy lại: mỗi lượt test
  ~2 giờ GPU trong lúc giai đoạn P đang dùng GPU, và RQ2 về ràng buộc LLM đã có kết luận trên f2. Báo cáo ghi rõ số LLM là trên f2.
- Đây là lần mở test **thứ hai** cho W5/W6 (sau S8); không chọn lại gì từ số test.

### 3. Thứ tự

1. `filter_predictions` → kiểm số recording và SHA postproc.
2. W6 validation (4 cấu hình) → W5 template dev.
3. Chỉ khi bước 2 đạt contract/wiring: W6 test (4 cấu hình) → W5 template test.
4. Sổ test, freeze artifact, STATUS, PAPER_NOTES.

### 4. Kết quả (08/11, chạy một lần)

- Validation: wiring đạt (contract 96/96, unsupported-claim 0.000, evidence thật 100%).
- Test (97 câu có relevant), nDCG@10 gold B0 so f2 (ADR-0040): structured_only/en 0.392 vs 0.416,
  hybrid/en 0.383 vs 0.415, vector_only/en 0.458 vs 0.526; CI 95% chồng lấn. Answers: mọi cấu hình
  unsupported-claim 0.000, contract/evidence 97/97; số câu có trả lời 58/97 (f2 65/97).
- Caption template e2e EN/VI trên test (139 annotated, 142 all): mọi lỗi grounding bằng 0.
- Không đổi hệ thống phục vụ hay lựa chọn SED từ các số này (PAPER_NOTES S59).

## Alternatives considered

| Phương án | Lý do không chọn |
|---|---|
| Dùng `dev.npz` in-sample của 5 model fold | Model đã thấy dev; số validation sẽ lạc quan giả |
| Chạy lại cả ba nhánh LLM trên B0 | Tốn ~6 giờ GPU test + dev, tranh GPU với giai đoạn P; không đổi câu hỏi nghiên cứu RQ2 |
| Giữ W5/W6 trên f2 | Báo cáo mô tả hai hệ thống SED khác nhau cho các tầng của cùng một pipeline |

## Consequences

DB demo validation/test sẽ chứa event B0; corpus f2 vẫn tái dựng được từ ADR-0040. Số RQ3 trên
validation không so được trực tiếp với f2 vì tập recording khác; so sánh B0 vs f2 chỉ dùng test.
