# ADR-0028 — Ablation A4: trần `pos_weight`, giao thức ghi trước khi có số

**Status:** Accepted — agent tự quyết trong chế độ tự động (26/09); ghi **trước** khi run A4
đầu tiên xong
**Date:** 2026-09-26

## Context

ADR-0003 để mở câu hỏi "trần `pos_weight = 50` có phải giá trị tốt không" (A4, SYSTEM §9:
{10, 30, 50, không clip}). Mọi kết quả W3–W6 đã khoá trên trần 50. Train SED không tất định
cùng seed (ADR-0021: SD event-F1 test giữa seed nhánh B = 0.0048), nên một run mỗi trần chỉ
cho tín hiệu thô.

## Decision

1. **Nhánh B** (AudioSet, cấu hình chính thức), seed 20260922, 8 epoch, mọi thứ khác giữ nguyên.
   Trần 50 = run có sẵn `sed_polyphonic_20260924T054531Z`; train mới trần 10, 30, `inf`
   (`scripts.train_sed --pos-weight-cap`), mỗi trần **một** run.
2. Mỗi run: `scripts.sweep_threshold` (θ per-class + duration prior, như run chính thức) →
   `postproc.json`. **Metric so sánh: event-F1 trên dev** với postproc của chính run đó;
   kèm frame macro-F1 dev (`best_validation`).
3. Test: `scripts.evaluate_run` một lần mỗi run, chỉ để báo cáo — không dùng để chọn.
4. **Luật quyết định:** trần mặc định **giữ 50** cho mọi kết quả đã báo. A4 là mô tả: một
   trần khác chỉ được ghi là "tốt hơn" nếu hơn trần 50 trên dev quá 2 × 0.0048 event-F1; kể cả
   khi đó cũng không train lại hệ thống chính (W5/W6 đã khoá) — chỉ ghi vào Hạn chế/hướng mở.

## Consequences

- Trả lời câu hỏi mở của ADR-0003 mà không đụng số đã khoá.
- n = 1 mỗi trần: khác biệt dưới ngưỡng 2 SD được báo là không phân biệt được với nhiễu seed.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| 3 seed mỗi trần | 9 run GPU (~3 h) cho một ablation không trả lời RQ nào (PLAN cut-list #3) |
| Chọn trần theo test | Tuning trên test |
| Đổi trần mặc định nếu tốt hơn | Phải train lại toàn bộ B/C và làm lại W5/W6 |
