# ADR-0026 — Nhánh caption `constrained_cover`: bắt buộc nhắc mọi lớp

**Status:** Accepted — thiết kế và luật báo cáo ghi **sau dev, trước test** (§4); kết quả §5
**Date:** 2026-09-25

## Context

Nhánh constrained (ADR-0023) đưa suy diễn bối cảnh, gọi tên quá mức và G3 về 0 theo cấu
tạo, nhưng **bỏ sót nhiều hơn hẳn**: dev (v1) omission e2e 0.280 / oracle 0.086, so với
unconstrained 0.045 / 0.017. Grammar cho model tự chọn dừng, và model dừng sớm. Đây là
điểm yếu chính của C1. Người dùng chọn thử một biến thể buộc phủ lớp (25/09).

## Decision

### 1. Grammar: event đầu của mỗi lớp bắt buộc

Giữ nguyên grammar ADR-0023 (một câu, dãy con theo onset, mỗi event tối đa một lần) và
chỉ đổi một điểm: **event sớm nhất của mỗi lớp trở thành bắt buộc**, event lặp của lớp
vẫn tuỳ chọn, caption bắt đầu từ event sớm nhất. Prompt, model, tham số sinh, verb,
separator, ngân sách token (ký tự, ADR-0023 §7) giống hệt nhánh constrained → so hai nhánh
cô lập đúng một ràng buộc.

Bảo đảm theo cấu tạo: omission **theo lớp** = 0 (trừ khi chạm trần context — không xảy ra
ở ngân sách v1.2 trên dữ liệu này). Omission theo event (bỏ event lặp) vẫn có thể.

### 2. Là nhánh THÊM, không thay nhánh constrained

Số của constrained giữ nguyên và vẫn là nhánh chính của ADR-0023. Không chọn giữa hai
nhánh dựa trên test.

### 3. Báo cáo ghi trước

Trên test, một lần: run B `054531Z` (oracle + e2e) và ensemble C e2e (ADR-0024, hướng D).
Báo đủ metric C2 kèm CI, hiệu số cặp cover − constrained và cover − unconstrained, số
caption bị cắt, số mention, lỗi theo lớp, và caption lớp gộp (§7 taxonomy).

### 4. Đã biết gì khi ghi ADR này

- **Đã biết:** kết quả test v1 của constrained/unconstrained (ADR-0023 §4); kết quả dev
  của nhánh cover (bảng dưới); constrained v1.2 trên dev.
- **Chưa biết:** mọi kết quả test của nhánh cover; constrained v1.2 trên test.

**Dev** (run B `054531Z`, 137 recording/mức; nguồn `caption_grounding_sed_polyphonic_20260924T054531Z_dev.md`):

| Nhánh / mức | Omission | Thứ tự (≥2 mention) | Gọi tên quá mức | Bối cảnh | Mention/caption |
|---|---:|---:|---:|---:|---:|
| constrained / e2e | 0.278 [0.224, 0.333] | 1.000 | 0 | 0 | 2.96 |
| **cover / e2e** | **0.000** | 1.000 | 0 | 0 | 6.54 |
| unconstrained / e2e | 0.044 [0.028, 0.064] | 0.844 | 0.152 | 0.358 | 3.25 |
| template / e2e | 0.000 | 1.000 | 0 | 0 | 6.98 |
| constrained / oracle | 0.083 [0.053, 0.118] | 1.000 | 0 | 0 | 3.77 |
| **cover / oracle** | **0.000** | 1.000 | 0 | 0 | 5.64 |
| unconstrained / oracle | 0.017 [0.006, 0.033] | 0.858 | 0.093 | 0.226 | 2.09 |

Cover − constrained (e2e): omission −0.278 [−0.333, −0.224], mọi metric khác bằng nhau. 0/274
caption bị cắt; omission theo lớp = 0 ở 274/274 caption (đúng cấu tạo). Thời gian sinh dev
3,226 s so với 1,568 s của constrained (×2.1). Mention/caption gần template: khi buộc phủ
lớp, model còn tự nhắc phần lớn event lặp — caption tiến sát template.

