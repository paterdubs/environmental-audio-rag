# Kế hoạch báo cáo khóa luận giữa kỳ

> Task gốc: **L3** trong [docs/PLAN.md](../docs/PLAN.md) ("Viết báo cáo luận văn"). Đây là phần
> báo cáo **giữa kỳ** của L3, không thay thế bản báo cáo cuối kỳ.
> Người dùng duyệt kế hoạch ngày 03/10/2026; bản nháp `docs/thesis/ch1.md`–`ch4.md` **không** được
> dùng (người dùng xác nhận là bản rác), nội dung viết mới hoàn toàn trong `report/src/`.

## 1. Phạm vi và mốc chốt

| Hạng mục | Quyết định |
|---|---|
| Mốc chốt nội dung | Commit `b1802f4` (03/10/2026). Mọi số liệu lấy từ artifact đã có tại commit này |
| Loại báo cáo | Giữa kỳ: báo cáo đúng phần đã đạt, phân biệt kết quả – hạn chế – kế hoạch tiếp theo |
| Kết quả vượt lịch | Giữ nguyên (S8, S13, W7 đã xong sớm); trình bày là đã đạt, kèm giới hạn |
| Không làm | Train, tuning, chọn lại checkpoint/θ, chạy lại test, đọc prediction test, sửa split/taxonomy/annotation/metric, slide, poster |
| Đầu ra chính | `report/Bao_cao_KLTN_giua_ky_environmental_audio_rag.docx` (+ PDF xem trước) |

Mức trạng thái dùng xuyên suốt báo cáo và bảng đối chiếu:

- **(a) Thiết kế dự kiến** — có trong SYSTEM.md/ADR nhưng chưa có code.
- **(b) Đã triển khai** — có code và test đơn vị, chưa có số đo trên dữ liệu thật.
- **(c) Đã kiểm chứng** — có command và artifact (measurement/run manifest).
- **(d) Chưa thực hiện** — nằm trong kế hoạch giai đoạn sau.

## 2. Đề cương

| Phần | Nội dung | Nguồn chính | Xử lý |
|---|---|---|---|
| Bìa VI, bìa phụ, bìa EN | Theo mẫu khoa, thông tin cá nhân để placeholder | Mẫu DOCX | Dựng lại từ XML của mẫu |
| Abstract / Tóm tắt | Một trang mỗi bản, có từ khóa | Toàn báo cáo | Viết mới |
| Lời cảm ơn | Placeholder để sinh viên tự viết | — | Placeholder |
| Nhận xét GVHD | Trang trống theo mẫu | Mẫu DOCX | Giữ; **bỏ** hai trang phản biện (giữa kỳ) |
| Mục lục, DM hình, DM bảng | Word fields TOC | — | Field, cập nhật bằng Word |
| DM viết tắt | Bảng A→Z | Thân bài | Viết mới |
| Ch.1 Giới thiệu | Bối cảnh, bài toán, mục tiêu, RQ1–RQ3, phạm vi, đóng góp dự kiến vs đã có bằng chứng | SYSTEM §1, ADR-0001/0021, PAPER_NOTES §1 | Viết mới |
| Ch.2 Cơ sở lý thuyết | SED đa nhãn, metric (frame/event/PSDS, micro/macro), transfer & pretraining, grounded captioning, RAG/hybrid retrieval | RELATED_WORK (chỉ V3/V4), evaluation_protocol | Viết mới + nâng nguồn lên V3 |
| Ch.3 Dữ liệu | DataSEC/DataSED, taxonomy 22 vs 21, D0–D4, dedup nội bộ/xuyên dataset, split theo leakage group, độ phủ GT | DATA_PLAN, taxonomy.md, measurements D0–D4, ADR-0007…0013, 0034 | Viết mới |
| Ch.4 Phương pháp | Classifier phân cấp, SED v1→v2→T2b/f2, ensemble, hậu xử lý θ/cSEBB, caption 3 chế độ + G1–G3, RAG + parser, giao thức đánh giá | SYSTEM §5–§8, code `ml/`, ADR-0016/0024/0030/0032/0023/0026/0027/0036 | Viết mới, công thức đối chiếu code |
| Ch.5 Triển khai | Service, contract, event store, frontend, Compose/demo, tái lập, kiểm thử | `services/`, `contracts/`, DEMO, REPRODUCE, ADR-0029/0033/0039 | Viết mới |
| Ch.6 Kết quả hiện có | D1 classifier, RQ1/RQ1-v2, tiến triển SED, S13, cSEBB, RQ2, RQ3, parser, parity; đe dọa tính hợp lệ | `docs/thesis/tables/`, measurements, PAPER_NOTES §2, §8 | Viết mới |
| Ch.7 Tiến độ và kế hoạch | Kế hoạch vs thực tế, mức đạt mục tiêu, hạn chế, việc còn lại, kết luận giữa kỳ | PLAN, CLAUDE §3/§10, STATUS | Viết mới |
| Tài liệu tham khảo | Nhóm theo ngôn ngữ, alphabet theo họ, `[n].`, thụt 1 cm | bibliography (V3) | Sinh bằng script |
| Phụ lục (không đánh số trang) | A Taxonomy; B Artifact freeze; C Bảng theo lớp; D Lệnh tái lập; E Nhật ký làm việc | config, measurements, REPRODUCE, CLAUDE §10 | Sinh bảng bằng script + viết |

