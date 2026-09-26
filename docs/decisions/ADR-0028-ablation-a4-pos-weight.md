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

## Kết quả (26/09, `ablation_a4_pos_weight_20260926.md`)

Event-F1 dev (in-sample): trần 10 **0.1233**, 30 0.0944, 50 0.0814, không clip 0.0946 → theo
luật cả ba trần khác đều "tốt hơn" 50 trên dev (Δ +0.042 / +0.013 / +0.013). Test (chỉ báo):
0.0725 / 0.0548 / 0.0621 / 0.0614 — chỉ trần 10 giữ hướng tăng; 30 và không clip đảo chiều.
**Đọc đúng:** trần thấp (10) là tín hiệu nhất quán dev + test, nhưng n = 1 và SD seed ~0.005;
trần 50 giữ nguyên cho mọi số đã báo (§4). Trần 10 là hướng mở, không phải kết luận.

## Consequences

- Trả lời câu hỏi mở của ADR-0003 mà không đụng số đã khoá.
- n = 1 mỗi trần: khác biệt dưới ngưỡng 2 SD được báo là không phân biệt được với nhiễu seed.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| 3 seed mỗi trần | 9 run GPU (~3 h) cho một ablation không trả lời RQ nào (PLAN cut-list #3) |
| Chọn trần theo test | Tuning trên test |
| Đổi trần mặc định nếu tốt hơn | Phải train lại toàn bộ B/C và làm lại W5/W6 |
