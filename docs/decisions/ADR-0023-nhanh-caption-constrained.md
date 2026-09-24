# ADR-0023 — Nhánh caption constrained: grammar phụ thuộc đầu vào, dãy con theo thời gian

**Status:** Accepted
**Date:** 2026-09-25

## Context

ADR-0022 chốt: nhánh constrained dùng **cùng** Qwen3.5-9B, **cùng** prompt, **cùng**
tham số sinh với nhánh unconstrained, khác duy nhất ở grammar lúc decode
(grammar-constrained decoding với grammar phụ thuộc đầu vào — Geng et al., EMNLP 2023).
Còn phải quyết grammar cho phép những gì. Hai lần smoke-test trên 3 recording dev
(run B `054531Z`) loại hai thiết kế đầu:

| Thiết kế | Hỏng thế nào |
|---|---|
| Mỗi câu = đúng một event | Prompt chung đòi "one short caption" → model viết **một câu rồi dừng**: mọi caption chỉ nhắc 1 event. Omission khổng lồ do xung đột định dạng, không phải do ràng buộc |
| Một câu liệt kê tự do các item | Greedy lặp **một item tới hết 256 token** (S-0012 oracle: cùng một câu thunder lặp 8 lần) |

Sửa lỗi lặp bằng repetition penalty sẽ làm hai nhánh khác nhau ở tham số sinh → loại.

## Decision

### 1. Grammar: MỘT câu, dãy con các event theo thứ tự onset, mỗi event tối đa một lần

```text
root ::= (f0 | f1 | … | f{n-1}) "."
f{i} ::= <Phrase_i> verb " from <on_i> to <off_i> seconds" r{i+1}
r{j} ::= (separator <phrase_j> verb? " from <on_j> to <off_j> seconds")? r{j+1}
verb ::= " can be heard" | " can be detected"
separator ::= ", " | ", and " | " and " | ", followed by " | ", while "
```

Kích thước tuyến tính theo số event. Timeline rỗng → grammar ép đúng câu
"No target sound event was detected in this recording." (SYSTEM §6.6).

Cụm nguồn âm: `the sound of <class_id có dấu cách>`, hai lớp gộp giữ nguyên độ mơ hồ
của template (`a siren- or alarm-like sound`, `an impulsive sound resembling
thunder, fireworks, or a gunshot`). Test khoá: lexicon đóng băng đọc **cả 21** cụm
thành đúng lớp của nó, loại `class` — nhánh constrained không thể bị chấm oan.

### 2. Evidence (G2) căn khớp chính xác

Mỗi item mang đúng cụm + mốc thời gian của một event → `align_evidence` ánh xạ về
`event_id` không mơ hồ.

### 3. Cái gì được bảo đảm, cái gì còn đo

| Chiều | Constrained |
|---|---|
| Hallucination nguồn âm (G1), từ cấm (G3), bối cảnh, gọi tên quá cụ thể, bịa thời gian | **= 0 theo cấu tạo** |
| Thứ tự thời gian, lặp | **Bảo đảm theo cấu tạo** (dãy con theo onset) |
| **Omission** — nhắc event nào, dừng lúc nào | **Model quyết → đo** |

Vì vậy RQ2 trên nhánh này thực chất hỏi: *ràng buộc loại bỏ được những vi phạm của
sinh tự do với cái giá omission bao nhiêu?* — so với unconstrained (vi phạm thật ở
bối cảnh, gọi tên quá cụ thể, G3, thứ tự; hallucination nguồn âm ở sàn, ADR-0022 §5)
và với template (không omission, không linh hoạt).

## Consequences

### Tích cực

- Hai nhánh LLM khác nhau đúng một biến; timeline của nhánh sau được kiểm trùng khít
  với nhánh trước (`generate_llm_captions` dừng nếu lệch; `score_captions` cũng kiểm).
- Hợp đồng G1–G3 kiểm được bằng máy (C1) trên output LLM, không chỉ trên template.

### Đánh đổi

- Văn phong gò bó ("the sound of vehicle pass by") — đề tài không đo độ trôi chảy;
  phải ghi vào Hạn chế, không tuyên bố caption constrained "tự nhiên".
- Thứ tự và không-lặp là bảo đảm của grammar, không phải năng lực của model — không
  được diễn giải temporal order = 1 như model "hiểu" trình tự.
- Timeline dài (tới 31 event) có thể chạm max_tokens 256 (chung với unconstrained);
  số caption bị cắt ghi trong `*.meta.json` và báo cùng kết quả.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| Mỗi câu một event | Model dừng sau 1 event (smoke-test) |
| Danh sách item tự do | Greedy lặp tới max_tokens (smoke-test) |
| Repetition/presence penalty chỉ cho constrained | Hai nhánh khác tham số sinh → Δ RQ2 không còn cô lập grammar |
| Grammar cho phép hoán vị, cấm lặp | Không biểu diễn gọn bằng CFG (bùng nổ tổ hợp) |
| Ràng buộc chỉ danh từ nguồn âm, phần còn lại tự do | Không chặn được G3/bối cảnh/thời gian bịa ở phần tự do |
