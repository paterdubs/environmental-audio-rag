# N-gram caption (chỉ tham khảo) — `sed_polyphonic_20260924T054531Z` (test)

> Sinh bởi `scripts.report_caption_ngram`. **Không dùng để kết luận** (evaluation_protocol §8.3): tham chiếu là caption template của cùng timeline, không phải caption người viết; nhánh constrained dùng cụm từ gần template theo cấu tạo nên có lợi sẵn; n-gram không phát hiện hallucination. Scorer `pycocoevalcap` (Bleu, Cider); tách từ đơn giản thay PTB (cần Java).

| Nhánh / mức | n | BLEU-1 | BLEU-4 | CIDEr |
|---|---:|---:|---:|---:|
| constrained/e2e | 142 | 0.2791 | 0.1827 | 1.4133 |
| constrained/oracle | 142 | 0.4328 | 0.2729 | 1.6460 |
| constrained_cover/e2e | 142 | 0.6204 | 0.3789 | 1.6574 |
| constrained_cover/oracle | 142 | 0.5885 | 0.3621 | 1.7846 |
| unconstrained/e2e | 142 | 0.0454 | 0.0051 | 0.0625 |
| unconstrained/oracle | 142 | 0.0480 | 0.0058 | 0.0685 |
