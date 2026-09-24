# Audit lexicon trên caption unconstrained test — `sed_polyphonic_20260924T054531Z`

> **Audit thủ công** (Claude Code, 25/09), không phải số sinh bằng script — nên được
> người kiểm lại trước khi dẫn trong báo cáo. Lexicon `caption-lexicon-v2`
> (SHA-256 `6f5634bb…`) **đã đóng băng trước khi sinh caption test và KHÔNG sửa sau
> audit** (ADR-0022 §3): các lỗi dưới đây được báo, không được "vá" bằng test.
> Số chấm tự động: [caption_grounding_sed_polyphonic_20260924T054531Z_test.md](caption_grounding_sed_polyphonic_20260924T054531Z_test.md).

## 1. Toàn bộ mention bị chấm "không có căn cứ" (8 / ~730)

Tổng mention unconstrained trên test: e2e 3.13 × 142 ≈ 444, oracle 2.01 × 142 ≈ 285.

| Recording | Mức | Mention | Timeline | Phán định |
|---|---|---|---|---|
| S-0011 | oracle | "horn **blasts**" | horn, voices | Lexicon sai — `blast` → `thunder_fireworks_gunshot` |
| S-0241 | oracle | "sharp horn **blast**" | horn, train | Lexicon sai (như trên) |
| S-0258 | oracle | "frequent horn **blasts**" | horn, train | Lexicon sai (như trên) |
| S-0301 | oracle | "brief horn **blast**" | horn, music, vehicle_* , voices | Lexicon sai (như trên) |
| S-0412 | oracle | "sharp horn **blast**" | horn, train, vehicle_idling | Lexicon sai (như trên) |
| S-0400 | oracle | "insect **song**" | cicadas_and_crickets | Lexicon sai — `song` → `music` |
| S-0582 | e2e | "birds **singing**" | birds, cicadas_and_crickets | Lexicon sai — `singing` → {music, voices} |
| S-0101 | e2e | "**bird calls**" | crows_seagulls_magpies, … (không có `birds`) | Ranh giới — quạ/hải âu cũng là chim; taxonomy tách lớp |

**Kết luận:** 7/8 là dương tính giả của lexicon, 1/8 ranh giới. Hallucination nguồn
âm thật của Qwen3.5-9B khi chỉ nhận timeline: **0–1 / ~730 mention**. Tỷ lệ tự động
(oracle 0.0126, e2e 0.0038) là **cận trên** do lỗi lexicon.

## 2. Mẫu ngẫu nhiên 30 caption (seed 20260922) — độ phủ lexicon

72 mention phát hiện được. Âm tính giả (nguồn âm có nhắc mà lexicon không bắt):
**0 rõ ràng**, 1 ranh giới ("mechanical activity" nhắc lại `workshop` đã có mention —
không đổi metric). Dương tính giả: 1 ("horn blast", đã tính ở §1).

## 3. Lỗi của sinh tự do mà lexicon KHÔNG đo (hạn chế)

- **Bịa thời lượng/thời điểm:** "A 153-second environmental recording", "early morning
  bird songs" — không có metric cho khẳng định số/thời gian. `morning` không nằm trong
  `context_terms`.
- **Khẳng định im lặng** trên timeline rỗng: "A 27.5-second silence captures the quiet
  stillness…" (S-0665), "A quiet, soundless moment captured in nature" (S-0717) — bắt
  được một phần qua `context_terms` (`silence`, `quiet`, `stillness`, `nature`), nhưng
  "soundless" thì không.

## 4. Ứng viên sửa cho một lexicon v3 (chưa áp dụng)

`horn blast(s)` → `horn`; `insect song` → `cicadas_and_crickets`; `birds singing` →
`birds`; `soundless` → context. Chỉ được áp dụng nếu có một vòng dev mới và đóng băng
lại, kèm công bố rõ trong báo cáo; không áp lên số test hiện tại.
