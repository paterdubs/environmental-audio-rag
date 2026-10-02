# N-gram caption (chỉ tham khảo) — `sed_ensemble_s13_f2_20260929T045053Z` (test)

> Sinh bởi `scripts.report_caption_ngram`. **Không dùng để kết luận** (evaluation_protocol §8.3): tham chiếu là caption template của cùng timeline, không phải caption người viết; nhánh constrained dùng cụm từ gần template theo cấu tạo nên có lợi sẵn; n-gram không phát hiện hallucination. Scorer `pycocoevalcap` (Bleu, Cider); tách từ đơn giản thay PTB (cần Java).

| Nhánh / mức | n | BLEU-1 | BLEU-4 | CIDEr |
|---|---:|---:|---:|---:|
| constrained/e2e | 139 | 0.5670 | 0.3675 | 3.7534 |
| constrained/oracle | 139 | 0.4258 | 0.2677 | 1.4534 |
| constrained_cover/e2e | 139 | 0.5659 | 0.3645 | 3.7680 |
| constrained_cover/oracle | 139 | 0.5874 | 0.3607 | 1.5883 |
| unconstrained/e2e | 139 | 0.1720 | 0.0283 | 0.1468 |
| unconstrained/oracle | 139 | 0.0461 | 0.0051 | 0.0664 |
