# N-gram caption (chỉ tham khảo) — `sed_ensemble_s13_f2_20260929T045053Z` (dev)

> Sinh bởi `scripts.report_caption_ngram`. **Không dùng để kết luận** (evaluation_protocol §8.3): tham chiếu là caption template của cùng timeline, không phải caption người viết; nhánh constrained dùng cụm từ gần template theo cấu tạo nên có lợi sẵn; n-gram không phát hiện hallucination. Scorer `pycocoevalcap` (Bleu, Cider); tách từ đơn giản thay PTB (cần Java).

| Nhánh / mức | n | BLEU-1 | BLEU-4 | CIDEr |
|---|---:|---:|---:|---:|
| constrained/e2e | 137 | 0.5529 | 0.3500 | 3.3085 |
| constrained/oracle | 137 | 0.3996 | 0.2422 | 1.5024 |
| constrained_cover/e2e | 137 | 0.5536 | 0.3501 | 3.3427 |
| constrained_cover/oracle | 137 | 0.5731 | 0.3437 | 1.5318 |
| unconstrained/e2e | 137 | 0.0943 | 0.0060 | 0.0972 |
| unconstrained/oracle | 137 | 0.0251 | 0.0027 | 0.0371 |
