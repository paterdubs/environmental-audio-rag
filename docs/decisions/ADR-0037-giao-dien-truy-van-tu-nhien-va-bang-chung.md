# ADR-0037 — Giao diện truy vấn tự nhiên và bằng chứng phát lại

**Status:** Accepted — 2026-09-28  
**Date:** 2026-09-28

## Context

API đã có parser câu hỏi theo ADR-0036 và vẫn hỗ trợ bộ lọc thủ công. Giao diện demo cần cho người dùng thấy parser đã hiểu gì, sửa được bộ lọc trước khi truy vấn, đồng thời không biến lỗi llama.cpp thành một bộ lọc đoán. Kết quả truy hồi có evidence gồm recording và khoảng thời gian; giao diện cần liên kết evidence với timeline và audio.

## Decision

1. Chế độ mặc định của ô tìm kiếm là câu hỏi tự nhiên. UI gọi `/api/v1/retrieval/parse`, hiển thị các chip lớp/predicate/thời lượng và cho phép xoá hoặc chỉnh predicate trước khi gửi `/retrieval/query`.
2. Khi parser lỗi hoặc LLM không sẵn sàng, UI giữ câu hỏi, báo lỗi rõ ràng và chuyển sang biểu mẫu bộ lọc thủ công; không tự suy đoán filter.
3. Evidence được hiển thị với recording, class tiếng Việt lấy từ `/taxonomy`, onset/offset và nút mở đúng recording/giây. Timeline giữ màu theo taxonomy; class_id không được dịch trong dữ liệu.
4. UI đọc `/api/v1/models/status`; `official=false` phải hiện nhãn “Demo — SED v2, chưa phải hệ thống chính thức”.
5. Các câu chữ tiếng Việt mới và caption VI chỉ được lập danh sách review cho người dùng; không sửa lexicon VI trong ADR-0025.

## Alternatives considered

| Phương án | Lý do không chọn |
|---|---|
| Gửi câu hỏi thẳng vào truy hồi | Không hiển thị được filter đã hiểu và khó sửa lỗi parser |
| Im lặng rơi về filter mặc định | Có thể làm thay đổi ý định người dùng |
| Chỉ hiện recording, không có thời gian | Mất liên kết grounding của evidence |

## Consequences

Natural search minh bạch hơn và vẫn có đường lui thủ công. Query có thể cần thêm một thao tác sửa chip; trạng thái parser unavailable được coi là lỗi có thể quan sát. UI phụ thuộc taxonomy API để lấy tên hiển thị và không tạo thêm nguồn sự thật.

## Verification

Kiểm thử Vitest bao phủ parse thành công → chip → query và parser lỗi → manual fallback. `npm test` và `npm run build` là gate của frontend; Python ruff/pytest vẫn là gate của repository. Kịch bản stack thật và thời gian xử lý được ghi trong `docs/DEMO.md` và measurement liên quan.