## 3. Bảng, hình, công thức dự kiến

**Bảng (sinh từ artifact bằng `scripts/build_thesis_tables.py`, không chép tay):** 01 dữ liệu/split,
02 leakage D3/D4, 03 RQ1/RQ1-v2, 04 tiến triển SED, 05 ablation v2, 06 S13 xếp hạng + test,
07 cSEBB, 08 RQ2, 09 RQ3, 10 parser, 11 parity, 12 runtime. Bổ sung nếu cần: bảng classifier
DataSEC (D1), bảng taxonomy (phụ lục), bảng per-class f2 (phụ lục, theo quy tắc n_test < 10).
Bảng văn bản (không định lượng): RQ ↔ metric, trạng thái thành phần, tiến độ, viết tắt.

**Hình (PNG 300 dpi, `scripts/build_thesis_figures.py`):** 01 kiến trúc, 02 pipeline dữ liệu,
03 kiến trúc SED, 04 tiến triển event-F1, 05 per-class f2 (CV dev), 06 timeline + caption (dev),
07 giao diện demo.

**Công thức (đối chiếu code):** BCE có mask và `pos_weight` (`ml/training/sed.py::masked_bce`);
loss phân cấp + consistency (`ml/models/hierarchical.py`); ensemble trung bình xác suất
(`ml/evaluation/ensemble.py`); event-F1 micro/macro (`ml/evaluation/sed_metrics.py`, sed_eval);
collar offset; hallucination/omission (`ml/evaluation/grounding.py`); nDCG@10, Recall@k, MRR,
filter exactness (`scripts/evaluate_retrieval.py`); bootstrap percentile
(`ml/evaluation/bootstrap.py`); vị từ thời gian (`ml/retrieval/temporal.py`).

## 4. Văn liệu

Chỉ nguồn V3/V4 vào danh mục. Hiện có 4 nguồn V3. Kế hoạch nâng lên V3 (đọc trực tiếp toàn văn,
ghi RELATED_WORK §2.1 + §10): PANNs (Kong 2020), metric SED (Mesaros 2016), PSDS (Bilen 2020),
SED tutorial (Mesaros 2021), RAG (Lewis 2020), BGE-M3 (Chen 2024), mixup (Zhang 2018),
FilterAugment (Nam 2022), BEATs (Chen 2023), hallucination survey (Ji 2023). Nguồn nào không đọc
được toàn văn thì **không** đưa vào và ghi lại.

## 5. Các bước dựng DOCX

1. `scripts/build_thesis_tables.py` / `build_thesis_figures.py` — chỉ chạy lại nếu thêm bảng; kiểm
   trước rằng script không chạy inference/evaluation trên test.
2. `scripts/build_midterm_report.py`:
   - tiền xử lý Markdown: trích dẫn `[@key]` → `[n]` theo danh mục đã sắp xếp; chèn bảng sinh tự động;
   - Pandoc (`markdown` → `docx`) cho thân bài (giữ công thức OMML);
   - lắp ráp gói từ **package mẫu khoa**: giữ numbering `CHƯƠNG %1`, header/footer, 5 section, bìa;
     chuẩn hóa style theo hướng dẫn chữ; caption bằng `STYLEREF`+`SEQ`; TOC/TOF bằng field;
     bảng có hàng tiêu đề lặp, không tách hàng; hình `keepNext` với caption.
3. Word COM (`scripts/update_docx_fields.ps1`): cập nhật mọi field, lưu, xuất PDF.
4. Kiểm tra: script kiểm cấu trúc (style/font/lề/section/field/caption) + render PDF → ảnh, xem từng trang.

## 6. Tiêu chí nghiệm thu

- [ ] Một file DOCX duy nhất gồm bìa → phụ lục, mở được trong Word.
- [ ] Mọi số định lượng có dòng trong `doi_chieu_bang_chung.md` và truy được về artifact.
- [ ] Không câu nào tuyên bố "tốt hơn" khi CI chồng lấn / chênh ≤ sd; kết quả âm tính và suy giảm được giữ.
- [ ] Phân biệt 22 lớp taxonomy với 21 lớp SED; frame-F1 / event-F1 / micro / macro / PSDS; split và eval-set.
- [ ] Trích dẫn chỉ nguồn V3/V4; số `[n]` khớp danh mục.
- [ ] Style, lề, font, section, header/footer, numbering, caption, field đúng `quy_cach_bao_cao.md`.
- [ ] Đã cập nhật field bằng Word và kiểm bố cục trên PDF (hoặc ghi rõ giới hạn nếu không làm được).
- [ ] `kiem_tra_bao_cao.md` liệt kê command, kết quả kiểm tra, placeholder, điểm cần xác minh.

## 7. Thông tin còn thiếu (placeholder `[CẦN ĐIỀN: …]`)

Họ tên sinh viên (1 hay 2 người), MSSV, lớp; họ tên và học hàm/học vị GVHD; ngày/tháng nộp;
tên đề tài tiếng Anh đã duyệt; lời cảm ơn; ngày báo cáo GVHD trong nhật ký.