### 5. Kết quả test (một lần, sau commit `954d09d`)

Nguồn: `caption_grounding_sed_polyphonic_20260924T054531Z_test.md`,
`caption_grounding_sed_ensemble_C_clean_20260925T045631Z_test.md`, `caption_per_class_*_test.md`.
0/284 (run B) và 0/142 (ensemble C) caption cover bị cắt; omission theo lớp = 0 ở mọi caption.

| Nhánh (test) | Omission | Thứ tự ≥2 | Gọi tên quá mức | Bối cảnh | Halluc. | Mention |
|---|---:|---:|---:|---:|---:|---:|
| cover / e2e (run B) | **0.000** | 1.000 | 0 | 0 | 0 | 5.57 |
| constrained / e2e (run B) | 0.284 | 1.000 | 0 | 0 | 0 | 2.75 |
| unconstrained / e2e (run B) | 0.060 | 0.871 | 0.186 | 0.423 | 0.004 | 3.13 |
| cover / oracle | **0.000** | 1.000 | 0 | 0 | 0 | 4.59 |
| cover / e2e (ensemble C) | **0.000** | 1.000 | 0 | 0 | 0 | 2.50 |
| constrained / e2e (ensemble C) | 0.036 | 1.000 | 0 | 0 | 0 | 2.37 |
| unconstrained / e2e (ensemble C) | 0.013 | 0.880 | 0.131 | 0.444 | 0.005 | 1.50 |

Hiệu số cặp, CI 95%: cover − unconstrained (run B e2e) omission −0.060 [−0.079, −0.041],
thứ tự +0.129 [+0.088, +0.172], gọi tên quá mức −0.186 [−0.229, −0.145], bối cảnh −0.423
[−0.500, −0.345], hallucination −0.004 [−0.010, +0.000]; oracle omission −0.012 [−0.022,
−0.004]. Cover − constrained: omission −0.284 [−0.340, −0.233] (e2e), −0.097 [−0.132,
−0.065] (oracle), mọi metric khác bằng nhau. Diễn đạt lớp gộp §7: 0 vi phạm (như constrained).

**Đọc đúng:** cover là nhánh duy nhất không thua unconstrained ở metric nào — nhưng omission
0 là do cấu tạo, và caption tiến sát template (5.57 so với 6.13 mention). Thời gian sinh ×2.2
so với constrained (5,263 s so với 2,398 s trên test). **Hướng D:** trên SED tối ưu, timeline
ngắn hơn nên omission của constrained giảm từ 0.284 xuống 0.036 — bỏ sót của constrained chủ
yếu là hệ quả của timeline dài; kết luận RQ2 về bối cảnh/gọi tên quá mức/thứ tự giữ nguyên.

## Consequences

### Tích cực

- Trả lời được: ép phủ lớp có giữ được grounding không, và đổi lại gì.

### Đánh đổi

- Caption dài hơn; omission theo lớp = 0 là do cấu tạo, không phải năng lực model.
- Khi grammar gần như quyết định nội dung, nhánh này tiến gần template: giá trị còn lại
  của LLM chỉ ở lựa chọn nối câu và event lặp — không đo độ tự nhiên, nên không kết luận
  được LLM hơn template ở đâu.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| Bắt buộc mọi event | Caption rất dài (tới 59 event), gần như template; không còn lựa chọn nào cho model |
| Thêm câu nhắc "mention every event" vào prompt | Đổi prompt → hai nhánh khác nhau ở hơn một yếu tố |
| Phạt lặp / đổi sampling | Đổi cách giải mã → cùng vấn đề |
| Gộp mọi event cùng lớp vào một mệnh đề | Thứ tự trong câu không còn theo thời gian ("followed by" sai nghĩa) |
