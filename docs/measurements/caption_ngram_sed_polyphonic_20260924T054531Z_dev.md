# N-gram caption (chỉ tham khảo) — `sed_polyphonic_20260924T054531Z` (dev)

> Sinh bởi `scripts.report_caption_ngram`. **Không dùng để kết luận** (evaluation_protocol §8.3): tham chiếu là caption template của cùng timeline, không phải caption người viết; nhánh constrained dùng cụm từ gần template theo cấu tạo nên có lợi sẵn; n-gram không phát hiện hallucination. Scorer `pycocoevalcap` (Bleu, Cider); tách từ đơn giản thay PTB (cần Java).

| Nhánh / mức | n | BLEU-1 | BLEU-4 | CIDEr |
|---|---:|---:|---:|---:|
| constrained/e2e | 137 | 0.2391 | 0.1560 | 1.0981 |
| constrained/oracle | 137 | 0.3426 | 0.2079 | 1.5076 |
| unconstrained/e2e | 137 | 0.0322 | 0.0033 | 0.0474 |
| unconstrained/oracle | 137 | 0.0246 | 0.0026 | 0.0373 |
