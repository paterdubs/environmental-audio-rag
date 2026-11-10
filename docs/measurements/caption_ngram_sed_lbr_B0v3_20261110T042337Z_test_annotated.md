# N-gram caption (chỉ tham khảo) — `sed_lbr_B0v3_20261110T042337Z` (test)

> Sinh bởi `scripts.report_caption_ngram`. **Không dùng để kết luận** (evaluation_protocol §8.3): tham chiếu là caption template của cùng timeline, không phải caption người viết; nhánh constrained dùng cụm từ gần template theo cấu tạo nên có lợi sẵn; n-gram không phát hiện hallucination. Scorer `pycocoevalcap` (Bleu, Cider); tách từ đơn giản thay PTB (cần Java).

| Nhánh / mức | n | BLEU-1 | BLEU-4 | CIDEr |
|---|---:|---:|---:|---:|
| constrained/e2e | 139 | 0.4027 | 0.2481 | 1.7217 |
| constrained_cover/e2e | 139 | 0.5275 | 0.3223 | 1.8449 |
| unconstrained/e2e | 139 | 0.0622 | 0.0064 | 0.0648 |
