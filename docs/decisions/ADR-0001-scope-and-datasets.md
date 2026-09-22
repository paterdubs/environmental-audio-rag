# ADR-0001 — Chọn DataSEC và DataSED làm phạm vi dữ liệu

**Status:** Accepted  
**Date:** 2026-09-22

## Context

Hướng an ninh trước đây cần ghép nhiều nguồn, thiếu class, provenance không đồng đều và phải gán gold test thủ công. Mục tiêu mới ưu tiên dataset công bố có audio và labels sẵn, nhưng vẫn giữ SED, grounded caption và RAG.

## Decision

- Dùng DataSEC cho isolated classification, encoder pretraining và subclass refinement.
- Dùng DataSED polyphonic làm benchmark temporal SED chính.
- Dùng DataSED monophonic làm benchmark phụ.
- Dùng ontology công bố thay vì duy trì taxonomy an ninh cũ.
- Đổi miền tuyên bố sang environmental acoustic monitoring.
- Không tuyên bố phát hiện sự cố trường học, tội phạm hoặc tình trạng khẩn cấp.

## Consequences

Tích cực:

- Loại phần lớn công gán nhãn thủ công.
- Dataset, paper và DOI rõ hơn.
- Giữ được pipeline kỹ thuật cốt lõi.
- Có thể so sánh classification, SED, caption grounding và retrieval.

Đánh đổi:

- DataSED gộp siren/alarm và thunder/fireworks/gunshot.
- Nhiều class không liên quan an ninh.
- Subclass classifier không có temporal subclass ground truth trên DataSED.
- Cần audit duplicate xuyên hai dataset trước transfer learning.

## Alternatives considered

- STARSS23: dữ liệu trong nhà và spatial labels tốt, thiếu event môi trường/nguy hiểm cần thiết.
- SONYC-UST-V2: sensor data thực tế lớn, chỉ weak clip-level tagging.
- DCASE Rare Sound Events: gần hazardous detection, nhưng mixture tổng hợp và class hẹp.
- Tiếp tục taxonomy cũ: chi phí data/gold vượt trọng tâm khóa luận.

## Evidence cần kiểm lại

- License bên trong từng archive.
- File counts của phiên bản tải thực tế.
- Khả năng trùng source giữa DataSEC và DataSED.

