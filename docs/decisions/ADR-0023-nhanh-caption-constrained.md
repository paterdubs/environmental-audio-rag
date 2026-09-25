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

### 4. Kết quả RQ2 trên test (lexicon `6f5634bb…` đóng băng, chấm một lần)

| Nhánh / mức | Halluc. | Omission | Temporal | G3 | Over-specific | Context | Mentions |
|---|---:|---:|---:|---:|---:|---:|---:|
| template / oracle | 0 | 0 | 1.000 | 0 | 0 | 0 | 5.21 |
| template / e2e | 0 | 0 | 1.000 | 0 | 0 | 0 | 6.13 |
| constrained / oracle | 0 | 0.100 | 0.998 | 0 | 0 | 0 | 3.06 |
| constrained / e2e | 0 | 0.284 | 0.999 | 0 | 0 | 0 | 2.75 |
| unconstrained / oracle | 0.013* | 0.012 | 0.941 | 0.007 | 0.137 | 0.324 | 2.01 |
| unconstrained / e2e | 0.004* | 0.060 | 0.903 | 0.014 | 0.186 | 0.423 | 3.13 |

\* cận trên — 7/8 là dương tính giả của lexicon (`caption_lexicon_audit_test_20260925.md`).
Nguồn: `caption_grounding_sed_polyphonic_20260924T054531Z_test.md`. 6/284 caption
constrained chạm max_tokens.

**Đọc đúng:** ràng buộc đưa bối cảnh (32–42% → 0), gọi tên quá mức (14–19% → 0),
G3 (0.7–1.4% → 0) và thứ tự (0.90–0.94 → ~1) về sàn theo cấu tạo; cái giá là
**omission cao hơn nhiều** (e2e 6% → 28%, oracle 1% → 10%) — model, khi phải nhắc
đúng từng event kèm mốc thời gian, dừng sớm. Không có khác biệt ở hallucination
nguồn âm (cả hai ở sàn). Thứ tự ~1 là bảo đảm của grammar, không phải năng lực model.

**Sửa metric trong lúc đánh giá (dev, trước khi chấm test):** temporal order trước
đó gán mỗi mention vào onset sớm nhất chưa nhận của lớp, nên caption bỏ qua một event
sớm hơn cùng lớp bị chấm sai thứ tự (constrained dev 0.86 dù grammar ép thứ tự). Nay
mention có evidence dùng onset của đúng event được trích; unconstrained (không
evidence) không đổi số. Test khoá hành vi.

### 5. Diễn đạt lớp gộp — taxonomy.md §7 (thêm 25/09, nghiệm thu W5 cuối)

Pipeline chỉ có SED coarse nên áp dòng "Chỉ có coarse SED" của §7. Đơn vị: caption có
lớp gộp trong timeline. `specific` = gọi subclass như sự thật ("a gunshot", "sirens",
"thunder, fireworks, and gunshots"); liệt kê bằng "or" ("thunder or fireworks") tính là
nêu được không chắc chắn (có lợi cho caption, luật định trên dev). Test, e2e:

| Nhánh | `sirens_and_alarms` specific | `thunder_fireworks_gunshot` specific |
|---|---:|---:|
| template | 0/18 | 0/39 |
| constrained | 0/18 | 0/39 (1 không nhắc) |
| unconstrained | **11/18** | **22/39** (13 liệt kê "or") |

Oracle: template/constrained 0/17 và 0/4; unconstrained 6/17 và 3/4. Nguồn:
`grouped_class_wording_sed_polyphonic_20260924T054531Z_test.md`; test khoá cụm gộp của
template và constrained cho cả hai lớp (`tests/test_grouped_class_wording.py`). Mệnh đề
"DataSED không có subclass ground truth" của §7 dòng thứ hai **không áp dụng**: hệ
thống không đưa subclass prediction vào caption.

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
