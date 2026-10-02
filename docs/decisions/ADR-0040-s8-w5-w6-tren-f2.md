# ADR-0040 — S8: W5/W6 trên hệ thống SED cuối f2

**Status:** Accepted — runbook khóa trước validation và trước mọi lượt test S8.
**Date:** 2026-10-02

## Context

S13 đã khóa f2 tại commit `c3f0033`: ensemble T2b × 3, hậu xử lý cSEBB
`sebb_cv_selection_annotated.json`. W5 trước đây dùng run B và ensemble C v1; W6 đang nạp
corpus run B trong PostgreSQL. ADR-0031 §6 yêu cầu chạy lại W5/W6 đúng một lần sau khi khóa hệ
thống cuối, dev/validation trước rồi mới test.

Artifact S13 `sed_ensemble_s13_f2_20260929T045053Z` chỉ dựng split test và đã có
`predictions/test.npz`. Cùng ensemble ba member có `predictions/dev.npz` trong
`sed_ensemble_t2b_20260927T200914Z`; hai manifest liệt kê đúng cùng ba member và cùng phép trung
bình xác suất. Vì vậy S8 đọc hai prediction đã có, không gọi `dump_predictions` và không đánh giá
SED lại.

## Decision

### 1. Đầu vào và cấu hình bất biến

- Dev: `sed_ensemble_t2b_20260927T200914Z/predictions/dev.npz`.
- Test: `sed_ensemble_s13_f2_20260929T045053Z/predictions/test.npz`.
- Cả hai áp đúng
  `sed_ensemble_t2b_20260927T200914Z/sebb_cv_selection_annotated.json` (`tau0.64_rel2`, ngưỡng
  box 0.9). Script phải ghi riêng run logic f2, run chứa prediction và hash prediction.
- Không đổi lexicon EN/VI, grammar, prompt, model Qwen3.5-9B, seed, tham số sinh, query set,
  embedding BGE-M3 hay hậu xử lý. Không train và không dump prediction mới.

### 2. Runbook W5

Chạy trên dev trước, rồi test đúng một lần. Một lượt sinh caption tạo cả hai mức `oracle` và
`e2e`; ba nhánh LLM là `unconstrained`, `constrained`, `constrained_cover`. Nhánh `template` EN
được sinh tất định khi chấm; template VI được chấm riêng theo ADR-0025. RQ2 LLM vẫn chỉ EN vì
đổi sang prompt VI sẽ vi phạm thiết kế khóa của ADR-0022/0025.

```text
generate_llm_captions <f2> --predictions-run <dev|test-source> --postproc <cSEBB>
  --branch <unconstrained|constrained|constrained_cover> --split <dev|test>
score_captions <f2> --split <dev|test> --eval-set <all|annotated>
report_caption_per_class <f2> --split <dev|test> --eval-set <all|annotated>
report_caption_ngram <f2> --split <dev|test> --eval-set <all|annotated>
report_vi_template <f2> --split <dev|test> --eval-set <all|annotated>
```

Test sinh đúng một bộ 142 recording cho mỗi nhánh; phép chấm headline lọc 139 recording
`annotated`, và phép chấm `all` trên cùng output 142 recording được báo như độ nhạy để so trực tiếp
với số cũ. Không gọi LLM lần thứ hai để tạo tập annotated. File ra bắt đầu bằng
`caption_{grounding,per_class,ngram,vi_template}_s8_f2_...`.

### 3. Runbook W6

Corpus PostgreSQL hiện không có khóa `corpus_version`; vì vậy không thể giữ đồng thời run B và f2
dưới cùng tên split mà không đổi schema. S8 dùng `--replace` để thay `validation` và `test` trong
DB demo bằng f2. Bản run B vẫn được giữ nguyên trong `ml/runs/retrieval_index_*` và các measurement
`retrieval_*_20260925`, dùng làm baseline so sánh.

```text
build_retrieval_index --run <f2> --predictions-run <dev-source> --postproc <cSEBB>
  --split validation --replace
build_retrieval_index --run <f2> --predictions-run <test-source> --postproc <cSEBB>
  --split test --replace
evaluate_retrieval --split validation                    # gold
evaluate_retrieval --split validation --parsed-filters <query_parser> --gold-reference <gold>
evaluate_answers   --split validation                    # gold
evaluate_answers   --split validation --parsed-filters <query_parser>
```

Chỉ sau khi bốn lượt validation đạt wiring/contract mới chạy đúng bốn cấu hình tương ứng trên
test. Bộ lọc parse tái sử dụng output parser đã khóa ở ADR-0036; parser phụ thuộc câu hỏi, không
phụ thuộc corpus nên không gọi LLM lại. File ra bắt đầu bằng
`retrieval_{benchmark,answers}_{validation,test}_s8_f2_{gold,parsed}_...`.

### 4. Metric và artifact tổng

- RQ2: hallucination, omission, G3 (`forbidden_term_rate`) và CI bootstrap theo recording; kèm
  per-class và BLEU/CIDEr chỉ tham khảo.
- RQ3: nDCG@10, Recall@1/5/10, filter exactness; câu trả lời phải giữ unsupported-claim rate 0.
- `scripts.report_s8_summary` chỉ đọc measurement cũ và mới để sinh
  `s8_summary_20261002.{md,json}`; không tính từ test prediction.
- `scripts.report_test_ledger` chạy sau cùng. Tất cả measurement test f2 phải xuất hiện đúng một
  lần theo cấu hình đã liệt kê ở trên.

## Alternatives considered

| Phương án | Lý do không chọn |
|---|---|
| Dump lại dev/test vào artifact S13 | Prediction tương đương đã có; dump lại tăng một lượt chạm test không cần thiết. |
| Dùng postproc θ vì script cũ hỗ trợ sẵn | Không phải hệ thống f2 đã khóa và làm sai câu hỏi S8. |
| Tạo prompt/grammar VI cho ba nhánh LLM | Đổi biến nghiên cứu sau test và trái ADR-0022/0025. |
| Đổi schema để giữ nhiều corpus trong DB | Mở rộng kiến trúc không cần thiết cho S8; baseline đã được giữ bằng artifact bất biến. |

## Consequences

Script dùng chung timeline phải hiểu cả hậu xử lý θ cũ và cSEBB, đồng thời ghi provenance của
prediction source riêng với run logic. DB demo sau S8 chỉ chứa corpus f2 cho `validation`/`test`;
muốn tái tạo run B phải chạy lại lệnh ADR-0027 từ artifact cũ. Số mới có thể kém số cũ và vẫn phải
báo nguyên văn.

## Verification

Trước test: ADR và code hỗ trợ cSEBB/prediction source được commit, tree sạch; ba nhánh dev sinh
đủ, score/per-class/n-gram/VI pass; corpus validation ghi model f2; retrieval/answer gold và parse
pass. Sau test: hash caption/prediction/postproc có trong JSON, corpus test ghi f2, filter exactness
hard-filter bằng 1.000, ledger liệt kê đủ lượt và `s8_summary_20261002` sinh tự động.
