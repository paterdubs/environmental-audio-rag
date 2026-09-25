# N-gram caption (chỉ tham khảo) — `sed_ensemble_C_clean_20260925T045631Z` (test)

> Sinh bởi `scripts.report_caption_ngram`. **Không dùng để kết luận** (evaluation_protocol §8.3): tham chiếu là caption template của cùng timeline, không phải caption người viết; nhánh constrained dùng cụm từ gần template theo cấu tạo nên có lợi sẵn; n-gram không phát hiện hallucination. Scorer `pycocoevalcap` (Bleu, Cider); tách từ đơn giản thay PTB (cần Java).

| Nhánh / mức | n | BLEU-1 | BLEU-4 | CIDEr |
|---|---:|---:|---:|---:|
| constrained/e2e | 142 | 0.5767 | 0.3672 | 2.8541 |
| constrained_cover/e2e | 142 | 0.5798 | 0.3685 | 2.9481 |
| unconstrained/e2e | 142 | 0.1277 | 0.0170 | 0.1089 |
