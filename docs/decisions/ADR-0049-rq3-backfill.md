# ADR-0049 — RQ3: chế độ truy hồi backfill (lọc cứng trước, nối kết quả ngữ nghĩa sau)

**Status:** Accepted (người dùng duyệt 24/11/2026: "cứ đưa backfill lên test")
**Date:** 2026-11-24

## Context

Trên test, hybrid thua vector_only ở kho f2, B0 và LBR V2, thắng ở LBR V3
(`rq3_modes_20261123`). Đếm trên `per_query` đã lưu của các báo cáo `retrieval_benchmark_*_gold`:
khi SED phát hiện thưa, bộ lọc cứng chỉ giữ rất ít bản ghi (danh sách hybrid rỗng ở 32/97 câu của
f2), nên hybrid mất điểm vì trả ít kết quả, không phải vì xếp sai. Chương 6 và 7 đã ghi "dùng bộ lọc
như điểm cộng thay cho điều kiện cứng" là hướng chưa thử.

Kiểm trước khi ghi ADR (chỉ đọc artifact): ở cả tám báo cáo gold (validation và test, bốn kho), mọi câu
hybrid trả dưới 10 kết quả đều trả **đúng** tập của structured_only. Tức chỉ mục HNSW không cắt bớt
kết quả lọc, và hybrid khi ngắn hơn 10 chứa mọi bản ghi thỏa bộ lọc.

Một mô phỏng nháp ngoài repo trên validation (không đọc test) cho backfill cao hơn cả hybrid lẫn
vector_only ở bốn kho. Số đó không được dùng; script dưới đây sinh lại.

## Decision

### 1. Định nghĩa

`backfill(q) = hybrid(q) ⧺ [r ∈ vector_only(q) | r ∉ hybrid(q)]`, cắt ở k = 10.

- Tầng 1 là kết quả hybrid (thỏa bộ lọc). Tầng 2 là kết quả ngữ nghĩa **không** thỏa bộ lọc (suy ra từ
  kiểm ở Context), phải được gắn nhãn "gần khớp, không thỏa bộ lọc" khi hiển thị hay trả lời.
- Không có tham số tự do. Không đổi query set v2, BGE-M3, parser (ADR-0036), top-k, định nghĩa hybrid.
- Tính từ danh sách `retrieved` đã lưu trong các báo cáo đã khóa; không dựng lại DB, không embed lại,
  không chạy lại truy hồi.

### 2. Phạm vi và so sánh ghi trước

- Kho: `f2` (`retrieval_benchmark_<split>_20261002`), `B0` (`_s8lite_b0_gold_20261108`), `lbrv2`,
  `lbrv3` (`_gold_20261110`).
- **Chính:** bộ lọc gold, tiếng Anh, nDCG@10; hai hiệu ghép cặp `backfill − vector_only` và
  `backfill − hybrid`.
- **Phụ:** tiếng Việt; bộ lọc từ parser (`_parsed_`); recall@10, MRR; RRF (k = 60, gộp hybrid và
  vector_only, hòa xếp theo `recording_id`) làm đối chứng có tham số; thắng/hòa/thua theo câu;
  độ đúng bộ lọc của top-10 (tỷ lệ tầng 1).
- Thống kê: bootstrap ghép cặp theo câu hỏi, 10 000 lần, seed 20260922 (`recording_bootstrap`);
  kiểm định hoán vị dấu ghép cặp, 10 000 lần, cùng seed, hai phía.

### 3. Luật diễn giải

- Chỉ viết "backfill tốt hơn X" khi CI 95% của hiệu trên test không chứa 0.
- Hybrid vẫn là chế độ của số RQ3 đã khóa; backfill báo như chế độ thứ tư, không thay số cũ.
- Đánh đổi phải báo cùng lúc: độ đúng bộ lọc của backfill dưới 1.000 theo định nghĩa.

### 4. Thứ tự chạy

1. Commit ADR này và script `scripts.report_rq3_backfill` cùng test.
2. Chạy `--split validation` trên tree sạch, commit measurement.
3. Chạy `--split test` **một lần** trên tree sạch; thêm mẫu `retrieval_backfill_test` vào sổ test.
4. Phục vụ: demo dùng backfill có nhãn tầng (ADR này quyết định trên validation, độc lập với số test).

## Alternatives considered

- **Điểm trộn lồi α·cosine + (1 − α)·[thỏa bộ lọc]** (Bruch và cộng sự 2023): artifact không lưu điểm
  cosine, phải dựng lại DB và quét α trên validation; tốn công hơn và thêm một tham số.
- **RRF k = 60 làm chế độ chính:** có tham số, không giữ được tính chất "mọi kết quả thỏa bộ lọc đứng
  trước", nên chỉ báo làm đối chứng.
- **Reranker (bge-reranker-v2-m3):** không tính được vị từ onset/offset, văn liệu cho thấy có thể hại
  khi xếp hạng đầu đã tốt; để sau nộp.
- **Dung sai thời gian và nới `classes_all`:** cần dựng lại event trong DB; để sau nộp.

## Consequences

- Đây là lượt mở test thứ tư cho W6 (sau S8, S8-lite, ADR-0047); chỉ đọc danh sách đã lưu, không
  chạm prediction SED.
- Câu trả lời template (ADR-0027) phải tách hai tầng để unsupported-claim vẫn giữ nghĩa: chỉ tầng 1
  được tính là khớp bộ lọc.

## Kết quả

(điền sau khi chạy, từ measurement sinh tự động)
