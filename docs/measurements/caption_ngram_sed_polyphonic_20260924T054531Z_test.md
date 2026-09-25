# N-gram caption (chỉ tham khảo) — `sed_polyphonic_20260924T054531Z` (test)

> Sinh bởi `scripts.report_caption_ngram`. **Không dùng để kết luận** (evaluation_protocol §8.3): tham chiếu là caption template của cùng timeline, không phải caption người viết; nhánh constrained dùng cụm từ gần template theo cấu tạo nên có lợi sẵn; n-gram không phát hiện hallucination. Scorer `pycocoevalcap` (Bleu, Cider); tách từ đơn giản thay PTB (cần Java).

| Nhánh / mức | n | BLEU-1 | BLEU-4 | CIDEr |
|---|---:|---:|---:|---:|
| constrained/e2e | 142 | 0.2773 | 0.1813 | 1.4246 |
| constrained/oracle | 142 | 0.4043 | 0.2521 | 1.6440 |
| unconstrained/e2e | 142 | 0.0454 | 0.0051 | 0.0625 |
| unconstrained/oracle | 142 | 0.0480 | 0.0058 | 0.0685 |
