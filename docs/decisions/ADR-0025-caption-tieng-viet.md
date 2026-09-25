# ADR-0025 — Caption tiếng Việt: template tất định + lexicon riêng giữ dấu

**Status:** Accepted (25/09) — cách làm đã chốt; **cụm từ tiếng Việt chờ người dùng duyệt**
**Date:** 2026-09-25

## Context

ADR-0004 (đã khoá) quy định caption song ngữ: EN cho benchmark, **VI cho giao diện**, embed
cả hai; bảng `captions` ở SYSTEM §4.3 có cột `language 'en' | 'vi'`; HANDOFF_CODEX §A2 (đặc
tả lexicon, task 5.3) đòi mọi lớp có ít nhất một cụm EN **và** một cụm VI, kèm từ cấm G3
tiếng Việt. Rà nghiệm thu W5 trước khi push (25/09) thấy: cả ba captioner từ chối
`language="vi"`, lexicon không có cụm tiếng Việt nào.

Hai ràng buộc làm cách làm không hiển nhiên:

1. Lexicon EN đã **đóng băng** cho RQ2 (sha `6f5634bb…`, ADR-0022 §4): thêm cụm VI vào
   cùng file đổi hash và phá cổng tái lập của phép chấm test.
2. Đường khớp từ cấm hiện tại bỏ dấu (`normalize_text` → ASCII). Với tiếng Việt, bỏ dấu
   gây dương tính giả: "tới phạm vi" → "toi pham vi" chứa "toi pham" = "tội phạm".

## Decision

### 1. Caption VI = template tất định, không LLM

Cùng cấu trúc template EN — mỗi event một câu, evidence tường minh — nên G1–G3 đúng theo
cấu tạo. Benchmark RQ2 vẫn chỉ EN; nhánh LLM không sinh tiếng Việt.

Câu: `Có thể nghe thấy {cụm lớp} từ {onset} đến {offset} giây.` — số thập phân dùng dấu
phẩy theo quy ước tiếng Việt. Không có event: `Không phát hiện sự kiện âm thanh mục tiêu nào
trong bản ghi này.` (không khẳng định im lặng — cùng lý do bản EN).

### 2. Lexicon VI ở file riêng; ngôn ngữ là thuộc tính của lexicon

- `ml/configs/caption_lexicon_vi.yaml` (`caption-lexicon-vi-v1`, `language: vi`), hash
  riêng. Hash lexicon EN **không đổi** (test ghim `6f5634bb…`); chấm lại RQ2 dev (`--audit`)
  và test cho measurement trùng từng byte với bản đã commit.
- Tiếng Việt khớp **giữ dấu** (NFC + chữ thường) với ranh giới từ Unicode (`\w`); đường
  EN giữ nguyên hành vi cũ. Text tiếng Việt phải ở dạng NFC — NFD bị từ chối vì sẽ không
  khớp gì mà không báo lỗi.
- Phần tử đầu của mỗi lớp là cụm template dùng (`canonical_phrase`). Cụm dịch sát câu mẫu
  EN của taxonomy.md §2–§6; hai lớp gộp giữ cách nói rào đón §7 ("âm thanh giống còi hú
  hoặc chuông báo động", "âm thanh dạng xung giống tiếng sấm, pháo hoa hoặc tiếng súng").
  Tên subclass đứng riêng ("tiếng súng", "tiếng còi hú"…) là `specific` → đếm gọi tên quá
  mức.
- G3 tiếng Việt: danh sách HANDOFF §A2 + tương ứng danh sách EN, liệt kê cả hai cách đặt
  dấu thanh ("đe dọa"/"đe doạ", "hỏa"/"hoả").

### 3. Sửa kèm: vị trí evidence của template

Code cũ tính `mention_span` câu thứ k chỉ cộng 1 khoảng trắng thay vì k−1 → lệch trái từ
câu thứ 3. Bản mới tính đúng; kiểm: measurement RQ2 dev/test không đổi byte nào (metric
thứ tự dùng span để nối mention với event, nhưng độ lệch chưa đủ làm hỏng phép nối).

### 4. Kiểm trên dữ liệu thật

Template VI trên đúng các timeline RQ2 (run B `054531Z`, oracle + e2e, dev 137 và test
142 recording): hallucination, omission, G3, gọi tên quá mức đều **0**; thứ tự và evidence
**1.0**; số mention trung bình bằng template EN (test 5.21 / 6.13). Nguồn:
`caption_vi_template_sed_polyphonic_20260924T054531Z_{dev,test}.md`.

## Consequences

### Tích cực

- Có caption VI grounded cho giao diện (W7) và để embed cùng EN (W6, ADR-0004).
- RQ2 không bị chạm: lexicon EN, hash và mọi số đã báo giữ nguyên.

### Đánh đổi

- Cụm từ VI do agent soạn, **chưa qua người duyệt**; sửa cụm chỉ đổi hash lexicon VI.
- Chỉ template có tiếng Việt; không có số grounding cho sinh tự do tiếng Việt.
- Câu template lặp khuôn ("Có thể nghe thấy … từ … đến … giây.") — đúng nhưng đơn điệu.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| Dịch máy caption EN sang VI | Thêm nguồn lỗi; lỗi dịch thuật ngữ âm học hỏng im lặng (lý do của ADR-0004) |
| LLM sinh trực tiếp tiếng Việt | Không bảo đảm G1–G3; RQ2 đã cho thấy sinh tự do vi phạm bối cảnh/§7 |
| Thêm cụm VI vào lexicon EN | Đổi hash đã đóng băng của RQ2 |
| Khớp tiếng Việt sau khi bỏ dấu | Dương tính giả ("tới phạm vi" → "tội phạm") |
