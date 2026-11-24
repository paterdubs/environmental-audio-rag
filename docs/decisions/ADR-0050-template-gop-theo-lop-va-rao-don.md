# ADR-0050 — Mô tả phục vụ: gộp sự kiện theo lớp, đếm số lần, rào đón theo điểm tin cậy

**Status:** Accepted (người dùng duyệt 24/11/2026 làm Pha 4; câu chữ tiếng Việt chờ người dùng đọc lại)
**Date:** 2026-11-24

## Context

Mô tả mẫu cố định (`TemplateCaptioner`, khóa cho RQ2) viết một câu cho mỗi sự kiện. Với dòng thời gian
dày của LBR V3 (hệ phục vụ), mô tả mẫu trên dev dài trung bình khoảng 400 ký tự, dài nhất hơn 2 300
ký tự (rà soát nội bộ 24/11), và không có câu nào cho biết sự kiện lặp lại hay SED kém chắc chắn.
Văn liệu (AudioCapBench, GEM 2024) cho thấy đánh đổi giữa bám sát và hữu ích; lời rào đón chỉ có giá
trị khi nó đến từ độ tin cậy của bộ phát hiện chứ không do mô hình ngôn ngữ tự đặt.

## Decision

### 1. Bộ sinh mới, không thay bộ sinh của RQ2

`GroupedTemplateCaptioner` (`caption-grouped-v1.0`) dùng cho hệ phục vụ. `TemplateCaptioner` và mọi số
RQ2 đã khóa giữ nguyên.

- Một mệnh đề cho mỗi lớp, theo thứ tự onset đầu tiên của lớp.
- Lớp có một sự kiện: giữ câu của mẫu cố định (EN) / "Nghe thấy {lớp} từ {a} đến {b} giây." (VI).
- Lớp có n ≥ 2 sự kiện: "A {lớp} is audible {n} times between {a} and {b} seconds." /
  "Nghe thấy {lớp} {n} lần trong khoảng {a} đến {b} giây.", với a là onset đầu, b là offset cuối.
- Rào đón: nếu điểm cao nhất trong các sự kiện của lớp nhỏ hơn θ_hedge thì EN chèn "possibly"
  ("A {lớp} is possibly audible …"), VI mở đầu bằng "Có lẽ nghe thấy …".
- Bằng chứng: mỗi mệnh đề trích sự kiện đầu tiên của lớp; không mệnh đề nào nêu nguồn âm ngoài
  dòng thời gian, không suy diễn nguyên nhân (G1–G3 giữ nguyên, `assert_safe`).

### 2. Ngưỡng rào đón, chọn trước khi đo

θ_hedge = phân vị 33,3% của điểm sự kiện trong dòng thời gian dev (ngoài mẫu) của hệ phục vụ LBR V3
`recall_first`, tính một lần và ghi vào measurement. Không chỉnh θ theo kết quả.

### 3. Đo trên dev (không mở test)

Trên dòng thời gian dev đã lưu của bốn hệ SED (134 bản ghi có nhãn):

- So với dòng thời gian dự đoán: ảo giác và bỏ sót theo lớp phải bằng 0 như mẫu cố định;
  độ dài (ký tự) trung bình và lớn nhất so với mẫu cố định.
- So với nhãn gốc: ảo giác và bỏ sót (phải trùng mẫu cố định vì cùng tập lớp).
- Rào đón có mang thông tin không: độ chính xác theo lớp (lớp có trong nhãn gốc của bản ghi) của
  mệnh đề có rào đón so với không rào đón, hiệu và CI 95% bootstrap theo bản ghi. Chỉ viết "rào đón
  mang thông tin" khi CI của hiệu (không rào đón − có rào đón) nằm trên 0.

## Alternatives considered

- **Để mô hình ngôn ngữ tự rào đón:** văn liệu cho thấy lời rào đón của LLM hiệu chuẩn kém ngoài miền.
- **Rào đón theo từng sự kiện:** làm câu dài lại, đi ngược mục tiêu gộp.
- **Thay luôn mẫu cố định của RQ2:** làm mất khả năng tái lập số đã khóa.

## Consequences

- Mô tả trong demo ngắn hơn và nói được "lặp lại n lần", "có lẽ".
- Bộ chấm G1–G3 áp dụng nguyên cho bộ sinh mới; mệnh đề gộp được chấm theo lớp nên bỏ sót theo lớp
  vẫn đo được.
- Câu chữ tiếng Việt ("Nghe thấy", "Có lẽ nghe thấy", "n lần trong khoảng") cần người dùng duyệt.

## Kết quả

(điền sau khi chạy, từ measurement sinh tự động)
