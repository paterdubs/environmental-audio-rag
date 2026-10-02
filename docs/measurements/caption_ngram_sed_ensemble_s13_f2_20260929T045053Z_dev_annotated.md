# N-gram caption (chỉ tham khảo) — `sed_ensemble_s13_f2_20260929T045053Z` (dev)

> Sinh bởi `scripts.report_caption_ngram`. **Không dùng để kết luận** (evaluation_protocol §8.3): tham chiếu là caption template của cùng timeline, không phải caption người viết; nhánh constrained dùng cụm từ gần template theo cấu tạo nên có lợi sẵn; n-gram không phát hiện hallucination. Scorer `pycocoevalcap` (Bleu, Cider); tách từ đơn giản thay PTB (cần Java).

| Nhánh / mức | n | BLEU-1 | BLEU-4 | CIDEr |
|---|---:|---:|---:|---:|
| constrained/e2e | 134 | 0.5473 | 0.3438 | 3.2359 |
| constrained/oracle | 134 | 0.3979 | 0.2403 | 1.3116 |
| constrained_cover/e2e | 134 | 0.5472 | 0.3434 | 3.2257 |
| constrained_cover/oracle | 134 | 0.5719 | 0.3421 | 1.3416 |
| unconstrained/e2e | 134 | 0.0951 | 0.0062 | 0.0978 |
| unconstrained/oracle | 134 | 0.0240 | 0.0026 | 0.0302 |
